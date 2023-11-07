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

@views.route('/')
@login_required
def saludo_index():
    """Página de inicio con saludo si está logueado """
    return render_template("index.html", user=current_user.nombre)

@views.route('/info')
def info_footer():
    """ Mostrar la vista del footer """
    user = current_user  
    return render_template("info.html", user=user)  

@views.route('/como-funciona')
def como_funciona_page():
    """ Mostrar la de como funciona """
    user = current_user  
    return render_template("como-funciona.html", user=user)  


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

@views.route('/perfil/<int:id>')
@login_required
def perfil_usuario(id):
    """perfil de usuario"""
    from .models import Reseña, Reserva, User, Auto
    usuario = User.query.get(id)
    if not usuario:
        flash('El usuario no existe.', category='error')
        return redirect(url_for('views.home'))

    reseñas = Reseña.query.filter_by(id_arrendatario=id, calificando_a=id).all()
    dueños_reseñas = []
    dueños_autos = []
    imagen_perfil = usuario.image_path
    promedio = 0
    puntaje = 0
    ultimas_dos_reseñas = []
    primer_reseña = []
    contador = Reseña.query.filter_by(id_arrendatario=id, calificando_a=id).count()
    dueño_auto = None

    for reseña in reseñas:
        if len(reseñas) == 0:
            break
        print(f"{reseña.id_resena}")
        calificacion = reseña.calificacion
        puntaje = puntaje + calificacion
    
    if contador == 0:
        dueño_auto = None
        print("sin reseñas")
    else:
        promedio = puntaje / contador
    print (f"puntaje:{puntaje}contador: {contador}promedio: {promedio}")
    if contador < 1:
        primeras_dos_reseñas = None
    elif contador == 1:
        primer_reseña = reseñas
        auto = Auto.query.filter_by(id_auto=primer_reseña[0].id_auto).first()
        dueño = User.query.get(reseña.id_arrendatario)
        if auto:
                dueño_auto = auto.owner
                print(f"ID del dueño del auto: {dueño_auto.id}")
                dueños_autos.append(dueño_auto)
        else:
            print("Auto no encontrado para la reseña") 
    else:
        ultimas_dos_reseñas = reseñas[-2:]
        for reseña in ultimas_dos_reseñas:
            print(f"{reseña.id_resena}")
            auto = Auto.query.filter_by(id_auto=reseña.id_auto).first()
            dueño_auto = User.query.get(reseña.id_arrendatario)
            dueño = User.query.get(reseña.id_arrendatario)
            # Verifica si el auto fue encontrado
            if auto:
                dueño_auto = auto.owner
                print(f"ID del dueño del auto: {dueño_auto.id}")
                dueños_autos.append(dueño_auto)
            else:
                print("Auto no encontrado para la reseña") 
            dueños_reseñas.append(dueño)
    
        
    
    return render_template("perfil.html", user=usuario, contador=contador, promedio=promedio, imagen_perfil=imagen_perfil,dueños_autos=dueños_autos,ultimas_dos_reseñas=ultimas_dos_reseñas,dueños_reseñas=dueños_reseñas, dueño_auto=dueño_auto, reseñas=reseñas)

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

@views.route('/mis-reservas')
@login_required
def mis_reservas():
    from .models import Reserva, Imagenes_auto, Auto
    """ lista las reservas que tiene el usuario activo"""
    reservas = Reserva.query.filter_by(id_usuario=current_user.id).all()
    imagenes_primer_auto = []
    autos = []

    for reserva in reservas:
        auto_id = reserva.id_auto  # Obtenemos el identificador del auto
        auto = Auto.query.get(auto_id)  # Obtenemos el objeto Auto
        if auto:
            autos.append(auto)
            primera_imagen = Imagenes_auto.query.filter_by(auto_id=auto.id_auto).first()
            if primera_imagen:
                imagenes_primer_auto.append(primera_imagen)

    # Combina las listas reservas ,imagenes_primer_auto y los autos que pertencen a las reservas
    reservas_con_imagenes = zip(reservas, imagenes_primer_auto, autos)

    return render_template("mis-reservas.html", user=current_user, reservas_con_imagenes=reservas_con_imagenes)
@views.route('/host/mis-reservas')
@login_required
def mis_reservas_host():
    """ lista las reservas que han hecho otros clientes a los autos del usuario activo"""
    from .models import Reserva, Imagenes_auto, Auto
    
    # Obtener los autos del usuario actual
    autos_del_usuario = Auto.query.filter_by(usuario_id=current_user.id).all()
    

    # Obtener las reservas en los autos del usuario actual
    reservas = Reserva.query.filter(Reserva.id_auto.in_([auto.id_auto for auto in autos_del_usuario])).all()
    
    arrendatario_id = reservas[0].id_usuario
    arrendatario = User.query.get(arrendatario_id)

    imagenes_primer_auto = []
    autos = []

    for reserva in reservas:
        auto_id = reserva.id_auto
        auto = Auto.query.get(auto_id)
        if auto:
            autos.append(auto)
            primera_imagen = Imagenes_auto.query.filter_by(auto_id=auto.id_auto).first()
            if primera_imagen:
                imagenes_primer_auto.append(primera_imagen)

    reservas_con_imagenes = zip(reservas, imagenes_primer_auto, autos)

    return render_template("mis-reservashost.html", user=current_user, reservas_con_imagenes=reservas_con_imagenes, arrendatario=arrendatario)

@views.route('/ver-vehiculo/<int:id>', methods=['GET', 'POST'])
def mostrar_vehiculo(id):
    """shows one car by id"""
    from .models import Auto, Imagenes_auto
    vehiculo = Auto.query.get_or_404(id)
    imagenes_url = [imagen.url for imagen in vehiculo.imagenes_auto]
    print("Imágenes asociadas:", imagenes_url)

    return render_template("ver-auto.html", vehiculo=vehiculo, user=current_user, imagenes_url=imagenes_url)

@views.route('/ver-auto', methods=['GET'])
def ver_auto():
    # Definir los datos que deseas pasar a la plantilla
    datos = {
        'nombre': 'Nombre del vehículo',
        'descripcion': 'Descripción del vehículo',
        'imagenes_url': ['url1.jpg', 'url2.jpg']
    }
    # Renderiza la plantilla ver-auto.html y pasa los datos como argumentos
    return render_template("ver-auto.html", datos=datos)

@views.route('/ver-reserva/<int:id>', methods=['GET', 'POST'])
def mostrar_reserva(id):
    """shows one reservation by id"""
    from .models import Auto, Imagenes_auto, Reserva
    reserva = Reserva.query.get_or_404(id)
    arrendatario_id = reserva.id_usuario
    arrendatario = User.query.get(arrendatario_id)
    fecha_ahora = datetime.now().date()

    # Obtén la ID del dueño del auto relacionado con la reserva
    dueño_del_auto_id = db.session.query(Auto.usuario_id).filter_by(id_auto=reserva.id_auto).scalar()

    # Verifica que quien mire la URL sea el dueño de la reserva o el dueño del auto de la reserva
    if current_user.id != reserva.id_usuario and current_user.id != dueño_del_auto_id:
        flash('Esta reserva no le pertenece', category='error')
        return redirect(url_for('views.mis_reservas'))
    id_auto = reserva.id_auto
    auto = Auto.query.get_or_404(id_auto)
    primera_imagen = Imagenes_auto.query.filter_by(auto_id=id_auto).first()
    propietario_id = auto.usuario_id
    propietario = User.query.get(propietario_id)
    fecha_hoy = datetime.now().date()
    fecha_fin = reserva.fecha_fin
    dif_dias = (fecha_hoy - fecha_fin).days
    print (f"{dif_dias}")

    return render_template("ver-reserva.html", reserva=reserva, user=current_user, auto=auto, propietario=propietario, primera_imagen=primera_imagen, arrendatario=arrendatario, fecha_ahora=fecha_ahora, dif_dias=dif_dias)

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

        # Validar el formulario
        if vehiculo.disponible and len(vehiculo.imagenes_auto) == 0:
            flash('El vehículo debe tener al menos una foto si está disponible!', category='error')
            return render_template("agregar-vehiculo.html", user=current_user)

            
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


@views.route('/cancelar-reserva/<int:id>', methods=['GET', 'POST'])
@login_required
def cancelar_reserva(id):
    """cancela reserva por id"""
    from .models import Auto, Reserva
    reserva = Reserva.query.get_or_404(id)

    car_to_cancel_id = Auto.query.get_or_404(reserva.id_auto)
    if current_user.id == car_to_cancel_id.usuario_id:
        reserva.estado = "cancelada"
        db.session.commit()
        flash('La reserva ha sido cancelada con éxito', 'success')

    else:
        print("no puedes cancelar esta reserva")
    return redirect(url_for('views.mis_reservas_host'))

@views.route('/devolver-vehiculo/<int:id>', methods=['GET', 'POST'])
@login_required
def devolver_vehiculo(id):
    """cambia el estado de una reserva de activa a completada"""
    from .models import Auto, Reserva
    reserva = Reserva.query.get_or_404(id)

    car_to_return_id = Auto.query.get_or_404(reserva.id_auto)
    if current_user.id == car_to_return_id.usuario_id:
        reserva.estado = "completada"
        db.session.commit()
        flash('Se ha confirmado la devolución de su vehículo con exito', 'success')

    else:
        print("no puedes cancelar esta reserva")
    return redirect(url_for('views.mis_reservas_host'))

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
    autos_del_usuario = Auto.query.filter_by(id_usuario=id).all()
    for auto in autos_del_usuario:
        auto.disponible = False
        db.session.add(auto)

    # Finalmente, elimina al usuario
    db.session.delete(user_to_delete)
    db.session.commit()
    flash("Su usuario y todas las imágenes asociadas se han eliminado correctamente")

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


    today = datetime.today().date()
    fecha_inicio = datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date()
    fecha_fin = datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d').date()
    
    # Consulta las fechas bloqueadas para el auto seleccionado
    fechas_bloqueadas = FechasBloqueadas.query.filter(
        and_(
            FechasBloqueadas.auto_id == auto.id_auto,
            FechasBloqueadas.fecha_inicio <= fecha_fin,
            FechasBloqueadas.fecha_fin >= fecha_inicio
        )
    ).all()
    
    if fechas_bloqueadas or fecha_inicio < today or fecha_fin < fecha_inicio:
        flash('El vehículo no está disponible para las fechas seleccionadas.', 'error')
        #aca agregar la ruta con #
        
        return redirect(url_for('views.home') + '#seccionalquilar')

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

    return redirect(url_for('views.mis_reservas'))

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
    filtro_depto = request.args.get('depto')

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

    if filtro_depto != 'todos':
        # Utilizamos la condición "or_" para buscar la marca en la lista de marcas
        query = query.filter(or_(Auto.departamento == filtro_depto))
    
    # Aplicar filtro de marca si se seleccionó una marca
    if filtro_marca != 'todas':
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
    from .models import Auto, User, Mensaje, Conversacion
    """ list the cars of loged user"""
    car_to_msg = Auto.query.get_or_404(id)
    destinatario = User.query.get(car_to_msg.usuario_id)

    imagen_perfil = car_to_msg.owner.image_path
    imagenes = car_to_msg.imagenes_auto
    if request.method == 'POST':
        contenido_mensaje = request.form.get('mensaje')
        fecha = datetime.utcnow()
        conversacion_existente = Conversacion.query.filter_by(
            usuario_id=current_user.id,
            destinatario_id=car_to_msg.usuario_id,
            auto_id=car_to_msg.id_auto
        ).first()

        if conversacion_existente:
            conversacion = conversacion_existente  # Cambio 'conversacion_id' a 'conversacion'
        else:
            # Si no existe una conversación, crea una nueva
            nueva_conversacion = Conversacion(
                usuario_id=current_user.id,
                destinatario_id=car_to_msg.usuario_id,
                auto_id=car_to_msg.id_auto
            )
            db.session.add(nueva_conversacion)
            db.session.commit()
            conversacion = nueva_conversacion  # Cambio 'conversacion_id' a 'conversacion'

        nuevo_mensaje = Mensaje(
            contenido_mensaje=contenido_mensaje,
            fecha=fecha,
            id_usuario=current_user.id,
            auto_id=car_to_msg.id_auto,
            destinatario_id=destinatario.id,
            conversacion=conversacion  # Cambio 'id_conversacion' a 'conversacion'
        )
        db.session.add(nuevo_mensaje)
        db.session.commit()
        flash('Mensaje enviado correctamente', 'success')
        return redirect(url_for('views.home'))

    return render_template("enviar-mensaje.html", user=current_user, auto=car_to_msg, imagen_perfil=imagen_perfil, imagenes=imagenes)

@views.route('/bandeja-entrada', methods=['GET'])
@login_required
def bandeja_entrada():
    from .models import Mensaje, Conversacion

    # Subconsulta para obtener el último mensaje por conversación
    subquery = db.session.query(
        func.max(Mensaje.fecha).label('max_fecha'),
        Mensaje.conversacion_id
    ).group_by(Mensaje.conversacion_id).subquery()

    # Consulta principal para obtener los últimos mensajes de las conversaciones del usuario actual
    mensajes = db.session.query(Mensaje, subquery.c.max_fecha.label('last_message_date')).join(
        subquery,
        and_(Mensaje.conversacion_id == subquery.c.conversacion_id, Mensaje.fecha == subquery.c.max_fecha)
    ).filter(or_(Mensaje.conversacion.has(usuario_id=current_user.id), Mensaje.conversacion.has(destinatario_id=current_user.id)))

    destinatario_names = []

    # Obtener el nombre de cada destinatario y almacenarlo en la lista
    for mensaje in mensajes:
        # Obtener el ID de la conversación
        conversacion_id = mensaje[0].conversacion_id

        # Obtener el ID del usuario con el que está chateando
        ultimo_mensaje = Mensaje.query.filter_by(conversacion_id=conversacion_id).order_by(Mensaje.fecha.desc()).first()
        id_usuario_ultimo_mensaje = ultimo_mensaje.id_usuario

        # Obtener el nombre del usuario con el que está chateando
        destinatario_name = User.query.filter_by(id=id_usuario_ultimo_mensaje).first()
        
        if id_usuario_ultimo_mensaje != current_user.id:
            id_usuario = ultimo_mensaje.id_usuario
            usuario = User.query.get(id_usuario)
            destinatario_name = usuario.nombre + " " + usuario.apellido
        else:
            id_usuario = ultimo_mensaje.destinatario_id
            usuario = User.query.get(id_usuario)
            destinatario_name = usuario.nombre + " " + usuario.apellido
        destinatario_names.append(destinatario_name)

    # Combinar mensajes y destinatario_names usando zip
    mensajes_con_nombres = zip(mensajes, destinatario_names)

    return render_template("bandeja-entrada.html", mensajes=mensajes_con_nombres, user=current_user)


@views.route('/bandeja-entrada/<int:id>', methods=['GET', 'POST'])
@login_required
def conversar(id):
    """Todos los mensajes de una misma conversación"""
    from .models import Mensaje, Conversacion, Auto
    conversacion = Conversacion.query.get(id)

    if not conversacion:
        # Manejar el caso en que la conversación no existe
        flash('La conversación no existe o no tienes permiso para acceder a ella.', 'error')
        return redirect(url_for('views.bandeja_entrada'))  

    # Verificar si el usuario actual tiene permiso para ver la conversación
    if conversacion.usuario_id != current_user.id and conversacion.destinatario_id != current_user.id:
        flash('No tienes permiso para acceder a esta conversación.', 'error')
        return redirect(url_for('views.bandeja_entrada'))  
    if request.method == 'POST':
        # Obtener el contenido del mensaje enviado por el usuario
        contenido_mensaje = request.form.get('nuevo-mensaje')
        
        # Obtener la conversación actual
        conversacion = Conversacion.query.get(id)
        if conversacion is not None:
            # Obtener el auto relacionado con la conversación
            car_to_msg = Auto.query.get(conversacion.auto_id)
            destinatario_id = (
            conversacion.destinatario_id
            if conversacion.usuario_id == current_user.id
            else conversacion.usuario_id
            )
            
            # Crear un nuevo mensaje y guardarlo en la base de datos
            nuevo_mensaje = Mensaje(
                contenido_mensaje=contenido_mensaje,
                fecha=datetime.utcnow(),
                id_usuario=current_user.id,
                auto_id=car_to_msg.id_auto,
                destinatario_id=destinatario_id,
                conversacion_id=id
            )
            db.session.add(nuevo_mensaje)
            db.session.commit()

            # Redirigir nuevamente a la página de conversación para mostrar el mensaje enviado
            return redirect(url_for('views.conversar', id=id))
    # Obtener todos los mensajes de la conversación con el ID especificado

    mensajes = Mensaje.query.filter_by(conversacion_id=id).all()
    destinatarios = []
    emisores = []
    # Consulta para obtener el nombre del destinatario
    for mensaje in mensajes:
        
        destinatario = User.query.get(mensaje.destinatario_id)  # Supongamos que el destinatario_id se encuentra en el primer mensaje
        destinatarios.append(destinatario)
        emisor = User.query.get(mensaje.id_usuario)
        emisores.append(emisor)

    
    subq = db.session.query(
    func.min(Mensaje.fecha).label('min_fecha'),
    Mensaje.destinatario_id,
    Mensaje.conversacion_id
    ).group_by(Mensaje.conversacion_id, Mensaje.destinatario_id).subquery()

    primer_mensaje = Mensaje.query.filter_by(conversacion_id=id).order_by(Mensaje.fecha).first()
    primer_destinatario = None
    if primer_mensaje:
        primer_destinatario = User.query.get(primer_mensaje.destinatario_id)


    mensajes_con_destinatarios = zip(mensajes, destinatarios, emisores)

    return render_template("mensaje.html", mensajes_con_destinatarios=mensajes_con_destinatarios, user=current_user, primer_destinatario=primer_destinatario)

@views.route('/calificar/<int:id>', methods=['GET', 'POST'])
@login_required
def calificar(id):
    from .models import Reserva, Reseña, Auto
    """dejar una calificacion al dueño del vehiculo"""

    reserva = Reserva.query.get(id)
    if current_user.id != reserva.id_usuario:
        flash('Esta reserva no le pertenece.', 'error')
        return redirect(url_for('views.mis_reservas'))
    fecha_hoy = datetime.now().date()
    car_to_msg = Auto.query.get_or_404(reserva.id_auto)
    imagenes = car_to_msg.imagenes_auto
    if request.method == 'POST':
        calificacion_estado = request.form.get('calificacion_estado')
        calificacion_limpieza = request.form.get('calificacion_limpieza')
        calificacion_puntualidad = request.form.get('calificacion_puntualidad')
        calificacion_comunicacion = request.form.get('calificacion_comunicacion')
        promedio = None
        if (calificacion_estado is not None and calificacion_limpieza is not None and 
        calificacion_puntualidad is not None and calificacion_comunicacion is not None):
            promedio = (int(calificacion_estado) + int(calificacion_limpieza) + int(calificacion_puntualidad) + int(calificacion_comunicacion)) / 4.0

        comentario = request.form.get('comentario')
        nueva_reseña = Reseña(
            reserva_id = id,
            calificacion_comunicacion=calificacion_comunicacion,
            calificacion_estado=calificacion_estado,
            calificacion_limpieza=calificacion_limpieza,
            calificacion_puntualidad=calificacion_puntualidad,
            comentario=comentario,
            calificacion=promedio,
            id_auto=reserva.id_auto,
            id_arrendatario=current_user.id,
            calificado_por=current_user.id,
            calificando_a=car_to_msg.usuario_id,
            fecha=fecha_hoy
        )
        db.session.add(nueva_reseña)
        reserva.calificado_por_arrendatario = True
        db.session.commit()
        
        flash('Has calificado con exito!', 'success')
        return redirect(url_for('views.mis_reservas'))

    return render_template("calificar.html", user=current_user, auto=car_to_msg, imagenes=imagenes)

@views.route('/calificar-host/<int:id>', methods=['GET', 'POST'])
@login_required
def calificar_host(id):
    from .models import Reserva, Reseña, Auto, User
    """dejar una calificacion al dueño del vehiculo"""

    reserva = Reserva.query.get(id)
    car_to_review = Auto.query.get(reserva.id_auto)
    owner_id = User.query.get(car_to_review.usuario_id)
    arrendatario = User.query.get(reserva.id_usuario)
    
    if current_user.id != owner_id.id:
        flash('Esta reserva no le pertenece.', 'error')
        return redirect(url_for('views.mis_reservas'))
    fecha_hoy = datetime.now().date()
    if request.method == 'POST':
        calificacion_limpieza = request.form.get('calificacion_limpieza')
        calificacion_puntualidad = request.form.get('calificacion_puntualidad')
        calificacion_comunicacion = request.form.get('calificacion_comunicacion')
        promedio = None
        if (calificacion_limpieza is not None and 
        calificacion_puntualidad is not None and calificacion_comunicacion is not None):
            promedio = (int(calificacion_limpieza) + int(calificacion_puntualidad) + int(calificacion_comunicacion)) / 3.0

        comentario = request.form.get('comentario')
        nueva_reseña = Reseña(
            reserva_id = id,
            calificacion_comunicacion=calificacion_comunicacion,
            calificacion_limpieza=calificacion_limpieza,
            calificacion_puntualidad=calificacion_puntualidad,
            comentario=comentario,
            calificacion=promedio,
            id_arrendatario=reserva.id_usuario,
            id_auto=car_to_review.id_auto,
            calificado_por=current_user.id,
            calificando_a=reserva.id_usuario,
            fecha=fecha_hoy
        )
        db.session.add(nueva_reseña)
        reserva.calificado_por_dueño = True
        db.session.commit()
        
        flash('Has calificado con exito!', 'success')
        return redirect(url_for('views.mis_reservas'))

    return render_template("calificarhost.html", user=current_user, arrendatario=arrendatario)
                