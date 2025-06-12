import pytest
from app import create_app, db
from app.domain.cart import Cart
from app.domain.cart_item import CartItem
from app.infrastructure.cart_repository import CartRepository
from app.infrastructure.cart_item_repository import CartItemRepository

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def cart_repo():
    return CartRepository()

@pytest.fixture
def cart_item_repo():
    return CartItemRepository()

def test_create_cart(cart_repo):
    cart = Cart(user_id=1)
    cart_repo.add_cart(cart)
    assert cart.id is not None

def test_add_cart_item(cart_repo, cart_item_repo):
    cart = Cart(user_id=1)
    cart_repo.add_cart(cart)
    cart_item = CartItem(cart_id=cart.id, product_id=1, quantity=2)
    cart_item_repo.add_cart_item(cart_item)
    items = cart_item_repo.get_items_by_cart(cart.id)
    assert len(items) == 1
    assert items[0].product_id == 1
    assert items[0].quantity == 2

def test_remove_cart_item(cart_repo, cart_item_repo):
    cart = Cart(user_id=1)
    cart_repo.add_cart(cart)
    cart_item = CartItem(cart_id=cart.id, product_id=1, quantity=2)
    cart_item_repo.add_cart_item(cart_item)
    cart_item_repo.remove_cart_item(cart_item.id)
    items = cart_item_repo.get_items_by_cart(cart.id)
    assert len(items) == 0

