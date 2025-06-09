from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.application.product_service import ProductService

bp = Blueprint('product', __name__, url_prefix='/api/products')

@bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    identity = get_jwt_identity()
    # Handle both string and dictionary identity formats
    if isinstance(identity, dict):
        if identity.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
    else:
        # If identity is a string, we need to get the role from JWT claims
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
    data = request.get_json()
    try:
        product = ProductService().create_product(data['name'], data['price'], data['stock'])
        return jsonify({'message': 'Product created', 'product_id': product.id}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('', methods=['GET'])
def get_products():
    products = ProductService().get_products()
    return jsonify([{'id': p.id, 'name': p.name, 'price': p.price, 'stock': p.stock} for p in products]), 200

@bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    identity = get_jwt_identity()
    # Handle both string and dictionary identity formats
    if isinstance(identity, dict):
        if identity.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
    else:
        # If identity is a string, we need to get the role from JWT claims
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
    data = request.get_json()
    try:
        product = ProductService().update_product(product_id, data['name'], data['price'], data['stock'])
        return jsonify({'message': 'Product updated', 'product_id': product.id}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400