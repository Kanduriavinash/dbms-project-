from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from extensions import db
from models import Warehouse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
warehouse_bp = Blueprint('warehouse', __name__, url_prefix='/warehouse')

@warehouse_bp.route('/')
def index():
    warehouses = Warehouse.query.order_by(Warehouse.created_at.desc()).all()
    return render_template('warehouse/index.html', warehouses=warehouses)

@warehouse_bp.route('/create', methods=['GET','POST'])
def create():
    if request.method == 'POST':
        try:
            # Get form data
            warehouse_name = request.form.get('warehouse_name', '').strip()
            capacity = request.form.get('capacity')
            is_refrigerated = request.form.get('is_refrigerated') == '1'
            
            # Validate required fields
            if not warehouse_name:
                flash('Warehouse name is required!', 'danger')
                return redirect(url_for('warehouse.create'))
            
            # Convert capacity to integer if provided
            capacity_int = None
            if capacity:
                try:
                    capacity_int = int(capacity)
                    if capacity_int < 0:
                        capacity_int = None
                except ValueError:
                    capacity_int = None
            
            # Create warehouse with all fields
            warehouse = Warehouse(
                warehouse_name=warehouse_name,
                is_refrigerated=is_refrigerated,
                capacity=capacity_int,
                created_at=datetime.utcnow()
            )
            
            # Save to database
            db.session.add(warehouse)
            
            # Log database info before commit
            db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Unknown')
            logger.info("=" * 60)
            logger.info("SAVING WAREHOUSE TO DATABASE")
            logger.info("=" * 60)
            logger.info(f"Database URI: {db_uri}")
            if 'sqlite' in db_uri.lower():
                logger.error("⚠️  WARNING: Using SQLite! Data will NOT save to PostgreSQL!")
                logger.error("   Set DATABASE_URL environment variable to use PostgreSQL!")
            logger.info(f"Creating warehouse: name={warehouse_name}, capacity={capacity_int}, refrigerated={is_refrigerated}")
            
            # Flush to get the ID before commit
            db.session.flush()
            logger.info(f"Warehouse ID after flush: {warehouse.warehouse_id}")
            
            db.session.commit()
            logger.info("✓ Commit successful!")
            
            # Verify it was saved
            saved_warehouse = Warehouse.query.filter_by(warehouse_name=warehouse_name).first()
            if saved_warehouse:
                logger.info(f"Warehouse saved successfully! ID: {saved_warehouse.warehouse_id}")
                flash(f'Warehouse "{warehouse_name}" created successfully! (ID: {saved_warehouse.warehouse_id})', 'success')
            else:
                logger.error("Warehouse was not found after commit!")
                flash('Warehouse created but could not verify. Please check database.', 'warning')
            
            return redirect(url_for('warehouse.index'))
            
        except Exception as e:
            db.session.rollback()
            logger.exception(f"Error creating warehouse: {str(e)}")
            flash(f'Error creating warehouse: {str(e)}', 'danger')
            return redirect(url_for('warehouse.create'))
    
    return render_template('warehouse/create.html')

@warehouse_bp.route('/edit/<int:warehouse_id>', methods=['GET','POST'])
def edit(warehouse_id):
    warehouse = Warehouse.query.get_or_404(warehouse_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            warehouse_name = request.form.get('warehouse_name', '').strip()
            capacity = request.form.get('capacity')
            is_refrigerated = request.form.get('is_refrigerated') == '1'
            
            # Validate required fields
            if not warehouse_name:
                flash('Warehouse name is required!', 'danger')
                return redirect(url_for('warehouse.edit', warehouse_id=warehouse_id))
            
            # Convert capacity to integer if provided
            capacity_int = None
            if capacity:
                try:
                    capacity_int = int(capacity)
                    if capacity_int < 0:
                        capacity_int = None
                except ValueError:
                    capacity_int = None
            
            # Update warehouse fields
            warehouse.warehouse_name = warehouse_name
            warehouse.is_refrigerated = is_refrigerated
            warehouse.capacity = capacity_int
            
            # Save to database
            db.session.commit()
            
            flash(f'Warehouse "{warehouse_name}" updated successfully!', 'success')
            return redirect(url_for('warehouse.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating warehouse: {str(e)}', 'danger')
            return redirect(url_for('warehouse.edit', warehouse_id=warehouse_id))
    
    return render_template('warehouse/edit.html', warehouse=warehouse)

@warehouse_bp.route('/delete/<int:warehouse_id>', methods=['POST'])
def delete(warehouse_id):
    warehouse = Warehouse.query.get_or_404(warehouse_id)
    warehouse_name = warehouse.warehouse_name
    
    try:
        db.session.delete(warehouse)
        db.session.commit()
        flash(f'Warehouse "{warehouse_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting warehouse: {str(e)}', 'danger')
    
    return redirect(url_for('warehouse.index'))
