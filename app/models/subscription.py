from datetime import datetime


from app.database import db


class Subscription(db.Model):
    """
    Store the subscription state belonging to an account.

    This is the foundation only. Billing, payments, upgrades,
    renewals and cancellations will be implemented later.
    """

    __tablename__ = "subscriptions"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id"
        ),
        nullable=False,
        unique=True,
        index=True
    )


    plan = db.Column(
        db.String(50),
        nullable=False,
        default="free"
    )


    status = db.Column(
        db.String(30),
        nullable=False,
        default="active"
    )


    started_at = db.Column(
        db.DateTime,
        nullable=True
    )


    expires_at = db.Column(
        db.DateTime,
        nullable=True
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


    def __repr__(self):
        return (
            f"<Subscription "
            f"user_id={self.user_id} "
            f"plan={self.plan} "
            f"status={self.status}>"
        )
