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
    
    try:
        fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
    except ValueError:
        flash('Formato de fecha de nacimiento inválido. Utilice YYYY-MM-DD.', category='error')
        return False

    today = datetime.today().date()
    age = today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    if fecha_nacimiento > today:
        return False
    elif age < 18:
        flash('debe ser mayor de edad para registrarse', category='error')
        return False

    return True

def contiene_numero(cadena):
    """verificar que no haya numeros en un campo de solo texto"""
    for caracter in cadena:
        # Verifica si el carácter es un dígito numérico
        if caracter.isdigit():
            return True
    # Si no se encontraron dígitos numéricos en la cadena
    return False

@auth.route('registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form.get('email')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        telefono = request.form.get('telefono')
        departamento = request.form.get('departamento')
        direccion = request.form.get('direccion')
        fecha_nacimiento = request.form.get('fecha_nacimiento')

        # Validar que se haya ingresado una fecha de nacimiento
        

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Ya existe una cuenta con este correo asociado.', category='error')
        elif len(email) < 4:
            flash('El correo electrónico debe tener al menos 4 caracteres.', category='error')
        elif contiene_numero(nombre):
            flash('El nombre no puede contenter numeros', category='error')
        elif len(nombre) < 3:
            flash('El nombre debe tener al menos 3 caracteres.', category='error')
        elif contiene_numero(apellido):
            flash('El apellido no puede contenter numeros', category='error')
        elif len(apellido) < 3:
            flash('El apellido debe tener al menos 3 caracteres.', category='error')
        elif password != password2:
            flash('Las contraseñas no coinciden.', category='error')
        elif len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', category='error')
        elif not es_mayor(fecha_nacimiento):
            flash('La fecha que utilizaste no esta disponible aun', category='error')
        else:
            # Todo está correcto, crear el usuario en la base de datos
            new_user = User(email=email, nombre=nombre, apellido=apellido, departamento=departamento, direccion=direccion, telefono=telefono, fecha_nacimiento=fecha_nacimiento, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('¡Cuenta creada con éxito! Ahora puedes iniciar sesión.', category='success')
            return redirect(url_for('auth.login'))

    return render_template("registro.html", user=current_user)