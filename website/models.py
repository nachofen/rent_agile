from . import db
from flask_login import UserMixin
from datetime import datetime


"""hacer una clase para cada tabla de la db"""


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    nombre = db.Column(db.String(150))
    apellido = db.Column(db.String(150))
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    verificado = db.Column(db.Boolean, default=False)
    departamento = db.Column(db.String(150))
    direccion = db.Column(db.String(150))
    reviews = db.Column(db.Boolean, default=False)
    image_path = db.Column(db.String(255))

