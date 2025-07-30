
def validate_and_fix_cache_runtime():
    """Runtime cache validation and fix."""
    import logging
    from app.db.database import SessionLocal
    from app.models.models import SlideImage
    
    logger = logging.getLogger(__name__)
    
    try:
        db = SessionLocal()
        
        # Test query with detailed logging
        logger.info("🔍 CACHE VALIDATOR: Testing slide image query")
        
        slide_image = db.query(SlideImage).filter(
            SlideImage.ppt_file_id == 1,
            SlideImage.slide_number == 1
        ).first()
        
        if slide_image:
            logger.info(f"✅ CACHE VALIDATOR: Query successful - {slide_image.image_format}")
            return True
        else:
            logger.warning("⚠️ CACHE VALIDATOR: No slide found")
            return False
            
    except Exception as e:
        logger.error(f"❌ CACHE VALIDATOR: Query failed - {e}")
        return False
    finally:
        db.close()
