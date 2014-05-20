
import flask
from flask import render_template, request, redirect, url_for
from bolao.models import User, Team, Game, BetGame, BetChampions
from database import db

app = flask.Blueprint('bolao', __name__)

def get_current_user():
  return User.query.get(1)

@app.route('/jogos')
def games():
  user = get_current_user()
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
  user = get_current_user()
  game = Game.query.get(game_id)

  if bet_id:
    bet = BetGame.query.get(bet_id)
  else:
    bet = BetGame(game=game, user=user)
    db.session.add(bet)
  bet.score_team1 = int(request.form.get('score_team1') or 0)
  bet.score_team2 = int(request.form.get('score_team2') or 0)
  db.session.commit()
  return redirect(url_for('.games'))


@app.route('/campeoes', methods=['GET', 'POST'])
def bet_champions():

  user = get_current_user()
  bet = BetChampions.query.filter_by(user=user).first()

  if request.method == 'POST':
    if bet is None:
      bet = BetChampions(user=user)
      db.session.add(bet)
    bet.first_id = request.form.get('first')
    bet.second_id = request.form.get('second')
    bet.third_id = request.form.get('third')
    bet.fourth_id = request.form.get('fourth')
    db.session.commit()
 
  if bet and request.args.get('edit') != 'edit':
    return render_template('bet_champions_short.html', bet=bet)
    
  teams = Team.query.order_by(Team.name)
  return render_template('bet_champions_full.html', teams=teams, bet=bet)


