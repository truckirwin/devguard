#!/usr/bin/env python3
"""
Script to recreate the database with correct schema.
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.db.database import engine, Base
from app.models.models import User, PPTFile, NoteVersion, SlideImage, PPTAnalysis

def recreate_database():
    """Drop all tables and recreate them with correct schema."""
    
    print("🗑️  Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("🏗️  Creating all tables with correct schema...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database recreated successfully!")
    print("\nTables created:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

if __name__ == "__main__":
    recreate_database() 