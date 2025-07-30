#!/usr/bin/env python3
"""
DIAGNOSTIC SERVER STARTUP SCRIPT

This script implements comprehensive diagnostics to identify why the NotesGen backend
server starts successfully but doesn't stay running to handle requests.

Following ENGINEERING_GUARDRAILS.md - this script:
1. Tests each component systematically
2. Provides detailed error reporting
3. Catches and reports ALL exceptions
4. Verifies system state before proceeding
"""

import os
import sys
import signal
import asyncio
import logging
import traceback
import json
from pathlib import Path
from typing import Dict, Any
import subprocess

# Ensure proper path setup
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configure comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(backend_dir / "diagnostic.log")
    ]
)
logger = logging.getLogger(__name__)

class ServerDiagnostics:
    """Comprehensive server diagnostics and startup."""
    
    def __init__(self):
        self.diagnostic_results = {}
        self.startup_errors = []
        
    def log_result(self, test_name: str, success: bool, details: str = "", error: Exception = None):
        """Log diagnostic test results."""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {details}")
        
        self.diagnostic_results[test_name] = {
            "success": success,
            "details": details,
            "error": str(error) if error else None
        }
        
        if not success and error:
            self.startup_errors.append(f"{test_name}: {error}")
    
    def test_python_environment(self) -> bool:
        """Test Python environment and virtual environment."""
        try:
            logger.info("🔍 Testing Python environment...")
            
            # Check Python version
            python_version = sys.version
            logger.info(f"Python version: {python_version}")
            
            # Check virtual environment
            venv_path = os.environ.get('VIRTUAL_ENV')
            if venv_path:
                logger.info(f"Virtual environment: {venv_path}")
            else:
                logger.warning("No virtual environment detected")
            
            # Check current working directory
            cwd = os.getcwd()
            logger.info(f"Current directory: {cwd}")
            
            self.log_result("python_environment", True, f"Python {sys.version_info.major}.{sys.version_info.minor}")
            return True
            
        except Exception as e:
            self.log_result("python_environment", False, error=e)
            return False
    
    def test_critical_imports(self) -> bool:
        """Test all critical imports step by step."""
        try:
            logger.info("🔍 Testing critical imports...")
            
            # Test basic imports
            logger.debug("Testing basic imports...")
            import fastapi
            import uvicorn
            import sqlalchemy
            logger.debug("✅ Basic imports successful")
            
            # Test pydantic settings (this was failing)
            logger.debug("Testing pydantic_settings import...")
            from pydantic_settings import BaseSettings, SettingsConfigDict
            logger.debug("✅ pydantic_settings import successful")
            
            # Test app config
            logger.debug("Testing app config import...")
            from app.core.config import get_settings
            settings = get_settings()
            logger.debug(f"✅ Config loaded: DB URL starts with {settings.SQLALCHEMY_DATABASE_URI[:20]}...")
            
            # Test database imports
            logger.debug("Testing database imports...")
            from app.db.database import engine, Base, SessionLocal
            logger.debug("✅ Database imports successful")
            
            # Test main app import
            logger.debug("Testing main app import...")
            from app.main import app
            logger.debug("✅ Main app import successful")
            
            self.log_result("critical_imports", True, "All critical imports successful")
            return True
            
        except Exception as e:
            logger.error(f"Import error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.log_result("critical_imports", False, error=e)
            return False
    
    def test_database_connection(self) -> bool:
        """Test database connectivity."""
        try:
            logger.info("🔍 Testing database connection...")
            
            import sqlalchemy
            from app.core.config import get_settings
            from app.db.database import engine, SessionLocal
            
            settings = get_settings()
            logger.info(f"Database URL: {settings.SQLALCHEMY_DATABASE_URI}")
            
            # Test engine connection
            logger.debug("Testing SQLAlchemy engine connection...")
            with engine.connect() as conn:
                result = conn.execute(sqlalchemy.text("SELECT 1"))
                test_result = result.fetchone()
                logger.debug(f"Database test query result: {test_result}")
            
            # Test session creation
            logger.debug("Testing session creation...")
            db = SessionLocal()
            db.close()
            logger.debug("✅ Session creation successful")
            
            self.log_result("database_connection", True, "Database connection successful")
            return True
            
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            self.log_result("database_connection", False, error=e)
            return False
    
    def test_file_system_access(self) -> bool:
        """Test file system access for uploads directory."""
        try:
            logger.info("🔍 Testing file system access...")
            
            from app.core.config import get_settings
            settings = get_settings()
            
            # Check uploads directory
            uploads_dir = Path(settings.UPLOAD_DIR)
            if not uploads_dir.exists():
                uploads_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created uploads directory: {uploads_dir}")
            
            # Test write access
            test_file = uploads_dir / "test_write.txt"
            test_file.write_text("test")
            test_file.unlink()
            logger.debug("✅ Write access confirmed")
            
            self.log_result("file_system_access", True, f"Uploads directory accessible: {uploads_dir}")
            return True
            
        except Exception as e:
            logger.error(f"File system access error: {e}")
            self.log_result("file_system_access", False, error=e)
            return False
    
    def test_port_availability(self, port: int = 8000) -> bool:
        """Test if the target port is available."""
        try:
            logger.info(f"🔍 Testing port {port} availability...")
            
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('127.0.0.1', port))
                
                if result == 0:
                    # Port is in use
                    logger.warning(f"Port {port} is already in use")
                    
                    # Try to identify what's using it
                    try:
                        result = subprocess.run(['lsof', '-i', f':{port}'], 
                                              capture_output=True, text=True)
                        if result.stdout:
                            logger.warning(f"Process using port {port}:\n{result.stdout}")
                    except:
                        pass
                    
                    self.log_result("port_availability", False, f"Port {port} is in use")
                    return False
                else:
                    # Port is available
                    logger.debug(f"✅ Port {port} is available")
                    self.log_result("port_availability", True, f"Port {port} is available")
                    return True
                    
        except Exception as e:
            logger.error(f"Port availability test error: {e}")
            self.log_result("port_availability", False, error=e)
            return False
    
    def setup_signal_handlers(self):
        """Set up signal handlers to catch server shutdown reasons."""
        def signal_handler(signum, frame):
            logger.error(f"🚨 Server received signal {signum}: {signal.Signals(signum).name}")
            logger.error("Server is shutting down due to signal")
            self.print_diagnostic_summary()
            sys.exit(1)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    def print_diagnostic_summary(self):
        """Print comprehensive diagnostic summary."""
        logger.info("\n" + "="*60)
        logger.info("📊 DIAGNOSTIC SUMMARY")
        logger.info("="*60)
        
        for test_name, result in self.diagnostic_results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            logger.info(f"{status} {test_name}")
            if result["details"]:
                logger.info(f"    Details: {result['details']}")
            if result["error"]:
                logger.info(f"    Error: {result['error']}")
        
        if self.startup_errors:
            logger.error("\n🚨 STARTUP ERRORS:")
            for error in self.startup_errors:
                logger.error(f"  - {error}")
        
        logger.info("="*60)
    
    async def start_server_with_monitoring(self):
        """Start the server with comprehensive monitoring."""
        try:
            logger.info("🚀 Starting server with monitoring...")
            
            import uvicorn
            from app.main import app
            
            # Create server configuration
            config = uvicorn.Config(
                app=app,
                host="127.0.0.1",
                port=8000,
                log_level="debug",
                reload=False,  # Disable reload to avoid subprocess issues
                access_log=True,
                loop="asyncio"
            )
            
            server = uvicorn.Server(config)
            
            logger.info("🌐 Server configured, starting...")
            logger.info("📚 API docs will be available at http://127.0.0.1:8000/docs")
            logger.info("❤️  Health check will be available at http://127.0.0.1:8000/health")
            
            # Start the server and keep it running
            logger.info("🔥 Starting server - will run until interrupted...")
            await server.serve()
            
            # This line should never be reached unless server stops
            logger.error("🚨 Server serve() completed unexpectedly!")
            
        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user (Ctrl+C)")
        except Exception as e:
            logger.error(f"❌ Server startup failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.log_result("server_startup", False, error=e)
            raise
    
    async def run_full_diagnostics_and_start(self):
        """Run complete diagnostics and start server if all tests pass."""
        logger.info("🔬 Starting comprehensive server diagnostics...")
        
        # Set up signal handlers
        self.setup_signal_handlers()
        
        # Run all diagnostic tests
        tests = [
            self.test_python_environment,
            self.test_critical_imports,
            self.test_database_connection,
            self.test_file_system_access,
            lambda: self.test_port_availability(8000)
        ]
        
        all_passed = True
        for test in tests:
            try:
                if not test():
                    all_passed = False
            except Exception as e:
                logger.error(f"Test failed with exception: {e}")
                all_passed = False
        
        # Print diagnostic summary
        self.print_diagnostic_summary()
        
        if not all_passed:
            logger.error("🚨 Diagnostic tests failed. Cannot start server safely.")
            logger.error("Please review the errors above and fix them before starting the server.")
            return False
        
        logger.info("✅ All diagnostic tests passed. Starting server...")
        
        try:
            # Create a task to run the server
            server_task = asyncio.create_task(self.start_server_with_monitoring())
            
            # Give the server a moment to start
            await asyncio.sleep(2)
            
            # Test if server is responding
            logger.info("🔍 Testing server responsiveness...")
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get('http://127.0.0.1:8000/health', timeout=5) as response:
                        if response.status == 200:
                            logger.info("✅ Server is responding to health checks!")
                        else:
                            logger.warning(f"⚠️  Server responded with status {response.status}")
            except Exception as test_e:
                logger.warning(f"⚠️  Server connectivity test failed: {test_e}")
                logger.info("🔧 This may be normal if health endpoint doesn't exist yet")
            
            # Wait for the server task to complete (should run forever)
            await server_task
            
        except Exception as e:
            logger.error(f"❌ Server failed after diagnostics: {e}")
            return False
        
        return True

def main():
    """Main entry point."""
    try:
        logger.info("🏁 NotesGen Backend Diagnostic Startup")
        logger.info("=" * 50)
        
        diagnostics = ServerDiagnostics()
        
        # Run diagnostics and start server
        success = asyncio.run(diagnostics.run_full_diagnostics_and_start())
        
        if not success:
            logger.error("🚨 Server startup failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"🚨 Fatal error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 