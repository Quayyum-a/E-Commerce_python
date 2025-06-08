from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)
    from app.presentation import auth_controller, product_controller, order_controller
    app.register_blueprint(auth_controller.bp)
    app.register_blueprint(product_controller.bp)
    app.register_blueprint(order_controller.bp)
    return app