# app.py — verbose debug version (replace your file with this exact content)

import os
import pprint
import logging
import sys
from datetime import datetime
from flask import Flask, render_template, current_app, redirect, url_for, request
from config import Config
from extensions import db, login_manager
from flask_wtf import CSRFProtect

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)
    app.config['SQLALCHEMY_ECHO'] = True  # Enable SQL query logging
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Unknown')
    app.logger.info("=" * 60)
    app.logger.info("DATABASE CONFIGURATION")
    app.logger.info("=" * 60)
    app.logger.info("DB URL (for SQLAlchemy): %s", db_uri)
    if 'sqlite' in db_uri.lower():
        app.logger.warning("⚠️  WARNING: Using SQLite! Set DATABASE_URL to use PostgreSQL!")
        app.logger.warning("   Example: $env:DATABASE_URL='postgresql://user:pass@localhost:5432/rims_db'")
    elif 'postgresql' in db_uri.lower():
        app.logger.info("✓ Using PostgreSQL database")
    app.logger.info("=" * 60)
    
# reduce SQLAlchemy engine logs to WARNING (only show warnings/errors)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

    # initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    CSRFProtect(app)

    # import models and create tables (dev convenience)
    with app.app_context():
        try:
            import models
            app.logger.info("Imported models module successfully.")
        except Exception as e:
            app.logger.exception("Failed to import models: %s", e)
            # still continue so we can see other errors

        try:
            db.create_all()
            app.logger.info("db.create_all() executed")
        except Exception:
            app.logger.exception("db.create_all() failed (ok for production if using migrations)")

    # register login loader
    try:
        from models import User
        @login_manager.user_loader
        def load_user(user_id):
            try:
                return User.query.get(int(user_id))
            except Exception:
                app.logger.exception("load_user failed for id: %s", user_id)
                return None
        app.logger.info("Registered login_user loader.")
    except Exception:
        app.logger.exception("Could not import User for login loader.")

    # debug route early so it's always present
    @app.route('/debug/cart-test', methods=['POST'])
    def debug_cart_test():
        app.logger.info("DEBUG /debug/cart-test - headers: %s", dict(request.headers))
        app.logger.info("DEBUG /debug/cart-test - form: %s", request.form)
        app.logger.info("DEBUG /debug/cart-test - json: %s", request.get_json(silent=True))
        return ('', 204)

    # list of blueprint import specs (module, varname)
    blueprints_to_load = [
        ('blueprints.auth', 'auth_bp'),
        ('blueprints.catalog', 'catalog_bp'),
        ('blueprints.product', 'product_bp'),
        ('blueprints.cart', 'cart_bp'),
        ('blueprints.payment', 'payment_bp'),
        ('blueprints.provider', 'provider_bp'),
        ('blueprints.warehouse', 'warehouse_bp'),
        ('blueprints.inventory', 'inventory_bp'),
        ('blueprints.order', 'order_bp'),
        ('blueprints.transfer', 'transfer_bp'),
        ('blueprints.delivery', 'delivery_bp'),
        ('blueprints.admin_dashboard', 'admin_bp'),
        ('blueprints.user_dashboard', 'user_bp'),
        ('blueprints.user_management', 'user_management_bp'),
        ('blueprints.reports', 'reports_bp'),
    ]

    imported_blueprints = {}
    for module_name, varname in blueprints_to_load:
        try:
            mod = __import__(module_name, fromlist=[varname])
            bp = getattr(mod, varname)
            imported_blueprints[module_name] = bp
            app.logger.info("Imported blueprint %s.%s", module_name, varname)
        except Exception:
            app.logger.exception("Failed to import blueprint %s (expecting %s inside).", module_name, varname)

    # Register blueprints and catch registration errors
    for module_name, bp in list(imported_blueprints.items()):
        try:
            app.register_blueprint(bp)
            app.logger.info("Registered blueprint from %s", module_name)
        except Exception:
            app.logger.exception("Failed to register blueprint from %s", module_name)

    # INDEX ROUTE - Show splash page first
    @app.route('/')
    def index():
        """Show splash/landing page when server starts."""
        return render_template('splash.html')
    
    # HOME ROUTE - After splash, show home or redirect based on auth
    @app.route('/home')
    def home():
        """Home page after splash - shows products for logged in users, register for guests."""
        from flask_login import current_user
        
        # If user is not logged in, send them to registration
        if not getattr(current_user, "is_authenticated", False):
            try:
                return redirect(url_for('auth.register'))
            except Exception:
                return "Auth register route not available. Check logs.", 503

        # logged-in users see the home products + stats
        try:
            from models import Product, Inventory
        except Exception:
            app.logger.exception("Couldn't import Product/Inventory in home route.")
            return "Server error: models not available.", 500

        total_products = 0
        low_stock_count = 0
        preview_products = []

        try:
            total_products = Product.query.count()
        except Exception:
            app.logger.exception("Counting products failed.")
            total_products = 0

        try:
            if hasattr(Inventory, "quantity_available"):
                low_stock_count = Inventory.query.filter(Inventory.quantity_available <= 5).count()
            else:
                if hasattr(Product, "quantity"):
                    low_stock_count = Product.query.filter(Product.quantity <= 5).count()
                else:
                    low_stock_count = 0
        except Exception:
            app.logger.exception("Calculating low_stock_count failed.")
            low_stock_count = 0

        try:
            preview_products = Product.query.order_by(Product.product_id.desc()).limit(8).all()
        except Exception:
            app.logger.exception("Querying preview products failed.")
            preview_products = []

        return render_template(
            "home.html",
            products=preview_products,
            total_products=total_products,
            low_stock_count=low_stock_count,
            now=datetime.utcnow
        )

    # Diagnostic: print blueprints and endpoints on startup
    with app.app_context():
        app.logger.info("Registered blueprints keys: %s", list(app.blueprints.keys()))
        app.logger.info("URL map endpoints:")
        for r in sorted(app.url_map.iter_rules(), key=lambda x: x.rule):
            app.logger.info("  %-30s -> %s", r.endpoint, r.rule)

    return app


if __name__ == '__main__':
    app = create_app()

    print("DEBUG: type(app) =", type(app))
    if isinstance(app, (tuple, list)):
        print("DEBUG: create_app returned a tuple/list. Contents:")
        pprint.pprint(app)
        app = app[0]

    if isinstance(app, dict):
        print("DEBUG: create_app returned a dict. Keys:", list(app.keys()))
        if 'app' in app and hasattr(app['app'], 'run'):
            app = app['app']
        else:
            print("ERROR: create_app returned a dict that doesn't contain a Flask app under key 'app'.")
            sys.exit(1)

    if not hasattr(app, "run"):
        print("ERROR: Final object assigned to 'app' has no '.run' method (not a Flask app).")
        print("Type:", type(app))
        pprint.pprint(app)
        raise RuntimeError("create_app() did not return a Flask application object. Fix create_app() and try again.")

    print("=== Flask URL map ===")
    print(app.url_map)
    app.run(debug=False,use_reloader=False)
