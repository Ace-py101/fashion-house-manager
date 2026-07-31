import re



def validate_name(name):

    if not name:
        return False, "Name is required"


    if len(name) < 3:
        return False, "Name must contain at least 3 characters"


    if len(name) > 100:
        return False, "Name is too long"


    if not re.match(
        r"^[A-Za-zÀ-ÿ\s'-]+$",
        name
    ):
        return False, "Name contains invalid characters"


    return True, ""





def validate_phone(phone):

    if not phone:
        return False, "Phone number is required"


    pattern = r"^\+?[0-9]{10,15}$"


    if not re.match(pattern, phone):
        return False, "Invalid phone number format"


    return True, ""





def validate_email(email):

    if not email:
        return True, ""


    pattern = (
        r"^[a-zA-Z0-9._%+-]+@"
        r"[a-zA-Z0-9.-]+\."
        r"[a-zA-Z]{2,}$"
    )


    if not re.match(pattern, email):

        return False, "Invalid email address"


    return True, ""





def validate_gender(gender):

    allowed = [
        "Male",
        "Female",
        "Other"
    ]


    if gender not in allowed:

        return False, "Invalid gender selection"


    return True, ""
