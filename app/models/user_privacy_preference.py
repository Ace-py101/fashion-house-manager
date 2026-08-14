from datetime import datetime

from app.database import db


class UserPrivacyPreference(db.Model):
    """
    Store user-controlled privacy preferences.

    The model is intentionally limited to preference state.
    Consent to legally required processing is handled through
    UserConsent and LegalDocument.
    """

    __tablename__ = "user_privacy_preferences"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True,
        index=True
    )

    analytics_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    personalization_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    marketing_enabled = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    data_sharing_enabled = db.Column(
        db.Boolean,
        default=False,
        nullable=False
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

    user = db.relationship(
        "User",
        back_populates="privacy_preferences"
    )

    def __repr__(self):
        return (
            f"<UserPrivacyPreference "
            f"user_id={self.user_id}>"
        )
