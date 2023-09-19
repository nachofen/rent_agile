from . import db
from flask_login import UserMixin


"""hacer una clase para cada tabla de la db"""


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    nombre = db.Column(db.String(150))
    apellido = db.Column(db.String(150))