def validate_customer(data):
    errors = []

    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()

    if not name:
        errors.append("Customer name is required")

    if len(name) < 3:
        errors.append("Customer name must be at least 3 characters")

    if not phone:
        errors.append("Phone number is required")

    if phone and not phone.isdigit():
        errors.append("Phone number must contain only numbers")

    return errors
