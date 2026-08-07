from datetime import datetime

from sqlalchemy import or_

from app.database import db
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_history import OrderHistory
from app.constants.garments import VALID_GARMENT_NAMES


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


def generate_order_id():

    today = datetime.now().strftime("%Y%m%d")

    last_order = (
        Order.query
        .filter(
            Order.order_id.like(
                f"ORD-{today}-%"
            )
        )
        .order_by(
            Order.id.desc()
        )
        .first()
    )

    if last_order:

        last_number = int(
            last_order.order_id.split("-")[-1]
        )

        new_number = last_number + 1

    else:

        new_number = 1

    return f"ORD-{today}-{new_number:03d}"


def validate_order_type(order_type):

    if order_type not in VALID_ORDER_TYPES:

        raise ValueError(
            "Invalid order type."
        )


def validate_fulfillment_type(fulfillment_type):

    if fulfillment_type not in VALID_FULFILLMENT_TYPES:

        raise ValueError(
            "Invalid fulfillment type."
        )


def validate_order_status(status):

    if status not in VALID_ORDER_STATUSES:

        raise ValueError(
            "Invalid order status."
        )


def validate_order_data(
    garment_name,
    fabric_name,
    price,
    deposit,
    fulfillment_type,
    size
):

    if not garment_name or not garment_name.strip():

        raise ValueError(
            "Garment name is required."
        )

    if garment_name not in VALID_GARMENT_NAMES:
    
        raise ValueError(
            "Please select a valid garment."
        )
    
    if not fabric_name or not fabric_name.strip():

        raise ValueError(
            "Garment style is required."
        )

    if price <= 0:

        raise ValueError(
            "Price must be greater than zero."
        )

    if deposit < 0:

        raise ValueError(
            "Deposit cannot be negative."
        )

    if deposit > price:

        raise ValueError(
            "Deposit cannot be greater than price."
        )

    if fulfillment_type == "ready_to_wear":
     
         if size in ("", None):
     
             raise ValueError(
                 "Size is required for Ready-to-Wear orders."
             )
     
         try:
     
             int(size)
     
         except (TypeError, ValueError):
     
             raise ValueError(
                 "Size must be a number."
             )

     
def calculate_balance(
    price,
    deposit
):

    return price - deposit


def create_order_history(
    order_id,
    action,
    field_name,
    old_value=None,
    new_value=None,
    changed_by=None
):

    history = OrderHistory(

        order_id=order_id,

        action=action,

        field_name=field_name,

        old_value=old_value,

        new_value=new_value,

        changed_by=changed_by

    )

    db.session.add(history)


def create_order(
    customer_id,
    order_type,
    fulfillment_type,
    size,
    garment_name,
    fabric_name,
    delivery_date,
    price,
    deposit,
    style_image=None,
    status="new",
    notes=None
):
    validate_order_type(
        order_type
    )

    validate_fulfillment_type(
        fulfillment_type
    )

    validate_order_status(
        status
    )

    validate_order_data(
        garment_name,
        fabric_name,
        price,
        deposit,
        fulfillment_type,
        size
    )

    if size in ("", None):
    
        size = None
    
    else:
    
        size = int(size)
    
    order = Order(

        order_id=generate_order_id(),

        customer_id=customer_id,

        order_type=order_type,

        fulfillment_type=fulfillment_type,

        size=size,

        garment_name=garment_name,

        fabric_name=fabric_name,

        style_image=style_image,

        delivery_date=delivery_date,

        price=price,

        deposit=deposit,

        balance=calculate_balance(
            price,
            deposit
        ),

        status=status,

        notes=notes

    )

    db.session.add(order)

    db.session.flush()

    create_order_history(

        order.id,

        "CREATE",

        "order",

        None,

        order.order_id

    )

    db.session.commit()

    return order


def get_all_orders():

    return (
        Order.query
        .order_by(
            Order.created_at.desc()
        )
        .all()
    )


def get_order_by_id(order_id):

    return (
        Order.query
        .filter_by(
            order_id=order_id
        )
        .first()
    )


def search_orders(query):

    search = query.strip()

    if not search:

        return []

    return (

        Order.query

        .join(Customer)

        .filter(

            or_(

                Order.order_id.ilike(
                    f"%{search}%"
                ),

                Customer.customer_code.ilike(
                    f"%{search}%"
                ),

                Customer.full_name.ilike(
                    f"%{search}%"
                ),

                Customer.phone.ilike(
                    f"%{search}%"
                ),

                Order.garment_name.ilike(
                    f"%{search}%"
                )

            )

        )

        .order_by(
            Order.created_at.desc()
        )

        .all()

    )


def get_order_history(order_id):

    return (

        OrderHistory.query

        .filter_by(
            order_id=order_id
        )

        .order_by(
            OrderHistory.changed_at.desc()
        )

        .all()

    )


def update_order(
    order,
    fulfillment_type,
    size,
    garment_name,
    fabric_name,
    delivery_date,
    price,
    deposit,
    style_image=None,
    status="new",
    notes=None
):

    validate_order_status(
        status
    )

    validate_order_data(
        garment_name,
        fabric_name,
        price,
        deposit,
        fulfillment_type,
        size
    )

    new_balance = calculate_balance(
        price,
        deposit
    )

    changes = [

        (
            "garment_name",
            order.garment_name,
            garment_name
        ),

        (
            "fabric_name",
            order.fabric_name,
            fabric_name
        ),

        (
            "delivery_date",
            str(order.delivery_date),
            str(delivery_date)
        ),

        (
            "price",
            str(order.price),
            str(price)
        ),

        (
            "deposit",
            str(order.deposit),
            str(deposit)
        ),

        (
            "balance",
            str(order.balance),
            str(new_balance)
        ),

        (
            "size",
            str(order.size),
            str(size)
        ),
        
        (
            "status",
            order.status,
            status
        ),

        (
            "notes",
            order.notes,
            notes
        )

    ]

    if style_image:

        changes.append(

            (
                "style_image",
                order.style_image,
                style_image
            )

        )

    for field, old_value, new_value in changes:

        if str(old_value) != str(new_value):

            create_order_history(

                order.id,

                "UPDATE",

                field,

                str(old_value) if old_value else "",

                str(new_value) if new_value else ""

            )

    order.fulfillment_type = fulfillment_type
    
    order.size = (
        int(size)
        if size not in ("", None)
        else None
    )
    
    order.garment_name = garment_name
    order.fabric_name = fabric_name
    order.delivery_date = delivery_date
    order.price = price
    order.deposit = deposit
    order.balance = new_balance
    order.status = status
    order.notes = notes

    if style_image:

        order.style_image = style_image

    if status == "delivered":

        if not order.delivered_at:

            order.delivered_at = datetime.utcnow()

    else:

        order.delivered_at = None

    order.updated_at = datetime.utcnow()

    db.session.commit()

    return order


def update_order_status(
    order,
    status
):

    validate_order_status(
        status
    )

    old_status = order.status

    if old_status != status:

        create_order_history(

            order.id,

            "STATUS_CHANGE",

            "status",

            old_status,

            status

        )

    order.status = status

    if status == "delivered":

        if not order.delivered_at:

            order.delivered_at = datetime.utcnow()

    else:

        order.delivered_at = None

    order.updated_at = datetime.utcnow()

    db.session.commit()

    return order


def get_order_measurement_summary(order):

    return {

        "measurement_status": "Pending",

        "measurement_count": 0,

        "measurement_revisions": 0,

        "last_measurement_update": None

    }


def get_order_payment_summary(order):

    paid = order.deposit

    return {

        "payment_status": (
            "Paid"
            if order.balance <= 0
            else "Outstanding"
        ),

        "payment_transactions": 1 if paid > 0 else 0,

        "total_price": order.price,

        "total_paid": paid,

        "outstanding_balance": order.balance

    }


def get_order_production_summary(order):

    completed = {

        "new": 10,
        "cutting": 25,
        "sewing": 50,
        "fitting": 70,
        "alteration": 85,
        "ready": 100,
        "delivered": 100,
        "cancelled": 0

    }

    return {

        "current_stage": order.status,

        "progress": completed.get(
            order.status,
            0
        )

    }


def get_order_delivery_summary(order):

    return {

        "expected_delivery": order.delivery_date,

        "delivered_at": order.delivered_at,

        "delivery_status": order.status,

        "delivery_notes": None

    }


def get_order_activity(order):

    return {

        "order": order,

        "history": get_order_history(
            order.id
        ),

        "production": get_order_production_summary(
            order
        ),

        "measurements": get_order_measurement_summary(
            order
        ),

        "payments": get_order_payment_summary(
            order
        ),

        "delivery": get_order_delivery_summary(
            order
        )

    }


def get_active_orders_count():

    return (

        Order.query

        .filter(

            Order.status.in_(

                [

                    "new",

                    "cutting",

                    "sewing",

                    "fitting",

                    "alteration"

                ]

            )

        )

        .count()

    )
