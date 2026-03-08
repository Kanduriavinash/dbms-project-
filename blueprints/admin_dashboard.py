from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import Product, Inventory, Payment, Order, User, Warehouse, Provider
from extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func, or_, and_

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

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

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_products = Product.query.count()
    
    # Calculate low stock items - simple rule: quantity_available < 5
    # Count all inventory items where quantity_available is less than 5
    try:
        # Get all inventory items with quantity < 5
        low_stock_items = Inventory.query.filter(Inventory.quantity_available < 5).all()
        low_stock_q = len(low_stock_items)
        
        # Log for debugging (optional - can remove in production)
        current_app.logger.debug(f"Low stock calculation: Found {low_stock_q} items with quantity < 5")
        if low_stock_q > 0:
            current_app.logger.debug(f"Low stock items: {[(inv.inventory_id, inv.quantity_available, inv.product_id) for inv in low_stock_items[:5]]}")
    except Exception as e:
        current_app.logger.error(f"Error calculating low stock: {str(e)}")
        low_stock_q = 0
    
    now = datetime.utcnow()
    one_month_ago = now - timedelta(days=30)
    sales_sum = db.session.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).filter(
        Payment.created_at >= one_month_ago, 
        Payment.status.in_(['paid', 'completed'])
    ).scalar() or 0
    
    total_orders = Order.query.count()
    total_users = User.query.count()
    warehouses_count = Warehouse.query.count()
    providers_count = Provider.query.count()
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(10).all()
    
    return render_template(
        'admin/dashboard.html', 
        total_products=total_products, 
        low_stock=low_stock_q, 
        sales_sum=sales_sum,
        total_orders=total_orders,
        total_users=total_users,
        warehouses_count=warehouses_count,
        providers_count=providers_count,
        recent_orders=recent_orders
    )
