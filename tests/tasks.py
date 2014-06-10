

from flask.ext.testing import TestCase

from bolao.models import Team, User, Game, BetGame
from bolao.main import app_factory
from bolao.tasks import update_scores_by_game
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
        self.assertEqual(18, self.user.score_games)

    def test_exact_draw(self):

        self.game.score_team1 = 1
        self.game.score_team2 = 1

        bet = BetGame(user=self.user, game=self.game, score_team1=1, score_team2=1)
        db.session.add(bet)
        db.session.commit()

        update_scores_by_game(self.game)
        self.assertEqual(18, bet.score)
        self.assertEqual(18, self.user.score_games)

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
        self.assertEqual(24, self.user.score_games)

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
        self.assertEqual(24, self.user.score_games)

    def test_team1_result(self):

        self.game.score_team1 = 1
        self.game.score_team2 = 0

        bet = BetGame(user=self.user, game=self.game, score_team1=2, score_team2=1)
        db.session.add(bet)
        db.session.commit()

        update_scores_by_game(self.game)
        self.assertEqual(9, bet.score)
        self.assertEqual(9, self.user.score_games)

    def test_team2_result(self):

        self.game.score_team1 = 0
        self.game.score_team2 = 1

        bet = BetGame(user=self.user, game=self.game, score_team1=1, score_team2=2)
        db.session.add(bet)
        db.session.commit()

        update_scores_by_game(self.game)
        self.assertEqual(9, bet.score)
        self.assertEqual(9, self.user.score_games)

    def test_draw(self):

        self.game.score_team1 = 0
        self.game.score_team2 = 0

        bet = BetGame(user=self.user, game=self.game, score_team1=1, score_team2=1)
        db.session.add(bet)
        db.session.commit()

        update_scores_by_game(self.game)
        self.assertEqual(9, bet.score)
        self.assertEqual(9, self.user.score_games)

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
        self.assertEqual(6, self.user.score_games)


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
        self.assertEqual(0, self.user.score_games)


    def test_user_without_bets(self):

        self.game.score_team1 = 1
        self.game.score_team2 = 0
        db.session.commit()

        update_scores_by_game(self.game)
        self.assertEqual(0, self.user.score_games)


    def test_update_score(self):

        self.game.score_team1 = 0
        self.game.score_team2 = 0

        bet = BetGame(user=self.user, game=self.game, score_team1=1, score_team2=1)
        db.session.add(bet)
        db.session.commit()

        update_scores_by_game(self.game)
        self.assertEqual(9, bet.score)
        self.assertEqual(9, self.user.score_games)

        self.game.score_team1 = 3
        self.game.score_team2 = 2
        db.session.commit()

        update_scores_by_game(self.game)
        self.assertEqual(0, bet.score)
        self.assertEqual(0, self.user.score_games)

