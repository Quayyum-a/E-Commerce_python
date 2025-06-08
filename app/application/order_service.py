from app.domain.order import Order
from app.infrastructure.order_repository import OrderRepository
from app.infrastructure.product_repository import ProductRepository

class OrderService:
def __init__(self):
        self.order_repo = OrderRepository()
        self.product_repo = ProductRepository()

    def place_order(self, user_id, product_id, quantity):
        product = self.product_repo.find_product_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        if product.stock < quantity:
            raise ValueError("Insufficient stock")
        order = Order(user_id=user_id, product_id=product_id, quantity=quantity)
        product.stock -= quantity
        self.product_repo.save_product(product)
        return self.order_repo.save_order(order)

    def get_user_orders(self, user_id):
        return self.order_repo.find_orders_by_user(user_id)