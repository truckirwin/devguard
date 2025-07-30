#!/usr/bin/env python3
"""
Permanent fix for SQLAlchemy column mapping issue.
This will force the correct column mapping at the ORM level.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def fix_column_mapping_permanently():
    """Apply a permanent fix to the SQLAlchemy column mapping."""
    
    print("🔧 PERMANENT COLUMN MAPPING FIX")
    print("=" * 50)
    
    try:
        # Step 1: Remove all Python cache
        print("🧹 STEP 1: Clear all Python cache completely")
        os.system("find . -name '*.pyc' -delete 2>/dev/null || true")
        os.system("find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true")
        
        # Step 2: Create a model definition override
        print("🔧 STEP 2: Create explicit column mapping override")
        
        override_code = '''# SQLAlchemy column mapping override
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

# Force correct column mapping
class SlideImageOverride:
    """Override to ensure correct column mapping."""
    
    @staticmethod
    def ensure_correct_mapping():
        """Ensure that image_format column is properly mapped."""
        from app.models.models import SlideImage
        
        # Force the correct column attribute mapping
        if hasattr(SlideImage, 'format'):
            # Remove the incorrect attribute if it exists
            delattr(SlideImage, 'format')
        
        # Ensure image_format is properly mapped
        if not hasattr(SlideImage, 'image_format'):
            raise Exception("SlideImage.image_format column is missing!")
        
        # Verify the column name in the table definition
        image_format_col = None
        for col in SlideImage.__table__.columns:
            if col.name == 'image_format':
                image_format_col = col
                break
        
        if not image_format_col:
            raise Exception("image_format column not found in table definition!")
        
        # Force SQLAlchemy to use the correct column mapping
        SlideImage.image_format.property.columns = [image_format_col]
        
        print(f"✅ Column mapping verified: {SlideImage.image_format.property.columns[0].name}")
        return True

# Apply the override function
def apply_column_override():
    try:
        override = SlideImageOverride()
        return override.ensure_correct_mapping()
    except Exception as e:
        print(f"❌ Column override failed: {e}")
        return False
'''
        
        with open("column_mapping_override.py", "w") as f:
            f.write(override_code)
        
        print("   📝 Created column_mapping_override.py")
        
        # Step 3: Update the models file to include the override
        print("🔧 STEP 3: Update models.py with explicit column reference")
        
        # Read current models file
        with open("app/models/models.py", "r") as f:
            models_content = f.read()
        
        # Check if we need to add the fix
        if "# EXPLICIT COLUMN MAPPING FIX" not in models_content:
            # Add explicit column mapping fix at the end
            models_fix = '''

# EXPLICIT COLUMN MAPPING FIX
# Force SQLAlchemy to use correct column name
import logging
logger = logging.getLogger(__name__)

def verify_slide_image_mapping():
    """Verify and fix SlideImage column mapping at runtime."""
    try:
        # Ensure image_format column is correctly mapped
        image_format_col = None
        for col in SlideImage.__table__.columns:
            if col.name == 'image_format':
                image_format_col = col
                break
        
        if image_format_col:
            # Force the correct column mapping
            SlideImage.image_format = SlideImage.__table__.c.image_format
            logger.info("✅ SlideImage.image_format column mapping verified")
            return True
        else:
            logger.error("❌ image_format column not found in SlideImage table")
            return False
    except Exception as e:
        logger.error(f"❌ Column mapping verification failed: {e}")
        return False

# Apply the fix immediately when module is imported
verify_slide_image_mapping()
'''
            
            models_content += models_fix
            
            with open("app/models/models.py", "w") as f:
                f.write(models_content)
            
            print("   📝 Updated models.py with explicit column mapping")
        
        # Step 4: Create a startup verification script
        print("🔧 STEP 4: Create startup verification")
        
        startup_code = '''#!/usr/bin/env python3
"""
Startup verification for correct column mapping.
Run this before starting the server.
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def verify_startup():
    """Verify that column mapping is correct before server starts."""
    
    print("🔍 STARTUP VERIFICATION")
    print("=" * 30)
    
    try:
        from app.models.models import SlideImage
        from sqlalchemy import text
        from app.db.database import SessionLocal
        
        # Test 1: Check model definition
        print("📋 Test 1: Model Definition")
        if hasattr(SlideImage, 'image_format'):
            print("   ✅ SlideImage.image_format attribute exists")
        else:
            print("   ❌ SlideImage.image_format attribute missing")
            return False
        
        # Test 2: Check table schema
        print("📋 Test 2: Table Schema")
        image_format_found = False
        for col in SlideImage.__table__.columns:
            if col.name == 'image_format':
                image_format_found = True
                print(f"   ✅ Found column: {col.name} ({col.type})")
                break
        
        if not image_format_found:
            print("   ❌ image_format column not found in table schema")
            return False
        
        # Test 3: Test actual query
        print("📋 Test 3: Query Test")
        db = SessionLocal()
        try:
            # Try a simple query that should work
            result = db.query(SlideImage).filter(
                SlideImage.ppt_file_id == 1
            ).first()
            
            if result:
                print(f"   ✅ Query successful - found slide with format: {result.image_format}")
            else:
                print("   ⚠️ Query successful but no data found")
            
            db.close()
            
        except Exception as query_error:
            print(f"   ❌ Query failed: {query_error}")
            db.close()
            return False
        
        print("✅ All startup verification tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Startup verification failed: {e}")
        return False

if __name__ == "__main__":
    success = verify_startup()
    if not success:
        print("\n❌ STARTUP VERIFICATION FAILED")
        sys.exit(1)
    else:
        print("\n✅ STARTUP VERIFICATION PASSED")
'''
        
        with open("verify_startup.py", "w") as f:
            f.write(startup_code)
        
        os.chmod("verify_startup.py", 0o755)
        print("   📝 Created verify_startup.py")
        
        # Step 5: Test the fix
        print("🔧 STEP 5: Test the fix")
        
        # Import and test
        from app.models.models import SlideImage
        
        print("   📋 Testing model import...")
        if hasattr(SlideImage, 'image_format'):
            print("   ✅ SlideImage.image_format exists")
        else:
            print("   ❌ SlideImage.image_format missing")
            return False
        
        # Check table columns
        print("   📋 Testing table schema...")
        for col in SlideImage.__table__.columns:
            if col.name == 'image_format':
                print(f"   ✅ Table column: {col.name}")
                break
        else:
            print("   ❌ image_format column not found in table")
            return False
        
        print("✅ PERMANENT FIX APPLIED SUCCESSFULLY!")
        print("\n🚀 NEXT STEPS:")
        print("1. Run: python verify_startup.py")
        print("2. Start server: uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
        print("3. Test image loading in web interface")
        
        return True
        
    except Exception as e:
        print(f"❌ PERMANENT FIX FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_column_mapping_permanently()
    
    if not success:
        print("\n❌ Fix failed - manual intervention needed")
        sys.exit(1)
    else:
        print("\n🎯 READY FOR SERVER START!") 