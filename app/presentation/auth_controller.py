from flask import Blueprint, request, jsonify
from flask_restx import Namespace, Resource, fields
from app.application.auth_service import AuthService
from sqlalchemy.exc import IntegrityError


bp = Blueprint('auth', __name__, url_prefix='/api/auth')
api = Namespace('auth', description='Authentication operations', path='/api/auth')

register_model = api.model('Register', {
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'role': fields.String(required=False, description='User role', default='customer')
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

@api.route('/register')
class Register(Resource):
    @api.expect(register_model)
    @api.response(201, 'User registered')
    @api.response(400, 'Email or username already exists')
    def post(self):
        data = api.payload
        try:
            user = AuthService().register_user(
                data['username'], data['email'], data['password'], data.get('role', 'customer')
            )
            return {'message': 'User registered', 'user_id': user.id}, 201
        except ValueError as e:
            return {'error': str(e), 'message': 'Email already exists'}, 400
        except IntegrityError:
            return {'error': 'Username or email already exists'}, 400

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    @api.response(200, 'Login successful')
    @api.response(401, 'Invalid credentials')
    def post(self):
        data = api.payload
        if not data.get('email'):
            return {'error': 'Email is required'}, 401
        if not data.get('password'):
            return {'error': 'Password is required'}, 401
        try:
            token = AuthService().login_user(data['email'], data['password'])
            return {'access_token': token}, 200
        except ValueError as e:
            return {'error': str(e)}, 401

# Keep the Blueprint for backward compatibility
@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        user = AuthService().register_user(
            data['username'], data['email'], data['password'], data.get('role', 'customer')
        )
        return jsonify({'message': 'User registered', 'user_id': user.id}), 201
    except ValueError as e:
        return jsonify({'error': str(e), 'message': 'Email already exists'}), 400
    except IntegrityError:
        return jsonify({'error': 'Username or email already exists'}), 400

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data.get('email'):
        return jsonify({'error': 'Email is required'}), 401
    if not data.get('password'):
        return jsonify({'error': 'Password is required'}), 401
    try:
        token = AuthService().login_user(data['email'], data['password'])
        return jsonify({'access_token': token}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401