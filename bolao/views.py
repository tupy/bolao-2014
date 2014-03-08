
import flask
from flask import render_template
from bolao.models import Game

app = flask.Blueprint('bolao', __name__)


@app.route('/jogos')
def games():
  games = Game.query.order_by(Game.time)
  return render_template('games.html', games=games)
