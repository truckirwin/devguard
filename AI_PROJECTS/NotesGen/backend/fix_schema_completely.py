#!/usr/bin/env python3
"""
Fix database schema completely by dropping and recreating all tables.
This ensures that the column mapping issue with slide_images.format is resolved.
"""

import os
import sqlite3
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.db.database import engine, Base
from app.models.models import User, PPTFile, NoteVersion, SlideImage, PPTTextCache, PPTAnalysis

def main():
    print("🔄 Completely recreating database schema...")
    
    # Database file path
    db_path = backend_dir / "notesgen.db"
    
    try:
        # Drop all tables by recreating the database file
        if db_path.exists():
            print(f"📁 Removing existing database: {db_path}")
            os.remove(db_path)
        
        # Recreate all tables with correct schema
        print("📊 Creating all tables with correct schema...")
        Base.metadata.create_all(bind=engine)
        
        # Verify the schema
        print("\n✅ Verifying slide_images table schema:")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("PRAGMA table_info(slide_images);")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"   {col[1]} ({col[2]})")
                
            # Check specifically for image_format column
            column_names = [col[1] for col in columns]
            if 'image_format' in column_names:
                print("✅ image_format column exists")
            else:
                print("❌ image_format column missing")
                
            if 'format' in column_names:
                print("❌ Old 'format' column still exists - this should not happen")
            else:
                print("✅ Old 'format' column does not exist")
        
        print("\n🎉 Database schema completely recreated successfully!")
        print("The slide_images.format column mapping issue should now be resolved.")
        
    except Exception as e:
        print(f"❌ Error recreating database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 