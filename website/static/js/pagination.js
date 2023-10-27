// Supongamos que tienes una lista de autos en un array llamado "autos".
const autos = [...]; // Tu lista de autos

// Define el número de autos por página.
const autosPorPagina = 12;
let paginaActual = 1;

function mostrarAutosEnPagina(pagina) {
    const inicio = (pagina - 1) * autosPorPagina;
    const fin = inicio + autosPorPagina;
    const autosContainer = document.getElementById('autoContainer');
    autosContainer.innerHTML = '';

    for (let i = inicio; i < fin && i < autos.length; i++) {
        const auto = autos[i];
        const autoCard = document.createElement('div');
        autoCard.classList.add('auto');
        autoCard.innerHTML = `
            <a href="/ver-vehiculo/${auto.id_auto}">
                <div class="auto-inner">
                    <div class="auto-front">
                        <img src="${auto.imagenes_auto[0].url}" alt="${auto.marca} ${auto.modelo}">
                    </div>
                    <div class="auto-back">
                        <h2>Rent Agile</h2> 
                        <p>${auto.marca} ${auto.modelo}</p> 
                        <p>Precio: ${auto.tarifa}$</p>
                    </div>
                </div>
            </a>
        `;
        autosContainer.appendChild(autoCard);
    }
}

// Maneja la navegación entre páginas
function cambiarPagina(nuevaPagina) {
    paginaActual = nuevaPagina;
    mostrarAutosEnPagina(paginaActual);
}

// Inicializa la página
mostrarAutosEnPagina(paginaActual);

// Agrega un evento para el botón "Anterior"
const btnAnterior = document.getElementById('previous');
btnAnterior.addEventListener('click', () => {
    if (paginaActual > 1) {
        cambiarPagina(paginaActual - 1);
    }
});

// Agrega un evento para el botón "Siguiente"
const btnSiguiente = document.getElementById('next');
btnSiguiente.addEventListener('click', () => {
    if (paginaActual < Math.ceil(autos.length / autosPorPagina)) {
        cambiarPagina(paginaActual + 1);
    }
});

// Genera la paginación
const pagination = document.getElementById('pagination');
for (let i = 1; i <= Math.ceil(autos.length / autosPorPagina); i++) {
    const pageLink = document.createElement('a');
    pageLink.textContent = i;
    pageLink.href = 'javascript:void(0);';
    pageLink.addEventListener('click', () => cambiarPagina(i));
    pagination.appendChild(pageLink);
}
