# blueprints/cart.py
from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify, flash, session
from flask_login import login_required, current_user
from extensions import db
from datetime import datetime
from models import Product, CartItem, Cart

cart_bp = Blueprint('cart', __name__, template_folder='templates', url_prefix='')

def get_or_create_cart():
    """Get or create a cart for the current user."""
    if not current_user.is_authenticated:
        return None
    
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    return cart

@cart_bp.route('/cart/')
@login_required
def index():
    """Show current user's cart."""
    cart = get_or_create_cart()
    items = cart.items if cart else []
    
    # Compute totals
    total = 0
    for item in items:
        try:
            price = float(item.unit_price) if item.unit_price else (float(item.product.unit_price) if item.product else 0)
            total += (item.quantity or 0) * price
        except Exception:
            pass
    
    return render_template('cart/cart.html', items=items, total=total, cart=cart)

@cart_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    """Add a product to the user's cart."""
    try:
        product_id_raw = request.form.get('product_id') or (request.json and request.json.get('product_id'))
        quantity_raw = request.form.get('quantity') or (request.json and request.json.get('quantity') or '1')

        if product_id_raw is None:
            current_app.logger.warning("add_to_cart called without product_id")
            return _respond_error("Missing product_id", ajax=request.is_json)

        try:
            product_id = int(product_id_raw)
        except (TypeError, ValueError):
            return _respond_error("Invalid product_id", ajax=request.is_json)

        try:
            quantity = int(quantity_raw)
            if quantity < 1:
                quantity = 1
        except (TypeError, ValueError):
            quantity = 1

        product = Product.query.get(product_id)
        if not product:
            return _respond_error("Product not found", ajax=request.is_json)

        # Check stock availability
        if hasattr(product, 'quantity') and product.quantity is not None:
            if product.quantity < quantity:
                return _respond_error("Requested quantity exceeds stock", ajax=request.is_json)

        # Get or create cart
        cart = get_or_create_cart()
        if not cart:
            return _respond_error("Unable to create cart", ajax=request.is_json)

        # Check if item already in cart -> update quantity
        cart_item = CartItem.query.filter_by(cart_id=cart.cart_id, product_id=product_id).first()
        unit_price = float(product.unit_price) if product.unit_price else 0
        
        if cart_item:
            cart_item.quantity = (cart_item.quantity or 0) + quantity
            cart_item.unit_price = unit_price
        else:
            cart_item = CartItem(
                cart_id=cart.cart_id,
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price
            )
            db.session.add(cart_item)

        db.session.commit()
        current_app.logger.info("User %s added product %s (qty %s) to cart", current_user.id, product_id, quantity)

        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=True, message="Added to cart", product_id=product_id, quantity=quantity)

        flash("Item added to cart!", "success")
        return redirect(url_for('cart.index'))

    except Exception:
        current_app.logger.exception("Add to cart failed")
        db.session.rollback()
        return _respond_error("Server error while adding to cart", ajax=request.is_json)

@cart_bp.route('/cart/remove/<int:cart_item_id>', methods=['POST'])
@login_required
def remove_item(cart_item_id):
    """Remove a cart item for the logged-in user."""
    try:
        cart = get_or_create_cart()
        if not cart:
            return _respond_error("Cart not found", ajax=request.is_json)
        
        item = CartItem.query.filter_by(cart_item_id=cart_item_id, cart_id=cart.cart_id).first()
        if not item:
            return _respond_error("Cart item not found", ajax=request.is_json)
        
        db.session.delete(item)
        db.session.commit()
        
        if request.is_json:
            return jsonify(success=True)
        flash("Item removed from cart.", "success")
        return redirect(url_for('cart.index'))
    except Exception:
        current_app.logger.exception("Failed to remove cart item %s", cart_item_id)
        db.session.rollback()
        return _respond_error("Server error while removing item", ajax=request.is_json)

@cart_bp.route('/cart/update/<int:cart_item_id>', methods=['POST'])
@login_required
def update_item(cart_item_id):
    """Update quantity of a cart item."""
    try:
        cart = get_or_create_cart()
        if not cart:
            return _respond_error("Cart not found", ajax=request.is_json)
        
        item = CartItem.query.filter_by(cart_item_id=cart_item_id, cart_id=cart.cart_id).first()
        if not item:
            return _respond_error("Cart item not found", ajax=request.is_json)
        
        quantity_raw = request.form.get('quantity') or (request.json and request.json.get('quantity'))
        if quantity_raw:
            try:
                quantity = int(quantity_raw)
                if quantity < 1:
                    quantity = 1
                item.quantity = quantity
                db.session.commit()
                
                if request.is_json:
                    return jsonify(success=True, quantity=quantity)
                flash("Cart updated.", "success")
            except (TypeError, ValueError):
                return _respond_error("Invalid quantity", ajax=request.is_json)
        
        return redirect(url_for('cart.index'))
    except Exception:
        current_app.logger.exception("Failed to update cart item %s", cart_item_id)
        db.session.rollback()
        return _respond_error("Server error while updating item", ajax=request.is_json)

def merge_guest_cart_into_user(user_id):
    """Merge guest cart (session-based) into user cart."""
    try:
        session_key = session.get('cart_session_key')
        if not session_key:
            return
        
        guest_cart = Cart.query.filter_by(session_key=session_key, user_id=None).first()
        if not guest_cart:
            return
        
        user_cart = Cart.query.filter_by(user_id=user_id).first()
        if not user_cart:
            user_cart = Cart(user_id=user_id)
            db.session.add(user_cart)
            db.session.flush()
        
        # Merge items
        for guest_item in guest_cart.items:
            existing = CartItem.query.filter_by(
                cart_id=user_cart.cart_id,
                product_id=guest_item.product_id
            ).first()
            
            if existing:
                existing.quantity = (existing.quantity or 0) + (guest_item.quantity or 0)
            else:
                new_item = CartItem(
                    cart_id=user_cart.cart_id,
                    product_id=guest_item.product_id,
                    quantity=guest_item.quantity,
                    unit_price=guest_item.unit_price
                )
                db.session.add(new_item)
        
        # Delete guest cart
        db.session.delete(guest_cart)
        db.session.commit()
        session.pop('cart_session_key', None)
    except Exception:
        current_app.logger.exception("Failed to merge guest cart for user %s", user_id)
        db.session.rollback()

def _respond_error(message, ajax=False, status_code=400):
    """Helper: return JSON for AJAX or a redirected flash for normal requests."""
    if ajax:
        resp = jsonify(success=False, message=message)
        resp.status_code = status_code
        return resp
    else:
        flash(message, 'danger')
        try:
            return redirect(url_for('catalog.catalog'))
        except Exception:
            return redirect(url_for('cart.index'))
