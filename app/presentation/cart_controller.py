from flask import Blueprint, request, jsonify
from flask_restx import Namespace, Resource, fields
from app.infrastructure.cart_repository import CartRepository
from app.infrastructure.cart_item_repository import CartItemRepository
from app.domain.cart import Cart
from app.domain.cart_item import CartItem
from app.mappers.cart_mapper import cart_to_response, cart_item_to_response

bp = Blueprint('cart', __name__, url_prefix='/api/cart')
api = Namespace('cart', description='Cart operations', path='/api/cart')
cart_repo = CartRepository()
cart_item_repo = CartItemRepository()

cart_model = api.model('Cart', {
    'user_id': fields.Integer(required=True, description='User ID'),
})

cart_item_model = api.model('CartItem', {
    'product_id': fields.Integer(required=True, description='Product ID'),
    'quantity': fields.Integer(required=True, description='Quantity'),
})

cart_response = api.model('CartResponse', {
    'cart': fields.Raw(description='Cart object'),
})

@bp.route('/', methods=['POST'])
class CartCreate(Resource):
    @api.expect(cart_model)
    @api.response(201, 'Cart created', model=cart_response)
    def post(self):
        data = api.payload
        cart = Cart(user_id=data['user_id'])
        cart_repo.add_cart(cart)
        return {'cart': cart_to_response(cart).__dict__}, 201

@bp.route('/<int:cart_id>', methods=['GET'])
@api.param('cart_id', 'The cart identifier')
class CartResource(Resource):
    @api.response(200, 'Success', model=cart_response)
    @api.response(404, 'Cart not found')
    def get(self, cart_id):
        cart = cart_repo.get_cart(cart_id)
        if not cart:
            api.abort(404, 'Cart not found')
        return {'cart': cart_to_response(cart).__dict__}

@bp.route('/<int:cart_id>/items', methods=['POST'])
@api.param('cart_id', 'The cart identifier')
class CartItemAdd(Resource):
    @api.expect(cart_item_model)
    @api.response(200, 'Item added', model=cart_response)
    def post(self, cart_id):
        data = api.payload
        cart_item = CartItem(cart_id=cart_id, product_id=data['product_id'], quantity=data['quantity'])
        cart_item_repo.add_cart_item(cart_item)
        cart = cart_repo.get_cart(cart_id)
        return {'cart': cart_to_response(cart).__dict__}

@bp.route('/<int:cart_id>/items/<int:item_id>', methods=['DELETE'])
@api.param('cart_id', 'The cart identifier')
@api.param('item_id', 'The item identifier')
class CartItemRemove(Resource):
    @api.response(200, 'Item removed', model=cart_response)
    def delete(self, cart_id, item_id):
        cart_item_repo.remove_cart_item(item_id)
        cart = cart_repo.get_cart(cart_id)
        return {'cart': cart_to_response(cart).__dict__}
