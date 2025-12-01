import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

# Read the SQL file
with open('create_tables.sql', 'r') as f:
    sql_script = f.read()

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Execute the SQL script
    cursor.executescript(sql_script)
    conn.commit()
    print("Tables created successfully!")
except Exception as e:
    print(f"Error creating tables: {e}")
finally:
    conn.close()