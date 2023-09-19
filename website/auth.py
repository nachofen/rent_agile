from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_required, login_user, logout_user, current_user

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

@auth.route('registro', methods=['GET', 'POST'])
def registro():
    """registro url"""
    if request.method == 'POST':
        email = request.form.get('email')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('ya existe una cuenta con este correo asosiado', category='error')
        elif len(email) < 4:
            flash('Email debe tener al menos 4 caracteres.', category='error')
        elif len(nombre) < 3:
            flash('Nombre debe tener al menos 3 caracteres.', category='error')
        elif len(apellido) < 3:
            flash('Apellido debe tener al menos 3 caracteres.', category='error')
        elif password != password2:
            flash('Las contraseñas no coinciden.', category='error')
        elif len(password) < 6:
            flash('Su contraseña debe tener al menos 6 caracteres.', category='error')
        elif len(password2) < 6:
            flash('Su contraseña debe tener almenos 6 caracteres.', category='error')
        else:
            #all info is correct so create user to database
            new_user = User(email=email, nombre=nombre, apellido=apellido, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Cuenta creada con exito! ya puedes iniciar sesión!', category='success')
            return redirect(url_for('views.home'))

    return render_template("registro.html", user=current_user)

