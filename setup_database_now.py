"""
Automatic PostgreSQL Database Setup
Uses your credentials: postgres/avinash
No user input required - just run it!
"""
import os
import sys

# Your PostgreSQL credentials
PG_USER = "postgres"
PG_PASSWORD = "avinash"
PG_HOST = "localhost"
PG_PORT = "5432"
PG_DB = "rims_db"

# Build connection strings
ADMIN_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/postgres"
DB_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

print("=" * 70)
print("PostgreSQL Database Setup for RIMS")
print("=" * 70)
print(f"\nConfiguration:")
print(f"  Username: {PG_USER}")
print(f"  Host: {PG_HOST}:{PG_PORT}")
print(f"  Database: {PG_DB}")
print()

# Step 1: Create database
print("=" * 70)
print("Step 1: Creating Database")
print("=" * 70)

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    conn = psycopg2.connect(ADMIN_URL)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (PG_DB,))
    exists = cursor.fetchone()
    
    if exists:
        print(f"Database '{PG_DB}' exists. Dropping for fresh start...")
        try:
            cursor.execute(
                f"SELECT pg_terminate_backend(pg_stat_activity.pid) "
                f"FROM pg_stat_activity "
                f"WHERE pg_stat_activity.datname = '{PG_DB}' "
                f"AND pid <> pg_backend_pid();"
            )
        except:
            pass
        cursor.execute(f"DROP DATABASE {PG_DB};")
        print("✓ Dropped existing database")
    
    cursor.execute(f'CREATE DATABASE {PG_DB};')
    print(f"✓ Created database '{PG_DB}'")
    
    cursor.close()
    conn.close()
    print("✓ Step 1 complete")
    
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nPlease check:")
    print("  1. PostgreSQL is running")
    print("  2. Username: postgres, Password: avinash")
    print("  3. You have permission to create databases")
    sys.exit(1)

# Step 2: Create tables
print("\n" + "=" * 70)
print("Step 2: Creating All Tables")
print("=" * 70)

os.environ['DATABASE_URL'] = DB_URL

try:
    from app import create_app
    from extensions import db
    import models
    
    app = create_app()
    
    with app.app_context():
        print("Dropping existing tables...")
        db.drop_all()
        print("✓ Dropped existing tables")
        
        print("Creating all tables...")
        db.create_all()
        print("✓ Created all tables")
        
        # Verify
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        expected = [
            'user', 'category', 'product', 'warehouse', 'inventory',
            'cart', 'cart_item', 'order_tbl', 'order_detail', 'payment',
            'provider', 'customer', 'delivery', 'delivery_detail', 'transfer'
        ]
        
        print(f"\nCreated {len(tables)} tables:")
        for table in sorted(tables):
            status = "✓" if table in expected else "?"
            print(f"  {status} {table}")
        
        missing = set(expected) - set(tables)
        if missing:
            print(f"\n⚠️  Missing: {missing}")
            sys.exit(1)
        
        print("\n✓ All 15 tables created!")
        print("✓ Step 2 complete")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Create initial data
print("\n" + "=" * 70)
print("Step 3: Creating Initial Data")
print("=" * 70)

try:
    from app import create_app
    from extensions import db
    from models import User, Category
    from werkzeug.security import generate_password_hash
    
    app = create_app()
    
    with app.app_context():
        # Admin user
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@rims.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            print("✓ Created admin user (admin/admin123)")
        else:
            print("✓ Admin user exists")
        
        # Categories
        if not Category.query.filter_by(name='Electronics').first():
            cat1 = Category(name='Electronics', description='Electronic products')
            cat2 = Category(name='Home Appliances', description='Home essentials')
            db.session.add_all([cat1, cat2])
            print("✓ Created sample categories")
        else:
            print("✓ Categories exist")
        
        db.session.commit()
        print("✓ Step 3 complete")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Verify
print("\n" + "=" * 70)
print("Step 4: Verifying Database")
print("=" * 70)

try:
    from app import create_app
    from extensions import db
    from models import Warehouse
    from datetime import datetime
    
    app = create_app()
    
    with app.app_context():
        # Test operations
        print("Testing INSERT...")
        test = Warehouse(
            warehouse_name="Test Warehouse",
            is_refrigerated=True,
            capacity=1000,
            created_at=datetime.utcnow()
        )
        db.session.add(test)
        db.session.commit()
        print("  ✓ INSERT successful")
        
        print("Testing SELECT...")
        saved = Warehouse.query.filter_by(warehouse_name="Test Warehouse").first()
        if saved:
            print(f"  ✓ SELECT successful (ID: {saved.warehouse_id})")
        else:
            print("  ✗ SELECT failed")
            sys.exit(1)
        
        print("Testing UPDATE...")
        saved.capacity = 2000
        db.session.commit()
        print("  ✓ UPDATE successful")
        
        print("Testing DELETE...")
        db.session.delete(saved)
        db.session.commit()
        print("  ✓ DELETE successful")
        
        print("\n✓ All operations verified!")
        print("✓ Step 4 complete")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Success!
print("\n" + "=" * 70)
print("✅ DATABASE SETUP COMPLETE!")
print("=" * 70)
print(f"\nDatabase: {PG_DB}")
print(f"Connection: {DB_URL}")
print("\n" + "=" * 70)
print("NEXT STEPS - IMPORTANT!")
print("=" * 70)
print(f"\n1. Set DATABASE_URL in your terminal (SAME terminal where you run app.py):")
print(f"\n   PowerShell:")
print(f'   $env:DATABASE_URL="{DB_URL}"')
print(f"\n   CMD:")
print(f'   set DATABASE_URL={DB_URL}')
print(f"\n2. Verify it's working:")
print(f"   python check_database.py")
print(f"\n3. Start your application:")
print(f"   python app.py")
print(f"\n4. Login as admin:")
print(f"   Username: admin")
print(f"   Password: admin123")
print(f"\n5. Create a warehouse and check PostgreSQL - it will be there!")
print(f"\n" + "=" * 70)
print("✅ Your database is ready! All data will save to PostgreSQL now!")
print("=" * 70)

