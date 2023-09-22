from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """login route"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Inicio de sesion correcto!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Contraseña incorrecta, intente de nuevo', category='error')
        else:
            flash('el email no es correcto, intente de nuevo', category='error')
    
    return render_template ('/login.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    """logout route"""
    logout_user()
    return redirect(url_for('auth.login'))

def es_mayor(fecha_nacimiento):
    if not fecha_nacimiento:
        flash('Debe seleccionar su fecha de nacimiento.', category='error')
        return False
    
    fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
    today = datetime.today().date()
    age = today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

    if age < 18:
        flash('Debe ser mayor de edad para registrarse.', category='error')
        return False

    return True

@auth.route('registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form.get('email')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        departamento = request.form.get('departamento')
        direccion = request.form.get('direccion')
        fecha_nacimiento = request.form.get('fecha_nacimiento')

        # Validar que se haya ingresado una fecha de nacimiento
        

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Ya existe una cuenta con este correo asociado.', category='error')
        elif len(email) < 4:
            flash('El correo electrónico debe tener al menos 4 caracteres.', category='error')
        elif len(nombre) < 3:
            flash('El nombre debe tener al menos 3 caracteres.', category='error')
        elif len(apellido) < 3:
            flash('El apellido debe tener al menos 3 caracteres.', category='error')
        elif password != password2:
            flash('Las contraseñas no coinciden.', category='error')
        elif len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', category='error')
        elif not es_mayor(fecha_nacimiento):
            return redirect(url_for('auth.registro'))
        else:
            # Todo está correcto, crear el usuario en la base de datos
            new_user = User(email=email, nombre=nombre, apellido=apellido, departamento=departamento, direccion=direccion, fecha_nacimiento=fecha_nacimiento, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('¡Cuenta creada con éxito! Ahora puedes iniciar sesión.', category='success')
            return redirect(url_for('views.home'))

    return render_template("registro.html", user=current_user)