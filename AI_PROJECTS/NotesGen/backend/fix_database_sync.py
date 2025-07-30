#!/usr/bin/env python3
"""
Fix Database-File System Sync Issue

This script registers all PPT files from the uploads directory into the database,
fixing the stale data issue where files exist but aren't tracked in the database.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import sqlite3

def fix_database_sync():
    """Register all PPT files from uploads directory into the database."""
    
    print("🔧 Starting database-file system sync fix...")
    
    # Database path
    db_path = "notesgen.db"
    uploads_dir = "uploads"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    if not os.path.exists(uploads_dir):
        print(f"❌ Uploads directory not found: {uploads_dir}")
        return False
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current state
    cursor.execute("SELECT COUNT(*) FROM ppt_files")
    current_count = cursor.fetchone()[0]
    print(f"📊 Current PPT files in database: {current_count}")
    
    # Find all PPT files in uploads directory
    ppt_files = []
    for file in os.listdir(uploads_dir):
        if file.endswith('.pptx') and not file.startswith('~$'):  # Skip temp files
            file_path = os.path.join(uploads_dir, file)
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                ppt_files.append({
                    'filename': file,
                    'path': file_path,
                    'size': file_stat.st_size,
                    'modified': datetime.fromtimestamp(file_stat.st_mtime)
                })
    
    print(f"📁 Found {len(ppt_files)} PPT files in uploads directory")
    
    if not ppt_files:
        print("⚠️ No PPT files found to register")
        conn.close()
        return True
    
    # Register each file
    registered = 0
    for ppt_file in ppt_files:
        # Check if file already exists in database
        cursor.execute("SELECT id FROM ppt_files WHERE filename = ? OR path = ?", 
                      (ppt_file['filename'], ppt_file['path']))
        existing = cursor.fetchone()
        
        if existing:
            print(f"📝 Updating existing record: {ppt_file['filename']}")
            cursor.execute("""
                UPDATE ppt_files 
                SET path = ?, size = ?, last_modified = ?, updated_at = ?, 
                    text_cached = 0, images_cached = 0
                WHERE id = ?
            """, (
                ppt_file['path'],
                ppt_file['size'], 
                ppt_file['modified'],
                datetime.utcnow(),
                existing[0]
            ))
        else:
            print(f"✅ Registering new file: {ppt_file['filename']}")
            cursor.execute("""
                INSERT INTO ppt_files 
                (user_id, filename, path, size, created_at, updated_at, 
                 images_cached, text_cached, last_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                1,  # Default user_id
                ppt_file['filename'],
                ppt_file['path'],
                ppt_file['size'],
                datetime.utcnow(),
                datetime.utcnow(),
                False,  # images_cached
                False,  # text_cached  
                ppt_file['modified']
            ))
            registered += 1
    
    # Commit changes
    conn.commit()
    
    # Verify results
    cursor.execute("SELECT COUNT(*) FROM ppt_files")
    final_count = cursor.fetchone()[0]
    
    print(f"🎉 Database sync complete!")
    print(f"   - Registered {registered} new files")
    print(f"   - Total files in database: {final_count}")
    
    # Show registered files
    print(f"\n📋 Registered PPT files:")
    cursor.execute("SELECT id, filename, text_cached, last_modified FROM ppt_files ORDER BY id")
    for row in cursor.fetchall():
        print(f"   ID {row[0]}: {row[1]} (cached: {row[2]}, modified: {row[3]})")
    
    conn.close()
    return True

if __name__ == "__main__":
    success = fix_database_sync()
    if success:
        print("\n✅ Database sync fix completed successfully!")
        print("   You can now restart the server and the stale data issue should be resolved.")
    else:
        print("\n❌ Database sync fix failed!")
        sys.exit(1) 