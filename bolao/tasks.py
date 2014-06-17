
from collections import Counter
from sqlalchemy import func, select, and_, or_

from bolao.database import db
from bolao.models import BetGame, User

EXACT_RESULT = 18
RESULT_AND_A_SCORE = 12
ONLY_RESULT = 9
ONLY_ONE_SCORE = 3


def update_scores_by_game(game):

    bets = BetGame.query.filter_by(game=game)

    for bet in bets:
        if bet.score_team1 == game.score_team1 and bet.score_team2 == game.score_team2:
            bet.score = EXACT_RESULT
        elif (bet.score_team1 > bet.score_team2 and game.score_team1 > game.score_team2) or \
             (bet.score_team1 < bet.score_team2 and game.score_team1 < game.score_team2) or \
             (bet.score_team1 == bet.score_team2 and game.score_team1 == game.score_team2):
            bet.score = ONLY_RESULT
            if bet.score_team1 == game.score_team1 or bet.score_team2 == game.score_team2:
                bet.score = RESULT_AND_A_SCORE
        elif bet.score_team1 == game.score_team1 or bet.score_team2 == game.score_team2:
            bet.score = ONLY_ONE_SCORE
        else:
            bet.score = 0  # force update

    db.session.commit()


def update_ranking():
    for user in User.ranking():
        user.score_games = db.session.query(func.sum(BetGame.score)).filter_by(user=user).scalar() or 0
        update_ranking_criterias(user)

    db.session.commit()


def update_ranking_criterias(user):
    criterias = compute_criterias(user)
    user.crit_exact = criterias.get('exact', 0)
    user.crit_game_result = criterias.get('game_result', 0)
    user.crit_win_goals = criterias.get('win_goals', 0)
    user.crit_lose_goals = criterias.get('lose_goals', 0)


def compute_criterias(user):

    criterias = Counter()
    bets = BetGame.query.filter_by(user=user)
    for bet in bets:
        if bet.score == EXACT_RESULT:
            criterias['exact'] += 1
            criterias['game_result'] += 1
        elif bet.score == RESULT_AND_A_SCORE or bet.score == ONLY_RESULT:
            criterias['game_result'] += 1

        # this criteria is not valid just for draw
        if bet.game.score_team1 != bet.game.score_team2:
            home_is_winner = bet.game.score_team1 > bet.game.score_team2
            if (home_is_winner and bet.score_team1 == bet.game.score_team1) or \
                  (not home_is_winner and bet.score_team2 == bet.game.score_team2):
                criterias['win_goals'] += 1
            # also scores for exact match
            if (home_is_winner and bet.score_team2 == bet.game.score_team2) or \
                  (not home_is_winner and bet.score_team1 == bet.game.score_team1):
                criterias['lose_goals'] += 1

    return criterias

