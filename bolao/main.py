
import flask

from flask.ext.admin import Admin


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
    #configure_blueprints(app, blueprints or config.BLUEPRINTS)
    configure_database(app)
    configure_extensions(app)
 #   configure_views(app)

    return app


def configure_app(app, config):
    """Loads configuration class into flask app"""
    app.config.from_object(config)
    app.config.from_envvar("APP_CONFIG", silent=True)  # available in the server


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

    admin = Admin(app)

    from flask.ext.admin.contrib.sqla import ModelView
    from .models import Scorer, Team, Game, User
    from .database import db

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Scorer, db.session))
    admin.add_view(ModelView(Team, db.session))
    admin.add_view(ModelView(Game, db.session))
