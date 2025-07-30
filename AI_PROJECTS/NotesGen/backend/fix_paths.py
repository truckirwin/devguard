#!/usr/bin/env python3
"""
Fix file paths in database to use absolute paths.
"""

import os
import sqlite3
from pathlib import Path

def fix_paths():
    """Update all PPT file paths to absolute paths."""
    
    print("🔧 Fixing file paths to use absolute paths...")
    
    # Get current backend directory
    backend_dir = os.getcwd()
    print(f"📁 Backend directory: {backend_dir}")
    
    # Connect to database
    conn = sqlite3.connect("notesgen.db")
    cursor = conn.cursor()
    
    # Get all files
    cursor.execute("SELECT id, filename, path FROM ppt_files")
    files = cursor.fetchall()
    
    updated = 0
    for file_id, filename, current_path in files:
        if not os.path.isabs(current_path):
            # Convert to absolute path
            absolute_path = os.path.abspath(current_path)
            
            # Verify file exists
            if os.path.exists(absolute_path):
                cursor.execute("UPDATE ppt_files SET path = ? WHERE id = ?", 
                              (absolute_path, file_id))
                print(f"✅ Updated {filename}: {absolute_path}")
                updated += 1
            else:
                print(f"⚠️ File not found: {absolute_path}")
    
    conn.commit()
    print(f"🎉 Updated {updated} file paths to absolute paths")
    
    # Verify results
    cursor.execute("SELECT id, filename, path FROM ppt_files LIMIT 3")
    for row in cursor.fetchall():
        print(f"   ID {row[0]}: {row[2]}")
    
    conn.close()

if __name__ == "__main__":
    fix_paths() 