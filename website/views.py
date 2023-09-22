from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
import os
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from werkzeug.utils import secure_filename

views = Blueprint('views', __name__)
UPLOAD_FOLDER = os.path.abspath('website/static/img/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """to validate allowed extensions"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@views.route('/perfil')
@login_required
def perfil_usuario():
    """perfil de usuario"""
    print(current_user.nombre)
    return render_template("perfil.html", user=current_user)

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
UPLOAD_FOLDER = 'website/static/img/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Función para validar extensiones de archivo permitidas"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/mis-datos', methods=['GET', 'POST'])
@login_required
def update_info():
    if request.method == 'POST':
        # Obtener datos del formulario
        email = request.form.get('email')
        nombre = request.form.get('name')
        apellido = request.form.get('apellido')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        departamento = request.form.get('departamento')
        direccion = request.form.get('direccion')
        
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
            flash('Su contraseña debe tener al menos 6 caracteres.', category='error')
        else:
            if 'image' in request.files:
                image = request.files['image']
                if image.filename != '' and allowed_file(image.filename):
                    # Guarda la imagen en el directorio UPLOAD_FOLDER
                    filename = f"{current_user.id}_profile.jpg"
                    image.save(os.path.join(UPLOAD_FOLDER, filename))
                    current_user.image_path = os.path.join('static/img/uploads', filename)
                    

            # Actualiza la información del usuario en la base de datos
            current_user.email = email
            current_user.nombre = nombre
            current_user.apellido = apellido
            current_user.password = generate_password_hash(password, method='sha256')
            current_user.departamento = departamento
            current_user.direccion = direccion
            # Commit los cambios en la base de datos
            db.session.commit()
            
            flash('Sus datos se han actualizado con éxito!', category='success')
            return redirect(url_for('views.update_info'))

    # Pasa los datos del usuario a la plantilla
    return render_template('mis-datos.html', user=current_user, departamentos=departamentos)