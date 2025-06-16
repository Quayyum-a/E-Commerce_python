from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_restx import Api
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": ["http://127.0.0.1:5500", "http://localhost:5500"],
                 "supports_credentials": True,
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"]
             }
         })
    
    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)

    # Initialize Flask-RESTX Api
    api = Api(app, version='1.0', title='E-Commerce API',
              description='API documentation for the E-Commerce platform',
              doc='/docs')

    from app.presentation import auth_controller, product_controller, order_controller, cart_controller
    # Register blueprints as before (for backward compatibility)
    app.register_blueprint(auth_controller.bp)
    app.register_blueprint(product_controller.bp)
    app.register_blueprint(order_controller.bp)
    app.register_blueprint(cart_controller.bp)

    # Register RESTX namespaces if available (to be added in controllers)
    if hasattr(auth_controller, 'api'):
        api.add_namespace(auth_controller.api)
    if hasattr(product_controller, 'api'):
        api.add_namespace(product_controller.api)
    if hasattr(order_controller, 'api'):
        api.add_namespace(order_controller.api)
    if hasattr(cart_controller, 'api'):
        api.add_namespace(cart_controller.api)

    return app
