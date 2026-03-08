from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Provider
provider_bp = Blueprint('provider', __name__, url_prefix='/provider')

@provider_bp.route('/')
def index():
    providers = Provider.query.all()
    return render_template('provider/index.html', providers=providers)

@provider_bp.route('/create', methods=['GET','POST'])
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        p = Provider(provider_name=name, provider_address=address)
        db.session.add(p); db.session.commit(); flash('Provider created','success'); return redirect(url_for('provider.index'))
    return render_template('provider/create.html')
