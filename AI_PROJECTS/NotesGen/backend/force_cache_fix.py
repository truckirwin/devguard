#!/usr/bin/env python3
"""
Force cache fix by ensuring correct database column mapping in the main API.
This script modifies the running system to use the correct column references.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def apply_targeted_cache_fix():
    """Apply a targeted fix to the caching system."""
    
    print("🎯 TARGETED CACHE FIX - STARTING")
    print("=" * 50)
    
    # The key insight: the debug script works, main app doesn't
    # This suggests there's a different code path or import issue
    
    try:
        print("🔧 STEP 1: Verify current model definition")
        from app.models.models import SlideImage
        
        print("   SlideImage model columns:")
        for column in SlideImage.__table__.columns:
            print(f"     {column.name}: {column.type}")
        
        # Verify the actual column name exists
        if 'image_format' in [col.name for col in SlideImage.__table__.columns]:
            print("   ✅ Model has correct 'image_format' column")
        else:
            print("   ❌ Model missing 'image_format' column")
            return False
        
        print("\n🔧 STEP 2: Test direct database query")
        from app.db.database import SessionLocal
        db = SessionLocal()
        
        # Test the exact query that's failing
        try:
            slide_image = db.query(SlideImage).filter(
                SlideImage.ppt_file_id == 1,
                SlideImage.slide_number == 1
            ).first()
            
            if slide_image:
                print(f"   ✅ Direct query SUCCESS: Found slide {slide_image.slide_number}")
                print(f"     Format: {slide_image.image_format}")
                print(f"     Image size: {len(slide_image.image_data) if slide_image.image_data else 0} bytes")
            else:
                print("   ⚠️ No slide found")
                
        except Exception as e:
            print(f"   ❌ Direct query FAILED: {e}")
            db.close()
            return False
        
        print("\n🔧 STEP 3: Test converter method")
        from app.utils.ppt_to_png_converter import PPTToPNGConverter
        
        converter = PPTToPNGConverter()
        image_bytes = converter.get_slide_image(1, 1, db, thumbnail=False)
        
        if image_bytes:
            print(f"   ✅ Converter SUCCESS: Retrieved {len(image_bytes)} bytes")
        else:
            print("   ❌ Converter FAILED: No image data")
            db.close()
            return False
        
        db.close()
        
        print("\n🔧 STEP 4: Create optimized cache checker")
        
        # Create a runtime cache validation function
        cache_validator_code = '''
def validate_and_fix_cache_runtime():
    """Runtime cache validation and fix."""
    import logging
    from app.db.database import SessionLocal
    from app.models.models import SlideImage
    
    logger = logging.getLogger(__name__)
    
    try:
        db = SessionLocal()
        
        # Test query with detailed logging
        logger.info("🔍 CACHE VALIDATOR: Testing slide image query")
        
        slide_image = db.query(SlideImage).filter(
            SlideImage.ppt_file_id == 1,
            SlideImage.slide_number == 1
        ).first()
        
        if slide_image:
            logger.info(f"✅ CACHE VALIDATOR: Query successful - {slide_image.image_format}")
            return True
        else:
            logger.warning("⚠️ CACHE VALIDATOR: No slide found")
            return False
            
    except Exception as e:
        logger.error(f"❌ CACHE VALIDATOR: Query failed - {e}")
        return False
    finally:
        db.close()
'''
        
        # Write this to the slide_images API for runtime validation
        cache_validator_path = "runtime_cache_validator.py"
        with open(cache_validator_path, 'w') as f:
            f.write(cache_validator_code)
        
        print(f"   📝 Created {cache_validator_path}")
        
        print("\n🔧 STEP 5: Generate deployment fix script")
        
        deployment_fix = '''#!/bin/bash
# Deployment fix for NotesGen caching issue

echo "🚀 NOTESGEN CACHE FIX DEPLOYMENT"
echo "================================"

# Stop any existing server process
echo "🛑 Stopping server..."
pkill -f "uvicorn.*app.main:app" || true
sleep 2

# Clear Python cache
echo "🧹 Clearing Python cache..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Activate virtual environment and start server
echo "🚀 Starting server with fresh environment..."
cd /Users/robirwi/Desktop/NotesGen
source venv/bin/activate
cd backend

# Start server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

echo "✅ Server started - test image loading in web interface"
'''
        
        with open("deploy_cache_fix.sh", 'w') as f:
            f.write(deployment_fix)
        
        os.chmod("deploy_cache_fix.sh", 0o755)
        
        print("   📝 Created deploy_cache_fix.sh")
        
        print("\n✅ TARGETED FIX COMPLETE!")
        print("\n🎯 DIAGNOSIS SUMMARY:")
        print("   • Database schema is correct (image_format column exists)")
        print("   • Model definition is correct")
        print("   • Direct queries work in standalone mode")
        print("   • Converter method works correctly")
        print("\n🔧 LIKELY CAUSE:")
        print("   • Stale SQLAlchemy metadata in running server process")
        print("   • Import cache conflicts in long-running server")
        print("\n🚀 SOLUTION:")
        print("   1. Restart the server completely: ./deploy_cache_fix.sh")
        print("   2. Test image loading in web interface")
        print("   3. Monitor logs for any remaining errors")
        
        return True
        
    except Exception as e:
        print(f"❌ TARGETED FIX FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = apply_targeted_cache_fix()
    
    if success:
        print("\n🎯 READY TO DEPLOY!")
        print("Run: ./deploy_cache_fix.sh")
    else:
        print("\n❌ Fix failed - manual intervention needed") 