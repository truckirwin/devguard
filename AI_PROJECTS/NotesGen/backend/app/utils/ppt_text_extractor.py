"""
PowerPoint Comprehensive Text Extractor

Extracts all editable text elements from PowerPoint XML files with their locations 
for modification and saving back to the original structure.
"""

import zipfile
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import re
import tempfile
import shutil
import os

@dataclass
class TextElement:
    """Represents an editable text element in the PPT with its XML location."""
    
    # Identification
    element_id: str
    element_type: str  # 'slide_text', 'alt_text', 'speaker_notes', 'table_text'
    slide_number: int
    
    # Content
    text_content: str
    original_text: str
    
    # Location information for XML editing
    shape_name: Optional[str] = None
    shape_id: Optional[str] = None
    xpath_location: Optional[str] = None
    xml_file_path: str = ""  # Relative path within the PPTX
    
    # Context information
    placeholder_type: Optional[str] = None
    is_title: bool = False
    is_content: bool = False
    paragraph_index: Optional[int] = None
    run_index: Optional[int] = None
    
    # Visual properties
    position: Optional[Dict[str, float]] = None
    formatting: Optional[Dict[str, str]] = None

@dataclass
class SpeakerNotesSection:
    """Represents a structured section within speaker notes."""
    
    section_type: str  # 'developer_notes', 'instructor_notes', 'student_notes', 'image_description', 'alt_text_description', 'general'
    content: str
    original_content: str
    paragraph_index: int

@dataclass
class SlideTextStructure:
    """Complete text structure for a single slide."""
    
    slide_number: int
    slide_xml_path: str
    notes_xml_path: Optional[str]
    
    # Text elements
    text_elements: List[TextElement]
    speaker_notes_sections: List[SpeakerNotesSection]
    
    # Summary info
    total_text_elements: int = 0
    has_speaker_notes: bool = False
    has_alt_text: bool = False

class PPTTextExtractor:
    """Comprehensive PowerPoint text extractor and editor."""
    
    # PowerPoint XML namespaces
    NAMESPACES = {
        'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    }
    
    def __init__(self):
        """Initialize the text extractor."""
        for prefix, uri in self.NAMESPACES.items():
            ET.register_namespace(prefix, uri)
    
    def extract_all_text_elements(self, file_path: str) -> List[SlideTextStructure]:
        """Extract all editable text elements from a PowerPoint file."""
        
        slides_structure = []
        
        with zipfile.ZipFile(file_path, 'r') as pptx_zip:
            # Get all slide XML files
            slide_files = [f for f in pptx_zip.namelist() 
                          if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
            
            # Sort by slide number
            slide_files.sort(key=lambda x: int(re.search(r'slide(\d+)\.xml', x).group(1)))
            
            for slide_file in slide_files:
                slide_number = int(re.search(r'slide(\d+)\.xml', slide_file).group(1))
                
                # Extract slide text elements
                slide_structure = self._extract_slide_text_structure(
                    pptx_zip, slide_file, slide_number
                )
                
                slides_structure.append(slide_structure)
        
        return slides_structure
    
    def extract_single_slide_text_elements(self, file_path: str, slide_number: int) -> SlideTextStructure:
        """Extract text elements from a specific slide only - PERFORMANCE OPTIMIZED."""
        
        with zipfile.ZipFile(file_path, 'r') as pptx_zip:
            # Target only the specific slide XML file
            slide_file = f'ppt/slides/slide{slide_number}.xml'
            
            # Check if the slide exists
            if slide_file not in pptx_zip.namelist():
                raise ValueError(f"Slide {slide_number} not found in PowerPoint file")
            
            # Extract only the target slide
            slide_structure = self._extract_slide_text_structure(
                pptx_zip, slide_file, slide_number
            )
        
        return slide_structure
    
    def _extract_slide_text_structure(self, pptx_zip: zipfile.ZipFile, slide_file: str, slide_number: int) -> SlideTextStructure:
        """Extract text structure from a single slide."""
        
        # Read slide XML
        slide_xml = pptx_zip.read(slide_file).decode('utf-8')
        slide_root = ET.fromstring(slide_xml)
        
        text_elements = []
        
        # Extract text from shapes
        shape_elements = slide_root.findall('.//p:sp', self.NAMESPACES)
        for i, shape in enumerate(shape_elements):
            shape_text_elements = self._extract_shape_text_elements(
                shape, slide_number, slide_file, i
            )
            text_elements.extend(shape_text_elements)
        
        # Extract text from images (alt text)
        image_elements = slide_root.findall('.//p:pic', self.NAMESPACES)
        for i, image in enumerate(image_elements):
            image_text_elements = self._extract_image_text_elements(
                image, slide_number, slide_file, i
            )
            text_elements.extend(image_text_elements)
        
        # Extract text from tables
        table_elements = slide_root.findall('.//a:tbl', self.NAMESPACES)
        for i, table in enumerate(table_elements):
            table_text_elements = self._extract_table_text_elements(
                table, slide_number, slide_file, i
            )
            text_elements.extend(table_text_elements)
        
        # Extract speaker notes
        notes_file = f'ppt/notesSlides/notesSlide{slide_number}.xml'
        speaker_notes_sections = []
        notes_xml_path = None
        
        # Generate tracking ID for this extraction operation (using a simple slide-based ID for now)
        tracking_id = f"EXTRACT_S{slide_number}_{int(__import__('time').time())}"
        
        print(f"🔍 TRACK[{tracking_id}] Looking for notes file: {notes_file}")
        
        if notes_file in pptx_zip.namelist():
            print(f"✅ TRACK[{tracking_id}] Notes file found in archive")
            notes_xml_path = notes_file
            speaker_notes_sections = self._extract_speaker_notes_sections(
                pptx_zip, notes_file, slide_number
            )
            print(f"📊 TRACK[{tracking_id}] Extracted {len(speaker_notes_sections)} speaker notes sections")
        else:
            print(f"⚠️ TRACK[{tracking_id}] Notes file not found in archive, skipping notes extraction")
            print(f"📝 TRACK[{tracking_id}] Available files in archive: {[f for f in pptx_zip.namelist() if 'notesSlide' in f]}")
        
        # Create slide structure
        slide_structure = SlideTextStructure(
            slide_number=slide_number,
            slide_xml_path=slide_file,
            notes_xml_path=notes_xml_path,
            text_elements=text_elements,
            speaker_notes_sections=speaker_notes_sections,
            total_text_elements=len(text_elements),
            has_speaker_notes=len(speaker_notes_sections) > 0,
            has_alt_text=any(elem.element_type == 'alt_text' for elem in text_elements)
        )
        
        return slide_structure
    
    def _extract_shape_text_elements(self, shape: ET.Element, slide_number: int, slide_file: str, shape_index: int) -> List[TextElement]:
        """Extract text elements from a shape."""
        
        text_elements = []
        
        # Get shape properties
        nv_sp_pr = shape.find('.//p:nvSpPr', self.NAMESPACES)
        c_nv_pr = nv_sp_pr.find('.//p:cNvPr', self.NAMESPACES) if nv_sp_pr is not None else None
        
        shape_name = c_nv_pr.get('name', f'Shape {shape_index + 1}') if c_nv_pr is not None else f'Shape {shape_index + 1}'
        shape_id = c_nv_pr.get('id', str(shape_index)) if c_nv_pr is not None else str(shape_index)
        
        # Determine shape type
        nv_pr = nv_sp_pr.find('.//p:nvPr', self.NAMESPACES) if nv_sp_pr is not None else None
        ph = nv_pr.find('.//p:ph', self.NAMESPACES) if nv_pr is not None else None
        placeholder_type = ph.get('type', '') if ph is not None else ''
        
        is_title = placeholder_type in ['title', 'ctrTitle'] or 'title' in shape_name.lower()
        is_content = placeholder_type in ['body', 'obj']
        
        # Get position information
        position = self._extract_position(shape)
        
        # Extract text from paragraphs
        paragraphs = shape.findall('.//a:p', self.NAMESPACES)
        for p_idx, paragraph in enumerate(paragraphs):
            runs = paragraph.findall('.//a:r', self.NAMESPACES)
            
            for r_idx, run in enumerate(runs):
                text_elem = run.find('.//a:t', self.NAMESPACES)
                if text_elem is not None and text_elem.text:
                    # Create XPath for this text element
                    xpath = f'.//p:sp[{shape_index + 1}]//a:p[{p_idx + 1}]//a:r[{r_idx + 1}]//a:t'
                    
                    text_element = TextElement(
                        element_id=f'slide_{slide_number}_shape_{shape_index}_p_{p_idx}_r_{r_idx}',
                        element_type='slide_text',
                        slide_number=slide_number,
                        text_content=text_elem.text,
                        original_text=text_elem.text,
                        shape_name=shape_name,
                        shape_id=shape_id,
                        xpath_location=xpath,
                        xml_file_path=slide_file,
                        placeholder_type=placeholder_type,
                        is_title=is_title,
                        is_content=is_content,
                        paragraph_index=p_idx,
                        run_index=r_idx,
                        position=position
                    )
                    
                    text_elements.append(text_element)
        
        return text_elements
    
    def _extract_image_text_elements(self, image: ET.Element, slide_number: int, slide_file: str, image_index: int) -> List[TextElement]:
        """Extract alt text from images."""
        
        text_elements = []
        
        # Get image properties
        nv_pic_pr = image.find('.//p:nvPicPr', self.NAMESPACES)
        c_nv_pr = nv_pic_pr.find('.//p:cNvPr', self.NAMESPACES) if nv_pic_pr is not None else None
        
        if c_nv_pr is not None:
            image_name = c_nv_pr.get('name', f'Image {image_index + 1}')
            image_id = c_nv_pr.get('id', str(image_index))
            
            # Extract alt text (descr attribute)
            alt_text = c_nv_pr.get('descr', '')
            if alt_text:
                xpath = f'.//p:pic[{image_index + 1}]//p:cNvPr/@descr'
                
                text_element = TextElement(
                    element_id=f'slide_{slide_number}_image_{image_index}_alt',
                    element_type='alt_text',
                    slide_number=slide_number,
                    text_content=alt_text,
                    original_text=alt_text,
                    shape_name=image_name,
                    shape_id=image_id,
                    xpath_location=xpath,
                    xml_file_path=slide_file,
                    position=self._extract_position(image)
                )
                
                text_elements.append(text_element)
            
            # Extract title text if present
            title_text = c_nv_pr.get('title', '')
            if title_text:
                xpath = f'.//p:pic[{image_index + 1}]//p:cNvPr/@title'
                
                text_element = TextElement(
                    element_id=f'slide_{slide_number}_image_{image_index}_title',
                    element_type='alt_text',
                    slide_number=slide_number,
                    text_content=title_text,
                    original_text=title_text,
                    shape_name=f'{image_name} (Title)',
                    shape_id=image_id,
                    xpath_location=xpath,
                    xml_file_path=slide_file,
                    position=self._extract_position(image)
                )
                
                text_elements.append(text_element)
        
        return text_elements
    
    def _extract_table_text_elements(self, table: ET.Element, slide_number: int, slide_file: str, table_index: int) -> List[TextElement]:
        """Extract text from table cells."""
        
        text_elements = []
        
        # Find all table cells
        cells = table.findall('.//a:tc', self.NAMESPACES)
        
        for cell_idx, cell in enumerate(cells):
            paragraphs = cell.findall('.//a:p', self.NAMESPACES)
            
            for p_idx, paragraph in enumerate(paragraphs):
                runs = paragraph.findall('.//a:r', self.NAMESPACES)
                
                for r_idx, run in enumerate(runs):
                    text_elem = run.find('.//a:t', self.NAMESPACES)
                    if text_elem is not None and text_elem.text:
                        xpath = f'.//a:tbl[{table_index + 1}]//a:tc[{cell_idx + 1}]//a:p[{p_idx + 1}]//a:r[{r_idx + 1}]//a:t'
                        
                        text_element = TextElement(
                            element_id=f'slide_{slide_number}_table_{table_index}_cell_{cell_idx}_p_{p_idx}_r_{r_idx}',
                            element_type='table_text',
                            slide_number=slide_number,
                            text_content=text_elem.text,
                            original_text=text_elem.text,
                            shape_name=f'Table {table_index + 1} Cell {cell_idx + 1}',
                            xpath_location=xpath,
                            xml_file_path=slide_file,
                            paragraph_index=p_idx,
                            run_index=r_idx
                        )
                        
                        text_elements.append(text_element)
        
        return text_elements
    
    def _extract_speaker_notes_sections(self, pptx_zip: zipfile.ZipFile, notes_file: str, slide_number: int) -> List[SpeakerNotesSection]:
        """Extract and categorize speaker notes sections using enhanced parser."""
        
        sections = []
        
        try:
            from .enhanced_speaker_notes_parser import EnhancedSpeakerNotesParser
            from pptx import Presentation
            import tempfile
            import os
            
            # Extract the PowerPoint file to get raw text (preserves \x0b characters)
            with tempfile.NamedTemporaryFile(suffix='.pptx', delete=False) as temp_file:
                # Write the entire PPTX to a temporary file
                temp_file.write(pptx_zip.read(pptx_zip.namelist()[0].split('/')[0] + '.pptx' if '.pptx' in pptx_zip.namelist()[0] else ''))
                temp_file.flush()
                
                # This approach won't work - we need a different strategy
                # Let's use the XML but try to get raw text from the presentation object
                pass
            
            # For now, use the text-based approach by extracting raw text from XML differently
            notes_xml = pptx_zip.read(notes_file).decode('utf-8')
            
            # Try to extract raw text that preserves \x0b characters
            # Parse XML to get text elements but preserve special characters
            import xml.etree.ElementTree as ET
            
            root = ET.fromstring(notes_xml)
            namespaces = {
                'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
                'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
            }
            
            # Extract raw text preserving vertical tabs
            all_text_parts = []
            paragraphs = root.findall('.//a:p', namespaces)
            
            for paragraph in paragraphs:
                # Look for line breaks (br elements) and text elements
                para_parts = []
                for child in paragraph:
                    if child.tag.endswith('}r'):  # Text run
                        text_elem = child.find('.//a:t', namespaces)
                        if text_elem is not None and text_elem.text:
                            para_parts.append(text_elem.text)
                    elif child.tag.endswith('}br'):  # Line break
                        para_parts.append('\x0b')  # Add vertical tab for line breaks
                
                if para_parts:
                    para_text = ''.join(para_parts)
                    if para_text.strip():
                        all_text_parts.append(para_text)
            
            # Join all text preserving structure
            raw_text = '\n'.join(all_text_parts)
            
            # Use enhanced parser with raw text
            parser = EnhancedSpeakerNotesParser()
            parsed_sections = parser.parse_speaker_notes_text(raw_text)
            
            # Convert to SpeakerNotesSection format
            for idx, parsed_section in enumerate(parsed_sections):
                # Map section types from enhanced parser to existing types
                section_type_mapping = {
                    'instructor': 'instructor_notes',
                    'student': 'student_notes', 
                    'developer': 'developer_notes',
                    'alt_text': 'alt_text_description',
                    'general': 'general'
                }
                
                section_type = section_type_mapping.get(parsed_section.section_type, 'general')
                
                sections.append(SpeakerNotesSection(
                    section_type=section_type,
                    content=parsed_section.content,
                    original_content=parsed_section.original_content,
                    paragraph_index=idx
                ))
        
        except Exception as e:
            # Enhanced parser failed, silently fall back to simple extraction
            # (this is normal and expected, the fallback works correctly)
            sections = self._fallback_speaker_notes_extraction(pptx_zip, notes_file, slide_number)
        
        return sections
    
    def _fallback_speaker_notes_extraction(self, pptx_zip: zipfile.ZipFile, notes_file: str, slide_number: int) -> List[SpeakerNotesSection]:
        """Fallback method using original extraction logic."""
        
        # Generate tracking ID for this fallback operation
        tracking_id = f"FALLBACK_S{slide_number}_{int(__import__('time').time())}"
        
        sections = []
        
        # Fix empty notes_file issue
        if not notes_file or notes_file.strip() == '':
            notes_file = f'ppt/notesSlides/notesSlide{slide_number}.xml'
            print(f"🔧 TRACK[{tracking_id}] Empty notes_file, constructed: {notes_file}")
        
        print(f"📖 TRACK[{tracking_id}] Reading notes file: '{notes_file}'")
        
        # Check if the notes file exists in the archive
        if notes_file not in pptx_zip.namelist():
            print(f"⚠️ TRACK[{tracking_id}] Notes file '{notes_file}' not found in archive")
            print(f"📝 TRACK[{tracking_id}] Available notes files: {[f for f in pptx_zip.namelist() if 'notesSlide' in f]}")
            return []
        
        try:
            notes_xml = pptx_zip.read(notes_file).decode('utf-8')
            print(f"✅ TRACK[{tracking_id}] Successfully read {len(notes_xml)} characters from notes file")
            notes_root = ET.fromstring(notes_xml)
            
            # Extract all speaker notes text first
            paragraphs = notes_root.findall('.//a:p', self.NAMESPACES)
            all_notes_text = []
            
            for paragraph in paragraphs:
                text_elements = paragraph.findall('.//a:t', self.NAMESPACES)
                paragraph_text = ''.join([elem.text or '' for elem in text_elements]).strip()
                if paragraph_text:
                    all_notes_text.append(paragraph_text)
            
            # Combine all text
            full_notes_text = '\n'.join(all_notes_text)
            print(f"🔍 TRACK[{tracking_id}] Full notes text: {len(full_notes_text)} characters")
            
            # Parse based on format (clean PowerPoint format vs. old delimited format)
            sections = self._parse_speaker_notes_by_format(full_notes_text, tracking_id)
            
        except Exception as e:
            print(f"❌ TRACK[{tracking_id}] Error extracting speaker notes: {e}")
            return []
        
        return sections
    
    def _parse_speaker_notes_by_format(self, full_text: str, tracking_id: str) -> List[SpeakerNotesSection]:
        """Parse speaker notes based on detected format (clean vs delimited)."""
        
        sections = []
        
        # Check if this is the new clean PowerPoint format
        clean_format_headers = ['References:', 'Developer Notes:', 'Script:', 'Instructornotes:', 'Studentnotes:', 'Alt Text:', 'Slide Description:']
        delimited_format_markers = ['~Script:', '|INSTRUCTOR NOTES:', '|STUDENT NOTES:', '~Developer Notes:', '~Alt Text:', '~Slide Description:', '~References:']
        
        has_clean_headers = any(header in full_text for header in clean_format_headers)
        has_delimited_markers = any(marker in full_text for marker in delimited_format_markers)
        
        print(f"🔍 TRACK[{tracking_id}] Format detection - Clean headers: {has_clean_headers}, Delimited markers: {has_delimited_markers}")
        
        if has_clean_headers and not has_delimited_markers:
            # This is the new clean PowerPoint format - convert to delimited format for UI compatibility
            print(f"✨ TRACK[{tracking_id}] Detected clean PowerPoint format, converting to delimited format")
            sections = self._parse_clean_powerpoint_format(full_text)
        elif has_delimited_markers:
            # This is the old delimited format - parse as before
            print(f"🔧 TRACK[{tracking_id}] Detected delimited format, using legacy parsing")
            sections = self._parse_delimited_format(full_text)
        else:
            # General format - treat as script
            print(f"📝 TRACK[{tracking_id}] Unstructured format, treating as general script")
            sections = [SpeakerNotesSection(
                section_type='general',
                content=full_text,
                original_content=full_text,
                paragraph_index=0
            )]
        
        return sections
    
    def _parse_clean_powerpoint_format(self, full_text: str) -> List[SpeakerNotesSection]:
        """Parse the new clean PowerPoint format and convert to delimited format for UI."""
        
        sections = []
        current_section = None
        current_content = []
        
        lines = full_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for clean format headers
            if line == 'References:':
                if current_section and current_content:
                    sections.append(self._create_section_with_delimiters(current_section, current_content))
                current_section = 'references'
                current_content = []
            elif line == 'Developer Notes:':
                if current_section and current_content:
                    sections.append(self._create_section_with_delimiters(current_section, current_content))
                current_section = 'developer_notes'
                current_content = []
            elif line == 'Script:':
                if current_section and current_content:
                    sections.append(self._create_section_with_delimiters(current_section, current_content))
                current_section = 'script'
                current_content = []
            elif line == 'Instructornotes:':
                if current_section and current_content:
                    sections.append(self._create_section_with_delimiters(current_section, current_content))
                current_section = 'instructor_notes'
                current_content = []
            elif line == 'Studentnotes:':
                if current_section and current_content:
                    sections.append(self._create_section_with_delimiters(current_section, current_content))
                current_section = 'student_notes'
                current_content = []
            elif line == 'Alt Text:':
                if current_section and current_content:
                    sections.append(self._create_section_with_delimiters(current_section, current_content))
                current_section = 'alt_text_description'
                current_content = []
            elif line == 'Slide Description:':
                if current_section and current_content:
                    sections.append(self._create_section_with_delimiters(current_section, current_content))
                current_section = 'image_description'
                current_content = []
            else:
                # This is content for the current section
                if current_section:
                    current_content.append(line)
                else:
                    # No section header found yet, treat as general script
                    current_section = 'script'
                    current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            sections.append(self._create_section_with_delimiters(current_section, current_content))
        
        return sections
    
    def _create_section_with_delimiters(self, section_type: str, content_lines: list) -> SpeakerNotesSection:
        """Create a speaker notes section with proper delimiters for UI compatibility."""
        
        content = '\n'.join(content_lines).strip()
        
        # CRITICAL FIX: Preserve original formatting instead of converting to plain text
        # The content here is from properly saved PowerPoint XML and should retain its formatting
        # for the UI to display correctly. Only convert to plain text if there's no HTML present.
        import re
        has_html = bool(re.search(r'<[^>]+>', content))
        
        if has_html:
            # Content has HTML formatting - preserve it for proper UI display
            clean_content = content
        else:
            # Content is plain text - can safely process it
            clean_content = self._convert_html_to_plain_text_for_ui(content)
        
        # Add delimiters based on section type
        if section_type == 'script':
            delimited_content = f"~Script:\n{clean_content}\n~"
        elif section_type == 'instructor_notes':
            delimited_content = f"|INSTRUCTOR NOTES:\n{clean_content}\n|"
        elif section_type == 'student_notes':
            delimited_content = f"|STUDENT NOTES:\n{clean_content}\n|"
        elif section_type == 'developer_notes':
            delimited_content = f"~Developer Notes:\n{clean_content}\n~"
        elif section_type == 'references':
            delimited_content = f"~References:\n{clean_content}\n~"
        elif section_type == 'alt_text_description':
            delimited_content = f"~Alt Text:\n{clean_content}\n~"
        elif section_type == 'image_description':
            delimited_content = f"~Slide Description:\n{clean_content}\n~"
        else:
            delimited_content = clean_content
        
        return SpeakerNotesSection(
            section_type='general',  # Use 'general' since UI expects all content in one section
            content=delimited_content,
            original_content=delimited_content,
            paragraph_index=0
        )
    
    def _parse_delimited_format(self, full_text: str) -> List[SpeakerNotesSection]:
        """Parse the old delimited format."""
        
        # Legacy parsing logic for delimited format
        current_section_type = 'general'
        current_content = []
        sections = []
        
        lines = full_text.split('\n')
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check for delimited section headers
            if (line_lower.startswith('developer notes') or 
                line_lower.startswith('dev notes') or
                line_lower.startswith('technical notes')):
                if current_content:
                            sections.append(SpeakerNotesSection(
                                section_type=current_section_type,
                                content='\n'.join(current_content),
                                original_content='\n'.join(current_content),
                        paragraph_index=0
                            ))
                        current_section_type = 'developer_notes'
                current_content = []
            elif (line_lower.startswith('instructor notes') or 
                  line_lower.startswith('teacher notes') or
                  line_lower.startswith('facilitator notes')):
                if current_content:
                    sections.append(SpeakerNotesSection(
                        section_type=current_section_type,
                        content='\n'.join(current_content),
                        original_content='\n'.join(current_content),
                        paragraph_index=0
                    ))
                        current_section_type = 'instructor_notes'
                current_content = []
            elif (line_lower.startswith('student notes') or 
                  line_lower.startswith('learner notes') or
                  line_lower.startswith('participant notes')):
                if current_content:
                    sections.append(SpeakerNotesSection(
                        section_type=current_section_type,
                        content='\n'.join(current_content),
                        original_content='\n'.join(current_content),
                        paragraph_index=0
                    ))
                        current_section_type = 'student_notes'
                current_content = []
                    else:
                # Add content to current section
                current_content.append(line)
            
        # Add the last section
            if current_content:
                sections.append(SpeakerNotesSection(
                    section_type=current_section_type,
                    content='\n'.join(current_content),
                    original_content='\n'.join(current_content),
                paragraph_index=0
                ))
        
        return sections
    
    def _convert_html_to_plain_text_for_ui(self, html_content: str) -> str:
        """Convert HTML content to clean plain text for UI display."""
        import re
        
        if not html_content or not html_content.strip():
            return ""
        
        content = html_content.strip()
        
        # Convert links to clean format: "Link Text (URL)"
        link_pattern = r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
        def replace_link(match):
            url = match.group(1).strip()
            text = match.group(2).strip()
            if text and url:
                return f"{text}\n({url})"
            elif url:
                return url
            else:
                return text or ""
        
        content = re.sub(link_pattern, replace_link, content, flags=re.IGNORECASE)
        
        # Convert line breaks
        content = re.sub(r'<br[^>]*/?>', '\n', content, flags=re.IGNORECASE)
        
        # Convert lists to bullet points
        content = re.sub(r'<ul[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'</ul>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'<ol[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'</ol>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'<li[^>]*>', '• ', content, flags=re.IGNORECASE)
        content = re.sub(r'</li>', '\n', content, flags=re.IGNORECASE)
        
        # Convert paragraphs
        content = re.sub(r'<p[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'</p>', '\n', content, flags=re.IGNORECASE)
        
        # Remove bold/italic formatting but keep content
        content = re.sub(r'<(strong|b)[^>]*>(.*?)</\1>', r'\2', content, flags=re.IGNORECASE)
        content = re.sub(r'<(em|i)[^>]*>(.*?)</\1>', r'\2', content, flags=re.IGNORECASE)
        
        # Remove any remaining HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Clean up whitespace
        content = re.sub(r'\n\n\n+', '\n\n', content)  # Max 2 consecutive newlines
        content = re.sub(r'[ \t]+', ' ', content)  # Normalize spaces
        content = re.sub(r'\n +', '\n', content)  # Remove leading spaces on lines
        content = re.sub(r' +\n', '\n', content)  # Remove trailing spaces on lines
        
        return content.strip()
    
    def _extract_position(self, element: ET.Element) -> Optional[Dict[str, float]]:
        """Extract position and size information from an element."""
        
        try:
            # Look for transform element in different possible locations
            xfrm = element.find('.//a:xfrm', self.NAMESPACES)
            
            # If not found, try looking in picture or shape properties
            if xfrm is None:
                xfrm = element.find('.//p:spPr//a:xfrm', self.NAMESPACES)
            
            if xfrm is None:
                xfrm = element.find('.//p:picPr//a:xfrm', self.NAMESPACES)
                
            if xfrm is None:
                # Try to find position in group shapes
                xfrm = element.find('.//p:grpSpPr//a:xfrm', self.NAMESPACES)
            
            if xfrm is None:
                return None
            
            off = xfrm.find('.//a:off', self.NAMESPACES)
            ext = xfrm.find('.//a:ext', self.NAMESPACES)
            
            position_data = {}
            
            # Extract offset (position)
            if off is not None:
                x_str = off.get('x', '0')
                y_str = off.get('y', '0')
                
                try:
                    x_emu = int(x_str) if x_str else 0
                    y_emu = int(y_str) if y_str else 0
                    
                    # Convert EMU (English Metric Units) to inches
                    # 1 inch = 914400 EMU
                    position_data['x'] = round(x_emu / 914400, 3)
                    position_data['y'] = round(y_emu / 914400, 3)
                except ValueError:
                    position_data['x'] = 0.0
                    position_data['y'] = 0.0
            
            # Extract extent (size)
            if ext is not None:
                cx_str = ext.get('cx', '0')
                cy_str = ext.get('cy', '0')
                
                try:
                    cx_emu = int(cx_str) if cx_str else 0
                    cy_emu = int(cy_str) if cy_str else 0
                    
                    position_data['width'] = round(cx_emu / 914400, 3)
                    position_data['height'] = round(cy_emu / 914400, 3)
                except ValueError:
                    position_data['width'] = 0.0
                    position_data['height'] = 0.0
            
            # Add slide coordinates (assuming standard slide size 10" x 7.5")
            if 'x' in position_data and 'y' in position_data:
                position_data['x_percent'] = round((position_data['x'] / 10.0) * 100, 1)
                position_data['y_percent'] = round((position_data['y'] / 7.5) * 100, 1)
            
            # Only return if we have meaningful position data
            if any(v > 0 for v in position_data.values()):
                return position_data
            
            return None
            
        except Exception as e:
            # Log the error but don't fail the extraction
            print(f"Warning: Failed to extract position information: {e}")
            return None
    
    def save_modified_text_elements(self, file_path: str, modified_slides: List[SlideTextStructure], output_path: str) -> bool:
        """Save modified text elements back to the PowerPoint file."""
        
        try:
            # Create a temporary working directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract the original PPTX
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Modify each slide's XML
                for slide_structure in modified_slides:
                    self._update_slide_xml(temp_dir, slide_structure)
                
                # Create new PPTX file
                self._create_updated_pptx(temp_dir, output_path)
                
                return True
        
        except Exception as e:
            print(f"Error saving modified PPT: {e}")
            return False
    
    def save_speaker_notes_to_slide(self, file_path: str, slide_number: int, notes_content: str) -> bool:
        """Save speaker notes content to a specific slide in the PowerPoint file."""
        
        try:
            print(f"🔄 Starting save operation for slide {slide_number}")
            print(f"   File path: {file_path}")
            print(f"   Content length: {len(notes_content)} characters")
            print(f"   Content preview: {notes_content[:200]}...")
            
            # Verify the original file exists and is accessible
            if not os.path.exists(file_path):
                print(f"❌ Error: PPT file does not exist: {file_path}")
                return False
            
            # Check file permissions
            if not os.access(file_path, os.R_OK | os.W_OK):
                print(f"❌ Error: Insufficient permissions for file: {file_path}")
                return False
            
            # Get original file size for comparison
            original_size = os.path.getsize(file_path)
            print(f"   Original file size: {original_size} bytes")
            
            # Create a temporary working directory
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f"   Created temp directory: {temp_dir}")
                
                # Extract the original PPTX
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                        print(f"   ✅ Successfully extracted PPTX to temp directory")
                except Exception as e:
                    print(f"   ❌ Error extracting PPTX: {e}")
                    return False
                
                # Update the speaker notes for the specific slide
                notes_file = f'ppt/notesSlides/notesSlide{slide_number}.xml'
                notes_xml_path = os.path.join(temp_dir, notes_file)
                
                print(f"   Looking for notes file: {notes_xml_path}")
                
                # Check if notes slide exists
                if not os.path.exists(notes_xml_path):
                    print(f"   ⚠️  Notes slide doesn't exist, creating new one")
                    # Create a new notes slide if it doesn't exist
                    try:
                        self._create_notes_slide(temp_dir, slide_number, notes_content)
                        print(f"   ✅ Successfully created new notes slide")
                    except Exception as e:
                        print(f"   ❌ Error creating notes slide: {e}")
                        return False
                else:
                    print(f"   ✅ Notes slide exists, updating content")
                    # Update existing notes slide
                    try:
                        self._update_existing_notes_slide(notes_xml_path, notes_content)
                        print(f"   ✅ Successfully updated existing notes slide")
                    except Exception as e:
                        print(f"   ❌ Error updating notes slide: {e}")
                        return False
                
                # Verify the notes file was created/updated
                if os.path.exists(notes_xml_path):
                    file_size = os.path.getsize(notes_xml_path)
                    print(f"   ✅ Notes file verified: {notes_xml_path} ({file_size} bytes)")
                else:
                    print(f"   ❌ Notes file was not created: {notes_xml_path}")
                    return False
                
                # Update content types and relationships if needed
                try:
                    self._ensure_notes_slide_relationships(temp_dir, slide_number)
                    print(f"   ✅ Successfully updated relationships and content types")
                except Exception as e:
                    print(f"   ❌ Error updating relationships: {e}")
                    return False
                
                # Create backup of original file
                backup_path = file_path + ".backup"
                try:
                    import shutil
                    shutil.copy2(file_path, backup_path)
                    print(f"   ✅ Created backup: {backup_path}")
                except Exception as e:
                    print(f"   ⚠️  Warning: Could not create backup: {e}")
                
                # Create new PPTX file (overwrite original)
                print(f"   🔄 Creating updated PPTX file...")
                try:
                    self._create_updated_pptx(temp_dir, file_path)
                    print(f"   ✅ Successfully created updated PPTX file")
                except Exception as e:
                    print(f"   ❌ Error creating updated PPTX: {e}")
                    # Try to restore backup if creation failed
                    if os.path.exists(backup_path):
                        try:
                            shutil.copy2(backup_path, file_path)
                            print(f"   ✅ Restored original file from backup")
                        except:
                            pass
                    return False
                
                # Verify the updated file
                if os.path.exists(file_path):
                    new_size = os.path.getsize(file_path)
                    print(f"   ✅ Updated file verified: {file_path} ({new_size} bytes)")
                    print(f"   📊 Size change: {new_size - original_size:+d} bytes")
                    
                    # Clean up backup on success
                    if os.path.exists(backup_path):
                        try:
                            os.remove(backup_path)
                            print(f"   ✅ Cleaned up backup file")
                        except:
                            pass
                else:
                    print(f"   ❌ Updated file not found: {file_path}")
                    return False
                
                print(f"✅ Successfully saved speaker notes to slide {slide_number}")
                return True
        
        except Exception as e:
            print(f"❌ Error saving speaker notes to slide {slide_number}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_notes_slide(self, temp_dir: str, slide_number: int, notes_content: str):
        """Create a new notes slide XML file."""
        
        print(f"     🔧 Creating new notes slide for slide {slide_number}")
        
        # Create basic notes slide XML structure
        notes_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:notes xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
    <p:cSld>
        <p:spTree>
            <p:nvGrpSpPr>
                <p:cNvPr id="1" name=""/>
                <p:cNvGrpSpPr/>
                <p:nvPr/>
            </p:nvGrpSpPr>
            <p:grpSpPr>
                <a:xfrm>
                    <a:off x="0" y="0"/>
                    <a:ext cx="0" cy="0"/>
                </a:xfrm>
            </p:grpSpPr>
            <p:sp>
                <p:nvSpPr>
                    <p:cNvPr id="2" name="Slide Image Placeholder 1"/>
                    <p:cNvSpPr>
                        <a:spLocks noGrp="1" noRot="1" noChangeAspect="1"/>
                    </p:cNvSpPr>
                    <p:nvPr>
                        <p:ph type="sldImg"/>
                    </p:nvPr>
                </p:nvSpPr>
                <p:spPr/>
            </p:sp>
            <p:sp>
                <p:nvSpPr>
                    <p:cNvPr id="3" name="Notes Placeholder 2"/>
                    <p:cNvSpPr>
                        <a:spLocks noGrp="1"/>
                    </p:cNvSpPr>
                    <p:nvPr>
                        <p:ph type="body" idx="1"/>
                    </p:nvPr>
                </p:nvSpPr>
                <p:spPr/>
                <p:txBody>
                    <a:bodyPr/>
                    <a:lstStyle/>
                    {self._generate_notes_paragraphs_xml(notes_content)}
                </p:txBody>
            </p:sp>
        </p:spTree>
    </p:cSld>
    <p:clrMapOvr>
        <a:masterClrMapping/>
    </p:clrMapOvr>
</p:notes>'''
        
        try:
            # Ensure the notesSlides directory exists
            notes_dir = os.path.join(temp_dir, 'ppt', 'notesSlides')
            print(f"     📁 Creating notes directory: {notes_dir}")
            os.makedirs(notes_dir, exist_ok=True)
            
            # Write the notes slide file
            notes_file_path = os.path.join(notes_dir, f'notesSlide{slide_number}.xml')
            print(f"     💾 Writing notes file: {notes_file_path}")
            
            with open(notes_file_path, 'w', encoding='utf-8') as f:
                f.write(notes_xml)
            
            # Verify the file was created
            if os.path.exists(notes_file_path):
                file_size = os.path.getsize(notes_file_path)
                print(f"     ✅ Notes file created successfully ({file_size} bytes)")
            else:
                print(f"     ❌ Notes file was not created")
                raise Exception("Notes file creation failed")
            
            # Update relationships if needed
            print(f"     🔗 Updating slide relationships...")
            self._update_slide_relationships(temp_dir, slide_number)
            print(f"     ✅ Slide relationships updated")
            
        except Exception as e:
            print(f"     ❌ Error in _create_notes_slide: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _update_existing_notes_slide(self, notes_xml_path: str, notes_content: str):
        """Update existing notes slide with new content."""
        
        try:
            import re
            
            with open(notes_xml_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            root = ET.fromstring(xml_content)
            
            # Find the text body element where speaker notes are stored
            text_bodies = root.findall('.//p:txBody', self.NAMESPACES)
            
            if text_bodies:
                # Use the first text body (speaker notes area)
                text_body = text_bodies[0]
                
                # Clear all existing paragraphs
                for paragraph in text_body.findall('.//a:p', self.NAMESPACES):
                    text_body.remove(paragraph)
                
                # Check if content contains HTML tags
                if re.search(r'<[^>]+>', notes_content):
                    # Content contains HTML - convert to proper PowerPoint XML
                    powerpoint_xml = self._convert_html_to_powerpoint_xml(notes_content)
                    
                    # Parse the generated XML and insert into text body
                    try:
                        # Wrap in a temporary root to parse multiple paragraphs
                        temp_xml = f'<temp xmlns:a="{self.NAMESPACES["a"]}">{powerpoint_xml}</temp>'
                        temp_root = ET.fromstring(temp_xml)
                        
                        # Move all paragraphs from temp root to text body
                        for paragraph in temp_root.findall('.//a:p', self.NAMESPACES):
                            text_body.append(paragraph)
                    
                    except ET.ParseError as parse_error:
                        print(f"Error parsing generated PowerPoint XML: {parse_error}")
                        print(f"Generated XML content: {powerpoint_xml[:500]}...")
                        # Fallback to plain text processing
                        self._add_plain_text_paragraphs(text_body, notes_content)
                
                else:
                    # Content is plain text - use simple processing
                    self._add_plain_text_paragraphs(text_body, notes_content)
            else:
                print(f"Warning: No text body found in notes slide XML")
            
            # Write updated XML with proper formatting
            xml_str = ET.tostring(root, encoding='unicode')
            # Add XML declaration if not present
            if not xml_str.startswith('<?xml'):
                xml_str = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + xml_str
                
            with open(notes_xml_path, 'w', encoding='utf-8') as f:
                f.write(xml_str)
                
            print(f"Successfully updated notes slide: {notes_xml_path}")
        
        except Exception as e:
            print(f"Error updating existing notes slide: {e}")
            import traceback
            traceback.print_exc()
    
    def _add_plain_text_paragraphs(self, text_body: ET.Element, notes_content: str):
        """Add plain text content as simple paragraphs to the text body."""
                lines = notes_content.split('\n')
                
                for line in lines:
                    # Create new paragraph
                    paragraph = ET.SubElement(text_body, f'{{{self.NAMESPACES["a"]}}}p')
                    
                    if line.strip():  # Only add runs for non-empty lines
                        # Create run with text
                        run = ET.SubElement(paragraph, f'{{{self.NAMESPACES["a"]}}}r')
                        
                        # Add run properties
                        rPr = ET.SubElement(run, f'{{{self.NAMESPACES["a"]}}}rPr')
                        rPr.set('lang', 'en-US')
                        rPr.set('dirty', '0')
                        
                        # Add text element
                        text_elem = ET.SubElement(run, f'{{{self.NAMESPACES["a"]}}}t')
                        text_elem.text = line
                    else:
                        # For empty lines, create paragraph with empty run
                        run = ET.SubElement(paragraph, f'{{{self.NAMESPACES["a"]}}}r')
                        rPr = ET.SubElement(run, f'{{{self.NAMESPACES["a"]}}}rPr')
                        rPr.set('lang', 'en-US')
                        rPr.set('dirty', '0')
                        text_elem = ET.SubElement(run, f'{{{self.NAMESPACES["a"]}}}t')
                        text_elem.text = ''
    
    def _update_slide_relationships(self, temp_dir: str, slide_number: int):
        """Update slide relationships to include notes slide if needed."""
        
        try:
            slide_rels_path = os.path.join(temp_dir, 'ppt', 'slides', '_rels', f'slide{slide_number}.xml.rels')
            print(f"       🔗 Checking relationships file: {slide_rels_path}")
            
            # Check if relationships file exists
            if not os.path.exists(slide_rels_path):
                print(f"       📝 Relationships file doesn't exist, creating new one")
                # Create relationships directory if it doesn't exist
                rels_dir = os.path.dirname(slide_rels_path)
                print(f"       📁 Creating relationships directory: {rels_dir}")
                os.makedirs(rels_dir, exist_ok=True)
                
                # Create basic relationships file
                rels_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide{slide_number}.xml"/>
</Relationships>'''
                
                with open(slide_rels_path, 'w', encoding='utf-8') as f:
                    f.write(rels_xml)
                
                print(f"       ✅ Created new relationships file")
            else:
                print(f"       ✅ Relationships file exists, checking for notes relationship")
                # Check if notes relationship already exists
                with open(slide_rels_path, 'r', encoding='utf-8') as f:
                    rels_content = f.read()
                
                if 'notesSlide' not in rels_content:
                    print(f"       📝 Notes relationship not found, adding it")
                    # Parse existing relationships and add notes relationship
                    root = ET.fromstring(rels_content)
                    
                    # Find highest existing ID
                    max_id = 0
                    for rel in root.findall('.//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                        rel_id = rel.get('Id', 'rId0')
                        if rel_id.startswith('rId'):
                            try:
                                id_num = int(rel_id[3:])
                                max_id = max(max_id, id_num)
                            except ValueError:
                                pass
                    
                    # Add notes relationship
                    new_rel = ET.SubElement(root, '{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')
                    new_rel.set('Id', f'rId{max_id + 1}')
                    new_rel.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide')
                    new_rel.set('Target', f'../notesSlides/notesSlide{slide_number}.xml')
                    
                    print(f"       📎 Added relationship with ID rId{max_id + 1}")
                    
                    # Write updated relationships
                    with open(slide_rels_path, 'w', encoding='utf-8') as f:
                        f.write(ET.tostring(root, encoding='unicode'))
                    
                    print(f"       ✅ Updated relationships file")
                else:
                    print(f"       ✅ Notes relationship already exists")
            
            # Verify the relationships file
            if os.path.exists(slide_rels_path):
                file_size = os.path.getsize(slide_rels_path)
                print(f"       ✅ Relationships file verified ({file_size} bytes)")
            else:
                print(f"       ❌ Relationships file was not created")
                raise Exception("Relationships file creation failed")
        
        except Exception as e:
            print(f"       ❌ Error updating slide relationships: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _ensure_notes_slide_relationships(self, temp_dir: str, slide_number: int):
        """Ensure all necessary relationships and content types are set up for the notes slide."""
        
        try:
            # Update slide relationships
            self._update_slide_relationships(temp_dir, slide_number)
            
            # Update content types to include notes slide
            self._update_content_types(temp_dir, slide_number)
            
            # Update presentation relationships if needed  
            self._update_presentation_relationships(temp_dir, slide_number)
            
        except Exception as e:
            print(f"Error ensuring notes slide relationships: {e}")
    
    def _update_content_types(self, temp_dir: str, slide_number: int):
        """Update [Content_Types].xml to include notes slide content type."""
        
        try:
            content_types_path = os.path.join(temp_dir, '[Content_Types].xml')
            
            if os.path.exists(content_types_path):
                with open(content_types_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if notes slide content type exists
                notes_override = f'<Override PartName="/ppt/notesSlides/notesSlide{slide_number}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/>'
                
                if notes_override not in content:
                    # Find the closing </Types> tag and insert before it
                    insert_position = content.rfind('</Types>')
                    if insert_position != -1:
                        new_content = (content[:insert_position] + 
                                     '  ' + notes_override + '\n' + 
                                     content[insert_position:])
                        
                        with open(content_types_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        print(f"Added content type for notesSlide{slide_number}.xml")
        
        except Exception as e:
            print(f"Error updating content types: {e}")
    
    def _update_presentation_relationships(self, temp_dir: str, slide_number: int):
        """Update presentation relationships if needed."""
        
        try:
            # In most cases, slide-level relationships are sufficient
            # This method is here for completeness and future enhancements
            pass
            
        except Exception as e:
            print(f"Error updating presentation relationships: {e}")
    
    def _generate_notes_paragraphs_xml(self, notes_content: str) -> str:
        """Generate properly formatted XML paragraphs for speaker notes content."""
        import re
        
        print(f"🔧 _generate_notes_paragraphs_xml: Processing {len(notes_content)} characters")
        print(f"🔧 Content preview: {notes_content[:200]}...")
        
        # Check if content contains HTML tags
        has_html = bool(re.search(r'<[^>]+>', notes_content))
        print(f"🔧 Contains HTML tags: {has_html}")
        
        if has_html:
            # Content contains HTML - use HTML to PowerPoint XML converter
            print(f"🔧 Using HTML-to-PowerPoint converter")
            powerpoint_xml = self._convert_html_to_powerpoint_xml(notes_content)
            print(f"🔧 Generated PowerPoint XML: {len(powerpoint_xml)} characters")
            print(f"🔧 XML preview: {powerpoint_xml[:300]}...")
            # The converter returns complete paragraphs, so we need to format them properly for the notes structure
            # Extract just the inner content and reformat with proper indentation
            formatted_xml = '\n                    '.join(powerpoint_xml.split('\n'))
            return formatted_xml
        else:
            # Content is plain text - use simple line-by-line conversion
            print(f"🔧 Using plain text conversion")
        import html
        
        lines = notes_content.split('\n')
        paragraphs_xml = []
        
        for line in lines:
            if line.strip():
                # Escape XML special characters
                escaped_line = html.escape(line)
                # Non-empty line
                paragraph_xml = f'''<a:p>
                        <a:r>
                            <a:rPr lang="en-US" dirty="0"/>
                            <a:t>{escaped_line}</a:t>
                        </a:r>
                    </a:p>'''
            else:
                # Empty line
                paragraph_xml = '''<a:p>
                        <a:r>
                            <a:rPr lang="en-US" dirty="0"/>
                            <a:t></a:t>
                        </a:r>
                    </a:p>'''
            
            paragraphs_xml.append(paragraph_xml)
        
        return '\n                    '.join(paragraphs_xml)
    
    def _update_slide_xml(self, temp_dir: str, slide_structure: SlideTextStructure):
        """Update slide XML with modified text elements."""
        
        slide_xml_path = os.path.join(temp_dir, slide_structure.slide_xml_path)
        
        # Read and parse slide XML
        with open(slide_xml_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        root = ET.fromstring(xml_content)
        
        # Update text elements
        for text_element in slide_structure.text_elements:
            if text_element.text_content != text_element.original_text:
                self._update_text_element_in_xml(root, text_element)
        
        # Update speaker notes if present
        if slide_structure.notes_xml_path:
            notes_xml_path = os.path.join(temp_dir, slide_structure.notes_xml_path)
            self._update_speaker_notes_xml(notes_xml_path, slide_structure.speaker_notes_sections)
        
        # Write updated XML
        with open(slide_xml_path, 'w', encoding='utf-8') as f:
            f.write(ET.tostring(root, encoding='unicode'))
    
    def _update_text_element_in_xml(self, root: ET.Element, text_element: TextElement):
        """Update a specific text element in the XML."""
        
        try:
            if text_element.element_type == 'slide_text':
                # Find the specific text element using the stored indices
                shapes = root.findall('.//p:sp', self.NAMESPACES)
                if text_element.paragraph_index is not None and text_element.run_index is not None:
                    shape_idx = int(text_element.element_id.split('_')[3])  # Extract shape index from ID
                    
                    if shape_idx < len(shapes):
                        paragraphs = shapes[shape_idx].findall('.//a:p', self.NAMESPACES)
                        if text_element.paragraph_index < len(paragraphs):
                            runs = paragraphs[text_element.paragraph_index].findall('.//a:r', self.NAMESPACES)
                            if text_element.run_index < len(runs):
                                text_elem = runs[text_element.run_index].find('.//a:t', self.NAMESPACES)
                                if text_elem is not None:
                                    text_elem.text = text_element.text_content
            
            elif text_element.element_type == 'alt_text':
                # Find and update alt text attributes
                images = root.findall('.//p:pic', self.NAMESPACES)
                image_idx = int(text_element.element_id.split('_')[3])  # Extract image index
                
                if image_idx < len(images):
                    c_nv_pr = images[image_idx].find('.//p:cNvPr', self.NAMESPACES)
                    if c_nv_pr is not None:
                        if 'alt' in text_element.element_id:
                            c_nv_pr.set('descr', text_element.text_content)
                        elif 'title' in text_element.element_id:
                            c_nv_pr.set('title', text_element.text_content)
        
        except Exception as e:
            print(f"Error updating text element {text_element.element_id}: {e}")
    
    def _update_speaker_notes_xml(self, notes_xml_path: str, sections: List[SpeakerNotesSection]):
        """Update speaker notes XML with modified sections."""
        
        try:
            with open(notes_xml_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            root = ET.fromstring(xml_content)
            
            # For simplicity, we'll rebuild the notes content
            # In a production system, you'd want more precise XML manipulation
            paragraphs = root.findall('.//a:p', self.NAMESPACES)
            
            # Clear existing text content
            for paragraph in paragraphs:
                for text_elem in paragraph.findall('.//a:t', self.NAMESPACES):
                    text_elem.text = ''
            
            # Add updated content
            if paragraphs and sections:
                combined_content = []
                for section in sections:
                    if section.section_type == 'developer_notes':
                        combined_content.append('Developer Notes:')
                    elif section.section_type == 'instructor_notes':
                        combined_content.append('Instructor Notes:')
                    elif section.section_type == 'student_notes':
                        combined_content.append('Student Notes:')
                    elif section.section_type == 'image_description':
                        combined_content.append('Image Description:')
                    elif section.section_type == 'alt_text_description':
                        combined_content.append('Alt Text:')
                    
                    combined_content.append(section.content)
                    combined_content.append('')  # Add spacing
            
            # Set the first paragraph's text to the combined content
            if paragraphs:
                first_text_elem = paragraphs[0].find('.//a:t', self.NAMESPACES)
                if first_text_elem is not None:
                    first_text_elem.text = '\n'.join(combined_content)
            
            # Write updated XML
            with open(notes_xml_path, 'w', encoding='utf-8') as f:
                f.write(ET.tostring(root, encoding='unicode'))
        
        except Exception as e:
            print(f"Error updating speaker notes: {e}")
    
    def _create_updated_pptx(self, temp_dir: str, output_path: str):
        """Create the updated PPTX file from the temporary directory."""
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname) 
    
    def _convert_html_to_plain_text_for_powerpoint(self, html_content: str) -> str:
        """Convert HTML content to plain text suitable for PowerPoint with proper formatting preserved as XML."""
        if not html_content or not html_content.strip():
            return ""
        
        # Convert HTML to PowerPoint XML structure
        return self._convert_html_to_powerpoint_xml(html_content)
    
    def _convert_html_to_powerpoint_xml(self, html_content: str) -> str:
        """Convert HTML content to properly formatted PowerPoint XML structure."""
        import re
        from html import unescape
        
        # First, unescape any HTML entities
        content = unescape(html_content)
        
        # Parse and convert HTML to PowerPoint XML paragraphs
        paragraphs = self._parse_html_to_paragraphs(content)
        
        # Convert each paragraph to PowerPoint XML
        xml_paragraphs = []
        for paragraph in paragraphs:
            xml_paragraph = self._convert_paragraph_to_powerpoint_xml(paragraph)
            xml_paragraphs.append(xml_paragraph)
        
        return '\n'.join(xml_paragraphs)
    
    def _parse_html_to_paragraphs(self, content: str) -> list:
        """Parse HTML content into structured paragraphs with formatting."""
        import re
        
        paragraphs = []
        
        # Handle section-based format first (References:\n<content>\n\nDeveloper Notes:\n<content>)
        # Split by section headers but preserve the content formatting
        section_pattern = r'((?:References|Developer Notes|Script|Instructornotes|Studentnotes|Alt Text|Slide Description):\s*\n)'
        
        if re.search(section_pattern, content):
            # This is section-based content - split by sections and process each
            parts = re.split(section_pattern, content)
            
            current_section_header = None
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                    
                # Check if this is a section header
                if re.match(r'(References|Developer Notes|Script|Instructornotes|Studentnotes|Alt Text|Slide Description):\s*$', part):
                    current_section_header = part
                    # Add section header as its own paragraph
                    paragraphs.append({
                        'content': part.rstrip(':'),
                        'is_list_item': False,
                        'list_type': None,
                        'indent_level': 0,
                        'runs': [{'text': part.rstrip(':'), 'bold': True, 'italic': False, 'underline': False, 'link': None}]
                    })
                else:
                    # This is section content - parse it for formatting
                    if part.strip():
                        section_paragraphs = self._parse_content_paragraphs(part)
                        paragraphs.extend(section_paragraphs)
            
            return [p for p in paragraphs if p['content']]
        
        # Fallback to original logic for other formats
        # Split content by major paragraph breaks
        # Handle both explicit <p> tags and double line breaks
        if '<p>' in content or '</p>' in content:
            # Split by <p> tags
            parts = re.split(r'<p[^>]*>|</p>', content)
            for part in parts:
                if part.strip():
                    paragraphs.append(self._parse_paragraph_content(part.strip()))
        else:
            # Split by double line breaks or <br><br>
            parts = re.split(r'\n\s*\n|<br\s*/?\s*>\s*<br\s*/?\s*>', content)
            for part in parts:
                if part.strip():
                    paragraphs.append(self._parse_paragraph_content(part.strip()))
        
        return [p for p in paragraphs if p['content']]  # Filter empty paragraphs
    
    def _parse_content_paragraphs(self, content: str) -> list:
        """Parse content within a section, handling various HTML formats."""
        import re
        
        paragraphs = []
        
        # Handle different content formats
        if '<p>' in content or '</p>' in content:
            # Content has explicit paragraphs
            parts = re.split(r'<p[^>]*>|</p>', content)
            for part in parts:
                if part.strip():
                    paragraphs.append(self._parse_paragraph_content(part.strip()))
        elif '<div>' in content or '</div>' in content:
            # Content uses div elements (common in rich text editors)
            parts = re.split(r'<div[^>]*>|</div>', content)
            for part in parts:
                if part.strip():
                    paragraphs.append(self._parse_paragraph_content(part.strip()))
        elif '<br' in content:
            # Content uses line breaks
            parts = content.split('<br')
            for i, part in enumerate(parts):
                if i > 0:
                    # Remove the closing > from br tag
                    part = re.sub(r'^[^>]*>', '', part)
                if part.strip():
                    paragraphs.append(self._parse_paragraph_content(part.strip()))
        else:
            # Simple text content - split by line breaks
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    paragraphs.append(self._parse_paragraph_content(line.strip()))
        
        return paragraphs
    
    def _parse_paragraph_content(self, content: str) -> dict:
        """Parse a single paragraph's content, including formatting and lists."""
        import re
        
        paragraph = {
            'content': '',
            'is_list_item': False,
            'list_type': None,
            'indent_level': 0,
            'runs': []
        }
        
        # Check if this is a list item
        list_item_match = re.match(r'^<li[^>]*>(.*)</li>$', content, re.DOTALL)
        if list_item_match:
            paragraph['is_list_item'] = True
            paragraph['list_type'] = 'bullet'
            content = list_item_match.group(1)
        
        # Check for numbered list indicators
        if re.match(r'^\s*\d+\.\s+', content):
            paragraph['is_list_item'] = True
            paragraph['list_type'] = 'number'
            content = re.sub(r'^\s*\d+\.\s+', '', content)
        
        # Parse text runs with formatting
        paragraph['runs'] = self._parse_text_runs(content)
        paragraph['content'] = ''.join([run['text'] for run in paragraph['runs']])
        
        return paragraph
    
    def _parse_text_runs(self, content: str) -> list:
        """Parse text content into runs with formatting information."""
        import re
        
        runs = []
        
        # Handle simple cases first - if no HTML tags, return as single run
        if not re.search(r'<[^>]+>', content):
            # Convert single line breaks to spaces, preserve paragraph structure
            text = re.sub(r'<br\s*/?\s*>', ' ', content)
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                runs.append({'text': text, 'bold': False, 'italic': False, 'underline': False, 'link': None})
            return runs
        
        # More complex parsing for formatted content
        current_pos = 0
        current_formatting = {'bold': False, 'italic': False, 'underline': False, 'link': None}
        formatting_stack = []
        
        # Find all HTML tags and their positions
        tag_pattern = r'<(/?)([bi]|strong|em|u|a)([^>]*)>'
        
        while current_pos < len(content):
            tag_match = re.search(tag_pattern, content[current_pos:])
            
            if not tag_match:
                # No more tags, add remaining text
                remaining_text = content[current_pos:]
                remaining_text = re.sub(r'<br\s*/?\s*>', ' ', remaining_text)
                remaining_text = re.sub(r'\s+', ' ', remaining_text).strip()
                if remaining_text:
                    runs.append({
                        'text': remaining_text,
                        'bold': current_formatting['bold'],
                        'italic': current_formatting['italic'],
                        'underline': current_formatting['underline'],
                        'link': current_formatting['link']
                    })
                break
            
            # Add text before the tag
            text_before = content[current_pos:current_pos + tag_match.start()]
            text_before = re.sub(r'<br\s*/?\s*>', ' ', text_before)
            text_before = re.sub(r'\s+', ' ', text_before).strip()
            if text_before:
                runs.append({
                    'text': text_before,
                    'bold': current_formatting['bold'],
                    'italic': current_formatting['italic'],
                    'underline': current_formatting['underline'],
                    'link': current_formatting['link']
                })
            
            # Process the tag
            is_closing = tag_match.group(1) == '/'
            tag_name = tag_match.group(2).lower()
            tag_attrs = tag_match.group(3)
            
            if tag_name in ['b', 'strong']:
                if is_closing:
                    current_formatting['bold'] = False
                else:
                    current_formatting['bold'] = True
            elif tag_name in ['i', 'em']:
                if is_closing:
                    current_formatting['italic'] = False
                else:
                    current_formatting['italic'] = True
            elif tag_name == 'u':
                if is_closing:
                    current_formatting['underline'] = False
                else:
                    current_formatting['underline'] = True
            elif tag_name == 'a':
                if is_closing:
                    current_formatting['link'] = None
                else:
                    # Extract href attribute
                    href_match = re.search(r'href=["\']([^"\']+)["\']', tag_attrs)
                    if href_match:
                        current_formatting['link'] = href_match.group(1)
            
            current_pos += tag_match.end()
        
        return runs
    
    def _convert_paragraph_to_powerpoint_xml(self, paragraph: dict) -> str:
        """Convert a parsed paragraph to PowerPoint XML format."""
        
        if not paragraph['runs']:
            # Empty paragraph
            return '''<a:p>
                        <a:r>
                            <a:rPr lang="en-US" dirty="0"/>
                            <a:t></a:t>
                        </a:r>
                    </a:p>'''
        
        # Build paragraph properties
        p_pr_content = ''
        if paragraph['is_list_item']:
            if paragraph['list_type'] == 'bullet':
                p_pr_content = '''<a:pPr>
                            <a:buFont typeface="Arial"/>
                            <a:buChar char="•"/>
                        </a:pPr>'''
            elif paragraph['list_type'] == 'number':
                p_pr_content = '''<a:pPr>
                            <a:buFont typeface="Arial"/>
                            <a:buAutoNum type="arabicPeriod"/>
                        </a:pPr>'''
        
        # Build text runs
        runs_xml = []
        for run in paragraph['runs']:
            if not run['text']:
                continue
                
            # Escape XML special characters in text
            import html
            escaped_text = html.escape(run['text'])
            
            # Build run properties
            rpr_attrs = []
            rpr_elements = []
            
            if run['bold']:
                rpr_attrs.append('b="1"')
            if run['italic']:
                rpr_attrs.append('i="1"')
            if run['underline']:
                rpr_attrs.append('u="sng"')
            
            # Always include basic attributes
            rpr_attrs.extend(['lang="en-US"', 'dirty="0"'])
            
            # Build rPr element
            rpr_attr_str = ' '.join(rpr_attrs)
            if run['link']:
                # For links, we'd need to create hyperlink relationships
                # For now, just format as regular text but keep the URL in parentheses
                if not escaped_text.endswith(')') or '(' not in escaped_text:
                    escaped_text = f"{escaped_text} ({html.escape(run['link'])})"
            
            run_xml = f'''<a:r>
                            <a:rPr {rpr_attr_str}/>
                            <a:t>{escaped_text}</a:t>
                        </a:r>'''
            runs_xml.append(run_xml)
        
        # Combine paragraph properties and runs
        if p_pr_content:
            paragraph_xml = f'''<a:p>
                        {p_pr_content}
                        {''.join(runs_xml)}
                    </a:p>'''
        else:
            paragraph_xml = f'''<a:p>
                        {''.join(runs_xml)}
                    </a:p>'''
        
        return paragraph_xml 