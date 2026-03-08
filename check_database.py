"""
Script to check database connection and verify PostgreSQL is being used
"""
import os
from app import create_app
from extensions import db
from models import Warehouse

def check_database():
    """Check which database is being used and verify connection."""
    app = create_app()
    
    with app.app_context():
        # Get database URI
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Unknown')
        print("=" * 60)
        print("DATABASE CONNECTION CHECK")
        print("=" * 60)
        print(f"\nDatabase URI: {db_uri}")
        
        # Check if PostgreSQL or SQLite
        if 'postgresql' in db_uri.lower():
            print("✓ Using PostgreSQL")
        elif 'sqlite' in db_uri.lower():
            print("⚠ WARNING: Using SQLite (not PostgreSQL!)")
            print("\nTo use PostgreSQL, set DATABASE_URL environment variable:")
            print("  Windows PowerShell: $env:DATABASE_URL='postgresql://user:pass@localhost:5432/rims_db'")
            print("  Windows CMD: set DATABASE_URL=postgresql://user:pass@localhost:5432/rims_db")
            print("  Linux/Mac: export DATABASE_URL='postgresql://user:pass@localhost:5432/rims_db'")
        else:
            print("⚠ Unknown database type")
        
        # Test connection
        try:
            db.engine.connect()
            print("✓ Database connection successful!")
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False
        
        # Check if warehouse table exists
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"\nTables in database: {len(tables)}")
            if 'warehouse' in tables:
                print("✓ 'warehouse' table exists")
                
                # Get warehouse columns
                columns = inspector.get_columns('warehouse')
                print("\nWarehouse table columns:")
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
                
                # Count warehouses
                count = Warehouse.query.count()
                print(f"\nCurrent warehouses in database: {count}")
                
                if count > 0:
                    print("\nSample warehouses:")
                    warehouses = Warehouse.query.limit(5).all()
                    for w in warehouses:
                        print(f"  ID: {w.warehouse_id}, Name: {w.warehouse_name}, "
                              f"Refrigerated: {w.is_refrigerated}, Capacity: {w.capacity}")
            else:
                print("✗ 'warehouse' table does NOT exist!")
                print("  Run: python setup_database.py")
        except Exception as e:
            print(f"✗ Error checking tables: {e}")
        
        print("\n" + "=" * 60)
        return True

if __name__ == '__main__':
    check_database()

