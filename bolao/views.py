# -*- coding: utf-8 -*-

import flask

from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from datetime import datetime
from flask import render_template, request, redirect, url_for, g
from flask.ext.login import login_user, logout_user, login_required
from collections import OrderedDict

from bolao.database import db
from bolao.models import User, Team, Game, Scorer
from bolao.models import BetGame, BetChampions, BetScorer
from bolao.forms import LoginForm, SignupForm
from bolao.utils import generate_password_hash

app = flask.Blueprint('bolao', __name__)

INACTIVE_USER_MESSAGE = u'Apenas usuários autorizados podem reliazar apostas. Por favor, entre em <a href="/sobre">contato com a organização</a>'
WELCOME_MESSAGE = u'Bem-vindo ao Bolão RIACHAO.COM. Aguarde instruções por e-mail para ativar sua conta.'


@app.route('/')
def index():
    if g.user.is_anonymous():
        return redirect(url_for('.login'))
    return profile(g.user.id)


@app.route('/profile/<int:id>')
def profile(id):
    profile = User.query.get(id)
    # show only expired games for visitor
    if g.user.get_id() != str(id):  # See Flask-Login reference
        profile.games = [bet for bet in profile.games if __is_game_expired(bet.game)]
    return render_template('profile.html', profile=profile)


@app.route('/ranking')
def ranking():
    return render_template('ranking.html', users=User.ranking())


@app.route('/estatistica')
def statistics():
    games = Game.query.order_by(Game.time).all()

    from sqlalchemy import select
    query = select([
      BetGame.game_id,
      func.count(func.IF(BetGame.score_team1>BetGame.score_team2,1,None)).label("team1"),
      func.count(func.IF(BetGame.score_team1==BetGame.score_team2,1,None)).label("draw"),
      func.count(func.IF(BetGame.score_team1<BetGame.score_team2,1,None)).label("team2"),
    ], group_by=BetGame.game_id).alias("game_stats")

    game_stats = db.session.query(query).all()
    game_stats = {x.game_id:x for x in game_stats}
    return render_template("statistics.html", games=games, game_stats=game_stats)


@app.route('/jogos')
@login_required
def games():
    games = Game.query.order_by(Game.time)
    games_by_day = __group_by_day(games)
    bets = BetGame.query.filter_by(user=g.user)
    bets = {bet.game_id:bet for bet in bets}
    return render_template('games.html', games_by_day=games_by_day, bets=bets)


def __group_by_day(games):
    groups = OrderedDict()
    for game in games:
        key = game.time.date()
        if key in groups:
            groups[key].append(game)
        else:
           groups[key] = [game]
    return groups

def __is_game_expired(game):
    return datetime.now() > game.time + flask.current_app.config['BOLAO_BET_GAME_LIMIT']


@app.route('/apostar_jogo/<int:game_id>')
@login_required
def bet_game_view(game_id):
    if not g.user.is_active():
        flask.flash(INACTIVE_USER_MESSAGE, category='warning')
        return redirect(url_for('.games'))

    game = Game.query.get(game_id)
    if __is_game_expired(game):
        flask.flash(u'O prazo para apostar em <strong>%s</strong> expirou.' % game, category='warning')
        return redirect(url_for('.games'))
    bet = BetGame.query.filter_by(user=g.user, game=game).first()
    return render_template('bet_game.html', game=game, bet=bet)


@app.route('/apostar_jogo', methods=["POST"])
@login_required
def bet_game():
    game_id = request.form.get('game_id')
    bet_id = request.form.get('bet_id')
    game = Game.query.get(game_id)

    if __is_game_expired(game):
        flask.flash(u'O prazo para apostar em <strong>%s</strong> expirou.' % game, category='warning')
        return redirect(url_for('.games'))

    if bet_id:
        bet = BetGame.query.get(bet_id)
        bet.updated_at = datetime.now()
    else:
        try:
            bet = BetGame(game=game, user=g.user)
            db.session.add(bet)
            db.session.flush()
        except IntegrityError, e:
            db.session.rollback()
            bet = BetGame.query.filter_by(user=g.user, game=game).first()
            bet.updated_at = datetime.now()

    bet.score_team1 = int(request.form.get('score_team1') or 0)
    bet.score_team2 = int(request.form.get('score_team2') or 0)
    db.session.commit()
    return redirect(url_for('.games', _anchor='game-%s' % game_id))


@app.route('/campeoes', methods=['GET', 'POST'])
@login_required
def bet_champions():

    if datetime.now() > flask.current_app.config['BOLAO_BET_CHAMPIONS_LIMIT']:
        flask.flash(u'O prazo para escolher as primeiras colocadas expirou.', category='warning')
        return redirect(url_for('.index'))
    elif not g.user.is_active():
        flask.flash(INACTIVE_USER_MESSAGE, category='warning')
        return redirect(url_for('.index'))

    bet = BetChampions.query.filter_by(user=g.user).first()

    if request.method == 'POST':
        if bet:
            bet.updated_at = datetime.now()
        else:
            bet = BetChampions(user=g.user)
            db.session.add(bet)
        bet.first_id = request.form.get('first')
        bet.second_id = request.form.get('second')
        bet.third_id = request.form.get('third')
        bet.fourth_id = request.form.get('fourth')
        db.session.commit()

    if bet is None or (bet and request.args.get('edit') == 'edit'):
        teams = Team.query.order_by(Team.name)
        return render_template('bet_champions_full.html', teams=teams, bet=bet)

    return render_template('bet_champions_short.html', bet=bet)


@app.route('/artilheiros', methods=['GET', 'POST'])
@login_required
def bet_scorer():
    if datetime.now() > flask.current_app.config['BOLAO_BET_SCORER_LIMIT']:
        flask.flash(u'O prazo para escolher os artilheiros expirou.', category='warning')
        return redirect(url_for('.index'))
    elif not g.user.is_active():
        flask.flash(INACTIVE_USER_MESSAGE, category='warning')
        return redirect(url_for('.index'))

    bet = BetScorer.query.filter_by(user=g.user).first()

    if request.method == 'POST':
        if bet:
            bet.updated_at = datetime.now()
        else:
            bet = BetScorer(user=g.user)
            db.session.add(bet)
        bet.scorer1_id = request.form.get('scorer1')
        bet.scorer2_id = request.form.get('scorer2')
        db.session.commit()
        flask.flash("Artilheiros salvos com sucesso!", category="success")
    scorers = Scorer.query.order_by(Scorer.name)
    teams = Team.query.order_by(Team.name)
    return render_template('bet_scorer.html', bet=bet, scorers=scorers, teams=teams)


@app.route('/ajax/add_scorer', methods=['POST'])
@login_required
def add_scorer():
    name = request.form.get('name')
    team_id = request.form.get('team')
    team = Team.query.get(team_id)
    scorer = Scorer(name=name, team=team)
    db.session.add(scorer)
    db.session.commit()
    return flask.jsonify({"success": True, "scorer_id": scorer.id})


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user.is_authenticated():
        return redirect('/')

    form = LoginForm()
    if form.validate_on_submit():
        # login and validate the user...
        email = form.email.data.lower()
        password = generate_password_hash(form.password.data)
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            user.authenticated = True
            login_user(user, remember=True, force=True)  # force login for inactive users
            # flask.flash("Logged in successfully.", category='success')
            return redirect(request.args.get("next") or url_for(".index"))
        flask.flash(u'Usuário ou senha inválidos.', category='danger')
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    if g.user.is_authenticated():
        logout_user()
    return redirect('/')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignupForm(request.form)
    if form.validate_on_submit():
        user = User()
        user.name = form.name.data
        user.email = form.email.data.lower()
        user.password = generate_password_hash(form.password.data)
        user.phone_number = form.phone_number.data
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True, force=True)
        flask.flash(WELCOME_MESSAGE, category='info')
        return redirect(url_for('.index'))
    return render_template('signup.html', form=form)


@app.route('/como-funciona', defaults={"template": 'como_funciona.html'}, endpoint='comofunciona')
@app.route('/sobre', defaults={"template": 'sobre.html'}, endpoint='sobre')
def page(template):
    return render_template(template)

