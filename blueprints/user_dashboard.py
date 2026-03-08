# blueprints/user_dashboard.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Order, OrderDetail, User
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

user_bp = Blueprint('user_dashboard', __name__, url_prefix='/user')

@user_bp.route('/orders')
@login_required
def orders():
    orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('user/orders.html', orders=orders)

@user_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.customer_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for('user_dashboard.orders'))
    return render_template('user/order_detail.html', order=order)

@user_bp.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html', user=current_user)

@user_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.email = request.form.get('email', current_user.email)
        password = request.form.get('password')
        if password:
            current_user.password_hash = generate_password_hash(password)
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('user_dashboard.profile'))
    return render_template('user/edit_profile.html', user=current_user)

@user_bp.route('/addresses')
@login_required
def addresses():
    return render_template('user/addresses.html')

@user_bp.route('/dashboard')
@login_required
def dashboard():
    orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.order_date.desc()).limit(5).all()
    total_orders = Order.query.filter_by(customer_id=current_user.id).count()
    return render_template('user/dashboard.html', orders=orders, total_orders=total_orders, user=current_user)
