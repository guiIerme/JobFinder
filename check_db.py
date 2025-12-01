import sqlite3
import os

# Check if database exists
if os.path.exists('db.sqlite3'):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    
    print("All tables in database:")
    for table in tables:
        print(f"  - {table}")
    
    # Check for specific tables from migration 0017
    migration_tables = [
        'services_achievement',
        'services_notification',
        'services_servicerequest',
        'services_userachievement'
    ]
    
    print(f"\nTables from migration 0017:")
    for table in migration_tables:
        exists = table in tables
        print(f"  - {table}: {'EXISTS' if exists else 'MISSING'}")
    
    conn.close()
else:
    print("Database file db.sqlite3 does not exist")