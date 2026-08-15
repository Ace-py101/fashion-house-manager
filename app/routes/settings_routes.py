from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)

from app.database import db

from app.models.user import User
from app.models.business import Business
from app.models.user_privacy_preference import (
    UserPrivacyPreference
)
from app.models.user_notification_preference import (
    UserNotificationPreference
)
from app.models.legal_document import LegalDocument
from app.models.user_consent import UserConsent

from app.services.auth_helpers import (
    current_user_id,
    login_required
)


settings_bp = Blueprint(
    "settings",
    __name__
)


# ============================================================
# SETTINGS SECTIONS
# ============================================================

ACCOUNT_SETTINGS_SECTIONS = {

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

    "preferences": {
        "title": "Preferences",
        "description": (
            "Manage application preferences and account "
            "experience settings."
        )
    },

    "users": {
        "title": "Users & Roles",
        "description": (
            "Manage business users, roles and organizational "
            "access."
        )
    },

    "activity": {
        "title": "Activity",
        "description": (
            "Review account and organizational activity."
        )
    },

    "subscription": {
        "title": "Subscription",
        "description": (
            "View subscription plan, feature access, limits "
            "and subscription status."
        )
    },

    "billing": {
        "title": "Billing",
        "description": (
            "Manage billing records and payment configuration."
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


# ============================================================
# AUTHENTICATED USER
# ============================================================

def _get_authenticated_user():

    return (
        User.query
        .filter_by(
            id=current_user_id()
        )
        .first()
    )


# ============================================================
# BUSINESS ACCESS
# ============================================================

def _require_business_account(user):

    if not user:

        return False

    return user.account_type == "admin"


def _get_business(user):

    if not user or not user.business_id:

        return None

    return (
        Business.query
        .filter_by(
            id=user.business_id
        )
        .first()
    )


# ============================================================
# VALIDATION
# ============================================================

def _validate_phone_number(value):

    value = (
        value
        or ""
    ).strip()

    if not value:

        return None

    if len(value) > 30:

        raise ValueError(
            "Phone number must not exceed 30 characters."
        )

    allowed = set(
        "0123456789+()- "
    )

    if any(
        character not in allowed
        for character in value
    ):

        raise ValueError(
            "Please enter a valid phone number."
        )

    digits = "".join(
        character
        for character in value
        if character.isdigit()
    )

    if len(digits) < 7:

        raise ValueError(
            "Please enter a valid phone number."
        )

    return value


def _validate_business_name(value):

    value = (
        value
        or ""
    ).strip()

    if not value:

        raise ValueError(
            "Business name is required."
        )

    if len(value) < 2:

        raise ValueError(
            "Business name must contain at least 2 characters."
        )

    if len(value) > 150:

        raise ValueError(
            "Business name must not exceed 150 characters."
        )

    return value


def _get_form_boolean(form, field_name):

    value = form.get(
        field_name
    )

    if value is None:
        return False

    value = value.strip().lower()

    if value not in {
        "1",
        "true",
        "on"
    }:

        raise ValueError(
            f"Invalid value submitted for {field_name}."
        )

    return True


# ============================================================
# CONSENT HELPERS
# ============================================================

def _get_active_legal_documents():
    """
    Return currently active legal documents.
    """

    return (
        LegalDocument.query
        .filter(
            LegalDocument.is_active.is_(True)
        )
        .order_by(
            LegalDocument.document_type.asc(),
            LegalDocument.id.desc()
        )
        .all()
    )


def _get_latest_user_consent(
    user_id,
    document_type
):
    """
    Return the user's most recent consent record for a
    particular legal document type.
    """

    return (
        UserConsent.query
        .join(
            LegalDocument,
            UserConsent.legal_document_id
            == LegalDocument.id
        )
        .filter(
            UserConsent.user_id == user_id,
            LegalDocument.document_type == document_type
        )
        .order_by(
            UserConsent.accepted_at.desc(),
            UserConsent.id.desc()
        )
        .first()
    )


def _get_request_ip():
    """
    Obtain the client IP address used for consent auditing.
    """

    forwarded_for = request.headers.get(
        "X-Forwarded-For",
        ""
    ).strip()

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.remote_addr


# ============================================================
# SETTINGS HOME
# ============================================================

@settings_bp.route(
    "/settings"
)
@login_required
def settings():

    user = _get_authenticated_user()

    if not user:

        return (
            "Authenticated account could not be found.",
            401
        )

    return render_template(
        "account_settings.html",
        user=user,
        business=_get_business(user)
    )


# ============================================================
# ACCOUNT
# ============================================================

@settings_bp.route(
    "/settings/account",
    methods=["GET", "POST"]
)
@login_required
def account_settings():

    user = _get_authenticated_user()

    if not user:

        return (
            "Authenticated account could not be found.",
            401
        )

    if request.method == "POST":

        try:

            phone_number = _validate_phone_number(
                request.form.get(
                    "phone_number",
                    ""
                )
            )

            if phone_number:

                existing_user = (
                    User.query
                    .filter(
                        User.phone_number == phone_number,
                        User.id != user.id
                    )
                    .first()
                )

                if existing_user:

                    raise ValueError(
                        "Phone number already exists."
                    )

            user.phone_number = phone_number

            # Changing the phone number invalidates an existing
            # phone verification state. Verification is handled
            # by the authentication system.
            user.phone_verified = False
            user.phone_verified_at = None

            db.session.commit()

            flash(
                "Account information updated successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "settings.account_settings"
                )
            )

        except ValueError as error:

            db.session.rollback()

            flash(
                str(error),
                "error"
            )

        except Exception:

            db.session.rollback()

            flash(
                "Unable to update account information. "
                "Please try again.",
                "error"
            )

    return render_template(
        "settings_account.html",
        user=user
    )


# ============================================================
# BUSINESS
# ============================================================

@settings_bp.route(
    "/settings/business",
    methods=["GET", "POST"]
)
@login_required
def business_settings():

    user = _get_authenticated_user()

    if not user:

        return (
            "Authenticated account could not be found.",
            401
        )

    if not _require_business_account(user):

        flash(
            "Business settings are available only to "
            "business accounts.",
            "error"
        )

        return redirect(
            url_for(
                "settings.settings"
            )
        )

    business = _get_business(user)

    if request.method == "POST":

        try:

            business_name = _validate_business_name(
                request.form.get(
                    "business_name",
                    ""
                )
            )

            if not business:

                business = Business(
                    name=business_name
                )

                db.session.add(
                    business
                )

                db.session.flush()

                user.business_id = business.id

            else:

                business.name = business_name

            # Preserve the existing field while the Business
            # organization model becomes authoritative.
            user.business_name = business_name

            db.session.commit()

            flash(
                "Business information updated successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "settings.business_settings"
                )
            )

        except ValueError as error:

            db.session.rollback()

            flash(
                str(error),
                "error"
            )

        except Exception:

            db.session.rollback()

            flash(
                "Unable to update business information. "
                "Please try again.",
                "error"
            )

    return render_template(
        "settings_business.html",
        user=user,
        business=business
    )


# ============================================================
# PROFILE
# ============================================================

@settings_bp.route(
    "/settings/profile"
)
@login_required
def profile_settings():

    user = _get_authenticated_user()

    if not user:

        return (
            "Authenticated account could not be found.",
            401
        )

    return render_template(
        "settings_profile.html",
        user=user
    )


# ============================================================
# PRIVACY SETTINGS
# ============================================================

@settings_bp.route(
    "/settings/privacy",
    methods=["GET", "POST"]
)
@login_required
def privacy_settings():

    user = _get_authenticated_user()

    if not user:

        return (
            "Authenticated account could not be found.",
            401
        )

    preferences = (
        UserPrivacyPreference.query
        .filter_by(
            user_id=user.id
        )
        .first()
    )

    if request.method == "POST":

        try:

            analytics_enabled = _get_form_boolean(
                request.form,
                "analytics_enabled"
            )

            personalization_enabled = _get_form_boolean(
                request.form,
                "personalization_enabled"
            )

            marketing_enabled = _get_form_boolean(
                request.form,
                "marketing_enabled"
            )

            data_sharing_enabled = _get_form_boolean(
                request.form,
                "data_sharing_enabled"
            )

            if not preferences:

                preferences = UserPrivacyPreference(
                    user_id=user.id
                )

                db.session.add(
                    preferences
                )

            preferences.analytics_enabled = (
                analytics_enabled
            )

            preferences.personalization_enabled = (
                personalization_enabled
            )

            preferences.marketing_enabled = (
                marketing_enabled
            )

            preferences.data_sharing_enabled = (
                data_sharing_enabled
            )

            db.session.commit()

            flash(
                "Privacy preferences updated successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "settings.privacy_settings"
                )
            )

        except ValueError as error:

            db.session.rollback()

            flash(
                str(error),
                "error"
            )

        except Exception:

            db.session.rollback()

            flash(
                "Unable to update privacy preferences. "
                "Please try again.",
                "error"
            )

    return render_template(
        "settings_privacy.html",
        user=user,
        preferences=preferences
    )


# ============================================================
# NOTIFICATION SETTINGS
# ============================================================

@settings_bp.route(
    "/settings/notifications",
    methods=["GET", "POST"]
)
@login_required
def notification_settings():

    user = _get_authenticated_user()

    if not user:

        return (
            "Authenticated account could not be found.",
            401
        )

    preferences = (
        UserNotificationPreference.query
        .filter_by(
            user_id=user.id
        )
        .first()
    )

    if request.method == "POST":

        try:

            email_enabled = _get_form_boolean(
                request.form,
                "email_enabled"
            )

            sms_enabled = _get_form_boolean(
                request.form,
                "sms_enabled"
            )

            in_app_enabled = _get_form_boolean(
                request.form,
                "in_app_enabled"
            )

            order_notifications = _get_form_boolean(
                request.form,
                "order_notifications"
            )

            delivery_notifications = _get_form_boolean(
                request.form,
                "delivery_notifications"
            )

            security_notifications = _get_form_boolean(
                request.form,
                "security_notifications"
            )

            marketing_notifications = _get_form_boolean(
                request.form,
                "marketing_notifications"
            )

            if not preferences:

                preferences = UserNotificationPreference(
                    user_id=user.id
                )

                db.session.add(
                    preferences
                )

            preferences.email_enabled = (
                email_enabled
            )

            preferences.sms_enabled = (
                sms_enabled
            )

            preferences.in_app_enabled = (
                in_app_enabled
            )

            preferences.order_notifications = (
                order_notifications
            )

            preferences.delivery_notifications = (
                delivery_notifications
            )

            preferences.security_notifications = (
                security_notifications
            )

            preferences.marketing_notifications = (
                marketing_notifications
            )

            db.session.commit()

            flash(
                "Notification preferences updated successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "settings.notification_settings"
                )
            )

        except ValueError as error:

            db.session.rollback()

            flash(
                str(error),
                "error"
            )

        except Exception:

            db.session.rollback()

            flash(
                "Unable to update notification preferences. "
                "Please try again.",
                "error"
            )

    return render_template(
        "settings_notifications.html",
        user=user,
        preferences=preferences
    )


# ============================================================
# CONSENT & AGREEMENTS
# ============================================================

@settings_bp.route(
    "/settings/consent",
    methods=["GET", "POST"]
)
@login_required
def consent_settings():

    user = _get_authenticated_user()

    if not user:

        return (
            "Authenticated account could not be found.",
            401
        )

    if request.method == "POST":

        try:

            document_id = request.form.get(
                "document_id",
                ""
            ).strip()

            agreement = request.form.get(
                "agreement",
                ""
            ).strip().lower()

            if agreement not in {
                "1",
                "true",
                "on"
            }:

                raise ValueError(
                    "You must confirm that you have read and agree "
                    "to the selected document."
                )

            if not document_id:

                raise ValueError(
                    "A legal document must be selected."
                )

            if not document_id.isdigit():

                raise ValueError(
                    "Invalid legal document selection."
                )

            document_id = int(document_id)

            document = (
                LegalDocument.query
                .filter(
                    LegalDocument.id == document_id,
                    LegalDocument.is_active.is_(True)
                )
                .first()
            )

            if not document:

                raise ValueError(
                    "The selected legal document is not available."
                )

            existing_consent = (
                UserConsent.query
                .filter(
                    UserConsent.user_id == user.id,
                    UserConsent.legal_document_id
                    == document.id,
                    UserConsent.document_version
                    == document.version
                )
                .first()
            )

            if existing_consent:

                flash(
                    "You have already accepted this document version.",
                    "warning"
                )

                return redirect(
                    url_for(
                        "settings.consent_settings"
                    )
                )

            consent = UserConsent(
                user_id=user.id,
                legal_document_id=document.id,
                consent_type=document.document_type,
                document_version=document.version,
                ip_address=_get_request_ip(),
                user_agent=request.headers.get(
                    "User-Agent",
                    ""
                )[:500]
            )

            db.session.add(consent)
            db.session.commit()

            flash(
                f"{document.title} v{document.version} "
                "accepted successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "settings.consent_settings"
                )
            )

        except ValueError as error:

            db.session.rollback()

            flash(
                str(error),
                "error"
            )

        except Exception:

            db.session.rollback()

            flash(
                "Unable to record your consent. "
                "Please try again.",
                "error"
            )

    documents = _get_active_legal_documents()

    document_rows = []

    for document in documents:

        latest_consent = _get_latest_user_consent(
            user.id,
            document.document_type
        )

        accepted_current_version = (
            latest_consent is not None
            and latest_consent.document_version
            == document.version
        )

        document_rows.append(
            {
                "document": document,
                "latest_consent": latest_consent,
                "accepted_current_version":
                    accepted_current_version
            }
        )

    return render_template(
        "settings_consent.html",
        user=user,
        document_rows=document_rows
    )


# ============================================================
# REMAINING SETTINGS SECTIONS
# ============================================================

@settings_bp.route(
    "/settings/<section>"
)
@login_required
def settings_placeholder(section):

    if section in {
        "account",
        "business",
        "profile",
        "privacy",
        "notifications",
        "consent"
    }:

        abort(404)

    section_data = ACCOUNT_SETTINGS_SECTIONS.get(
        section
    )

    if not section_data:

        abort(404)

    user = _get_authenticated_user()

    if not user:

        return (
            "Authenticated account could not be found.",
            401
        )

    # Business-only sections must never become accessible merely
    # because a user manually enters their URL.
    if section == "users" and user.account_type != "admin":

        flash(
            "Users & Roles settings are available only to "
            "business accounts.",
            "error"
        )

        return redirect(
            url_for(
                "settings.settings"
            )
        )

    return render_template(
        "settings_placeholder.html",
        user=user,
        section=section,
        section_data=section_data
    )
