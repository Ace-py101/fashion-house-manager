from datetime import datetime

from sqlalchemy import JSON

from app.database import db


class Measurement(db.Model):

    __tablename__ = "measurements"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    measurement_id = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False
    )

    measurement_unit = db.Column(
        db.String(20),
        nullable=False
    )

    measurement_type = db.Column(
        db.String(50),
        nullable=False,
        default="Initial"
    )

    measurement_data = db.Column(
        JSON,
        nullable=False
    )

    notes = db.Column(
        db.Text
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

    order = db.relationship(
        "Order",
        backref="measurements"
    )

    customer = db.relationship(
        "Customer",
        backref="measurements"
    )
