import os

from datetime import datetime

from flask import Flask
from flask_migrate import Migrate

from config import Config

from app.database import db


migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    # ============================================================
    # SECURITY: REQUIRE A REAL SESSION SECRET
    #
    # Flask sessions depend on SECRET_KEY. The application must
    # refuse to start when the persistent secret is missing.
    #
    # The value now comes from .env through python-dotenv and
    # Config, so it remains available across application restarts.
    # ============================================================

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY environment variable is required."
        )

    # ======================================================
    # Upload Configuration
    # ======================================================

    UPLOAD_ROOT = os.path.join(
        app.root_path,
        "static",
        "uploads"
    )

    app.config["UPLOAD_ROOT"] = UPLOAD_ROOT

    app.config["UPLOAD_FOLDERS"] = {

        "styles": os.path.join(
            UPLOAD_ROOT,
            "styles"
        ),

        "customers": os.path.join(
            UPLOAD_ROOT,
            "customers"
        ),

        "inventory": os.path.join(
            UPLOAD_ROOT,
            "inventory"
        ),

        "payments": os.path.join(
            UPLOAD_ROOT,
            "payments"
        ),

        "staff": os.path.join(
            UPLOAD_ROOT,
            "staff"
        ),

        "reports": os.path.join(
            UPLOAD_ROOT,
            "reports"
        ),

        "temp": os.path.join(
            UPLOAD_ROOT,
            "temp"
        )

    }

    # Maximum upload size (25 MB)

    app.config["MAX_CONTENT_LENGTH"] = (
        25 * 1024 * 1024
    )

    # Allowed image extensions

    app.config["UPLOAD_EXTENSIONS"] = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    }

    # Create upload folders automatically

    for folder in app.config[
        "UPLOAD_FOLDERS"
    ].values():

        os.makedirs(
            folder,
            exist_ok=True
        )

    db.init_app(app)

    migrate.init_app(
        app,
        db
    )

    # ======================================================
    # Greeting
    # ======================================================

    @app.context_processor
    def inject_greeting():

        hour = datetime.now().hour

        if 5 <= hour < 12:

            greeting = "Good Morning"

        elif 12 <= hour < 17:

            greeting = "Good Afternoon"

        elif 17 <= hour < 22:

            greeting = "Good Evening"

        else:

            greeting = "Good Night"

        return {
            "greeting": greeting
        }

    # ======================================================
    # Existing Routes
    # ======================================================

    from app.routes.main import main_bp
    from app.routes.customer_routes import customer_bp
    from app.routes.order_routes import order_bp
    from app.routes.measurement_routes import measurement_bp
    from app.routes.inventory_routes import inventory_bp
    from app.routes.payment_routes import payment_bp
    from app.routes.report_routes import report_bp
    from app.routes.style_routes import style_bp
    from app.routes.settings_routes import settings_bp

    # ======================================================
    # Platform Routes
    # ======================================================

    from app.routes.auth_routes import auth_bp
    from app.routes.profile_routes import profile_bp
    from app.routes.marketplace_routes import marketplace_bp
    from app.routes.firm_activity_routes import firm_activity_bp
    from app.routes.analytics_routes import analytics_bp
    from app.routes.message_routes import message_bp
    from app.routes.client_routes import client_bp

    # ======================================================
    # Register Existing Blueprints
    # ======================================================

    app.register_blueprint(main_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(measurement_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(style_bp)
    app.register_blueprint(settings_bp)

    # ======================================================
    # Register Platform Blueprints
    # ======================================================

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(marketplace_bp)
    app.register_blueprint(firm_activity_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(client_bp)

    # ======================================================
    # Import Models
    # ======================================================

    from app import models

    return app
