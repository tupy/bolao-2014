
import flask
from flask import render_template, request, redirect, url_for
from bolao.models import User, Game, BetGame
from database import db

app = flask.Blueprint('bolao', __name__)


@app.route('/jogos')
def games():
  user = User.query.get(1)
  games = Game.query.order_by(Game.time)
  bets = BetGame.query.filter_by(user=user)
  bets = {bet.game_id:bet for bet in bets}
  return render_template('games.html', games=games, bets=bets)


@app.route('/apostar_jogo/<int:game_id>')
def bet_game_view(game_id):
  game = Game.query.get(game_id)
  bet = BetGame.query.filter_by(game=game).first()
  return render_template('bet_game.html', game=game, bet=bet)
 

@app.route('/apostar_jogo', methods=["POST"])
def bet_game():
  game_id = request.form.get('game_id')
  bet_id = request.form.get('bet_id')
  game = Game.query.get(game_id)
  user = User.query.get(1)

  if bet_id:
    bet = BetGame.query.get(bet_id)
  else:
    bet = BetGame(game=game, user=user)
    db.session.add(bet)
  bet.score_team1 = int(request.form.get('score_team1') or 0)
  bet.score_team2 = int(request.form.get('score_team2') or 0)
  db.session.commit()
  return redirect(url_for('.games'))

