

from flask_testing import TestCase

from bolao.models import Team, User, Game, Scorer, BetScorer, BetGame, BetChampions
from bolao.main import app_factory
from bolao.tasks import (update_scores_by_game, update_ranking, update_ranking_criterias,
    update_scorer, update_champions)
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
        user2 = User(name="Test2", email="email2@test.co", active=True)
        db.session.add(user)
        db.session.add(user2)
        db.session.commit()

        self.game = game
        self.user = user
        self.user2 = user2

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
        bet2 = BetGame(user=self.user2, game=self.game, score_team1=1, score_team2=0)
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
        bet2 = BetGame(user=self.user2, game=self.game, score_team1=0, score_team2=1)
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
        bet2 = BetGame(user=self.user2, game=self.game, score_team1=0, score_team2=1)
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
        bet2 = BetGame(user=self.user2, game=self.game, score_team1=2, score_team2=1)
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
        chi = Team(name='Chile', alias='CHI')
        self.game1 = Game(team1=bra, team2=arg)
        self.game2 = Game(team1=bra, team2=uru)
        self.game3 = Game(team1=bra, team2=chi)
        self.game4 = Game(team1=arg, team2=uru)
        self.game5 = Game(team1=arg, team2=bra)
        self.game6 = Game(team1=arg, team2=chi)
        self.game7 = Game(team1=uru, team2=bra)
        self.game8 = Game(team1=uru, team2=arg)
        self.game9 = Game(team1=uru, team2=chi)

        db.session.add(self.game1)
        db.session.add(self.game2)
        db.session.add(self.game3)
        db.session.add(self.game4)
        db.session.add(self.game5)
        db.session.add(self.game6)
        db.session.add(self.game7)
        db.session.add(self.game8)

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


    def test_update_ranking_criterias(self):

        user = User(name="User", email="user@email.co", active=True)
        db.session.add(user)

        self.game1.score_team1 = 2
        self.game1.score_team2 = 0

        self.game2.score_team1 = 2
        self.game2.score_team2 = 2

        self.game3.score_team1 = 2
        self.game3.score_team2 = 0

        self.game4.score_team1 = 2
        self.game4.score_team2 = 0

        self.game5.score_team1 = 2
        self.game5.score_team2 = 0

        self.game6.score_team1 = 2
        self.game6.score_team2 = 0

        self.game7.score_team1 = 2
        self.game7.score_team2 = 2

        self.game8.score_team1 = 2
        self.game8.score_team2 = 2

        # exact (+game result, winner and loser goals)
        bet1 = BetGame(user=user, game=self.game1, score_team1=2, score_team2=0, score=18)
        # game result
        bet2 = BetGame(user=user, game=self.game2, score_team1=1, score_team2=1, score=9)
        bet3 = BetGame(user=user, game=self.game3, score_team1=3, score_team2=1, score=9)
        # game result and winner goal
        bet4 = BetGame(user=user, game=self.game4, score_team1=2, score_team2=1, score=12)
        # game result and loser goal
        bet5 = BetGame(user=user, game=self.game5, score_team1=3, score_team2=0, score=12)
        # winner goal
        bet6 = BetGame(user=user, game=self.game6, score_team1=2, score_team2=0, score=3)
        # looser goal
        bet7 = BetGame(user=user, game=self.game7, score_team1=0, score_team2=2, score=3)
        # none
        bet8 = BetGame(user=user, game=self.game8, score_team1=0, score_team2=2, score=0)

        db.session.add(bet1)
        db.session.add(bet2)
        db.session.add(bet3)
        db.session.add(bet4)
        db.session.add(bet5)
        db.session.add(bet6)
        db.session.add(bet7)
        db.session.add(bet8)
        db.session.commit()

        update_ranking_criterias(user)
        self.assertEqual(1, user.crit_exact)
        self.assertEqual(5, user.crit_game_result)
        self.assertEqual(3, user.crit_win_goals)
        self.assertEqual(3, user.crit_lose_goals)


class UpdateScorerTest(TestCase):

    def create_app(self):
        app = app_factory('Testing')
        return app

    def setUp(self):
        db.create_all()

        user = User(name="Test", email="email@test.co", active=True)
        db.session.add(user)

        bra = Team(name='Brasil', alias='BRA')
        arg = Team(name='Argentina', alias='ARG')
        db.session.add(bra)
        db.session.add(arg)

        fred = Scorer(name="Fred", team=bra)
        neymar = Scorer(name="Neymar", team=bra)
        messi = Scorer(name="Messi", team=arg)

        db.session.add(fred)
        db.session.add(neymar)
        db.session.add(messi)

        db.session.commit()

        self.user = user
        self.fred = fred
        self.neymar = neymar
        self.messi = messi

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_scorer1(self):

        bet = BetScorer(scorer1=self.fred, scorer2=self.neymar, user=self.user)
        db.session.add(bet)
        db.session.commit()

        self.fred.scorer = True
        update_scorer(self.fred)
        self.assertEqual(20, bet.score)
        self.assertEqual(20, self.user.score_total)

    def test_scorer2(self):

        bet = BetScorer(scorer1=self.fred, scorer2=self.neymar, user=self.user)
        db.session.add(bet)
        db.session.commit()

        self.neymar.scorer = True
        update_scorer(self.neymar)
        self.assertEqual(20, bet.score)
        self.assertEqual(20, self.user.score_total)

    def test_scorer1_and_scorer2(self):

        bet = BetScorer(scorer1=self.fred, scorer2=self.neymar, user=self.user)
        db.session.add(bet)
        db.session.commit()

        self.fred.scorer = True
        update_scorer(self.fred)
        self.neymar.scorer = True
        update_scorer(self.neymar)
        self.assertEqual(40, bet.score)
        self.assertEqual(40, self.user.score_total)

    def test_remove_scorer(self):
        self.fred.scorer = True
        self.neymar.scorer = True
        bet = BetScorer(scorer1=self.fred, scorer2=self.neymar, user=self.user)
        bet.score = 40
        db.session.add(bet)
        db.session.commit()

        self.fred.scorer = False
        update_scorer(self.fred)
        self.assertEqual(20, bet.score)
        self.assertEqual(20, self.user.score_total)

        self.neymar.scorer = False
        update_scorer(self.neymar)
        self.assertEqual(0, bet.score)
        self.assertEqual(0, self.user.score_total)

    def test_remove_no_scorer(self):
        self.fred.scorer = True
        self.neymar.scorer = True
        bet = BetScorer(scorer1=self.fred, scorer2=self.neymar, user=self.user)
        bet.score = 40
        self.user.score_total = 40
        db.session.add(bet)
        db.session.commit()

        self.messi.scorer = True
        update_scorer(self.messi)
        self.assertEqual(40, bet.score)
        self.assertEqual(40, self.user.score_total)

    def test_no_changes(self):
        self.fred.scorer = False
        self.neymar.scorer = True
        bet = BetScorer(scorer1=self.fred, scorer2=self.neymar, user=self.user)
        bet.score = 20
        self.user.score_total = 20
        db.session.add(bet)
        db.session.commit()

        self.fred.scorer = False
        update_scorer(self.fred)
        self.assertEqual(20, bet.score)
        self.assertEqual(20, self.user.score_total)


class UpdateChampionsTest(TestCase):

    def create_app(self):
        app = app_factory('Testing')
        return app

    def setUp(self):
        db.create_all()

        user = User(name="Test", email="email@test.co", active=True)
        db.session.add(user)

        bra = Team(name='Brasil', alias='BRA')
        arg = Team(name='Argentina', alias='ARG')
        uru = Team(name='Uruguai', alias='URU')
        ale = Team(name='Alemanha', alias='ALE')
        usa = Team(name='Estados Unidos', alias='USA')
        db.session.add(bra)
        db.session.add(arg)
        db.session.add(uru)
        db.session.add(ale)
        db.session.add(usa)

        db.session.commit()

        self.user = user
        self.bra = bra
        self.arg = arg
        self.uru = uru
        self.ale = ale
        self.usa = usa

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_exact_positions(self):

        bet = BetChampions(first=self.bra, second=self.arg, third=self.ale, fourth=self.uru, user=self.user)
        db.session.add(bet)
        db.session.commit()

        update_champions(self.bra, self.arg, self.ale, self.uru)

        self.assertEqual(40, bet.score)
        self.assertEqual(40, self.user.score_total)

    def test_only_positions(self):

        bet = BetChampions(first=self.bra, second=self.arg, third=self.ale, fourth=self.uru, user=self.user)
        db.session.add(bet)
        db.session.commit()

        update_champions(self.uru, self.ale, self.arg, self.bra)

        self.assertEqual(20, bet.score)
        self.assertEqual(20, self.user.score_total)

    def test_mixed_positions(self):

        bet = BetChampions(first=self.ale, second=self.arg, third=self.bra, fourth=self.uru, user=self.user)
        db.session.add(bet)
        db.session.commit()

        update_champions(self.bra, self.usa, self.arg, self.uru)

        self.assertEqual(20, bet.score)
        self.assertEqual(20, self.user.score_total)

    def test_any_position(self):

        t1 = Team(name="T1", alias="T1")
        t2 = Team(name="T2", alias="T2")
        t3 = Team(name="T3", alias="T3")
        t4 = Team(name="T4", alias="T4")

        db.session.add(t1)
        db.session.add(t2)
        db.session.add(t3)
        db.session.add(t4)

        bet = BetChampions(first=self.bra, second=self.arg, third=self.ale, fourth=self.uru, user=self.user)
        db.session.add(bet)
        db.session.commit()

        update_champions(t1, t2, t3, t4)

        self.assertEqual(0, bet.score)


    def test_raises_with_none(self):
        bet = BetChampions(first=self.bra, second=self.arg, third=self.ale, fourth=self.uru, user=self.user)
        db.session.add(bet)
        db.session.commit()

        self.assertRaises(AssertionError, update_champions, None, None, None, None)

