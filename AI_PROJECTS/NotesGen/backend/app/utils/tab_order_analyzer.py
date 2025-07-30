"""
PowerPoint Tab Order and Reading Order Analyzer

This module provides comprehensive analysis of tab order and reading order
in PowerPoint (PPTX) presentations by parsing the underlying XML structure.
"""

import zipfile
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import re
import logging

logger = logging.getLogger(__name__)

@dataclass
class SlideObject:
    """Represents an object on a PowerPoint slide with ordering information."""
    
    # Object identification
    id: str
    name: str
    type: str  # 'shape', 'textbox', 'image', 'table', 'chart', etc.
    
    # Position and geometry
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    
    # Ordering information
    xml_order: int = 0  # Order in which it appears in XML
    z_order: Optional[int] = None  # Z-order (layering)
    tab_order: Optional[int] = None  # Explicit tab order if available
    
    # Content and accessibility
    text_content: str = ""
    alt_text: str = ""
    title_text: str = ""
    
    # PowerPoint specific
    placeholder_type: Optional[str] = None
    shape_type: Optional[str] = None
    is_title: bool = False
    is_content: bool = False
    
    # Visual properties
    is_visible: bool = True
    is_locked: bool = False
    
    # Reading order factors
    reading_priority: int = 0  # Calculated reading priority
    accessibility_order: Optional[int] = None


@dataclass
class TabOrderAnalysis:
    """Complete analysis of tab order and reading order for a slide."""
    
    slide_number: int
    total_objects: int
    
    # Object collections
    all_objects: List[SlideObject]
    interactive_objects: List[SlideObject]  # Objects that can receive focus
    
    # Ordering information
    xml_order: List[SlideObject]  # Order as they appear in XML
    suggested_reading_order: List[SlideObject]  # Logical reading order
    tab_navigation_order: List[SlideObject]  # Tab navigation order
    
    # Analysis results
    has_explicit_tab_order: bool = False
    has_accessibility_info: bool = False
    reading_order_issues: List[str] = None
    
    # Detailed analysis
    title_objects: List[SlideObject] = None
    content_objects: List[SlideObject] = None
    decorative_objects: List[SlideObject] = None


class PowerPointTabOrderAnalyzer:
    """Analyzes tab order and reading order in PowerPoint presentations."""
    
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
        """Initialize the analyzer."""
        for prefix, uri in self.NAMESPACES.items():
            ET.register_namespace(prefix, uri)
    
    def analyze_file(self, file_path: str) -> List[TabOrderAnalysis]:
        """
        Analyze tab order and reading order for all slides in a PPTX file.
        
        Args:
            file_path: Path to the PPTX file
            
        Returns:
            List of TabOrderAnalysis objects, one for each slide
        """
        try:
            with zipfile.ZipFile(file_path, 'r') as pptx_zip:
                return self._analyze_presentation(pptx_zip)
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            raise
    
    def _analyze_presentation(self, pptx_zip: zipfile.ZipFile) -> List[TabOrderAnalysis]:
        """Analyze the entire presentation."""
        results = []
        
        # Get all slide XML files
        slide_files = [f for f in pptx_zip.namelist() 
                      if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
        
        # Sort by slide number
        slide_files.sort(key=lambda x: int(re.search(r'slide(\d+)\.xml', x).group(1)))
        
        for slide_file in slide_files:
            slide_number = int(re.search(r'slide(\d+)\.xml', slide_file).group(1))
            
            # Read slide XML
            with pptx_zip.open(slide_file) as f:
                slide_xml = f.read().decode('utf-8')
            
            # Analyze this slide
            analysis = self._analyze_slide(slide_xml, slide_number, pptx_zip)
            results.append(analysis)
        
        return results
    
    def _analyze_slide(self, slide_xml: str, slide_number: int, 
                      pptx_zip: zipfile.ZipFile) -> TabOrderAnalysis:
        """Analyze a single slide for tab order and reading order."""
        
        # Parse XML
        root = ET.fromstring(slide_xml)
        
        # Extract all objects
        all_objects = self._extract_slide_objects(root, slide_number)
        
        # Analyze different orderings
        xml_order = sorted(all_objects, key=lambda obj: obj.xml_order)
        
        # Calculate suggested reading order
        suggested_reading_order = self._calculate_reading_order(all_objects)
        
        # Determine tab navigation order
        tab_navigation_order = self._determine_tab_order(all_objects)
        
        # Filter interactive objects
        interactive_objects = [obj for obj in all_objects 
                             if self._is_interactive_object(obj)]
        
        # Categorize objects
        title_objects = [obj for obj in all_objects if obj.is_title]
        content_objects = [obj for obj in all_objects if obj.is_content and not obj.is_title]
        decorative_objects = [obj for obj in all_objects 
                            if not obj.is_title and not obj.is_content]
        
        # Check for explicit tab order
        has_explicit_tab_order = any(obj.tab_order is not None for obj in all_objects)
        
        # Check for accessibility information
        has_accessibility_info = any(obj.alt_text or obj.title_text for obj in all_objects)
        
        # Identify potential issues
        reading_order_issues = self._identify_reading_order_issues(all_objects, suggested_reading_order)
        
        return TabOrderAnalysis(
            slide_number=slide_number,
            total_objects=len(all_objects),
            all_objects=all_objects,
            interactive_objects=interactive_objects,
            xml_order=xml_order,
            suggested_reading_order=suggested_reading_order,
            tab_navigation_order=tab_navigation_order,
            has_explicit_tab_order=has_explicit_tab_order,
            has_accessibility_info=has_accessibility_info,
            reading_order_issues=reading_order_issues,
            title_objects=title_objects,
            content_objects=content_objects,
            decorative_objects=decorative_objects
        )
    
    def _extract_slide_objects(self, root: ET.Element, slide_number: int) -> List[SlideObject]:
        """Extract all objects from a slide."""
        objects = []
        xml_order = 0
        
        # Find the shape tree
        sp_tree = root.find('.//p:cSld/p:spTree', self.NAMESPACES)
        if sp_tree is None:
            return objects
        
        # Process all shapes
        for shape_elem in sp_tree:
            if shape_elem.tag.endswith('}sp'):  # Text box/shape
                obj = self._extract_shape_object(shape_elem, xml_order)
                if obj:
                    objects.append(obj)
                    xml_order += 1
            
            elif shape_elem.tag.endswith('}pic'):  # Picture/image
                obj = self._extract_picture_object(shape_elem, xml_order)
                if obj:
                    objects.append(obj)
                    xml_order += 1
            
            elif shape_elem.tag.endswith('}graphicFrame'):  # Table, chart, etc.
                obj = self._extract_graphic_frame_object(shape_elem, xml_order)
                if obj:
                    objects.append(obj)
                    xml_order += 1
            
            elif shape_elem.tag.endswith('}grpSp'):  # Group
                group_objects = self._extract_group_objects(shape_elem, xml_order)
                objects.extend(group_objects)
                xml_order += len(group_objects)
        
        return objects
    
    def _extract_shape_object(self, shape_elem: ET.Element, xml_order: int) -> Optional[SlideObject]:
        """Extract information from a shape (text box, etc.)."""
        
        # Get basic properties
        nv_sp_pr = shape_elem.find('.//p:nvSpPr', self.NAMESPACES)
        if nv_sp_pr is None:
            return None
        
        c_nv_pr = nv_sp_pr.find('.//p:cNvPr', self.NAMESPACES)
        name = c_nv_pr.get('name', 'Unnamed') if c_nv_pr is not None else 'Unnamed'
        object_id = c_nv_pr.get('id', str(xml_order)) if c_nv_pr is not None else str(xml_order)
        
        # Get placeholder information
        nv_pr = nv_sp_pr.find('.//p:nvPr', self.NAMESPACES)
        placeholder_type = None
        is_title = False
        is_content = False
        
        if nv_pr is not None:
            ph = nv_pr.find('.//p:ph', self.NAMESPACES)
            if ph is not None:
                placeholder_type = ph.get('type', '')
                is_title = placeholder_type in ['title', 'ctrTitle']
                is_content = placeholder_type in ['body', 'obj', 'tbl', 'chart']
        
        # Check name for title indication
        if not is_title and ('title' in name.lower() or 'heading' in name.lower()):
            is_title = True
        
        # Get position and size
        x, y, width, height = self._extract_position_and_size(shape_elem)
        
        # Get text content
        text_content = self._extract_text_content(shape_elem)
        
        # Get accessibility information
        alt_text = c_nv_pr.get('descr', '') if c_nv_pr is not None else ''
        title_text = c_nv_pr.get('title', '') if c_nv_pr is not None else ''
        
        # Look for explicit tab order (often in extension lists)
        tab_order = self._extract_tab_order(shape_elem)
        
        # Get shape type
        shape_type = self._get_shape_type(shape_elem)
        
        return SlideObject(
            id=object_id,
            name=name,
            type='shape',
            x=x, y=y, width=width, height=height,
            xml_order=xml_order,
            tab_order=tab_order,
            text_content=text_content,
            alt_text=alt_text,
            title_text=title_text,
            placeholder_type=placeholder_type,
            shape_type=shape_type,
            is_title=is_title,
            is_content=is_content,
            reading_priority=self._calculate_reading_priority(is_title, is_content, y, x)
        )
    
    def _extract_picture_object(self, pic_elem: ET.Element, xml_order: int) -> Optional[SlideObject]:
        """Extract information from a picture/image."""
        
        nv_pic_pr = pic_elem.find('.//p:nvPicPr', self.NAMESPACES)
        if nv_pic_pr is None:
            return None
        
        c_nv_pr = nv_pic_pr.find('.//p:cNvPr', self.NAMESPACES)
        name = c_nv_pr.get('name', 'Image') if c_nv_pr is not None else 'Image'
        object_id = c_nv_pr.get('id', str(xml_order)) if c_nv_pr is not None else str(xml_order)
        
        # Get position and size
        x, y, width, height = self._extract_position_and_size(pic_elem)
        
        # Get accessibility information
        alt_text = c_nv_pr.get('descr', '') if c_nv_pr is not None else ''
        title_text = c_nv_pr.get('title', '') if c_nv_pr is not None else ''
        
        # Look for explicit tab order
        tab_order = self._extract_tab_order(pic_elem)
        
        return SlideObject(
            id=object_id,
            name=name,
            type='image',
            x=x, y=y, width=width, height=height,
            xml_order=xml_order,
            tab_order=tab_order,
            alt_text=alt_text,
            title_text=title_text,
            is_content=True,
            reading_priority=self._calculate_reading_priority(False, True, y, x)
        )
    
    def _extract_graphic_frame_object(self, frame_elem: ET.Element, xml_order: int) -> Optional[SlideObject]:
        """Extract information from a graphic frame (table, chart, etc.)."""
        
        nv_graphic_frame_pr = frame_elem.find('.//p:nvGraphicFramePr', self.NAMESPACES)
        if nv_graphic_frame_pr is None:
            return None
        
        c_nv_pr = nv_graphic_frame_pr.find('.//p:cNvPr', self.NAMESPACES)
        name = c_nv_pr.get('name', 'Graphic') if c_nv_pr is not None else 'Graphic'
        object_id = c_nv_pr.get('id', str(xml_order)) if c_nv_pr is not None else str(xml_order)
        
        # Determine type (table, chart, etc.)
        obj_type = 'graphic'
        graphic = frame_elem.find('.//a:graphic', self.NAMESPACES)
        if graphic is not None:
            graphic_data = graphic.find('.//a:graphicData', self.NAMESPACES)
            if graphic_data is not None:
                uri = graphic_data.get('uri', '')
                if 'table' in uri:
                    obj_type = 'table'
                elif 'chart' in uri:
                    obj_type = 'chart'
        
        # Get position and size
        x, y, width, height = self._extract_position_and_size(frame_elem)
        
        # Get accessibility information
        alt_text = c_nv_pr.get('descr', '') if c_nv_pr is not None else ''
        title_text = c_nv_pr.get('title', '') if c_nv_pr is not None else ''
        
        # Look for explicit tab order
        tab_order = self._extract_tab_order(frame_elem)
        
        return SlideObject(
            id=object_id,
            name=name,
            type=obj_type,
            x=x, y=y, width=width, height=height,
            xml_order=xml_order,
            tab_order=tab_order,
            alt_text=alt_text,
            title_text=title_text,
            is_content=True,
            reading_priority=self._calculate_reading_priority(False, True, y, x)
        )
    
    def _extract_group_objects(self, group_elem: ET.Element, xml_order: int) -> List[SlideObject]:
        """Extract objects from a group."""
        objects = []
        
        # Process each item in the group
        for i, child in enumerate(group_elem):
            if child.tag.endswith('}sp'):
                obj = self._extract_shape_object(child, xml_order + i)
                if obj:
                    obj.name = f"Group/{obj.name}"
                    objects.append(obj)
            elif child.tag.endswith('}pic'):
                obj = self._extract_picture_object(child, xml_order + i)
                if obj:
                    obj.name = f"Group/{obj.name}"
                    objects.append(obj)
        
        return objects
    
    def _extract_position_and_size(self, elem: ET.Element) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        """Extract position and size from an element."""
        
        xfrm = elem.find('.//a:xfrm', self.NAMESPACES)
        if xfrm is None:
            return None, None, None, None
        
        off = xfrm.find('.//a:off', self.NAMESPACES)
        ext = xfrm.find('.//a:ext', self.NAMESPACES)
        
        x = float(off.get('x', 0)) / 914400 if off is not None else None  # Convert EMU to inches
        y = float(off.get('y', 0)) / 914400 if off is not None else None
        width = float(ext.get('cx', 0)) / 914400 if ext is not None else None
        height = float(ext.get('cy', 0)) / 914400 if ext is not None else None
        
        return x, y, width, height
    
    def _extract_text_content(self, elem: ET.Element) -> str:
        """Extract text content from an element."""
        text_parts = []
        
        for t in elem.findall('.//a:t', self.NAMESPACES):
            if t.text:
                text_parts.append(t.text)
        
        return ' '.join(text_parts).strip()
    
    def _extract_tab_order(self, elem: ET.Element) -> Optional[int]:
        """Extract explicit tab order if available."""
        
        # Look in extension lists for tab order information
        for ext_lst in elem.findall('.//p:extLst', self.NAMESPACES):
            for ext in ext_lst.findall('.//p:ext', self.NAMESPACES):
                # Check for various tab order extensions
                for tab_elem in ext.findall('.//*[@tabOrder]'):
                    try:
                        return int(tab_elem.get('tabOrder'))
                    except (ValueError, TypeError):
                        continue
        
        # Check for order attributes in various namespaces
        order_attrs = ['order', 'tabOrder', 'tabIndex']
        for attr in order_attrs:
            value = elem.get(attr)
            if value:
                try:
                    return int(value)
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def _get_shape_type(self, shape_elem: ET.Element) -> Optional[str]:
        """Get the shape type."""
        
        # Look for preset geometry
        preset_geom = shape_elem.find('.//a:prstGeom', self.NAMESPACES)
        if preset_geom is not None:
            return preset_geom.get('prst', 'shape')
        
        # Look for custom geometry
        custom_geom = shape_elem.find('.//a:custGeom', self.NAMESPACES)
        if custom_geom is not None:
            return 'custom'
        
        return 'shape'
    
    def _calculate_reading_priority(self, is_title: bool, is_content: bool, 
                                  y: Optional[float], x: Optional[float]) -> int:
        """Calculate reading priority based on content type and position."""
        
        # Base priority
        priority = 1000
        
        # Title elements have highest priority
        if is_title:
            priority -= 500
        elif is_content:
            priority -= 200
        
        # Position-based priority (top-left first)
        if y is not None:
            priority += int(y * 100)  # Earlier Y position = higher priority
        
        if x is not None:
            priority += int(x * 10)   # Earlier X position = higher priority
        
        return priority
    
    def _calculate_reading_order(self, objects: List[SlideObject]) -> List[SlideObject]:
        """Calculate suggested reading order based on content and position."""
        
        # Sort by reading priority
        return sorted(objects, key=lambda obj: obj.reading_priority)
    
    def _determine_tab_order(self, objects: List[SlideObject]) -> List[SlideObject]:
        """Determine tab navigation order."""
        
        # First, use explicit tab order if available
        explicit_tab_objects = [obj for obj in objects if obj.tab_order is not None]
        if explicit_tab_objects:
            explicit_tab_objects.sort(key=lambda obj: obj.tab_order)
            
            # Add remaining objects without explicit tab order
            remaining_objects = [obj for obj in objects if obj.tab_order is None]
            remaining_objects = self._calculate_reading_order(remaining_objects)
            
            return explicit_tab_objects + remaining_objects
        
        # If no explicit tab order, use reading order for interactive objects
        interactive_objects = [obj for obj in objects if self._is_interactive_object(obj)]
        return self._calculate_reading_order(interactive_objects)
    
    def _is_interactive_object(self, obj: SlideObject) -> bool:
        """Determine if an object can receive focus for tab navigation."""
        
        # Text content usually makes objects interactive
        if obj.text_content.strip():
            return True
        
        # Interactive types
        interactive_types = ['table', 'chart']
        if obj.type in interactive_types:
            return True
        
        # Shapes with certain types might be interactive
        interactive_shapes = ['rect', 'roundRect', 'ellipse']
        if obj.shape_type in interactive_shapes and obj.text_content:
            return True
        
        return False
    
    def _identify_reading_order_issues(self, all_objects: List[SlideObject], 
                                     reading_order: List[SlideObject]) -> List[str]:
        """Identify potential reading order issues."""
        
        issues = []
        
        # Check if titles come first
        title_objects = [obj for obj in all_objects if obj.is_title]
        if title_objects:
            first_title_index = next((i for i, obj in enumerate(reading_order) 
                                    if obj.is_title), len(reading_order))
            if first_title_index > 2:  # Allow some flexibility
                issues.append("Title objects appear late in reading order")
        
        # Check for objects without accessibility information
        missing_alt_text = [obj for obj in all_objects 
                          if obj.type == 'image' and not obj.alt_text]
        if missing_alt_text:
            issues.append(f"{len(missing_alt_text)} image(s) missing alt text")
        
        # Check for potential tab order conflicts
        explicit_tab_orders = [obj.tab_order for obj in all_objects 
                             if obj.tab_order is not None]
        if len(explicit_tab_orders) != len(set(explicit_tab_orders)):
            issues.append("Duplicate tab order values detected")
        
        # Check for large position gaps that might indicate layout issues
        if len(reading_order) > 1:
            y_positions = [obj.y for obj in reading_order if obj.y is not None]
            if len(y_positions) > 1:
                y_gaps = [abs(y_positions[i] - y_positions[i-1]) 
                         for i in range(1, len(y_positions))]
                large_gaps = [gap for gap in y_gaps if gap > 2.0]  # 2 inches
                if large_gaps:
                    issues.append("Large vertical gaps between objects may affect reading flow")
        
        return issues
    
    def generate_report(self, analysis: TabOrderAnalysis) -> str:
        """Generate a human-readable report of the tab order analysis."""
        
        report = []
        report.append(f"=== TAB ORDER & READING ORDER ANALYSIS - SLIDE {analysis.slide_number} ===\n")
        
        # Summary
        report.append(f"📊 SUMMARY")
        report.append(f"   Total Objects: {analysis.total_objects}")
        report.append(f"   Interactive Objects: {len(analysis.interactive_objects)}")
        report.append(f"   Title Objects: {len(analysis.title_objects)}")
        report.append(f"   Content Objects: {len(analysis.content_objects)}")
        report.append(f"   Decorative Objects: {len(analysis.decorative_objects)}")
        report.append(f"   Explicit Tab Order: {'Yes' if analysis.has_explicit_tab_order else 'No'}")
        report.append(f"   Accessibility Info: {'Yes' if analysis.has_accessibility_info else 'No'}")
        report.append("")
        
        # Reading order
        report.append(f"📖 SUGGESTED READING ORDER")
        for i, obj in enumerate(analysis.suggested_reading_order, 1):
            report.append(f"   {i:2d}. {obj.name} ({obj.type})")
            if obj.is_title:
                report.append(f"       🏷️  TITLE")
            if obj.text_content:
                preview = obj.text_content[:50] + "..." if len(obj.text_content) > 50 else obj.text_content
                report.append(f"       📝 \"{preview}\"")
            if obj.x is not None and obj.y is not None:
                report.append(f"       📍 Position: ({obj.x:.1f}, {obj.y:.1f})")
        report.append("")
        
        # Tab navigation order
        if analysis.tab_navigation_order:
            report.append(f"⌨️  TAB NAVIGATION ORDER")
            for i, obj in enumerate(analysis.tab_navigation_order, 1):
                tab_info = f" [Tab #{obj.tab_order}]" if obj.tab_order is not None else ""
                report.append(f"   {i:2d}. {obj.name} ({obj.type}){tab_info}")
        report.append("")
        
        # XML order vs reading order comparison
        report.append(f"🔍 XML vs READING ORDER COMPARISON")
        report.append(f"   XML Order: {' → '.join([obj.name for obj in analysis.xml_order[:5]])}")
        report.append(f"   Reading:   {' → '.join([obj.name for obj in analysis.suggested_reading_order[:5]])}")
        if len(analysis.xml_order) > 5:
            report.append(f"              ... and {len(analysis.xml_order) - 5} more objects")
        report.append("")
        
        # Issues
        if analysis.reading_order_issues:
            report.append(f"⚠️  POTENTIAL ISSUES")
            for issue in analysis.reading_order_issues:
                report.append(f"   • {issue}")
        else:
            report.append(f"✅ NO READING ORDER ISSUES DETECTED")
        report.append("")
        
        # Detailed object information
        report.append(f"📋 DETAILED OBJECT INFORMATION")
        for obj in analysis.all_objects:
            report.append(f"   🔸 {obj.name} (ID: {obj.id})")
            report.append(f"      Type: {obj.type}")
            if obj.placeholder_type:
                report.append(f"      Placeholder: {obj.placeholder_type}")
            if obj.shape_type:
                report.append(f"      Shape Type: {obj.shape_type}")
            if obj.x is not None:
                report.append(f"      Position: ({obj.x:.1f}, {obj.y:.1f}) Size: {obj.width:.1f}×{obj.height:.1f}")
            report.append(f"      XML Order: {obj.xml_order}")
            if obj.tab_order is not None:
                report.append(f"      Tab Order: {obj.tab_order}")
            report.append(f"      Reading Priority: {obj.reading_priority}")
            if obj.alt_text:
                report.append(f"      Alt Text: \"{obj.alt_text}\"")
            if obj.title_text:
                report.append(f"      Title: \"{obj.title_text}\"")
            if obj.text_content:
                preview = obj.text_content[:100] + "..." if len(obj.text_content) > 100 else obj.text_content
                report.append(f"      Content: \"{preview}\"")
            report.append("")
        
        return "\n".join(report) 