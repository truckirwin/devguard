"""
FastAPI endpoints for comprehensive PowerPoint analysis.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json
import logging
import tempfile
import os
from pathlib import Path

from app.db.database import get_db
from app.models.models import PPTFile, PPTAnalysis
from app.utils.comprehensive_ppt_analyzer import ComprehensivePPTAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ppt-analysis", tags=["ppt-analysis"])

@router.post("/analyze/{ppt_file_id}")
async def analyze_ppt_file(
    ppt_file_id: int, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform comprehensive analysis of a PowerPoint file by ID.
    
    Args:
        ppt_file_id: ID of the PPT file in the database
        
    Returns:
        Complete analysis results
    """
    
    # Get the PPT file from database
    ppt_file = db.query(PPTFile).filter(PPTFile.id == ppt_file_id).first()
    if not ppt_file:
        raise HTTPException(status_code=404, detail="PPT file not found")
    
    # Check if analysis already exists
    existing_analysis = db.query(PPTAnalysis).filter(PPTAnalysis.ppt_file_id == ppt_file_id).first()
    if existing_analysis:
        return _serialize_analysis(existing_analysis)
    
    try:
        # Verify file exists
        if not os.path.exists(ppt_file.path):
            raise HTTPException(status_code=404, detail="PPT file not found on disk")
        
        # Perform analysis
        analyzer = ComprehensivePPTAnalyzer()
        analysis_result = analyzer.analyze_file(ppt_file.path)
        
        # Create database record
        ppt_analysis = PPTAnalysis(
            ppt_file_id=ppt_file_id,
            total_slides=analysis_result.total_slides,
            total_objects=analysis_result.total_objects,
            slides_with_tab_order=analysis_result.slides_with_tab_order,
            slides_with_accessibility=analysis_result.slides_with_accessibility,
            total_issues=analysis_result.total_issues,
            
            # File metadata
            file_size_mb=analysis_result.file_size_mb,
            slide_dimensions=analysis_result.slide_dimensions,
            has_animations=analysis_result.has_animations,
            has_transitions=analysis_result.has_transitions,
            has_embedded_media=analysis_result.has_embedded_media,
            
            # Content analysis
            slide_layouts_used=json.dumps(analysis_result.slide_layouts_used or []),
            theme_name=analysis_result.theme_name,
            color_scheme=json.dumps(analysis_result.color_scheme or {}),
            font_usage=json.dumps(analysis_result.font_usage or []),
            
            # Accessibility metrics
            accessibility_score=analysis_result.accessibility_score,
            missing_alt_text_count=analysis_result.missing_alt_text_count,
            color_contrast_issues=analysis_result.color_contrast_issues,
            reading_order_issues=analysis_result.reading_order_issues,
            
            # Quality metrics
            image_quality_score=analysis_result.image_quality_score,
            text_readability_score=analysis_result.text_readability_score,
            design_consistency_score=analysis_result.design_consistency_score,
            
            # Performance metrics
            estimated_load_time=analysis_result.estimated_load_time,
            complexity_score=analysis_result.complexity_score,
            
            # Detailed analysis data
            slide_analyses=json.dumps([_serialize_slide_analysis(s) for s in analysis_result.slide_analyses or []]),
            recommendations=json.dumps(analysis_result.recommendations or [])
        )
        
        db.add(ppt_analysis)
        db.commit()
        db.refresh(ppt_analysis)
        
        logger.info(f"Successfully analyzed PPT file {ppt_file_id}: {analysis_result.filename}")
        
        return _serialize_analysis(ppt_analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing PPT file {ppt_file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")

@router.get("/analysis/{ppt_file_id}")
async def get_ppt_analysis(
    ppt_file_id: int, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get existing analysis for a PowerPoint file.
    
    Args:
        ppt_file_id: ID of the PPT file
        
    Returns:
        Analysis results if they exist
    """
    
    analysis = db.query(PPTAnalysis).filter(PPTAnalysis.ppt_file_id == ppt_file_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return _serialize_analysis(analysis)

@router.get("/analysis/{ppt_file_id}/summary")
async def get_ppt_analysis_summary(
    ppt_file_id: int, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a summary of the PowerPoint analysis.
    
    Args:
        ppt_file_id: ID of the PPT file
        
    Returns:
        Summary of analysis results
    """
    
    analysis = db.query(PPTAnalysis).filter(PPTAnalysis.ppt_file_id == ppt_file_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return {
        "ppt_file_id": ppt_file_id,
        "total_slides": analysis.total_slides,
        "total_objects": analysis.total_objects,
        "file_size_mb": analysis.file_size_mb,
        "slide_dimensions": analysis.slide_dimensions,
        "theme_name": analysis.theme_name,
        "accessibility_score": analysis.accessibility_score,
        "design_consistency_score": analysis.design_consistency_score,
        "complexity_score": analysis.complexity_score,
        "estimated_load_time": analysis.estimated_load_time,
        "has_embedded_media": analysis.has_embedded_media,
        "recommendations_count": len(json.loads(analysis.recommendations or "[]")),
        "created_at": analysis.created_at.isoformat(),
        "updated_at": analysis.updated_at.isoformat()
    }

@router.delete("/analysis/{ppt_file_id}")
async def delete_ppt_analysis(
    ppt_file_id: int, 
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Delete analysis for a PowerPoint file (will trigger re-analysis on next request).
    
    Args:
        ppt_file_id: ID of the PPT file
        
    Returns:
        Success message
    """
    
    analysis = db.query(PPTAnalysis).filter(PPTAnalysis.ppt_file_id == ppt_file_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    db.delete(analysis)
    db.commit()
    
    return {"message": "Analysis deleted successfully"}

@router.post("/analyze-or-get/{ppt_file_id}")
async def analyze_or_get_ppt_analysis(
    ppt_file_id: int, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get existing analysis or perform new analysis if not exists.
    This is the main endpoint that the frontend should call.
    
    Args:
        ppt_file_id: ID of the PPT file
        
    Returns:
        Analysis results (existing or newly created)
    """
    
    # Check if analysis already exists
    existing_analysis = db.query(PPTAnalysis).filter(PPTAnalysis.ppt_file_id == ppt_file_id).first()
    if existing_analysis:
        return _serialize_analysis(existing_analysis)
    
    # If not, perform analysis
    return await analyze_ppt_file(ppt_file_id, db)

def _serialize_analysis(analysis: PPTAnalysis) -> Dict[str, Any]:
    """Serialize PPTAnalysis model to dictionary."""
    return {
        "id": analysis.id,
        "ppt_file_id": analysis.ppt_file_id,
        
        # Overall metrics
        "total_slides": analysis.total_slides,
        "total_objects": analysis.total_objects,
        "slides_with_tab_order": analysis.slides_with_tab_order,
        "slides_with_accessibility": analysis.slides_with_accessibility,
        "total_issues": analysis.total_issues,
        
        # File metadata
        "file_size_mb": analysis.file_size_mb,
        "slide_dimensions": analysis.slide_dimensions,
        "has_animations": analysis.has_animations,
        "has_transitions": analysis.has_transitions,
        "has_embedded_media": analysis.has_embedded_media,
        
        # Content analysis
        "slide_layouts_used": json.loads(analysis.slide_layouts_used or "[]"),
        "theme_name": analysis.theme_name,
        "color_scheme": json.loads(analysis.color_scheme or "{}"),
        "font_usage": json.loads(analysis.font_usage or "[]"),
        
        # Accessibility metrics
        "accessibility_score": analysis.accessibility_score,
        "missing_alt_text_count": analysis.missing_alt_text_count,
        "color_contrast_issues": analysis.color_contrast_issues,
        "reading_order_issues": analysis.reading_order_issues,
        
        # Quality metrics
        "image_quality_score": analysis.image_quality_score,
        "text_readability_score": analysis.text_readability_score,
        "design_consistency_score": analysis.design_consistency_score,
        
        # Performance metrics
        "estimated_load_time": analysis.estimated_load_time,
        "complexity_score": analysis.complexity_score,
        
        # Detailed analysis data
        "slide_analyses": json.loads(analysis.slide_analyses or "[]"),
        "recommendations": json.loads(analysis.recommendations or "[]"),
        
        # Timestamps
        "created_at": analysis.created_at.isoformat(),
        "updated_at": analysis.updated_at.isoformat()
    }

def _serialize_slide_analysis(slide_analysis) -> Dict[str, Any]:
    """Serialize SlideAnalysis dataclass to dictionary."""
    return {
        "slide_number": slide_analysis.slide_number,
        "text_words": slide_analysis.text_words,
        "text_characters": slide_analysis.text_characters,
        "text_complexity_score": slide_analysis.text_complexity_score,
        "total_objects": slide_analysis.total_objects,
        "text_objects": slide_analysis.text_objects,
        "image_objects": slide_analysis.image_objects,
        "shape_objects": slide_analysis.shape_objects,
        "table_objects": slide_analysis.table_objects,
        "chart_objects": slide_analysis.chart_objects,
        "layout_type": slide_analysis.layout_type,
        "layout_consistency_score": slide_analysis.layout_consistency_score,
        "accessibility_score": slide_analysis.accessibility_score,
        "missing_alt_text_count": slide_analysis.missing_alt_text_count,
        "color_contrast_issues": slide_analysis.color_contrast_issues,
        "reading_order_issues": slide_analysis.reading_order_issues or [],
        "color_usage": slide_analysis.color_usage or {},
        "font_usage": slide_analysis.font_usage or [],
        "design_consistency_score": slide_analysis.design_consistency_score,
        "estimated_load_time": slide_analysis.estimated_load_time,
        "complexity_score": slide_analysis.complexity_score,
        "tab_order_analysis": slide_analysis.tab_order_analysis or {}
    } 