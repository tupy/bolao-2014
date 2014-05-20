

from bolao.database import db


class User(db.Model): 
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(150))
  email = db.Column(db.String(50), unique=True)
  score_games = db.Column(db.Integer, default=0)
  score_champions = db.Column(db.Integer, default=0)
  score_scorer = db.Column(db.Integer, default=0)
  
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
  user = db.relationship('User', foreign_keys=user_id)
  game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
  game = db.relationship('Game', foreign_keys=game_id)
  score_team1 = db.Column(db.Integer)
  score_team2 = db.Column(db.Integer)


class BetChampions(db.Model): 
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  user = db.relationship('User', foreign_keys=user_id)
  first_id = db.Column(db.Integer, db.ForeignKey('team.id'))
  first = db.relationship('Team', foreign_keys=first_id)
  second_id = db.Column(db.Integer, db.ForeignKey('team.id'))
  second = db.relationship('Team', foreign_keys=second_id)
  third_id = db.Column(db.Integer, db.ForeignKey('team.id'))
  third = db.relationship('Team', foreign_keys=third_id)
  fourth_id = db.Column(db.Integer, db.ForeignKey('team.id'))
  fourth = db.relationship('Team', foreign_keys=fourth_id)
