# -*- coding: utf-8 -*-
import pymysql
pymysql.install_as_MySQLdb()

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()


def drop_all():
    db.drop_all()


def create_all():
    db.create_all()


def remove_session():
    db.session.remove()

