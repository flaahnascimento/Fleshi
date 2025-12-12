from email.policy import default

from flask_login import UserMixin

from appfleshi import db, login_manager
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

@login_manager.user_loader # consultando se tem ou não aquele usuário
def load_user(user_id):
    return User.query.get(int(user_id)) # consultado a tabela do banco



class User(db.Model, UserMixin):
    #metodo do banco de dados()
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    photos = db.relationship("Photo", backref="user", lazy=True) #lista de fotos, cada foto é um objeto
    likes = db.relationship("Like", backref="user", lazy=True)
    reposts = db.relationship("Repost", backref="user", lazy=True)
    comments = db.relationship("Comment", backref="user", lazy=True)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), default="default.png")
    upload_date = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    reposts = db.relationship("Repost", backref="photo", lazy=True, cascade="all, delete-orphan"
    )
    likes = db.relationship("Like", backref="photo", lazy=True, cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="photo", lazy=True, cascade="all, delete-orphan"
    )

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    photo_id = db.Column(db.Integer, db.ForeignKey("photo.id"), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False) # texto comentario
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False) # quem comentou
    photo_id = db.Column(db.Integer, db.ForeignKey("photo.id"), nullable=False) # qual foto comentada

class Repost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False) # quem comentou
    photo_id = db.Column(db.Integer, db.ForeignKey("photo.id"), nullable=False) # qual foto comentada

