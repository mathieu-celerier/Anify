from flask import current_app
from flask_login import UserMixin
from Anify import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}','{self.password}')"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    access_token = db.Column(db.String(60),unique=True)
    spotify_id = db.Column(db.String(60),unique=True)
    animes = db.relationship('AnimeSong', backref='owner', lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"

class AnimeSong(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"AnimeSongs('{self.name}','{self.user_id}')"