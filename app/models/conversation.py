from datetime import datetime

from app.database import db


class Conversation(db.Model):
    """
    Represents a communication thread between a client
    and a business/vendor.

    Messaging behavior will be implemented later.
    This model establishes the persistent communication
    structure first.
    """

    __tablename__ = "conversations"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    business_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=True,
        index=True
    )

    listing_id = db.Column(
        db.Integer,
        db.ForeignKey("marketplace_listings.id"),
        nullable=True,
        index=True
    )

    subject = db.Column(
        db.String(200),
        nullable=True
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="open",
        index=True
    )

    last_message_at = db.Column(
        db.DateTime,
        nullable=True,
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

    client = db.relationship(
        "User",
        foreign_keys=[client_id],
        backref="client_conversations"
    )

    business = db.relationship(
        "User",
        foreign_keys=[business_id],
        backref="business_conversations"
    )

    order = db.relationship(
        "Order",
        foreign_keys=[order_id],
        backref="conversations"
    )

    listing = db.relationship(
        "MarketplaceListing",
        foreign_keys=[listing_id],
        backref="conversations"
    )

    messages = db.relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )

    def __repr__(self):
        return (
            f"<Conversation "
            f"id={self.id} "
            f"client_id={self.client_id} "
            f"business_id={self.business_id} "
            f"status={self.status}>"
        )
