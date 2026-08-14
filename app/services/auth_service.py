import hashlib
import re
import secrets
from datetime import datetime, timedelta

from flask import current_app

from app.database import db
from app.models.user import User
from app.services.email_service import send_email


VALID_ACCOUNT_TYPES = [
    "client",
    "admin"
]


EMAIL_VERIFICATION_TOKEN_EXPIRATION_MINUTES = 30

PASSWORD_RESET_TOKEN_EXPIRATION_MINUTES = 30


def normalize_email(email):

    if not email:
        return ""

    return email.strip().lower()


def validate_password(password):

    if not password:
        raise ValueError(
            "Password is required."
        )

    if len(password) < 8:
        raise ValueError(
            "Password must be at least 8 characters."
        )

    if len(password) > 12:
        raise ValueError(
            "Password must not exceed 12 characters."
        )

    if not re.search(
        r"[A-Za-z]",
        password
    ):
        raise ValueError(
            "Password must contain at least one letter."
        )

    if not re.search(
        r"\d",
        password
    ):
        raise ValueError(
            "Password must contain at least one number."
        )

    if not re.search(
        r"[^A-Za-z0-9]",
        password
    ):
        raise ValueError(
            "Password must contain at least one symbol."
        )


def hash_verification_token(token):

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def generate_email_verification_token():

    return secrets.token_urlsafe(32)


def validate_registration_data(
    email,
    password,
    confirm_password,
    account_type
):

    email = normalize_email(
        email
    )

    if not email:
        raise ValueError(
            "Email address is required."
        )

    if "@" not in email:
        raise ValueError(
            "Please enter a valid email address."
        )

    validate_password(
        password
    )

    if password != confirm_password:
        raise ValueError(
            "Passwords do not match."
        )

    if account_type not in VALID_ACCOUNT_TYPES:
        raise ValueError(
            "Invalid account type."
        )

    existing_user = (
        User.query
        .filter_by(email=email)
        .first()
    )

    if existing_user:
        raise ValueError(
            "An account with that email already exists."
        )

    return email


def create_email_verification_token(
    user
):

    token = (
        generate_email_verification_token()
    )

    user.email_verification_token_hash = (
        hash_verification_token(
            token
        )
    )

    user.email_verification_token_expires_at = (
        datetime.utcnow()
        + timedelta(
            minutes=(
                EMAIL_VERIFICATION_TOKEN_EXPIRATION_MINUTES
            )
        )
    )

    db.session.commit()

    return token


def build_email_verification_url(
    token
):

    return (
        current_app.config.get(
            "APP_BASE_URL",
            "http://127.0.0.1:5000"
        ).rstrip("/")
        + "/verify-email/"
        + token
    )


def send_verification_email(
    user,
    token
):

    verification_url = (
        build_email_verification_url(
            token
        )
    )

    body = (
        "Welcome to Fashion House Manager.\n\n"
        "Please verify your email address by "
        "opening the link below:\n\n"
        f"{verification_url}\n\n"
        "This verification link expires in "
        f"{EMAIL_VERIFICATION_TOKEN_EXPIRATION_MINUTES} minutes.\n\n"
        "If you did not create this account, "
        "you can ignore this message."
    )

    return send_email(
        recipient=user.email,
        subject="Verify your Fashion House Manager account",
        body=body
    )


def register_user(
    email,
    password,
    confirm_password,
    account_type,
    phone_number
):

    email = validate_registration_data(
        email,
        password,
        confirm_password,
        account_type
    )

    phone_number = validate_phone_number(
        phone_number
    )

    existing_phone = (
        User.query
        .filter_by(
            phone_number=phone_number
        )
        .first()
    )

    if existing_phone:

        raise ValueError(
            "An account with that phone number already exists."
        )

    user = User(
        email=email,
        phone_number=phone_number,
        account_type=account_type,
        email_verified=False,
        phone_verified=False
    )

    user.set_password(
        password
    )

    db.session.add(
        user
    )

    db.session.flush()

    token = (
        create_email_verification_token(
            user
        )
    )

    email_sent = (
        send_verification_email(
            user,
            token
        )
    )

    return user, email_sent


def authenticate_user(
    email,
    password
):

    email = normalize_email(
        email
    )

    if not email:
        raise ValueError(
            "Email address is required."
        )

    if not password:
        raise ValueError(
            "Password is required."
        )

    user = (
        User.query
        .filter_by(email=email)
        .first()
    )

    if not user:
        raise ValueError(
            "Invalid email address or password."
        )

    if not user.check_password(
        password
    ):
        raise ValueError(
            "Invalid email address or password."
        )

    if not user.email_verified:

        raise ValueError(
            "Please verify your email address before logging in."
        )

    return user


def verify_email_token(
    token
):

    if not token:
        return False, "Invalid verification link."

    token_hash = (
        hash_verification_token(
            token
        )
    )

    user = (
        User.query
        .filter_by(
            email_verification_token_hash=token_hash
        )
        .first()
    )

    if not user:
        return False, "Invalid or expired verification link."

    if user.email_verified:

        user.email_verification_token_hash = None
        user.email_verification_token_expires_at = None

        db.session.commit()

        return True, "Your email address is already verified."

    if not user.email_verification_token_expires_at:

        return False, "Invalid or expired verification link."

    if (
        datetime.utcnow()
        > user.email_verification_token_expires_at
    ):

        user.email_verification_token_hash = None
        user.email_verification_token_expires_at = None

        db.session.commit()

        return False, "Invalid or expired verification link."

    user.email_verified = True
    user.email_verified_at = datetime.utcnow()

    user.email_verification_token_hash = None
    user.email_verification_token_expires_at = None

    db.session.commit()

    return True, "Email address verified successfully."



def resend_email_verification(email):
    """
    Generate and send a new email verification token.

    Returns a generic result so the caller does not reveal
    whether an email address belongs to an existing account.
    """

    email = normalize_email(email)

    if not email:
        return False

    user = (
        User.query
        .filter_by(email=email)
        .first()
    )

    if not user:
        return False

    if user.email_verified:
        return False

    token = create_email_verification_token(
        user
    )

    return send_verification_email(
        user,
        token
    )


def resend_verification_email(email):
    """
    Generate a fresh verification token and send it to an
    existing unverified account.

    Returns:
        tuple: (success, message)
    """

    email = normalize_email(
        email
    )

    if not email:
        return (
            False,
            "Please enter your email address."
        )

    user = (
        User.query
        .filter_by(
            email=email
        )
        .first()
    )

    if not user:
        return (
            False,
            "If an account exists for that email, "
            "a verification email has been sent."
        )

    if user.email_verified:
        return (
            False,
            "This email address is already verified."
        )

    token = create_email_verification_token(
        user
    )

    email_sent = send_verification_email(
        user,
        token
    )

    if not email_sent:
        return (
            False,
            "Unable to send the verification email. "
            "Please try again later."
        )

    return (
        True,
        "A new verification email has been sent. "
        "Please check your inbox."
    )

# ============================================================
# PASSWORD RESET
#
# Password-reset tokens are generated randomly and only their
# SHA-256 hashes are stored in the database.
#
# The raw token exists only inside the reset URL sent to the
# user's email address.
# ============================================================


def generate_password_reset_token():
    """
    Generate a cryptographically secure password-reset token.
    """

    return secrets.token_urlsafe(32)


def create_password_reset_token(user):
    """
    Generate and store a password-reset token for a user.

    Only the token hash is stored in the database.
    """

    token = generate_password_reset_token()

    user.password_reset_token_hash = (
        hash_verification_token(
            token
        )
    )

    user.password_reset_token_expires_at = (
        datetime.utcnow()
        + timedelta(
            minutes=(
                PASSWORD_RESET_TOKEN_EXPIRATION_MINUTES
            )
        )
    )

    db.session.commit()

    return token


def build_password_reset_url(token):
    """
    Build the public password-reset URL.
    """

    return (
        current_app.config.get(
            "APP_BASE_URL",
            "http://127.0.0.1:5000"
        ).rstrip("/")
        + "/reset-password/"
        + token
    )


def send_password_reset_email(user, token):
    """
    Send a password-reset email to the user.
    """

    reset_url = build_password_reset_url(
        token
    )

    body = (
        "Fashion House Manager\n\n"
        "We received a request to reset the password "
        "for your account.\n\n"
        "Open the link below to create a new password:\n\n"
        f"{reset_url}\n\n"
        "This password-reset link expires in "
        f"{PASSWORD_RESET_TOKEN_EXPIRATION_MINUTES} minutes.\n\n"
        "If you did not request a password reset, "
        "you can safely ignore this message."
    )

    return send_email(
        recipient=user.email,
        subject="Reset your Fashion House Manager password",
        body=body
    )


def request_password_reset(email):
    """
    Request a password reset.

    A generic response is returned whether or not the email
    belongs to an account. This prevents account enumeration.
    """

    email = normalize_email(
        email
    )

    generic_message = (
        "If an account exists for that email address, "
        "a password reset link has been sent."
    )

    if not email:
        return (
            False,
            "Please enter your email address."
        )

    user = (
        User.query
        .filter_by(
            email=email
        )
        .first()
    )

    if not user:
        return (
            True,
            generic_message
        )

    token = create_password_reset_token(
        user
    )

    email_sent = send_password_reset_email(
        user,
        token
    )

    if not email_sent:

        return (
            False,
            "Unable to send the password reset email. "
            "Please try again later."
        )

    return (
        True,
        generic_message
    )


def reset_password(
    token,
    password,
    confirm_password
):
    """
    Validate a password-reset token and replace the user's
    password.

    A successful reset immediately invalidates the token.
    """

    if not token:

        return (
            False,
            "Invalid or expired password reset link."
        )

    token_hash = hash_verification_token(
        token
    )

    user = (
        User.query
        .filter_by(
            password_reset_token_hash=token_hash
        )
        .first()
    )

    if not user:

        return (
            False,
            "Invalid or expired password reset link."
        )

    if not user.password_reset_token_expires_at:

        return (
            False,
            "Invalid or expired password reset link."
        )

    if (
        datetime.utcnow()
        > user.password_reset_token_expires_at
    ):

        user.password_reset_token_hash = None
        user.password_reset_token_expires_at = None

        db.session.commit()

        return (
            False,
            "Invalid or expired password reset link."
        )

    validate_password(
        password
    )

    if password != confirm_password:

        return (
            False,
            "Passwords do not match."
        )

    user.set_password(
        password
    )

    # --------------------------------------------------------
    # Invalidate the token immediately after successful use.
    # This makes the reset link one-time-use.
    # --------------------------------------------------------

    user.password_reset_token_hash = None
    user.password_reset_token_expires_at = None

    user.updated_at = datetime.utcnow()

    db.session.commit()

    return (
        True,
        "Your password has been reset successfully."
    )


# ============================================================
# PHONE VERIFICATION FOUNDATION
#
# This layer owns the security-sensitive OTP lifecycle.
#
# The SMS provider does NOT generate or validate the OTP.
# It only receives the already-generated message.
#
# This separation allows the application to change SMS
# providers later without changing authentication logic.
# ============================================================

PHONE_VERIFICATION_CODE_EXPIRATION_MINUTES = 10


def normalize_phone_number(phone_number):
    """
    Normalize a phone number before validation/storage.

    We remove common formatting characters while preserving
    the international '+' prefix.

    Example:

        +234 801-234-5678
                ↓
        +2348012345678
    """

    if not phone_number:
        return ""

    phone_number = phone_number.strip()

    phone_number = re.sub(
        r"[\s\-\(\)\.]",
        "",
        phone_number
    )

    return phone_number


def validate_phone_number(phone_number):
    """
    Validate an international phone number.

    The application deliberately requires an international
    country code. This prevents ambiguity when the eventual
    SMS provider receives the destination number.

    Accepted example:

        +2348012345678

    Rejected example:

        08012345678
    """

    phone_number = normalize_phone_number(
        phone_number
    )

    if not phone_number:

        raise ValueError(
            "Phone number is required."
        )

    if not re.fullmatch(
        r"\+[1-9]\d{7,14}",
        phone_number
    ):

        raise ValueError(
            "Please enter a valid international phone number "
            "including the country code."
        )

    return phone_number


def generate_phone_verification_code():
    """
    Generate a cryptographically secure six-digit OTP.

    secrets.randbelow() is used instead of random.randint()
    because this value participates in authentication.
    """

    return (
        f"{secrets.randbelow(1000000):06d}"
    )


def create_phone_verification_code(user):
    """
    Generate a new phone verification OTP and persist only
    its hash and expiration timestamp.

    The raw OTP is returned to the caller so the SMS delivery
    layer can send it to the user's phone.

    The raw OTP is NEVER written to the database.
    """

    if not user:

        raise ValueError(
            "User account is required."
        )

    if not user.phone_number:

        raise ValueError(
            "A phone number is required before verification."
        )

    if user.phone_verified:

        raise ValueError(
            "This phone number is already verified."
        )

    code = (
        generate_phone_verification_code()
    )

    user.phone_verification_code_hash = (
        hash_verification_token(
            code
        )
    )

    user.phone_verification_code_expires_at = (
        datetime.utcnow()
        + timedelta(
            minutes=(
                PHONE_VERIFICATION_CODE_EXPIRATION_MINUTES
            )
        )
    )

    db.session.commit()

    return code


def verify_phone_code(
    user,
    code
):
    """
    Verify a submitted six-digit phone OTP.

    Successful verification:

        phone_verified = True
        phone_verified_at = current timestamp
        stored OTP hash = None
        stored OTP expiration = None

    Failed verification does not expose the stored hash.
    """

    if not user:

        return (
            False,
            "Unable to verify phone number."
        )

    if user.phone_verified:

        return (
            True,
            "Phone number is already verified."
        )

    if not code:

        return (
            False,
            "Please enter the verification code."
        )

    code = code.strip()

    if not re.fullmatch(
        r"\d{6}",
        code
    ):

        return (
            False,
            "Verification code must contain 6 digits."
        )

    if not user.phone_verification_code_hash:

        return (
            False,
            "No active phone verification code exists."
        )

    if not user.phone_verification_code_expires_at:

        return (
            False,
            "The verification code is invalid or expired."
        )

    if (
        datetime.utcnow()
        > user.phone_verification_code_expires_at
    ):

        # ====================================================
        # Expired credentials are invalidated immediately.
        # ====================================================

        user.phone_verification_code_hash = None

        user.phone_verification_code_expires_at = None

        db.session.commit()

        return (
            False,
            "The verification code has expired."
        )

    supplied_hash = (
        hash_verification_token(
            code
        )
    )

    if supplied_hash != user.phone_verification_code_hash:

        return (
            False,
            "Invalid verification code."
        )

    # ========================================================
    # SUCCESSFUL VERIFICATION
    #
    # The OTP becomes unusable immediately after successful
    # verification.
    # ========================================================

    user.phone_verified = True

    user.phone_verified_at = (
        datetime.utcnow()
    )

    user.phone_verification_code_hash = None

    user.phone_verification_code_expires_at = None

    db.session.commit()

    return (
        True,
        "Phone number verified successfully."
    )


def resend_phone_verification_code(user):
    """
    Generate a fresh OTP for an existing unverified account.

    This function does not send the SMS itself. It returns the
    generated code to the SMS delivery layer.
    """

    if not user:

        return (
            False,
            "Unable to process phone verification."
        )

    if user.phone_verified:

        return (
            False,
            "This phone number is already verified."
        )

    if not user.phone_number:

        return (
            False,
            "No phone number is associated with this account."
        )

    code = create_phone_verification_code(
        user
    )

    return (
        True,
        code
    )


# ============================================================
# PHONE VERIFICATION SMS DELIVERY
# ============================================================

def send_phone_verification_code(
    user
):
    """
    Generate and send a phone verification OTP.

    The raw OTP exists only long enough to construct the SMS.
    It is never returned to the HTTP layer and is never stored
    in plaintext.

    Returns:
        tuple:
            (True, success_message)
            (False, failure_message)
    """

    from app.services.sms_service import (
        send_phone_verification_sms
    )

    if not user:

        return (
            False,
            "Unable to process phone verification."
        )

    if user.phone_verified:

        return (
            False,
            "This phone number is already verified."
        )

    if not user.phone_number:

        return (
            False,
            "Please add a phone number before verification."
        )

    try:

        code = create_phone_verification_code(
            user
        )

        sent = send_phone_verification_sms(
            user.phone_number,
            code
        )

        if not sent:

            user.phone_verification_code_hash = None
            user.phone_verification_code_expires_at = None

            db.session.commit()

            return (
                False,
                "Unable to send the verification code. "
                "SMS delivery is not configured or is temporarily unavailable."
            )

        return (
            True,
            "A verification code has been sent to your phone."
        )

    except Exception:

        db.session.rollback()

        return (
            False,
            "Unable to send the verification code. "
            "Please try again later."
        )
