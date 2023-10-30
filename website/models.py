
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
    telefono = db.Column(db.Integer)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    verificado = db.Column(db.Boolean, default=False)
    departamento = db.Column(db.String(150))
    direccion = db.Column(db.String(150))
    reviews = db.Column(db.Boolean, default=False)
    image_path = db.Column(db.String(255))
    autos = db.relationship('Auto', backref='owner', foreign_keys='Auto.usuario_id', lazy=True)
    mensajes_enviados = db.relationship('Mensaje', backref='remitente', foreign_keys='Mensaje.id_usuario', lazy='dynamic')


class Auto(db.Model):
    id_auto = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(150))
    matricula = db.Column(db.String(150))
    modelo = db.Column(db.String(150))
    año = db.Column(db.Integer)
    categoria = db.Column(db.String(150))
    departamento = db.Column(db.String(150))
    tarifa = db.Column(db.Float)
    descripcion = db.Column(db.Text)
    disponible = db.Column(db.Boolean, default=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mensajes = db.relationship('Mensaje', backref='auto_relacionado', foreign_keys='Mensaje.auto_id', lazy='dynamic')

class Imagenes_auto(db.Model):
    id_imagen = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(150))
    auto_id = db.Column(db.Integer, db.ForeignKey('auto.id_auto'))
    auto = db.relationship('Auto', backref='imagenes_auto')

class Mensaje(db.Model):
    id_mensaje = db.Column(db.Integer, primary_key=True)
    contenido_mensaje = db.Column(db.String(1500))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    id_usuario = db.Column(db.Integer, db.ForeignKey('user.id'))
    auto_id = db.Column(db.Integer, db.ForeignKey('auto.id_auto'))
    destinatario_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    conversacion_id = db.Column(db.Integer, db.ForeignKey('conversacion.id_conversacion'))
    conversacion = db.relationship('Conversacion', back_populates='mensajes')

class Conversacion(db.Model):
    id_conversacion = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    destinatario_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    auto_id = db.Column(db.Integer, db.ForeignKey('auto.id_auto'))
    mensajes = db.relationship('Mensaje', back_populates='conversacion')

class Reserva(db.Model):
    id_reserva = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('user.id'))
    id_auto = db.Column(db.Integer, db.ForeignKey('auto.id_auto'))
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    reseña = db.relationship('Reseña', backref='reserva', uselist=False)
    estado = db.Column(db.String(10), default="activa")

class Reseña(db.Model):
    id_resena = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reserva.id_reserva'))
    calificacion = db.Column(db.Integer)
    comentario = db.Column(db.Text)

class FechasBloqueadas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    auto_id = db.Column(db.Integer, db.ForeignKey('auto.id_auto'))
    auto = db.relationship('Auto', backref='fechas_bloqueadas')
