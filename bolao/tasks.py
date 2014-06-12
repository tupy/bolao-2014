
from sqlalchemy import func

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

    db.session.commit()
