# -*- coding: utf-8 -*-

from bolao.database import db
from flask.ext.login import UserMixin


class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(150))
  email = db.Column(db.String(50), unique=True)
  password = db.Column(db.String(50))
  active = db.Column(db.Boolean, default=False)
  admin = db.Column(db.Boolean, default=False)
  score_games = db.Column(db.Integer, default=0)
  games = db.relationship("BetGame", backref="user")
  bet_champions = db.relationship("BetChampions", uselist=False, backref="user")
  bet_scorer = db.relationship("BetScorer", uselist=False, backref="user")

  def is_admin(self):
    return self.admin

  def is_active(self):
    return self.active

  def __repr__(self):
    return self.name

class Team(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  alias = db.Column(db.String(3), unique=True)
  name = db.Column(db.String(80))

  def __repr__(self):
    return self.name

class Scorer(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80))
  image = db.Column(db.String(150))
  team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
  team = db.relationship('Team')

  def __repr__(self):
    return self.name


class Game(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  label = db.Column(db.String(50))
  group = db.Column(db.String(1))
  round = db.Column(db.Integer)
  time = db.Column(db.DateTime())
  place = db.Column(db.String(50))
  team1_id = db.Column(db.Integer, db.ForeignKey('team.id'))
  team1 = db.relationship('Team', foreign_keys=team1_id)
  team2_id = db.Column(db.Integer, db.ForeignKey('team.id'))
  team2 = db.relationship('Team', foreign_keys=team2_id)
  score_team1 = db.Column(db.Integer)
  score_team2 = db.Column(db.Integer)

  def __repr__(self):
    return u"%s vs %s" % (self.team1, self.team2)

class BetGame(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
  game = db.relationship('Game', foreign_keys=game_id)
  score_team1 = db.Column(db.Integer)
  score_team2 = db.Column(db.Integer)
  score = db.Column(db.Integer, default=0)


class BetChampions(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  first_id = db.Column(db.Integer, db.ForeignKey('team.id'))
  first = db.relationship('Team', foreign_keys=first_id)
  second_id = db.Column(db.Integer, db.ForeignKey('team.id'))
  second = db.relationship('Team', foreign_keys=second_id)
  third_id = db.Column(db.Integer, db.ForeignKey('team.id'))
  third = db.relationship('Team', foreign_keys=third_id)
  fourth_id = db.Column(db.Integer, db.ForeignKey('team.id'))
  fourth = db.relationship('Team', foreign_keys=fourth_id)
  score = db.Column(db.Integer, default=0)


class BetScorer(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  scorer1_id = db.Column(db.Integer, db.ForeignKey('scorer.id'))
  scorer1 = db.relationship('Scorer', foreign_keys=scorer1_id)
  scorer2_id = db.Column(db.Integer, db.ForeignKey('scorer.id'))
  scorer2 = db.relationship('Scorer', foreign_keys=scorer2_id)
  score = db.Column(db.Integer, default=0)
