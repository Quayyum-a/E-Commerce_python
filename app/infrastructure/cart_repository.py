
from app.domain.cart import Cart

class CartRepository:
    def __init__(self):
        self.carts = {}

    def add_cart(self, cart: Cart):
        self.carts[cart.id] = cart

    def get_cart(self, cart_id: int):
        return self.carts.get(cart_id)

    def remove_cart(self, cart_id: int):
        if cart_id in self.carts:
            del self.carts[cart_id]

    def get_carts_by_user(self, user_id: int):
        return [cart for cart in self.carts.values() if cart.user_id == user_id]

