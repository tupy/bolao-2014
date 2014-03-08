
import flask

from flask.ext.admin import Admin


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
    configure_blueprints(app, blueprints or config.BLUEPRINTS)
    configure_database(app)
    configure_extensions(app)
 #   configure_views(app)

    return app


def configure_app(app, config):
    """Loads configuration class into flask app"""
    app.config.from_object(config)
    app.config.from_envvar("APP_CONFIG", silent=True)  # available in the server


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

    admin = Admin(app)

    from flask.ext.admin.contrib.sqla import ModelView
    from .models import Scorer, Team, Game, User
    from .database import db

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Scorer, db.session))
    admin.add_view(ModelView(Team, db.session))
    admin.add_view(ModelView(Game, db.session))
