"""
Interactive script to set up PostgreSQL connection
"""
import os
import sys

def setup_postgresql():
    print("=" * 60)
    print("PostgreSQL Setup for RIMS")
    print("=" * 60)
    print()
    
    # Check if DATABASE_URL is already set
    current_db = os.environ.get('DATABASE_URL', 'NOT SET')
    print(f"Current DATABASE_URL: {current_db}")
    print()
    
    if 'postgresql' in current_db.lower():
        print("✓ PostgreSQL is already configured!")
        response = input("Do you want to change it? (y/n): ")
        if response.lower() != 'y':
            return
    
    print("Please enter your PostgreSQL connection details:")
    print()
    
    username = input("PostgreSQL Username [postgres]: ").strip() or "postgres"
    password = input("PostgreSQL Password: ").strip()
    if not password:
        print("Error: Password is required!")
        return
    
    host = input("Host [localhost]: ").strip() or "localhost"
    port = input("Port [5432]: ").strip() or "5432"
    database = input("Database Name [rims_db]: ").strip() or "rims_db"
    
    # Build connection string
    database_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    print()
    print("=" * 60)
    print("Connection String:")
    print("=" * 60)
    print(database_url)
    print("=" * 60)
    print()
    
    # Test connection
    print("Testing connection...")
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database
        )
        conn.close()
        print("✓ Connection successful!")
    except ImportError:
        print("⚠ psycopg2 not installed, skipping connection test")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nPlease check:")
        print("  1. PostgreSQL is running")
        print("  2. Database exists (CREATE DATABASE rims_db;)")
        print("  3. Username and password are correct")
        return
    
    print()
    print("=" * 60)
    print("SETUP INSTRUCTIONS")
    print("=" * 60)
    print()
    print("Copy and run ONE of these commands in your terminal:")
    print()
    print("Windows PowerShell:")
    print(f'  $env:DATABASE_URL="{database_url}"')
    print()
    print("Windows CMD:")
    print(f'  set DATABASE_URL={database_url}')
    print()
    print("Linux/Mac:")
    print(f'  export DATABASE_URL="{database_url}"')
    print()
    print("Then run:")
    print("  python check_database.py")
    print("  python setup_database.py")
    print("  python app.py")
    print()
    print("=" * 60)

if __name__ == '__main__':
    setup_postgresql()

