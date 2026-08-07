from datetime import datetime

from app.database import db
from app.models.customer import Customer
from app.models.customer_history import CustomerHistory
from app.validators.customer_validator import validate_customer


def generate_customer_code(phone):
    """
    Generate unique customer code.

    Format:
    CUS-YYYYMMDD-XXX-NNN

    XXX = last 3 digits of phone number
    NNN = daily sequence number
    """

    today = datetime.now().strftime("%Y%m%d")

    last_three = phone[-3:]

    prefix = f"CUS-{today}-{last_three}"

    latest_customer = (
        Customer.query
        .filter(
            Customer.customer_code.like(
                f"{prefix}-%"
            )
        )
        .order_by(
            Customer.id.desc()
        )
        .first()
    )

    if latest_customer:

        last_sequence = int(
            latest_customer.customer_code.split("-")[-1]
        )

        sequence = last_sequence + 1

    else:

        sequence = 1

    return f"{prefix}-{sequence:03d}"


def create_customer(customer_data):
    """
    Validate and create customer.
    """

    errors = validate_customer(customer_data)

    if errors:

        return {
            "success": False,
            "errors": errors
        }


    phone = customer_data["phone"].strip()


    existing_customer = (
        Customer.query
        .filter_by(phone=phone)
        .first()
    )


    if existing_customer:

        return {
            "success": False,
            "errors": [
                "Phone number already exists."
            ]
        }


    customer = Customer(

        customer_code=generate_customer_code(phone),

        full_name=customer_data["full_name"].strip(),

        phone=phone,

        email=customer_data.get("email", "").strip() or None,

        address=customer_data.get("address", "").strip() or None,

        gender=customer_data["gender"],

        notes=customer_data.get("notes", "").strip() or None

    )


    try:

        db.session.add(customer)

        db.session.flush()


        create_customer_history(

            customer_id=customer.id,

            action="CREATE",

            field_name="Customer Profile",

            old_value="-",

            new_value="Customer created",

            changed_by=None

        )


        db.session.commit()


        return {
            "success": True,
            "customer": customer
        }


    except Exception as e:

        db.session.rollback()

        return {
            "success": False,
            "errors": [
                str(e)
            ]
        }



def get_all_customers():

    return (
        Customer.query
        .filter_by(status="Active")
        .order_by(Customer.id.desc())
        .all()
    )



def search_customers(query):

    search = query.strip()

    if not search:

        return []


    return (

        Customer.query
        .filter(
            db.or_(

                Customer.customer_code.ilike(
                    f"%{search}%"
                ),

                Customer.full_name.ilike(
                    f"%{search}%"
                ),

                Customer.phone.ilike(
                    f"%{search}%"
                )

            )
        )
        .order_by(
            Customer.id.desc()
        )
        .all()

    )



def get_customer_by_id(customer_id):

    return (

        Customer.query
        .filter_by(
            id=customer_id
        )
        .first()

    )



def update_customer(customer_id, customer_data):

    errors = validate_customer(customer_data)


    if errors:

        return {
            "success": False,
            "errors": errors
        }


    customer = get_customer_by_id(customer_id)


    if not customer:

        return {
            "success": False,
            "errors": [
                "Customer not found."
            ]
        }


    existing_phone = (

        Customer.query
        .filter(
            Customer.phone == customer_data["phone"],
            Customer.id != customer_id
        )
        .first()

    )


    if existing_phone:

        return {
            "success": False,
            "errors": [
                "Phone number already exists."
            ]
        }


    try:

        record_customer_changes(
            customer,
            customer_data
        )


        customer.full_name = customer_data["full_name"].strip()

        customer.phone = customer_data["phone"].strip()

        customer.email = (
            customer_data.get("email") or None
        )

        customer.address = (
            customer_data.get("address") or None
        )

        customer.gender = customer_data["gender"]

        customer.notes = (
            customer_data.get("notes") or None
        )


        db.session.commit()


        return {
            "success": True,
            "customer": customer
        }


    except Exception as e:

        db.session.rollback()

        return {
            "success": False,
            "errors": [
                str(e)
            ]
        }



def create_customer_history(
    customer_id,
    action,
    field_name,
    old_value,
    new_value,
    changed_by=None
):

    history = CustomerHistory(

        customer_id=customer_id,

        action=action,

        field_name=field_name,

        old_value=str(old_value) if old_value else "",

        new_value=str(new_value) if new_value else "",

        changed_by=changed_by

    )


    db.session.add(history)



def record_customer_changes(customer, new_data):

    fields = {

        "full_name": "Full Name",

        "phone": "Phone Number",

        "email": "Email",

        "address": "Address",

        "gender": "Gender",

        "notes": "Notes"

    }


    for field, label in fields.items():


        old_value = getattr(
            customer,
            field
        )


        new_value = new_data.get(
            field
        )


        if str(old_value or "") != str(new_value or ""):


            create_customer_history(

                customer_id=customer.id,

                action="UPDATE",

                field_name=label,

                old_value=old_value,

                new_value=new_value,

                changed_by=None

            )



def get_customer_history(customer_id):

    return (

        CustomerHistory.query
        .filter_by(
            customer_id=customer_id
        )
        .order_by(
            CustomerHistory.changed_at.desc()
        )
        .all()

    )



def deactivate_customer(customer_id):

    customer = get_customer_by_id(
        customer_id
    )


    if not customer:

        return {

            "success": False,

            "errors": [
                "Customer not found."
            ]

        }


    old_status = customer.status


    customer.status = "Inactive"


    create_customer_history(

        customer_id=customer.id,

        action="UPDATE",

        field_name="Status",

        old_value=old_status,

        new_value="Inactive",

        changed_by=None

    )


    db.session.commit()


    return {

        "success": True,

        "errors": []

    }


def get_inactive_customers():

    return (

        Customer.query
        .filter_by(
            status="Inactive"
        )
        .order_by(
            Customer.id.desc()
        )
        .all()

    )


def activate_customer(customer_id):

    customer = get_customer_by_id(
        customer_id
    )

    if not customer:

        return {

            "success": False,

            "errors": [
                "Customer not found."
            ]

        }

    old_status = customer.status

    customer.status = "Active"

    create_customer_history(

        customer_id=customer.id,

        action="UPDATE",

        field_name="Status",

        old_value=old_status,

        new_value="Active",

        changed_by=None

    )

    db.session.commit()

    return {

        "success": True,

        "errors": []

    }
