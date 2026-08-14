from datetime import datetime

from app.database import db


class UserConsent(db.Model):
    """
    Store an auditable record of a user's acceptance of a
    specific version of a legal document.

    The accepted document version is copied onto this record
    so the historical consent remains identifiable even if
    the associated legal document is later changed.
    """

    __tablename__ = "user_consents"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    legal_document_id = db.Column(
        db.Integer,
        db.ForeignKey("legal_documents.id"),
        nullable=False,
        index=True
    )

    consent_type = db.Column(
        db.String(50),
        nullable=False,
        index=True
    )

    document_version = db.Column(
        db.String(30),
        nullable=False
    )

    accepted_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    ip_address = db.Column(
        db.String(45),
        nullable=True
    )

    user_agent = db.Column(
        db.Text,
        nullable=True
    )

    user = db.relationship(
        "User",
        back_populates="consents"
    )

    legal_document = db.relationship(
        "LegalDocument",
        back_populates="consents"
    )

    def __repr__(self):
        return (
            f"<UserConsent "
            f"user_id={self.user_id} "
            f"type={self.consent_type} "
            f"version={self.document_version}>"
        )
