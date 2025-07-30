from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
import zipfile
from pathlib import Path
from datetime import datetime
import hashlib

from app.core.config import get_settings
from app.db.database import get_db
from app.models.models import PPTFile, PPTSlide
from app.schemas.ppt_file import PPTFileCreate, PPTFileInDB
from app.utils.ppt_processor import PPTProcessor

router = APIRouter()

@router.post("/upload", response_model=PPTFileInDB)
async def upload_ppt_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Create uploads directory
        upload_dir = Path("uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded file
        file_path = upload_dir / file.filename
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        # Compute SHA256 hash for deduplication
        content_hash = hashlib.sha256(content).hexdigest()
        existing = db.query(PPTFile).filter(PPTFile.content_hash == content_hash).first()
        if existing:
            return existing
        
        # Create database record
        ppt_file = PPTFile(
            user_id=1,  # Default user for now
            filename=file.filename,
            path=str(file_path),
            size=len(content),
            content_hash=content_hash
        )
        db.add(ppt_file)
        db.commit()
        db.refresh(ppt_file)
        
        return ppt_file
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/{ppt_id}", response_model=List[dict])
async def get_ppt_content(
    ppt_id: int,
    db: Session = Depends(get_db)
):
    ppt_file = db.query(PPTFile).filter(PPTFile.id == ppt_id).first()
    if not ppt_file:
        raise HTTPException(status_code=404, detail="PPT file not found")
    
    processor = PPTProcessor()
    return processor.extract_text_from_ppt(ppt_file.path)

@router.get("/slide-with-ai/{tracking_id}/{slide_number}")
async def get_slide_with_ai_data(
    tracking_id: str,
    slide_number: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get slide data with AI-generated fields.
    Used by frontend to fetch individual slide content including all AI-generated fields.
    """
    try:
        # Find PPT file by tracking_id
        ppt_file = db.query(PPTFile).filter(PPTFile.tracking_id == tracking_id).first()
        if not ppt_file:
            raise HTTPException(status_code=404, detail=f"PPT file not found with tracking_id: {tracking_id}")
        
        # Find slide data
        slide = db.query(PPTSlide).filter(
            PPTSlide.ppt_file_id == ppt_file.id,
            PPTSlide.slide_number == slide_number
        ).first()
        
        if not slide:
            # Return empty structure if slide not found in database
            return {
                "slide_number": slide_number,
                "title": "",
                "content": "",
                "ai_generated": False,
                "ai_script": "",
                "ai_instructor_notes": "",
                "ai_student_notes": "",
                "ai_alt_text": "",
                "ai_slide_description": "",
                "ai_references": "",
                "ai_developer_notes": "",
                "ai_generated_at": None
            }
        
        # If slide has AI content, format it using the exact Speaker Notes format
        formatted_speaker_notes = ""
        if slide.ai_generated and (slide.ai_script or slide.ai_developer_notes or slide.ai_alt_text):
            from app.services.bulk_notes_service import bulk_notes_service
            
            # Prepare AI content for formatting
            generated_content = {
                'script': slide.ai_script or '',
                'developerNotes': slide.ai_developer_notes or '',
                'altText': slide.ai_alt_text or '',
                'instructorNotes': slide.ai_instructor_notes or '',
                'studentNotes': slide.ai_student_notes or '',
                'references': slide.ai_references or '',
                'slideDescription': slide.ai_slide_description or ''
            }
            
            # Generate formatted Speaker Notes with special characters
            formatted_speaker_notes = bulk_notes_service._create_combined_notes_with_exact_format(generated_content)

        # Return slide data with all AI fields AND formatted speaker notes
        return {
            "slide_number": slide.slide_number,
            "title": slide.title or "",
            "content": slide.content or "",
            "notes": slide.notes or "",
            "ai_generated": slide.ai_generated or False,
            "ai_script": slide.ai_script or "",
            "ai_instructor_notes": slide.ai_instructor_notes or "",
            "ai_student_notes": slide.ai_student_notes or "",
            "ai_alt_text": slide.ai_alt_text or "",
            "ai_slide_description": slide.ai_slide_description or "",
            "ai_references": slide.ai_references or "",
            "ai_developer_notes": slide.ai_developer_notes or "",
            "ai_generated_at": slide.ai_generated_at.isoformat() if slide.ai_generated_at else None,
            "ai_model_used": slide.ai_model_used or "",
            "formatted_speaker_notes": formatted_speaker_notes
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving slide data: {str(e)}")
