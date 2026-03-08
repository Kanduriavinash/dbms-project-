from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Transfer, Product, Warehouse
transfer_bp = Blueprint('transfer', __name__, url_prefix='/transfer')

@transfer_bp.route('/')
def index():
    items = Transfer.query.all()
    return render_template('transfer/index.html', items=items)

@transfer_bp.route('/create', methods=['GET','POST'])
def create():
    products = Product.query.all(); warehouses = Warehouse.query.all()
    if request.method == 'POST':
        pid = request.form.get('product_id'); q = int(request.form.get('quantity',1)); from_w = request.form.get('from_warehouse'); to_w = request.form.get('to_warehouse')
        t = Transfer(product_id=pid, transfer_quantity=q, from_warehouse_id=int(from_w) if from_w else None, to_warehouse_id=int(to_w) if to_w else None)
        db.session.add(t); db.session.commit(); flash('Transfer created','success'); return redirect(url_for('transfer.index'))
    return render_template('transfer/create.html', products=products, warehouses=warehouses)
