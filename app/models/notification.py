from datetime import datetime

from app.database import db


class Notification(db.Model):
    """
    Persistent in-app notification.

    Notifications belong to an individual user and are consumed
    by the global notification shell.
    """

    __tablename__ = "notifications"

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

    notification_type = db.Column(
        db.String(50),
        nullable=False,
        index=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    message = db.Column(
        db.String(1000),
        nullable=False
    )

    link = db.Column(
        db.String(500),
        nullable=True
    )

    is_read = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "notifications",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

    def __repr__(self):
        return (
            f"<Notification "
            f"id={self.id} "
            f"user_id={self.user_id} "
            f"type={self.notification_type!r} "
            f"read={self.is_read}>"
        )
