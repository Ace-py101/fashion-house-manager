import os

from dotenv import load_dotenv


# ============================================================
# LOAD PERSISTENT LOCAL ENVIRONMENT CONFIGURATION
#
# The .env file stores local secrets and configuration values.
# It is loaded before the Config class reads any environment
# variables so Flask receives the correct values at startup.
#
# The .env file must NOT be committed to Git.
# ============================================================

load_dotenv()


class Config:
    """
    Base application configuration.

    Security-sensitive values are loaded from environment
    variables so secrets are not stored directly in source code.
    """

    # ============================================================
    # APPLICATION SECRET
    #
    # Flask uses SECRET_KEY to cryptographically sign sessions.
    #
    # There is intentionally NO fallback value.
    # The application factory will refuse to start if the
    # secret is missing.
    # ============================================================

    SECRET_KEY = os.environ.get(
        "SECRET_KEY"
    )

    # ============================================================
    # DATABASE
    #
    # DATABASE_URL can be supplied through .env or the shell.
    # ============================================================

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://localhost/fashion_house"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ============================================================
    # EMAIL / SMTP
    #
    # These values are loaded from the persistent environment.
    # Gmail credentials must never be written directly into
    # Python source files.
    # ============================================================

    MAIL_SERVER = os.environ.get(
        "MAIL_SERVER"
    )

    MAIL_PORT = int(
        os.environ.get(
            "MAIL_PORT",
            "587"
        )
    )

    MAIL_USE_TLS = (
        os.environ.get(
            "MAIL_USE_TLS",
            "true"
        ).lower()
        == "true"
    )

    MAIL_USERNAME = os.environ.get(
        "MAIL_USERNAME"
    )

    MAIL_PASSWORD = os.environ.get(
        "MAIL_PASSWORD"
    )

    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER"
    )

    # ============================================================
    # APPLICATION BASE URL
    #
    # Used when generating email verification links.
    # ============================================================

    APP_BASE_URL = os.environ.get(
        "APP_BASE_URL",
        "http://127.0.0.1:5000"
    )
