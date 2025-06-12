class CartItem:
    def __init__(self, id: int, cart_id: int, product_id: int, quantity: int):
        self.id = id
        self.cart_id = cart_id
        self.product_id = product_id
        self.quantity = quantity

