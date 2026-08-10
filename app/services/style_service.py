from datetime import datetime

from sqlalchemy import or_

from app.database import db
from app.models.style import Style

import os

from uuid import uuid4

from werkzeug.utils import secure_filename

from flask import current_app


VALID_STYLE_TYPES = [
    "Custom Made",
    "Ready to Wear"
]

VALID_OCCASION_FITS = [
    "Casual",
    "Corporate",
    "Traditional",
    "Wedding",
    "Party",
    "Ceremonial",
    "Sports",
    "Uniform",
    "Everyday",
    "Other"
]

VALID_GARMENT_NAMES = [
    "Agbada",
    "Boubou",
    "Kaftan",
    "Senator",
    "Native",
    "Shirt",
    "Trousers",
    "Jumpsuit",
    "Gown",
    "Dress",
    "Skirt",
    "Blouse",
    "Suit",
    "Blazer",
    "Two-Piece",
    "Three-Piece",
    "Tunic",
    "Top",
    "Shorts",
    "Children's Wear",
    "Other"
]

VALID_GENDERS = [
    "Male",
    "Female",
    "Unisex"
]

VALID_STATUSES = [
    "Active",
    "Archived"
]


ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}


def generate_style_id():

    today = datetime.now().strftime(
        "%Y%m%d"
    )

    prefix = f"STY-{today}-"

    latest = (
        Style.query
        .filter(
            Style.style_id.like(
                f"{prefix}%"
            )
        )
        .order_by(
            Style.id.desc()
        )
        .first()
    )

    if latest:

        number = int(
            latest.style_id.split(
                "-"
            )[-1]
        ) + 1

    else:

        number = 1

    return (
        f"{prefix}{number:03d}"
    )

def allowed_image(

    filename

):

    if (

        not filename
        or
        "." not in filename

    ):

        return False

    extension = (

        filename.rsplit(
            ".",
            1
        )[1]

        .lower()

    )

    return (

        extension

        in

        ALLOWED_IMAGE_EXTENSIONS

    )


def save_style_image(
    image_file
):
    """
    Save an uploaded style image and
    return the stored filename.
    """

    if (
        not image_file
        or
        image_file.filename == ""
    ):
        return None

    if not allowed_image(
        image_file.filename
    ):
        return None

    filename = secure_filename(
        image_file.filename
    )

    extension = (
        filename.rsplit(
            ".",
            1
        )[1]
        .lower()
    )

    unique_filename = (
        f"{uuid4().hex}.{extension}"
    )

    image_file.save(

        os.path.join(

            current_app.config[
                "UPLOAD_FOLDERS"
            ]["styles"],

            unique_filename

        )

    )

    return unique_filename


def create_style(
    image_file=None,
    **kwargs
):

    image_filename = save_style_image(
        image_file
    )

    style = Style(

        style_id=generate_style_id(),

        image_filename=image_filename,

        **kwargs

    )

    db.session.add(
        style
    )

    db.session.commit()

    return style


def get_all_styles():

    return (

        Style.query

        .order_by(

            Style.created_at.desc()

        )

        .all()

    )


def get_style_by_id(

    style_id

):

    return (

        Style.query

        .filter_by(

            id=style_id

        )

        .first()

    )


def search_styles(

    keyword

):

    if not keyword:

        return []

    keyword = keyword.strip()

    return (

        Style.query

        .filter(

            or_(

                Style.style_code.ilike(

                    f"%{keyword}%"

                ),

                Style.style_name.ilike(

                    f"%{keyword}%"

                ),

                Style.garment_type.ilike(

                    f"%{keyword}%"

                ),

                Style.tags.ilike(

                    f"%{keyword}%"

                )

            )

        )

        .order_by(

            Style.created_at.desc()

        )

        .all()

    )


def archive_style(

    style

):

    style.status = "Archived"

    db.session.commit()


def activate_style(

    style

):

    style.status = "Active"

    db.session.commit()


