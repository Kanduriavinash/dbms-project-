"""
Reports and Analytics Blueprint for Admin
Provides sales reports, inventory reports, and activity logs
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Order, Payment, Product, Inventory, User, OrderDetail
from datetime import datetime, timedelta
from sqlalchemy import func, extract

reports_bp = Blueprint('reports', __name__, url_prefix='/admin/reports')

def admin_required(f):
    """Decorator to require admin role."""
    from functools import wraps
    from flask import redirect, url_for, flash
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Admin access required.", "danger")
            return redirect(url_for('auth.login_admin'))
        return f(*args, **kwargs)
    return decorated_function

@reports_bp.route('/')
@login_required
@admin_required
def index():
    """Reports dashboard."""
    return render_template('admin/reports/index.html')

@reports_bp.route('/sales')
@login_required
@admin_required
def sales_report():
    """Sales report with date range filtering."""
    # Get date range from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_date = datetime.utcnow() - timedelta(days=30)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date = datetime.utcnow()
    
    # Get sales data
    orders = Order.query.filter(
        Order.order_date >= start_date,
        Order.order_date <= end_date
    ).all()
    
    payments = Payment.query.filter(
        Payment.created_at >= start_date,
        Payment.created_at <= end_date,
        Payment.status.in_(['paid', 'completed'])
    ).all()
    
    total_revenue = sum(float(p.amount) for p in payments)
    total_orders = len(orders)
    total_items_sold = sum(sum(item.order_quantity for item in order.items) for order in orders)
    
    # Daily sales breakdown
    daily_sales = db.session.query(
        func.date(Order.order_date).label('date'),
        func.count(Order.order_id).label('order_count'),
        func.sum(Order.total_amount).label('revenue')
    ).filter(
        Order.order_date >= start_date,
        Order.order_date <= end_date
    ).group_by(func.date(Order.order_date)).all()
    
    return render_template(
        'admin/reports/sales.html',
        orders=orders,
        total_revenue=total_revenue,
        total_orders=total_orders,
        total_items_sold=total_items_sold,
        daily_sales=daily_sales,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )

@reports_bp.route('/inventory')
@login_required
@admin_required
def inventory_report():
    """Inventory movement and stock levels report."""
    # Low stock items
    low_stock = Inventory.query.filter(
        Inventory.reorder_point != None,
        Inventory.quantity_available <= Inventory.reorder_point
    ).all()
    
    # Out of stock items
    out_of_stock = Inventory.query.filter(
        Inventory.quantity_available == 0
    ).all()
    
    # All inventory with product info
    all_inventory = Inventory.query.join(Product).all()
    
    # Total inventory value
    total_value = sum(
        float(inv.product.unit_price or 0) * inv.quantity_available 
        for inv in all_inventory if inv.product
    )
    
    return render_template(
        'admin/reports/inventory.html',
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        all_inventory=all_inventory,
        total_value=total_value
    )

@reports_bp.route('/products')
@login_required
@admin_required
def products_report():
    """Product sales and performance report."""
    try:
        # Get top selling products (only products that have been ordered)
        top_products = db.session.query(
            Product.product_id,
            Product.product_name,
            func.coalesce(func.sum(OrderDetail.order_quantity), 0).label('total_sold'),
            func.coalesce(func.sum(OrderDetail.order_quantity * OrderDetail.unit_price), 0).label('revenue')
        ).outerjoin(
            OrderDetail, Product.product_id == OrderDetail.product_id
        ).group_by(
            Product.product_id, Product.product_name
        ).having(
            func.coalesce(func.sum(OrderDetail.order_quantity), 0) > 0
        ).order_by(
            func.coalesce(func.sum(OrderDetail.order_quantity), 0).desc()
        ).limit(10).all()
    except Exception as e:
        top_products = []
    
    try:
        # Products by category
        products_by_category = db.session.query(
            Product.category_id,
            func.count(Product.product_id).label('count')
        ).group_by(Product.category_id).all()
    except Exception as e:
        products_by_category = []
    
    return render_template(
        'admin/reports/products.html',
        top_products=top_products,
        products_by_category=products_by_category
    )

@reports_bp.route('/users')
@login_required
@admin_required
def users_report():
    """User activity and statistics report."""
    total_users = User.query.count()
    admin_count = User.query.filter_by(role='admin').count()
    customer_count = User.query.filter_by(role='customer').count()
    
    # Top customers by order count
    top_customers = db.session.query(
        User.id,
        User.username,
        User.email,
        func.count(Order.order_id).label('order_count'),
        func.sum(Order.total_amount).label('total_spent')
    ).join(
        Order, User.id == Order.customer_id
    ).group_by(
        User.id, User.username, User.email
    ).order_by(
        func.count(Order.order_id).desc()
    ).limit(10).all()
    
    # Recent registrations
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    return render_template(
        'admin/reports/users.html',
        total_users=total_users,
        admin_count=admin_count,
        customer_count=customer_count,
        top_customers=top_customers,
        recent_users=recent_users
    )

