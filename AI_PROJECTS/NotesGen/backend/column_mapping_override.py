# SQLAlchemy column mapping override
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

# Force correct column mapping
class SlideImageOverride:
    """Override to ensure correct column mapping."""
    
    @staticmethod
    def ensure_correct_mapping():
        """Ensure that image_format column is properly mapped."""
        from app.models.models import SlideImage
        
        # Force the correct column attribute mapping
        if hasattr(SlideImage, 'format'):
            # Remove the incorrect attribute if it exists
            delattr(SlideImage, 'format')
        
        # Ensure image_format is properly mapped
        if not hasattr(SlideImage, 'image_format'):
            raise Exception("SlideImage.image_format column is missing!")
        
        # Verify the column name in the table definition
        image_format_col = None
        for col in SlideImage.__table__.columns:
            if col.name == 'image_format':
                image_format_col = col
                break
        
        if not image_format_col:
            raise Exception("image_format column not found in table definition!")
        
        # Force SQLAlchemy to use the correct column mapping
        SlideImage.image_format.property.columns = [image_format_col]
        
        print(f"✅ Column mapping verified: {SlideImage.image_format.property.columns[0].name}")
        return True

# Apply the override function
def apply_column_override():
    try:
        override = SlideImageOverride()
        return override.ensure_correct_mapping()
    except Exception as e:
        print(f"❌ Column override failed: {e}")
        return False
