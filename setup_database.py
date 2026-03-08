"""
Database setup script for RIMS
Creates database tables and optionally seeds initial data.
"""
import os
from app import create_app
from extensions import db
from models import *

def setup_database():
    """Create all database tables."""
    app = create_app()
    with app.app_context():
        print("Creating database tables...")
        try:
            db.create_all()
            print("✓ Database tables created successfully!")
            return True
        except Exception as e:
            print(f"✗ Error creating tables: {e}")
            return False

def check_connection():
    """Check database connection."""
    app = create_app()
    with app.app_context():
        try:
            db.engine.connect()
            print("✓ Database connection successful!")
            print(f"  Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            print("\nPlease check:")
            print("  1. PostgreSQL is running")
            print("  2. DATABASE_URL environment variable is set correctly")
            print("  3. Database exists and user has permissions")
            return False

if __name__ == '__main__':
    print("=" * 50)
    print("RIMS Database Setup")
    print("=" * 50)
    
    if not check_connection():
        print("\nCannot proceed without database connection.")
        exit(1)
    
    print()
    if setup_database():
        print("\n" + "=" * 50)
        print("Database setup complete!")
        print("=" * 50)
        print("\nNext steps:")
        print("  1. Run 'python seed_data.py' to add sample data")
        print("  2. Run 'python app.py' to start the application")
    else:
        print("\nDatabase setup failed. Please check the errors above.")
        exit(1)

