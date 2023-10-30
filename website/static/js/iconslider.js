// animaciones en perfil anfitrion slider iconos 

document.addEventListener("DOMContentLoaded", function () {
    const icons = document.querySelectorAll(".menu2 a i");
  
    setTimeout(function () {
      icons.forEach((icon, index) => {
        setTimeout(function () {
          icon.classList.add("show");
          icon.classList.add("slide-in");
        }, 100 * (index + 1));
      });
    }, 900);
  });