"""
Comprehensive PowerPoint Analyzer

This module provides in-depth analysis of PowerPoint presentations including:
- Content analysis (text, images, layouts)
- Accessibility assessment
- Design quality metrics
- Performance analysis
- Reading order and tab order
- Visual design consistency
"""

import zipfile
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import re
import json
import logging
import os
from PIL import Image
import io
import statistics

from .tab_order_analyzer import PowerPointTabOrderAnalyzer, TabOrderAnalysis

logger = logging.getLogger(__name__)

@dataclass
class SlideAnalysis:
    """Comprehensive analysis of a single slide."""
    
    slide_number: int
    
    # Content metrics
    text_words: int = 0
    text_characters: int = 0
    text_complexity_score: float = 0.0
    
    # Object counts
    total_objects: int = 0
    text_objects: int = 0
    image_objects: int = 0
    shape_objects: int = 0
    table_objects: int = 0
    chart_objects: int = 0
    
    # Layout analysis
    layout_type: str = ""
    layout_consistency_score: float = 0.0
    
    # Accessibility
    accessibility_score: float = 0.0
    missing_alt_text_count: int = 0
    color_contrast_issues: int = 0
    reading_order_issues: List[str] = None
    
    # Visual design
    color_usage: Dict[str, int] = None
    font_usage: List[str] = None
    design_consistency_score: float = 0.0
    
    # Performance
    estimated_load_time: float = 0.0
    complexity_score: float = 0.0
    
    # Tab order analysis (from existing analyzer)
    tab_order_analysis: Dict[str, Any] = None


@dataclass
class PPTAnalysisResult:
    """Complete analysis result for a PowerPoint presentation."""
    
    filename: str
    file_size_mb: float
    
    # Overall metrics
    total_slides: int
    total_objects: int
    slides_with_tab_order: int = 0
    slides_with_accessibility: int = 0
    total_issues: int = 0
    
    # File metadata
    slide_dimensions: str = ""
    has_animations: bool = False
    has_transitions: bool = False
    has_embedded_media: bool = False
    
    # Content analysis
    slide_layouts_used: List[str] = None
    theme_name: str = ""
    color_scheme: Dict[str, Any] = None
    font_usage: List[str] = None
    
    # Accessibility metrics
    accessibility_score: float = 0.0
    missing_alt_text_count: int = 0
    color_contrast_issues: int = 0
    reading_order_issues: int = 0
    
    # Quality metrics
    image_quality_score: float = 0.0
    text_readability_score: float = 0.0
    design_consistency_score: float = 0.0
    
    # Performance metrics
    estimated_load_time: float = 0.0
    complexity_score: float = 0.0
    
    # Detailed per-slide analysis
    slide_analyses: List[SlideAnalysis] = None
    
    # Recommendations
    recommendations: List[str] = None


class ComprehensivePPTAnalyzer:
    """Comprehensive PowerPoint presentation analyzer."""
    
    # PowerPoint XML namespaces
    NAMESPACES = {
        'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
        'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
        'p14': 'http://schemas.microsoft.com/office/powerpoint/2010/main',
        'p15': 'http://schemas.microsoft.com/office/powerpoint/2013/main',
        'p16': 'http://schemas.microsoft.com/office/powerpoint/2016/main',
        'p188': 'http://schemas.microsoft.com/office/powerpoint/2018/8/main',
    }
    
    def __init__(self):
        """Initialize the comprehensive analyzer."""
        for prefix, uri in self.NAMESPACES.items():
            ET.register_namespace(prefix, uri)
        
        self.tab_analyzer = PowerPointTabOrderAnalyzer()
    
    def analyze_file(self, file_path: str) -> PPTAnalysisResult:
        """
        Perform comprehensive analysis of a PowerPoint file.
        
        Args:
            file_path: Path to the PPTX file
            
        Returns:
            Complete analysis result
        """
        try:
            with zipfile.ZipFile(file_path, 'r') as pptx_zip:
                return self._analyze_presentation(pptx_zip, file_path)
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            raise
    
    def _analyze_presentation(self, pptx_zip: zipfile.ZipFile, file_path: str) -> PPTAnalysisResult:
        """Perform comprehensive analysis of the presentation."""
        
        filename = Path(file_path).name
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        # Initialize result
        result = PPTAnalysisResult(
            filename=filename,
            file_size_mb=file_size_mb,
            total_slides=0,
            total_objects=0,
            slide_analyses=[],
            recommendations=[],
            slide_layouts_used=[],
            font_usage=[],
            color_scheme={}
        )
        
        # Get presentation metadata
        self._analyze_presentation_metadata(pptx_zip, result)
        
        # Get all slide XML files
        slide_files = [f for f in pptx_zip.namelist() 
                      if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
        
        # Sort by slide number
        slide_files.sort(key=lambda x: int(re.search(r'slide(\d+)\.xml', x).group(1)))
        
        result.total_slides = len(slide_files)
        
        # Analyze each slide
        all_colors = []
        all_fonts = []
        
        for slide_file in slide_files:
            slide_number = int(re.search(r'slide(\d+)\.xml', slide_file).group(1))
            
            # Read slide XML
            with pptx_zip.open(slide_file) as f:
                slide_xml = f.read().decode('utf-8')
            
            # Analyze this slide
            slide_analysis = self._analyze_slide(slide_xml, slide_number, pptx_zip)
            result.slide_analyses.append(slide_analysis)
            
            # Aggregate metrics
            result.total_objects += slide_analysis.total_objects
            if slide_analysis.tab_order_analysis and slide_analysis.tab_order_analysis.get('has_explicit_tab_order'):
                result.slides_with_tab_order += 1
            if slide_analysis.accessibility_score > 70:
                result.slides_with_accessibility += 1
            if slide_analysis.reading_order_issues:
                result.total_issues += len(slide_analysis.reading_order_issues)
            
            result.missing_alt_text_count += slide_analysis.missing_alt_text_count
            result.color_contrast_issues += slide_analysis.color_contrast_issues
            result.reading_order_issues += len(slide_analysis.reading_order_issues or [])
            
            # Collect colors and fonts
            if slide_analysis.color_usage:
                all_colors.extend(slide_analysis.color_usage.keys())
            if slide_analysis.font_usage:
                all_fonts.extend(slide_analysis.font_usage)
        
        # Calculate overall metrics
        result.font_usage = list(set(all_fonts))
        result.color_scheme = self._analyze_color_scheme(all_colors)
        
        # Calculate scores
        result.accessibility_score = self._calculate_accessibility_score(result)
        result.text_readability_score = self._calculate_readability_score(result)
        result.design_consistency_score = self._calculate_design_consistency_score(result)
        result.image_quality_score = self._calculate_image_quality_score(result)
        result.estimated_load_time = self._estimate_load_time(result)
        result.complexity_score = self._calculate_complexity_score(result)
        
        # Generate recommendations
        result.recommendations = self._generate_recommendations(result)
        
        return result
    
    def _analyze_presentation_metadata(self, pptx_zip: zipfile.ZipFile, result: PPTAnalysisResult):
        """Analyze presentation-level metadata."""
        
        try:
            # Check for presentation.xml
            if 'ppt/presentation.xml' in pptx_zip.namelist():
                with pptx_zip.open('ppt/presentation.xml') as f:
                    pres_xml = f.read().decode('utf-8')
                    pres_root = ET.fromstring(pres_xml)
                    
                    # Check for slide size
                    slide_size = pres_root.find('.//p:sldSz', self.NAMESPACES)
                    if slide_size is not None:
                        cx = slide_size.get('cx', '0')
                        cy = slide_size.get('cy', '0')
                        # Convert EMU to standard ratios
                        if cx and cy:
                            ratio = float(cx) / float(cy)
                            if abs(ratio - 16/9) < 0.1:
                                result.slide_dimensions = "16:9"
                            elif abs(ratio - 4/3) < 0.1:
                                result.slide_dimensions = "4:3"
                            else:
                                result.slide_dimensions = f"{ratio:.2f}:1"
        
        except Exception as e:
            logger.warning(f"Could not analyze presentation metadata: {e}")
        
        # Check for embedded media
        media_files = [f for f in pptx_zip.namelist() if f.startswith('ppt/media/')]
        result.has_embedded_media = len(media_files) > 0
        
        # Check for themes
        theme_files = [f for f in pptx_zip.namelist() if f.startswith('ppt/theme/')]
        if theme_files:
            try:
                with pptx_zip.open(theme_files[0]) as f:
                    theme_xml = f.read().decode('utf-8')
                    theme_root = ET.fromstring(theme_xml)
                    theme_name_elem = theme_root.find('.//a:theme', self.NAMESPACES)
                    if theme_name_elem is not None:
                        result.theme_name = theme_name_elem.get('name', 'Unknown')
            except Exception:
                pass
    
    def _analyze_slide(self, slide_xml: str, slide_number: int, 
                      pptx_zip: zipfile.ZipFile) -> SlideAnalysis:
        """Analyze a single slide comprehensively."""
        
        # Parse XML
        root = ET.fromstring(slide_xml)
        
        # Initialize slide analysis
        analysis = SlideAnalysis(
            slide_number=slide_number,
            reading_order_issues=[],
            color_usage={},
            font_usage=[]
        )
        
        # Get tab order analysis
        try:
            tab_analyses = self.tab_analyzer._analyze_slide(slide_xml, slide_number, pptx_zip)
            analysis.tab_order_analysis = {
                'total_objects': tab_analyses.total_objects,
                'has_explicit_tab_order': tab_analyses.has_explicit_tab_order,
                'has_accessibility_info': tab_analyses.has_accessibility_info,
                'reading_order_issues': tab_analyses.reading_order_issues or [],
                'all_objects': [asdict(obj) for obj in tab_analyses.all_objects]
            }
            analysis.total_objects = tab_analyses.total_objects
            analysis.reading_order_issues = tab_analyses.reading_order_issues or []
        except Exception as e:
            logger.warning(f"Could not get tab order analysis for slide {slide_number}: {e}")
        
        # Analyze content
        self._analyze_slide_content(root, analysis)
        
        # Analyze layout
        self._analyze_slide_layout(root, analysis)
        
        # Analyze accessibility
        self._analyze_slide_accessibility(root, analysis)
        
        # Analyze visual design
        self._analyze_slide_design(root, analysis)
        
        # Calculate slide-level scores
        analysis.accessibility_score = self._calculate_slide_accessibility_score(analysis)
        analysis.design_consistency_score = self._calculate_slide_design_score(analysis)
        analysis.complexity_score = self._calculate_slide_complexity_score(analysis)
        analysis.estimated_load_time = self._estimate_slide_load_time(analysis)
        
        return analysis
    
    def _analyze_slide_content(self, root: ET.Element, analysis: SlideAnalysis):
        """Analyze content metrics of a slide."""
        
        # Count different object types
        sp_tree = root.find('.//p:cSld/p:spTree', self.NAMESPACES)
        if sp_tree is None:
            return
        
        for elem in sp_tree:
            if elem.tag.endswith('}sp'):  # Shape/text box
                analysis.shape_objects += 1
                
                # Extract text content
                text_content = self._extract_text_content(elem)
                if text_content:
                    analysis.text_objects += 1
                    analysis.text_words += len(text_content.split())
                    analysis.text_characters += len(text_content)
                
            elif elem.tag.endswith('}pic'):  # Picture
                analysis.image_objects += 1
                
            elif elem.tag.endswith('}graphicFrame'):  # Table, chart, etc.
                # Determine specific type
                graphic = elem.find('.//a:graphic', self.NAMESPACES)
                if graphic is not None:
                    graphic_data = graphic.find('.//a:graphicData', self.NAMESPACES)
                    if graphic_data is not None:
                        uri = graphic_data.get('uri', '')
                        if 'table' in uri:
                            analysis.table_objects += 1
                        elif 'chart' in uri:
                            analysis.chart_objects += 1
        
        # Calculate text complexity
        if analysis.text_words > 0:
            avg_word_length = analysis.text_characters / analysis.text_words
            analysis.text_complexity_score = min(100, avg_word_length * 10)
    
    def _analyze_slide_layout(self, root: ET.Element, analysis: SlideAnalysis):
        """Analyze layout characteristics of a slide."""
        
        # Try to determine layout type based on placeholder types
        placeholders = []
        for elem in root.findall('.//p:ph', self.NAMESPACES):
            ph_type = elem.get('type', 'content')
            placeholders.append(ph_type)
        
        # Determine layout type
        if 'title' in placeholders and 'body' in placeholders:
            analysis.layout_type = "Title and Content"
        elif 'title' in placeholders and len(placeholders) == 1:
            analysis.layout_type = "Title Only"
        elif 'ctrTitle' in placeholders:
            analysis.layout_type = "Title Slide"
        elif len(placeholders) == 0:
            analysis.layout_type = "Blank"
        else:
            analysis.layout_type = "Custom"
    
    def _analyze_slide_accessibility(self, root: ET.Element, analysis: SlideAnalysis):
        """Analyze accessibility features of a slide."""
        
        # Count missing alt text
        for pic in root.findall('.//p:pic', self.NAMESPACES):
            c_nv_pr = pic.find('.//p:cNvPr', self.NAMESPACES)
            if c_nv_pr is not None:
                alt_text = c_nv_pr.get('descr', '')
                if not alt_text.strip():
                    analysis.missing_alt_text_count += 1
        
        # Color contrast analysis would require more complex color extraction
        # For now, we'll estimate based on color usage patterns
        
    def _analyze_slide_design(self, root: ET.Element, analysis: SlideAnalysis):
        """Analyze visual design elements of a slide."""
        
        # Extract fonts using an alternative to getparent()
        fonts = set()
        
        # Find all text runs and their properties
        for text_run in root.findall('.//a:r', self.NAMESPACES):
            rpr = text_run.find('.//a:rPr', self.NAMESPACES)
            if rpr is not None:
                # Check for latin font
                latin_font = rpr.find('.//a:latin', self.NAMESPACES)
                if latin_font is not None:
                    typeface = latin_font.get('typeface')
                    if typeface:
                        fonts.add(typeface)
                
                # Check for east asian font
                ea_font = rpr.find('.//a:ea', self.NAMESPACES)
                if ea_font is not None:
                    typeface = ea_font.get('typeface')
                    if typeface:
                        fonts.add(typeface)
                
                # Check for complex script font
                cs_font = rpr.find('.//a:cs', self.NAMESPACES)
                if cs_font is not None:
                    typeface = cs_font.get('typeface')
                    if typeface:
                        fonts.add(typeface)
        
        # Also check paragraph-level font defaults
        for ppr in root.findall('.//a:pPr', self.NAMESPACES):
            def_rpr = ppr.find('.//a:defRPr', self.NAMESPACES)
            if def_rpr is not None:
                latin_font = def_rpr.find('.//a:latin', self.NAMESPACES)
                if latin_font is not None:
                    typeface = latin_font.get('typeface')
                    if typeface:
                        fonts.add(typeface)
        
        analysis.font_usage = list(fonts)
        
        # Extract colors (simplified)
        colors = {}
        for color_elem in root.findall('.//a:srgbClr', self.NAMESPACES):
            color_val = color_elem.get('val')
            if color_val:
                colors[f"#{color_val}"] = colors.get(f"#{color_val}", 0) + 1
        
        analysis.color_usage = colors
    
    def _extract_text_content(self, elem: ET.Element) -> str:
        """Extract text content from an element."""
        text_parts = []
        for t in elem.findall('.//a:t', self.NAMESPACES):
            if t.text:
                text_parts.append(t.text)
        return ' '.join(text_parts).strip()
    
    def _calculate_slide_accessibility_score(self, analysis: SlideAnalysis) -> float:
        """Calculate accessibility score for a slide."""
        score = 100.0
        
        # Deduct for missing alt text
        if analysis.image_objects > 0:
            alt_text_ratio = 1.0 - (analysis.missing_alt_text_count / analysis.image_objects)
            score *= alt_text_ratio
        
        # Deduct for reading order issues
        if analysis.reading_order_issues:
            score -= len(analysis.reading_order_issues) * 10
        
        # Deduct for color contrast issues
        score -= analysis.color_contrast_issues * 15
        
        return max(0.0, score)
    
    def _calculate_slide_design_score(self, analysis: SlideAnalysis) -> float:
        """Calculate design consistency score for a slide."""
        score = 100.0
        
        # Too many fonts reduce consistency
        if len(analysis.font_usage) > 3:
            score -= (len(analysis.font_usage) - 3) * 15
        
        # Too many colors reduce consistency
        if len(analysis.color_usage) > 5:
            score -= (len(analysis.color_usage) - 5) * 10
        
        return max(0.0, score)
    
    def _calculate_slide_complexity_score(self, analysis: SlideAnalysis) -> float:
        """Calculate complexity score for a slide."""
        complexity = 0.0
        
        # Base complexity on object count
        complexity += analysis.total_objects * 5
        
        # Text complexity
        complexity += analysis.text_words * 0.5
        
        # Visual complexity
        complexity += len(analysis.color_usage) * 2
        complexity += len(analysis.font_usage) * 3
        
        return min(100.0, complexity)
    
    def _estimate_slide_load_time(self, analysis: SlideAnalysis) -> float:
        """Estimate load time for a slide in seconds."""
        base_time = 0.1  # Base load time
        
        # Add time for each object type
        base_time += analysis.text_objects * 0.01
        base_time += analysis.image_objects * 0.05
        base_time += analysis.table_objects * 0.03
        base_time += analysis.chart_objects * 0.08
        
        return base_time
    
    def _calculate_accessibility_score(self, result: PPTAnalysisResult) -> float:
        """Calculate overall accessibility score."""
        if not result.slide_analyses:
            return 0.0
        
        slide_scores = [s.accessibility_score for s in result.slide_analyses]
        return statistics.mean(slide_scores)
    
    def _calculate_readability_score(self, result: PPTAnalysisResult) -> float:
        """Calculate text readability score."""
        if not result.slide_analyses:
            return 0.0
        
        total_words = sum(s.text_words for s in result.slide_analyses)
        total_chars = sum(s.text_characters for s in result.slide_analyses)
        
        if total_words == 0:
            return 100.0  # No text = perfect readability
        
        avg_word_length = total_chars / total_words
        # Ideal word length is around 4-6 characters
        if 4 <= avg_word_length <= 6:
            return 100.0
        else:
            deviation = abs(avg_word_length - 5)
            return max(0.0, 100.0 - deviation * 10)
    
    def _calculate_design_consistency_score(self, result: PPTAnalysisResult) -> float:
        """Calculate design consistency score."""
        if not result.slide_analyses:
            return 0.0
        
        slide_scores = [s.design_consistency_score for s in result.slide_analyses]
        return statistics.mean(slide_scores)
    
    def _calculate_image_quality_score(self, result: PPTAnalysisResult) -> float:
        """Calculate image quality score."""
        # This would require actual image analysis
        # For now, return a placeholder score
        total_images = sum(s.image_objects for s in result.slide_analyses)
        if total_images == 0:
            return 100.0
        
        # Assume good quality if not too many images per slide
        avg_images_per_slide = total_images / result.total_slides
        if avg_images_per_slide <= 3:
            return 90.0
        else:
            return max(50.0, 90.0 - (avg_images_per_slide - 3) * 10)
    
    def _estimate_load_time(self, result: PPTAnalysisResult) -> float:
        """Estimate total presentation load time."""
        slide_times = [s.estimated_load_time for s in result.slide_analyses]
        base_time = 0.5  # Base presentation load time
        return base_time + sum(slide_times)
    
    def _calculate_complexity_score(self, result: PPTAnalysisResult) -> float:
        """Calculate overall complexity score."""
        if not result.slide_analyses:
            return 0.0
        
        slide_scores = [s.complexity_score for s in result.slide_analyses]
        return statistics.mean(slide_scores)
    
    def _analyze_color_scheme(self, all_colors: List[str]) -> Dict[str, Any]:
        """Analyze color usage across the presentation."""
        color_counts = {}
        for color in all_colors:
            color_counts[color] = color_counts.get(color, 0) + 1
        
        # Get most used colors
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'primary_colors': [color for color, count in sorted_colors[:5]],
            'total_colors': len(color_counts),
            'color_distribution': dict(sorted_colors[:10])
        }
    
    def _generate_recommendations(self, result: PPTAnalysisResult) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Accessibility recommendations
        if result.accessibility_score < 70:
            recommendations.append("Improve accessibility by adding alt text to images and ensuring proper reading order")
        
        if result.missing_alt_text_count > 0:
            recommendations.append(f"Add alt text to {result.missing_alt_text_count} images for better accessibility")
        
        # Design recommendations
        if result.design_consistency_score < 70:
            recommendations.append("Improve design consistency by limiting font and color variety")
        
        if len(result.font_usage) > 3:
            recommendations.append(f"Consider reducing font variety (currently using {len(result.font_usage)} fonts)")
        
        # Performance recommendations
        if result.estimated_load_time > 5:
            recommendations.append("Consider optimizing images and reducing complexity to improve load times")
        
        if result.complexity_score > 80:
            recommendations.append("Simplify slides to reduce cognitive load and improve comprehension")
        
        # Content recommendations
        total_words = sum(s.text_words for s in result.slide_analyses)
        avg_words_per_slide = total_words / result.total_slides if result.total_slides > 0 else 0
        
        if avg_words_per_slide > 50:
            recommendations.append("Consider reducing text content per slide for better readability")
        
        # Layout recommendations
        layout_variety = len(set(s.layout_type for s in result.slide_analyses))
        if layout_variety == 1:
            recommendations.append("Consider using different slide layouts to improve visual interest")
        
        return recommendations 