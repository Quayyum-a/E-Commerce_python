import pytest
from app import create_app, db


@pytest.fixture(scope='function')
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_user(client):
    response = client.post('/api/auth/register', json={
        'username': 'testuser', 'email': 'again@example.com', 'password': 'password123', 'role': 'customer'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User registered'

def test_login_user(client):
    client.post('/api/auth/register', json={
        'username': 'testuser', 'email': 'test@example.com', 'password': 'password123'
    })
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com', 'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json