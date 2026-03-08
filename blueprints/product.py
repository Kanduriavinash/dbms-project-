from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from extensions import db
from models import Product, Category
from werkzeug.utils import secure_filename
import os
product_bp = Blueprint('product', __name__, url_prefix='/product')
ALLOWED = {'png','jpg','jpeg','gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED

@product_bp.route('/')
def index():
    products = Product.query.all()
    return render_template('product/index.html', products=products)

@product_bp.route('/create', methods=['GET','POST'])
def create():
    categories = Category.query.all()
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            if not name:
                flash('Product name is required!', 'danger')
                return redirect(url_for('product.create'))
            
            price = request.form.get('price') or 0
            try:
                price = float(price)
                if price < 0:
                    price = 0
            except (ValueError, TypeError):
                price = 0
            
            qty = request.form.get('quantity') or 0
            try:
                qty = int(qty)
                if qty < 0:
                    qty = 0
            except (ValueError, TypeError):
                qty = 0
            
            desc = request.form.get('description', '').strip()
            cat_id = request.form.get('category_id') or None
            if cat_id:
                try:
                    cat_id = int(cat_id)
                except (ValueError, TypeError):
                    cat_id = None
            
            image = request.files.get('image')
            filename = None
            if image and image.filename and allowed_file(image.filename):
                fname = secure_filename(image.filename)
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                image.save(os.path.join(upload_folder, fname))
                filename = fname
            
            p = Product(
                product_name=name,
                unit_price=price,
                quantity=qty,
                product_description=desc,
                image_filename=filename,
                category_id=cat_id
            )
            db.session.add(p)
            db.session.commit()
            current_app.logger.info("Product created: %s (ID: %s)", name, p.product_id)
            flash('Product created successfully!', 'success')
            return redirect(url_for('product.index'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception("Error creating product: %s", e)
            flash(f'Error creating product: {str(e)}', 'danger')
            return redirect(url_for('product.create'))
    return render_template('product/create.html', categories=categories)

@product_bp.route('/edit/<int:product_id>', methods=['GET','POST'])
def edit(product_id):
    p = Product.query.get_or_404(product_id)
    categories = Category.query.all()
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            if name:
                p.product_name = name
            
            price = request.form.get('price')
            if price is not None:
                try:
                    p.unit_price = float(price)
                    if p.unit_price < 0:
                        p.unit_price = 0
                except (ValueError, TypeError):
                    pass
            
            qty = request.form.get('quantity')
            if qty is not None:
                try:
                    p.quantity = int(qty)
                    if p.quantity < 0:
                        p.quantity = 0
                except (ValueError, TypeError):
                    pass
            
            desc = request.form.get('description', '').strip()
            if desc is not None:
                p.product_description = desc
            
            cat_id = request.form.get('category_id')
            if cat_id is not None:
                try:
                    p.category_id = int(cat_id) if cat_id else None
                except (ValueError, TypeError):
                    pass
            
            image = request.files.get('image')
            if image and image.filename and allowed_file(image.filename):
                fname = secure_filename(image.filename)
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                image.save(os.path.join(upload_folder, fname))
                p.image_filename = fname
            
            db.session.commit()
            current_app.logger.info("Product updated: %s (ID: %s)", p.product_name, product_id)
            flash('Product updated successfully!', 'success')
            return redirect(url_for('product.index'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception("Error updating product: %s", e)
            flash(f'Error updating product: {str(e)}', 'danger')
            return redirect(url_for('product.edit', product_id=product_id))
    return render_template('product/edit.html', p=p, categories=categories)

@product_bp.route('/delete/<int:product_id>', methods=['POST'])
def delete(product_id):
    try:
        p = Product.query.get_or_404(product_id)
        product_name = p.product_name
        
        # Check if product is in any orders
        from models import OrderDetail
        order_details = OrderDetail.query.filter_by(product_id=product_id).first()
        if order_details:
            flash('Cannot delete product that has been ordered. Archive it instead.', 'danger')
            return redirect(url_for('product.index'))
        
        db.session.delete(p)
        db.session.commit()
        current_app.logger.info("Product deleted: %s (ID: %s)", product_name, product_id)
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Error deleting product: %s", e)
        flash(f'Error deleting product: {str(e)}', 'danger')
    return redirect(url_for('product.index'))
