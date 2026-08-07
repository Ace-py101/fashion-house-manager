from pathlib import Path


class DocumentType:

    MEASUREMENT = "measurement"

    ORDER = "order"

    PAYMENT = "payment"

    INVENTORY = "inventory"

    REPORT = "report"


class DocumentFormat:

    HTML = "html"

    PDF = "pdf"

    THERMAL = "thermal"


def build_document_filename(

    document_type,

    document_number,

    extension

):

    safe_number = (

        str(document_number)

        .replace("/", "-")

        .replace(" ", "_")

    )

    return (

        f"{document_type}_"

        f"{safe_number}."

        f"{extension}"

    )


def document_directory():

    base = (

        Path("generated_documents")

    )

    base.mkdir(

        exist_ok=True

    )

    return base


def build_document_path(

    document_type,

    document_number,

    extension

):

    return (

        document_directory()

        /

        build_document_filename(

            document_type,

            document_number,

            extension

        )

    )

from datetime import datetime


def build_document_context(

    *,

    document_type,

    document_number,

    title,

    customer=None,

    order=None,

    measurement=None,

    payment=None,

    inventory=None

):

    return {

        "document_type": document_type,

        "document_number": document_number,

        "document_title": title,

        "generated_at": datetime.utcnow(),

        "customer": customer,

        "order": order,

        "measurement": measurement,

        "payment": payment,

        "inventory": inventory

    }

from flask import url_for


def build_measurement_document_url(

    measurement

):

    return url_for(

        "measurement.print_measurement",

        measurement_id=measurement.id,

        _external=True

    )
