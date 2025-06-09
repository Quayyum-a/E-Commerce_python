import pytest
from app import create_app, db
from app.domain.user import User

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