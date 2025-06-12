from app.domain.cart_item import CartItem

class CartItemRepository:
    def __init__(self):
        self.cart_items = {}

    def add_cart_item(self, cart_item: CartItem):
        self.cart_items[cart_item.id] = cart_item

    def get_cart_item(self, cart_item_id: int):
        return self.cart_items.get(cart_item_id)

    def remove_cart_item(self, cart_item_id: int):
        if cart_item_id in self.cart_items:
            del self.cart_items[cart_item_id]

    def get_items_by_cart(self, cart_id: int):
        return [item for item in self.cart_items.values() if item.cart_id == cart_id]

