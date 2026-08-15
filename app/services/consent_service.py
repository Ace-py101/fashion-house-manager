from datetime import datetime

from app.database import db
from app.models.user_consent import UserConsent
from app.models.legal_document import LegalDocument


def get_user_consents(user_id):
    """
    Return the user's consent history.
    """
    return (
        UserConsent.query
        .filter_by(user_id=user_id)
        .order_by(
            UserConsent.accepted_at.desc()
        )
        .all()
    )


def has_user_accepted(
    user_id,
    legal_document_id
):
    """
    Determine whether the user has already accepted
    the specified legal document version.
    """
    return (
        UserConsent.query
        .filter_by(
            user_id=user_id,
            legal_document_id=legal_document_id
        )
        .first()
        is not None
    )


def record_consent(
    user,
    legal_document,
    ip_address=None,
    user_agent=None
):
    """
    Record acceptance of an exact legal-document version.

    Historical consent records are never updated when a newer
    legal document version is published.
    """

    if not user:
        raise ValueError(
            "Authenticated user is required."
        )

    if not legal_document:
        raise ValueError(
            "Legal document not found."
        )

    if not legal_document.is_active:
        raise ValueError(
            "This legal document is no longer active."
        )

    existing = (
        UserConsent.query
        .filter_by(
            user_id=user.id,
            legal_document_id=legal_document.id
        )
        .first()
    )

    if existing:
        return existing, False

    consent = UserConsent(
        user_id=user.id,
        legal_document_id=legal_document.id,
        consent_type=legal_document.document_type,
        document_version=legal_document.version,
        accepted_at=datetime.utcnow(),
        ip_address=ip_address,
        user_agent=user_agent
    )

    db.session.add(consent)
    db.session.commit()

    return consent, True
