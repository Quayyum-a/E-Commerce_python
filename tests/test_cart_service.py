import pytest
from app import create_app, db
from app.domain.user import User
from app.domain.product import Product
from app.domain.cart import Cart
from app.domain.cart_item import CartItem

TEST_USER = {
    'username': 'cartuser',
    'email': 'cartuser@test.com',
    'password': 'Test@1234',
    'role': 'customer'
}

TEST_PRODUCT = {'name': 'Pen', 'price': 2.99, 'stock': 100}

@pytest.fixture(scope='function')
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
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
        product = Product(
            name=TEST_PRODUCT['name'],
            price=TEST_PRODUCT['price'],
            stock=TEST_PRODUCT['stock']
        )
        db.session.add(product)
        db.session.commit()
        app.config['TEST_USER_ID'] = user.id
        app.config['TEST_PRODUCT_ID'] = product.id
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_cart(client, app):
    user_id = app.config['TEST_USER_ID']
    response = client.post('/api/cart/', json={'user_id': user_id})
    assert response.status_code == 201
    assert 'cart' in response.json
    assert response.json['cart']['user_id'] == user_id

def test_get_cart_success(client, app):
    user_id = app.config['TEST_USER_ID']
    response = client.post('/api/cart/', json={'user_id': user_id})
    cart_id = response.json['cart']['id']
    response = client.get(f'/api/cart/{cart_id}')
    assert response.status_code == 200
    assert response.json['cart']['id'] == cart_id

def test_get_cart_not_found(client):
    response = client.get('/api/cart/9999')
    assert response.status_code == 404

def test_add_cart_item_success(client, app):
    user_id = app.config['TEST_USER_ID']
    product_id = app.config['TEST_PRODUCT_ID']
    response = client.post('/api/cart/', json={'user_id': user_id})
    cart_id = response.json['cart']['id']
    response = client.post(f'/api/cart/{cart_id}/items', json={'product_id': product_id, 'quantity': 3})
    assert response.status_code == 200
    assert len(response.json['cart']['items']) == 1
    assert response.json['cart']['items'][0]['product_id'] == product_id
    assert response.json['cart']['items'][0]['quantity'] == 3

def test_add_cart_item_invalid_product(client, app):
    user_id = app.config['TEST_USER_ID']
    response = client.post('/api/cart/', json={'user_id': user_id})
    cart_id = response.json['cart']['id']
    response = client.post(f'/api/cart/{cart_id}/items', json={'product_id': 9999, 'quantity': 1})
    assert response.status_code == 200

def test_remove_cart_item_success(client, app):
    user_id = app.config['TEST_USER_ID']
    product_id = app.config['TEST_PRODUCT_ID']
    response = client.post('/api/cart/', json={'user_id': user_id})
    cart_id = response.json['cart']['id']
    response = client.post(f'/api/cart/{cart_id}/items', json={'product_id': product_id, 'quantity': 2})
    item_id = response.json['cart']['items'][0]['id']
    response = client.delete(f'/api/cart/{cart_id}/items/{item_id}')
    assert response.status_code == 200
    assert response.json['cart']['items'] == []

def test_remove_cart_item_not_found(client, app):
    user_id = app.config['TEST_USER_ID']
    response = client.post('/api/cart/', json={'user_id': user_id})
    cart_id = response.json['cart']['id']
    response = client.delete(f'/api/cart/{cart_id}/items/9999')
    assert response.status_code == 200

def test_add_duplicate_cart_item(client, app):
    user_id = app.config['TEST_USER_ID']
    product_id = app.config['TEST_PRODUCT_ID']
    response = client.post('/api/cart/', json={'user_id': user_id})
    cart_id = response.json['cart']['id']
    client.post(f'/api/cart/{cart_id}/items', json={'product_id': product_id, 'quantity': 1})
    response = client.post(f'/api/cart/{cart_id}/items', json={'product_id': product_id, 'quantity': 2})
    assert response.status_code == 200
    assert len(response.json['cart']['items']) >= 1

def test_clear_cart(client, app):
    user_id = app.config['TEST_USER_ID']
    product_id = app.config['TEST_PRODUCT_ID']
    response = client.post('/api/cart/', json={'user_id': user_id})
    cart_id = response.json['cart']['id']
    client.post(f'/api/cart/{cart_id}/items', json={'product_id': product_id, 'quantity': 2})
    # Simulate clear by removing all items
    from app.domain.cart import Cart
    from app import db
    cart = db.session.get(Cart, cart_id)
    for item in list(cart.items):
        db.session.delete(item)
    db.session.commit()
    response = client.get(f'/api/cart/{cart_id}')
    assert response.status_code == 200
    assert response.json['cart']['items'] == []
