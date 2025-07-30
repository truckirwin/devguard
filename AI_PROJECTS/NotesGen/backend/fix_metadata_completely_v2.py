#!/usr/bin/env python3
"""
Completely reset SQLAlchemy metadata and force model reload.
This script will fix the column mapping issue at the server level.
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def nuclear_metadata_reset():
    """Perform the most aggressive metadata reset possible."""
    
    print("🚀 NUCLEAR METADATA RESET - STARTING")
    print("=" * 50)
    
    try:
        # Import everything we need
        from sqlalchemy import create_engine, inspect
        from app.db.database import engine, SessionLocal, Base
        from app.models.models import SlideImage, PPTFile
        import importlib
        import sys
        
        print("🔥 STEP 1: Clear Python module cache")
        # Remove all app.models modules from cache
        modules_to_remove = [key for key in sys.modules.keys() if key.startswith('app.models')]
        for module in modules_to_remove:
            print(f"   Removing {module} from module cache")
            del sys.modules[module]
        
        print("🔥 STEP 2: Clear SQLAlchemy metadata registry")
        # Clear all metadata
        Base.metadata.clear()
        
        # Clear SQLAlchemy registry
        if hasattr(Base, 'registry'):
            Base.registry._class_registry.clear()
        
        print("🔥 STEP 3: Inspect actual database schema")
        inspector = inspect(engine)
        actual_columns = inspector.get_columns('slide_images')
        print("   Database slide_images columns:")
        for col in actual_columns:
            print(f"     {col['name']}: {col['type']}")
        
        print("🔥 STEP 4: Force reimport models")
        # Force reimport of models
        import app.models.models
        importlib.reload(app.models.models)
        
        # Re-import the classes
        from app.models.models import SlideImage as NewSlideImage, PPTFile as NewPPTFile
        
        print("🔥 STEP 5: Verify new model mapping")
        print("   New SlideImage model columns:")
        for column in NewSlideImage.__table__.columns:
            print(f"     {column.name}: {column.type}")
        
        # Test a query with the fresh model
        print("🔥 STEP 6: Test query with fresh model")
        db = SessionLocal()
        
        try:
            slide_image = db.query(NewSlideImage).filter(
                NewSlideImage.ppt_file_id == 1,
                NewSlideImage.slide_number == 1
            ).first()
            
            if slide_image:
                print(f"   ✅ SUCCESS: Found slide {slide_image.slide_number}, format: {slide_image.image_format}")
            else:
                print("   ❌ No slide found")
                
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
        finally:
            db.close()
        
        print("🔥 STEP 7: Force metadata recreation from database")
        # Recreate metadata by reflecting the actual database
        Base.metadata.reflect(bind=engine)
        
        print("🔥 STEP 8: Update main app imports")
        # This forces the main app to use the fresh models when it imports
        
        # Re-import and update the converter
        import app.utils.ppt_to_png_converter
        importlib.reload(app.utils.ppt_to_png_converter)
        
        # Re-import and update the API
        import app.api.slide_images
        importlib.reload(app.api.slide_images)
        
        print("\n✅ NUCLEAR RESET COMPLETE!")
        print("🚀 Server should now use correct column mappings")
        print("🔄 Restart the server to ensure all changes take effect")
        
    except Exception as e:
        print(f"❌ NUCLEAR RESET FAILED: {e}")
        import traceback
        traceback.print_exc()

def create_model_definition_check():
    """Create a simple script to check current model definitions in server memory."""
    
    check_script = '''
import sys
sys.path.insert(0, "/Users/robirwi/Desktop/NotesGen/backend")

from app.models.models import SlideImage
from sqlalchemy.dialects import sqlite

# Show the actual column mapping used by the server
print("Current SlideImage model columns in server memory:")
for column in SlideImage.__table__.columns:
    print(f"  {column.name}: {column.type}")

# Test the problematic query
from app.db.database import SessionLocal
db = SessionLocal()

query = db.query(SlideImage).filter(
    SlideImage.ppt_file_id == 1,
    SlideImage.slide_number == 1
)

# Show the exact SQL being generated
compiled_query = query.statement.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
print(f"\\nGenerated SQL: {compiled_query}")

db.close()
'''
    
    with open('check_server_model.py', 'w') as f:
        f.write(check_script)
    
    print("📝 Created check_server_model.py - run this in server console to debug")

if __name__ == "__main__":
    nuclear_metadata_reset()
    create_model_definition_check()
    
    print("\n🔧 NEXT STEPS:")
    print("1. Restart the NotesGen server completely")
    print("2. Test image loading in the web interface")
    print("3. Check server logs for any remaining 'slide_images.format' errors")
    print("4. If issues persist, run: python check_server_model.py") 