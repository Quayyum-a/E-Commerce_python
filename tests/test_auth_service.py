import pytest

from app import create_app, db
from app.domain.user import User


@pytest.fixture(scope='function')
def app():

    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret-key'
    })

    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.query(User).delete()
        db.session.commit()
        
        yield app
        
        # Clean up after test
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# Test Data
TEST_USER = {
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'Test@1234',
    'role': 'customer'
}

def test_register_user_success(client):
    response = client.post('/api/auth/register', 
                         json=TEST_USER,
                         content_type='application/json')
    assert response.status_code == 201
    assert response.json['message'] == 'User registered'
    assert 'user_id' in response.json

    with client.application.app_context():
        user = User.query.filter_by(email=TEST_USER['email']).first()
        assert user is not None
        assert user.username == TEST_USER['username']
        assert user.role == TEST_USER['role']
        assert user.check_password(TEST_USER['password'])

def test_register_duplicate_email(client):
    client.post('/api/auth/register', json=TEST_USER)

    response = client.post('/api/auth/register', 
                         json={
                             'username': 'anotheruser',
                             'email': TEST_USER['email'],
                             'password': 'Another@1234',
                             'role': 'customer'
                         })
    assert response.status_code == 400
    assert 'email already exists' in response.json['error'].lower()

def test_register_invalid_email_format(client):

    response = client.post('/api/auth/register',
                         json={
                             'username': 'invaliduser',
                             'email': 'invalid-email',
                             'password': 'Invalid@1234',
                             'role': 'customer'
                         })
    assert response.status_code == 400
    assert 'invalid email format' in response.json['error'].lower()


def test_login_success(client):
    client.post('/api/auth/register', json=TEST_USER)

    response = client.post('/api/auth/login',
                         json={
                             'email': TEST_USER['email'],
                             'password': TEST_USER['password']
                         })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_login_invalid_credentials(client):
    client.post('/api/auth/register', json=TEST_USER)

    response = client.post('/api/auth/login',
                         json={
                             'email': TEST_USER['email'],
                             'password': 'wrongpassword'
                         })
    assert response.status_code == 401

    response = client.post('/api/auth/login',
                         json={
                             'email': 'nonexistent@example.com',
                             'password': 'doesntmatter'
                         })
    assert response.status_code == 401

def test_login_missing_credentials(client):
    response = client.post('/api/auth/login', json={'password': 'Test@1234'})
    assert response.status_code == 401
    assert 'email is required' in response.json['error'].lower()

    response = client.post('/api/auth/login', json={'email': TEST_USER['email']})
    assert response.status_code == 401
    assert 'password is required' in response.json['error'].lower()
