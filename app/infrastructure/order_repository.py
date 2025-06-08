from app.domain.order import Order
from app import db

class OrderRepository:
    def save_order(self, order):
        db.session.add(order)
        db.session.commit()
        return order

    def find_orders_by_user(self, user_id):
        return Order.query.filter_by(user_id=user_id).all()