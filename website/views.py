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

@views.route('/agregar-vehiculo', methods=['GET', 'POST'])
@login_required
def agregar_vehiculo():
    """add vehicle url"""
    from .models import Auto, Imagenes_auto

    if request.method == 'POST':
        # Obtener datos del formulario
        marca = request.form.get('marca')
        modelo = request.form.get('modelo')
        año = request.form.get('año')
        categoria = request.form.get('categoria')
        departamento = request.form.get('departamento')
        tarifa = request.form.get('tarifa')
        descripcion = request.form.get('descripcion')

        nuevo_vehiculo = Auto(
            marca=marca,
            modelo=modelo,
            año=año,
            categoria=categoria,
            departamento=departamento,
            tarifa=tarifa,
            descripcion=descripcion,
            usuario_id=current_user.id  # Asociar el vehículo al usuario actual
        )

        # Agregar el nuevo vehículo a la lista de vehículos del usuario
        current_user.autos.append(nuevo_vehiculo)

        # Guardar provisionalmente el nuevo vehículo en la sesión de SQLAlchemy
        db.session.add(nuevo_vehiculo)
        db.session.commit()  # El vehículo se insertará en la base de datos y se generará el ID automáticamente

        auto = Auto.query.get(nuevo_vehiculo.id_auto)

        # Procesar la carga de imágenes
        for image in request.files.getlist('images[]'):
            if image.filename != '' and allowed_file(image.filename):
                # Guardar la imagen en el directorio UPLOAD_FOLDER
                filename = secure_filename(image.filename)
                unique_filename = f"auto_{str(auto.id_auto)}_{filename}"  # Nombre único de archivo
                image.save(os.path.join(UPLOAD_FOLDER, unique_filename))

                # Crear una entrada en la tabla Imagenes_auto para la imagen
                nueva_imagen = Imagenes_auto(url=os.path.join('static/img/uploads', unique_filename), auto=auto)
                db.session.add(nueva_imagen)

        # Commit los cambios en la base de datos
        db.session.commit()

        flash('El nuevo vehículo se ha agregado con éxito!', category='success')
        return redirect(url_for('views.agregar_vehiculo'))

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
                    filename = f"{current_user.id}_{secure_filename(image.filename)}"
                    image.save(os.path.join(UPLOAD_FOLDER, filename))
                    # Crear una URL relativa para la imagen
                    relative_url = os.path.join('static/img/uploads', filename)

                    # Actualizar el campo image_path del usuario
                    current_user.image_path = relative_url
                    

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

@views.route('/mis-vehiculos')
@login_required
def mis_vehiculos():
    """ list the cars of loged user"""
    vehiculos = current_user.autos

    return render_template("mis-vehiculos.html", user=current_user, vehiculos=vehiculos)

@views.route('/ver-vehiculo/<int:id>', methods=['GET', 'POST'])
@login_required
def mostrar_vehiculo(id):
    """shows one car by id"""
    from .models import Auto, Imagenes_auto
    vehiculo = Auto.query.get_or_404(id)
    imagenes_url = [imagen.url for imagen in vehiculo.imagenes_auto]
    print("Imágenes asociadas:", imagenes_url)

    return render_template("ver-auto.html", vehiculo=vehiculo, user=current_user, imagenes_url=imagenes_url)

@views.route('/delete-vehiculo/<int:id>', methods=['POST'])
@login_required
def borrar_vehiculo(id):
    """Deletes a car by id"""
    from .models import Auto
    car_to_delete = Auto.query.get_or_404(id)
    try:
        db.session.delete(car_to_delete)
        db.session.commit()
        flash("Se ha eliminado el auto correctamente")
    except:
        flash("Ha ocurrido un error, vuelve a intentarlo")
    
    return redirect(url_for('views.mis_vehiculos'))

@views.route('/delete-usuario/<int:id>', methods=['POST'])
@login_required
def borrar_usuario(id):
    from .models import User, Auto, Imagenes_auto

    # Busca y elimina el usuario por ID
    user_to_delete = User.query.get_or_404(id)

    try:
        # Elimina todos los autos del usuario y sus imágenes asociadas
        for auto in user_to_delete.autos:
            for imagen in auto.imagenes_auto:
                db.session.delete(imagen)
            db.session.delete(auto)

        # Finalmente, elimina al usuario
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("Su usuario y todas las imágenes asociadas se han eliminado correctamente")
    except:
        flash("Ha ocurrido un error, vuelve a intentarlo")

    logout_user()
    return redirect(url_for('auth.login'))