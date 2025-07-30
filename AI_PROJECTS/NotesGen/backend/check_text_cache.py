#!/usr/bin/env python3
"""
Script to check text cache data in the database
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.db.database import engine
from sqlalchemy import text
import json

def check_text_cache():
    with engine.connect() as conn:
        # Check if PPTTextCache table exists and has data
        result = conn.execute(text('SELECT COUNT(*) FROM ppt_text_cache'))
        cache_count = result.scalar()
        print(f'📊 Text cache entries: {cache_count}')
        
        if cache_count > 0:
            # Get latest cache entry details
            result = conn.execute(text('''
                SELECT ptc.id, ptc.ppt_file_id, pf.filename, ptc.total_slides, 
                       ptc.total_text_elements, ptc.created_at, ptc.updated_at,
                       LENGTH(ptc.text_elements_data) as data_size
                FROM ppt_text_cache ptc
                JOIN ppt_files pf ON ptc.ppt_file_id = pf.id
                ORDER BY ptc.updated_at DESC
                LIMIT 5
            '''))
            
            print('\n📋 Text cache entries:')
            for row in result:
                print(f'  Cache ID {row[0]}: PPT {row[1]} ({row[2]})')
                print(f'    Slides: {row[3]}, Text elements: {row[4]}')
                print(f'    Data size: {row[7]} bytes')
                print(f'    Created: {row[5]}, Updated: {row[6]}')
                print()
            
            # Get sample text data structure
            result = conn.execute(text('''
                SELECT text_elements_data 
                FROM ppt_text_cache 
                ORDER BY updated_at DESC 
                LIMIT 1
            '''))
            
            text_data = result.scalar()
            if text_data:
                try:
                    data = json.loads(text_data)
                    print('📄 Sample cached text structure:')
                    print(f'  Total slides: {data.get("total_slides", "N/A")}')
                    print(f'  Filename: {data.get("filename", "N/A")}')
                    print(f'  Cached: {data.get("cached", "N/A")}')
                    if data.get('slides'):
                        first_slide = data['slides'][0]
                        print(f'\n  First slide ({first_slide.get("slide_number")}):')
                        print(f'    Text elements: {len(first_slide.get("text_elements", []))}')
                        print(f'    Speaker notes: {len(first_slide.get("speaker_notes", []))}')
                        if first_slide.get('text_elements'):
                            first_element = first_slide['text_elements'][0]
                            sample_text = first_element.get("text", "")[:100]
                            print(f'    Sample text: "{sample_text}..."')
                except Exception as e:
                    print(f'❌ Error parsing cached data: {e}')
        
        # Check PPT files text_cached status
        result = conn.execute(text('''
            SELECT id, filename, text_cached, images_cached, last_modified
            FROM ppt_files
            ORDER BY id DESC
            LIMIT 5
        '''))
        
        print('\n📁 PPT Files cache status:')
        for row in result:
            print(f'  PPT {row[0]}: {row[1]}')
            print(f'    Text cached: {row[2]}, Images cached: {row[3]}')
            print(f'    Last modified: {row[4]}')
            print()

if __name__ == "__main__":
    check_text_cache() 