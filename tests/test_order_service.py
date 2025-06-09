from http import HTTPStatus

import pytest
from flask_jwt_extended import create_access_token, JWTManager

from app import create_app, db
from app.domain.product import Product
from app.domain.user import User

TEST_USER = {
    'username': 'testuser',
    'email': 'user@test.com',
    'password': 'Test@1234',
    'role': 'customer'
}

TEST_PRODUCT = {'name': 'Book', 'price': 19.99, 'stock': 5}

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
        return {'id': identity, 'role': jwt_data.get('role', 'customer')}
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = User(
            username=TEST_USER['username'],
            email=TEST_USER['email'],
            role=TEST_USER['role']
        )
        user.set_password(TEST_USER['password'])
        db.session.add(user)
        db.session.commit()
        app.config['TEST_USER_ID'] = user.id
        product = Product(
            name=TEST_PRODUCT['name'],
            price=TEST_PRODUCT['price'],
            stock=TEST_PRODUCT['stock']
        )
        db.session.add(product)
        db.session.commit()
        app.config['TEST_PRODUCT_ID'] = product.id
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def get_auth_headers(app, user_id=None, role='customer'):
    with app.app_context():
        if user_id is None:
            user_id = app.config.get('TEST_USER_ID', 1)
        user_identity = {'id': str(user_id), 'role': role}
        access_token = create_access_token(
            identity=user_identity,
            additional_claims={'role': role}
        )
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

class TestOrderEndpoints:
    def test_place_order_success(self, client, app):
        headers = get_auth_headers(app)
        product_id = app.config['TEST_PRODUCT_ID']
        response = client.post(
            '/api/orders',
            json={'product_id': product_id, 'quantity': 2},
            headers=headers
        )
        assert response.status_code == HTTPStatus.CREATED
        data = response.get_json()
        assert 'order_id' in data
        assert data['message'] == 'Order placed'

    def test_place_order_insufficient_stock(self, client, app):
        headers = get_auth_headers(app)
        product_id = app.config['TEST_PRODUCT_ID']
        response = client.post(
            '/api/orders',
            json={'product_id': product_id, 'quantity': 100},
            headers=headers
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = response.get_json()
        assert 'error' in data
        assert 'Insufficient stock' in data['error']

    def test_place_order_product_not_found(self, client, app):
        headers = get_auth_headers(app)
        response = client.post(
            '/api/orders',
            json={'product_id': 9999, 'quantity': 1},
            headers=headers
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = response.get_json()
        assert 'error' in data
        assert 'Product not found' in data['error']

    def test_place_order_unauthorized(self, client):
        response = client.post(
            '/api/orders',
            json={'product_id': 1, 'quantity': 1}
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_get_orders_empty(self, client, app):
        headers = get_auth_headers(app)
        response = client.get('/api/orders', headers=headers)
        assert response.status_code == HTTPStatus.OK
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_orders_with_orders(self, client, app):
        headers = get_auth_headers(app)
        product_id = app.config['TEST_PRODUCT_ID']
        # Place an order
        client.post(
            '/api/orders',
            json={'product_id': product_id, 'quantity': 1},
            headers=headers
        )
        response = client.get('/api/orders', headers=headers)
        assert response.status_code == HTTPStatus.OK
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        order = data[0]
        assert order['product_id'] == product_id
        assert order['quantity'] == 1
        assert order['status'] == 'pending'
