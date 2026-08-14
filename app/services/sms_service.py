# ============================================================
# SMS SERVICE
#
# Central SMS delivery abstraction.
#
# Authentication and phone-verification logic must not depend
# directly on a particular SMS provider.
#
# Supported providers:
#   - twilio
#   - termii
#
# Credentials are loaded from Flask configuration first and
# environment variables second.
#
# No API credential is stored in source code.
# ============================================================

import base64
import json
import os
from urllib import request
from urllib.error import HTTPError, URLError

from flask import current_app


def _config(name, default=None):
    """
    Read a configuration value from Flask configuration.

    Environment variables are used as a deployment-safe fallback.
    """

    value = current_app.config.get(name)

    if value is not None:
        return value

    return os.getenv(
        name,
        default
    )


def sms_provider():
    """
    Return the configured SMS provider.

    Supported values:

        twilio
        termii

    Returns an empty string when SMS is not configured.
    """

    return (
        _config(
            "SMS_PROVIDER",
            ""
        )
        or ""
    ).strip().lower()


def sms_is_configured():
    """
    Return True when the selected SMS provider has the
    minimum required configuration.
    """

    provider = sms_provider()

    if provider == "twilio":

        return all(
            [
                _config("TWILIO_ACCOUNT_SID"),
                _config("TWILIO_AUTH_TOKEN"),
                _config("TWILIO_FROM_NUMBER")
            ]
        )

    if provider == "termii":

        return all(
            [
                _config("TERMII_API_KEY"),
                _config("TERMII_SENDER_ID"),
                _config("SMS_API_BASE_URL")
            ]
        )

    return False


def _send_twilio(
    recipient,
    message
):
    """
    Send an SMS through Twilio's Messages REST resource.

    Twilio uses HTTP Basic Authentication for this API.
    """

    account_sid = _config(
        "TWILIO_ACCOUNT_SID"
    )

    auth_token = _config(
        "TWILIO_AUTH_TOKEN"
    )

    from_number = _config(
        "TWILIO_FROM_NUMBER"
    )

    if not all(
        [
            account_sid,
            auth_token,
            from_number
        ]
    ):
        return False

    url = (
        "https://api.twilio.com/2010-04-01/Accounts/"
        f"{account_sid}/Messages.json"
    )

    credentials = (
        f"{account_sid}:{auth_token}"
    ).encode(
        "utf-8"
    )

    authorization = (
        "Basic "
        + base64.b64encode(
            credentials
        ).decode("ascii")
    )

    payload = (
        f"To={request.quote(recipient)}"
        f"&From={request.quote(from_number)}"
        f"&Body={request.quote(message)}"
    ).encode(
        "utf-8"
    )

    http_request = request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": authorization,
            "Content-Type": (
                "application/x-www-form-urlencoded"
            )
        }
    )

    try:

        with request.urlopen(
            http_request,
            timeout=15
        ) as response:

            return (
                200
                <= response.status
                < 300
            )

    except (
        HTTPError,
        URLError,
        TimeoutError
    ):

        return False


def _send_termii(
    recipient,
    message
):
    """
    Send an SMS through the configured Termii API base URL.

    SMS_API_BASE_URL must be supplied by deployment configuration
    because Termii currently uses account-specific API base URLs.
    """

    api_key = _config(
        "TERMII_API_KEY"
    )

    sender_id = _config(
        "TERMII_SENDER_ID"
    )

    base_url = (
        _config(
            "SMS_API_BASE_URL"
        )
        or ""
    ).rstrip("/")

    if not all(
        [
            api_key,
            sender_id,
            base_url
        ]
    ):
        return False

    url = (
        base_url
        + "/api/sms/send"
    )

    payload = json.dumps(
        {
            "api_key": api_key,
            "to": recipient,
            "from": sender_id,
            "sms": message,
            "type": "plain",
            "channel": "generic"
        }
    ).encode(
        "utf-8"
    )

    http_request = request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )

    try:

        with request.urlopen(
            http_request,
            timeout=15
        ) as response:

            return (
                200
                <= response.status
                < 300
            )

    except (
        HTTPError,
        URLError,
        TimeoutError
    ):

        return False


def send_sms(
    recipient,
    message
):
    """
    Deliver an SMS using the configured provider.

    Returns:

        True
            SMS accepted by the provider.

        False
            SMS could not be delivered or SMS is not configured.

    Provider credentials and response bodies are deliberately not
    exposed to callers.
    """

    if not recipient:
        return False

    if not message:
        return False

    provider = sms_provider()

    if provider == "twilio":

        return _send_twilio(
            recipient,
            message
        )

    if provider == "termii":

        return _send_termii(
            recipient,
            message
        )

    return False


def send_phone_verification_sms(
    phone_number,
    verification_code
):
    """
    Send the application's phone-verification OTP.

    The raw OTP exists only for the duration of this function and
    is never persisted by this service.
    """

    if not phone_number:
        return False

    if not verification_code:
        return False

    message = (
        "Your Fashion House Manager verification code is: "
        f"{verification_code}. "
        "This code expires soon. "
        "If you did not request it, ignore this message."
    )

    return send_sms(
        recipient=phone_number,
        message=message
    )
