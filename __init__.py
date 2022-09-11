import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.menu import MenuLink
from Anify.config import Config
from Anify.views import MyAdminIndexView, UserModelView, AnimeModelView

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
admin = Admin(name='Anify', index_view=MyAdminIndexView(), template_mode='bootstrap3')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.debug = False
    app.config.from_object(Config)

    from Anify.routes import main
    from Anify.models import User, AnimeSong

    db.init_app(app)
    login_manager.init_app(app)
    admin.init_app(app)
    admin.add_link(MenuLink(name='Logout', category='', url="/logout"))
    admin.add_link(MenuLink(name='Back to site', category='', url="/"))
    admin.add_view(UserModelView(User,db.session))
    admin.add_view(AnimeModelView(AnimeSong, db.session))

    app.register_blueprint(main)

    with app.app_context():
        db.create_all(app=app)
        # app.app_context().push()
        from Anify.models import Admin
        admin_user = Admin(username="egtquzr9",password="hn9zm")
        db.session.add(admin_user)
        admin_user = Admin(username="naruto",password="hewath")
        db.session.add(admin_user)
        db.session.commit()

    return app