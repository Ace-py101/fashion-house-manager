from datetime import datetime

from app.database import db


class Order(db.Model):

    __tablename__ = "orders"

    VALID_ORDER_TYPES = [
        "new",
        "amendment",
        "replacement",
    ]

    VALID_FULFILLMENT_TYPES = [
        "custom",
        "ready_to_wear",
    ]

    VALID_ORDER_STATUSES = [
        "new",
        "cutting",
        "sewing",
        "fitting",
        "alteration",
        "ready",
        "delivered",
        "cancelled",
    ]

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    order_id = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False
    )

    style_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "styles.id"
        ),
        nullable=True
    )

    order_type = db.Column(
        db.String(50),
        nullable=False,
        default="new"
    )

    fulfillment_type = db.Column(
        db.String(50),
        nullable=False,
        default="custom"
    )

    size = db.Column(
        db.Integer,
        nullable=True
    )

    garment_name = db.Column(
        db.String(120),
        nullable=False
    )

    fabric_name = db.Column(
        db.String(120),
        nullable=False
    )

    style_image = db.Column(
        db.String(255),
        nullable=True
    )

    delivery_date = db.Column(
        db.Date,
        nullable=False
    )

    delivered_at = db.Column(
        db.DateTime,
        nullable=True
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    deposit = db.Column(
        db.Float,
        nullable=False
    )

    balance = db.Column(
        db.Float,
        nullable=False
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="new"
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    customer = db.relationship(
        "Customer",
        backref="orders"
    )

    style = db.relationship(
        "Style",
        back_populates="orders"
    )

    def __repr__(self):
        return (
            f"<Order "
            f"{self.order_id} "
            f"({self.order_type}) "
            f"[{self.fulfillment_type}]>"
        )
