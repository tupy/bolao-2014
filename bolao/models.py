

from bolao.database import db


class User(db.Model): 
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(150))
  email = db.Column(db.String(50), unique=True)
  score_games = db.Column(db.Integer, default=0)
  score_champions = db.Column(db.Integer, default=0)
  score_scorer = db.Column(db.Integer, default=0)
  
  def __repr__(self):
        return '<User %r>' % self.name

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
        return '<Artilheiro %r>' % self.name
  
class Game(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  label = db.Column(db.String(50))
  time = db.Column(db.DateTime())
  team1_id = db.Column(db.Integer, db.ForeignKey('team.id'))
  team1 = db.relationship('Team', foreign_keys=team1_id)
  team2_id = db.Column(db.Integer, db.ForeignKey('team.id'))
  team2 = db.relationship('Team', foreign_keys=team2_id)
  score_team1 = db.Column(db.Integer)
  score_team2 = db.Column(db.Integer)
