# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, Optional, Email, Length, EqualTo


class LoginForm(Form):
    email = TextField('E-mail', validators=[Email(u"E-mail inválido")])
    password = PasswordField('Senha', validators=[DataRequired(u"Senha não informada")])


class SignupForm(Form):
    name = TextField('Nome', validators=[DataRequired(u"Nome não informado")])
    email = TextField('E-mail', validators=[Email(u"E-mail inválido")])
    phone_number = TextField('Celular (Opcional)', validators=[Optional()])
    password = PasswordField('Senha', validators=[DataRequired(u"Senha não informada"), Length(min=5, message="Sua senha deve ter pelo menos 5 caracteres"), EqualTo('confirm_password', u'Senhas digitadas não conferem')])
    confirm_password = PasswordField('Confirme a senha', validators=[DataRequired(u"Por favor, confirme a senha")])
