from flask import redirect, url_for, abort, request
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose

class MyAdminIndexView(AdminIndexView):
    column_display_pk = True # optional, but I like to see the IDs in the list
    column_hide_backrefs = False

    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('main.login'))
        elif current_user.username != 'egtquzr9':
            abort(403)
        return super(MyAdminIndexView, self).index()

class UserModelView(ModelView):
    column_display_pk = True # optional, but I like to see the IDs in the list
    column_hide_backrefs = False
    column_list = ["id","username","animes"]
    form_columns = ["id","username","animes"]

    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.username == 'egtquzr9':
                return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('main.login', next=request.url))

class AnimeModelView(ModelView):
    column_display_pk = True # optional, but I like to see the IDs in the list
    column_hide_backrefs = False
    column_list = ["id","name","user_id"]
    form_columns = ["id","name","user_id"]

    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.username == 'egtquzr9':
                return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('main.login', next=request.url))