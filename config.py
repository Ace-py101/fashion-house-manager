import os


class Config:
    """
    Base application configuration.
    """

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "development-secret-key"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://localhost/fashion_house"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
