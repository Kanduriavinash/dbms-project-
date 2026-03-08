"""
Quick script to check which database is currently being used
"""
import os
from app import create_app

app = create_app()

with app.app_context():
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Unknown')
    
    print("=" * 70)
    print("CURRENT DATABASE CONFIGURATION")
    print("=" * 70)
    print(f"Database URI: {db_uri}")
    print()
    
    if 'sqlite' in db_uri.lower():
        print("CURRENTLY USING: SQLite (sqlite:///rims.db)")
        print()
        print("WARNING: Data is stored in a local SQLite file, NOT PostgreSQL!")
        print()
        print("To switch to PostgreSQL, run:")
        print('  PowerShell: $env:DATABASE_URL="postgresql://postgres:avinash@localhost:5432/retail_db"')
        print('  CMD: set DATABASE_URL=postgresql://postgres:avinash@localhost:5432/retail_db')
        print()
        print("Then restart your application.")
    elif 'postgresql' in db_uri.lower():
        print("CURRENTLY USING: PostgreSQL")
        print()
        if 'retail_db' in db_uri:
            print("Database: retail_db")
        print("All data is being stored in PostgreSQL!")
    else:
        print("Unknown database type")
    
    print("=" * 70)

