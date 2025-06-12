from flask import Blueprint, request, jsonify
from app.infrastructure.cart_repository import CartRepository
from app.infrastructure.cart_item_repository import CartItemRepository
from app.domain.cart import Cart
from app.domain.cart_item import CartItem
from app.mappers.cart_mapper import cart_to_response, cart_item_to_response

bp = Blueprint('cart', __name__, url_prefix='/api/cart')
cart_repo = CartRepository()
cart_item_repo = CartItemRepository()

@bp.route('/', methods=['POST'])
def create_cart():
    data = request.get_json()
    cart = Cart(user_id=data['user_id'])
    cart_repo.add_cart(cart)
    return jsonify({'cart': cart_to_response(cart).__dict__}), 201

@bp.route('/<int:cart_id>', methods=['GET'])
def get_cart(cart_id):
    cart = cart_repo.get_cart(cart_id)
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
    return jsonify({'cart': cart_to_response(cart).__dict__})

@bp.route('/<int:cart_id>/items', methods=['POST'])
def add_cart_item(cart_id):
    data = request.get_json()
    cart_item = CartItem(cart_id=cart_id, product_id=data['product_id'], quantity=data['quantity'])
    cart_item_repo.add_cart_item(cart_item)
    cart = cart_repo.get_cart(cart_id)
    return jsonify({'cart': cart_to_response(cart).__dict__})

@bp.route('/<int:cart_id>/items/<int:item_id>', methods=['DELETE'])
def remove_cart_item(cart_id, item_id):
    cart_item_repo.remove_cart_item(item_id)
    cart = cart_repo.get_cart(cart_id)
    return jsonify({'cart': cart_to_response(cart).__dict__})

