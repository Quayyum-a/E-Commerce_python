import pytest
from app import create_app, db
from app.domain.product import Product
from app.domain.user import User
from flask_jwt_extended import create_access_token, JWTManager
import os

# Test admin user data
TEST_ADMIN = {
    'username': 'testadmin',
    'email': 'admin@test.com',
    'password': 'Test@1234',
    'role': 'admin'
}

@pytest.fixture(scope='function')
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret-key',
        'JWT_ACCESS_TOKEN_EXPIRES': False  # Tokens won't expire during testing
    })
    
    # Initialize JWT with the test app
    jwt = JWTManager()
    jwt.init_app(app)
    
    with app.app_context():
        # Drop all tables first to ensure a clean state
        db.drop_all()
        # Create all tables
        db.create_all()
        
        # Create test admin user
        admin = User(
            username=TEST_ADMIN['username'],
            email=TEST_ADMIN['email'],
            role=TEST_ADMIN['role']
        )
        admin.set_password(TEST_ADMIN['password'])
        db.session.add(admin)
        db.session.commit()
        
        # Store the admin user ID for use in tests
        app.config['TEST_ADMIN_ID'] = admin.id
        
        yield app
        
        # Clean up after test
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def get_auth_headers(app, user_id=None, role='admin'):
    """Helper function to get authentication headers"""
    with app.app_context():
        if user_id is None:
            user_id = app.config.get('TEST_ADMIN_ID', 1)
            
        # Create the identity as a dictionary with 'id' and 'role' keys
        identity = {
            'id': user_id,
            'role': role
        }
        
        # Create access token with the identity
        access_token = create_access_token(identity=identity)
        
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

def test_create_product(client, app):
    # First, get authentication headers
    with app.app_context():
        headers = get_auth_headers(app)
        
        # Test data
        product_data = {
            'name': 'Test Product',
            'price': 19.99,
            'stock': 100
        }
        
        # Print debug info
        print("Sending request with headers:", headers)
        print("Request data:", product_data)
        
        # Make authenticated request
        response = client.post(
            '/api/products',
            json=product_data,
            headers=headers,
            content_type='application/json'  # Explicitly set content type
        )
        
        # Debug output
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        # Check for any JWT errors first
        if response.status_code == 422:
            print("JWT Validation Error:", response.json)
        
        # Assertions
        assert response.status_code == 201, \
            f"Expected status code 201, got {response.status_code}. Response: {response.data}"
            
        response_data = response.get_json()
        assert 'message' in response_data, "Response missing 'message' field"
        assert response_data['message'] == 'Product created', \
            f"Unexpected message: {response_data.get('message')}"
        assert 'product_id' in response_data, "Response missing 'product_id' field"
        
        # Verify the product was actually created in the database
        product = Product.query.first()
        assert product is not None, "No product was created in the database"
        assert product.name == product_data['name'], \
            f"Expected product name '{product_data['name']}', got '{product.name}'"
        assert float(product.price) == product_data['price'], \
            f"Expected price {product_data['price']}, got {product.price}"
        assert product.stock == product_data['stock'], \
            f"Expected stock {product_data['stock']}, got {product.stock}"