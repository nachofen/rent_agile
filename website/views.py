from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
import os
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db

views = Blueprint('views', __name__)

@views.route('/')
def home():
    """home url"""
    return render_template("index.html", user=current_user)

@views.route('/host')
@login_required
def admin_home():
    """admin home url"""
    return render_template("indexp.html", user=current_user)

@views.route('/agregar-vehiculo')
@login_required
def agregar_vehiculo():
    """add vehicle url"""
    return render_template("agregar-vehiculo.html", user=current_user)

departamentos = [
    "Artigas",
    "Canelones",
    "Cerro Largo",
    "Colonia",
    "Durazno",
    "Flores",
    "Florida",
    "Lavalleja",
    "Maldonado",
    "Montevideo",
    "Paysandú",
    "Río Negro",
    "Rivera",
    "Rocha",
    "Salto",
    "San José",
    "Soriano",
    "Tacuarembó",
    "Treinta y Tres"
]

@views.route('/mis-datos', methods=['GET', 'POST'])
@login_required
def update_info():
    """update personal information"""
    if request.method == 'POST':
        # Retrieve form data
        email = request.form.get('email')
        nombre = request.form.get('name')
        apellido = request.form.get('apellido')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        departamento = request.form.get('departamento')
        
        if len(email) < 4:
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
            # Update user information in the database
            current_user.email = email
            current_user.nombre = nombre
            current_user.apellido = apellido
            current_user.password = generate_password_hash(password, method='sha256')
            current_user.departamento = departamento
            # Commit the changes to the database
            db.session.commit()
            
            flash('Sus datos se han actualizado con exito!', category='success')
            return redirect(url_for('views.update_info'))

        # Redirect to a success page or user profile
        return redirect(url_for('views.update_info'))

    # Pass user data to the template
    return render_template('mis-datos.html', user=current_user, departamentos=departamentos)
