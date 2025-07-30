#!/usr/bin/env python3

import os
import uvicorn

# Set environment variables (load from .env file or environment)
# AWS credentials should be set via environment variables or .env file
if not os.getenv('AWS_ACCESS_KEY_ID'):
    print("⚠️ WARNING: AWS_ACCESS_KEY_ID not set in environment")
if not os.getenv('AWS_SECRET_ACCESS_KEY'):
    print("⚠️ WARNING: AWS_SECRET_ACCESS_KEY not set in environment")
os.environ.setdefault('AWS_DEFAULT_REGION', 'us-east-1')

print("🔧 Environment variables set")
print(f"   AWS_ACCESS_KEY_ID: {os.environ.get('AWS_ACCESS_KEY_ID')[:8]}...")
print(f"   AWS_DEFAULT_REGION: {os.environ.get('AWS_DEFAULT_REGION')}")

try:
    print("📦 Importing app...")
    from app.main import app
    print("✅ App imported successfully")
    
    print("🚀 Starting uvicorn server...")
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000, 
        log_level="info",
        reload=False
    )
except Exception as e:
    print(f"❌ Error starting server: {e}")
    import traceback
    traceback.print_exc() 