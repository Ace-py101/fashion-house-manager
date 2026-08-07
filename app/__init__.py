from flask import Flask
from flask_migrate import Migrate

from config import Config

from app.database import db


migrate = Migrate()


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from datetime import datetime
    
    
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

    from app.routes.main import main_bp
    from app.routes.customer_routes import customer_bp
    from app.routes.order_routes import order_bp
    from app.routes.measurement_routes import measurement_bp
    from app.routes.inventory_routes import inventory_bp
    from app.routes.payment_routes import payment_bp
    from app.routes.report_routes import report_bp
    from app.routes.style_routes import style_bp
    from app.routes.settings_routes import settings_bp
    
    
    app.register_blueprint(main_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(measurement_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(style_bp)
    app.register_blueprint(settings_bp)
    
    from app import models

    return app
