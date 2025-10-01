#!/usr/bin/env python3
"""
Test script to verify Supabase database connection and create a test table.
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

# Load environment variables
load_dotenv()


def test_connection():
    """Test basic database connection."""
    print("=" * 60)
    print("Testing Supabase Database Connection")
    print("=" * 60)
    print()
    
    # Check if environment variable exists
    db_url = os.getenv("LOCAL_DATABASE_URL")
    if not db_url:
        print("❌ ERROR: LOCAL_DATABASE_URL not found in .env file")
        print()
        print("Please create a .env file with:")
        print("LOCAL_DATABASE_URL=postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres")
        return False
    
    # Hide password in output
    safe_url = db_url.split('@')[1] if '@' in db_url else db_url
    print(f"📡 Connecting to: ...@{safe_url}")
    print()
    
    try:
        # Attempt connection
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print("✅ Connection successful!")
        print(f"   PostgreSQL version: {version.split(',')[0]}")
        print()
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print("❌ Connection failed!")
        print(f"   Error: {e}")
        print()
        print("Common issues:")
        print("  • Wrong password in connection string")
        print("  • Incorrect database URL")
        print("  • Firewall/network blocking connection")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def create_test_table():
    """Create a test table and perform basic operations."""
    print("=" * 60)
    print("Creating Test Table")
    print("=" * 60)
    print()
    
    db_url = os.getenv("LOCAL_DATABASE_URL")
    
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Drop test table if it exists
        print("🗑️  Dropping existing test_table if it exists...")
        cursor.execute("DROP TABLE IF EXISTS test_table CASCADE;")
        print("   Done")
        print()
        
        # Create test table
        print("📝 Creating test_table...")
        cursor.execute("""
            CREATE TABLE test_table (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("   ✅ Table created")
        print()
        
        # Insert test data
        print("📥 Inserting test data...")
        test_data = [
            ("Alice Johnson", "alice@example.com"),
            ("Bob Smith", "bob@example.com"),
            ("Charlie Brown", "charlie@example.com")
        ]
        
        for name, email in test_data:
            cursor.execute(
                "INSERT INTO test_table (name, email) VALUES (%s, %s);",
                (name, email)
            )
            print(f"   Added: {name}")
        print()
        
        # Read data back
        print("📤 Reading data back from test_table...")
        cursor.execute("SELECT id, name, email, created_at FROM test_table ORDER BY id;")
        rows = cursor.fetchall()
        
        print()
        print("   ID | Name            | Email")
        print("   " + "-" * 50)
        for row in rows:
            print(f"   {row[0]:2} | {row[1]:15} | {row[2]}")
        print()
        
        # Count rows
        cursor.execute("SELECT COUNT(*) FROM test_table;")
        count = cursor.fetchone()[0]
        print(f"   ✅ Successfully read {count} rows")
        print()
        
        # Ask if user wants to keep or delete the test table
        print("🤔 What would you like to do with test_table?")
        print("   1. Keep it (you can view it in Supabase Table Editor)")
        print("   2. Delete it (clean up)")
        print()
        
        choice = input("   Enter choice [1]: ").strip() or "1"
        
        if choice == "2":
            cursor.execute("DROP TABLE test_table CASCADE;")
            print()
            print("   🗑️  test_table deleted")
        else:
            print()
            print("   💾 test_table kept - view it in Supabase Dashboard → Table Editor")
        
        print()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating test table: {e}")
        return False


def check_main_tables():
    """Check if main project tables exist."""
    print("=" * 60)
    print("Checking Main Project Tables")
    print("=" * 60)
    print()
    
    db_url = os.getenv("LOCAL_DATABASE_URL")
    expected_tables = ["case_detail", "disposition", "event", "setting"]
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Query for existing tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print("Tables found in your database:")
        for table in existing_tables:
            status = "✅" if table in expected_tables else "ℹ️"
            print(f"  {status} {table}")
        
        print()
        
        # Check for missing tables
        missing = [t for t in expected_tables if t not in existing_tables]
        
        if missing:
            print(f"⚠️  Missing project tables: {', '.join(missing)}")
            print()
            print("To create them, run this in Supabase SQL Editor:")
            print("  → sql/init_supabase.sql")
        else:
            print("✅ All main project tables exist!")
        
        print()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")


def main():
    """Run all tests."""
    print()
    
    # Test 1: Basic connection
    if not test_connection():
        print("⚠️  Please fix connection issues before proceeding.")
        sys.exit(1)
    
    # Test 2: Create test table
    print()
    create_test_table()
    
    # Test 3: Check main tables
    print()
    check_main_tables()
    
    print()
    print("=" * 60)
    print("✅ All Tests Complete!")
    print("=" * 60)
    print()
    print("Your database connection is working correctly.")
    print("You're ready to start scraping data!")
    print()


if __name__ == "__main__":
    main()

