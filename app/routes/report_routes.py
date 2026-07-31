from flask import Blueprint, render_template


report_bp = Blueprint(
    "report",
    __name__
)



@report_bp.route("/reports")
def reports():

    return render_template(
        "module_placeholder.html",
        module_name="Reports"
    )
