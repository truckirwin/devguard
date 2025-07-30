#!/usr/bin/env python3
"""
PowerPoint XML Analyzer - Diagnostic Tool
Extracts and analyzes speaker notes XML structures from real PowerPoint files
to understand formatting patterns and create robust parsing logic.
"""

import zipfile
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import re
import json
from pathlib import Path
import argparse

class PPTXMLAnalyzer:
    """Analyzes PowerPoint XML structure, specifically speaker notes."""
    
    # PowerPoint XML namespaces
    NAMESPACES = {
        'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    }
    
    def __init__(self):
        """Initialize the analyzer."""
        for prefix, uri in self.NAMESPACES.items():
            ET.register_namespace(prefix, uri)
    
    def analyze_pptx_speaker_notes(self, file_path: str) -> Dict[str, Any]:
        """Analyze speaker notes structure across all slides in a PPTX file."""
        
        analysis_result = {
            'file_path': file_path,
            'total_slides': 0,
            'slides_with_notes': 0,
            'slide_analyses': [],
            'formatting_patterns': {
                'bullet_types': set(),
                'special_characters': set(),
                'indentation_patterns': set(),
                'paragraph_structures': []
            }
        }
        
        with zipfile.ZipFile(file_path, 'r') as pptx_zip:
            # Get all slide files
            slide_files = [f for f in pptx_zip.namelist() 
                          if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
            
            analysis_result['total_slides'] = len(slide_files)
            
            # Sort by slide number
            slide_files.sort(key=lambda x: int(re.search(r'slide(\d+)\.xml', x).group(1)))
            
            for slide_file in slide_files:
                slide_number = int(re.search(r'slide(\d+)\.xml', slide_file).group(1))
                
                # Check for corresponding notes file
                notes_file = f'ppt/notesSlides/notesSlide{slide_number}.xml'
                
                if notes_file in pptx_zip.namelist():
                    analysis_result['slides_with_notes'] += 1
                    
                    # Analyze this slide's notes
                    slide_analysis = self._analyze_slide_notes(
                        pptx_zip, notes_file, slide_number
                    )
                    analysis_result['slide_analyses'].append(slide_analysis)
                    
                    # Collect formatting patterns
                    self._collect_formatting_patterns(
                        slide_analysis, analysis_result['formatting_patterns']
                    )
        
        # Convert sets to lists for JSON serialization
        analysis_result['formatting_patterns']['bullet_types'] = list(
            analysis_result['formatting_patterns']['bullet_types']
        )
        analysis_result['formatting_patterns']['special_characters'] = list(
            analysis_result['formatting_patterns']['special_characters']
        )
        analysis_result['formatting_patterns']['indentation_patterns'] = list(
            analysis_result['formatting_patterns']['indentation_patterns']
        )
        
        return analysis_result
    
    def _analyze_slide_notes(self, pptx_zip: zipfile.ZipFile, notes_file: str, slide_number: int) -> Dict[str, Any]:
        """Analyze speaker notes for a single slide."""
        
        slide_analysis = {
            'slide_number': slide_number,
            'notes_file': notes_file,
            'raw_xml_sample': '',
            'total_paragraphs': 0,
            'paragraphs': [],
            'raw_text_extraction': '',
            'formatted_text_extraction': '',
            'xml_structure_analysis': {}
        }
        
        try:
            # Read notes XML
            notes_xml = pptx_zip.read(notes_file).decode('utf-8')
            slide_analysis['raw_xml_sample'] = notes_xml[:1000] + '...' if len(notes_xml) > 1000 else notes_xml
            
            notes_root = ET.fromstring(notes_xml)
            
            # Find all paragraph elements
            paragraphs = notes_root.findall('.//a:p', self.NAMESPACES)
            slide_analysis['total_paragraphs'] = len(paragraphs)
            
            raw_texts = []
            formatted_texts = []
            
            for p_idx, paragraph in enumerate(paragraphs):
                paragraph_analysis = self._analyze_paragraph_structure(paragraph, p_idx)
                slide_analysis['paragraphs'].append(paragraph_analysis)
                
                if paragraph_analysis['text_content']:
                    raw_texts.append(paragraph_analysis['text_content'])
                    formatted_texts.append(paragraph_analysis['formatted_output'])
            
            slide_analysis['raw_text_extraction'] = '\n'.join(raw_texts)
            slide_analysis['formatted_text_extraction'] = '\n'.join(formatted_texts)
            
            # Analyze overall XML structure
            slide_analysis['xml_structure_analysis'] = self._analyze_xml_structure(notes_root)
            
        except Exception as e:
            slide_analysis['error'] = str(e)
        
        return slide_analysis
    
    def _analyze_paragraph_structure(self, paragraph: ET.Element, index: int) -> Dict[str, Any]:
        """Analyze the structure of a single paragraph element."""
        
        paragraph_analysis = {
            'paragraph_index': index,
            'raw_xml': ET.tostring(paragraph, encoding='unicode')[:500] + '...',
            'text_content': '',
            'formatting_properties': {},
            'bullet_info': {},
            'indentation_info': {},
            'run_properties': [],
            'formatted_output': '',
            'special_characters_found': []
        }
        
        # Extract text content
        text_elements = paragraph.findall('.//a:t', self.NAMESPACES)
        text_content = ''.join([elem.text or '' for elem in text_elements]).strip()
        paragraph_analysis['text_content'] = text_content
        
        if not text_content:
            return paragraph_analysis
        
        # Analyze paragraph properties
        p_pr = paragraph.find('.//a:pPr', self.NAMESPACES)
        if p_pr is not None:
            paragraph_analysis['formatting_properties'] = self._extract_paragraph_properties(p_pr)
        
        # Analyze bullet properties
        paragraph_analysis['bullet_info'] = self._extract_bullet_properties(paragraph)
        
        # Analyze indentation
        paragraph_analysis['indentation_info'] = self._extract_indentation_properties(paragraph)
        
        # Analyze run properties (text formatting within paragraph)
        runs = paragraph.findall('.//a:r', self.NAMESPACES)
        for run in runs:
            run_analysis = self._analyze_run_properties(run)
            if run_analysis:
                paragraph_analysis['run_properties'].append(run_analysis)
        
        # Find special characters
        special_chars = re.findall(r'[|~•·◦▪▫■□●○◆◇▲△▼▽★☆♦♠♣♥→←↑↓]', text_content)
        paragraph_analysis['special_characters_found'] = list(set(special_chars))
        
        # Generate formatted output
        paragraph_analysis['formatted_output'] = self._generate_formatted_output(paragraph_analysis)
        
        return paragraph_analysis
    
    def _extract_paragraph_properties(self, p_pr: ET.Element) -> Dict[str, Any]:
        """Extract paragraph-level properties."""
        
        properties = {}
        
        # Margin properties
        if 'marL' in p_pr.attrib:
            properties['margin_left'] = p_pr.attrib['marL']
        if 'marR' in p_pr.attrib:
            properties['margin_right'] = p_pr.attrib['marR']
        if 'indent' in p_pr.attrib:
            properties['indent'] = p_pr.attrib['indent']
        
        # Alignment
        if 'algn' in p_pr.attrib:
            properties['alignment'] = p_pr.attrib['algn']
        
        # Other properties
        for attr in p_pr.attrib:
            if attr not in properties:
                properties[attr] = p_pr.attrib[attr]
        
        return properties
    
    def _extract_bullet_properties(self, paragraph: ET.Element) -> Dict[str, Any]:
        """Extract bullet-related properties."""
        
        bullet_info = {
            'has_bullet': False,
            'bullet_type': None,
            'bullet_character': None,
            'bullet_font': None,
            'auto_numbering': False
        }
        
        # Check for custom bullet character
        bu_char = paragraph.find('.//a:buChar', self.NAMESPACES)
        if bu_char is not None:
            bullet_info['has_bullet'] = True
            bullet_info['bullet_type'] = 'custom_character'
            bullet_info['bullet_character'] = bu_char.get('char', '')
        
        # Check for bullet font
        bu_font = paragraph.find('.//a:buFont', self.NAMESPACES)
        if bu_font is not None:
            bullet_info['has_bullet'] = True
            bullet_info['bullet_font'] = bu_font.get('typeface', '')
            if bullet_info['bullet_type'] is None:
                bullet_info['bullet_type'] = 'font_bullet'
        
        # Check for auto numbering
        bu_auto_num = paragraph.find('.//a:buAutoNum', self.NAMESPACES)
        if bu_auto_num is not None:
            bullet_info['has_bullet'] = True
            bullet_info['auto_numbering'] = True
            bullet_info['bullet_type'] = 'auto_number'
        
        # Check for bullet size
        bu_sz_pct = paragraph.find('.//a:buSzPct', self.NAMESPACES)
        if bu_sz_pct is not None:
            bullet_info['has_bullet'] = True
            bullet_info['bullet_size_percent'] = bu_sz_pct.get('val', '')
        
        # Check for no bullet
        bu_none = paragraph.find('.//a:buNone', self.NAMESPACES)
        if bu_none is not None:
            bullet_info['bullet_type'] = 'none'
        
        return bullet_info
    
    def _extract_indentation_properties(self, paragraph: ET.Element) -> Dict[str, Any]:
        """Extract indentation-related properties."""
        
        indentation = {
            'left_margin_emu': 0,
            'left_margin_inches': 0.0,
            'indent_level': 0,
            'hanging_indent': False
        }
        
        p_pr = paragraph.find('.//a:pPr', self.NAMESPACES)
        if p_pr is not None:
            # Left margin
            if 'marL' in p_pr.attrib:
                margin_emu = int(p_pr.attrib['marL']) if p_pr.attrib['marL'].isdigit() else 0
                indentation['left_margin_emu'] = margin_emu
                indentation['left_margin_inches'] = round(margin_emu / 914400, 3)
                indentation['indent_level'] = margin_emu // 457200  # Approximate level
            
            # Hanging indent
            if 'indent' in p_pr.attrib:
                indent_val = int(p_pr.attrib['indent']) if p_pr.attrib['indent'].lstrip('-').isdigit() else 0
                if indent_val < 0:
                    indentation['hanging_indent'] = True
        
        return indentation
    
    def _analyze_run_properties(self, run: ET.Element) -> Optional[Dict[str, Any]]:
        """Analyze text run properties (formatting within paragraph)."""
        
        text_elem = run.find('.//a:t', self.NAMESPACES)
        if text_elem is None or not text_elem.text:
            return None
        
        run_analysis = {
            'text': text_elem.text,
            'formatting': {}
        }
        
        # Check for run properties
        r_pr = run.find('.//a:rPr', self.NAMESPACES)
        if r_pr is not None:
            # Bold
            if 'b' in r_pr.attrib:
                run_analysis['formatting']['bold'] = r_pr.attrib['b'] == '1'
            
            # Italic
            if 'i' in r_pr.attrib:
                run_analysis['formatting']['italic'] = r_pr.attrib['i'] == '1'
            
            # Underline
            if 'u' in r_pr.attrib:
                run_analysis['formatting']['underline'] = r_pr.attrib['u']
            
            # Font size
            if 'sz' in r_pr.attrib:
                run_analysis['formatting']['font_size'] = r_pr.attrib['sz']
        
        return run_analysis
    
    def _generate_formatted_output(self, paragraph_analysis: Dict[str, Any]) -> str:
        """Generate formatted output based on paragraph analysis."""
        
        text = paragraph_analysis['text_content']
        if not text:
            return ''
        
        # Start with indentation
        indent = ''
        indent_info = paragraph_analysis['indentation_info']
        if indent_info['indent_level'] > 0:
            indent = '  ' * indent_info['indent_level']
        
        # Add bullet if present
        bullet = ''
        bullet_info = paragraph_analysis['bullet_info']
        
        if bullet_info['has_bullet']:
            if bullet_info['bullet_character']:
                bullet = bullet_info['bullet_character'] + ' '
            elif bullet_info['auto_numbering']:
                bullet = '1. '  # Simplified
            elif bullet_info['bullet_type'] in ['font_bullet', None]:
                bullet = '• '
        
        return f"{indent}{bullet}{text}"
    
    def _analyze_xml_structure(self, notes_root: ET.Element) -> Dict[str, Any]:
        """Analyze overall XML structure of notes."""
        
        structure = {
            'root_tag': notes_root.tag,
            'namespaces_used': [],
            'shape_count': 0,
            'text_body_count': 0,
            'paragraph_count': 0,
            'run_count': 0
        }
        
        # Count different elements
        for elem in notes_root.iter():
            if 'sp' in elem.tag:
                structure['shape_count'] += 1
            elif 'txBody' in elem.tag:
                structure['text_body_count'] += 1
            elif elem.tag.endswith('}p'):
                structure['paragraph_count'] += 1
            elif elem.tag.endswith('}r'):
                structure['run_count'] += 1
        
        # Extract namespace information
        for elem in notes_root.iter():
            if '}' in elem.tag:
                namespace = elem.tag.split('}')[0] + '}'
                if namespace not in structure['namespaces_used']:
                    structure['namespaces_used'].append(namespace)
        
        return structure
    
    def _collect_formatting_patterns(self, slide_analysis: Dict[str, Any], patterns: Dict[str, Any]):
        """Collect formatting patterns from slide analysis."""
        
        for paragraph in slide_analysis['paragraphs']:
            # Collect bullet types
            bullet_info = paragraph.get('bullet_info', {})
            if bullet_info.get('bullet_type'):
                patterns['bullet_types'].add(bullet_info['bullet_type'])
            
            # Collect special characters
            for char in paragraph.get('special_characters_found', []):
                patterns['special_characters'].add(char)
            
            # Collect indentation patterns
            indent_info = paragraph.get('indentation_info', {})
            if indent_info.get('indent_level', 0) > 0:
                patterns['indentation_patterns'].add(indent_info['indent_level'])
            
            # Collect paragraph structures
            structure = {
                'has_bullet': bullet_info.get('has_bullet', False),
                'bullet_type': bullet_info.get('bullet_type'),
                'indent_level': indent_info.get('indent_level', 0),
                'has_special_chars': len(paragraph.get('special_characters_found', [])) > 0
            }
            patterns['paragraph_structures'].append(structure)
    
    def generate_analysis_report(self, analysis_result: Dict[str, Any]) -> str:
        """Generate a human-readable analysis report."""
        
        report = []
        report.append("="*80)
        report.append("POWERPOINT SPEAKER NOTES XML ANALYSIS REPORT")
        report.append("="*80)
        report.append("")
        
        # File summary
        report.append(f"File: {analysis_result['file_path']}")
        report.append(f"Total Slides: {analysis_result['total_slides']}")
        report.append(f"Slides with Notes: {analysis_result['slides_with_notes']}")
        report.append("")
        
        # Formatting patterns summary
        patterns = analysis_result['formatting_patterns']
        report.append("FORMATTING PATTERNS FOUND:")
        report.append("-" * 40)
        report.append(f"Bullet Types: {', '.join(patterns['bullet_types'])}")
        report.append(f"Special Characters: {', '.join(patterns['special_characters'])}")
        report.append(f"Indentation Levels: {', '.join(map(str, patterns['indentation_patterns']))}")
        report.append("")
        
        # Per-slide analysis
        for slide in analysis_result['slide_analyses']:
            report.append(f"SLIDE {slide['slide_number']} ANALYSIS:")
            report.append("-" * 30)
            report.append(f"Paragraphs: {slide['total_paragraphs']}")
            
            if 'error' in slide:
                report.append(f"ERROR: {slide['error']}")
                report.append("")
                continue
            
            report.append("")
            report.append("Raw Text:")
            report.append(slide['raw_text_extraction'][:500] + ('...' if len(slide['raw_text_extraction']) > 500 else ''))
            report.append("")
            report.append("Formatted Text:")
            report.append(slide['formatted_text_extraction'][:500] + ('...' if len(slide['formatted_text_extraction']) > 500 else ''))
            report.append("")
            
            # Show first few paragraphs in detail
            for i, para in enumerate(slide['paragraphs'][:3]):  # First 3 paragraphs
                if para['text_content']:
                    report.append(f"  Paragraph {i+1}:")
                    report.append(f"    Text: {para['text_content'][:100]}")
                    report.append(f"    Bullet: {para['bullet_info']['bullet_type']} ({para['bullet_info']['bullet_character']})")
                    report.append(f"    Indent: Level {para['indentation_info']['indent_level']}")
                    report.append(f"    Formatted: {para['formatted_output']}")
                    report.append("")
            
            report.append("")
        
        return '\n'.join(report)


def main():
    """Main function for command-line usage."""
    
    parser = argparse.ArgumentParser(description="Analyze PowerPoint XML structure for speaker notes")
    parser.add_argument("pptx_file", help="Path to the PowerPoint file to analyze")
    parser.add_argument("--output", "-o", help="Output file for analysis report")
    parser.add_argument("--json", "-j", help="Output raw analysis as JSON file")
    
    args = parser.parse_args()
    
    if not Path(args.pptx_file).exists():
        print(f"Error: File '{args.pptx_file}' not found")
        return 1
    
    # Run analysis
    analyzer = PPTXMLAnalyzer()
    print(f"Analyzing {args.pptx_file}...")
    
    try:
        analysis_result = analyzer.analyze_pptx_speaker_notes(args.pptx_file)
        
        # Generate report
        report = analyzer.generate_analysis_report(analysis_result)
        
        # Output report
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Analysis report saved to: {args.output}")
        else:
            print(report)
        
        # Output JSON if requested
        if args.json:
            with open(args.json, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, indent=2, ensure_ascii=False)
            print(f"Raw analysis data saved to: {args.json}")
        
        return 0
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return 1


if __name__ == "__main__":
    exit(main()) 