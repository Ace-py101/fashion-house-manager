from flask import Blueprint, render_template


measurement_bp = Blueprint(
    "measurement",
    __name__
)



@measurement_bp.route("/measurements")
def measurements():

    return render_template(
        "module_placeholder.html",
        module_name="Measurements"
    )
