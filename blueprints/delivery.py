from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Delivery, DeliveryDetail, Product, Warehouse, Customer
from sqlalchemy.orm import joinedload

delivery_bp = Blueprint('delivery', __name__, url_prefix='/delivery')

@delivery_bp.route('/')
def index():
    items = Delivery.query.options(joinedload(Delivery.customer)).order_by(Delivery.sales_date.desc()).all()
    return render_template('delivery/index.html', items=items)

@delivery_bp.route('/create', methods=['GET','POST'])
def create():
    products = Product.query.all(); warehouses = Warehouse.query.all(); customers = Customer.query.all()
    if request.method == 'POST':
        try:
            # Get and validate customer_id - it's required
            customer_id = request.form.get('customer_id', '').strip()
            if not customer_id:
                flash('Customer is required. Please select a customer.', 'danger')
                return render_template('delivery/create.html', products=products, warehouses=warehouses, customers=customers)
            
            # Create delivery with customer_id
            d = Delivery()
            d.customer_id = int(customer_id)
            db.session.add(d)
            db.session.flush()
            
            # Get delivery details
            pid = request.form.get('product_id')
            qty = int(request.form.get('quantity', 1))
            wh = request.form.get('warehouse_id')
            
            # Create delivery detail
            dd = DeliveryDetail(delivery_id=d.delivery_id, product_id=pid, delivery_quantity=qty, warehouse_id=wh)
            db.session.add(dd)
            db.session.commit()
            
            flash(f'Delivery #{d.delivery_id} created successfully for Customer ID: {d.customer_id}', 'success')
            return redirect(url_for('delivery.index'))
        except ValueError as e:
            db.session.rollback()
            flash(f'Invalid input: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating delivery: {str(e)}', 'danger')
    
    return render_template('delivery/create.html', products=products, warehouses=warehouses, customers=customers)

@delivery_bp.route('/<int:delivery_id>/edit', methods=['GET', 'POST'])
def edit(delivery_id):
    """Edit delivery to assign/update customer."""
    delivery = Delivery.query.get_or_404(delivery_id)
    customers = Customer.query.all()
    
    if request.method == 'POST':
        try:
            customer_id = request.form.get('customer_id', '').strip()
            if customer_id:
                delivery.customer_id = int(customer_id)
                db.session.commit()
                flash(f'Delivery #{delivery_id} updated with Customer ID: {delivery.customer_id}', 'success')
            else:
                flash('Please select a customer.', 'danger')
                return render_template('delivery/edit.html', delivery=delivery, customers=customers)
            
            return redirect(url_for('delivery.index'))
        except ValueError as e:
            db.session.rollback()
            flash(f'Invalid input: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating delivery: {str(e)}', 'danger')
    
    return render_template('delivery/edit.html', delivery=delivery, customers=customers)

@delivery_bp.route('/<int:delivery_id>/update_status', methods=['POST'])
def update_status(delivery_id):
    """Update delivery status (pending -> completed)."""
    delivery = Delivery.query.get_or_404(delivery_id)
    new_status = request.form.get('status', 'completed')
    
    try:
        delivery.status = new_status
        db.session.commit()
        flash(f'Delivery #{delivery_id} status updated to {new_status}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating delivery status: {str(e)}', 'danger')
    
    return redirect(url_for('delivery.index'))
