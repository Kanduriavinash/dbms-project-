# utils/cart_utils.py
from datetime import datetime
from extensions import db
from models import Cart

def get_or_create_cart_for_user(user_id=None, session_key=None):
    if user_id:
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(user_id=user_id, created_at=datetime.utcnow())
            db.session.add(cart)
            db.session.commit()
        return cart
    # use session_key when provided, or caller handles session_key creation
    if session_key:
        cart = Cart.query.filter_by(session_key=session_key).first()
        if not cart:
            cart = Cart(session_key=session_key, created_at=datetime.utcnow())
            db.session.add(cart)
            db.session.commit()
        return cart
    return None
