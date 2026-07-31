from flask import Blueprint, render_template


style_bp = Blueprint(
    "style",
    __name__
)



@style_bp.route("/styles")
def styles():

    return render_template(
        "module_placeholder.html",
        module_name="Styles Gallery"
    )
