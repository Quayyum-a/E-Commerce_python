from app.domain.cart_item import CartItem
from app import db

class CartItemRepository:
    def add_cart_item(self, cart_item: CartItem):
        db.session.add(cart_item)
        db.session.commit()
        return cart_item

    def get_cart_item(self, cart_item_id: int):
        return CartItem.query.get(cart_item_id)

    def remove_cart_item(self, cart_item_id: int):
        cart_item = CartItem.query.get(cart_item_id)
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()

    def get_items_by_cart(self, cart_id: int):
        return CartItem.query.filter_by(cart_id=cart_id).all()
