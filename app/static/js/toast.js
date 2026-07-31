document.addEventListener("DOMContentLoaded", function () {

const toasts = document.querySelectorAll(".toast");

toasts.forEach(function (toast) {

const closeButton = toast.querySelector(".toast-close");

const hideToast = function () {

toast.classList.add("hide");

setTimeout(function () {

toast.remove();

},400);

};

setTimeout(hideToast,5000);

closeButton.addEventListener("click",hideToast);

});

});
