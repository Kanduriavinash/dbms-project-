"""
Complete Database Setup Script
Creates a fresh PostgreSQL database with all tables and verifies everything works
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError, ProgrammingError
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def get_db_config():
    """Get database configuration from user or environment."""
    print("=" * 70)
    print("PostgreSQL Database Setup for RIMS")
    print("=" * 70)
    print()
    
    # Check if DATABASE_URL is already set
    db_url = os.environ.get('DATABASE_URL')
    if db_url and 'postgresql' in db_url.lower():
        print(f"Found DATABASE_URL: {db_url}")
        use_existing = input("Use this connection? (y/n): ").strip().lower()
        if use_existing == 'y':
            return db_url
    
    print("Enter PostgreSQL connection details:")
    print()
    
    username = input("PostgreSQL Username [postgres]: ").strip() or "postgres"
    password = input("PostgreSQL Password: ").strip()
    if not password:
        print("Error: Password is required!")
        sys.exit(1)
    
    host = input("Host [localhost]: ").strip() or "localhost"
    port = input("Port [5432]: ").strip() or "5432"
    database = input("Database Name [rims_db]: ").strip() or "rims_db"
    
    # Build connection strings
    admin_url = f"postgresql://{username}:{password}@{host}:{port}/postgres"
    db_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    return admin_url, db_url, database

def create_database(admin_url, database_name):
    """Create database if it doesn't exist."""
    print("\n" + "=" * 70)
    print("Step 1: Creating Database")
    print("=" * 70)
    
    try:
        # Connect to PostgreSQL server (not specific database)
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
            drop = input("Drop and recreate? (y/n): ").strip().lower()
            if drop == 'y':
                # Terminate connections to the database
                cursor.execute(
                    f"SELECT pg_terminate_backend(pg_stat_activity.pid) "
                    f"FROM pg_stat_activity "
                    f"WHERE pg_stat_activity.datname = '{database_name}' "
                    f"AND pid <> pg_backend_pid();"
                )
                cursor.execute(f"DROP DATABASE {database_name};")
                print(f"✓ Dropped existing database '{database_name}'")
            else:
                cursor.close()
                conn.close()
                return False
        
        # Create database
        cursor.execute(f'CREATE DATABASE {database_name};')
        print(f"✓ Created database '{database_name}'")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        return False

def create_all_tables(db_url):
    """Create all tables using Flask app context."""
    print("\n" + "=" * 70)
    print("Step 2: Creating Tables")
    print("=" * 70)
    
    # Set DATABASE_URL for the app
    os.environ['DATABASE_URL'] = db_url
    
    from app import create_app
    from extensions import db
    # Import all models to register them
    import models
    
    app = create_app()
    
    with app.app_context():
        try:
            # Drop all tables (fresh start)
            print("Dropping existing tables (if any)...")
            db.drop_all()
            print("✓ Dropped existing tables")
            
            # Create all tables
            print("Creating all tables...")
            db.create_all()
            print("✓ Created all tables")
            
            # Verify tables were created
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = [
                'user', 'category', 'product', 'warehouse', 'inventory',
                'cart', 'cart_item', 'order_tbl', 'order_detail', 'payment',
                'provider', 'customer', 'delivery', 'delivery_detail', 'transfer'
            ]
            
            print(f"\nCreated {len(tables)} tables:")
            for table in sorted(tables):
                status = "✓" if table in expected_tables else "?"
                print(f"  {status} {table}")
            
            # Check for missing tables
            missing = set(expected_tables) - set(tables)
            if missing:
                print(f"\n⚠️  Missing tables: {missing}")
                return False
            
            print("\n✓ All tables created successfully!")
            return True
            
        except Exception as e:
            print(f"✗ Error creating tables: {e}")
            import traceback
            traceback.print_exc()
            return False

def verify_database(db_url):
    """Verify database structure and test operations."""
    print("\n" + "=" * 70)
    print("Step 3: Verifying Database")
    print("=" * 70)
    
    os.environ['DATABASE_URL'] = db_url
    
    from app import create_app
    from extensions import db
    from models import Warehouse, Product, User, Category
    from datetime import datetime
    from werkzeug.security import generate_password_hash
    import models  # Import to register all models
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test 1: Check connection
            print("1. Testing database connection...")
            db.engine.connect()
            print("   ✓ Connection successful")
            
            # Test 2: Verify warehouse table structure
            print("\n2. Verifying warehouse table structure...")
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = inspector.get_columns('warehouse')
            
            expected_columns = {
                'warehouse_id', 'warehouse_name', 'is_refrigerated', 
                'capacity', 'created_at'
            }
            actual_columns = {col['name'] for col in columns}
            
            if expected_columns.issubset(actual_columns):
                print("   ✓ All required columns exist")
                for col in columns:
                    print(f"     - {col['name']}: {col['type']}")
            else:
                missing = expected_columns - actual_columns
                print(f"   ✗ Missing columns: {missing}")
                return False
            
            # Test 3: Insert test warehouse
            print("\n3. Testing warehouse insert...")
            test_warehouse = Warehouse(
                warehouse_name="Test Warehouse",
                is_refrigerated=True,
                capacity=1000,
                created_at=datetime.utcnow()
            )
            db.session.add(test_warehouse)
            db.session.commit()
            print("   ✓ Warehouse inserted successfully")
            print(f"     ID: {test_warehouse.warehouse_id}")
            print(f"     Name: {test_warehouse.warehouse_name}")
            print(f"     Refrigerated: {test_warehouse.is_refrigerated}")
            print(f"     Capacity: {test_warehouse.capacity}")
            
            # Test 4: Query test warehouse
            print("\n4. Testing warehouse query...")
            saved = Warehouse.query.filter_by(warehouse_name="Test Warehouse").first()
            if saved:
                print("   ✓ Warehouse retrieved successfully")
                print(f"     Retrieved ID: {saved.warehouse_id}")
            else:
                print("   ✗ Warehouse not found after insert!")
                return False
            
            # Test 5: Update test warehouse
            print("\n5. Testing warehouse update...")
            saved.capacity = 2000
            db.session.commit()
            updated = Warehouse.query.get(saved.warehouse_id)
            if updated.capacity == 2000:
                print("   ✓ Warehouse updated successfully")
            else:
                print("   ✗ Warehouse update failed!")
                return False
            
            # Test 6: Delete test warehouse
            print("\n6. Testing warehouse delete...")
            db.session.delete(updated)
            db.session.commit()
            deleted = Warehouse.query.get(updated.warehouse_id)
            if deleted is None:
                print("   ✓ Warehouse deleted successfully")
            else:
                print("   ✗ Warehouse delete failed!")
                return False
            
            # Test 7: Create admin user
            print("\n7. Creating admin user...")
            admin = User(
                username='admin',
                email='admin@rims.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("   ✓ Admin user created")
            print("     Username: admin")
            print("     Password: admin123")
            
            # Test 8: Create sample category
            print("\n8. Creating sample category...")
            category = Category(
                name='Electronics',
                description='Electronic products'
            )
            db.session.add(category)
            db.session.commit()
            print("   ✓ Category created")
            
            print("\n" + "=" * 70)
            print("✅ ALL TESTS PASSED - Database is ready!")
            print("=" * 70)
            return True
            
        except Exception as e:
            print(f"\n✗ Verification failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main setup function."""
    try:
        # Get database configuration
        config = get_db_config()
        if isinstance(config, tuple):
            admin_url, db_url, database_name = config
        else:
            # DATABASE_URL was provided
            db_url = config
            # Extract database name from URL
            database_name = db_url.split('/')[-1].split('?')[0]
            admin_url = db_url.rsplit('/', 1)[0] + '/postgres'
        
        # Step 1: Create database
        if not create_database(admin_url, database_name):
            print("\n⚠️  Using existing database...")
        
        # Step 2: Create tables
        if not create_all_tables(db_url):
            print("\n✗ Failed to create tables!")
            sys.exit(1)
        
        # Step 3: Verify database
        if not verify_database(db_url):
            print("\n✗ Database verification failed!")
            sys.exit(1)
        
        # Final instructions
        print("\n" + "=" * 70)
        print("✅ DATABASE SETUP COMPLETE!")
        print("=" * 70)
        print("\nNext steps:")
        print(f"1. Set DATABASE_URL environment variable:")
        print(f"   PowerShell: $env:DATABASE_URL='{db_url}'")
        print(f"   CMD: set DATABASE_URL={db_url}")
        print()
        print("2. Verify connection:")
        print("   python check_database.py")
        print()
        print("3. Start application:")
        print("   python app.py")
        print()
        print("4. Login as admin:")
        print("   Username: admin")
        print("   Password: admin123")
        print()
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

