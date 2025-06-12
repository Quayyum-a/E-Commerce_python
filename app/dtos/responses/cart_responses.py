class CartResponse:
    def __init__(self, id, user_id, items):
        self.id = id
        self.user_id = user_id
        self.items = items

class CartItemResponse:
    def __init__(self, id, cart_id, product_id, quantity):
        self.id = id
        self.cart_id = cart_id
        self.product_id = product_id
        self.quantity = quantity

