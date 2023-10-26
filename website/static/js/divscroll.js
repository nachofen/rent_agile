// Obtén una referencia al div oculto
var divOculto = document.getElementById('divOculto');
var shown = false;

// Función para mostrar el div cuando el usuario hace scroll hacia abajo
function mostrarDivOculto() {
    // Obtén la posición vertical actual del scroll
    var scrollPosition = window.scrollY || window.scrollTop || document.getElementsByTagName("html")[0].scrollTop;

    // posición en la cual mostrar el  div (ej 150 píxeles desde la parte superior)
    var mostrarEnPosicion = 500;

    if (scrollPosition >= mostrarEnPosicion && !shown) {
        anime({
            targets: divOculto,
            translateY: [100, 30], // Cambia la posición vertical del div para que aparezca desde abajo
            opacity: [0, 4], // Cambia la opacidad para que aparezca gradualmente
            duration: 700, // Duración de la animación en milisegundos
            easing: 'easeOutQuad' // Tipo de transición 
        });
        shown = true;
    } else if (scrollPosition < mostrarEnPosicion && shown) {
        anime({
            targets: divOculto,
            translateY: [0, 100], // Cambia la posición vertical para que desaparezca hacia abajo
            opacity: [1, 0], 
            duration: 400, 
            easing: 'easeOutQuad' // Tipo de transición 
        });
        shown = false;
    }
}

// Agrega un evento de scroll para llamar a la función mostrarDivOculto cuando el usuario hace scroll
window.addEventListener('scroll', mostrarDivOculto);
