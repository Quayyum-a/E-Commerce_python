class CreateCartRequest:
    def __init__(self, user_id: int):
        self.user_id = user_id

class AddCartItemRequest:
    def __init__(self, cart_id: int, product_id: int, quantity: int):
        self.cart_id = cart_id
        self.product_id = product_id
        self.quantity = quantity

class RemoveCartItemRequest:
    def __init__(self, cart_id: int, product_id: int):
        self.cart_id = cart_id
        self.product_id = product_id

