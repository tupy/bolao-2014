# -*- coding:utf-8 -*-

from flask.ext import script
from flask.ext.script import Command

from bolao.database import create_all, drop_all

class CreateDB(Command):
    """
    Creates database using SQLAlchemy
    """

    def run(self):
        create_all()


class DropDB(Command):
    """
    Drops database using SQLAlchemy
    """

    def run(self):
        drop_all()


if __name__ == "__main__":
    from bolao.main import app_factory

    manager = script.Manager(app_factory)
    manager.add_option("-c", "--config", dest="config", required=False, default='Dev')
    manager.add_command("create_db", CreateDB())
    manager.add_command("drop_db", DropDB())
    manager.run()
