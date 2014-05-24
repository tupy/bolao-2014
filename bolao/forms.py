# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, Email


class LoginForm(Form):
    email = TextField('E-mail', validators=[Email(message=u"E-mail inválido")])
    password = PasswordField('Senha', validators=[DataRequired(message=u"Senha não informada")])
