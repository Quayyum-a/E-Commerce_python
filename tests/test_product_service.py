import pytest
from app import create_app, db
from app.domain.product import Product
from app.domain.user import User
from flask_jwt_extended import create_access_token, JWTManager


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
        'JWT_ACCESS_TOKEN_EXPIRES': False
    })
    
    jwt = JWTManager(app)
    
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return str(user['id'])
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data['sub']
        return {'id': identity, 'role': jwt_data.get('role', 'user')}
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
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
        
        # Create user identity as a dictionary with id and role
        user_identity = {'id': str(user_id), 'role': role}
        
        # Create access token with additional claims
        access_token = create_access_token(
            identity=user_identity,
            additional_claims={'role': role}
        )
        
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

def test_create_product(client, app):
    # First, get authentication headers
    with app.app_context():
        # Get admin user ID
        admin_id = app.config.get('TEST_ADMIN_ID', 1)
        
        # Get auth headers with role
        headers = get_auth_headers(app, user_id=admin_id, role='admin')
        
        # Test data
        product_data = {
            'name': 'Test Product',
            'price': 19.99,
            'stock': 100
        }
        
        # Print debug info
        print("\n=== Test Debug Info ===")
        print(f"Admin ID: {admin_id}")
        print("Request Headers:", headers)
        print("Request Data:", product_data)
        
        # Make authenticated request
        try:
            response = client.post(
                '/api/products',
                json=product_data,
                headers=headers,
                content_type='application/json'
            )
            
            # Debug output
            print("\n=== Response ===")
            print(f"Status Code: {response.status_code}")
            print("Response Data:", response.get_json())
            
            # Check for JWT errors
            if response.status_code == 422:
                print("\nJWT Validation Error:", response.get_json())
            
            # Verify response
            assert response.status_code == 201, \
                f"Expected status code 201, got {response.status_code}"
                
            response_data = response.get_json()
            assert 'message' in response_data, "Missing 'message' in response"
            assert response_data['message'] == 'Product created', \
                f"Unexpected message: {response_data.get('message')}"
            assert 'product_id' in response_data, "Missing 'product_id' in response"
            
            # Verify database
            product = Product.query.first()
            assert product is not None, "No product was created in the database"
            assert product.name == product_data['name'], \
                f"Expected name '{product_data['name']}', got '{product.name}'"
            assert float(product.price) == product_data['price'], \
                f"Expected price {product_data['price']}, got {product.price}"
            assert product.stock == product_data['stock'], \
                f"Expected stock {product_data['stock']}, got {product.stock}"
                
        except Exception as e:
            print("\n=== Test Failed ===")
            print(f"Error: {str(e)}")
            if 'response' in locals():
                print(f"Response status: {response.status_code}")
                print(f"Response data: {response.data}")
            raise