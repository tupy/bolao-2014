# -*- coding: utf-8 -*-

import os
import flask

from flask.ext.admin import Admin
from flask.ext.login import LoginManager

login_manager = LoginManager()

def __import_variable(blueprint_path, module, variable_name):
    path = '.'.join(blueprint_path.split('.') + [module])
    mod = __import__(path, fromlist=[variable_name])
    return getattr(mod, variable_name)


def config_str_to_obj(cfg):
    if isinstance(cfg, basestring):
        module = __import__('bolao.config', fromlist=[cfg])
        return getattr(module, cfg)
    return cfg


def app_factory(config, app_name=None, blueprints=None):
    app_name = app_name or __name__
    app = flask.Flask(app_name)

    config = config_str_to_obj(config)
    configure_app(app, config)
    configure_before_requests(app)
    configure_blueprints(app, blueprints or config.BLUEPRINTS)
    configure_database(app)
    configure_extensions(app)
    configure_views(app)
    configure_admin(app)

    return app


def configure_app(app, config):
    """Loads configuration class into flask app"""
    app.config.from_object(config)
    app.config.from_envvar("APP_CONFIG", silent=True)  # available in the server


def configure_before_requests(app):

    from flask.ext.login import current_user

    @app.before_request
    def before_request():
        flask.g.user = current_user


def configure_blueprints(app, blueprints):
    """Registers all blueprints set up in config.py"""
    for blueprint_config in blueprints:
        blueprint, kw = None, {}

        if isinstance(blueprint_config, basestring):
            blueprint = blueprint_config
        elif isinstance(blueprint_config, tuple):
            blueprint = blueprint_config[0]
            kw = blueprint_config[1]
        else:
            print "Error in BLUEPRINTS setup in config.py"
            print "Please, verify if each blueprint setup is either a string or a tuple."
            exit(1)

        blueprint = __import_variable(blueprint, 'views', 'app')
        app.register_blueprint(blueprint, **kw)


def configure_database(app):
    """
    Database configuration should be set here
    """
    # uncomment for sqlalchemy support
    from .database import db
    db.app = app
    db.init_app(app)


def configure_extensions(app):
    """Configure extensions like mail and login here"""

    login_manager.init_app(app)
    login_manager.login_view = '.login'
    login_manager.login_message = u'Ops! Você ainda está deslogado.'
    login_manager.login_message_category = 'info'

    from bolao.models import User

    @login_manager.user_loader
    def load_user(userid):
        return User.query.get(userid)


def configure_views(app):


    @app.route('/favicon.ico')
    def favicon():
          return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                                 'favicon.ico', mimetype='image/vnd.microsoft.icon')

def configure_admin(app):

    from .admin import ModelView, IndexView, UserView
    admin = Admin(app, index_view=IndexView())

    from .models import User, Scorer, Team, Game
    from .models import BetGame, BetChampions, BetScorer
    from .database import db

    admin.add_view(UserView(User, db.session, u'Usuários'))
    admin.add_view(ModelView(Scorer, db.session, 'Artilheiros'))
    # admin.add_view(ModelView(Team, db.session, u'Seleções'))
    admin.add_view(ModelView(Game, db.session, 'Jogos'))
    # admin.add_view(ModelView(BetGame, db.session))
    # admin.add_view(ModelView(BetChampions, db.session))
    # admin.add_view(ModelView(BetScorer, db.session))
