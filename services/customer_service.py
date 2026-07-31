from app.extensions import db
from app.models.customer import Customer
from app.validators.customer_validator import validate_customer


def create_customer(customer_data):
    """
    Create a new customer after validation
    """

    errors = validate_customer(customer_data)

    if errors:
        return {
            "success": False,
            "errors": errors
        }


    try:
        customer = Customer(
            name=customer_data["name"],
            phone=customer_data["phone"],
            address=customer_data.get("address"),
        )

        db.session.add(customer)
        db.session.commit()


        return {
            "success": True,
            "customer": customer
        }


    except Exception as e:

        db.session.rollback()

        return {
            "success": False,
            "errors": [str(e)]
        }
