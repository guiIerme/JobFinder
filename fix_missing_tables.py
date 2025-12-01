import sqlite3
import os

if os.path.exists('db.sqlite3'):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    try:
        # Create services_achievement table
        print("Creating services_achievement table...")
        cursor.execute('''
            CREATE TABLE "services_achievement" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
                "name" varchar(100) NOT NULL, 
                "description" text NOT NULL, 
                "icon" varchar(50) NOT NULL, 
                "points" integer unsigned NOT NULL CHECK ("points" >= 0), 
                "category" varchar(50) NOT NULL, 
                "created_at" datetime NOT NULL
            )
        ''')
        

        
        # Create services_userachievement table
        print("Creating services_userachievement table...")
        cursor.execute('''
            CREATE TABLE "services_userachievement" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
                "earned_at" datetime NOT NULL, 
                "progress" integer unsigned NOT NULL CHECK ("progress" >= 0), 
                "target" integer unsigned NOT NULL CHECK ("target" >= 0), 
                "achievement_id" bigint NOT NULL REFERENCES "services_achievement" ("id") DEFERRABLE INITIALLY DEFERRED, 
                "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
            )
        ''')
        
        # Create indexes
        print("Creating indexes...")

        cursor.execute('CREATE UNIQUE INDEX "services_userachievement_user_id_achievement_id_647d88a3_uniq" ON "services_userachievement" ("user_id", "achievement_id")')
        cursor.execute('CREATE INDEX "services_userachievement_achievement_id_3d298f9c" ON "services_userachievement" ("achievement_id")')
        cursor.execute('CREATE INDEX "services_userachievement_user_id_3832a24e" ON "services_userachievement" ("user_id")')
        
        conn.commit()
        print("Successfully created missing tables!")
        
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
    
    finally:
        conn.close()
else:
    print("Database file db.sqlite3 does not exist")