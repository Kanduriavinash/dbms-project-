# blueprints/cart_utils.py
import uuid
from flask import session, current_app
from flask_login import current_user
from extensions import db
from models import Cart, CartItem, Product

def _make_session_key():
    return "cart:" + uuid.uuid4().hex

def get_or_create_cart():
    """
    Return a Cart instance:
      - If user logged in: find cart for user_id, else create one linked to user_id.
      - If not logged in: use session['cart_key'] to find cart; create if needed.
    """
    # logged in user
    if getattr(current_user, "is_authenticated", False):
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if cart:
            return cart
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
        return cart

    # guest: use session_key stored in session cookie
    key = session.get("cart_key")
    if key:
        cart = Cart.query.filter_by(session_key=key).first()
        if cart:
            return cart

    # create new guest cart and save key to session
    key = _make_session_key()
    session["cart_key"] = key
    cart = Cart(session_key=key)
    db.session.add(cart)
    db.session.commit()
    return cart
