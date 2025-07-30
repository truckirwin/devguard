#!/usr/bin/env python3
"""Debug script to see what logical lines are extracted."""

import sys
import os
sys.path.append('.')

from app.utils.enhanced_speaker_notes_parser import EnhancedSpeakerNotesParser
import xml.etree.ElementTree as ET

def debug_lines():
    # Use the uploaded PPT file
    ppt_file = "uploads/ILT-TF-200-DEA-10-EN_M02.pptx"
    
    if not os.path.exists(ppt_file):
        print(f"❌ PPT file not found: {ppt_file}")
        return
    
    print(f"🔍 Debugging line extraction for: {ppt_file}")
    
    parser = EnhancedSpeakerNotesParser()
    
    try:
        # Get raw XML directly
        from pptx import Presentation
        prs = Presentation(ppt_file)
        slide = prs.slides[0]
        
        if slide.has_notes_slide:
            notes_slide = slide.notes_slide
            xml_content = notes_slide._element.xml
            
            # Parse XML to extract logical lines
            root = ET.fromstring(xml_content)
            paragraphs = root.findall('.//a:p', parser.NAMESPACES)
            
            all_logical_lines = []
            
            print(f"\n" + "="*50)
            print(f"EXTRACTING LOGICAL LINES FROM {len(paragraphs)} PARAGRAPHS:")
            print("="*50)
            
            for i, paragraph in enumerate(paragraphs):
                text_elements = paragraph.findall('.//a:t', parser.NAMESPACES)
                text_content = ''.join([elem.text or '' for elem in text_elements]).strip()
                
                print(f"\nParagraph {i+1}:")
                print(f"  Raw text: {repr(text_content)}")
                
                if text_content:
                    # Split on vertical tabs to get logical lines
                    logical_lines = text_content.split('\x0b')
                    print(f"  Split into {len(logical_lines)} logical lines:")
                    
                    for j, line in enumerate(logical_lines):
                        line = line.strip()
                        if line:
                            all_logical_lines.append(line)
                            # Check if it's a section header
                            is_header, section_type = parser._identify_section_header(line)
                            marker = "🔥 SECTION HEADER" if is_header else "   content"
                            print(f"    Line {j+1}: {marker} ({section_type}) - {repr(line[:100])}")
            
            print(f"\n" + "="*50)
            print(f"TOTAL LOGICAL LINES EXTRACTED: {len(all_logical_lines)}")
            print("="*50)
            
            for i, line in enumerate(all_logical_lines):
                is_header, section_type = parser._identify_section_header(line)
                marker = "🔥 HEADER" if is_header else "   content"
                print(f"{i+1:2d}: {marker} ({section_type or 'None':>10}) - {repr(line[:80])}")
            
        else:
            print("❌ No notes slide found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_lines() 