#!/usr/bin/env python3
"""
Debug script to identify the caching SQL column mapping issue.
This script mimics the exact same queries that the main app uses.
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.database import get_db
from app.models.models import SlideImage, PPTFile
from app.core.config import get_settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_raw_sql_queries():
    """Test raw SQL queries to identify the column mapping issue."""
    
    try:
        # Create engine and session (same as main app)
        from app.db.database import engine, SessionLocal
        db = SessionLocal()
        
        settings = get_settings()
        
        print("=== DEBUGGING CACHE SQL QUERIES ===")
        print(f"Database URL: {settings.SQLALCHEMY_DATABASE_URI}")
        print()
        
        # Test 1: Basic PPT file query
        print("🔍 TEST 1: Query PPT files")
        ppt_files = db.query(PPTFile).limit(5).all()
        for ppt_file in ppt_files:
            print(f"  PPT {ppt_file.id}: {ppt_file.filename} (cached: {ppt_file.images_cached})")
        print()
        
        # Test 2: Raw SQL query to check actual column names
        print("🔍 TEST 2: Check actual table schema")
        result = db.execute(text("PRAGMA table_info(slide_images)"))
        columns = result.fetchall()
        print("  slide_images table columns:")
        for col in columns:
            print(f"    {col[1]} ({col[2]})")  # column name and type
        print()
        
        # Test 3: Raw SQL query with manual column selection
        print("🔍 TEST 3: Manual SQL query with correct column names")
        try:
            result = db.execute(text("""
                SELECT id, ppt_file_id, slide_number, width, height, image_format, created_at
                FROM slide_images 
                WHERE ppt_file_id = 1 AND slide_number = 1
                LIMIT 1
            """))
            row = result.fetchone()
            if row:
                print(f"  Manual query SUCCESS: Found slide {row[2]} for PPT {row[1]}")
                print(f"    Dimensions: {row[3]}x{row[4]}, Format: {row[5]}")
            else:
                print("  Manual query: No results found")
        except Exception as e:
            print(f"  Manual query FAILED: {e}")
        print()
        
        # Test 4: SQLAlchemy query using the model
        print("🔍 TEST 4: SQLAlchemy model query (this is where it might fail)")
        try:
            slide_image = db.query(SlideImage).filter(
                SlideImage.ppt_file_id == 1,
                SlideImage.slide_number == 1
            ).first()
            
            if slide_image:
                print(f"  SQLAlchemy query SUCCESS: Found slide {slide_image.slide_number} for PPT {slide_image.ppt_file_id}")
                print(f"    Dimensions: {slide_image.width}x{slide_image.height}, Format: {slide_image.image_format}")
                print(f"    Image data: {len(slide_image.image_data) if slide_image.image_data else 0} bytes")
                print(f"    Thumbnail data: {len(slide_image.thumbnail_data) if slide_image.thumbnail_data else 0} bytes")
            else:
                print("  SQLAlchemy query: No results found")
                
        except Exception as e:
            print(f"  SQLAlchemy query FAILED: {e}")
            print(f"    Error type: {type(e).__name__}")
            if hasattr(e, 'orig'):
                print(f"    Original error: {e.orig}")
        print()
        
        # Test 5: Show generated SQL
        print("🔍 TEST 5: Show generated SQL for problematic query")
        try:
            from sqlalchemy.dialects import sqlite
            query = db.query(SlideImage).filter(
                SlideImage.ppt_file_id == 1,
                SlideImage.slide_number == 1
            )
            compiled_query = query.statement.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
            print("  Generated SQL:")
            print(f"    {compiled_query}")
        except Exception as e:
            print(f"  Failed to show SQL: {e}")
        print()
        
        # Test 6: Check model attributes
        print("🔍 TEST 6: Check SlideImage model attributes")
        print("  SlideImage model columns:")
        for column in SlideImage.__table__.columns:
            print(f"    {column.name}: {column.type}")
        print()
        
        # Test 7: Force SQLAlchemy metadata refresh
        print("🔍 TEST 7: Force SQLAlchemy metadata refresh")
        try:
            from app.models.models import Base
            from sqlalchemy import MetaData
            
            # Clear metadata
            Base.metadata.clear()
            
            # Recreate metadata from database
            Base.metadata.reflect(bind=engine)
            
            print("  Metadata refreshed successfully")
            
            # Try the query again
            slide_image = db.query(SlideImage).filter(
                SlideImage.ppt_file_id == 1,
                SlideImage.slide_number == 1
            ).first()
            
            if slide_image:
                print(f"  Post-refresh query SUCCESS: Found slide {slide_image.slide_number}")
            else:
                print("  Post-refresh query: No results found")
                
        except Exception as e:
            print(f"  Metadata refresh FAILED: {e}")
        
        db.close()
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

def test_converter_image_retrieval():
    """Test the exact same image retrieval method used by the main app."""
    
    print("\n=== TESTING CONVERTER IMAGE RETRIEVAL ===")
    
    try:
        from app.utils.ppt_to_png_converter import PPTToPNGConverter
        from app.db.database import SessionLocal
        
        db = SessionLocal()
        converter = PPTToPNGConverter()
        
        # Test the exact same method that fails in production
        image_bytes = converter.get_slide_image(1, 1, db, thumbnail=False)
        
        if image_bytes:
            print(f"✅ CONVERTER SUCCESS: Retrieved image ({len(image_bytes)} bytes)")
        else:
            print("❌ CONVERTER FAILED: No image data returned")
            
        db.close()
        
    except Exception as e:
        print(f"❌ CONVERTER EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🐛 DEBUG: NotesGen Cache Issue Diagnosis")
    print("=" * 50)
    
    test_raw_sql_queries()
    test_converter_image_retrieval()
    
    print("\n" + "=" * 50)
    print("�� DEBUG COMPLETE") 