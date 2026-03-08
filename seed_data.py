import os
from app import create_app
from extensions import db
from models import Category, Product, Warehouse, Inventory, User, Payment
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

app = create_app()
with app.app_context():
    # categories
    if not Category.query.filter_by(name='Electronics').first():
        c1 = Category(name='Electronics', description='Phones, laptops')
        c2 = Category(name='Home Appliances', description='Home essentials')
        db.session.add_all([c1,c2]); db.session.commit()
    else:
        c1 = Category.query.filter_by(name='Electronics').first()
        c2 = Category.query.filter_by(name='Home Appliances').first()

    # products (use bundled SVG placeholders)
    if not Product.query.filter_by(product_name='Sample Phone').first():
        p1 = Product(product_name='Sample Phone', product_description='Demo phone', unit_price=1345.00, quantity=50, category_id=c1.category_id, image_filename='sample_phone.svg')
        p2 = Product(product_name='Sample Laptop', product_description='Demo laptop', unit_price=100000.00, quantity=5, category_id=c1.category_id, image_filename='sample_laptop.svg')
        db.session.add_all([p1,p2]); db.session.commit()
    else:
        p1 = Product.query.filter_by(product_name='Sample Phone').first()
        p2 = Product.query.filter_by(product_name='Sample Laptop').first()

    # ensure products reference the sample svg files we added in static/uploads
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    # set filenames to the svg placeholders if missing or file absent
    for prod, fname in ((p1, 'sample_phone.svg'), (p2, 'sample_laptop.svg')):
        target = os.path.join(upload_folder, fname)
        if not prod.image_filename or prod.image_filename != fname or not os.path.exists(target):
            prod.image_filename = fname
    db.session.commit()

    # warehouse
    if not Warehouse.query.filter_by(warehouse_name='Main Warehouse').first():
        w = Warehouse(warehouse_name='Main Warehouse'); db.session.add(w); db.session.commit()
    else:
        w = Warehouse.query.filter_by(warehouse_name='Main Warehouse').first()

    # inventory
    if not Inventory.query.filter_by(product_id=p1.product_id, warehouse_id=w.warehouse_id).first():
        inv1 = Inventory(product_id=p1.product_id, warehouse_id=w.warehouse_id, quantity_available=50, minimum_stock_level=5, reorder_point=10)
        inv2 = Inventory(product_id=p2.product_id, warehouse_id=w.warehouse_id, quantity_available=5, minimum_stock_level=2, reorder_point=3)
        db.session.add_all([inv1,inv2]); db.session.commit()

    # admin user
    if not User.query.filter_by(username='admin').first():
        u = User(username='admin', email='admin@example.com', password_hash=generate_password_hash('admin123'), role='admin')
        db.session.add(u); db.session.commit()

    # sample payment
    pay = Payment(order_id=None, amount=1345.00, method='mock', status='paid', created_at=datetime.utcnow() - timedelta(days=10))
    db.session.add(pay); db.session.commit()

    print('Seed complete')
