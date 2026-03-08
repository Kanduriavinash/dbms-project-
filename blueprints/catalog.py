from flask import Blueprint, render_template
from models import Product, Inventory, Warehouse
catalog_bp = Blueprint('catalog', __name__, url_prefix='/catalog')

@catalog_bp.route('/')
def catalog():
    products = Product.query.all()
    return render_template('catalog.html', products=products)

@catalog_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product details page for users."""
    product = Product.query.get_or_404(product_id)
    
    # Get inventory information
    inventory_items = Inventory.query.filter_by(product_id=product_id).all()
    total_stock = sum(item.quantity_available for item in inventory_items)
    
    # Check if product is in stock
    is_in_stock = total_stock > 0 or (product.quantity and product.quantity > 0)
    
    return render_template(
        'catalog/product_detail.html',
        product=product,
        inventory_items=inventory_items,
        total_stock=total_stock,
        is_in_stock=is_in_stock
    )
