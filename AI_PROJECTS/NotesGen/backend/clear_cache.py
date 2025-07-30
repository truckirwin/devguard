#!/usr/bin/env python3
"""Script to clear all cached data from the database."""

import sqlite3
import os

def clear_database_cache():
    db_file = 'notesgen.db'
    
    if not os.path.exists(db_file):
        print('Database file not found')
        return
    
    print(f'Database file {db_file} found: {os.path.getsize(db_file)/1024/1024:.1f} MB')
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        # Show tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f'Tables found: {[t[0] for t in tables]}')
        
        # Clear cache tables (keeping structure but clearing data)
        cache_tables = [
            'ppt_text_cache', 
            'ppt_slide_cache', 
            'ppt_analysis_cache', 
            'slide_image_cache',
            'ppt_files',  # Also clear uploaded files table
            'analyzed_presentations'  # Clear analysis cache
        ]
        
        total_cleared = 0
        
        for table_name in cache_tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                count = cursor.fetchone()[0]
                print(f'Table {table_name}: {count} records')
                
                if count > 0:
                    cursor.execute(f'DELETE FROM {table_name}')
                    total_cleared += count
                    print(f'✅ Cleared {count} records from {table_name}')
                else:
                    print(f'⚪ No records to clear in {table_name}')
                    
            except Exception as e:
                print(f'❌ Table {table_name} not found or error: {e}')
        
        conn.commit()
        print(f'\n🎉 Database cache cleared successfully! Total records cleared: {total_cleared}')
        
        # Show new database size
        new_size = os.path.getsize(db_file)/1024/1024
        print(f'New database size: {new_size:.1f} MB')
        
    except Exception as e:
        print(f'Error clearing cache: {e}')
    finally:
        conn.close()

if __name__ == '__main__':
    clear_database_cache() 