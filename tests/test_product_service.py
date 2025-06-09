import pytest
from app import create_app, db
from app.domain.product import Product

@pytest.fixture(scope='function')
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # In-memory SQLite
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret-key'
    })
    # Reinitialize db with the test app context
    with app.app_context():
        # Drop all tables first to ensure a clean state
        db.drop_all()
        # Then create all tables
        db.create_all()
        # Clear any existing data
        db.session.query(Product).delete()
        db.session.commit()

        yield app

        # Clean up after test
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.mark.order(1)
def test_create_product(client):
    product_data = {
        'name': 'Test Product',
        'description': 'This is a test product',
        'price': 19.99,
        'stock': 100
    }

    response = client.post('/api/products', json=product_data)
    assert response.status_code == 201
    assert response.json['message'] == 'Product created'
    assert 'product_id' in response.json

    with client.application.app_context():
        product = Product.query.get(response.json['product_id'])
        assert product is not None
        assert product.name == product_data['name']
        assert product.description == product_data['description']
        assert product.price == product_data['price']
        assert product.stock == product_data['stock']