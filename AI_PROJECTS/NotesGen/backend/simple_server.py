#!/usr/bin/env python3
"""Simple server launcher without reload to avoid subprocess issues."""

import uvicorn
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Start the server without reload."""
    logger.info("🚀 Starting NotesGen API server...")
    logger.info("📚 API docs: http://127.0.0.1:8000/docs")
    logger.info("❤️  Health check: http://127.0.0.1:8000/health")
    
    # Start server without reload to avoid subprocess issues
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=False,  # No reload to avoid subprocess issues
        access_log=True
    )

if __name__ == "__main__":
    main() 