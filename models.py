\
from datetime import datetime
from extensions import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(20), default='customer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    product_description = db.Column(db.Text)
    unit_price = db.Column(db.Numeric(12,2), default=0)
    quantity = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=True)
    image_filename = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Warehouse(db.Model):
    __tablename__ = 'warehouse'
    warehouse_id = db.Column(db.Integer, primary_key=True)
    warehouse_name = db.Column(db.String(200), nullable=False)
    is_refrigerated = db.Column(db.Boolean, default=False)
    capacity = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    inventories = db.relationship('Inventory', backref='warehouse', lazy=True)

class Inventory(db.Model):
    __tablename__ = 'inventory'
    inventory_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.warehouse_id'), nullable=False)
    quantity_available = db.Column(db.Integer, nullable=False, default=0)
    minimum_stock_level = db.Column(db.Integer, nullable=True)
    reorder_point = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    product = db.relationship('Product', backref='inventories', lazy=True)

class Order(db.Model):
    __tablename__ = 'order_tbl'
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Numeric(14,2), default=0)
    status = db.Column(db.String(50), default='new')
    items = db.relationship('OrderDetail', backref='order', lazy=True)

class OrderDetail(db.Model):
    __tablename__ = 'order_detail'
    order_detail_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order_tbl.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    product_name = db.Column(db.String(200))
    order_quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(12,2), nullable=True)
    product = db.relationship('Product', backref='order_details', lazy=True)

class Payment(db.Model):
    __tablename__ = 'payment'
    payment_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order_tbl.order_id'), nullable=True)
    amount = db.Column(db.Numeric(14,2), nullable=False, default=0)
    method = db.Column(db.String(80))
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Cart(db.Model):
    __tablename__ = 'cart'
    cart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    session_key = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items = db.relationship('CartItem', backref='cart', cascade='all, delete-orphan', lazy=True)

class CartItem(db.Model):
    __tablename__ = 'cart_item'
    cart_item_id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.cart_id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(12,2), nullable=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref='cart_items', lazy=True)

# -----------------------
# Missing helper models (add these to the end of models.py)
# -----------------------

class Provider(db.Model):
    __tablename__ = 'provider'
    provider_id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(200), nullable=False)
    provider_address = db.Column(db.String(500))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # optional: provider -> orders
    # orders = db.relationship('Order', backref='provider', lazy=True)

class Customer(db.Model):
    __tablename__ = 'customer'
    customer_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_address = db.Column(db.String(500))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # optional relationships:
    # orders = db.relationship('Order', backref='customer', lazy=True)
    # deliveries = db.relationship('Delivery', backref='customer', lazy=True)

class Delivery(db.Model):
    __tablename__ = 'delivery'
    delivery_id = db.Column(db.Integer, primary_key=True)
    sales_date = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=True)
    status = db.Column(db.String(50), default='pending')
    # details relationship
    details = db.relationship('DeliveryDetail', backref='delivery', lazy=True)
    # customer relationship
    customer = db.relationship('Customer', backref='deliveries', lazy=True)

class DeliveryDetail(db.Model):
    __tablename__ = 'delivery_detail'
    delivery_detail_id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.delivery_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.warehouse_id'), nullable=True)
    delivery_quantity = db.Column(db.Integer, nullable=False, default=1)
    expected_date = db.Column(db.DateTime, nullable=True)
    actual_date = db.Column(db.DateTime, nullable=True)

class Transfer(db.Model):
    __tablename__ = 'transfer'
    transfer_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    transfer_quantity = db.Column(db.Integer, nullable=False, default=0)
    sent_date = db.Column(db.DateTime, nullable=True)
    received_date = db.Column(db.DateTime, nullable=True)
    from_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.warehouse_id'), nullable=True)
    to_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.warehouse_id'), nullable=True)
