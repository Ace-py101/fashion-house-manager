from datetime import datetime

from app.database import db
from app.models.measurement import Measurement

from app.models.measurement_history import MeasurementHistory

def generate_measurement_id():

    today = datetime.now().strftime("%Y%m%d")

    latest = (
        Measurement.query
        .filter(
            Measurement.measurement_id.like(
                f"MEA-{today}-%"
            )
        )
        .order_by(
            Measurement.id.desc()
        )
        .first()
    )

    if latest:

        sequence = (
            int(
                latest.measurement_id.split("-")[-1]
            ) + 1
        )

    else:

        sequence = 1

    return (
        f"MEA-{today}-{sequence:03d}"
    )

def get_measurement_history(
    measurement_id
):
    """
    Return all history records for a measurement,
    newest first.
    """

    return (
        MeasurementHistory.query
        .filter_by(
            measurement_id=measurement_id
        )
        .order_by(
            MeasurementHistory.created_at.desc()
        )
        .all()
    )


def record_measurement_history(
    measurement,
    action,
    description
):
    """
    Save a measurement history record.
    """

    history = MeasurementHistory(
        measurement_id=measurement.id,
        action=action,
        description=description
    )

    db.session.add(history)


def create_measurement(
  
    order_id,
    customer_id,
    measurement_unit,
    measurement_type,
    measurement_data,
    notes=None
  
):
  
    measurement = Measurement(
  
        measurement_id=generate_measurement_id(),
  
        order_id=order_id,
  
        customer_id=customer_id,
  
        measurement_unit=measurement_unit,

        measurement_type=measurement_type,
  
        measurement_data=measurement_data,
  
        notes=notes
  
    )
  
    db.session.add(
        measurement
    )
    
    record_measurement_history(
        measurement,
        "Created",
        "Initial measurement record created."
    )
    
    db.session.commit()
    
    return measurement
    

def update_measurement(
    measurement,
    measurement_unit,
    measurement_type,
    measurement_data,
    notes=None
):
    """
    Update an existing measurement.
    """

    measurement.measurement_unit = measurement_unit

    measurement.measurement_type = measurement_type

    measurement.measurement_data = measurement_data

    measurement.notes = notes

    record_measurement_history(
        measurement,
        "Updated",
        "Measurement record updated."
    )

    db.session.commit()

    return measurement
    

from app.models.customer import Customer
from app.models.order import Order


def get_customer_for_measurement(customer_code):

    customer = (
        Customer.query
        .filter_by(
            customer_code=customer_code
        )
        .first()
    )

    if not customer:

        return None, []

    orders = (
        Order.query
        .filter_by(
            customer_id=customer.id,
            fulfillment_type="custom"
        )
        .order_by(
            Order.created_at.desc()
        )
        .all()
    )

    return customer, orders

# =========================================================
# QUERY FUNCTIONS
# =========================================================

def get_all_measurements():

    return (
        Measurement.query
        .order_by(
            Measurement.created_at.desc()
        )
        .all()
    )


def get_measurement_by_id(
    measurement_id
):

    return (

        Measurement.query

        .filter_by(
            id=measurement_id
        )

        .first()

    )


def get_measurements_by_order(
    order_id
):
    """
    Return all measurements
    belonging to an order,
    newest first.
    """

    return (

        Measurement.query

        .filter_by(
            order_id=order_id
        )

        .order_by(
            Measurement.created_at.desc()
        )

        .all()

    )

def search_measurements(
    keyword
):

    keyword = keyword.strip()

    return (
        Measurement.query
        .filter(
            Measurement.measurement_id.ilike(
                f"%{keyword}%"
            )
        )
        .order_by(
            Measurement.created_at.desc()
        )
        .all()
    )

def update_measurement(
    measurement,
    measurement_unit,
    measurement_type,
    measurement_data,
    notes
):
    measurement.measurement_unit = measurement_unit
    measurement.measurement_type = measurement_type
    measurement.measurement_data = measurement_data
    measurement.notes = notes

    db.session.commit()

    return measurement

# =========================================================
# MEASUREMENT ACTIVITY
# =========================================================

def get_measurement_activity(
    measurement_id
):
    """
    Return activity records for a measurement,
    newest first.
    """

    return (

        MeasurementHistory.query

        .filter_by(
            measurement_id=measurement_id
        )

        .order_by(
            MeasurementHistory.created_at.desc()
        )

        .all()

    )
