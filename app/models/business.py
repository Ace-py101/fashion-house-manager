from datetime import datetime

from app.database import db


class Business(db.Model):
    """
    Business / organization identity.

    A Business is the organizational boundary for the
    business-side ATELIIER_FHM account.

    Users, roles, permissions, subscriptions, billing and
    audit records can be associated with this business as
    those Settings foundations are implemented.
    """

    __tablename__ = "businesses"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
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

    users = db.relationship(
        "User",
        back_populates="business",
        lazy=True
    )

    def __repr__(self):

        return (
            f"<Business "
            f"id={self.id} "
            f"name={self.name!r}>"
        )
