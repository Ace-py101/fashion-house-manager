from datetime import datetime

from app.database import db


class UserNotificationPreference(db.Model):
    """
    Store user notification preferences.

    Notification behavior will be implemented later.
    This model establishes the persistent configuration
    foundation for the Notifications settings area.
    """

    __tablename__ = "user_notification_preferences"

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

    email_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    sms_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    in_app_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    order_notifications = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    delivery_notifications = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    security_notifications = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    marketing_notifications = db.Column(
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
        back_populates="notification_preferences"
    )

    def __repr__(self):
        return (
            f"<UserNotificationPreference "
            f"user_id={self.user_id}>"
        )
