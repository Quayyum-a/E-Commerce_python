from flask import Blueprint, request, jsonify
from app.application.auth_service import AuthService


bp = Blueprint('auth', __name__, url_prefix='/api/auth')

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

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        token = AuthService().login_user(data['email'], data['password'])
        return jsonify({'access_token': token}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401