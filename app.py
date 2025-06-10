from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.presentation.auth_controller import bp as auth_bp
from app.presentation.product_controller import bp as product_bp
from app.presentation.order_controller import bp as order_bp
from app.infrastructure.database import init_db

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a strong secret in production
jwt = JWTManager(app)
CORS(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(product_bp)
app.register_blueprint(order_bp)

@app.before_first_request
def initialize_database():
    init_db()

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)
