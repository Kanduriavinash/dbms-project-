from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Order, OrderDetail, Product, User
order_bp = Blueprint('order', __name__, url_prefix='/order')

def admin_required(f):
    """Decorator to require admin role."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Admin access required.", "danger")
            return redirect(url_for('auth.login_admin'))
        return f(*args, **kwargs)
    return decorated_function

@order_bp.route('/')
@login_required
@admin_required
def index():
    """View all orders (admin only)."""
    orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template('order/index.html', orders=orders)

@order_bp.route('/<int:order_id>')
@login_required
def view(order_id):
    """View order details."""
    order = Order.query.get_or_404(order_id)
    
    # Check access: admin can see all, users can only see their own
    if current_user.role != 'admin' and order.customer_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for('user_dashboard.orders'))
    
    customer = User.query.get(order.customer_id) if order.customer_id else None
    return render_template('order/view.html', order=order, customer=customer)

@order_bp.route('/<int:order_id>/update_status', methods=['POST'])
@login_required
@admin_required
def update_status(order_id):
    """Update order status (admin only)."""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    valid_statuses = ['new', 'pending', 'processing', 'shipped', 'delivered', 'cancelled']
    if new_status and new_status in valid_statuses:
        order.status = new_status
        db.session.commit()
        flash(f"Order status updated to {new_status}.", "success")
    else:
        flash("Invalid status.", "danger")
    
    return redirect(url_for('order.view', order_id=order_id))

@order_bp.route('/create', methods=['GET','POST'])
@login_required
@admin_required
def create():
    """Create order manually (admin only)."""
    products = Product.query.all()
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        order = Order(customer_id=int(customer_id) if customer_id else None)
        db.session.add(order)
        db.session.flush()
        pid = request.form.get('product_id')
        qty = int(request.form.get('quantity', 1))
        product = Product.query.get(pid)
        if product:
            od = OrderDetail(
                order_id=order.order_id,
                product_id=pid,
                product_name=product.product_name,
                order_quantity=qty,
                unit_price=product.unit_price
            )
            db.session.add(od)
            db.session.commit()
            flash('Order created', 'success')
            return redirect(url_for('order.index'))
    return render_template('order/create.html', products=products)
