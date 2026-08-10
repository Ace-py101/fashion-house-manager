from datetime import datetime

from app.database import db


class Style(db.Model):

    __tablename__ = "styles"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    style_id = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
        index=True
    )

    style_name = db.Column(
        db.String(120),
        nullable=False
    )

    style_type = db.Column(
        db.String(50),
        nullable=False
    )

    occasion_fit = db.Column(
        db.String(80),
        nullable=False
    )

    garment_name = db.Column(
        db.String(80),
        nullable=False
    )

    gender = db.Column(
        db.String(20),
        nullable=False
    )

    fabric_requirement = db.Column(
        db.String(120),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Active"
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

    image_filename = db.Column(
        db.String(255)
    )

    orders = db.relationship(
        "Order",
        back_populates="style",
        lazy=True
    )

    def __repr__(self):

        return (
            f"<Style {self.style_id}>"
        )
