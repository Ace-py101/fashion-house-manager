document.addEventListener(
    "DOMContentLoaded",
    function () {

        const viewer =
            document.getElementById(
                "style-image-viewer"
            );

        if (!viewer) {

            return;

        }

        const image =
            document.getElementById(
                "viewer-image"
            );

        const close =
            document.getElementById(
                "viewer-close"
            );

        document
            .querySelectorAll(
                ".gallery-image"
            )
            .forEach(function (img) {

                img.addEventListener(
                    "click",
                    function () {

                        image.src =
                            this.dataset.full;

                        viewer.classList.add(
                            "active"
                        );

                    }
                );

            });

        close.addEventListener(
            "click",
            function () {

                viewer.classList.remove(
                    "active"
                );

            }
        );

        viewer.addEventListener(
            "click",
            function (event) {

                if (
                    event.target === viewer
                ) {

                    viewer.classList.remove(
                        "active"
                    );

                }

            }
        );

    }
);
