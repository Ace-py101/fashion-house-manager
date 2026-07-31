import re


def validate_customer(data):
    """
    Validate customer input before it reaches the service layer.
    """

    errors = []

    full_name = data.get("full_name", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()
    address = data.get("address", "").strip()
    gender = data.get("gender", "").strip()
    notes = data.get("notes", "").strip()

    # Full Name
    if not full_name:
        errors.append("Customer name is required.")

    elif len(full_name) < 3:
        errors.append(
            "Customer name must be at least 3 characters."
        )

    elif not re.fullmatch(
        r"[A-Za-z .'-]+",
        full_name
    ):
        errors.append(
            "Customer name contains invalid characters."
        )

    # Phone
    if not phone:
        errors.append(
            "Phone number is required."
        )

    elif not phone.isdigit():
        errors.append(
            "Phone number must contain only digits."
        )

    elif len(phone) < 11:
        errors.append(
            "Phone number must contain at least 11 digits."
        )

    # Email
    if email:

        pattern = (
            r"^[A-Za-z0-9._%+-]+"
            r"@[A-Za-z0-9.-]+"
            r"\.[A-Za-z]{2,}$"
        )

        if not re.fullmatch(pattern, email):
            errors.append(
                "Invalid email address."
            )

    # Address
    if address and len(address) > 255:
        errors.append(
            "Address is too long."
        )

    # Gender
    if gender not in (
        "Male",
        "Female"
    ):
        errors.append(
            "Please select a valid gender."
        )

    # Notes
    if len(notes) > 1000:
        errors.append(
            "Notes are too long."
        )

    return errors
