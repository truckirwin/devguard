#!/usr/bin/env python3
"""
Script to fix the database schema for slide_images table.
The issue is that the database has 'format' column but model expects 'image_format'.
"""

import os
import sys
import sqlite3
from pathlib import Path

def fix_slide_images_table():
    """Drop and recreate the slide_images table with correct schema."""
    
    # Find the database file - check multiple possible locations
    possible_db_paths = [
        Path("notesgen.db"),
        Path("database.db"),
        Path("NotesGenApp.db"),
        Path("../frontend/notesgen.db")
    ]
    
    db_path = None
    for path in possible_db_paths:
        if path.exists():
            db_path = path
            break
    
    if db_path is None:
        print(f"❌ Database file not found! Checked: {[str(p) for p in possible_db_paths]}")
        return False
    
    print(f"🔍 Using database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking current slide_images table schema...")
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='slide_images'")
        if not cursor.fetchone():
            print("⚠️  slide_images table doesn't exist yet - this is normal for a fresh database")
            conn.close()
            return True
        
        # Check current table schema
        cursor.execute("PRAGMA table_info(slide_images)")
        columns = cursor.fetchall()
        
        print("Current columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Check if we have the wrong column name
        column_names = [col[1] for col in columns]
        has_format = 'format' in column_names
        has_image_format = 'image_format' in column_names
        
        if has_format and not has_image_format:
            print("❌ Found 'format' column instead of 'image_format' - fixing...")
            
            # Backup existing data
            cursor.execute("SELECT COUNT(*) FROM slide_images")
            count = cursor.fetchone()[0]
            print(f"📊 Found {count} existing slide images")
            
            if count > 0:
                print("⚠️  Backing up existing data...")
                cursor.execute("""
                    CREATE TABLE slide_images_backup AS 
                    SELECT * FROM slide_images
                """)
            
            # Drop the old table
            print("🗑️  Dropping old table...")
            cursor.execute("DROP TABLE slide_images")
            
            # Create new table with correct schema
            print("🔨 Creating new table with correct schema...")
            cursor.execute("""
                CREATE TABLE slide_images (
                    id INTEGER PRIMARY KEY,
                    ppt_file_id INTEGER NOT NULL,
                    slide_number INTEGER NOT NULL,
                    image_data BLOB,
                    thumbnail_data BLOB,
                    width INTEGER,
                    height INTEGER,
                    image_format VARCHAR DEFAULT 'PNG',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ppt_file_id) REFERENCES ppt_files (id)
                )
            """)
            
            # Restore data if we had any (mapping old 'format' to new 'image_format')
            if count > 0:
                print("🔄 Restoring data with corrected column names...")
                cursor.execute("""
                    INSERT INTO slide_images 
                    (id, ppt_file_id, slide_number, image_data, thumbnail_data, width, height, image_format, created_at)
                    SELECT 
                        id, ppt_file_id, slide_number, image_data, thumbnail_data, width, height, 
                        COALESCE(format, 'PNG') as image_format, created_at
                    FROM slide_images_backup
                """)
                
                # Drop backup table
                cursor.execute("DROP TABLE slide_images_backup")
                print(f"✅ Restored {count} slide images with corrected schema")
            
            conn.commit()
            print("✅ Database schema fixed successfully!")
            
        elif has_image_format:
            print("✅ Database already has correct 'image_format' column")
        else:
            print("❓ No slide_images table found or unexpected schema")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database schema: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing slide_images database schema...")
    success = fix_slide_images_table()
    if success:
        print("✅ Schema fix completed")
        sys.exit(0)
    else:
        print("❌ Schema fix failed")
        sys.exit(1) 