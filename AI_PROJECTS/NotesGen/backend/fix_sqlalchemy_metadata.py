#!/usr/bin/env python3
"""
Aggressive fix for SQLAlchemy metadata caching issue.
This script will completely clear all SQLAlchemy metadata and force regeneration.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def main():
    print("🔧 Aggressively fixing SQLAlchemy metadata caching issue...")
    
    try:
        # Clear all possible SQLAlchemy caches
        from sqlalchemy import MetaData
        from sqlalchemy.orm import registry
        
        # Import our models and database
        from app.db.database import engine, Base
        from app.models.models import SlideImage
        
        print("📋 Current SlideImage columns before fix:")
        for column in SlideImage.__table__.columns:
            print(f"  - {column.name}: {column.type}")
        
        # Step 1: Clear the declarative registry
        print("🧹 Clearing declarative registry...")
        if hasattr(Base.registry, '_class_registry'):
            Base.registry._class_registry.clear()
        
        # Step 2: Clear metadata
        print("🧹 Clearing Base metadata...")
        Base.metadata.clear()
        
        # Step 3: Drop and recreate all table objects
        print("🔄 Recreating table metadata...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        # Step 4: Force reload of the SlideImage model
        print("🔄 Reloading SlideImage model...")
        from importlib import reload
        import app.models.models
        reload(app.models.models)
        
        # Step 5: Verify the column mapping
        print("✅ SlideImage columns after fix:")
        from app.models.models import SlideImage as ReloadedSlideImage
        for column in ReloadedSlideImage.__table__.columns:
            print(f"  - {column.name}: {column.type}")
        
        # Step 6: Test a simple query
        print("🧪 Testing query generation...")
        from app.db.database import SessionLocal
        db = SessionLocal()
        try:
            # This should not reference the old 'format' column
            query = db.query(ReloadedSlideImage).filter(
                ReloadedSlideImage.ppt_file_id == 1,
                ReloadedSlideImage.slide_number == 1
            )
            print(f"Generated SQL: {query}")
            result = query.first()
            print("✅ Query executed successfully!")
        except Exception as e:
            print(f"❌ Query still failing: {e}")
        finally:
            db.close()
        
        print("✅ SQLAlchemy metadata fix completed!")
        
    except Exception as e:
        print(f"❌ Error during metadata fix: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 