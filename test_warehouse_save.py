"""
Test script to verify warehouse data is being saved to PostgreSQL
"""
import os
from app import create_app
from extensions import db
from models import Warehouse
from datetime import datetime

def test_warehouse_save():
    """Test creating and saving a warehouse to verify database operations."""
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("WAREHOUSE SAVE TEST")
        print("=" * 70)
        
        # Check database connection
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Unknown')
        print(f"\n1. Database URI: {db_uri}")
        
        if 'sqlite' in db_uri.lower():
            print("   ⚠️  WARNING: Using SQLite! Data will NOT save to PostgreSQL!")
            print("   Set DATABASE_URL environment variable first!")
            return False
        elif 'postgresql' in db_uri.lower():
            print("   ✓ Using PostgreSQL")
        else:
            print("   ⚠️  Unknown database type")
        
        # Test connection
        try:
            conn = db.engine.connect()
            print("\n2. Database connection: ✓ SUCCESS")
            conn.close()
        except Exception as e:
            print(f"\n2. Database connection: ✗ FAILED - {e}")
            return False
        
        # Check if warehouse table exists
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'warehouse' not in tables:
                print("\n3. Warehouse table: ✗ DOES NOT EXIST")
                print("   Run: python setup_database.py")
                return False
            
            print("3. Warehouse table: ✓ EXISTS")
            
            # Count before
            count_before = Warehouse.query.count()
            print(f"\n4. Warehouses before: {count_before}")
            
            # Create test warehouse
            test_name = f"TEST_WAREHOUSE_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            print(f"\n5. Creating test warehouse: {test_name}")
            
            test_warehouse = Warehouse(
                warehouse_name=test_name,
                is_refrigerated=True,
                capacity=5000,
                created_at=datetime.utcnow()
            )
            
            print("   Adding to session...")
            db.session.add(test_warehouse)
            
            print("   Committing to database...")
            db.session.commit()
            
            print("   ✓ Commit successful!")
            
            # Verify it was saved
            print("\n6. Verifying save...")
            saved = Warehouse.query.filter_by(warehouse_name=test_name).first()
            
            if saved:
                print(f"   ✓ Warehouse found! ID: {saved.warehouse_id}")
                print(f"   Name: {saved.warehouse_name}")
                print(f"   Refrigerated: {saved.is_refrigerated}")
                print(f"   Capacity: {saved.capacity}")
                print(f"   Created: {saved.created_at}")
                
                # Count after
                count_after = Warehouse.query.count()
                print(f"\n7. Warehouses after: {count_after}")
                
                if count_after > count_before:
                    print("   ✓ Count increased - Data saved successfully!")
                else:
                    print("   ⚠️  Count did not increase")
                
                # Verify in PostgreSQL directly
                print("\n8. Verifying in PostgreSQL database...")
                try:
                    result = db.session.execute(
                        text("SELECT * FROM warehouse WHERE warehouse_name = :name"),
                        {"name": test_name}
                    ).fetchone()
                    
                    if result:
                        print("   ✓ Found in PostgreSQL database!")
                        print(f"   Row: {result}")
                    else:
                        print("   ✗ NOT found in PostgreSQL database!")
                except Exception as e:
                    print(f"   ⚠️  Could not verify directly: {e}")
                
                # Cleanup - delete test warehouse
                print(f"\n9. Cleaning up test warehouse (ID: {saved.warehouse_id})...")
                db.session.delete(saved)
                db.session.commit()
                print("   ✓ Test warehouse deleted")
                
                print("\n" + "=" * 70)
                print("✅ TEST PASSED - Data is being saved to database!")
                print("=" * 70)
                return True
            else:
                print("   ✗ Warehouse NOT found after commit!")
                print("\n" + "=" * 70)
                print("❌ TEST FAILED - Data was not saved!")
                print("=" * 70)
                return False
                
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    test_warehouse_save()

