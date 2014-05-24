# -*- coding: utf-8 -*-

import flask
from flask import render_template, request, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required, current_user

from bolao.models import User, Team, Game, BetGame, BetChampions
from bolao.database import db
from bolao.forms import LoginForm
from bolao.utils import generate_password_hash

app = flask.Blueprint('bolao', __name__)


@app.route('/')
def index():
  if current_user.is_anonymous():
    return redirect(url_for('.login'))
  return redirect(url_for('.games'))


@app.route('/jogos')
@login_required
def games():
  games = Game.query.order_by(Game.time)
  bets = BetGame.query.filter_by(user=current_user)
  bets = {bet.game_id:bet for bet in bets}
  return render_template('games.html', games=games, bets=bets)


@app.route('/apostar_jogo/<int:game_id>')
@login_required
def bet_game_view(game_id):
  game = Game.query.get(game_id)
  bet = BetGame.query.filter_by(game=game).first()
  return render_template('bet_game.html', game=game, bet=bet)


@app.route('/apostar_jogo', methods=["POST"])
@login_required
def bet_game():
  game_id = request.form.get('game_id')
  bet_id = request.form.get('bet_id')
  game = Game.query.get(game_id)

  if bet_id:
    bet = BetGame.query.get(bet_id)
  else:
    bet = BetGame(game=game, user=current_user)
    db.session.add(bet)
  bet.score_team1 = int(request.form.get('score_team1') or 0)
  bet.score_team2 = int(request.form.get('score_team2') or 0)
  db.session.commit()
  return redirect(url_for('.games'))


@app.route('/campeoes', methods=['GET', 'POST'])
@login_required
def bet_champions():

  bet = BetChampions.query.filter_by(user=current_user).first()

  if request.method == 'POST':
    if bet is None:
      bet = BetChampions(user=current_user)
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


@app.route("/login", methods=["GET", "POST"])
def login():
  if current_user.is_authenticated():
    return redirect('/')

  form = LoginForm()
  if form.validate_on_submit():
    # login and validate the user...
    email = form.email.data
    password = generate_password_hash(form.password.data)
    user = User.query.filter_by(email=email, password=password).first()
    if user:
      user.authenticated = True
      login_user(user, remember=True)
      # flask.flash("Logged in successfully.", category='success')
      return redirect(request.args.get("next") or url_for(".index"))
    flask.flash(u'Usuário ou senha inválidos.', category='danger')
  return render_template("login.html", form=form)


@app.route("/logout")
def logout():
  if current_user.is_authenticated():
    logout_user()
  return redirect('/')
