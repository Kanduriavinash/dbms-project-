"""
Setup retail_db PostgreSQL Database
Fully automatic - no prompts needed
"""
import os
import sys

# Database configuration
DB_CONFIG = {
    'user': 'postgres',
    'password': 'avinash',
    'host': 'localhost',
    'port': '5432',
    'database': 'retail_db'
}

ADMIN_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/postgres"
DB_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

print("=" * 70)
print("Setting up retail_db PostgreSQL Database")
print("=" * 70)
print(f"Database: {DB_CONFIG['database']}")
print(f"User: {DB_CONFIG['user']}")
print()

# Step 1: Create database
print("Step 1: Creating database...")
try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    conn = psycopg2.connect(ADMIN_URL)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['database'],))
    if cursor.fetchone():
        print("  Dropping existing database...")
        try:
            cursor.execute(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{DB_CONFIG['database']}' AND pid <> pg_backend_pid();")
        except: pass
        cursor.execute(f"DROP DATABASE {DB_CONFIG['database']};")
    cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']};")
    cursor.close()
    conn.close()
    print("  ✓ Database created")
except Exception as e:
    print(f"  ✗ Error: {e}")
    sys.exit(1)

# Step 2: Create tables
print("\nStep 2: Creating tables...")
os.environ['DATABASE_URL'] = DB_URL
try:
    from app import create_app
    from extensions import db
    import models
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        from sqlalchemy import inspect
        tables = inspect(db.engine).get_table_names()
        print(f"  ✓ Created {len(tables)} tables")
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Initial data
print("\nStep 3: Creating initial data...")
try:
    from app import create_app
    from extensions import db
    from models import User, Category
    from werkzeug.security import generate_password_hash
    app = create_app()
    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', email='admin@rims.com', password_hash=generate_password_hash('admin123'), role='admin'))
        if not Category.query.filter_by(name='Electronics').first():
            db.session.add_all([Category(name='Electronics'), Category(name='Home Appliances')])
        db.session.commit()
        print("  ✓ Admin user and categories created")
except Exception as e:
    print(f"  ✗ Error: {e}")
    sys.exit(1)

# Step 4: Verify
print("\nStep 4: Verifying...")
try:
    from app import create_app
    from extensions import db
    from models import Warehouse
    from datetime import datetime
    app = create_app()
    with app.app_context():
        test = Warehouse(warehouse_name="Test", is_refrigerated=True, capacity=1000, created_at=datetime.utcnow())
        db.session.add(test)
        db.session.commit()
        saved = Warehouse.query.filter_by(warehouse_name="Test").first()
        if saved:
            db.session.delete(saved)
            db.session.commit()
            print("  ✓ All operations working")
        else:
            print("  ✗ Failed")
            sys.exit(1)
except Exception as e:
    print(f"  ✗ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ SETUP COMPLETE!")
print("=" * 70)
print(f"\nDatabase: {DB_CONFIG['database']}")
print(f"Connection: {DB_URL}")
print("\nIMPORTANT - Set DATABASE_URL:")
print(f'  PowerShell: $env:DATABASE_URL="{DB_URL}"')
print(f'  CMD: set DATABASE_URL={DB_URL}')
print("\nThen run: python app.py")
print("=" * 70)

