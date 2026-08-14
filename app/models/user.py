from datetime import datetime

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app.database import db


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    account_type = db.Column(
        db.String(20),
        nullable=False
    )

    # ============================================================
    # EMAIL VERIFICATION
    # ============================================================

    email_verified = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    email_verified_at = db.Column(
        db.DateTime,
        nullable=True
    )

    email_verification_token_hash = db.Column(
        db.String(255),
        nullable=True,
        unique=True
    )

    email_verification_token_expires_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # ============================================================
    # PASSWORD RESET
    #
    # The raw reset token is never stored in the database.
    # Only its SHA-256 hash is stored.
    # ============================================================

    password_reset_token_hash = db.Column(
        db.String(255),
        nullable=True,
        unique=True
    )

    password_reset_token_expires_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # ============================================================
    # PHONE VERIFICATION
    #
    # The verification OTP itself is never stored in plaintext.
    # Only the SHA-256 hash is persisted.
    # ============================================================

    phone_number = db.Column(
        db.String(30),
        nullable=True,
        unique=True,
        index=True
    )

    phone_verified = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    phone_verified_at = db.Column(
        db.DateTime,
        nullable=True
    )

    phone_verification_code_hash = db.Column(
        db.String(255),
        nullable=True
    )

    phone_verification_code_expires_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # ============================================================
    # BUSINESS IDENTITY
    # ============================================================

    business_name = db.Column(
        db.String(150),
        nullable=True,
        index=True
    )

    # ============================================================
    # ACCOUNT SETTINGS RELATIONSHIPS
    # ============================================================

    consents = db.relationship(
        "UserConsent",
        back_populates="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    privacy_preferences = db.relationship(
        "UserPrivacyPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    notification_preferences = db.relationship(
        "UserNotificationPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # ============================================================
    # TIMESTAMPS
    # ============================================================

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

    # ============================================================
    # PASSWORD METHODS
    # ============================================================

    def set_password(self, password):

        self.password_hash = (
            generate_password_hash(password)
        )

    def check_password(self, password):

        return check_password_hash(
            self.password_hash,
            password
        )

    # ============================================================
    # REPRESENTATION
    # ============================================================

    def __repr__(self):

        return (
            f"<User {self.email} "
            f"({self.account_type})>"
        )
