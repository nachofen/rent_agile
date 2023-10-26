// Obtén una referencia al div oculto
var divOculto = document.getElementById('divOculto');
var shown = false;

// Función para mostrar el div cuando el usuario hace scroll hacia abajo
function mostrarDivOculto() {
    // Obtén la posición vertical actual del scroll
    var scrollPosition = window.scrollY || window.scrollTop || document.getElementsByTagName("html")[0].scrollTop;

    // Define la posición en la que deseas mostrar el div (por ejemplo, a 200 píxeles desde la parte superior)
    var mostrarEnPosicion = 200;

    if (scrollPosition >= mostrarEnPosicion && !shown) {
        anime({
            targets: divOculto,
            translateY: [100, 0], // Cambia la posición vertical del div para que aparezca desde abajo
            opacity: [0, 1], // Cambia la opacidad para que aparezca gradualmente
            duration: 500, // Duración de la animación en milisegundos
            easing: 'easeOutQuad' // Tipo de transición (puedes ajustarlo)
        });
        shown = true;
    } else if (scrollPosition < mostrarEnPosicion && shown) {
        anime({
            targets: divOculto,
            translateY: [0, 100], // Cambia la posición vertical para que desaparezca hacia abajo
            opacity: [1, 0], // Cambia la opacidad para que desaparezca gradualmente
            duration: 500, // Duración de la animación en milisegundos
            easing: 'easeOutQuad' // Tipo de transición (puedes ajustarlo)
        });
        shown = false;
    }
}

// Agrega un evento de scroll para llamar a la función mostrarDivOculto cuando el usuario hace scroll
window.addEventListener('scroll', mostrarDivOculto);
