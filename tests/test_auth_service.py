import pytest
import json
from app import create_app, db
from app.domain.user import User
from flask_jwt_extended import decode_token, create_access_token
from datetime import timedelta

@pytest.fixture(scope='function')
def app():
    # Create app with test configuration
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
        # Then create all tables
        db.create_all()
        # Clear any existing data
        db.session.query(User).delete()
        db.session.commit()
        
        yield app
        
        # Clean up after test
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# Test Data
TEST_USER = {
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'Test@1234',
    'role': 'customer'
}

def test_register_user_success(client):
    response = client.post('/api/auth/register', 
                         json=TEST_USER,
                         content_type='application/json')
    assert response.status_code == 201
    assert response.json['message'] == 'User registered'
    assert 'user_id' in response.json

    with client.application.app_context():
        user = User.query.filter_by(email=TEST_USER['email']).first()
        assert user is not None
        assert user.username == TEST_USER['username']
        assert user.role == TEST_USER['role']
        assert user.check_password(TEST_USER['password'])

def test_register_duplicate_email(client):
    client.post('/api/auth/register', json=TEST_USER)

    response = client.post('/api/auth/register', 
                         json={
                             'username': 'anotheruser',
                             'email': TEST_USER['email'],
                             'password': 'Another@1234',
                             'role': 'customer'
                         })
    assert response.status_code == 400
    assert 'email already exists' in response.json['error'].lower()

def test_register_invalid_email_format(client):

    response = client.post('/api/auth/register',
                         json={
                             'username': 'invaliduser',
                             'email': 'invalid-email',
                             'password': 'Invalid@1234',
                             'role': 'customer'
                         })
    assert response.status_code == 400
    assert 'invalid email format' in response.json['error'].lower()


def test_login_success(client):
    client.post('/api/auth/register', json=TEST_USER)

    response = client.post('/api/auth/login',
                         json={
                             'email': TEST_USER['email'],
                             'password': TEST_USER['password']
                         })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_login_invalid_credentials(client):
    client.post('/api/auth/register', json=TEST_USER)

    response = client.post('/api/auth/login',
                         json={
                             'email': TEST_USER['email'],
                             'password': 'wrongpassword'
                         })
    assert response.status_code == 401

    response = client.post('/api/auth/login',
                         json={
                             'email': 'nonexistent@example.com',
                             'password': 'doesntmatter'
                         })
    assert response.status_code == 401

def test_login_missing_credentials(client):
    """Test login with missing credentials"""
    # Missing email
    response = client.post('/api/auth/login',
                         json={'password': 'Test@1234'})
    assert response.status_code == 400

    # Missing password
    response = client.post('/api/auth/login',
                         json={'email': 'test@example.com'})
    assert response.status_code == 400

def test_token_validation(client):
    """Test JWT token validation"""
    # Get token
    client.post('/api/auth/register', json=TEST_USER)
    login_response = client.post('/api/auth/login',
                               json={
                                   'email': TEST_USER['email'],
                                   'password': TEST_USER['password']
                               })
    token = login_response.json['access_token']

    # Test protected endpoint with valid token
    response = client.get('/api/orders',
                        headers={'Authorization': f'Bearer {token}'})
    assert response.status_code != 401  # Should not be unauthorized

    # Test with invalid token
    response = client.get('/api/orders',
                        headers={'Authorization': 'Bearer invalidtoken'})
    assert response.status_code == 422  # Unprocessable Entity

def test_user_roles(client):
    """Test different user roles"""
    # Register admin user
    admin_user = {
        'username': 'adminuser',
        'email': 'admin@example.com',
        'password': 'Admin@1234',
        'role': 'admin'
    }
    client.post('/api/auth/register', json=admin_user)

    # Login as admin
    login_response = client.post('/api/auth/login',
                               json={
                                   'email': admin_user['email'],
                                   'password': admin_user['password']
                               })
    admin_token = login_response.json['access_token']

    # Test admin access
    response = client.post('/api/products',
                         headers={'Authorization': f'Bearer {admin_token}'},
                         json={
                             'name': 'Test Product',
                             'price': 9.99,
                             'stock': 100
                         })
    assert response.status_code == 201  # Admin should have access

    # Login as regular customer
    login_response = client.post('/api/auth/login',
                               json={
                                   'email': TEST_USER['email'],
                                   'password': TEST_USER['password']
                               })
    customer_token = login_response.json['access_token']

    # Test customer access to admin endpoint
    response = client.post('/api/products',
                         headers={'Authorization': f'Bearer {customer_token}'},
                         json={
                             'name': 'Test Product 2',
                             'price': 19.99,
                             'stock': 50
                         })
    assert response.status_code == 403  # Forbidden for customers