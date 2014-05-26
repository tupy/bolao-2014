# -*- coding: utf-8 -*-

import datetime
import flask

from flask.ext.testing import TestCase

from bolao.main import app_factory
from bolao.database import db
from bolao.models import Game, Team, User


class ViewsTest(TestCase):

    def create_app(self):
        app = app_factory('Testing')
        return app

    def setUp(self):

        db.create_all()
        self.user = User(name="Test", email="email@test.co")
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):

        db.session.remove()
        db.drop_all()

    def test_games(self):

        bra = Team(name="Brasil", alias="BRA")
        usa = Team(name="United States", alias="USA")
        now = datetime.datetime.utcnow()
        game = Game(team1=bra, team2=usa, time=now)
        db.session.add(bra)
        db.session.add(usa)
        db.session.add(game)
        db.session.commit()

        with self.client.session_transaction() as sess:
          sess['user_id'] = self.user.id

        response = self.client.get("/jogos")
        self.assert200(response)
        self.assertIn('BRA', response.data)
        self.assertIn('USA', response.data)
#        self.assert_template_used('games.html')
