"""
Enhanced Speaker Notes Parser

Based on XML analysis of real PowerPoint files, this parser handles various
formatting patterns and special characters used in speaker notes to provide
consistent, properly formatted text output.
"""

import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ParsedNotesSection:
    """Represents a parsed section of speaker notes."""
    section_type: str  # 'instructor', 'student', 'developer', 'alt_text', 'general'
    title: str
    content: str
    original_content: str
    formatting_info: Dict[str, Any]

@dataclass
class ParsedParagraph:
    """Represents a parsed paragraph with formatting."""
    text: str
    bullet_type: Optional[str]
    bullet_character: Optional[str]
    indent_level: int
    is_section_header: bool
    section_type: Optional[str]

class EnhancedSpeakerNotesParser:
    """Enhanced parser for PowerPoint speaker notes with robust formatting handling."""
    
    # PowerPoint XML namespaces
    NAMESPACES = {
        'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    }
    
    # Section patterns based on XML analysis
    SECTION_PATTERNS = {
        'instructor': [
            r'^[\|]*\s*INSTRUCTOR\s+NOTES?\s*:?\s*[\|]*',
            r'^[\|]*\s*TEACHER\s+NOTES?\s*:?\s*[\|]*',
            r'^[\|]*\s*FACILITATOR\s+NOTES?\s*:?\s*[\|]*',
        ],
        'student': [
            r'^[\|]*\s*STUDENT\s+NOTES?\s*:?\s*[\|]*',
            r'^[\|]*\s*LEARNER\s+NOTES?\s*:?\s*[\|]*',
            r'^[\|]*\s*PARTICIPANT\s+NOTES?\s*:?\s*[\|]*',
        ],
        'developer': [
            r'^[\~]*\s*DEVELOPER\s+NOTES?\s*:?\s*[\~]*',
            r'^[\~]*\s*DEV\s+NOTES?\s*:?\s*[\~]*',
            r'^[\~]*\s*TECHNICAL\s+NOTES?\s*:?\s*[\~]*',
        ],
        'alt_text': [
            r'^[\~]*\s*ALT\s+TEXT\s*:?\s*[\~]*',
            r'^[\~]*\s*ALTERNATIVE\s+TEXT\s*:?\s*[\~]*',
            r'^[\~]*\s*IMAGE\s+DESCRIPTION\s*:?\s*[\~]*',
            r'^[\~]*\s*ACCESSIBILITY\s+TEXT\s*:?\s*[\~]*',
        ]
    }
    
    # Special characters that indicate structure
    STRUCTURE_CHARS = ['|', '~', '•', '◦', '▪', '▫']
    
    def __init__(self):
        """Initialize the enhanced parser."""
        for prefix, uri in self.NAMESPACES.items():
            ET.register_namespace(prefix, uri)
    
    def parse_speaker_notes_xml(self, xml_content: str) -> List[ParsedNotesSection]:
        """Parse speaker notes XML and return structured sections."""
        
        try:
            # Try to extract raw text directly from the notes slide if possible
            # This preserves \x0b characters that get lost in XML parsing
            try:
                from pptx import Presentation
                import io
                
                # Create a temporary file-like object from the XML content
                # This is a bit of a hack, but we need the raw text with \x0b preserved
                # For now, let's use a simpler approach and extract from XML but handle \x0b differently
                pass
            except:
                pass
            
            root = ET.fromstring(xml_content)
            paragraphs = root.findall('.//a:p', self.NAMESPACES)
            
            # Extract all text content, preserving line breaks
            all_text_parts = []
            for paragraph in paragraphs:
                text_elements = paragraph.findall('.//a:t', self.NAMESPACES)
                para_text = ''.join([elem.text or '' for elem in text_elements]).strip()
                if para_text:
                    all_text_parts.append(para_text)
            
            # Join all text and then split properly
            full_text = '\n'.join(all_text_parts)
            
            # Now split by both \x0b and \n to get all logical lines
            all_logical_lines = []
            
            # First split by newlines to get paragraphs
            paragraphs_text = full_text.split('\n')
            
            for para_text in paragraphs_text:
                if para_text.strip():
                    # Then split each paragraph by \x0b (vertical tab)
                    logical_lines = para_text.split('\x0b')
                    for line in logical_lines:
                        line = line.strip()
                        if line:
                            all_logical_lines.append(line)
            
            # Second pass: group logical lines into sections
            sections = self._group_lines_into_sections(all_logical_lines)
            
            # Third pass: clean and format sections
            formatted_sections = self._format_sections(sections)
            
            return formatted_sections
            
        except Exception as e:
            print(f"Error parsing speaker notes XML: {e}")
            # Fallback to simple text extraction
            return self._fallback_text_extraction(xml_content)
    
    def parse_speaker_notes_text(self, raw_text: str) -> List[ParsedNotesSection]:
        """Parse speaker notes from raw text content (preserves \x0b characters)."""
        
        if not raw_text or not raw_text.strip():
            return []
        
        try:
            # Split by both \x0b and \n to get all logical lines
            all_logical_lines = []
            
            # First split by newlines to get paragraphs
            paragraphs_text = raw_text.split('\n')
            
            for para_text in paragraphs_text:
                if para_text.strip():
                    # Then split each paragraph by \x0b (vertical tab)
                    logical_lines = para_text.split('\x0b')
                    for line in logical_lines:
                        line = line.strip()
                        if line:
                            all_logical_lines.append(line)
            
            # Group logical lines into sections
            sections = self._group_lines_into_sections(all_logical_lines)
            
            # Clean and format sections
            formatted_sections = self._format_sections(sections)
            
            return formatted_sections
            
        except Exception as e:
            print(f"Error parsing speaker notes text: {e}")
            return []
    
    def _parse_paragraph_structure(self, paragraph: ET.Element) -> List[ParsedParagraph]:
        """Parse a single paragraph element and extract structure.
        
        Returns a list because PowerPoint may use \x0b (vertical tab) to separate
        logical lines that should be treated as separate paragraphs.
        """
        
        # Extract text content
        text_elements = paragraph.findall('.//a:t', self.NAMESPACES)
        text_content = ''.join([elem.text or '' for elem in text_elements]).strip()
        
        if not text_content:
            return []
        
        # Analyze paragraph properties
        p_pr = paragraph.find('.//a:pPr', self.NAMESPACES)
        
        # Extract bullet information
        bullet_type, bullet_char = self._extract_bullet_info(paragraph)
        
        # Extract indentation
        indent_level = self._extract_indent_level(p_pr)
        
        # Split on vertical tab characters (\x0b) - PowerPoint uses these as line separators
        logical_lines = text_content.split('\x0b')
        
        parsed_paragraphs = []
        
        for line in logical_lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            is_section_header, section_type = self._identify_section_header(line)
            
            parsed_paragraphs.append(ParsedParagraph(
                text=line,
                bullet_type=bullet_type,
                bullet_character=bullet_char,
                indent_level=indent_level,
                is_section_header=is_section_header,
                section_type=section_type
            ))
        
        return parsed_paragraphs
    
    def _extract_bullet_info(self, paragraph: ET.Element) -> Tuple[Optional[str], Optional[str]]:
        """Extract bullet type and character from paragraph."""
        
        # Check for custom bullet character
        bu_char = paragraph.find('.//a:buChar', self.NAMESPACES)
        if bu_char is not None:
            return 'custom', bu_char.get('char', '•')
        
        # Check for auto numbering
        bu_auto_num = paragraph.find('.//a:buAutoNum', self.NAMESPACES)
        if bu_auto_num is not None:
            return 'numbered', None
        
        # Check for bullet font (indicates default bullet)
        bu_font = paragraph.find('.//a:buFont', self.NAMESPACES)
        bu_sz_pct = paragraph.find('.//a:buSzPct', self.NAMESPACES)
        if bu_font is not None or bu_sz_pct is not None:
            return 'default', '•'
        
        # Check for no bullet
        bu_none = paragraph.find('.//a:buNone', self.NAMESPACES)
        if bu_none is not None:
            return 'none', None
        
        return None, None
    
    def _extract_indent_level(self, p_pr: Optional[ET.Element]) -> int:
        """Extract indentation level from paragraph properties."""
        
        if p_pr is None:
            return 0
        
        if 'marL' in p_pr.attrib:
            try:
                margin_emu = int(p_pr.attrib['marL'])
                # Convert EMU to indent levels (approximately 457200 EMU per level)
                return max(0, margin_emu // 457200)
            except ValueError:
                return 0
        
        return 0
    
    def _identify_section_header(self, text: str) -> Tuple[bool, Optional[str]]:
        """Identify if text is a section header and determine section type.
        
        Only considers text up to the first vertical tab (\x0b) or line break,
        since PowerPoint may pack multiple logical lines into one paragraph.
        """
        
        # Take only the first logical line for header detection
        first_line = text.split('\x0b')[0].split('\n')[0].strip()
        text_upper = first_line.upper().strip()
        
        for section_type, patterns in self.SECTION_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, text_upper, re.IGNORECASE):
                    return True, section_type
        
        return False, None
    
    def _group_lines_into_sections(self, lines: List[str]) -> List[ParsedNotesSection]:
        """Group logical lines into sections based on section headers."""
        
        sections = []
        current_section_type = 'general'
        current_section_title = ''
        current_content_lines = []
        
        for line in lines:
            # Check if this line is a section header
            is_header, section_type = self._identify_section_header(line)
            
            if is_header and section_type:
                # Save previous section if it has content
                if current_content_lines:
                    sections.append(self._create_section_from_lines(
                        current_section_type, current_section_title, current_content_lines
                    ))
                
                # Start new section
                current_section_type = section_type
                current_section_title = line
                current_content_lines = []
            else:
                # Add to current section content
                current_content_lines.append(line)
        
        # Add final section
        if current_content_lines or current_section_title:
            sections.append(self._create_section_from_lines(
                current_section_type, current_section_title, current_content_lines
            ))
        
        return sections
    
    def _create_section_from_lines(self, section_type: str, title: str, content_lines: List[str]) -> ParsedNotesSection:
        """Create a ParsedNotesSection from content lines."""
        
        content = '\n'.join(content_lines)
        original_content = content
        
        # Extract formatting info
        formatting_info = {
            'has_bullets': any(line.strip().startswith(('•', '-', '*')) for line in content_lines),
            'max_indent_level': 0,
            'paragraph_count': len(content_lines)
        }
        
        return ParsedNotesSection(
            section_type=section_type,
            title=title,
            content=content,
            original_content=original_content,
            formatting_info=formatting_info
        )
    
    def _create_section(self, section_type: str, title: str, paragraphs: List[ParsedParagraph]) -> ParsedNotesSection:
        """Create a ParsedNotesSection from paragraphs."""
        
        # Format content based on paragraph structure
        formatted_lines = []
        
        for para in paragraphs:
            formatted_line = self._format_paragraph_text(para)
            if formatted_line:
                formatted_lines.append(formatted_line)
        
        content = '\n'.join(formatted_lines)
        original_content = '\n'.join([para.text for para in paragraphs])
        
        # Extract formatting info
        formatting_info = {
            'has_bullets': any(para.bullet_type for para in paragraphs),
            'max_indent_level': max([para.indent_level for para in paragraphs] + [0]),
            'paragraph_count': len(paragraphs)
        }
        
        return ParsedNotesSection(
            section_type=section_type,
            title=title,
            content=content,
            original_content=original_content,
            formatting_info=formatting_info
        )
    
    def _format_paragraph_text(self, para: ParsedParagraph) -> str:
        """Format a paragraph according to its structure."""
        
        text = para.text
        
        # Remove leading structure characters that are not meaningful
        text = self._clean_structure_characters(text)
        
        if not text.strip():
            return ''
        
        # Add indentation
        indent = '  ' * para.indent_level
        
        # Add bullet if present
        bullet_prefix = ''
        if para.bullet_type == 'custom' and para.bullet_character:
            bullet_prefix = f"{para.bullet_character} "
        elif para.bullet_type == 'numbered':
            bullet_prefix = "1. "  # Simplified numbering
        elif para.bullet_type == 'default':
            bullet_prefix = "• "
        
        return f"{indent}{bullet_prefix}{text}"
    
    def _clean_structure_characters(self, text: str) -> str:
        """Clean up structural characters while preserving meaningful content."""
        
        # Remove leading structure chars that are just formatting
        text = re.sub(r'^[\|\~\•\◦\▪\▫\-]+\s*', '', text)
        
        # Handle cases where structure chars separate content
        # e.g., "|INSTRUCTOR NOTES:|Some content" -> "Some content"
        for section_type, patterns in self.SECTION_PATTERNS.items():
            for pattern in patterns:
                # Remove section header patterns from content
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up multiple consecutive structure characters
        text = re.sub(r'[\|\~]{2,}', '|', text)
        
        # DO NOT remove "- |" patterns as these are valid instructor notes formatting
        # text = re.sub(r'\s*-\s*\|\s*', ' ', text)  # REMOVED - this was destroying instructor notes
        
        # Handle special cases where | separates different content types
        # e.g., "content1||content2" should become separate lines
        if '||' in text:
            parts = text.split('||')
            text = '\n'.join([part.strip() for part in parts if part.strip()])
        
        return text.strip()
    
    def _format_sections(self, sections: List[ParsedNotesSection]) -> List[ParsedNotesSection]:
        """Apply final formatting to sections."""
        
        formatted_sections = []
        
        for section in sections:
            # Apply section-specific formatting
            if section.section_type == 'instructor':
                content = self._format_instructor_notes(section.content)
            elif section.section_type == 'student':
                content = self._format_student_notes(section.content)
            elif section.section_type == 'developer':
                content = self._format_developer_notes(section.content)
            elif section.section_type == 'alt_text':
                content = self._format_alt_text(section.content)
            else:
                content = self._format_general_notes(section.content)
            
            formatted_section = ParsedNotesSection(
                section_type=section.section_type,
                title=section.title,
                content=content,
                original_content=section.original_content,
                formatting_info=section.formatting_info
            )
            
            formatted_sections.append(formatted_section)
        
        return formatted_sections
    
    def _format_instructor_notes(self, content: str) -> str:
        """Format instructor notes with proper structure matching PowerPoint format."""
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Format as: dash + space + | + text (matching PowerPoint exactly)
                # Remove any existing bullets or | characters first, but preserve the content
                clean_line = re.sub(r'^[•\-\|]+\s*', '', line)
                if clean_line:  # Only add non-empty lines
                    formatted_lines.append(f"- |{clean_line}")
        
        # Add empty line with | for spacing
        formatted_lines.append('|')
        return '\n'.join(formatted_lines)
    
    def _format_student_notes(self, content: str) -> str:
        """Format student notes as readable paragraphs with NO prefixes."""
        # Student notes are typically longer form content and should be plain text
        lines = content.split('\n')
        formatted_lines = []
        
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            
            # Remove any bullet characters from student notes (make completely plain text)
            line = re.sub(r'^[\•\-\*]+\s*', '', line)
            
            if line:
                # Check if this looks like a sentence ending (for paragraph breaks)
                if current_paragraph and (line[0].isupper() and 
                    current_paragraph[-1].endswith(('.', '!', '?'))):
                    # Start new paragraph
                    formatted_lines.append(' '.join(current_paragraph))
                    current_paragraph = [line]
                else:
                    current_paragraph.append(line)
            else:
                # Empty line - end current paragraph
                if current_paragraph:
                    formatted_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
        
        # Add final paragraph
        if current_paragraph:
            formatted_lines.append(' '.join(current_paragraph))
        
        # Student notes should be plain text with NO special character prefixes
        return '\n\n'.join(formatted_lines).strip()
    
    def _format_developer_notes(self, content: str) -> str:
        """Format developer notes with ~ prefix matching PowerPoint format."""
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Ensure ~ prefix for all developer notes lines
                if not line.startswith('~'):
                    formatted_lines.append(f"~{line}")
                else:
                    formatted_lines.append(line)
        
        # Add empty line with ~ for spacing
        formatted_lines.append('~')
        return '\n'.join(formatted_lines)
    
    def _format_alt_text(self, content: str) -> str:
        """Format alt text descriptions matching screenshot format."""
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Preserve tilde prefix and format properly
                if line.lower().startswith('no images') or line.lower().startswith('no image'):
                    formatted_lines.append(f"~{line}")
                elif line.startswith('~'):
                    formatted_lines.append(line)  # Already has tilde
                else:
                    formatted_lines.append(f"~{line}")
        
        # Add empty line with ~ for spacing
        formatted_lines.append('~')
        return '\n'.join(formatted_lines)
    
    def _format_general_notes(self, content: str) -> str:
        """Format general notes."""
        return content.strip()
    
    def _fallback_text_extraction(self, xml_content: str) -> List[ParsedNotesSection]:
        """Fallback method for simple text extraction."""
        
        # Simple regex-based extraction
        text_matches = re.findall(r'<a:t>([^<]*)</a:t>', xml_content)
        text_content = ' '.join([match.strip() for match in text_matches if match.strip()])
        
        return [ParsedNotesSection(
            section_type='general',
            title='Speaker Notes',
            content=text_content,
            original_content=text_content,
            formatting_info={'fallback': True}
        )]
    
    def format_for_display(self, sections: List[ParsedNotesSection], style: str = 'combined') -> str:
        """Format parsed sections for display in the UI matching screenshot format."""
        
        if style == 'combined':
            # Combine all sections into a single formatted text
            formatted_parts = []
            
            for section in sections:
                if section.content.strip():
                    # Add section header with proper special characters
                    header = self._format_section_header(section.section_type, section.title)
                    formatted_parts.append(header)
                    
                    formatted_parts.append(section.content)
            
            return '\n'.join(formatted_parts).strip()
        
        elif style == 'sections':
            # Return sections as structured data
            return {
                section.section_type: {
                    'title': section.title,
                    'content': section.content
                }
                for section in sections
            }
        
        else:
            # Default to combined
            return self.format_for_display(sections, 'combined')
    
    def _format_section_header(self, section_type: str, title: str) -> str:
        """Format section headers for display matching screenshot format."""
        
        # Preserve original special characters from the PowerPoint
        type_labels = {
            'instructor': '|INSTRUCTOR NOTES:',
            'student': '|STUDENT NOTES:',
            'developer': '~Developer Notes:',
            'alt_text': '~Alt text:',
            'general': 'NOTES:'
        }
        
        label = type_labels.get(section_type, 'NOTES:')
        return label 