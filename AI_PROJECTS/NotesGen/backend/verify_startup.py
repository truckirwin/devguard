#!/usr/bin/env python3
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
