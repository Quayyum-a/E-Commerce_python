import pytest
from app import create_app, db
from app.domain.user import User

@pytest.fixture(scope='function')
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # In-memory SQLite
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    # Reinitialize db with the test app context
    with app.app_context():
        db.init_app(app)  # Rebind db to the app with updated config
        db.create_all()
        db.session.query(User).delete()  # Clear any residual data
        db.session.commit()
        yield app
        db.drop_all()
        db.session.remove()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.mark.order(1)
def test_register_user(client):
    response = client.post('/api/auth/register', json={
        'username': 'testuser', 'email': 'again@example.com', 'password': 'password123', 'role': 'customer'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User registered'

@pytest.mark.order(2)
def test_login_user(client):
    client.post('/api/auth/register', json={
        'username': 'testuser', 'email': 'test@example.com', 'password': 'password123'
    })
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com', 'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json