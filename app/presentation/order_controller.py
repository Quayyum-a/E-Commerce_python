from flask import Blueprint, request, jsonify
      from flask_jwt_extended import jwt_required, get_jwt_identity
      from app.application.order_service import OrderService

      bp = Blueprint('order', __name__, url_prefix='/api/orders')

      @bp.route('', methods=['POST'])
      @jwt_required()
      def place_order():
          identity = get_jwt_identity()
          data = request.get_json()
          try:
              order = OrderService().place_order(identity['id'], data['product_id'], data['quantity'])
              return jsonify({'message': 'Order placed', 'order_id': order.id}), 201
          except ValueError as e:
              return jsonify({'error': str(e)}), 400

      @bp.route('', methods=['GET'])
      @jwt_required()
      def get_orders():
          identity = get_jwt_identity()
          orders = OrderService().get_user_orders(identity['id'])
          return jsonify([{'id': o.id, 'product_id': o.product_id, 'quantity': o.quantity, 'status': o.status} for o in orders]), 200