#!/usr/bin/env python3
"""
Database migration script to add caching features.
Adds columns for tracking cached images/text and creates PPTTextCache table.
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.db.database import engine, Base
from app.models.models import PPTFile, PPTTextCache
from sqlalchemy import text

def migrate_database():
    """Add new caching columns and table to existing database."""
    
    print("🔄 Running database migration for caching features...")
    
    try:
        with engine.connect() as conn:
            # Add new columns to ppt_files table
            try:
                print("📝 Adding caching columns to ppt_files table...")
                conn.execute(text("ALTER TABLE ppt_files ADD COLUMN images_cached BOOLEAN DEFAULT FALSE"))
                conn.execute(text("ALTER TABLE ppt_files ADD COLUMN text_cached BOOLEAN DEFAULT FALSE")) 
                conn.execute(text("ALTER TABLE ppt_files ADD COLUMN last_modified DATETIME DEFAULT CURRENT_TIMESTAMP"))
                conn.execute(text("ALTER TABLE ppt_files ADD COLUMN content_hash VARCHAR"))
                conn.commit()
                print("✅ Added caching columns to ppt_files table")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print("ℹ️  Caching columns already exist in ppt_files table")
                else:
                    print(f"⚠️  Warning adding columns to ppt_files: {e}")
            
            # Create PPTTextCache table
            try:
                print("📝 Creating ppt_text_cache table...")
                Base.metadata.create_all(bind=engine, tables=[PPTTextCache.__table__])
                print("✅ Created ppt_text_cache table")
            except Exception as e:
                print(f"ℹ️  Text cache table may already exist: {e}")
        
        print("🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        return False

if __name__ == "__main__":
    migrate_database() 