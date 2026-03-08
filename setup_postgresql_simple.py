"""
Simple PostgreSQL Database Setup - Non-Interactive
Usage: python setup_postgresql_simple.py
Or set environment variables: PG_USER, PG_PASSWORD, PG_HOST, PG_PORT, PG_DB
"""
import os
import sys
from sqlalchemy import create_engine, inspect, text
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def get_config():
    """Get database configuration from environment or defaults."""
    username = os.environ.get('PG_USER', 'postgres')
    password = os.environ.get('PG_PASSWORD', 'postgres')
    host = os.environ.get('PG_HOST', 'localhost')
    port = os.environ.get('PG_PORT', '5432')
    database = os.environ.get('PG_DB', 'rims_db')
    
    admin_url = f"postgresql://{username}:{password}@{host}:{port}/postgres"
    db_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    print(f"Using configuration:")
    print(f"  Username: {username}")
    print(f"  Host: {host}:{port}")
    print(f"  Database: {database}")
    print()
    
    return admin_url, db_url, database

def create_database(admin_url, database_name):
    """Create database if it doesn't exist."""
    print("=" * 70)
    print("Step 1: Creating Database")
    print("=" * 70)
    
    try:
        conn = psycopg2.connect(admin_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (database_name,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"Database '{database_name}' already exists.")
            print("Dropping and recreating...")
            # Terminate connections
            cursor.execute(
                f"SELECT pg_terminate_backend(pg_stat_activity.pid) "
                f"FROM pg_stat_activity "
                f"WHERE pg_stat_activity.datname = '{database_name}' "
                f"AND pid <> pg_backend_pid();"
            )
            cursor.execute(f"DROP DATABASE {database_name};")
            print(f"✓ Dropped existing database")
        
        # Create database
        cursor.execute(f'CREATE DATABASE {database_name};')
        print(f"✓ Created database '{database_name}'")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def setup_tables(db_url):
    """Create all tables."""
    print("\n" + "=" * 70)
    print("Step 2: Creating Tables")
    print("=" * 70)
    
    # Set DATABASE_URL
    os.environ['DATABASE_URL'] = db_url
    
    from app import create_app
    from extensions import db
    import models  # Import to register all models
    
    app = create_app()
    
    with app.app_context():
        try:
            print("Dropping existing tables...")
            db.drop_all()
            print("✓ Dropped existing tables")
            
            print("Creating all tables...")
            db.create_all()
            print("✓ Created all tables")
            
            # Verify
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
                return False
            
            print("\n✓ All tables created!")
            return True
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

def create_initial_data(db_url):
    """Create initial admin user and sample data."""
    print("\n" + "=" * 70)
    print("Step 3: Creating Initial Data")
    print("=" * 70)
    
    os.environ['DATABASE_URL'] = db_url
    
    from app import create_app
    from extensions import db
    from models import User, Category
    from werkzeug.security import generate_password_hash
    
    app = create_app()
    
    with app.app_context():
        try:
            # Create admin user
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    email='admin@rims.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin'
                )
                db.session.add(admin)
                print("✓ Created admin user (admin/admin123)")
            
            # Create sample categories
            if not Category.query.filter_by(name='Electronics').first():
                cat1 = Category(name='Electronics', description='Electronic products')
                cat2 = Category(name='Home Appliances', description='Home essentials')
                db.session.add_all([cat1, cat2])
                print("✓ Created sample categories")
            
            db.session.commit()
            print("✓ Initial data created")
            return True
            
        except Exception as e:
            print(f"✗ Error: {e}")
            db.session.rollback()
            return False

def verify_database(db_url):
    """Verify database works."""
    print("\n" + "=" * 70)
    print("Step 4: Verifying Database")
    print("=" * 70)
    
    os.environ['DATABASE_URL'] = db_url
    
    from app import create_app
    from extensions import db
    from models import Warehouse
    from datetime import datetime
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test insert
            print("Testing warehouse insert...")
            test = Warehouse(
                warehouse_name="Test Warehouse",
                is_refrigerated=True,
                capacity=1000,
                created_at=datetime.utcnow()
            )
            db.session.add(test)
            db.session.commit()
            print("  ✓ Insert successful")
            
            # Test query
            saved = Warehouse.query.filter_by(warehouse_name="Test Warehouse").first()
            if saved:
                print(f"  ✓ Query successful (ID: {saved.warehouse_id})")
            else:
                print("  ✗ Query failed")
                return False
            
            # Test update
            saved.capacity = 2000
            db.session.commit()
            updated = Warehouse.query.get(saved.warehouse_id)
            if updated.capacity == 2000:
                print("  ✓ Update successful")
            else:
                print("  ✗ Update failed")
                return False
            
            # Test delete
            db.session.delete(updated)
            db.session.commit()
            deleted = Warehouse.query.get(saved.warehouse_id)
            if deleted is None:
                print("  ✓ Delete successful")
            else:
                print("  ✗ Delete failed")
                return False
            
            print("\n✓ All database operations working!")
            return True
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main setup function."""
    print("=" * 70)
    print("PostgreSQL Database Setup for RIMS")
    print("=" * 70)
    print()
    print("To customize, set environment variables:")
    print("  PG_USER=postgres PG_PASSWORD=yourpass PG_DB=rims_db")
    print()
    
    try:
        admin_url, db_url, database = get_config()
        
        # Step 1: Create database
        if not create_database(admin_url, database):
            print("Failed to create database!")
            sys.exit(1)
        
        # Step 2: Create tables
        if not setup_tables(db_url):
            print("Failed to create tables!")
            sys.exit(1)
        
        # Step 3: Create initial data
        if not create_initial_data(db_url):
            print("Failed to create initial data!")
            sys.exit(1)
        
        # Step 4: Verify
        if not verify_database(db_url):
            print("Database verification failed!")
            sys.exit(1)
        
        # Success!
        print("\n" + "=" * 70)
        print("✅ DATABASE SETUP COMPLETE!")
        print("=" * 70)
        print(f"\nDatabase URL: {db_url}")
        print("\nNext steps:")
        print(f"1. Set DATABASE_URL:")
        print(f"   PowerShell: $env:DATABASE_URL='{db_url}'")
        print(f"   CMD: set DATABASE_URL={db_url}")
        print("\n2. Verify: python check_database.py")
        print("\n3. Start app: python app.py")
        print("\n4. Login: admin / admin123")
        print("\n" + "=" * 70)
        
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

