from flask import Blueprint, render_template


firm_activity_bp = Blueprint(
    "firm_activity",
    __name__,
    url_prefix="/firm-activity"
)


@firm_activity_bp.route("/")
def firm_activity():
    return render_template(
        "firm_activity.html"
    )
