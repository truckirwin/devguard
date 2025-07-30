#!/usr/bin/env python3
"""
Production-ready server startup script for NotesGen API.
This script addresses the subprocess issues with uvicorn --reload.
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Ensure the backend directory is in Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Start the server with proper error handling."""
    try:
        logger.info("🚀 Starting NotesGen API Server...")
        
        # Import after path setup
        import uvicorn
        from app.main import app
        
        # Verify imports work
        logger.info("✅ All imports successful")
        
        # Get port from environment or use default
        port = int(os.getenv("PORT", 8000))
        host = os.getenv("HOST", "127.0.0.1")
        
        # Configure uvicorn
        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            log_level="info",
            reload=False,  # Disable reload to avoid subprocess issues
            access_log=True,
            loop="asyncio"
        )
        
        server = uvicorn.Server(config)
        
        logger.info(f"🌐 Server starting on http://{host}:{port}")
        logger.info("📚 API docs available at http://127.0.0.1:8000/docs")
        logger.info("❤️  Health check at http://127.0.0.1:8000/health")
        
        # Run the server
        asyncio.run(server.serve())
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("💡 Make sure you're in the virtual environment and all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 