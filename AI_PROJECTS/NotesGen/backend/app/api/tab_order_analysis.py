"""
FastAPI endpoints for PowerPoint tab order and reading order analysis.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import tempfile
import os
import logging
from app.utils.tab_order_analyzer import PowerPointTabOrderAnalyzer, TabOrderAnalysis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tab-order", tags=["tab-order-analysis"])

@router.post("/analyze")
async def analyze_ppt_tab_order(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Analyze tab order and reading order for a PowerPoint file.
    
    Args:
        file: Uploaded PPTX file
        
    Returns:
        Analysis results including tab order, reading order, and accessibility information
    """
    
    if not file.filename.lower().endswith(('.pptx', '.ppt')):
        raise HTTPException(status_code=400, detail="File must be a PowerPoint presentation (.pptx or .ppt)")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pptx') as temp_file:
        try:
            # Save uploaded file
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Analyze the file
            analyzer = PowerPointTabOrderAnalyzer()
            analyses = analyzer.analyze_file(temp_file.name)
            
            # Convert to serializable format
            results = []
            for analysis in analyses:
                slide_result = {
                    "slide_number": analysis.slide_number,
                    "total_objects": analysis.total_objects,
                    "has_explicit_tab_order": analysis.has_explicit_tab_order,
                    "has_accessibility_info": analysis.has_accessibility_info,
                    "reading_order_issues": analysis.reading_order_issues or [],
                    
                    # Object collections
                    "all_objects": [_serialize_slide_object(obj) for obj in analysis.all_objects],
                    "interactive_objects": [_serialize_slide_object(obj) for obj in analysis.interactive_objects],
                    "title_objects": [_serialize_slide_object(obj) for obj in analysis.title_objects or []],
                    "content_objects": [_serialize_slide_object(obj) for obj in analysis.content_objects or []],
                    "decorative_objects": [_serialize_slide_object(obj) for obj in analysis.decorative_objects or []],
                    
                    # Ordering information
                    "xml_order": [_serialize_slide_object(obj) for obj in analysis.xml_order],
                    "suggested_reading_order": [_serialize_slide_object(obj) for obj in analysis.suggested_reading_order],
                    "tab_navigation_order": [_serialize_slide_object(obj) for obj in analysis.tab_navigation_order],
                }
                results.append(slide_result)
            
            return {
                "success": True,
                "filename": file.filename,
                "total_slides": len(results),
                "slides": results
            }
            
        except Exception as e:
            logger.error(f"Error analyzing PowerPoint file: {e}")
            raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file.name)
            except OSError:
                pass

@router.post("/analyze/report")
async def analyze_ppt_tab_order_report(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Analyze tab order and reading order for a PowerPoint file and return detailed text reports.
    
    Args:
        file: Uploaded PPTX file
        
    Returns:
        Detailed text reports for each slide
    """
    
    if not file.filename.lower().endswith(('.pptx', '.ppt')):
        raise HTTPException(status_code=400, detail="File must be a PowerPoint presentation (.pptx or .ppt)")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pptx') as temp_file:
        try:
            # Save uploaded file
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Analyze the file
            analyzer = PowerPointTabOrderAnalyzer()
            analyses = analyzer.analyze_file(temp_file.name)
            
            # Generate reports
            reports = []
            summary_stats = {
                "total_slides": len(analyses),
                "slides_with_explicit_tab_order": 0,
                "slides_with_accessibility_info": 0,
                "total_objects": 0,
                "total_interactive_objects": 0,
                "total_issues": 0
            }
            
            for analysis in analyses:
                report_text = analyzer.generate_report(analysis)
                reports.append({
                    "slide_number": analysis.slide_number,
                    "report": report_text,
                    "summary": {
                        "total_objects": analysis.total_objects,
                        "interactive_objects": len(analysis.interactive_objects),
                        "has_explicit_tab_order": analysis.has_explicit_tab_order,
                        "has_accessibility_info": analysis.has_accessibility_info,
                        "issues_count": len(analysis.reading_order_issues or [])
                    }
                })
                
                # Update summary stats
                if analysis.has_explicit_tab_order:
                    summary_stats["slides_with_explicit_tab_order"] += 1
                if analysis.has_accessibility_info:
                    summary_stats["slides_with_accessibility_info"] += 1
                summary_stats["total_objects"] += analysis.total_objects
                summary_stats["total_interactive_objects"] += len(analysis.interactive_objects)
                summary_stats["total_issues"] += len(analysis.reading_order_issues or [])
            
            return {
                "success": True,
                "filename": file.filename,
                "summary": summary_stats,
                "reports": reports
            }
            
        except Exception as e:
            logger.error(f"Error analyzing PowerPoint file: {e}")
            raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file.name)
            except OSError:
                pass

@router.post("/analyze/slide/{slide_number}")
async def analyze_specific_slide(slide_number: int, file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Analyze tab order and reading order for a specific slide.
    
    Args:
        slide_number: Slide number to analyze (1-based)
        file: Uploaded PPTX file
        
    Returns:
        Analysis results for the specified slide
    """
    
    if not file.filename.lower().endswith(('.pptx', '.ppt')):
        raise HTTPException(status_code=400, detail="File must be a PowerPoint presentation (.pptx or .ppt)")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pptx') as temp_file:
        try:
            # Save uploaded file
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Analyze the file
            analyzer = PowerPointTabOrderAnalyzer()
            analyses = analyzer.analyze_file(temp_file.name)
            
            # Find the requested slide
            target_analysis = None
            for analysis in analyses:
                if analysis.slide_number == slide_number:
                    target_analysis = analysis
                    break
            
            if target_analysis is None:
                raise HTTPException(status_code=404, detail=f"Slide {slide_number} not found")
            
            # Generate detailed report
            report_text = analyzer.generate_report(target_analysis)
            
            return {
                "success": True,
                "filename": file.filename,
                "slide_number": slide_number,
                "analysis": {
                    "total_objects": target_analysis.total_objects,
                    "has_explicit_tab_order": target_analysis.has_explicit_tab_order,
                    "has_accessibility_info": target_analysis.has_accessibility_info,
                    "reading_order_issues": target_analysis.reading_order_issues or [],
                    "all_objects": [_serialize_slide_object(obj) for obj in target_analysis.all_objects],
                    "suggested_reading_order": [_serialize_slide_object(obj) for obj in target_analysis.suggested_reading_order],
                    "tab_navigation_order": [_serialize_slide_object(obj) for obj in target_analysis.tab_navigation_order],
                },
                "report": report_text
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error analyzing PowerPoint file: {e}")
            raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file.name)
            except OSError:
                pass

def _serialize_slide_object(obj) -> Dict[str, Any]:
    """Convert a SlideObject to a serializable dictionary."""
    return {
        "id": obj.id,
        "name": obj.name,
        "type": obj.type,
        "x": obj.x,
        "y": obj.y,
        "width": obj.width,
        "height": obj.height,
        "xml_order": obj.xml_order,
        "z_order": obj.z_order,
        "tab_order": obj.tab_order,
        "text_content": obj.text_content,
        "alt_text": obj.alt_text,
        "title_text": obj.title_text,
        "placeholder_type": obj.placeholder_type,
        "shape_type": obj.shape_type,
        "is_title": obj.is_title,
        "is_content": obj.is_content,
        "is_visible": obj.is_visible,
        "is_locked": obj.is_locked,
        "reading_priority": obj.reading_priority,
        "accessibility_order": obj.accessibility_order
    } 