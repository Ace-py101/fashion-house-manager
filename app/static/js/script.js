document.addEventListener("DOMContentLoaded", () => {

const sidebar = document.getElementById("sidebar");
const menu = document.getElementById("menu-toggle");
const overlay = document.getElementById("overlay");

function closeMenu() {
    if (sidebar) sidebar.classList.remove("active");
    if (overlay) overlay.classList.remove("active");
}

function openMenu() {
    if (sidebar) sidebar.classList.add("active");
    if (overlay) overlay.classList.add("active");
}

if (menu && sidebar && overlay) {

    menu.addEventListener("click", () => {
        sidebar.classList.contains("active") ? closeMenu() : openMenu();
    });

    overlay.addEventListener("click", closeMenu);

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenu();
            closeModal();
        }
    });

    document.querySelectorAll(".sidebar a").forEach((link) => {
        link.addEventListener("click", closeMenu);
    });

}

document.querySelectorAll(".notification-close").forEach((button) => {
    button.addEventListener("click", () => {
        button.parentElement.remove();
    });
});

setTimeout(() => {
    document.querySelectorAll(".notification-card").forEach((card) => {
        card.remove();
    });
}, 5000);

/* Confirmation Modal */

const modal = document.getElementById("confirm-modal");
const cancelButton = document.getElementById("modal-cancel");
const confirmButton = document.getElementById("modal-confirm");

let confirmCallback = null;

function closeModal() {
    if (modal) {
        modal.classList.remove("active");
    }
}

window.showConfirmDialog = function(message, callback) {

    document.getElementById("modal-message").textContent = message;

    confirmCallback = callback;

    modal.classList.add("active");

};

if (cancelButton) {
    cancelButton.addEventListener("click", closeModal);
}

if (confirmButton) {
    confirmButton.addEventListener("click", () => {

        if (confirmCallback) {
            confirmCallback();
        }

        closeModal();

    });
}

window.scrollTo(0, 0);

// Profile Dropdown

const profileToggle = document.getElementById(
    "profile-toggle"
);

const profileMenu = document.getElementById(
    "profile-menu"
);



if(profileToggle && profileMenu){

    profileToggle.addEventListener(
        "click",
        () => {

            profileMenu.classList.toggle(
                "active"
            );

        }
    );


    document.addEventListener(
        "click",
        (event) => {


            if(
                !profileToggle.contains(event.target)
                &&
                !profileMenu.contains(event.target)
            ){

                profileMenu.classList.remove(
                    "active"
                );

            }

        }
    );

}

// Notification Dropdown


const notificationToggle =
document.getElementById(
    "notification-toggle"
);


const notificationMenu =
document.getElementById(
    "notification-menu"
);



if(notificationToggle && notificationMenu){


notificationToggle.addEventListener(
    "click",
    () => {

        notificationMenu.classList.toggle(
            "active"
        );

    }
);



document.addEventListener(
    "click",
    (event)=>{


        if(
            !notificationToggle.contains(
                event.target
            )
            &&
            !notificationMenu.contains(
                event.target
            )
        ){

            notificationMenu.classList.remove(
                "active"
            );

        }


    }
);


}

});
