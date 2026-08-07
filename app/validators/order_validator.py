from datetime import datetime


ALLOWED_STATUSES = [
    "new",
    "cutting",
    "sewing",
    "ready",
    "delivered"
]


def validate_required(value):

    if value is None:
        return False

    if str(value).strip() == "":
        return False

    return True



def validate_price(price):

    try:

        price = float(price)

        return price > 0

    except (ValueError, TypeError):

        return False



def validate_deposit(price, deposit):

    try:

        price = float(price)

        deposit = float(deposit)

        return (
            deposit >= 0
            and deposit <= price
        )

    except (ValueError, TypeError):

        return False



def validate_delivery_date(date_value):

    try:

        if isinstance(date_value, datetime):

            return True


        datetime.strptime(
            str(date_value),
            "%Y-%m-%d"
        )

        return True


    except ValueError:

        return False



def validate_status(status):

    return status in ALLOWED_STATUSES



def validate_order(data):

    errors = []


    required_fields = [
        "customer_id",
        "garment_name",
        "fabric_name",
        "delivery_date",
        "price",
        "deposit"
    ]


    for field in required_fields:

        if not validate_required(
            data.get(field)
        ):

            errors.append(
                f"{field.replace('_',' ').title()} is required."
            )


    if "price" in data:

        if not validate_price(
            data.get("price")
        ):

            errors.append(
                "Price must be greater than zero."
            )


    if "price" in data and "deposit" in data:

        if not validate_deposit(
            data.get("price"),
            data.get("deposit")
        ):

            errors.append(
                "Deposit cannot exceed price."
            )


    if data.get("delivery_date"):

        if not validate_delivery_date(
            data.get("delivery_date")
        ):

            errors.append(
                "Invalid delivery date."
            )


    if data.get("status"):

        if not validate_status(
            data.get("status")
        ):

            errors.append(
                "Invalid order status."
            )


    return errors
