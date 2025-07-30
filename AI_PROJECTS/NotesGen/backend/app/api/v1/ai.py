from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...services.ai_notes_service import AINotesService
from ...db.database import get_db

router = APIRouter()

class SlideDataRequest(BaseModel):
    """Request model for AI notes generation."""
    ppt_file_id: str = None  # Accept both tracking_id and numeric ID
    slide_number: int
    title: str = ""
    content: str = ""
    slide_content: str = ""  # Add support for explicit slide content
    speakerNotes: str = ""
    text_elements: list = []

class AINotesResponse(BaseModel):
    """Response model for AI generated notes."""
    success: bool
    notes: Dict[str, str]
    message: str = ""

@router.post("/generate-notes", response_model=AINotesResponse)
async def generate_notes(request: SlideDataRequest, db: Session = Depends(get_db)) -> AINotesResponse:
    """
    Generate AI-powered speaker notes for a slide.
    
    This endpoint is completely separate from existing PPT processing.
    It takes slide data as input and returns structured notes.
    """
    try:
        # Initialize AI service
        ai_service = AINotesService()
        
        # Check if AI service is available
        if not ai_service.is_available():
            return AINotesResponse(
                success=False,
                notes={},
                message="AI service is not available. Please check AWS Bedrock configuration and credentials."
            )
        
        # Resolve ppt_file_id if provided (for image analysis)
        resolved_ppt_file_id = None
        if request.ppt_file_id:
            from app.models.models import PPTFile
            
            # First try as tracking ID (preferred)
            ppt_file = db.query(PPTFile).filter(PPTFile.tracking_id == request.ppt_file_id).first()
            
            # If not found and identifier looks numeric, try as numeric ID (backward compatibility)
            if not ppt_file and request.ppt_file_id.isdigit():
                ppt_file = db.query(PPTFile).filter(PPTFile.id == int(request.ppt_file_id)).first()
            
            if ppt_file:
                resolved_ppt_file_id = ppt_file.id
        
        # Convert request to slide data format
        slide_data = {
            "ppt_file_id": resolved_ppt_file_id,  # Use resolved numeric ID for image analysis
            "slide_number": request.slide_number,
            "title": request.title,
            "content": request.content,
            "slide_content": request.slide_content,  # Pass through explicit slide content
            "speakerNotes": request.speakerNotes,
            "text_elements": request.text_elements
        }
        
        # Generate notes using AI service
        generated_notes = ai_service.generate_notes(slide_data)
        
        return AINotesResponse(
            success=True,
            notes=generated_notes,
            message="Notes generated successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating AI notes: {str(e)}"
        )

@router.get("/status")
async def ai_status():
    """Check AI service availability status."""
    try:
        ai_service = AINotesService()
        is_available = ai_service.is_available()
        
        return {
            "available": is_available,
            "message": "AI service is ready" if is_available else "AI service is not configured"
        }
    except Exception as e:
        return {
            "available": False,
            "message": f"Error checking AI status: {str(e)}"
        }

@router.get("/debug")
async def ai_debug():
    """Debug AI service configuration."""
    try:
        from ...core.config import get_settings
        settings = get_settings()
        
        return {
            "aws_access_key_id": f"{settings.AWS_ACCESS_KEY_ID[:8]}..." if settings.AWS_ACCESS_KEY_ID != "dummy" else "dummy",
            "aws_secret_access_key": "configured" if settings.AWS_SECRET_ACCESS_KEY != "dummy" else "dummy",
            "aws_region": settings.AWS_DEFAULT_REGION,
            "credentials_look_real": settings.AWS_ACCESS_KEY_ID != "dummy" and settings.AWS_SECRET_ACCESS_KEY != "dummy"
        }
    except Exception as e:
        return {
            "error": str(e)
        } 