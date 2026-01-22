#!/usr/bin/env python3
"""Database Initialization Script

This script initializes the database with schema and sample data.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def get_db_params():
    """Get database connection parameters from environment."""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'ramayana_training'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', '')
    }

def create_database():
    """Create the database if it doesn't exist."""
    params = get_db_params()
    db_name = params.pop('database')
    
    try:
        conn = psycopg2.connect(**params, database='postgres')
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE {db_name}')
            print(f"✅ Database '{db_name}' created successfully!")
        else:
            print(f"ℹ️  Database '{db_name}' already exists.")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def run_sql_file(filepath):
    """Execute SQL commands from a file."""
    params = get_db_params()
    
    try:
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        
        with open(filepath, 'r') as f:
            sql = f.read()
            cursor.execute(sql)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Executed {filepath} successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error executing {filepath}: {e}")
        return False

def initialize_database():
    """Initialize the database with schema and sample data."""
    print("�� Initializing Ramayana Sustainability Training Database...\n")
    
    # Create database
    print("Step 1: Creating database...")
    if not create_database():
        sys.exit(1)
    
    # Create schema
    print("\nStep 2: Creating database schema...")
    schema_path = Path(__file__).parent.parent / 'database' / 'schema.sql'
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        sys.exit(1)
    
    if not run_sql_file(schema_path):
        sys.exit(1)
    
    # Load sample data
    print("\nStep 3: Loading sample data...")
    seed_path = Path(__file__).parent.parent / 'database' / 'seed_data.sql'
    if not seed_path.exists():
        print(f"❌ Seed data file not found: {seed_path}")
        sys.exit(1)
    
    if not run_sql_file(seed_path):
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ Database initialization completed successfully!")
    print("="*60)
    print("\n📝 Sample Login Credentials:")
    print("   Username: admin")
    print("   Password: password123")
    print("\n🚀 You can now start the application!")

if __name__ == '__main__':
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed. Using system environment variables.")
    
    initialize_database()