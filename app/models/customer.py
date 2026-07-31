from datetime import datetime

from app.database import db



class Customer(db.Model):

    __tablename__ = "customers"



    id = db.Column(
        db.Integer,
        primary_key=True
    )



    customer_code = db.Column(

        db.String(20),

        unique=True,

        nullable=False

    )



    full_name = db.Column(

        db.String(100),

        nullable=False

    )



    phone = db.Column(

        db.String(20),

        nullable=False

    )



    email = db.Column(

        db.String(120),

        unique=True,

        nullable=True

    )



    address = db.Column(

        db.Text,

        nullable=True

    )



    gender = db.Column(

        db.String(20),

        nullable=False

    )



    status = db.Column(

        db.String(20),

        default="Active",

        nullable=False

    )



    notes = db.Column(

        db.Text,

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

        onupdate=datetime.utcnow

    )



    created_by = db.Column(

        db.Integer,

        nullable=True

    )




    def __repr__(self):

        return f"<Customer {self.full_name}>"
