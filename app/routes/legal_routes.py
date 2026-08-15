from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort
)

from app.services.auth_helpers import (
    current_user_id,
    login_required
)

from app.models.user import User

from app.services.legal_service import (
    get_active_legal_documents,
    get_legal_document
)

from app.services.consent_service import (
    get_user_consents,
    record_consent
)


legal_bp = Blueprint(
    "legal",
    __name__,
    url_prefix="/legal"
)


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
# LEGAL DOCUMENT INDEX
# ============================================================

@legal_bp.route("/")
@login_required
def legal_index():

    user = _get_authenticated_user()

    if not user:

        flash(
            "Your account session is no longer valid. "
            "Please log in again.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    documents = get_active_legal_documents()

    consents = get_user_consents(
        user.id
    )

    accepted_document_ids = {
        consent.legal_document_id
        for consent in consents
    }

    return render_template(
        "legal.html",
        user=user,
        documents=documents,
        accepted_document_ids=accepted_document_ids
    )


# ============================================================
# LEGAL DOCUMENT DETAIL
# ============================================================

@legal_bp.route(
    "/<int:document_id>"
)
@login_required
def legal_document(document_id):

    user = _get_authenticated_user()

    if not user:

        flash(
            "Your account session is no longer valid. "
            "Please log in again.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    document = get_legal_document(
        document_id
    )

    if not document:

        abort(404)

    # Active documents are publicly discoverable to the
    # authenticated account.
    #
    # Historical/inactive documents may only be viewed when
    # the current user previously accepted that exact version.

    if not document.is_active:

        historical_consent = (
            next(
                (
                    consent
                    for consent in get_user_consents(user.id)
                    if consent.legal_document_id == document.id
                ),
                None
            )
        )

        if not historical_consent:

            abort(404)

    accepted = any(
        consent.legal_document_id == document.id
        for consent in get_user_consents(user.id)
    )

    return render_template(
        "legal_document.html",
        user=user,
        document=document,
        accepted=accepted
    )


# ============================================================
# ACCEPT LEGAL DOCUMENT
# ============================================================

@legal_bp.route(
    "/consent/<int:document_id>",
    methods=["POST"]
)
@login_required
def accept_consent(document_id):

    user = _get_authenticated_user()

    if not user:

        flash(
            "Your account session is no longer valid. "
            "Please log in again.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    document = get_legal_document(
        document_id
    )

    if not document or not document.is_active:

        flash(
            "The selected legal document is no longer available "
            "for acceptance.",
            "error"
        )

        return redirect(
            url_for("legal.legal_index")
        )

    accepted = request.form.get(
        "accept_consent"
    )

    if accepted != "1":

        flash(
            "You must explicitly confirm that you accept "
            "this document.",
            "warning"
        )

        return redirect(
            url_for(
                "legal.legal_document",
                document_id=document.id
            )
        )

    try:

        consent, created = record_consent(
            user=user,
            legal_document=document,
            ip_address=request.remote_addr,
            user_agent=request.headers.get(
                "User-Agent"
            )
        )

        if created:

            flash(
                f"You accepted {document.title} "
                f"version {document.version}.",
                "success"
            )

        else:

            flash(
                f"You have already accepted {document.title} "
                f"version {document.version}.",
                "warning"
            )

    except ValueError as error:

        flash(
            str(error),
            "error"
        )

    except Exception:

        flash(
            "Unable to record your consent. "
            "Please try again.",
            "error"
        )

    return redirect(
        url_for(
            "legal.legal_document",
            document_id=document.id
        )
    )


# ============================================================
# CONSENT HISTORY
# ============================================================

@legal_bp.route(
    "/consent-history"
)
@login_required
def consent_history():

    user = _get_authenticated_user()

    if not user:

        flash(
            "Your account session is no longer valid. "
            "Please log in again.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    consents = get_user_consents(
        user.id
    )

    return render_template(
        "consent.html",
        user=user,
        consents=consents
    )
