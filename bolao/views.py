# -*- coding: utf-8 -*-

import flask
from flask import render_template, request, redirect, url_for, g
from flask.ext.login import login_user, logout_user, login_required

from bolao.models import User, Team, Game, Scorer
from bolao.models import BetGame, BetChampions, BetScorer
from bolao.database import db
from bolao.forms import LoginForm
from bolao.utils import generate_password_hash

app = flask.Blueprint('bolao', __name__)


@app.route('/')
def index():
  if g.user.is_anonymous():
    return redirect(url_for('.login'))
  return profile(g.user.id)


@app.route('/profile/<int:id>')
def profile(id):
  profile = User.query.get(id)
  return render_template('profile.html', profile=profile)


@app.route('/jogos')
@login_required
def games():
  games = Game.query.order_by(Game.time)
  bets = BetGame.query.filter_by(user=g.user)
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
    bet = BetGame(game=game, user=g.user)
    db.session.add(bet)
  bet.score_team1 = int(request.form.get('score_team1') or 0)
  bet.score_team2 = int(request.form.get('score_team2') or 0)
  db.session.commit()
  return redirect(url_for('.games'))


@app.route('/campeoes', methods=['GET', 'POST'])
@login_required
def bet_champions():

  bet = BetChampions.query.filter_by(user=g.user).first()

  if request.method == 'POST':
    if bet is None:
      bet = BetChampions(user=g.user)
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


@app.route('/artilheiros', methods=['GET', 'POST'])
@login_required
def bet_scorer():
  bet = BetScorer.query.filter_by(user=g.user).first()

  if request.method == 'POST':
    if bet is None:
      bet = BetScorer(user=g.user)
      db.session.add(bet)
    bet.scorer1_id = __get_scorer('scorer1')
    bet.scorer2_id = __get_scorer('scorer2')
    db.session.commit()
    flask.flash("Artilheiros salvos com sucesso!", category="success")
  scorers = Scorer.query.order_by(Scorer.name)
  teams = Team.query.order_by(Team.name)
  return render_template('bet_scorer.html', bet=bet, scorers=scorers, teams=teams)


def __get_scorer(name):
  value = request.form.get(name)
  if value == 'other':
    scorer_name = request.form.get('%s-other' % name)
    team_id = request.form.get('%s-team' % name)
    team = Team.query.get(team_id)
    scorer = Scorer(name=scorer_name, team=team)
    db.session.add(scorer)
    db.session.commit()
    return scorer.id
  return value


@app.route("/login", methods=["GET", "POST"])
def login():
  if g.user.is_authenticated():
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
  if g.user.is_authenticated():
    logout_user()
  return redirect('/')
