from flask import Blueprint, render_template

from app.services.dashboard_service import (
    get_dashboard_metrics,
    get_greeting
)



main_bp = Blueprint(
    "main",
    __name__
)



@main_bp.route("/")
def index():

    metrics = get_dashboard_metrics()

    greeting = get_greeting()


    return render_template(
        "index.html",
        greeting=greeting,
        total_customers=metrics["total_customers"]
    )
