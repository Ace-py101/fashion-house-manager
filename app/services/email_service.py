# ============================================================
# EMAIL SERVICE
#
# Provides SMTP email delivery for the application.
#
# SMTP credentials are never hard-coded here.
# They are loaded from Flask's application configuration,
# which itself obtains sensitive values from environment
# variables.
# ============================================================

import smtplib

from email.message import EmailMessage

from flask import current_app


def send_email(
    recipient,
    subject,
    body
):
    """
    Send an email using the application's SMTP configuration.

    Returns:
        True  -> email was successfully handed to the SMTP server.
        False -> email could not be sent.
    """

    # ========================================================
    # LOAD SMTP CONFIGURATION
    #
    # We use current_app.config instead of reading os.environ
    # directly. This keeps the email service synchronized with
    # the application's actual configuration.
    # ========================================================

    smtp_host = current_app.config.get(
        "MAIL_SERVER"
    )

    smtp_port = current_app.config.get(
        "MAIL_PORT",
        587
    )

    smtp_use_tls = current_app.config.get(
        "MAIL_USE_TLS",
        True
    )

    smtp_username = current_app.config.get(
        "MAIL_USERNAME"
    )

    smtp_password = current_app.config.get(
        "MAIL_PASSWORD"
    )

    sender = current_app.config.get(
        "MAIL_DEFAULT_SENDER"
    )

    # ========================================================
    # VALIDATE SMTP CONFIGURATION
    #
    # If SMTP is not configured, do not attempt a connection.
    # This prevents confusing connection errors when the
    # application is intentionally running without email.
    # ========================================================

    if not all(
        [
            smtp_host,
            smtp_username,
            smtp_password,
            sender
        ]
    ):
        return False

    # ========================================================
    # BUILD EMAIL MESSAGE
    # ========================================================

    message = EmailMessage()

    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient

    message.set_content(
        body
    )

    # ========================================================
    # CONNECT TO SMTP SERVER
    # ========================================================

    try:

        smtp_port = int(
            smtp_port
        )

        with smtplib.SMTP(
            smtp_host,
            smtp_port,
            timeout=15
        ) as server:

            # ==================================================
            # START TLS WHEN ENABLED
            #
            # Gmail SMTP on port 587 expects STARTTLS.
            # ==================================================

            if smtp_use_tls:

                server.starttls()

            # ==================================================
            # AUTHENTICATE WITH SMTP SERVER
            # ==================================================

            server.login(
                smtp_username,
                smtp_password
            )

            # ==================================================
            # SEND MESSAGE
            # ==================================================

            server.send_message(
                message
            )

        return True

    except Exception:

        # =====================================================
        # SECURITY NOTE
        #
        # SMTP credentials and authentication details are never
        # included in the returned error or printed to output.
        #
        # Stage 2 will later introduce more structured security
        # logging/error handling.
        # =====================================================

        return False
