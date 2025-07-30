#!/usr/bin/env python3
"""
Motivational AI System Launcher
Checks dependencies and starts the web application
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['flask', 'flask_cors']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print("\n🔧 Installing missing dependencies...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            print("Please run: pip install -r requirements.txt")
            return False
    
    return True

def check_sample_files():
    """Check if sample message files exist"""
    messages_dir = Path("Messages")
    if not messages_dir.exists():
        print("⚠️  Warning: Messages directory not found")
        return False
    
    sample_files = [
        "RiseandGrindMessages.MD",
        "StayHardMessages.md", 
        "JobhuntComedyMessages.md",
        "NewYogaMessages.MD",
        "JobCoachMessages.md"
    ]
    
    found_files = 0
    for file in sample_files:
        if (messages_dir / file).exists():
            found_files += 1
            print(f"✅ Found {file}")
        else:
            print(f"⚠️  Missing {file}")
    
    if found_files == 0:
        print("❌ No sample message files found")
        return False
    elif found_files < len(sample_files):
        print(f"⚠️  Only {found_files}/{len(sample_files)} sample files found")
    else:
        print("✅ All sample message files found")
    
    return True

def start_application():
    """Start the Flask application"""
    print("\n🚀 Starting Motivational AI System...")
    print("=" * 50)
    
    try:
        # Import and run the app
        from app import app
        print("📱 Web interface: http://localhost:5000")
        print("🔥 Generate your motivational messages!")
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        return False
    except KeyboardInterrupt:
        print("\n\n👋 Motivational AI stopped. Keep being awesome!")
        return True
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return False

def main():
    """Main launcher function"""
    print("🚀 Motivational AI System Launcher")
    print("=" * 40)
    
    # Check system requirements
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    # Check sample files (warn but don't exit)
    check_sample_files()
    
    # Start the application
    if not start_application():
        sys.exit(1)

if __name__ == "__main__":
    main() 