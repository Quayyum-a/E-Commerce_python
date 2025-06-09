import pytest
from app import app
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def get_token(user_id=1, role='customer'):
    # Simulate JWT token creation
    return create_access_token(identity={'id': user_id, 'role': role})

def test_place_order(client, monkeypatch):
    token = get_token()
    response = client.post('/api/orders',
        json={'product_id': 1, 'quantity': 1},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code in (201, 400)

def test_get_orders(client, monkeypatch):
    token = get_token()
    response = client.get('/api/orders', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code in (200, 400)
