"""
Fully Automatic PostgreSQL Database Setup
No prompts - just runs with your credentials
"""
import os
import sys

# Your PostgreSQL credentials (already set)
PG_USER = "postgres"
PG_PASSWORD = "avinash"
PG_HOST = "localhost"
PG_PORT = "5432"
PG_DB = "retail_db"

ADMIN_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/postgres"
DB_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

print("=" * 70)
print("Automatic PostgreSQL Database Setup")
print("=" * 70)
print(f"Username: {PG_USER}")
print(f"Database: {PG_DB}")
print()

# Step 1: Create Database
print("Step 1: Creating database...")
try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    conn = psycopg2.connect(ADMIN_URL)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (PG_DB,))
    if cursor.fetchone():
        print("  Dropping existing database...")
        try:
            cursor.execute(f"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{PG_DB}' AND pid <> pg_backend_pid();")
        except: pass
        cursor.execute(f"DROP DATABASE {PG_DB};")
    cursor.execute(f'CREATE DATABASE {PG_DB};')
    cursor.close()
    conn.close()
    print("  ✓ Database created")
except Exception as e:
    print(f"  ✗ Error: {e}")
    sys.exit(1)

# Step 2: Create Tables
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

# Step 3: Initial Data
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
            db.session.add_all([Category(name='Electronics', description='Electronic products'), Category(name='Home Appliances', description='Home essentials')])
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
            print("  ✗ Verification failed")
            sys.exit(1)
except Exception as e:
    print(f"  ✗ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ SETUP COMPLETE!")
print("=" * 70)
print(f"\nDatabase URL: {DB_URL}")
print("\nIMPORTANT - Run this in your terminal:")
print(f'  PowerShell: $env:DATABASE_URL="{DB_URL}"')
print(f'  CMD: set DATABASE_URL={DB_URL}')
print("\nThen run: python app.py")
print("=" * 70)

