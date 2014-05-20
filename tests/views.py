from flask.ext.testing import TestCase

from bolao.main import app_factory


class ViewsTest(TestCase):
    
    def create_app(self):

        app = app_factory('Testing')
        return app

    def test_games(self):
        response = self.client.get("/jogos")
        self.assert200(response)
#        self.assert_template_used('games.html')        
