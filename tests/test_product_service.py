import pytest
from flask_jwt_extended import create_access_token, JWTManager
from http import HTTPStatus

from app import create_app, db
from app.domain.user import User
from app.domain.product import Product

# Test data
TEST_ADMIN = {
    'username': 'testadmin',
    'email': 'admin@test.com',
    'password': 'Test@1234',
    'role': 'admin'
}

TEST_PRODUCTS = [
    {'name': 'Laptop', 'price': 999.99, 'stock': 10},
    {'name': 'Mouse', 'price': 24.99, 'stock': 50},
    {'name': 'Keyboard', 'price': 59.99, 'stock': 30}
]

# Fixtures
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

        app.config['TEST_ADMIN_ID'] = admin.id
        
        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def get_auth_headers(app, user_id=None, role='admin'):
    with app.app_context():
        if user_id is None:
            user_id = app.config.get('TEST_ADMIN_ID', 1)

        user_identity = {'id': str(user_id), 'role': role}
        access_token = create_access_token(
            identity=user_identity,
            additional_claims={'role': role}
        )
        
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

# Helper functions
def create_test_products(client, headers, products=None):
    if products is None:
        products = TEST_PRODUCTS
    
    created_products = []
    for product in products:
        response = client.post(
            '/api/products',
            json=product,
            headers=headers,
            content_type='application/json'
        )
        assert response.status_code == HTTPStatus.CREATED
        created_products.append(response.get_json())
    
    return created_products


class TestProductEndpoints:
    
    def test_create_product_success(self, client, app):
        with app.app_context():
            headers = get_auth_headers(app)
            product_data = TEST_PRODUCTS[0]

            response = client.post(
                '/api/products',
                json=product_data,
                headers=headers
            )

            assert response.status_code == HTTPStatus.CREATED
            response_data = response.get_json()
            assert response_data['message'] == 'Product created successfully'
            assert 'product_id' in response_data

            product = Product.query.get(response_data['product_id'])
            assert product is not None
            assert product.name == product_data['name']
            assert product.price == product_data['price']
            assert product.stock == product_data['stock']
    
    def test_create_product_invalid_data(self, client, app):
        with app.app_context():
            headers = get_auth_headers(app)
            invalid_product = {'name': '', 'price': -10, 'stock': -5}

            response = client.post(
                '/api/products',
                json=invalid_product,
                headers=headers
            )

            assert response.status_code == HTTPStatus.BAD_REQUEST
            response_data = response.get_json()
            assert 'error' in response_data
    
    def test_create_product_unauthorized(self, client, app):
        response = client.post(
            '/api/products',
            json=TEST_PRODUCTS[0],
            content_type='application/json'
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
    
    def test_create_product_forbidden(self, client, app):
        headers = get_auth_headers(app, role='user')

        response = client.post(
            '/api/products',
            json=TEST_PRODUCTS[0],
            headers=headers
        )

        assert response.status_code == HTTPStatus.FORBIDDEN
    
    def test_get_products_empty(self, client, app):
        # Act
        response = client.get('/api/products')
        
        # Assert
        assert response.status_code == HTTPStatus.OK
        response_data = response.get_json()
        assert isinstance(response_data, dict)
        assert 'products' in response_data
        assert 'total' in response_data
        assert isinstance(response_data['products'], list)
        assert len(response_data['products']) == 0
        assert response_data['total'] == 0
    
    def test_get_products_success(self, client, app):
        """Test getting all products."""
        with app.app_context():
            # Arrange
            headers = get_auth_headers(app)
            created_products = create_test_products(client, headers)
            
            # Act
            response = client.get('/api/products')
            
            # Assert
            assert response.status_code == HTTPStatus.OK
            response_data = response.get_json()
            assert isinstance(response_data, dict)
            assert 'products' in response_data
            assert 'total' in response_data
            assert isinstance(response_data['products'], list)
            assert len(response_data['products']) == len(created_products)
            assert response_data['total'] == len(created_products)
            
            # Verify product data
            for i, product in enumerate(response_data['products']):
                assert product['name'] == TEST_PRODUCTS[i]['name']
                assert float(product['price']) == TEST_PRODUCTS[i]['price']
                assert product['stock'] == TEST_PRODUCTS[i]['stock']
    
    def test_update_product_success(self, client, app):
        """Test updating a product with valid data."""
        with app.app_context():
            # Arrange
            headers = get_auth_headers(app)
            created_products = create_test_products(client, headers, [TEST_PRODUCTS[0]])
            product_id = created_products[0]['product_id']
            
            update_data = {
                'name': 'Updated Laptop',
                'price': 1099.99,
                'stock': 5
            }
            
            # Act
            response = client.put(
                f'/api/products/{product_id}',
                json=update_data,
                headers=headers
            )
            
            # Assert
            assert response.status_code == HTTPStatus.OK
            response_data = response.get_json()
            assert response_data['message'] == 'Product updated successfully'
            
            # Verify product was updated in the database
            product = Product.query.get(product_id)
            assert product.name == update_data['name']
            assert product.price == update_data['price']
            assert product.stock == update_data['stock']
    
    def test_update_product_partial(self, client, app):
        """Test updating a product with partial data."""
        with app.app_context():
            # Arrange
            headers = get_auth_headers(app)
            created_products = create_test_products(client, headers, [TEST_PRODUCTS[0]])
            product_id = created_products[0]['product_id']
            
            # Only update the price
            update_data = {'price': 899.99}
            
            # Act
            response = client.put(
                f'/api/products/{product_id}',
                json=update_data,
                headers=headers
            )
            
            # Assert
            assert response.status_code == HTTPStatus.OK
            
            # Verify only price was updated
            product = Product.query.get(product_id)
            assert product.price == update_data['price']
            assert product.name == TEST_PRODUCTS[0]['name']  # Should remain unchanged
    
    def test_update_product_not_found(self, client, app):
        """Test updating a non-existent product."""
        # Arrange
        headers = get_auth_headers(app)
        non_existent_id = 9999
        
        # Act
        response = client.put(
            f'/api/products/{non_existent_id}',
            json={'name': 'Test'},
            headers=headers
        )
        
        # Assert
        assert response.status_code == HTTPStatus.NOT_FOUND
    
    def test_delete_product_success(self, client, app):
        """Test deleting a product."""
        with app.app_context():
            # Arrange
            headers = get_auth_headers(app)
            created_products = create_test_products(client, headers, [TEST_PRODUCTS[0]])
            product_id = created_products[0]['product_id']
            
            # Act
            response = client.delete(
                f'/api/products/{product_id}',
                headers=headers
            )
            
            # Assert
            assert response.status_code == HTTPStatus.OK
            response_data = response.get_json()
            assert response_data['message'] == 'Product deleted successfully'
            
            # Verify product was deleted from the database
            product = Product.query.get(product_id)
            assert product is None
    
    def test_delete_product_not_found(self, client, app):
        """Test deleting a non-existent product."""
        # Arrange
        headers = get_auth_headers(app)
        non_existent_id = 9999
        
        # Act
        response = client.delete(
            f'/api/products/{non_existent_id}',
            headers=headers
        )
        
        # Assert
        assert response.status_code == HTTPStatus.NOT_FOUND