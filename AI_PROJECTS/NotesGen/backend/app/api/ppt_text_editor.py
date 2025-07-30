"""
API endpoints for PowerPoint text extraction and editing.
"""

import logging
import os
import json
import tempfile
import time
import datetime
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Response
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..models.models import PPTFile, PPTTextCache
from ..utils.ppt_text_extractor import PPTTextExtractor, SlideTextStructure, TextElement, SpeakerNotesSection
from ..utils.tracking_utils import generate_tracking_id, format_tracking_log

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ppt-text-editor", tags=["ppt-text-editor"])

def resolve_ppt_file(ppt_identifier: str, db: Session) -> PPTFile:
    """
    Resolve a PPT file from either tracking_id or numeric ID.
    
    Args:
        ppt_identifier: Either a tracking_id (string) or numeric ID (as string)
        db: Database session
        
    Returns:
        PPTFile object
        
    Raises:
        HTTPException: If PPT file not found
    """
    # First try as tracking ID (preferred)
    ppt_file = db.query(PPTFile).filter(PPTFile.tracking_id == ppt_identifier).first()
    
    # If not found and identifier looks numeric, try as numeric ID (backward compatibility)
    if not ppt_file and ppt_identifier.isdigit():
        ppt_file = db.query(PPTFile).filter(PPTFile.id == int(ppt_identifier)).first()
        if ppt_file:
            logger.warning(f"⚠️ DEPRECATED: Using dangerous numeric ID {ppt_identifier} - should use tracking_id: {ppt_file.tracking_id}")
    
    if not ppt_file:
        raise HTTPException(status_code=404, detail=f"PPT file not found for identifier: {ppt_identifier}")
    
    return ppt_file

@router.get("/extract/{ppt_identifier}")
async def extract_text_elements(ppt_identifier: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Extract all editable text elements from a PowerPoint file with intelligent caching."""
    
    logger.info(f"🔍 Starting text extraction for PPT {ppt_identifier}")
    
    # Resolve PPT file from tracking_id or numeric ID
    ppt_file = resolve_ppt_file(ppt_identifier, db)
    ppt_file_id = ppt_file.id
    
    logger.info(f"📁 Found PPT file: {ppt_file.filename} (path: {ppt_file.path})")
    logger.info(f"💾 Text cached status: {ppt_file.text_cached}")
    
    # **CACHING LOGIC**: Check if text elements are already cached
    if ppt_file.text_cached and ppt_file.text_cache:
        logger.info(f"✅ Text elements already cached for PPT {ppt_file_id}, returning cached data")
        
        try:
            cached_data = json.loads(ppt_file.text_cache.text_elements_data)
            logger.info(f"📊 Cached data loaded: {len(cached_data.get('slides', []))} slides, {cached_data.get('total_text_elements', 0)} text elements")
            
            # Add metadata
            cached_data.update({
                "ppt_file_id": ppt_file_id,
                "filename": ppt_file.filename,
                "cached": True,
                "cache_timestamp": ppt_file.text_cache.updated_at.isoformat() if ppt_file.text_cache.updated_at else None
            })
            
            return cached_data
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load cached text data, will reprocess: {e}")
            # Continue with normal processing if cache is corrupted
    
    file_path = ppt_file.path
    if not os.path.exists(file_path):
        logger.error(f"❌ PPT file not found on disk: {file_path}")
        raise HTTPException(status_code=404, detail="PPT file not found on disk")
    
    # Check file modification time for cache invalidation
    file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
    logger.info(f"📅 File modification time: {file_mtime}")
    
    if ppt_file.text_cache and ppt_file.last_modified and file_mtime > ppt_file.last_modified:
        logger.info(f"🔄 File modified since last text cache, clearing old data for PPT {ppt_file_id}")
        # Clear old cached text
        if ppt_file.text_cache:
            db.delete(ppt_file.text_cache)
        ppt_file.text_cached = False
        db.commit()

    try:
        logger.info(f"🔄 Processing text elements for PPT {ppt_file_id} (file: {ppt_file.filename})")
        logger.info(f"📍 File path: {file_path}")
        
        extractor = PPTTextExtractor()
        logger.info(f"🏗️ Created PPTTextExtractor instance")
        
        slides_structure = extractor.extract_all_text_elements(file_path)
        logger.info(f"✅ Text extraction completed: {len(slides_structure)} slides processed")
        
        # Convert to serializable format
        result = {
            "ppt_file_id": ppt_file_id,
            "filename": ppt_file.filename,
            "total_slides": len(slides_structure),
            "cached": False,
            "slides": []
        }
        
        total_text_elements = 0
        
        for slide_structure in slides_structure:
            logger.info(f"📄 Processing slide {slide_structure.slide_number}: {slide_structure.total_text_elements} text elements")
            
            slide_data = {
                "slide_number": slide_structure.slide_number,
                "total_text_elements": slide_structure.total_text_elements,
                "has_speaker_notes": slide_structure.has_speaker_notes,
                "has_alt_text": slide_structure.has_alt_text,
                "text_elements": [],
                "speaker_notes_sections": []
            }
            
            # Add text elements
            for text_element in slide_structure.text_elements:
                slide_data["text_elements"].append({
                    "element_id": text_element.element_id,
                    "element_type": text_element.element_type,
                    "text_content": text_element.text_content,
                    "original_text": text_element.original_text,
                    "shape_name": text_element.shape_name,
                    "shape_id": text_element.shape_id,
                    "placeholder_type": text_element.placeholder_type,
                    "is_title": text_element.is_title,
                    "is_content": text_element.is_content,
                    "position": text_element.position,
                    "formatting": text_element.formatting
                })
                total_text_elements += 1
            
            # Add speaker notes sections
            for section in slide_structure.speaker_notes_sections:
                slide_data["speaker_notes_sections"].append({
                    "section_type": section.section_type,
                    "content": section.content,
                    "original_content": section.original_content,
                    "paragraph_index": section.paragraph_index
                })
            
            result["slides"].append(slide_data)
        
        logger.info(f"📊 Final result: {total_text_elements} total text elements across {len(slides_structure)} slides")
        
        # **CACHE THE RESULTS**: Save extracted text to database
        try:
            logger.info(f"💾 Attempting to cache text elements to database...")
            
            # Create or update text cache
            if ppt_file.text_cache:
                logger.info(f"🔄 Updating existing text cache")
                text_cache = ppt_file.text_cache
                text_cache.text_elements_data = json.dumps(result)
                text_cache.total_slides = len(slides_structure)
                text_cache.total_text_elements = total_text_elements
                text_cache.updated_at = datetime.datetime.utcnow()
            else:
                logger.info(f"🆕 Creating new text cache entry")
                text_cache = PPTTextCache(
                    ppt_file_id=ppt_file_id,
                    text_elements_data=json.dumps(result),
                    total_slides=len(slides_structure),
                    total_text_elements=total_text_elements
                )
                db.add(text_cache)
            
            # Mark PPT file as text cached
            ppt_file.text_cached = True
            ppt_file.last_modified = file_mtime
            
            db.commit()
            logger.info(f"✅ Successfully cached text elements for PPT {ppt_file_id}: {total_text_elements} elements across {len(slides_structure)} slides")
            
        except Exception as cache_error:
            logger.error(f"❌ Failed to cache text elements: {cache_error}")
            # Continue even if caching fails
        
        logger.info(f"🎉 Text extraction completed successfully for PPT {ppt_file_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error extracting text elements for PPT {ppt_file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting text elements: {str(e)}")

@router.get("/extract/{ppt_identifier}/slide/{slide_number}")
async def extract_slide_text_elements(
    ppt_identifier: str, 
    slide_number: int, 
    response: Response,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Extract text elements from a specific slide in a PowerPoint file."""
    
    # Resolve PPT file from tracking_id or numeric ID  
    ppt_file = resolve_ppt_file(ppt_identifier, db)
    ppt_file_id = ppt_file.id
    
    # Add comprehensive cache control headers to prevent stale data issues
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["ETag"] = f"slide-{ppt_file_id}-{slide_number}-{int(time.time())}"
    response.headers["Last-Modified"] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # Generate meaningful tracking ID for this operation
    tracking_id = generate_tracking_id(ppt_file.filename, "EXTRACT", slide_number)
    
    # Add file modification time tracking for cache invalidation
    try:
        if os.path.exists(ppt_file.path):
            file_mtime = os.path.getmtime(ppt_file.path)
            response.headers["X-File-Modified"] = str(file_mtime)
            logger.info(format_tracking_log(tracking_id, f"PPT file modified at: {file_mtime}", "INFO"))
    except Exception as e:
        logger.warning(format_tracking_log(tracking_id, f"Could not get file modification time: {e}", "WARNING"))
    
    logger.info(format_tracking_log(tracking_id, "Starting slide extraction", "INFO"))
    
    file_path = ppt_file.path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PPT file not found on disk")
    
    logger.info(format_tracking_log(tracking_id, f"PPT file path: {file_path}", "INFO"))
    logger.info(format_tracking_log(tracking_id, f"Text cached status: {ppt_file.text_cached}", "INFO"))
    
    # **ALWAYS FORCE FRESH EXTRACTION** - No cache for individual slide requests to ensure fresh data
    logger.info(format_tracking_log(tracking_id, "FORCING FRESH EXTRACTION from PPT file", "INFO"))
    logger.info(format_tracking_log(tracking_id, "This ensures updated speaker notes are always loaded from the actual PPT file", "INFO"))
    
    try:
        logger.info(format_tracking_log(tracking_id, f"Extracting text elements from slide {slide_number} only", "INFO"))
        
        extractor = PPTTextExtractor()
        
        # PERFORMANCE FIX: Extract only the specific slide instead of all slides
        try:
            target_slide = extractor.extract_single_slide_text_elements(file_path, slide_number)
            logger.info(format_tracking_log(tracking_id, f"Successfully extracted slide {slide_number} with {target_slide.total_text_elements} text elements", "INFO"))
        except ValueError as ve:
            logger.error(format_tracking_log(tracking_id, f"Slide {slide_number} not found: {ve}", "ERROR"))
            raise HTTPException(status_code=404, detail=str(ve))
        
        # Convert to serializable format
        slide_data = {
            "slide_number": target_slide.slide_number,
            "total_text_elements": target_slide.total_text_elements,
            "has_speaker_notes": target_slide.has_speaker_notes,
            "has_alt_text": target_slide.has_alt_text,
            "text_elements": [],
            "speaker_notes_sections": []
        }
        
        # Add text elements
        for text_element in target_slide.text_elements:
            slide_data["text_elements"].append({
                "element_id": text_element.element_id,
                "element_type": text_element.element_type,
                "text_content": text_element.text_content,
                "original_text": text_element.original_text,
                "shape_name": text_element.shape_name,
                "shape_id": text_element.shape_id,
                "placeholder_type": text_element.placeholder_type,
                "is_title": text_element.is_title,
                "is_content": text_element.is_content,
                "position": text_element.position,
                "formatting": text_element.formatting
            })
        
        # Add speaker notes sections
        for section in target_slide.speaker_notes_sections:
            slide_data["speaker_notes_sections"].append({
                "section_type": section.section_type,
                "content": section.content,
                "original_content": section.original_content,
                "paragraph_index": section.paragraph_index
            })
        
        result = {
            "ppt_file_id": ppt_file_id,
            "filename": ppt_file.filename,
            "slide_number": slide_number,
            "cached": False,
            "slide_data": slide_data
        }
        
        logger.info(format_tracking_log(tracking_id, f"Successfully extracted {target_slide.total_text_elements} text elements from slide", "SUCCESS"))
        
        return result
        
    except Exception as e:
        logger.error(format_tracking_log(tracking_id, f"Error extracting slide text elements: {str(e)}", "ERROR"))
        raise HTTPException(status_code=500, detail=f"Error extracting slide text elements: {str(e)}")

def _convert_html_to_plain_text(html_content: str, prefix: str = "") -> str:
    """Convert HTML content to clean instructor deck style text."""
    import re
    
    if not html_content or not html_content.strip():
        return ""
    
    # Clean up the HTML content first
    clean_content = html_content.strip()
    
    # For bullet points (instructor notes) - match instructor deck style
    if prefix == "• ":
        lines = []
        
        # Extract all <li> content
        li_pattern = r'<li[^>]*>(.*?)</li>'
        li_matches = re.findall(li_pattern, clean_content, re.DOTALL | re.IGNORECASE)
        
        for content in li_matches:
            # Clean the content of HTML tags
            clean_line = re.sub(r'<[^>]+>', '', content).strip()
            clean_line = re.sub(r'\s+', ' ', clean_line)  # Normalize whitespace
            if clean_line:
                lines.append(f"• {clean_line}")
        
        # Handle non-list paragraphs (add as plain lines)
        no_lists = re.sub(r'<[uo]l[^>]*>.*?</[uo]l>', '', clean_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Extract paragraph content
        p_pattern = r'<p[^>]*>(.*?)</p>'
        p_matches = re.findall(p_pattern, no_lists, re.DOTALL | re.IGNORECASE)
        
        for content in p_matches:
            clean_line = re.sub(r'<[^>]+>', '', content).strip()
            clean_line = re.sub(r'\s+', ' ', clean_line)
            if clean_line:
                lines.append(clean_line)
        
        # If no structured content found, just clean the entire content
        if not lines:
            clean_line = re.sub(r'<[^>]+>', '', clean_content).strip()
            clean_line = re.sub(r'\s+', ' ', clean_line)
            if clean_line:
                lines.append(clean_line)
        
        return '\n'.join(lines)
    
    else:
        # For student notes and other content - clean paragraph style like instructor deck
        
        # Remove bold/strong formatting but keep content
        clean_content = re.sub(r'<(strong|b)[^>]*>(.*?)</\1>', r'\2', clean_content, flags=re.IGNORECASE)
        
        # Remove italic/emphasis formatting but keep content  
        clean_content = re.sub(r'<(em|i)[^>]*>(.*?)</\1>', r'\2', clean_content, flags=re.IGNORECASE)
        
        # Convert lists to simple bullet points
        li_pattern = r'<li[^>]*>(.*?)</li>'
        li_matches = re.findall(li_pattern, clean_content, re.DOTALL | re.IGNORECASE)
        
        # Replace lists with bullet points
        for content in li_matches:
            clean_line = re.sub(r'<[^>]+>', '', content).strip()
            clean_line = re.sub(r'\s+', ' ', clean_line)
            bullet_point = f"• {clean_line}"
            clean_content = clean_content.replace(f"<li>{content}</li>", bullet_point, 1)
        
        # Remove list container tags
        clean_content = re.sub(r'</?[uo]l[^>]*>', '', clean_content, flags=re.IGNORECASE)
        
        # Convert paragraphs to line breaks (instructor deck style)
        clean_content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', clean_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert line breaks
        clean_content = re.sub(r'<br[^>]*>', '\n', clean_content, flags=re.IGNORECASE)
        
        # Remove any remaining HTML tags
        clean_content = re.sub(r'<[^>]+>', '', clean_content)
        
        # Clean up whitespace to match instructor deck style
        clean_content = re.sub(r'\n\n\n+', '\n\n', clean_content)  # Max 2 consecutive newlines
        clean_content = re.sub(r'[ \t]+', ' ', clean_content)  # Normalize spaces and tabs
        clean_content = re.sub(r'\n +', '\n', clean_content)  # Remove leading spaces on lines
        clean_content = clean_content.strip()
        
        return clean_content

def _convert_html_to_plain_text_for_powerpoint(html_content: str) -> str:
    """Convert HTML content to clean plain text optimized for PowerPoint display."""
    import re
    
    if not html_content or not html_content.strip():
        return ""
    
    content = html_content.strip()
    
    # Convert links to clean format for PowerPoint
    link_pattern = r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
    def replace_link(match):
        url = match.group(1).strip()
        text = match.group(2).strip()
        if text and url:
            return f"{text} ({url})"
        elif url:
            return url
        else:
            return text or ""
    
    content = re.sub(link_pattern, replace_link, content, flags=re.IGNORECASE)
    
    # Convert line breaks
    content = re.sub(r'<br[^>]*/?>', '\n', content, flags=re.IGNORECASE)
    
    # Convert lists to clean bullet points for PowerPoint
    content = re.sub(r'<ul[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</ul>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<ol[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</ol>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<li[^>]*>', '• ', content, flags=re.IGNORECASE)
    content = re.sub(r'</li>', '\n', content, flags=re.IGNORECASE)
    
    # Convert paragraphs to clean formatting
    content = re.sub(r'<p[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</p>', '\n\n', content, flags=re.IGNORECASE)
    
    # Remove bold/italic formatting but keep content
    content = re.sub(r'<(strong|b)[^>]*>(.*?)</\1>', r'\2', content, flags=re.IGNORECASE)
    content = re.sub(r'<(em|i)[^>]*>(.*?)</\1>', r'\2', content, flags=re.IGNORECASE)
    
    # Remove any remaining HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    
    # Clean up whitespace for PowerPoint
    content = re.sub(r'\n\n\n+', '\n\n', content)  # Max 2 consecutive newlines
    content = re.sub(r'[ \t]+', ' ', content)  # Normalize spaces
    content = re.sub(r'\n +', '\n', content)  # Remove leading spaces on lines
    content = re.sub(r' +\n', '\n', content)  # Remove trailing spaces on lines
    
    return content.strip()

@router.post("/save-speaker-notes/{ppt_identifier}/slide/{slide_number}")
async def save_slide_speaker_notes(
    ppt_identifier: str,
    slide_number: int,
    speaker_notes_content: Dict[str, str],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Save structured speaker notes to a specific slide in the PowerPoint file."""
    
    # Resolve PPT file from tracking_id or numeric ID
    ppt_file = resolve_ppt_file(ppt_identifier, db)
    ppt_file_id = ppt_file.id
    
    # Generate meaningful tracking ID for this save operation
    tracking_id = generate_tracking_id(ppt_file.filename, "SAVE", slide_number)
    
    logger.info(format_tracking_log(tracking_id, "Starting speaker notes save operation", "INFO"))
    
    file_path = ppt_file.path
    if not os.path.exists(file_path):
        logger.error(format_tracking_log(tracking_id, f"PPT file not found on disk: {file_path}", "ERROR"))
        raise HTTPException(status_code=404, detail="PPT file not found on disk")
    
    try:
        # Format speaker notes preserving HTML formatting for proper PowerPoint XML generation
        formatted_content = ""
        
        # References section - preserve HTML for proper PowerPoint formatting
        if speaker_notes_content.get("references", "").strip():
            references = speaker_notes_content['references'].strip()
            formatted_content += f"References:\n{references}\n\n"
        
        # Developer Notes section - preserve HTML formatting
        if speaker_notes_content.get("developerNotes", "").strip():
            developer_notes = speaker_notes_content['developerNotes'].strip()
            formatted_content += f"Developer Notes:\n{developer_notes}\n\n"
        
        # Script section - preserve HTML formatting
        if speaker_notes_content.get("script", "").strip():
            script_content = speaker_notes_content['script'].strip()
            formatted_content += f"Script:\n{script_content}\n\n"
        
        # Instructor Notes section - preserve HTML formatting
        if speaker_notes_content.get("instructorNotes", "").strip():
            instructor_notes = speaker_notes_content['instructorNotes'].strip()
            formatted_content += f"Instructornotes:\n{instructor_notes}\n\n"
        
        # Student Notes section - preserve HTML formatting
        if speaker_notes_content.get("studentNotes", "").strip():
            student_notes = speaker_notes_content['studentNotes'].strip()
            formatted_content += f"Studentnotes:\n{student_notes}\n\n"
        
        # Alt Text section (if present) - preserve HTML formatting
        if speaker_notes_content.get("altText", "").strip():
            alt_text = speaker_notes_content['altText'].strip()
            formatted_content += f"Alt Text:\n{alt_text}\n\n"
        
        # Slide Description section (if present) - preserve HTML formatting
        if speaker_notes_content.get("slideDescription", "").strip():
            slide_desc = speaker_notes_content['slideDescription'].strip()
            formatted_content += f"Slide Description:\n{slide_desc}\n\n"
        
        formatted_content = formatted_content.strip()
        
        logger.info(format_tracking_log(tracking_id, f"Formatted speaker notes content: {len(formatted_content)} characters", "INFO"))
        logger.info(format_tracking_log(tracking_id, f"Content preview: {formatted_content[:500]}...", "DEBUG"))
        
        # Debug: Check if content contains HTML
        import re
        has_html = bool(re.search(r'<[^>]+>', formatted_content))
        logger.info(format_tracking_log(tracking_id, f"Content contains HTML tags: {has_html}", "DEBUG"))
        
        # Use PPTTextExtractor to save the speaker notes
        extractor = PPTTextExtractor()
        success = extractor.save_speaker_notes_to_slide(file_path, slide_number, formatted_content)
        
        if success:
            logger.info(format_tracking_log(tracking_id, "Successfully saved speaker notes to PPT file", "SUCCESS"))
            
            # **UPDATE DATABASE**: Update the PPTSlide table with new AI content
            try:
                logger.info(format_tracking_log(tracking_id, "Updating database with new AI content", "INFO"))
                
                # Find or create slide record in database
                from app.models.models import PPTSlide
                slide = db.query(PPTSlide).filter(
                    PPTSlide.ppt_file_id == ppt_file_id,
                    PPTSlide.slide_number == slide_number
                ).first()
                
                if not slide:
                    # Create new slide record
                    slide = PPTSlide(
                        ppt_file_id=ppt_file_id,
                        slide_number=slide_number,
                        title="",
                        content=""
                    )
                    db.add(slide)
                
                # Update AI-generated fields with new content
                slide.ai_developer_notes = speaker_notes_content.get("developerNotes", "")
                slide.ai_alt_text = speaker_notes_content.get("altText", "")
                slide.ai_slide_description = speaker_notes_content.get("slideDescription", "")
                slide.ai_script = speaker_notes_content.get("script", "")
                slide.ai_instructor_notes = speaker_notes_content.get("instructorNotes", "")
                slide.ai_student_notes = speaker_notes_content.get("studentNotes", "")
                slide.ai_references = speaker_notes_content.get("references", "")
                slide.ai_generated = True
                slide.ai_generated_at = datetime.utcnow()
                slide.ai_model_used = "manual_edit"
                
                db.commit()
                logger.info(format_tracking_log(tracking_id, "Successfully updated database with new AI content", "SUCCESS"))
                
            except Exception as db_error:
                logger.error(format_tracking_log(tracking_id, f"Failed to update database: {db_error}", "ERROR"))
                # Don't fail the whole operation if database update fails
            
            # **VERIFICATION**: Verify the save by reading back the data
            try:
                logger.info(format_tracking_log(tracking_id, "Starting save verification", "INFO"))
                verification_extractor = PPTTextExtractor()
                verification_slides = verification_extractor.extract_all_text_elements(file_path)
                
                # Find the slide we just saved to
                verification_slide = None
                for slide_structure in verification_slides:
                    if slide_structure.slide_number == slide_number:
                        verification_slide = slide_structure
                        break
                
                if verification_slide and verification_slide.speaker_notes_sections:
                    total_content = ''.join([section.content for section in verification_slide.speaker_notes_sections])
                    logger.info(format_tracking_log(tracking_id, f"Save verification successful: {len(verification_slide.speaker_notes_sections)} sections, {len(total_content)} characters", "SUCCESS"))
                    logger.info(format_tracking_log(tracking_id, f"Content preview: {total_content[:200]}...", "DEBUG"))
                else:
                    logger.warning(format_tracking_log(tracking_id, "Save verification failed: No speaker notes found when reading back", "WARNING"))
                    
            except Exception as verification_error:
                logger.error(format_tracking_log(tracking_id, f"Save verification failed: {verification_error}", "ERROR"))
            
            # Invalidate text cache since we modified the file
            if ppt_file.text_cached:
                logger.info(format_tracking_log(tracking_id, "Invalidating text cache due to file modification", "INFO"))
                if ppt_file.text_cache:
                    db.delete(ppt_file.text_cache)
                ppt_file.text_cached = False
                db.commit()
            
            return {
                "success": True,
                "message": f"Speaker notes saved successfully to slide {slide_number}",
                "slide_number": slide_number,
                "content_length": len(formatted_content),
                "tracking_id": tracking_id
            }
        else:
            logger.error(format_tracking_log(tracking_id, "Failed to save speaker notes to PowerPoint file", "ERROR"))
            raise HTTPException(status_code=500, detail="Failed to save speaker notes to PowerPoint file")
        
    except Exception as e:
        logger.error(format_tracking_log(tracking_id, f"Error saving speaker notes: {str(e)}", "ERROR"))
        raise HTTPException(status_code=500, detail=f"Error saving speaker notes: {str(e)}")

@router.post("/save/{ppt_identifier}")
async def save_modified_text_elements(
    ppt_identifier: str, 
    modified_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Save modified text elements back to the PowerPoint file."""
    
    # Resolve PPT file from tracking_id or numeric ID
    ppt_file = resolve_ppt_file(ppt_identifier, db)
    ppt_file_id = ppt_file.id
    
    original_file_path = ppt_file.path
    if not os.path.exists(original_file_path):
        raise HTTPException(status_code=404, detail="PPT file not found on disk")
    
    try:
        # Convert modified data back to SlideTextStructure objects
        modified_slides = []
        
        for slide_data in modified_data.get("slides", []):
            # Reconstruct text elements
            text_elements = []
            for elem_data in slide_data.get("text_elements", []):
                text_element = TextElement(
                    element_id=elem_data["element_id"],
                    element_type=elem_data["element_type"],
                    slide_number=slide_data["slide_number"],
                    text_content=elem_data["text_content"],
                    original_text=elem_data["original_text"],
                    shape_name=elem_data.get("shape_name"),
                    shape_id=elem_data.get("shape_id"),
                    xpath_location=elem_data.get("xpath_location"),
                    xml_file_path=f'ppt/slides/slide{slide_data["slide_number"]}.xml',
                    placeholder_type=elem_data.get("placeholder_type"),
                    is_title=elem_data.get("is_title", False),
                    is_content=elem_data.get("is_content", False),
                    paragraph_index=elem_data.get("paragraph_index"),
                    run_index=elem_data.get("run_index"),
                    position=elem_data.get("position"),
                    formatting=elem_data.get("formatting")
                )
                text_elements.append(text_element)
            
            # Reconstruct speaker notes sections
            speaker_notes_sections = []
            for section_data in slide_data.get("speaker_notes_sections", []):
                section = SpeakerNotesSection(
                    section_type=section_data["section_type"],
                    content=section_data["content"],
                    original_content=section_data["original_content"],
                    paragraph_index=section_data["paragraph_index"]
                )
                speaker_notes_sections.append(section)
            
            # Create slide structure
            slide_structure = SlideTextStructure(
                slide_number=slide_data["slide_number"],
                slide_xml_path=f'ppt/slides/slide{slide_data["slide_number"]}.xml',
                notes_xml_path=f'ppt/notesSlides/notesSlide{slide_data["slide_number"]}.xml' if slide_data.get("has_speaker_notes") else None,
                text_elements=text_elements,
                speaker_notes_sections=speaker_notes_sections,
                total_text_elements=len(text_elements),
                has_speaker_notes=len(speaker_notes_sections) > 0,
                has_alt_text=any(elem.element_type == 'alt_text' for elem in text_elements)
            )
            
            modified_slides.append(slide_structure)
        
        # Generate output file path
        original_path = Path(original_file_path)
        output_filename = f"{original_path.stem}_edited{original_path.suffix}"
        output_path = original_path.parent / output_filename
        
        # Save modified file
        extractor = PPTTextExtractor()
        success = extractor.save_modified_text_elements(
            original_file_path, 
            modified_slides, 
            str(output_path)
        )
        
        if success:
            # Create new database entry for the modified file
            new_ppt_file = PPTFile(
                filename=output_filename,
                path=str(output_path),
                size=os.path.getsize(output_path)
            )
            db.add(new_ppt_file)
            db.commit()
            db.refresh(new_ppt_file)
            
            return {
                "success": True,
                "message": "PPT file saved successfully",
                "original_file_id": ppt_file_id,
                "new_file_id": new_ppt_file.id,
                "new_filename": output_filename,
                "output_path": str(output_path)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save modified PPT file")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving modified text elements: {str(e)}")

@router.get("/structure/{ppt_identifier}")
async def get_text_structure_summary(ppt_identifier: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get a summary of the text structure for a PowerPoint file."""
    
    # Resolve PPT file from tracking_id or numeric ID
    ppt_file = resolve_ppt_file(ppt_identifier, db)
    ppt_file_id = ppt_file.id
    
    file_path = ppt_file.path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PPT file not found on disk")
    
    try:
        extractor = PPTTextExtractor()
        slides_structure = extractor.extract_all_text_elements(file_path)
        
        # Generate summary
        total_text_elements = sum(slide.total_text_elements for slide in slides_structure)
        slides_with_speaker_notes = sum(1 for slide in slides_structure if slide.has_speaker_notes)
        slides_with_alt_text = sum(1 for slide in slides_structure if slide.has_alt_text)
        
        # Count by element type
        element_type_counts = {}
        for slide in slides_structure:
            for element in slide.text_elements:
                element_type_counts[element.element_type] = element_type_counts.get(element.element_type, 0) + 1
        
        # Count speaker notes sections by type
        speaker_notes_type_counts = {}
        for slide in slides_structure:
            for section in slide.speaker_notes_sections:
                speaker_notes_type_counts[section.section_type] = speaker_notes_type_counts.get(section.section_type, 0) + 1
        
        return {
            "ppt_file_id": ppt_file_id,
            "filename": ppt_file.filename,
            "total_slides": len(slides_structure),
            "total_text_elements": total_text_elements,
            "slides_with_speaker_notes": slides_with_speaker_notes,
            "slides_with_alt_text": slides_with_alt_text,
            "element_type_counts": element_type_counts,
            "speaker_notes_type_counts": speaker_notes_type_counts,
            "slide_summaries": [
                {
                    "slide_number": slide.slide_number,
                    "text_elements_count": slide.total_text_elements,
                    "has_speaker_notes": slide.has_speaker_notes,
                    "has_alt_text": slide.has_alt_text,
                    "element_types": list(set(elem.element_type for elem in slide.text_elements)),
                    "speaker_notes_types": list(set(section.section_type for section in slide.speaker_notes_sections))
                }
                for slide in slides_structure
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting text structure: {str(e)}")

@router.post("/validate-changes")
async def validate_text_changes(changes_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate text changes before saving."""
    
    try:
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "summary": {}
        }
        
        total_changes = 0
        changes_by_type = {}
        
        for slide_data in changes_data.get("slides", []):
            slide_number = slide_data.get("slide_number")
            
            # Validate text elements
            for elem_data in slide_data.get("text_elements", []):
                original_text = elem_data.get("original_text", "")
                new_text = elem_data.get("text_content", "")
                
                if original_text != new_text:
                    total_changes += 1
                    element_type = elem_data.get("element_type", "unknown")
                    changes_by_type[element_type] = changes_by_type.get(element_type, 0) + 1
                    
                    # Validation rules
                    if element_type == "alt_text" and len(new_text.strip()) == 0:
                        validation_results["warnings"].append(
                            f"Slide {slide_number}: Alt text for {elem_data.get('shape_name', 'image')} is empty"
                        )
                    
                    if len(new_text) > 1000:  # Arbitrary limit
                        validation_results["warnings"].append(
                            f"Slide {slide_number}: Text in {elem_data.get('shape_name', 'element')} is very long ({len(new_text)} characters)"
                        )
            
            # Validate speaker notes
            for section_data in slide_data.get("speaker_notes_sections", []):
                original_content = section_data.get("original_content", "")
                new_content = section_data.get("content", "")
                
                if original_content != new_content:
                    total_changes += 1
                    section_type = section_data.get("section_type", "general")
                    changes_by_type[f"speaker_notes_{section_type}"] = changes_by_type.get(f"speaker_notes_{section_type}", 0) + 1
        
        validation_results["summary"] = {
            "total_changes": total_changes,
            "changes_by_type": changes_by_type
        }
        
        # Check if there are any errors that would prevent saving
        if len(validation_results["errors"]) > 0:
            validation_results["valid"] = False
        
        return validation_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating changes: {str(e)}") 