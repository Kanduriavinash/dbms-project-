"""
Comprehensive Database Operations Test Script
Tests all CRUD operations to ensure data is properly saved to PostgreSQL
"""
import os
import sys
from datetime import datetime

# Set database URL
DB_URL = "postgresql://postgres:avinash@localhost:5432/retail_db"
os.environ['DATABASE_URL'] = DB_URL

print("=" * 70)
print("COMPREHENSIVE DATABASE OPERATIONS TEST")
print("=" * 70)
print(f"Database: {DB_URL}")
print()

from app import create_app
from extensions import db
from models import (
    User, Category, Product, Warehouse, Inventory,
    Cart, CartItem, Order, OrderDetail, Payment
)
from werkzeug.security import generate_password_hash

app = create_app()

def test_user_operations():
    """Test user registration and login"""
    print("1. Testing User Operations...")
    with app.app_context():
        try:
            # Create test user
            test_user = User(
                username=f"testuser_{datetime.now().timestamp()}",
                email=f"test_{datetime.now().timestamp()}@test.com",
                password_hash=generate_password_hash("test123"),
                role="customer"
            )
            db.session.add(test_user)
            db.session.commit()
            user_id = test_user.id
            print(f"   [OK] User created: ID {user_id}")
            
            # Verify user exists
            saved_user = User.query.get(user_id)
            assert saved_user is not None, "User not found after creation"
            print(f"   [OK] User verified in database")
            
            # Update user
            saved_user.email = "updated@test.com"
            db.session.commit()
            updated = User.query.get(user_id)
            assert updated.email == "updated@test.com", "User update failed"
            print(f"   [OK] User updated in database")
            
            # Delete user
            db.session.delete(saved_user)
            db.session.commit()
            deleted = User.query.get(user_id)
            assert deleted is None, "User not deleted"
            print(f"   [OK] User deleted from database")
            print("   [PASS] User operations: PASSED\n")
            return True
        except Exception as e:
            print(f"   [FAIL] User operations failed: {e}\n")
            db.session.rollback()
            return False

def test_product_operations():
    """Test product CRUD operations"""
    print("2. Testing Product Operations...")
    with app.app_context():
        try:
            # Create category first
            cat = Category(name=f"TestCategory_{datetime.now().timestamp()}")
            db.session.add(cat)
            db.session.flush()
            
            # Create product
            product = Product(
                product_name=f"Test Product {datetime.now().timestamp()}",
                unit_price=99.99,
                quantity=100,
                product_description="Test description",
                category_id=cat.category_id
            )
            db.session.add(product)
            db.session.commit()
            product_id = product.product_id
            print(f"   [OK] Product created: ID {product_id}")
            
            # Verify product
            saved = Product.query.get(product_id)
            assert saved is not None, "Product not found"
            assert float(saved.unit_price) == 99.99, "Product price mismatch"
            print(f"   [OK] Product verified in database")
            
            # Update product
            saved.quantity = 50
            db.session.commit()
            updated = Product.query.get(product_id)
            assert updated.quantity == 50, "Product update failed"
            print(f"   [OK] Product updated in database")
            
            # Delete product
            db.session.delete(saved)
            db.session.delete(cat)
            db.session.commit()
            print(f"   [OK] Product deleted from database")
            print("   [PASS] Product operations: PASSED\n")
            return True
        except Exception as e:
            print(f"   [FAIL] Product operations failed: {e}\n")
            db.session.rollback()
            return False

def test_warehouse_operations():
    """Test warehouse CRUD operations"""
    print("3. Testing Warehouse Operations...")
    with app.app_context():
        try:
            warehouse = Warehouse(
                warehouse_name=f"Test Warehouse {datetime.now().timestamp()}",
                is_refrigerated=True,
                capacity=5000,
                created_at=datetime.utcnow()
            )
            db.session.add(warehouse)
            db.session.commit()
            warehouse_id = warehouse.warehouse_id
            print(f"   ✓ Warehouse created: ID {warehouse_id}")
            
            # Verify
            saved = Warehouse.query.get(warehouse_id)
            assert saved is not None, "Warehouse not found"
            assert saved.is_refrigerated == True, "Warehouse field mismatch"
            assert saved.capacity == 5000, "Warehouse capacity mismatch"
            print(f"   ✓ Warehouse verified in database")
            
            # Update
            saved.capacity = 10000
            db.session.commit()
            updated = Warehouse.query.get(warehouse_id)
            assert updated.capacity == 10000, "Warehouse update failed"
            print(f"   ✓ Warehouse updated in database")
            
            # Delete
            db.session.delete(saved)
            db.session.commit()
            print(f"   ✓ Warehouse deleted from database")
            print("   ✅ Warehouse operations: PASSED\n")
            return True
        except Exception as e:
            print(f"   ✗ Warehouse operations failed: {e}\n")
            db.session.rollback()
            return False

def test_cart_operations():
    """Test cart and cart item operations"""
    print("4. Testing Cart Operations...")
    with app.app_context():
        try:
            # Create user
            user = User(
                username=f"cartuser_{datetime.now().timestamp()}",
                password_hash=generate_password_hash("test"),
                role="customer"
            )
            db.session.add(user)
            db.session.flush()
            
            # Create product
            product = Product(
                product_name="Cart Test Product",
                unit_price=25.50,
                quantity=10
            )
            db.session.add(product)
            db.session.flush()
            
            # Create cart
            cart = Cart(user_id=user.id)
            db.session.add(cart)
            db.session.flush()
            print(f"   ✓ Cart created: ID {cart.cart_id}")
            
            # Add item to cart
            cart_item = CartItem(
                cart_id=cart.cart_id,
                product_id=product.product_id,
                quantity=2,
                unit_price=25.50
            )
            db.session.add(cart_item)
            db.session.commit()
            print(f"   ✓ Cart item added: ID {cart_item.cart_item_id}")
            
            # Verify
            saved_item = CartItem.query.get(cart_item.cart_item_id)
            assert saved_item is not None, "Cart item not found"
            assert saved_item.quantity == 2, "Cart item quantity mismatch"
            print(f"   ✓ Cart item verified in database")
            
            # Update cart item
            saved_item.quantity = 5
            db.session.commit()
            updated = CartItem.query.get(cart_item.cart_item_id)
            assert updated.quantity == 5, "Cart item update failed"
            print(f"   ✓ Cart item updated in database")
            
            # Delete cart item
            db.session.delete(saved_item)
            db.session.delete(cart)
            db.session.delete(product)
            db.session.delete(user)
            db.session.commit()
            print(f"   ✓ Cart item deleted from database")
            print("   ✅ Cart operations: PASSED\n")
            return True
        except Exception as e:
            print(f"   ✗ Cart operations failed: {e}\n")
            db.session.rollback()
            return False

def test_order_operations():
    """Test order, order detail, and payment operations"""
    print("5. Testing Order Operations...")
    with app.app_context():
        try:
            # Create user
            user = User(
                username=f"orderuser_{datetime.now().timestamp()}",
                password_hash=generate_password_hash("test"),
                role="customer"
            )
            db.session.add(user)
            db.session.flush()
            
            # Create product
            product = Product(
                product_name="Order Test Product",
                unit_price=50.00,
                quantity=20
            )
            db.session.add(product)
            db.session.flush()
            
            # Create order
            order = Order(
                customer_id=user.id,
                order_date=datetime.utcnow(),
                total_amount=100.00,
                status='paid'
            )
            db.session.add(order)
            db.session.flush()
            print(f"   ✓ Order created: ID {order.order_id}")
            
            # Create order detail
            order_detail = OrderDetail(
                order_id=order.order_id,
                product_id=product.product_id,
                product_name=product.product_name,
                order_quantity=2,
                unit_price=50.00
            )
            db.session.add(order_detail)
            print(f"   ✓ Order detail created: ID {order_detail.order_detail_id}")
            
            # Create payment
            payment = Payment(
                order_id=order.order_id,
                amount=100.00,
                method='test',
                status='completed',
                created_at=datetime.utcnow()
            )
            db.session.add(payment)
            db.session.commit()
            print(f"   ✓ Payment created: ID {payment.payment_id}")
            
            # Verify all records
            saved_order = Order.query.get(order.order_id)
            assert saved_order is not None, "Order not found"
            assert saved_order.total_amount == 100.00, "Order amount mismatch"
            
            saved_detail = OrderDetail.query.get(order_detail.order_detail_id)
            assert saved_detail is not None, "Order detail not found"
            
            saved_payment = Payment.query.get(payment.payment_id)
            assert saved_payment is not None, "Payment not found"
            print(f"   ✓ All order records verified in database")
            
            # Update order status
            saved_order.status = 'shipped'
            db.session.commit()
            updated = Order.query.get(order.order_id)
            assert updated.status == 'shipped', "Order status update failed"
            print(f"   ✓ Order updated in database")
            
            # Cleanup
            db.session.delete(saved_payment)
            db.session.delete(saved_detail)
            db.session.delete(saved_order)
            db.session.delete(product)
            db.session.delete(user)
            db.session.commit()
            print(f"   ✓ Order records deleted from database")
            print("   ✅ Order operations: PASSED\n")
            return True
        except Exception as e:
            print(f"   ✗ Order operations failed: {e}\n")
            db.session.rollback()
            return False

def test_inventory_operations():
    """Test inventory operations"""
    print("6. Testing Inventory Operations...")
    with app.app_context():
        try:
            # Create product and warehouse
            product = Product(
                product_name="Inventory Test Product",
                unit_price=30.00,
                quantity=100
            )
            db.session.add(product)
            db.session.flush()
            
            warehouse = Warehouse(
                warehouse_name="Inventory Test Warehouse",
                capacity=10000
            )
            db.session.add(warehouse)
            db.session.flush()
            
            # Create inventory
            inventory = Inventory(
                product_id=product.product_id,
                warehouse_id=warehouse.warehouse_id,
                quantity_available=50,
                updated_at=datetime.utcnow()
            )
            db.session.add(inventory)
            db.session.commit()
            inventory_id = inventory.inventory_id
            print(f"   ✓ Inventory created: ID {inventory_id}")
            
            # Verify
            saved = Inventory.query.get(inventory_id)
            assert saved is not None, "Inventory not found"
            assert saved.quantity_available == 50, "Inventory quantity mismatch"
            print(f"   ✓ Inventory verified in database")
            
            # Update inventory
            saved.quantity_available = 75
            saved.updated_at = datetime.utcnow()
            db.session.commit()
            updated = Inventory.query.get(inventory_id)
            assert updated.quantity_available == 75, "Inventory update failed"
            print(f"   ✓ Inventory updated in database")
            
            # Delete
            db.session.delete(saved)
            db.session.delete(product)
            db.session.delete(warehouse)
            db.session.commit()
            print(f"   ✓ Inventory deleted from database")
            print("   ✅ Inventory operations: PASSED\n")
            return True
        except Exception as e:
            print(f"   ✗ Inventory operations failed: {e}\n")
            db.session.rollback()
            return False

def main():
    """Run all tests"""
    results = []
    
    results.append(("User Operations", test_user_operations()))
    results.append(("Product Operations", test_product_operations()))
    results.append(("Warehouse Operations", test_warehouse_operations()))
    results.append(("Cart Operations", test_cart_operations()))
    results.append(("Order Operations", test_order_operations()))
    results.append(("Inventory Operations", test_inventory_operations()))
    
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Database operations are working correctly!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

