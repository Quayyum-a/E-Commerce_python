from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields

from app.application.order_service import OrderService

bp = Blueprint('order', __name__, url_prefix='/api/orders')
api = Namespace('orders', description='Order operations', path='/api/orders')

order_model = api.model('Order', {
    'product_id': fields.Integer(required=True, description='Product ID'),
    'quantity': fields.Integer(required=True, description='Quantity'),
})

order_response = api.model('OrderResponse', {
    'message': fields.String(description='Message'),
    'order_id': fields.Integer(description='Order ID'),
})

order_list_item = api.model('OrderListItem', {
    'id': fields.Integer(description='Order ID'),
    'product_id': fields.Integer(description='Product ID'),
    'quantity': fields.Integer(description='Quantity'),
    'status': fields.String(description='Order status'),
})

@bp.route('', methods=['POST'])
@jwt_required()
def place_order():
    identity = get_jwt_identity()
    data = request.get_json()
    try:
        order = OrderService().place_order(identity, data['product_id'], data['quantity'])
        return jsonify({'message': 'Order placed', 'order_id': order.id}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    identity = get_jwt_identity()
    orders = OrderService().get_user_orders(identity)
    return jsonify([{'id': o.id, 'product_id': o.product_id, 'quantity': o.quantity, 'status': o.status} for o in orders]), 200

@api.route('')
class OrderList(Resource):
    @api.doc('place_order')
    @api.expect(order_model)
    @api.response(201, 'Order placed', model=order_response)
    @api.response(400, 'Invalid input')
    @jwt_required()
    def post(self):
        identity = get_jwt_identity()
        data = api.payload
        try:
            order = OrderService().place_order(identity, data['product_id'], data['quantity'])
            return {'message': 'Order placed', 'order_id': order.id}, 201
        except ValueError as e:
            api.abort(400, str(e))

    @api.doc('get_orders')
    @api.marshal_list_with(order_list_item)
    @jwt_required()
    def get(self):
        identity = get_jwt_identity()
        orders = OrderService().get_user_orders(identity)
        return [{'id': o.id, 'product_id': o.product_id, 'quantity': o.quantity, 'status': o.status} for o in orders], 200
