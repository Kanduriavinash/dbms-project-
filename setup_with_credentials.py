"""
PostgreSQL Database Setup with Your Credentials
This script will create a fresh database with all tables
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

def create_database():
    """Create database if it doesn't exist."""
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
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (PG_DB,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"Database '{PG_DB}' already exists.")
            print("Dropping and recreating for fresh start...")
            # Terminate connections
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
            print(f"✓ Dropped existing database")
        
        # Create database
        cursor.execute(f'CREATE DATABASE {PG_DB};')
        print(f"✓ Created database '{PG_DB}'")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        print("\nPlease check:")
        print("  1. PostgreSQL is running")
        print("  2. Username and password are correct")
        print("  3. You have permission to create databases")
        return False

def setup_tables():
    """Create all tables."""
    print("\n" + "=" * 70)
    print("Step 2: Creating All Tables")
    print("=" * 70)
    
    # Set DATABASE_URL
    os.environ['DATABASE_URL'] = DB_URL
    
    from app import create_app
    from extensions import db
    import models  # Import to register all models
    
    app = create_app()
    
    with app.app_context():
        try:
            print("Dropping existing tables (if any)...")
            db.drop_all()
            print("✓ Dropped existing tables")
            
            print("Creating all tables...")
            db.create_all()
            print("✓ Created all tables")
            
            # Verify tables
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
                print(f"\n⚠️  Missing tables: {missing}")
                return False
            
            print("\n✓ All 15 tables created successfully!")
            return True
            
        except Exception as e:
            print(f"✗ Error creating tables: {e}")
            import traceback
            traceback.print_exc()
            return False

def create_initial_data():
    """Create admin user and sample data."""
    print("\n" + "=" * 70)
    print("Step 3: Creating Initial Data")
    print("=" * 70)
    
    os.environ['DATABASE_URL'] = DB_URL
    
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
                print("✓ Created admin user")
                print("   Username: admin")
                print("   Password: admin123")
            else:
                print("✓ Admin user already exists")
            
            # Create sample categories
            if not Category.query.filter_by(name='Electronics').first():
                cat1 = Category(name='Electronics', description='Electronic products')
                cat2 = Category(name='Home Appliances', description='Home essentials')
                db.session.add_all([cat1, cat2])
                print("✓ Created sample categories")
            else:
                print("✓ Categories already exist")
            
            db.session.commit()
            print("✓ Initial data created")
            return True
            
        except Exception as e:
            print(f"✗ Error: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False

def verify_database():
    """Verify database operations work."""
    print("\n" + "=" * 70)
    print("Step 4: Verifying Database Operations")
    print("=" * 70)
    
    os.environ['DATABASE_URL'] = DB_URL
    
    from app import create_app
    from extensions import db
    from models import Warehouse
    from datetime import datetime
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test INSERT
            print("1. Testing INSERT...")
            test = Warehouse(
                warehouse_name="Test Warehouse",
                is_refrigerated=True,
                capacity=1000,
                created_at=datetime.utcnow()
            )
            db.session.add(test)
            db.session.commit()
            print("   ✓ INSERT successful")
            
            # Test SELECT
            print("2. Testing SELECT...")
            saved = Warehouse.query.filter_by(warehouse_name="Test Warehouse").first()
            if saved and saved.warehouse_id:
                print(f"   ✓ SELECT successful (ID: {saved.warehouse_id})")
            else:
                print("   ✗ SELECT failed")
                return False
            
            # Test UPDATE
            print("3. Testing UPDATE...")
            saved.capacity = 2000
            db.session.commit()
            updated = Warehouse.query.get(saved.warehouse_id)
            if updated and updated.capacity == 2000:
                print("   ✓ UPDATE successful")
            else:
                print("   ✗ UPDATE failed")
                return False
            
            # Test DELETE
            print("4. Testing DELETE...")
            db.session.delete(updated)
            db.session.commit()
            deleted = Warehouse.query.get(saved.warehouse_id)
            if deleted is None:
                print("   ✓ DELETE successful")
            else:
                print("   ✗ DELETE failed")
                return False
            
            print("\n✓ All database operations verified!")
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
    print(f"\nUsing credentials:")
    print(f"  Username: {PG_USER}")
    print(f"  Host: {PG_HOST}:{PG_PORT}")
    print(f"  Database: {PG_DB}")
    print()
    
    try:
        # Step 1: Create database
        if not create_database():
            print("\n✗ Failed to create database!")
            sys.exit(1)
        
        # Step 2: Create tables
        if not setup_tables():
            print("\n✗ Failed to create tables!")
            sys.exit(1)
        
        # Step 3: Create initial data
        if not create_initial_data():
            print("\n✗ Failed to create initial data!")
            sys.exit(1)
        
        # Step 4: Verify
        if not verify_database():
            print("\n✗ Database verification failed!")
            sys.exit(1)
        
        # Success!
        print("\n" + "=" * 70)
        print("✅ DATABASE SETUP COMPLETE!")
        print("=" * 70)
        print(f"\nDatabase: {PG_DB}")
        print(f"Connection: {DB_URL}")
        print("\n" + "=" * 70)
        print("NEXT STEPS:")
        print("=" * 70)
        print(f"\n1. Set DATABASE_URL (in the SAME terminal where you run the app):")
        print(f"\n   PowerShell:")
        print(f'   $env:DATABASE_URL="{DB_URL}"')
        print(f"\n   CMD:")
        print(f'   set DATABASE_URL={DB_URL}')
        print(f"\n2. Verify connection:")
        print(f"   python check_database.py")
        print(f"\n3. Start application:")
        print(f"   python app.py")
        print(f"\n4. Login:")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"\n5. Create a warehouse and verify it's in PostgreSQL!")
        print(f"\n" + "=" * 70)
        
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

