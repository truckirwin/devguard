#!/usr/bin/env python3
"""
Robust Backend Startup Script
Automatically detects correct directories and prevents common startup errors
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def find_project_root():
    """Find the NotesGen project root directory."""
    current = Path.cwd()
    
    # Search up the directory tree
    for path in [current] + list(current.parents):
        if (path / "requirements.txt").exists() and (path / "backend").is_dir() and (path / "frontend").is_dir():
            return path
    
    # Try common locations
    common_locations = [
        Path.home() / "Desktop" / "PROJECTS" / "NotesGen",
        Path.home() / "Desktop" / "NotesGen",
        Path("/Users/robirwi/Desktop/PROJECTS/NotesGen"),
        Path("/Users/robirwi/Desktop/NotesGen"),
    ]
    
    for path in common_locations:
        if path.exists() and (path / "requirements.txt").exists() and (path / "backend").is_dir():
            return path
    
    return None

def validate_environment(project_root):
    """Validate the project environment."""
    backend_dir = project_root / "backend"
    venv_dir = project_root / "venv"
    app_main = backend_dir / "app" / "main.py"
    
    if not backend_dir.exists():
        raise RuntimeError(f"Backend directory not found: {backend_dir}")
    
    if not venv_dir.exists():
        raise RuntimeError(f"Virtual environment not found: {venv_dir}")
    
    if not app_main.exists():
        raise RuntimeError(f"Main application file not found: {app_main}")
    
    return backend_dir, venv_dir

def setup_aws_credentials():
    """Set up AWS credentials if not already present."""
    if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
        print("⚠️  AWS credentials not found, setting from stored values...")
        os.environ["AWS_ACCESS_KEY_ID"] = "YOUR_AWS_ACCESS_KEY_HERE"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "YOUR_AWS_SECRET_ACCESS_KEY_HERE"
        print("✅ AWS credentials configured")
    else:
        print("✅ AWS credentials found in environment")

def kill_existing_processes():
    """Kill any existing processes on port 8000."""
    try:
        result = subprocess.run(["lsof", "-ti:8000"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print("⚠️  Port 8000 is in use. Cleaning up...")
            subprocess.run(["kill", "-9"] + result.stdout.strip().split(), check=False)
            import time
            time.sleep(2)
            print("✅ Port cleaned up")
    except Exception as e:
        print(f"Warning: Could not clean up port 8000: {e}")

def validate_app_import(backend_dir):
    """Validate that we can import the app module."""
    # Change to backend directory temporarily
    original_cwd = os.getcwd()
    try:
        os.chdir(backend_dir)
        
        # Add backend to Python path
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))
        
        # Try to import the app module
        spec = importlib.util.find_spec("app.main")
        if spec is None:
            raise ImportError("Cannot find app.main module")
        
        print("✅ app.main module validated")
        return True
        
    except Exception as e:
        print(f"❌ Cannot import app.main module: {e}")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Python path: {sys.path[:3]}...")
        print(f"   Contents of backend directory:")
        for item in os.listdir(backend_dir):
            print(f"     {item}")
        return False
    finally:
        os.chdir(original_cwd)

def main():
    """Main startup function."""
    print("🔄 Starting NotesGen Backend Server...")
    
    # Find project root
    print("🔍 Detecting project directory...")
    project_root = find_project_root()
    if not project_root:
        print("❌ Could not find project root directory!")
        print("   Looking for directory containing: requirements.txt, backend/, frontend/")
        print(f"   Current directory: {Path.cwd()}")
        print("   Please run this script from within the NotesGen project directory.")
        sys.exit(1)
    
    print(f"✅ Found project root: {project_root}")
    
    # Validate environment
    print("🔍 Validating project structure...")
    try:
        backend_dir, venv_dir = validate_environment(project_root)
        print("✅ Project structure validated")
    except RuntimeError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # Validate app import
    print("🔍 Validating app module...")
    if not validate_app_import(backend_dir):
        sys.exit(1)
    
    # Setup AWS credentials
    print("🔍 Checking AWS credentials...")
    setup_aws_credentials()
    
    # Kill existing processes
    print("🔍 Checking for existing processes on port 8000...")
    kill_existing_processes()
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Start the server
    print("🚀 Starting uvicorn server...")
    print(f"   Project Root: {project_root}")
    print(f"   Backend Dir: {backend_dir}")
    print(f"   Working Dir: {Path.cwd()}")
    print(f"   Server URL: http://127.0.0.1:8000")
    print("")
    
    try:
        # Use uvicorn directly
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn not installed, trying to install...")
        subprocess.run([sys.executable, "-m", "pip", "install", "uvicorn"], check=True)
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )

if __name__ == "__main__":
    main() 