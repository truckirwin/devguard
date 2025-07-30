import zipfile
import os
from pathlib import Path
from xml.etree import ElementTree as ET
import tempfile
from typing import List, Dict

class PPTProcessor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()

    def extract_text_from_ppt(self, ppt_path: str) -> List[Dict]:
        """Extract text content from PPT file"""
        try:
            with zipfile.ZipFile(ppt_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
                
                # Extract text from slides
                slides_dir = os.path.join(self.temp_dir, 'ppt', 'slides')
                slide_files = [f for f in os.listdir(slides_dir) if f.startswith('slide')]
                
                slide_texts = []
                for slide_file in sorted(slide_files):
                    slide_path = os.path.join(slides_dir, slide_file)
                    with open(slide_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        root = ET.fromstring(content)
                        
                        # Extract text from slide
                        text = self._extract_text_from_slide(root)
                        slide_texts.append({
                            'slide_number': int(slide_file.replace('slide', '').replace('.xml', '')),
                            'content': text
                        })
                
                return slide_texts
                
        except Exception as e:
            raise Exception(f"Error extracting text from PPT: {str(e)}")
        finally:
            self._cleanup()

    def _extract_text_from_slide(self, root: ET.Element) -> str:
        """Extract text from a single slide"""
        text = []
        for element in root.iter():
            if element.tag.endswith('t'):
                text.append(element.text or '')
        return ' '.join(text).strip()

    def update_ppt_with_notes(self, ppt_path: str, notes: List[Dict]) -> None:
        """Update PPT file with notes"""
        try:
            with zipfile.ZipFile(ppt_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
                
                # Update slides with notes
                slides_dir = os.path.join(self.temp_dir, 'ppt', 'slides')
                for note in notes:
                    slide_num = note['slide_number']
                    slide_file = f'slide{slide_num}.xml'
                    slide_path = os.path.join(slides_dir, slide_file)
                    
                    if os.path.exists(slide_path):
                        self._update_slide_with_note(slide_path, note['content'])
                
                # Create new PPT file
                output_path = ppt_path.replace('.pptx', '_with_notes.pptx')
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(self.temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, self.temp_dir)
                            zipf.write(file_path, arcname)
                
        except Exception as e:
            raise Exception(f"Error updating PPT with notes: {str(e)}")
        finally:
            self._cleanup()

    def _update_slide_with_note(self, slide_path: str, note: str) -> None:
        """Update a single slide with notes"""
        with open(slide_path, 'r', encoding='utf-8') as f:
            content = f.read()
            root = ET.fromstring(content)
            
            # Add note to slide
            # This is a simplified example - actual implementation would need to
            # properly structure the XML according to PPTX schema
            notes_elem = ET.SubElement(root, 'notes')
            text_elem = ET.SubElement(notes_elem, 'text')
            text_elem.text = note
            
            # Write updated content
            with open(slide_path, 'w', encoding='utf-8') as f:
                f.write(ET.tostring(root, encoding='unicode'))

    def _cleanup(self) -> None:
        """Clean up temporary files"""
        if os.path.exists(self.temp_dir):
            for root, dirs, files in os.walk(self.temp_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.temp_dir)
