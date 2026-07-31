from datetime import datetime

from app.database import db



class CustomerHistory(db.Model):

    __tablename__ = "customer_history"



    id = db.Column(
        db.Integer,
        primary_key=True
    )


    customer_id = db.Column(
        db.Integer,
        nullable=False
    )


    field_name = db.Column(
        db.String(100),
        nullable=False
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



    def __repr__(self):

        return (
            f"<CustomerHistory "
            f"{self.field_name}>"
        )
