from app.domain.cart import Cart
from app import db

class CartRepository:
    def add_cart(self, cart: Cart):
        db.session.add(cart)
        db.session.commit()
        return cart

    def get_cart(self, cart_id: int):
        return Cart.query.get(cart_id)

    def remove_cart(self, cart_id: int):
        cart = Cart.query.get(cart_id)
        if cart:
            db.session.delete(cart)
            db.session.commit()

    def get_carts_by_user(self, user_id: int):
        return Cart.query.filter_by(user_id=user_id).all()
