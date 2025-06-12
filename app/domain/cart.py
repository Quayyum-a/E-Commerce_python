class Cart:
    def __init__(self, id: int, user_id: int):
        self.id = id
        self.user_id = user_id
        self.items = []  # List of CartItem

    def get_items(self):
        return self.items

    def add_item(self, cart_item):
        self.items.append(cart_item)

    def remove_item(self, product_id):
        self.items = [item for item in self.items if item.product_id != product_id]

    def clear_cart(self):
        self.items = []

