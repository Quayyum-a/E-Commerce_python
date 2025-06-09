import pytest
from app import create_app, db
from app.domain.product import Product
from app.domain.user import User

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
        'JWT_SECRET_KEY': 'test-secret-key'
    })
    
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
        
        yield app
        
        # Clean up after test
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def get_auth_headers(client):
    """Helper function to get authentication headers"""
    # Login to get token
    login_response = client.post('/api/auth/login', json={
        'email': TEST_ADMIN['email'],
        'password': TEST_ADMIN['password']
    })
    token = login_response.json['access_token']
    return {'Authorization': f'Bearer {token}'}

def test_create_product(client):

    headers = get_auth_headers(client)
    
    # Test data
    product_data = {
        'name': 'Test Product',
        'price': 19.99,
        'stock': 100
    }
    
    # Make authenticated request
    response = client.post('/api/products', 
                         json=product_data,
                         headers=headers)
    
    # Assertions
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}. Response: {response.data}"
    assert 'message' in response.json
    assert response.json['message'] == 'Product created'
    assert 'product_id' in response.json
    
    # Verify the product was actually created in the database
    with client.application.app_context():
        product = Product.query.first()
        assert product is not None
        assert product.name == product_data['name']
        assert float(product.price) == product_data['price']
        assert product.stock == product_data['stock']