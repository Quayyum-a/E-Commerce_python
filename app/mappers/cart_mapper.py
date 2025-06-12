from app.dtos.responses.cart_responses import CartResponse, CartItemResponse

def cart_item_to_response(cart_item):
    return CartItemResponse(
        id=cart_item.id,
        cart_id=cart_item.cart_id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity
    )

def cart_to_response(cart):
    items = [cart_item_to_response(item) for item in cart.items]
    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=items
    )

