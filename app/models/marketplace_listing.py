from datetime import datetime

from app.database import db


class MarketplaceListing(db.Model):
    """
    Marketplace listing published by a business account.

    A listing may optionally originate from an existing Style record.
    Publication and marketplace behavior are handled by the service layer.
    """

    __tablename__ = "marketplace_listings"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    business_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    style_id = db.Column(
        db.Integer,
        db.ForeignKey("styles.id"),
        nullable=True,
        index=True,
    )

    title = db.Column(
        db.String(255),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    category = db.Column(
        db.String(100),
        nullable=True,
        index=True,
    )

    price = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    currency = db.Column(
        db.String(3),
        nullable=False,
        default="NGN",
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="draft",
        index=True,
    )

    featured = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    image_path = db.Column(
        db.String(500),
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    business = db.relationship(
        "User",
        foreign_keys=[business_id],
    )

    style = db.relationship(
        "Style",
        foreign_keys=[style_id],
    )

    def __repr__(self):
        return (
            f"<MarketplaceListing "
            f"id={self.id} "
            f"title={self.title!r} "
            f"business_id={self.business_id} "
            f"status={self.status}>"
        )
