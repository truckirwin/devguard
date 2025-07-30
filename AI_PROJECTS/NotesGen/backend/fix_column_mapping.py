#!/usr/bin/env python3
"""
Fix database column mapping issue by recreating tables.
This script will drop existing tables and recreate them with correct column names.
"""

import os
import sys
from sqlalchemy import create_engine, text
from app.db.database import Base, engine
from app.models.models import User, PPTFile, NoteVersion, SlideImage, PPTAnalysis, PPTTextCache
from app.core.config import get_settings

def fix_database():
    """Drop and recreate all tables to fix column mapping issues."""
    
    print("🔧 Fixing database column mapping...")
    
    settings = get_settings()
    
    # Drop all tables
    print("📦 Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    # Recreate all tables with correct schema
    print("🏗️ Creating tables with correct schema...")
    Base.metadata.create_all(bind=engine)
    
    # Verify the slide_images table has correct columns
    with engine.connect() as conn:
        if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
            result = conn.execute(text("PRAGMA table_info(slide_images)"))
            columns = [row[1] for row in result]
            print(f"✅ slide_images columns: {columns}")
            
            if "image_format" in columns:
                print("✅ Column 'image_format' exists - mapping should work now")
            else:
                print("❌ Column 'image_format' missing - there's still an issue")
        else:
            # PostgreSQL
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'slide_images'
            """))
            columns = [row[0] for row in result]
            print(f"✅ slide_images columns: {columns}")
    
    print("🎉 Database schema fixed!")

if __name__ == "__main__":
    fix_database() 