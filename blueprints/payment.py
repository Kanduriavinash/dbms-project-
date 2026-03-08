# blueprints/payment.py
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Order, Cart, CartItem, Payment, Product  # Order-line model detection done at runtime
from flask_login import current_user
from datetime import datetime
from sqlalchemy import text

logger = logging.getLogger(__name__)

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')


@payment_bp.route('/checkout', methods=['GET', 'POST'])
def checkout_payment():
    """
    Checkout endpoint (GET shows checkout, POST performs mock payment → creates Order, Order-lines, Payment).
    This function detects which order-line ORM model exists at runtime (inside app context) and uses it.
    """
    # locate cart for current user
    cart = None
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id).first()
    else:
        flash("Please log in to checkout.", "warning")
        return redirect(url_for('auth.login'))

    if not cart or not cart.items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('cart.index'))

    items = cart.items
    total = sum(float(it.unit_price or 0) * (it.quantity or 0) for it in items)

    if request.method == 'GET':
        return render_template('payment/checkout.html', items=items, total=total, cart=cart)

    # POST: perform a (mock) payment and create order + order-lines + payment record
    # Detect a suitable Order-line model (common names: OrderItem, OrderDetail)
    OrderLineModel = None
    try:
        # try common class names (import at runtime so app context exists)
        from models import OrderItem  # preferred
        OrderLineModel = OrderItem
        logger.info("Using OrderItem model for order lines.")
    except Exception:
        try:
            from models import OrderDetail
            OrderLineModel = OrderDetail
            logger.info("Using OrderDetail model for order lines.")
        except Exception:
            OrderLineModel = None
            logger.info("No OrderItem/OrderDetail model found; will fallback to raw SQL if needed.")

    try:
        # Validate stock before creating order
        from models import Inventory
        for it in items:
            product = Product.query.get(it.product_id)
            if not product:
                flash(f"Product {it.product_id} not found.", "danger")
                return redirect(url_for('cart.index'))
            
            # Check product quantity
            if hasattr(product, 'quantity') and product.quantity is not None:
                if product.quantity < it.quantity:
                    flash(f"Insufficient stock for {product.product_name}. Available: {product.quantity}, Requested: {it.quantity}", "danger")
                    return redirect(url_for('cart.index'))
            
            # Check inventory if exists
            inventory = Inventory.query.filter_by(product_id=it.product_id).first()
            if inventory and inventory.quantity_available < it.quantity:
                flash(f"Insufficient inventory for {product.product_name}. Available: {inventory.quantity_available}, Requested: {it.quantity}", "danger")
                return redirect(url_for('cart.index'))

        order = Order(
            customer_id=current_user.id if current_user.is_authenticated else None,
            order_date=datetime.utcnow(),
            total_amount=total,
            status='paid'
        )
        db.session.add(order)
        db.session.flush()  # to get order.order_id

        # create order lines and update inventory
        for it in items:
            product = Product.query.get(it.product_id)
            
            # Create order detail
            if OrderLineModel is not None:
                # Create using ORM model
                try:
                    ol = OrderLineModel(
                        order_id=order.order_id,
                        product_id=it.product_id,
                        order_quantity=it.quantity,
                        unit_price=it.unit_price,
                        product_name=product.product_name if product else None
                    )
                    db.session.add(ol)
                except Exception as e:
                    logger.exception("ORM order-line insert failed; switching to raw SQL fallback. Error: %s", e)
                    OrderLineModel = None
            
            if OrderLineModel is None:
                # Raw SQL fallback
                try:
                    sql = text("INSERT INTO order_detail (order_id, product_id, order_quantity, unit_price, product_name) "
                               "VALUES (:order_id, :product_id, :qty, :unit_price, :product_name)")
                    db.session.execute(sql, {
                        "order_id": order.order_id,
                        "product_id": it.product_id,
                        "qty": it.quantity,
                        "unit_price": float(it.unit_price),
                        "product_name": product.product_name if product else None
                    })
                except Exception as e:
                    logger.exception("Raw SQL insert into order_detail failed: %s", e)
                    raise  # Re-raise to trigger rollback

            # Update product quantity
            if product:
                if hasattr(product, 'quantity') and product.quantity is not None:
                    product.quantity = (product.quantity or 0) - it.quantity
                    if product.quantity < 0:
                        product.quantity = 0
            
            # Update inventory
            inventory = Inventory.query.filter_by(product_id=it.product_id).first()
            if inventory:
                inventory.quantity_available = (inventory.quantity_available or 0) - it.quantity
                if inventory.quantity_available < 0:
                    inventory.quantity_available = 0
                inventory.updated_at = datetime.utcnow()

        # create payment record
        payment = Payment(order_id=order.order_id, amount=total, method='mock', status='completed', created_at=datetime.utcnow())
        db.session.add(payment)

        # remove cart items and cart
        for it in items:
            db.session.delete(it)
        if cart:
            db.session.delete(cart)

        db.session.commit()
        logger.info("Order %s created successfully with payment %s", order.order_id, payment.payment_id)
        flash("Payment successful and order created.", "success")

        if current_user.is_authenticated:
            return redirect(url_for('payment.receipt', order_id=order.order_id))
        return redirect(url_for('catalog.catalog'))

    except Exception as exc:
        logger.exception("Checkout failed: %s", exc)
        db.session.rollback()
        flash("Payment failed. Try again.", "danger")
        return redirect(url_for('cart.index'))

@payment_bp.route('/receipt/<int:order_id>')
def receipt(order_id):
    """Show payment receipt for an order."""
    order = Order.query.get_or_404(order_id)
    payment = Payment.query.filter_by(order_id=order_id).first()
    
    # Check if user has access to this order
    if current_user.is_authenticated:
        if order.customer_id != current_user.id and current_user.role != 'admin':
            flash("Access denied.", "danger")
            return redirect(url_for('user_dashboard.orders'))
    
    return render_template('payment/receipt.html', order=order, payment=payment)
