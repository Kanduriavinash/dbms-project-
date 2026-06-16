import os
class Config:
    # PostgreSQL connection string format: postgresql://username:password@host:port/database
    # Default to PostgreSQL (can be overridden by DATABASE_URL environment variable)
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:avinash@localhost:5432/retail_db')
    
    # Ensure we handle postgres:// (common in Render/Heroku) and map to postgresql+psycopg2://
    if DATABASE_URL:
        # Replace postgres:// with postgresql:// if present
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
            
        # Ensure psycopg2 driver is used for PostgreSQL
        if DATABASE_URL.startswith('postgresql://'):
            SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg2://', 1)
        elif DATABASE_URL.startswith('postgresql+psycopg2://'):
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
        else:
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///rims.db'
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # Set to True for SQL query debugging - ENABLED TO SEE QUERIES

