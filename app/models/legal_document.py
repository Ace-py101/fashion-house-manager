from datetime import datetime

from app.database import db


class LegalDocument(db.Model):
    """
    Store versioned legal documents used by Ateliier_fhm.

    Examples:
        - Privacy Policy
        - Terms & Conditions
        - Cookie Policy
        - Acceptable Use Policy

    Legal content is versioned so historical user consent can
    remain associated with the exact document version accepted.
    """

    __tablename__ = "legal_documents"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    document_type = db.Column(
        db.String(50),
        nullable=False,
        index=True
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    version = db.Column(
        db.String(30),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    effective_at = db.Column(
        db.DateTime,
        nullable=True
    )

    published_at = db.Column(
        db.DateTime,
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            "document_type",
            "version",
            name="uq_legal_document_type_version"
        ),
    )

    consents = db.relationship(
        "UserConsent",
        back_populates="legal_document",
        lazy=True
    )

    def __repr__(self):
        return (
            f"<LegalDocument "
            f"{self.document_type} "
            f"v{self.version}>"
        )
