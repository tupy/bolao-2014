# -*- coding: utf-8 -*-

from flask.ext.admin import BaseView, AdminIndexView, expose
from flask.ext.admin.contrib.sqla import ModelView as SQLAModelView
from flask.ext import login

from wtforms import PasswordField
from bolao.utils import generate_password_hash
from bolao.tasks import update_scores_by_game, update_ranking


class OnlyAdmin(BaseView):

    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.is_admin()


class IndexView(AdminIndexView, OnlyAdmin):

    @expose('/')
    def index(self):
        return self.render('admin/index.html')


class ModelView(SQLAModelView, OnlyAdmin):
    pass


class UserView(ModelView):
    form_excluded_columns = ('password', 'created_at', 'score_games', 'score_champions', 'score_scorer',
      'crit_exact', 'crit_game_result', 'crit_win_goals', 'crit_lose_goals',
      'games', 'bet_champions', 'bet_scorer')
    column_exclude_list = ('password',  'crit_exact', 'crit_game_result', 'crit_win_goals', 'crit_lose_goals')
    column_searchable_list = ('name', 'email')

    def scaffold_form(self):
        form_class = super(UserView, self).scaffold_form()
        form_class.password2 = PasswordField('New Password')
        return form_class

    def on_model_change(self, form, model, is_created):
        if len(model.password2):
            model.password = generate_password_hash(form.password2.data)


class GameView(ModelView):

    can_create = False
    can_delete = False
    page_size = 50
    column_default_sort = 'time'

    def on_model_change(self, form, model, is_created):
        if not is_created:
            update_scores_by_game(model)
            update_ranking()
