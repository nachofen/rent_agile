document.addEventListener('DOMContentLoaded', function() {
    const cambiarImagenInputs = document.querySelectorAll('.imagen-input');
    const imagenesQuitarInput = document.querySelector('.imagenes-quitar-input');
    
    cambiarImagenInputs.forEach(function(input, index) {
        input.addEventListener('change', function() {
            // Cuando el usuario elige una nueva imagen, agrega la URL de la imagen anterior a imagenes_quitar[]
            const imagenAnterior = input.closest('li').querySelector('img').getAttribute('src');
            const imagenesQuitar = imagenesQuitarInput.value.split(',').filter(Boolean); // Eliminar elementos vacíos

            // Eliminar la barra diagonal al principio de la URL si está presente
            const urlSinBarraDiagonal = imagenAnterior.startsWith('/') ? imagenAnterior.substring(1) : imagenAnterior;
                // Obtener el nombre del archivo de la URL (la última parte de la ruta)
            const nombreArchivo = urlSinBarraDiagonal.split('/').pop();

            // Establecer un atributo personalizado en el input para almacenar el nombre del archivo
            input.setAttribute('data-nombre-archivo', nombreArchivo);
                
            // Verifica si la URL de la imagen anterior ya existe en imagenes_quitar
            if (imagenesQuitar.indexOf(urlSinBarraDiagonal) === -1) {
                imagenesQuitar.push(urlSinBarraDiagonal);
            }

            // Actualiza el valor del campo oculto
            imagenesQuitarInput.value = imagenesQuitar.join(',');

            // Agrega un console.log para verificar
            console.log('Imagenes a quitar:', imagenesQuitar);
        });
    });
});
