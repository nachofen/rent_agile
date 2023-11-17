// pop up info importante
function openPopup() {
    document.getElementById("popup").style.display = "block";
    document.getElementById("overlay").style.display = "block";
}

function closePopup() {
    document.getElementById("popup").style.display = "none";
    document.getElementById("overlay").style.display = "none";
}

// Oculta el pop-up y el overlay al cargar la página
document.addEventListener("DOMContentLoaded", function() {
    closePopup();

    // Oculta el pop-up y el overlay al hacer clic fuera del pop-up
    const overlay = document.getElementById("overlay");
    overlay.addEventListener("click", function(event) {
        if (event.target === overlay) {
            closePopup();
        }
    });
});