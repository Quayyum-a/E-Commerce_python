from typing import Dict, Any

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.application.product_service import ProductService
from app.dtos.exceptions import ForbiddenException, NotFoundException, ValidationException
from app.dtos.requests.product_requests import ProductCreateRequest, ProductUpdateRequest
from app.mappers.product_mapper import ProductMapper

bp = Blueprint('product', __name__, url_prefix='/api/products')

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

@bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    identity = get_jwt_identity()
    user_role = _get_user_role(identity, get_jwt())
    if user_role != 'admin':
        raise ForbiddenException("Admin access required")

    try:
        create_dto = ProductCreateRequest(**request.get_json())
    except Exception as e:
        raise ValidationException(f"Invalid product data: {str(e)}")
    
    # Create product
    product_data = ProductMapper.create_to_entity(create_dto)
    product = ProductService().create_product(**product_data)
    
    # Return response
    response = ProductMapper.to_message_response(
        message="Product created successfully",
        product_id=product.id
    )
    return jsonify(response.model_dump()), 201

@bp.route('', methods=['GET'])
def get_products():
    # Get products from service
    products = ProductService().get_products()
    
    # Convert to response DTO
    response = ProductMapper.to_list_response(
        products=products,
        total=len(products)
    )
    return jsonify(response.model_dump())

@bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id: int):
    # Check admin access
    identity = get_jwt_identity()
    user_role = _get_user_role(identity, get_jwt())
    if user_role != 'admin':
        raise ForbiddenException("Admin access required")
    
    # Validate and parse request
    try:
        update_dto = ProductUpdateRequest(**request.get_json())
    except Exception as e:
        raise ValidationException(f"Invalid product data: {str(e)}")
    
    # Update product
    update_data = ProductMapper.update_to_entity(update_dto)
    product = ProductService().update_product(product_id, **update_data)
    
    if not product:
        raise NotFoundException("Product")
    
    # Return response
    response = ProductMapper.to_message_response(
        message="Product updated successfully",
        product_id=product.id
    )
    return jsonify(response.model_dump())

@bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id: int):
    # Check admin access
    identity = get_jwt_identity()
    user_role = _get_user_role(identity, get_jwt())
    if user_role != 'admin':
        raise ForbiddenException("Admin access required")
    
    # Delete product
    success = ProductService().delete_product(product_id)
    
    if not success:
        raise NotFoundException("Product")
    
    # Return success response
    response = ProductMapper.to_message_response(
        message="Product deleted successfully"
    )
    return jsonify(response.model_dump()), 200