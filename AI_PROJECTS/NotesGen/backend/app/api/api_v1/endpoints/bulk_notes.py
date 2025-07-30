"""
Bulk Notes API Endpoints - Isolated bulk processing endpoints
===========================================================

This module provides API endpoints for bulk AI notes generation.
These endpoints are completely separate from existing single-slide endpoints
to ensure zero breaking changes to current functionality.

Endpoints:
- POST /bulk-generate-notes/{ppt_file_id} - Start bulk processing
- GET /bulk-progress/{job_id} - Get progress updates  
- DELETE /bulk-cancel/{job_id} - Cancel running job
- GET /bulk-status/{job_id} - Get detailed job status

CRITICAL: These endpoints do NOT modify existing API behavior.
All bulk operations are additive and isolated from current workflows.
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import asyncio
import json
import uuid
from datetime import datetime
from sqlalchemy import text
from pydantic import BaseModel

from app.db.database import get_db
from app.services.bulk_notes_service import bulk_notes_service, BulkProcessingStatus, BulkNotesService
from app.models.models import PPTFile
from app.utils.tracking_utils import format_tracking_log

# Set up logging
logger = logging.getLogger(__name__)

# Create router for bulk notes endpoints
router = APIRouter()

@router.post("/bulk-generate-notes/{ppt_identifier}")
async def start_bulk_generation(
    ppt_identifier: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Start bulk AI generation for all slides in a PPT file
    
    Args:
        ppt_identifier: Either tracking_id (preferred) or numeric ID of the PPT file
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        job_id: Unique identifier for tracking the bulk processing job
        
    Raises:
        HTTPException: If PPT file not found or validation fails
    """
    try:
        # Resolve PPT file from tracking_id or numeric ID
        ppt_file = None
        
        # First try as tracking ID (preferred)
        ppt_file = db.query(PPTFile).filter(PPTFile.tracking_id == ppt_identifier).first()
        
        # If not found and identifier looks numeric, try as numeric ID (backward compatibility)
        if not ppt_file and ppt_identifier.isdigit():
            ppt_file = db.query(PPTFile).filter(PPTFile.id == int(ppt_identifier)).first()
            logger.warning(f"⚠️ DEPRECATED: Using dangerous numeric ID {ppt_identifier} - should use tracking_id: {ppt_file.tracking_id if ppt_file else 'N/A'}")
        
        if not ppt_file:
            raise HTTPException(
                status_code=404, 
                detail=f"PPT file not found for identifier: {ppt_identifier}"
            )
        
        ppt_file_id = ppt_file.id  # Use internal numeric ID for processing
        
        # Check if file has slides
        from app.models.models import SlideImage
        slide_count = db.query(SlideImage).filter(
            SlideImage.ppt_file_id == ppt_file_id
        ).count()
        
        if slide_count == 0:
            raise HTTPException(
                status_code=400,
                detail=f"PPT file '{ppt_file.filename}' has no slides to process"
            )
        
        # Start bulk processing
        job_id = await bulk_notes_service.start_bulk_processing(ppt_file_id)
        
        logger.info(f"Started bulk generation job {job_id} for PPT file {ppt_file.tracking_id} ({slide_count} slides)")
        
        return {
            "job_id": job_id,
            "ppt_file_id": ppt_file_id,
            "ppt_filename": ppt_file.filename,
            "ppt_tracking_id": ppt_file.tracking_id,
            "total_slides": slide_count,
            "status": "pending",
            "message": f"Bulk processing started for {slide_count} slides",
            "estimated_time_seconds": slide_count * 3,  # Rough estimate: 3 seconds per slide
            "progress_endpoint": f"/api/v1/bulk-progress/{job_id}",
            "status_endpoint": f"/api/v1/bulk-status/{job_id}",
            "cancel_endpoint": f"/api/v1/bulk-cancel/{job_id}"
        }
        
    except ValueError as e:
        logger.error(f"Validation error starting bulk generation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error starting bulk generation: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error starting bulk processing"
        )

@router.get("/bulk-progress/{job_id}")
async def get_bulk_progress_stream(job_id: str):
    """
    Get real-time progress updates for a bulk processing job
    
    Uses Server-Sent Events (SSE) to provide real-time progress updates
    to the frontend for status bar integration.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        StreamingResponse: Real-time progress updates
        
    Raises:
        HTTPException: If job not found
    """
    # Validate job exists
    job_status = bulk_notes_service.get_job_status(job_id)
    if not job_status:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    async def progress_stream():
        """Generate real-time progress events"""
        try:
            while True:
                # Get current status
                current_status = bulk_notes_service.get_job_status(job_id)
                if not current_status:
                    break
                
                # Create progress data for frontend
                progress_data = {
                    "job_id": job_id,
                    "status": current_status.status,
                    "progress": round((current_status.completed_slides / current_status.total_slides) * 100, 1),
                    "completed_slides": current_status.completed_slides,
                    "failed_slides": current_status.failed_slides,
                    "total_slides": current_status.total_slides,
                    "current_slide": current_status.completed_slides + 1 if current_status.status == "processing" else current_status.completed_slides,
                    "estimated_completion": current_status.estimated_completion_at.isoformat() if current_status.estimated_completion_at else None,
                    "has_errors": len(current_status.error_log) > 0
                }
                
                # Send progress update
                yield f"data: {json.dumps(progress_data)}\n\n"
                
                # Stop streaming if job is complete
                if current_status.status in ["completed", "failed", "cancelled"]:
                    # Send final status
                    final_data = progress_data.copy()
                    final_data["final"] = True
                    yield f"data: {json.dumps(final_data)}\n\n"
                    break
                
                # Wait before next update
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in progress stream for job {job_id}: {e}")
            error_data = {
                "job_id": job_id,
                "error": "Progress stream error",
                "final": True
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        progress_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@router.get("/bulk-status/{job_id}")
async def get_bulk_status(job_id: str) -> Dict[str, Any]:
    """
    Get detailed status information for a bulk processing job
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Detailed job status including errors and timing
        
    Raises:
        HTTPException: If job not found
    """
    job_status = bulk_notes_service.get_job_status(job_id)
    if not job_status:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Calculate progress percentage
    progress_percent = (job_status.completed_slides / job_status.total_slides) * 100 if job_status.total_slides > 0 else 0
    
    # Calculate timing information
    timing_info = {}
    if job_status.started_at:
        timing_info["started_at"] = job_status.started_at.isoformat()
        
        if job_status.status == "processing":
            elapsed = (datetime.utcnow() - job_status.started_at).total_seconds()
            timing_info["elapsed_seconds"] = round(elapsed, 1)
            
            if job_status.completed_slides > 0:
                avg_time_per_slide = elapsed / job_status.completed_slides
                timing_info["avg_time_per_slide"] = round(avg_time_per_slide, 1)
                
                remaining_slides = job_status.total_slides - job_status.completed_slides - job_status.failed_slides
                if remaining_slides > 0:
                    eta_seconds = remaining_slides * avg_time_per_slide
                    timing_info["estimated_remaining_seconds"] = round(eta_seconds, 1)
        
        if job_status.estimated_completion_at:
            timing_info["estimated_completion_at"] = job_status.estimated_completion_at.isoformat()
    
    return {
        "job_id": job_id,
        "status": job_status.status,
        "progress": {
            "completed_slides": job_status.completed_slides,
            "failed_slides": job_status.failed_slides,
            "total_slides": job_status.total_slides,
            "progress_percent": round(progress_percent, 1),
            "success_rate": round((job_status.completed_slides / max(1, job_status.completed_slides + job_status.failed_slides)) * 100, 1)
        },
        "timing": timing_info,
        "errors": {
            "has_errors": len(job_status.error_log) > 0,
            "error_count": len(job_status.error_log),
            "latest_errors": job_status.error_log[-5:] if job_status.error_log else []  # Last 5 errors
        },
        "is_complete": job_status.status in ["completed", "failed", "cancelled"],
        "is_successful": job_status.status == "completed" and job_status.failed_slides == 0
    }

@router.delete("/bulk-cancel/{job_id}")
async def cancel_bulk_generation(job_id: str) -> Dict[str, Any]:
    """
    Cancel a running bulk processing job
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Cancellation confirmation
        
    Raises:
        HTTPException: If job not found or not cancellable
    """
    job_status = bulk_notes_service.get_job_status(job_id)
    if not job_status:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if job_status.status not in ["pending", "processing"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Job {job_id} cannot be cancelled (status: {job_status.status})"
        )
    
    # Attempt to cancel the job
    success = await bulk_notes_service.cancel_job(job_id)
    
    if success:
        logger.info(f"Successfully cancelled bulk processing job {job_id}")
        return {
            "job_id": job_id,
            "status": "cancelled",
            "message": "Bulk processing job cancelled successfully",
            "completed_slides": job_status.completed_slides,
            "total_slides": job_status.total_slides
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel job {job_id}"
        )

@router.get("/bulk-jobs")
async def list_bulk_jobs(
    limit: int = 10,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    List recent bulk processing jobs
    
    Args:
        limit: Maximum number of jobs to return
        status_filter: Filter by job status (pending, processing, completed, failed, cancelled)
        db: Database session
        
    Returns:
        List of recent bulk processing jobs
    """
    try:
        # Build query
        base_query = """
            SELECT 
                bgj.job_id,
                bgj.status,
                bgj.total_slides,
                bgj.completed_slides,
                bgj.failed_slides,
                bgj.created_at,
                bgj.started_at,
                bgj.completed_at,
                pf.filename,
                pf.tracking_id
            FROM bulk_generation_jobs bgj
            JOIN ppt_files pf ON bgj.ppt_file_id = pf.id
        """
        
        params = {"limit": limit}
        
        if status_filter:
            base_query += " WHERE bgj.status = :status"
            params["status"] = status_filter
        
        base_query += " ORDER BY bgj.created_at DESC LIMIT :limit"
        
        # Execute query
        result = db.execute(text(base_query), params)
        rows = result.fetchall()
        
        # Format results
        jobs = []
        for row in rows:
            job_data = {
                "job_id": row[0],
                "status": row[1],
                "progress": {
                    "total_slides": row[2],
                    "completed_slides": row[3],
                    "failed_slides": row[4],
                    "progress_percent": round((row[3] / max(1, row[2])) * 100, 1)
                },
                "timing": {
                    "created_at": row[5].isoformat() if row[5] else None,
                    "started_at": row[6].isoformat() if row[6] else None,
                    "completed_at": row[7].isoformat() if row[7] else None
                },
                "ppt_file": {
                    "filename": row[8],
                    "tracking_id": row[9]
                }
            }
            jobs.append(job_data)
        
        return {
            "jobs": jobs,
            "total_returned": len(jobs),
            "status_filter": status_filter,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error listing bulk jobs: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving job list")

@router.get("/bulk-test")
async def test_bulk_service() -> Dict[str, Any]:
    """
    Test endpoint to verify bulk service is working
    
    Returns:
        Service health status
    """
    try:
        # Test that the service can be imported and initialized
        from app.services.bulk_notes_service import bulk_notes_service, progress_tracker
        
        return {
            "service": "bulk_notes",
            "status": "healthy",
            "message": "Bulk notes service is operational",
            "active_jobs": len(bulk_notes_service.processing_jobs),
            "service_config": {
                "max_workers": bulk_notes_service.config.max_workers,
                "batch_size": bulk_notes_service.config.batch_size,
                "timeout_per_slide": bulk_notes_service.config.timeout_per_slide,
                "ai_model_preference": bulk_notes_service.config.ai_model_preference
            }
        }
    except Exception as e:
        logger.error(f"Bulk service test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk service error: {str(e)}")

# Health check specifically for bulk processing
@router.get("/bulk-health")
async def bulk_health_check() -> Dict[str, str]:
    """Simple health check for bulk processing endpoints"""
    return {"status": "healthy", "service": "bulk_notes_api"}

# Add new web search endpoint
class WebSearchRequest(BaseModel):
    query: str
    max_results: int = 5

class WebSearchResponse(BaseModel):
    results: List[Dict[str, str]]
    success: bool
    message: str

@router.post("/web-search", response_model=WebSearchResponse)
async def perform_web_search(request: WebSearchRequest):
    """
    Perform web search for AWS documentation.
    This endpoint allows the AI service to perform dynamic web searches
    instead of using hard-coded URL mappings.
    """
    try:
        # Import requests for web search
        import requests
        from urllib.parse import urlencode
        
        # Create AWS-specific search query
        search_query = f"site:docs.aws.amazon.com {request.query}"
        
        # Try DuckDuckGo instant answers API
        try:
            ddg_url = "https://api.duckduckgo.com/"
            params = {
                'q': search_query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; AWS-NotesGen/1.0)'
            }
            
            response = requests.get(ddg_url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Extract AWS documentation URLs
                if 'RelatedTopics' in data and data['RelatedTopics']:
                    for topic in data['RelatedTopics'][:request.max_results]:
                        if isinstance(topic, dict) and 'FirstURL' in topic:
                            url = topic['FirstURL']
                            if 'docs.aws.amazon.com' in url:
                                results.append({
                                    'url': url,
                                    'title': topic.get('Text', '').split(' - ')[0] or 'AWS Documentation',
                                    'snippet': topic.get('Text', '')
                                })
                
                if results:
                    return WebSearchResponse(
                        results=results,
                        success=True,
                        message=f"Found {len(results)} AWS documentation results"
                    )
                    
        except Exception as search_error:
            print(f"Web search error: {search_error}")
        
        # If web search fails, return appropriate message
        return WebSearchResponse(
            results=[],
            success=False,
            message="Web search functionality not available - requires real search integration"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Web search failed: {str(e)}")

# Import datetime at module level for use in functions
from datetime import datetime 