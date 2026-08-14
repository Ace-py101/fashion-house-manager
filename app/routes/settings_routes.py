from flask import (
    Blueprint,
    render_template,
    abort
)

from app.models.user import User

from app.services.auth_helpers import (
    current_user_id,
    login_required
)


settings_bp = Blueprint(
    "settings",
    __name__
)


# ============================================================
# ACCOUNT SETTINGS
# ============================================================

@settings_bp.route("/settings")
@login_required
def settings():

    user = (
        User.query
        .filter_by(
            id=current_user_id()
        )
        .first()
    )

    if not user:
        return (
            "Authenticated account could not be found.",
            401
        )

    return render_template(
        "account_settings.html",
        user=user
    )


# ============================================================
# ACCOUNT SETTINGS PLACEHOLDERS
#
# These routes establish the navigation architecture.
# Feature logic will be implemented later according to the
# Ateliier_fhm development roadmap.
# ============================================================

ACCOUNT_SETTINGS_SECTIONS = {

    "account": {
        "title": "Account",
        "description": (
            "Manage account information and account-level "
            "preferences."
        )
    },

    "security": {
        "title": "Security",
        "description": (
            "Manage password, sessions, login protection "
            "and account security."
        )
    },

    "privacy": {
        "title": "Privacy",
        "description": (
            "Manage privacy preferences and personal-data "
            "settings."
        )
    },

    "consent": {
        "title": "Consent & Agreements",
        "description": (
            "Review privacy agreements, terms acceptance "
            "and consent records."
        )
    },

    "notifications": {
        "title": "Notifications",
        "description": (
            "Manage email, SMS and application notification "
            "preferences."
        )
    },

    "subscription": {
        "title": "Subscription",
        "description": (
            "View subscription plan, account limits, billing "
            "and subscription status."
        )
    },

    "status": {
        "title": "Account Status",
        "description": (
            "View the current status and verification state "
            "of this account."
        )
    },

    "legal": {
        "title": "Legal & Terms",
        "description": (
            "Review Ateliier_fhm terms, privacy policy and "
            "other legal documents."
        )
    },

    "about": {
        "title": "About Ateliier_fhm",
        "description": (
            "Application information, version details and "
            "Ateliier_fhm platform information."
        )
    },

    "support": {
        "title": "Help & Support",
        "description": (
            "Access help resources and support information."
        )
    }
}


@settings_bp.route(
    "/settings/<section>"
)
@login_required
def settings_placeholder(section):

    section_data = ACCOUNT_SETTINGS_SECTIONS.get(
        section
    )

    if not section_data:
        abort(404)

    user = (
        User.query
        .filter_by(
            id=current_user_id()
        )
        .first()
    )

    if not user:
        return (
            "Authenticated account could not be found.",
            401
        )

    return render_template(
        "settings_placeholder.html",
        user=user,
        section=section,
        section_data=section_data
    )
