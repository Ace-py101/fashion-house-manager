from datetime import datetime

from app.database import db


class MeasurementHistory(db.Model):

    __tablename__ = "measurement_history"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    measurement_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "measurements.id"
        ),
        nullable=False
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "orders.id"
        ),
        nullable=False
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "customers.id"
        ),
        nullable=False
    )

    activity = db.Column(
        db.String(50),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    created_by = db.Column(
        db.String(100),
        default="System"
    )
