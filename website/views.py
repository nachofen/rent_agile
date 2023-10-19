from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
import os
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import and_, or_
from sqlalchemy.sql import func

views = Blueprint('views', __name__)
UPLOAD_FOLDER = os.path.abspath('website/static/img/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """to validate allowed extensions"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/')
def home():
    """home url"""
    from .models import Auto
    autos = Auto.query.all()
    return render_template("index.html", user=current_user, autos=autos)

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
        matricula = request.form.get('matricula')
        categoria = request.form.get('categoria')
        departamento = request.form.get('departamento')
        tarifa = request.form.get('tarifa')
        descripcion = request.form.get('descripcion')

        nuevo_vehiculo = Auto(
            marca=marca,
            modelo=modelo,
            año=año,
            matricula=matricula,
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
marcas = [
    "Alfa Romeo",
    "Audi",
    "BMW",
    "BYD",
    "Chevrolet",
    "Chrysler",
    "Dodge",
    "Fiat",
    "Ford",
    "GMC",
    "Honda",
    "Hyundai",
    "Jaguar",
    "Jeep",
    "Kia",
    "Land Rover",
    "Lexus",
    "Mazda",
    "Mercedes-Benz",
    "Mini",
    "Nissan",
    "Peugeot",
    "Porsche",
    "Subaru",
    "Tesla",
    "Toyota",
    "Volkswagen",
    "Volvo"
]


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
        telefono = request.form.get('telefono')
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
            current_user.telefono = telefono
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
def mostrar_vehiculo(id):
    """shows one car by id"""
    from .models import Auto, Imagenes_auto
    vehiculo = Auto.query.get_or_404(id)
    imagenes_url = [imagen.url for imagen in vehiculo.imagenes_auto]
    print("Imágenes asociadas:", imagenes_url)

    return render_template("ver-auto.html", vehiculo=vehiculo, user=current_user, imagenes_url=imagenes_url)

@views.route('/editar-vehiculo/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_vehiculo(id):
    from .models import Auto, Imagenes_auto, FechasBloqueadas

    vehiculo = Auto.query.get_or_404(id)
    if current_user.id != vehiculo.usuario_id:
        flash('Este vehiculo no le pertenece', category='error')
        return redirect(url_for('views.mis_vehiculos'))
    imagenes_url = [imagen.url for imagen in vehiculo.imagenes_auto]
    fechas_bloqueadas = FechasBloqueadas.query.filter_by(auto_id=id).all()

    if request.method == 'POST':
        marca = request.form.get('marca')
        modelo = request.form.get('modelo')
        año = request.form.get('año')
        categoria = request.form.get('categoria')
        departamento = request.form.get('departamento')
        tarifa = request.form.get('tarifa')
        descripcion = request.form.get('descripcion')
        fecha_bloqueo_inicio = request.form.get('fecha_bloqueo_inicio')
        fecha_bloqueo_fin = request.form.get('fecha_bloqueo_fin')

        # Convierte las fechas en objetos datetime si se proporcionan
        if fecha_bloqueo_inicio:
            fecha_bloqueo_inicio = datetime.strptime(fecha_bloqueo_inicio, '%Y-%m-%d').date()

        if fecha_bloqueo_fin:
            fecha_bloqueo_fin = datetime.strptime(fecha_bloqueo_fin, '%Y-%m-%d').date()

        if fecha_bloqueo_inicio and fecha_bloqueo_fin:
            nueva_fecha_bloqueada = FechasBloqueadas(auto_id=id, fecha_inicio=fecha_bloqueo_inicio, fecha_fin=fecha_bloqueo_fin)
            db.session.add(nueva_fecha_bloqueada)

        vehiculo.marca = marca
        vehiculo.modelo = modelo
        vehiculo.año = año
        vehiculo.categoria = categoria
        vehiculo.departamento = departamento
        vehiculo.tarifa = tarifa
        vehiculo.descripcion = descripcion
        vehiculo.disponible = bool(int(request.form['disponibilidad']))  # Convierte a bool

        nuevas_imagenes = request.files.getlist('nuevas_imagenes[]')
        for nueva_imagen in nuevas_imagenes:
            if nueva_imagen and allowed_file(nueva_imagen.filename):
                # Guardar la nueva imagen en el directorio UPLOAD_FOLDER
                filename = secure_filename(nueva_imagen.filename)
                unique_filename = f"auto_{str(vehiculo.id_auto)}_{filename}"  # Nombre único de archivo
                nueva_imagen.save(os.path.join(UPLOAD_FOLDER, unique_filename))

                # Crear una entrada en la tabla Imagenes_auto para la nueva imagen
                nueva_imagen_db = Imagenes_auto(url=os.path.join('static/img/uploads', unique_filename), auto=vehiculo)
                db.session.add(nueva_imagen_db)

        # Obtén la lista de imágenes a quitar desde el html
        imagenes_quitar = request.form.getlist('imagenes_quitar[]')

        # Elimina las imágenes a quitar de la base de datos
        for url in imagenes_quitar:
            imagen = Imagenes_auto.query.filter_by(url=url, auto=vehiculo).first()
            if imagen:
                db.session.delete(imagen)

        db.session.commit()
        flash('Sus datos se han actualizado con éxito!', category='success')
        return redirect(url_for('views.mis_vehiculos'))

    return render_template("editar-vehiculo.html", user=current_user, vehiculo=vehiculo, departamentos=departamentos, imagenes_url=imagenes_url, fechas_bloqueadas=fechas_bloqueadas, marcas=marcas)


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
    

@views.route('/alquilar-vehiculo/<int:id>', methods=['GET', 'POST'])
@login_required
def alquilar_vehiculo(id):
    """para alquilar un vehiculo"""
    from .models import Auto, Reserva, FechasBloqueadas

    auto = Auto.query.get_or_404(id)
    if auto is None:
        flash('El vehículo seleccionado no existe.', 'error')
        return redirect(url_for('index'))

    fecha_inicio = None
    fecha_fin = None

    if request.method == 'POST':
        fecha_inicio = datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d').date()
        print("Fecha de inicio:", fecha_inicio)
        print("Fecha de fin:", fecha_fin)

    # Consulta las fechas bloqueadas para el auto seleccionado
    fechas_bloqueadas = FechasBloqueadas.query.filter(
        and_(
            FechasBloqueadas.auto_id == auto.id_auto,
            FechasBloqueadas.fecha_inicio <= fecha_fin,
            FechasBloqueadas.fecha_fin >= fecha_inicio
        )
    ).all()
    print("Fechasbloqueadas:", fechas_bloqueadas)
    if fechas_bloqueadas:
        flash('El vehículo no está disponible para las fechas seleccionadas debido a fechas bloqueadas.', 'error')
    else:
        # El vehículo está disponible para las fechas seleccionadas
        reserva = Reserva(
            id_usuario=current_user.id,  # Reemplaza con el ID del usuario actual
            id_auto=auto.id_auto,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        db.session.add(reserva)

        # Agregar las fechas a la tabla FechasBloqueadas
        nueva_fecha_bloqueada = FechasBloqueadas(
            auto_id=auto.id_auto,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        db.session.add(nueva_fecha_bloqueada)

        db.session.commit()
        flash('Reserva realizada con éxito.', 'success')

    return redirect(url_for('views.home'))

def filtrar_autos_disponibles(fecha_inicio, fecha_fin):
    from .models import Auto, FechasBloqueadas
    autos_disponibles = []

    # Obtener todos los autos de la base de datos
    todos_los_autos = Auto.query.all()

    for auto in todos_los_autos:
        # Obtener las fechas bloqueadas de este auto
        fechas_bloqueadas = FechasBloqueadas.query.filter_by(auto_id=auto.id_auto).all()

        # Verificar si alguna de las fechas bloqueadas coincide con el rango de fechas de los filtros
        if fecha_inicio and fecha_fin:  # Comprobación de que las fechas no son None
            fechas_bloqueadas_coincidentes = [fb for fb in fechas_bloqueadas if
                                              fb.fecha_inicio <= fecha_fin and fb.fecha_fin >= fecha_inicio]
        else:
            # Si alguna de las fechas es None, no hay coincidencia con las fechas bloqueadas
            fechas_bloqueadas_coincidentes = []

        # Si no hay fechas bloqueadas coincidentes, agregar este auto a la lista de disponibles
        if not fechas_bloqueadas_coincidentes:
            autos_disponibles.append(auto)

    return autos_disponibles

@views.route('/resultados/', methods=['GET', 'POST'])
def resultados():
    """Resultados de búsqueda acorde a los filtros"""
    from .models import Auto

    # Obtener los valores de los filtros desde la solicitud GET
    precio_min = request.args.get('precioMinimo')
    precio_max = request.args.get('precioMaximo')
    fecha_inicio_str = request.args.get('fechaInicio')  # Cadena de texto
    fecha_fin_str = request.args.get('fechaFin')  # Cadena de texto
    filtro_marca = request.args.get('marca')  # Obtener la marca seleccionada

    # Convertir las cadenas de texto en objetos de fecha
    fecha_inicio = None
    fecha_fin = None

    if fecha_inicio_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
    if fecha_fin_str:
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()

    # Filtrar autos disponibles según las fechas
    autos_disponibles = filtrar_autos_disponibles(fecha_inicio, fecha_fin)

    # Consulta de autos
    query = Auto.query

    # Aplicar filtros de precio
    if precio_min and precio_min != '':
        query = query.filter(Auto.tarifa >= float(precio_min))

    if precio_max and precio_max != '':
        query = query.filter(Auto.tarifa <= float(precio_max))

    # Aplicar filtro de marca si se seleccionó una marca
    if filtro_marca:
        # Utilizamos la condición "or_" para buscar la marca en la lista de marcas
        query = query.filter(or_(Auto.marca == filtro_marca))

    # Filtrar autos disponibles por ID
    autos_ids_disponibles = [auto.id_auto for auto in autos_disponibles]
    query = query.filter(Auto.id_auto.in_(autos_ids_disponibles))

    # Obtener los resultados de la consulta
    autos_resultado = query.all()


    return render_template("resultados.html", autos=autos_resultado, user=current_user)


@views.route('/enviar-mensaje/<int:id>', methods=['GET', 'POST'])
@login_required
def enviar_mensaje(id):
    from .models import Auto, User, Mensaje
    """ list the cars of loged user"""
    car_to_msg = Auto.query.get_or_404(id)
    imagen_perfil = car_to_msg.owner.image_path
    imagenes = car_to_msg.imagenes_auto
    if request.method == 'POST':
        contenido_mensaje = request.form.get('mensaje')
        fecha = datetime.utcnow()

        nuevo_mensaje = Mensaje(
            contenido_mensaje=contenido_mensaje,
            fecha=fecha,
            id_usuario=current_user.id,
            auto_id=car_to_msg.id_auto
        )
        db.session.add(nuevo_mensaje)
        db.session.commit()
        flash('Mensaje enviado correctamente', 'success')
        return redirect(url_for('views.home'))

    return render_template("enviar-mensaje.html", user=current_user, auto=car_to_msg, imagen_perfil=imagen_perfil, imagenes=imagenes)