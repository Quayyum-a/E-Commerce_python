from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure CORS
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
    
    from app.presentation import auth_controller, product_controller, order_controller
    app.register_blueprint(auth_controller.bp, url_prefix='/api')
    app.register_blueprint(product_controller.bp, url_prefix='/api')
    app.register_blueprint(order_controller.bp, url_prefix='/api')
    
    return app
