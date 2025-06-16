from typing import Dict, Any

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from flask_restx import Namespace, Resource, fields

from app.application.product_service import ProductService
from app.dtos.exceptions import ForbiddenException, NotFoundException, ValidationException
from app.dtos.requests.product_requests import ProductCreateRequest, ProductUpdateRequest
from app.mappers.product_mapper import ProductMapper

bp = Blueprint('product', __name__, url_prefix='/api/products')
api = Namespace('products', description='Product operations', path='/api/products')

product_model = api.model('Product', {
    'name': fields.String(required=True, description='Product name'),
    'price': fields.Float(required=True, description='Product price'),
    'stock': fields.Integer(required=True, description='Product stock'),
})

product_update_model = api.model('ProductUpdate', {
    'name': fields.String(required=False, description='Product name'),
    'price': fields.Float(required=False, description='Product price'),
    'stock': fields.Integer(required=False, description='Product stock'),
})

message_response = api.model('MessageResponse', {
    'message': fields.String(description='Message'),
    'product_id': fields.Integer(description='Product ID'),
})

def _get_user_role(identity: Any, jwt: Dict[str, Any]) -> str:
    if isinstance(identity, dict):
        return identity.get('role')
    return jwt.get('role')

@bp.errorhandler(ValidationException)
def handle_validation_error(e):
    return jsonify({'error': str(e)}), 400

@bp.errorhandler(NotFoundException)
def handle_not_found_error(e):
    return jsonify({'error': str(e)}), 404

@bp.errorhandler(ForbiddenException)
def handle_forbidden_error(e):
    return jsonify({'error': str(e)}), 403

@api.route('')
class ProductList(Resource):
    @api.doc('list_products')
    @api.response(200, 'Success')
    def get(self):
        products = ProductService().get_products()
        response = ProductMapper.to_list_response(products=products, total=len(products))
        return response.model_dump(), 200

    @api.doc('create_product')
    @api.expect(product_model)
    @api.response(201, 'Product created', model=message_response)
    @jwt_required()
    def post(self):
        identity = get_jwt_identity()
        user_role = _get_user_role(identity, get_jwt())
        if user_role != 'admin':
            api.abort(403, 'Admin access required')
        try:
            create_dto = ProductCreateRequest(**api.payload)
        except Exception as e:
            api.abort(400, f"Invalid product data: {str(e)}")
        product_data = ProductMapper.create_to_entity(create_dto)
        product = ProductService().create_product(**product_data)
        response = ProductMapper.to_message_response(
            message="Product created successfully",
            product_id=product.id
        )
        return response.model_dump(), 201

@api.route('/<int:product_id>')
@api.param('product_id', 'The product identifier')
class ProductResource(Resource):
    @api.doc('update_product')
    @api.expect(product_update_model)
    @api.response(200, 'Product updated', model=message_response)
    @jwt_required()
    def put(self, product_id):
        identity = get_jwt_identity()
        user_role = _get_user_role(identity, get_jwt())
        if user_role != 'admin':
            api.abort(403, 'Admin access required')
        try:
            update_dto = ProductUpdateRequest(**api.payload)
        except Exception as e:
            api.abort(400, f"Invalid product data: {str(e)}")
        update_data = ProductMapper.update_to_entity(update_dto)
        product = ProductService().update_product(product_id, **update_data)
        if not product:
            api.abort(404, 'Product not found')
        response = ProductMapper.to_message_response(
            message="Product updated successfully",
            product_id=product.id
        )
        return response.model_dump(), 200

    @api.doc('delete_product')
    @api.response(200, 'Product deleted', model=message_response)
    @jwt_required()
    def delete(self, product_id):
        identity = get_jwt_identity()
        user_role = _get_user_role(identity, get_jwt())
        if user_role != 'admin':
            api.abort(403, 'Admin access required')
        success = ProductService().delete_product(product_id)
        if not success:
            api.abort(404, 'Product not found')
        response = ProductMapper.to_message_response(
            message="Product deleted successfully"
        )
        return response.model_dump(), 200
