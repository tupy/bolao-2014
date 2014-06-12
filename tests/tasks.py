

from flask.ext.testing import TestCase

from bolao.models import Team, User, Game, BetGame
from bolao.main import app_factory
from bolao.tasks import update_scores_by_game, update_ranking
from bolao.database import db


class UpdateScoresGameTest(TestCase):

    def create_app(self):
        app = app_factory('Testing')
        return app

    def setUp(self):
        db.create_all()
        bra = Team(name='Brasil', alias='BRA')
        arg = Team(name='Argentina', alias='ARG')
        game = Game(team1=bra, team2=arg)
        db.session.add(game)

        user = User(name="Test", email="email@test.co", active=True)
        db.session.add(user)
        db.session.commit()

        self.game = game
        self.user = user

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_exact_result(self):

        self.game.score_team1 = 1
        self.game.score_team2 = 0

        bet = BetGame(user=self.user, game=self.game, score_team1=1, score_team2=0)
        db.session.add(bet)
        db.session.commit()

        update_scores_by_game(self.game)
        self.assertEqual(18, bet.score)

    def test_exact_draw(self):

        self.game.score_team1 = 1
        self.game.score_team2 = 1

        bet = BetGame(user=self.user, game=self.game, score_team1=1, score_team2=1)
        db.session.add(bet)
        db.session.commit()

        update_scores_by_game(self.game)
        self.assertEqual(18, bet.score)

    def test_team1_result_with_score(self):

        self.game.score_team1 = 2
        self.game.score_team2 = 0

        bet1 = BetGame(user=self.user, game=self.game, score_team1=2, score_team2=1)
        bet2 = BetGame(user=self.user, game=self.game, score_team1=1, score_team2=0)
        db.session.add(bet1)
        db.session.add(bet2)
        db.session.commit()

        update_scores_by_game(self.game)

        self.assertEqual(12, bet1.score)
        self.assertEqual(12, bet2.score)

    def test_team2_result_with_score(self):

        self.game.score_team1 = 0
        self.game.score_team2 = 2

        bet1 = BetGame(user=self.user, game=self.game, score_team1=1, score_team2=2)
        bet2 = BetGame(user=self.user, game=self.game, score_team1=0, score_team2=1)
        db.session.add(bet1)
        db.session.add(bet2)
        db.session.commit()

        update_scores_by_game(self.game)
        self.assertEqual(12, bet1.score)
        self.assertEqual(12, bet2.score)

    def test_team1_result(self):

        self.game.score_team1 = 1
        self.game.score_team2 = 0

        bet = BetGame(user=self.user, game=self.game, score_team1=2, score_team2=1)
        db.session.add(bet)
        db.session.commit()

        update_scores_by_game(self.game)
        self.assertEqual(9, bet.score)

    def test_team2_result(self):

        self.game.score_team1 = 0
        self.game.score_team2 = 1

        bet = BetGame(user=self.user, game=self.game, score_team1=1, score_team2=2)
        db.session.add(bet)
        db.session.commit()

        update_scores_by_game(self.game)
        self.assertEqual(9, bet.score)

    def test_draw(self):

        self.game.score_team1 = 0
        self.game.score_team2 = 0

        bet = BetGame(user=self.user, game=self.game, score_team1=1, score_team2=1)
        db.session.add(bet)
        db.session.commit()

        update_scores_by_game(self.game)
        self.assertEqual(9, bet.score)

    def test_only_score(self):

        self.game.score_team1 = 0
        self.game.score_team2 = 0

        bet1 = BetGame(user=self.user, game=self.game, score_team1=1, score_team2=0)
        bet2 = BetGame(user=self.user, game=self.game, score_team1=0, score_team2=1)
        db.session.add(bet1)
        db.session.add(bet2)
        db.session.commit()

        update_scores_by_game(self.game)
        self.assertEqual(3, bet1.score)
        self.assertEqual(3, bet2.score)


    def test_no_score(self):

        self.game.score_team1 = 0
        self.game.score_team2 = 0

        bet1 = BetGame(user=self.user, game=self.game, score_team1=1, score_team2=2)
        bet2 = BetGame(user=self.user, game=self.game, score_team1=2, score_team2=1)
        db.session.add(bet1)
        db.session.add(bet2)
        db.session.commit()

        update_scores_by_game(self.game)
        self.assertEqual(0, bet1.score)
        self.assertEqual(0, bet2.score)


    def test_user_without_bets(self):

        self.game.score_team1 = 1
        self.game.score_team2 = 0
        db.session.commit()

        update_scores_by_game(self.game)


    def test_update_score(self):

        self.game.score_team1 = 0
        self.game.score_team2 = 0

        bet = BetGame(user=self.user, game=self.game, score_team1=1, score_team2=1)
        db.session.add(bet)
        db.session.commit()

        update_scores_by_game(self.game)
        self.assertEqual(9, bet.score)

        self.game.score_team1 = 3
        self.game.score_team2 = 2
        db.session.commit()

        update_scores_by_game(self.game)
        self.assertEqual(0, bet.score)


class UpdateRankingTest(TestCase):

    def create_app(self):
        app = app_factory('Testing')
        return app

    def setUp(self):
        db.create_all()
        bra = Team(name='Brasil', alias='BRA')
        arg = Team(name='Argentina', alias='ARG')
        uru = Team(name='Uruguai', alias='URU')
        self.game1 = Game(team1=bra, team2=arg)
        self.game2 = Game(team1=bra, team2=uru)
        self.game3 = Game(team1=arg, team2=uru)
        db.session.add(self.game1)
        db.session.add(self.game2)
        db.session.add(self.game3)

        db.session.commit()


    def tearDown(self):
        db.session.remove()
        db.drop_all()



    def test_update_ranking(self):

        user1 = User(name="User1", email="user1@email.co", active=True)
        user2 = User(name="User2", email="user2@email.co", active=True)
        db.session.add(user1)
        db.session.add(user2)

        self.game1.score_team1 = 1
        self.game1.score_team2 = 1

        self.game2.score_team1 = 2
        self.game2.score_team2 = 0

        self.game3.score_team1 = 2
        self.game3.score_team2 = 1

        user1_bet1 = BetGame(user=user1, game=self.game1, score_team1=1, score_team2=1, score=18)
        user1_bet2 = BetGame(user=user1, game=self.game2, score_team1=1, score_team2=0, score=12)

        user2_bet1 = BetGame(user=user2, game=self.game1, score_team1=1, score_team2=0, score=3)
        user2_bet2 = BetGame(user=user2, game=self.game2, score_team1=2, score_team2=0, score=18)

        db.session.add(user1_bet1)
        db.session.add(user1_bet2)
        db.session.add(user2_bet1)
        db.session.add(user2_bet2)
        db.session.commit()

        update_ranking()

        self.assertEqual(30, user1.score_games)
        self.assertEqual(21, user2.score_games)

        ranking = User.ranking()
        self.assertEqual(user1.id, ranking[0].id)
        self.assertEqual(user2.id, ranking[1].id)

        user1_bet3 = BetGame(user=user1, game=self.game3, score_team1=0, score_team2=0, score=0)
        user2_bet3 = BetGame(user=user2, game=self.game3, score_team1=2, score_team2=1, score=18)
        db.session.add(user1_bet3)
        db.session.add(user2_bet3)
        db.session.commit()

        update_ranking()

        self.assertEqual(30, user1.score_games)
        self.assertEqual(39, user2.score_games)

        ranking = User.ranking()
        self.assertEqual(user2.id, ranking[0].id)
        self.assertEqual(user1.id, ranking[1].id)

