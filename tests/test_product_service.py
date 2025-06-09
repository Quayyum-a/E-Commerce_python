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
    with app.app_context():
        admin_id = app.config.get('TEST_ADMIN_ID', 1)

        headers = get_auth_headers(app, user_id=admin_id, role='admin')

        product_data = {
            'name': 'Test Product',
            'price': 19.99,
            'stock': 100
        }

        # Make authenticated request
        try:
            response = client.post(
                '/api/products',
                json=product_data,
                headers=headers,
                content_type='application/json'
            )


            response_data = response.get_json()
            assert response_data['message'] == 'Product created'

        except Exception as e:
            print("\n=== Test Failed ===")
            print(f"Error: {str(e)}")
            if 'response' in locals():
                print(f"Response status: {response.status_code}")
                print(f"Response data: {response.data}")
            raise