from flask import Blueprint, render_template

from app.services.auth_helpers import login_required


client_bp = Blueprint(
    "client",
    __name__,
)


def _client_placeholder(
    title,
    description,
    icon="✨",
):
    return render_template(
        "client_placeholder.html",
        section_data={
            "title": title,
            "description": description,
            "icon": icon,
        },
    )


@client_bp.route("/client-dashboard")
@login_required
def dashboard():
    return render_template(
        "client_dashboard.html"
    )


@client_bp.route("/client/orders")
@login_required
def orders():
    return _client_placeholder(
        "My Orders",
        "View and manage your orders with participating fashion businesses.",
        "📋",
    )


@client_bp.route("/client/measurements")
@login_required
def measurements():
    return _client_placeholder(
        "My Measurements",
        "View your saved measurement records.",
        "📏",
    )


@client_bp.route("/client/payments")
@login_required
def payments():
    return _client_placeholder(
        "Payments",
        "View your payment history and transaction status.",
        "💳",
    )


@client_bp.route("/client/deliveries")
@login_required
def deliveries():
    return _client_placeholder(
        "Deliveries",
        "Track upcoming and completed deliveries.",
        "📦",
    )


@client_bp.route("/client/saved-styles")
@login_required
def saved_styles():
    return _client_placeholder(
        "Saved Styles",
        "Your saved fashion styles and wishlist will appear here.",
        "❤️",
    )
