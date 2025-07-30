#!/usr/bin/env python3
"""
Complete migration script from SQLite to PostgreSQL.

This script performs a full data migration from the old SQLite database
to the new PostgreSQL database, ensuring all data is preserved and 
the application is ready for production use.

CRITICAL: This migration resolves the "Server unavailable" issues caused by:
1. SQLite concurrency limitations
2. Column mapping errors (format vs image_format)
3. Database locking during heavy image processing
4. Performance issues with large PPT files

Run this script ONCE to migrate your data, then PostgreSQL will be used exclusively.
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_prerequisites():
    """Check that PostgreSQL is ready and SQLite data exists."""
    logger.info("🔍 Checking migration prerequisites...")
    
    # Check if SQLite database exists
    sqlite_path = backend_dir / "notesgen.db"
    if not sqlite_path.exists():
        logger.warning(f"⚠️ SQLite database not found at {sqlite_path}")
        logger.info("This appears to be a fresh installation - no migration needed")
        return False
    
    # Check PostgreSQL connection
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        # This will validate PostgreSQL connection
        from app.db.database import engine
        with engine.connect() as conn:
            result = conn.execute("SELECT version()").scalar()
            if "PostgreSQL" in result:
                logger.info(f"✅ PostgreSQL connection verified: {result.split(',')[0]}")
                return True
            else:
                logger.error(f"❌ Expected PostgreSQL but got: {result}")
                return False
                
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        logger.error("Please ensure PostgreSQL is running and properly configured")
        return False

def create_postgresql_database():
    """Create PostgreSQL database schema."""
    logger.info("🏗️ Creating PostgreSQL database schema...")
    
    try:
        from app.db.database import Base, engine
        from app.models.models import User, PPTFile, NoteVersion, SlideImage, PPTAnalysis, PPTTextCache
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ PostgreSQL schema created successfully")
        
        # Verify schema
        with engine.connect() as conn:
            tables = conn.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """).fetchall()
            
            table_names = [row[0] for row in tables]
            expected_tables = ['users', 'ppt_files', 'note_versions', 'slide_images', 'ppt_analyses', 'ppt_text_cache']
            
            for table in expected_tables:
                if table in table_names:
                    logger.info(f"   ✅ Table '{table}' created")
                else:
                    logger.error(f"   ❌ Table '{table}' missing")
                    return False
                    
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create PostgreSQL schema: {e}")
        return False

def extract_sqlite_data():
    """Extract all data from SQLite database."""
    logger.info("📦 Extracting data from SQLite database...")
    
    sqlite_path = backend_dir / "notesgen.db"
    
    try:
        conn = sqlite3.connect(str(sqlite_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        
        data = {}
        
        # Extract users
        logger.info("   📊 Extracting users...")
        users = conn.execute("SELECT * FROM users").fetchall()
        data['users'] = [dict(row) for row in users]
        logger.info(f"   Found {len(data['users'])} users")
        
        # Extract PPT files
        logger.info("   📊 Extracting PPT files...")
        ppt_files = conn.execute("SELECT * FROM ppt_files").fetchall()
        data['ppt_files'] = [dict(row) for row in ppt_files]
        logger.info(f"   Found {len(data['ppt_files'])} PPT files")
        
        # Extract note versions
        logger.info("   📊 Extracting note versions...")
        note_versions = conn.execute("SELECT * FROM note_versions").fetchall()
        data['note_versions'] = [dict(row) for row in note_versions]
        logger.info(f"   Found {len(data['note_versions'])} note versions")
        
        # Extract slide images (handle column mapping issue)
        logger.info("   📊 Extracting slide images...")
        try:
            # Try new column name first
            slide_images = conn.execute("SELECT * FROM slide_images").fetchall()
        except sqlite3.OperationalError as e:
            if "no such column" in str(e):
                logger.warning("   ⚠️ Detected column mapping issue - attempting fix...")
                # Try with explicit column selection
                slide_images = conn.execute("""
                    SELECT id, ppt_file_id, slide_number, image_data, thumbnail_data, 
                           width, height, 
                           CASE 
                               WHEN format IS NOT NULL THEN format 
                               ELSE image_format 
                           END as image_format,
                           created_at
                    FROM slide_images
                """).fetchall()
            else:
                raise
                
        data['slide_images'] = [dict(row) for row in slide_images]
        logger.info(f"   Found {len(data['slide_images'])} slide images")
        
        # Extract PPT analyses (if table exists)
        logger.info("   📊 Extracting PPT analyses...")
        try:
            ppt_analyses = conn.execute("SELECT * FROM ppt_analyses").fetchall()
            data['ppt_analyses'] = [dict(row) for row in ppt_analyses]
            logger.info(f"   Found {len(data['ppt_analyses'])} PPT analyses")
        except sqlite3.OperationalError:
            logger.info("   No PPT analyses table found (normal for older databases)")
            data['ppt_analyses'] = []
            
        # Extract text cache (if table exists)
        logger.info("   📊 Extracting text cache...")
        try:
            text_cache = conn.execute("SELECT * FROM ppt_text_cache").fetchall()
            data['ppt_text_cache'] = [dict(row) for row in text_cache]
            logger.info(f"   Found {len(data['ppt_text_cache'])} text cache entries")
        except sqlite3.OperationalError:
            logger.info("   No text cache table found (normal for older databases)")
            data['ppt_text_cache'] = []
        
        conn.close()
        logger.info("✅ SQLite data extraction completed")
        return data
        
    except Exception as e:
        logger.error(f"❌ Failed to extract SQLite data: {e}")
        return None

def insert_postgresql_data(data: Dict[str, List[Dict[str, Any]]]):
    """Insert extracted data into PostgreSQL."""
    logger.info("📥 Inserting data into PostgreSQL...")
    
    try:
        from app.db.database import SessionLocal
        from app.models.models import User, PPTFile, NoteVersion, SlideImage, PPTAnalysis, PPTTextCache
        
        db = SessionLocal()
        
        try:
            # Insert users
            logger.info("   👤 Inserting users...")
            for user_data in data['users']:
                user = User(
                    id=user_data['id'],
                    username=user_data['username'],
                    hashed_password=user_data['hashed_password'],
                    home_directory=user_data['home_directory'],
                    created_at=datetime.fromisoformat(user_data['created_at']) if user_data['created_at'] else datetime.utcnow()
                )
                db.merge(user)  # Use merge to handle existing records
            
            # Insert PPT files
            logger.info("   📄 Inserting PPT files...")
            for ppt_data in data['ppt_files']:
                ppt_file = PPTFile(
                    id=ppt_data['id'],
                    user_id=ppt_data['user_id'],
                    filename=ppt_data['filename'],
                    path=ppt_data['path'],
                    size=ppt_data['size'],
                    created_at=datetime.fromisoformat(ppt_data['created_at']) if ppt_data['created_at'] else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(ppt_data['updated_at']) if ppt_data.get('updated_at') else datetime.utcnow(),
                    images_cached=bool(ppt_data.get('images_cached', False)),
                    text_cached=bool(ppt_data.get('text_cached', False)),
                    last_modified=datetime.fromisoformat(ppt_data['last_modified']) if ppt_data.get('last_modified') else datetime.utcnow(),
                    content_hash=ppt_data.get('content_hash')
                )
                db.merge(ppt_file)
            
            # Insert note versions
            logger.info("   📝 Inserting note versions...")
            for note_data in data['note_versions']:
                note = NoteVersion(
                    id=note_data['id'],
                    ppt_file_id=note_data['ppt_file_id'],
                    version_number=note_data['version_number'],
                    content=note_data['content'],
                    ai_model=note_data.get('ai_model'),
                    ai_temperature=note_data.get('ai_temperature'),
                    created_at=datetime.fromisoformat(note_data['created_at']) if note_data['created_at'] else datetime.utcnow()
                )
                db.merge(note)
            
            # Insert slide images (CRITICAL: Fixed column mapping)
            logger.info("   🖼️ Inserting slide images...")
            for slide_data in data['slide_images']:
                slide = SlideImage(
                    id=slide_data['id'],
                    ppt_file_id=slide_data['ppt_file_id'],
                    slide_number=slide_data['slide_number'],
                    image_data=slide_data['image_data'],
                    thumbnail_data=slide_data.get('thumbnail_data'),
                    width=slide_data['width'],
                    height=slide_data['height'],
                    image_format=slide_data.get('image_format', 'PNG'),  # FIXED: Use image_format, not format
                    created_at=datetime.fromisoformat(slide_data['created_at']) if slide_data['created_at'] else datetime.utcnow()
                )
                db.merge(slide)
            
            # Insert PPT analyses
            logger.info("   📊 Inserting PPT analyses...")
            for analysis_data in data['ppt_analyses']:
                analysis = PPTAnalysis(
                    id=analysis_data['id'],
                    ppt_file_id=analysis_data['ppt_file_id'],
                    total_slides=analysis_data.get('total_slides'),
                    total_objects=analysis_data.get('total_objects'),
                    slides_with_tab_order=analysis_data.get('slides_with_tab_order', 0),
                    slides_with_accessibility=analysis_data.get('slides_with_accessibility', 0),
                    total_issues=analysis_data.get('total_issues', 0),
                    file_size_mb=analysis_data.get('file_size_mb'),
                    slide_dimensions=analysis_data.get('slide_dimensions'),
                    has_animations=bool(analysis_data.get('has_animations', False)),
                    has_transitions=bool(analysis_data.get('has_transitions', False)),
                    has_embedded_media=bool(analysis_data.get('has_embedded_media', False)),
                    slide_layouts_used=analysis_data.get('slide_layouts_used'),
                    theme_name=analysis_data.get('theme_name'),
                    color_scheme=analysis_data.get('color_scheme'),
                    font_usage=analysis_data.get('font_usage'),
                    accessibility_score=analysis_data.get('accessibility_score'),
                    missing_alt_text_count=analysis_data.get('missing_alt_text_count', 0),
                    color_contrast_issues=analysis_data.get('color_contrast_issues', 0),
                    reading_order_issues=analysis_data.get('reading_order_issues', 0),
                    image_quality_score=analysis_data.get('image_quality_score'),
                    text_readability_score=analysis_data.get('text_readability_score'),
                    design_consistency_score=analysis_data.get('design_consistency_score'),
                    estimated_load_time=analysis_data.get('estimated_load_time'),
                    complexity_score=analysis_data.get('complexity_score'),
                    slide_analyses=analysis_data.get('slide_analyses'),
                    recommendations=analysis_data.get('recommendations'),
                    created_at=datetime.fromisoformat(analysis_data['created_at']) if analysis_data['created_at'] else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(analysis_data['updated_at']) if analysis_data.get('updated_at') else datetime.utcnow()
                )
                db.merge(analysis)
            
            # Insert text cache
            logger.info("   💾 Inserting text cache...")
            for cache_data in data['ppt_text_cache']:
                cache = PPTTextCache(
                    id=cache_data['id'],
                    ppt_file_id=cache_data['ppt_file_id'],
                    text_elements_data=cache_data.get('text_elements_data'),
                    total_slides=cache_data.get('total_slides'),
                    total_text_elements=cache_data.get('total_text_elements'),
                    extraction_version=cache_data.get('extraction_version', '1.0'),
                    created_at=datetime.fromisoformat(cache_data['created_at']) if cache_data['created_at'] else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(cache_data['updated_at']) if cache_data.get('updated_at') else datetime.utcnow()
                )
                db.merge(cache)
            
            # Commit all changes
            db.commit()
            logger.info("✅ All data successfully inserted into PostgreSQL")
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to insert data into PostgreSQL: {e}")
            raise
        finally:
            db.close()
            
        return True
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL data insertion failed: {e}")
        return False

def verify_migration():
    """Verify that migration was successful."""
    logger.info("🔍 Verifying migration...")
    
    try:
        from app.db.database import SessionLocal
        from app.models.models import User, PPTFile, NoteVersion, SlideImage, PPTAnalysis, PPTTextCache
        
        db = SessionLocal()
        
        try:
            # Count records in each table
            user_count = db.query(User).count()
            ppt_count = db.query(PPTFile).count()
            note_count = db.query(NoteVersion).count()
            slide_count = db.query(SlideImage).count()
            analysis_count = db.query(PPTAnalysis).count()
            cache_count = db.query(PPTTextCache).count()
            
            logger.info(f"   👤 Users: {user_count}")
            logger.info(f"   📄 PPT Files: {ppt_count}")
            logger.info(f"   📝 Note Versions: {note_count}")
            logger.info(f"   🖼️ Slide Images: {slide_count}")
            logger.info(f"   📊 PPT Analyses: {analysis_count}")
            logger.info(f"   💾 Text Cache: {cache_count}")
            
            # Test the problematic SlideImage query that was causing errors
            logger.info("   🧪 Testing SlideImage query (the one that was failing)...")
            test_slide = db.query(SlideImage).filter(
                SlideImage.ppt_file_id == 1
            ).first()
            
            if test_slide:
                logger.info(f"   ✅ SlideImage query successful - format: {test_slide.image_format}")
            else:
                logger.info("   ⚠️ No slide images found (normal if no data was migrated)")
            
            logger.info("✅ Migration verification completed successfully")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Migration verification failed: {e}")
        return False

def backup_sqlite_database():
    """Create a backup of the SQLite database before migration."""
    logger.info("💾 Creating SQLite database backup...")
    
    sqlite_path = backend_dir / "notesgen.db"
    backup_path = backend_dir / f"notesgen_sqlite_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    try:
        import shutil
        shutil.copy2(sqlite_path, backup_path)
        logger.info(f"✅ SQLite backup created: {backup_path}")
        return str(backup_path)
    except Exception as e:
        logger.error(f"❌ Failed to create SQLite backup: {e}")
        return None

def main():
    """Main migration process."""
    print("🚀 STARTING SQLITE TO POSTGRESQL MIGRATION")
    print("=" * 60)
    print()
    print("This migration will resolve the following issues:")
    print("• 'Server unavailable' errors during PPT uploads")
    print("• Infinite polling loops for slide images")
    print("• Database locking during heavy processing")
    print("• Column mapping errors (format vs image_format)")
    print()
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        logger.error("❌ Prerequisites not met - aborting migration")
        return False
    
    # Step 2: Create backup
    backup_path = backup_sqlite_database()
    if not backup_path:
        logger.error("❌ Could not create backup - aborting migration")
        return False
    
    # Step 3: Create PostgreSQL schema
    if not create_postgresql_database():
        logger.error("❌ Could not create PostgreSQL schema - aborting migration")
        return False
    
    # Step 4: Extract SQLite data
    data = extract_sqlite_data()
    if not data:
        logger.error("❌ Could not extract SQLite data - aborting migration")
        return False
    
    # Step 5: Insert data into PostgreSQL
    if not insert_postgresql_data(data):
        logger.error("❌ Could not insert data into PostgreSQL - aborting migration")
        return False
    
    # Step 6: Verify migration
    if not verify_migration():
        logger.error("❌ Migration verification failed")
        return False
    
    print()
    print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("✅ Your application is now using PostgreSQL")
    print("✅ All SQLite data has been migrated")
    print("✅ The 'Server unavailable' issues should be resolved")
    print("✅ Column mapping errors are fixed")
    print()
    print(f"📁 SQLite backup saved: {backup_path}")
    print("🔥 You can now delete the old SQLite database: notesgen.db")
    print()
    print("⚠️  IMPORTANT: Do not revert to SQLite - it will cause system failures")
    print("PostgreSQL is now required for proper operation.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 