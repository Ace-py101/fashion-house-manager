from datetime import datetime

from app.database import db


class OrderHistory(db.Model):

    __tablename__ = "order_history"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )


    action = db.Column(
        db.String(100),
        nullable=False
    )


    field_name = db.Column(
        db.String(120),
        nullable=True
    )


    old_value = db.Column(
        db.Text,
        nullable=True
    )


    new_value = db.Column(
        db.Text,
        nullable=True
    )


    changed_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


    changed_by = db.Column(
        db.Integer,
        nullable=True
    )


    order = db.relationship(
        "Order",
        backref="history"
    )


    def __repr__(self):

        return (
            f"<OrderHistory {self.action}>"
        )
