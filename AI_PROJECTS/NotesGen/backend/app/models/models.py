from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, LargeBinary, Text, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

# CRITICAL NOTE: Database Migration from SQLite to PostgreSQL
# =============================================================
# This application has been migrated from SQLite to PostgreSQL to resolve:
# 1. Concurrency issues causing "Server unavailable" errors
# 2. Performance problems with large PPT files (40+ slides)
# 3. Database locking during heavy image processing
# 4. Column mapping issues (sqlite: 'format' vs postgres: 'image_format')
# 
# ALL MODELS ARE NOW OPTIMIZED FOR POSTGRESQL ONLY
# DO NOT REVERT TO SQLITE - IT WILL CAUSE SYSTEM FAILURES

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)  # PostgreSQL: explicit length
    hashed_password = Column(String(255))
    home_directory = Column(String(512))  # PostgreSQL: explicit length for file paths
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ppt_files = relationship("PPTFile", back_populates="user")

class PPTFile(Base):
    __tablename__ = "ppt_files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)  # PostgreSQL: indexed for joins
    filename = Column(String(512))  # PostgreSQL: explicit length for long filenames
    path = Column(String(1024))  # PostgreSQL: explicit length for full paths
    size = Column(Integer)  # in bytes
    created_at = Column(DateTime, default=datetime.utcnow, index=True)  # PostgreSQL: indexed for sorting
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Robust tracking identifier for handling many similar files  
    tracking_id = Column(String(255), index=True, nullable=True)  # Format: filename_YYYYMMDD_HHMMSS_sizeMB_hash
    
    # Cache tracking - PostgreSQL optimized
    images_cached = Column(Boolean, default=False, index=True)  # PostgreSQL: indexed for filtering
    text_cached = Column(Boolean, default=False, index=True)    # PostgreSQL: indexed for filtering
    last_modified = Column(DateTime, default=datetime.utcnow, index=True)  # PostgreSQL: indexed for cache invalidation
    content_hash = Column(String(64), index=True, unique=False, nullable=True)  # PostgreSQL: SHA-256 hash length

    # Relationships
    user = relationship("User", back_populates="ppt_files")
    note_versions = relationship("NoteVersion", back_populates="ppt_file", cascade="all, delete-orphan")
    slide_images = relationship("SlideImage", back_populates="ppt_file", cascade="all, delete-orphan")
    slides = relationship("PPTSlide", back_populates="ppt_file", cascade="all, delete-orphan")
    analysis = relationship("PPTAnalysis", back_populates="ppt_file", uselist=False, cascade="all, delete-orphan")
    text_cache = relationship("PPTTextCache", back_populates="ppt_file", uselist=False, cascade="all, delete-orphan")
    bulk_jobs = relationship("BulkGenerationJob", back_populates="ppt_file", cascade="all, delete-orphan")

    # PostgreSQL: Composite index for common queries
    __table_args__ = (
        Index('idx_ppt_files_user_created', 'user_id', 'created_at'),
        Index('idx_ppt_files_cache_status', 'images_cached', 'text_cached'),
    )
    
    @staticmethod
    def generate_tracking_id(filename: str, file_size: int, created_at: datetime = None, content_hash: str = None) -> str:
        """
        Generate a robust tracking ID for PPT files.
        Format: {clean_filename}_{YYYYMMDD_HHMMSS}_{sizeMB}_{hash_prefix}
        Example: "MLModelApproach_20250624_142337_4MB_A1B2C3D4"
        """
        import re
        from hashlib import md5
        
        # Use current time if not provided
        if created_at is None:
            created_at = datetime.utcnow()
        
        # Clean filename: remove extension and special characters
        base_filename = filename.rsplit('.', 1)[0] if '.' in filename else filename
        clean_filename = re.sub(r'[^\w\-_]', '_', base_filename)
        clean_filename = re.sub(r'_{2,}', '_', clean_filename)  # Replace multiple underscores
        clean_filename = clean_filename[:50]  # Limit length
        
        # Format timestamp
        timestamp = created_at.strftime('%Y%m%d_%H%M%S')
        
        # Format file size in MB
        size_mb = max(1, file_size // (1024 * 1024))  # At least 1MB
        size_str = f"{size_mb}MB"
        
        # Generate hash prefix (first 8 chars of content_hash or filename hash)
        if content_hash and len(content_hash) >= 8:
            hash_prefix = content_hash[:8].upper()
        else:
            # Fallback: hash the filename + size
            hash_input = f"{filename}_{file_size}_{timestamp}"
            hash_prefix = md5(hash_input.encode()).hexdigest()[:8].upper()
        
        return f"{clean_filename}_{timestamp}_{size_str}_{hash_prefix}"

class NoteVersion(Base):
    __tablename__ = "note_versions"

    id = Column(Integer, primary_key=True, index=True)
    ppt_file_id = Column(Integer, ForeignKey("ppt_files.id"), index=True)  # PostgreSQL: indexed for joins
    version_number = Column(Integer, index=True)  # PostgreSQL: indexed for ordering
    content = Column(Text)  # PostgreSQL: TEXT type for unlimited length
    ai_model = Column(String(100))  # PostgreSQL: explicit length
    ai_temperature = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    ppt_file = relationship("PPTFile", back_populates="note_versions")

    # PostgreSQL: Composite index for version queries
    __table_args__ = (
        Index('idx_note_versions_ppt_version', 'ppt_file_id', 'version_number'),
    )

class SlideImage(Base):
    __tablename__ = "slide_images"
    
    # CRITICAL: Fixed column mapping issue that was causing SQLite errors
    # PostgreSQL handles this correctly - no more 'format' vs 'image_format' issues

    id = Column(Integer, primary_key=True, index=True)
    ppt_file_id = Column(Integer, ForeignKey("ppt_files.id"), index=True)  # PostgreSQL: indexed for joins
    slide_number = Column(Integer, index=True)  # PostgreSQL: indexed for ordering
    image_data = Column(LargeBinary)  # PostgreSQL: BYTEA type for binary data
    thumbnail_data = Column(LargeBinary, nullable=True)  # PostgreSQL: BYTEA type
    width = Column(Integer)
    height = Column(Integer)
    image_format = Column(String(10), default="PNG")  # PostgreSQL: explicit length, FIXED COLUMN NAME
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    ppt_file = relationship("PPTFile", back_populates="slide_images")

    # PostgreSQL: Composite indexes for performance
    __table_args__ = (
        Index('idx_slide_images_ppt_slide', 'ppt_file_id', 'slide_number'),
        Index('idx_slide_images_ppt_created', 'ppt_file_id', 'created_at'),
    )

class PPTTextCache(Base):
    __tablename__ = "ppt_text_cache"

    id = Column(Integer, primary_key=True, index=True)
    ppt_file_id = Column(Integer, ForeignKey("ppt_files.id"), unique=True, index=True)  # PostgreSQL: unique constraint
    
    # Cached text data (JSON serialized) - PostgreSQL optimized
    text_elements_data = Column(Text)  # PostgreSQL: TEXT type for large JSON data
    total_slides = Column(Integer)
    total_text_elements = Column(Integer)
    
    # Cache metadata
    extraction_version = Column(String(20), default="1.0")  # PostgreSQL: explicit length
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    # Relationships
    ppt_file = relationship("PPTFile", back_populates="text_cache")

class PPTAnalysis(Base):
    __tablename__ = "ppt_analyses"

    id = Column(Integer, primary_key=True, index=True)
    ppt_file_id = Column(Integer, ForeignKey("ppt_files.id"), unique=True, index=True)  # PostgreSQL: unique constraint
    
    # Overall analysis summary
    total_slides = Column(Integer)
    total_objects = Column(Integer)
    slides_with_tab_order = Column(Integer, default=0)
    slides_with_accessibility = Column(Integer, default=0)
    total_issues = Column(Integer, default=0)
    
    # File metadata
    file_size_mb = Column(Float)
    slide_dimensions = Column(String(20))  # PostgreSQL: explicit length, e.g., "16:9", "4:3"
    has_animations = Column(Boolean, default=False, index=True)  # PostgreSQL: indexed for filtering
    has_transitions = Column(Boolean, default=False, index=True)
    has_embedded_media = Column(Boolean, default=False, index=True)
    
    # Content analysis - PostgreSQL optimized for JSON storage
    slide_layouts_used = Column(Text)  # PostgreSQL: JSON array of layout types
    theme_name = Column(String(255))
    color_scheme = Column(Text)  # PostgreSQL: JSON object
    font_usage = Column(Text)  # PostgreSQL: JSON array of fonts used
    
    # Accessibility metrics
    accessibility_score = Column(Float, index=True)  # PostgreSQL: indexed for scoring queries
    missing_alt_text_count = Column(Integer, default=0)
    color_contrast_issues = Column(Integer, default=0)
    reading_order_issues = Column(Integer, default=0)
    
    # Quality metrics
    image_quality_score = Column(Float)
    text_readability_score = Column(Float)
    design_consistency_score = Column(Float)
    
    # Performance metrics
    estimated_load_time = Column(Float)
    complexity_score = Column(Float, index=True)  # PostgreSQL: indexed for complexity queries
    
    # Detailed analysis data (JSON) - PostgreSQL handles large JSON efficiently
    slide_analyses = Column(Text)  # PostgreSQL: JSON array of per-slide analysis
    recommendations = Column(Text)  # PostgreSQL: JSON array of improvement suggestions
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    # Relationships
    ppt_file = relationship("PPTFile", back_populates="analysis")

    # PostgreSQL: Composite indexes for analysis queries
    __table_args__ = (
        Index('idx_ppt_analyses_scores', 'accessibility_score', 'complexity_score'),
    )


class AIPromptSettings(Base):
    __tablename__ = "ai_prompt_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Model identification
    model_name = Column(String(50), index=True)  # 'nova_micro', 'nova_lite', 'nova_pro'
    model_fields = Column(String(500))  # JSON array of fields this model generates
    
    # Prompt content - PostgreSQL optimized for large text
    prompt_template = Column(Text)  # The actual prompt template
    
    # Settings metadata
    is_default = Column(Boolean, default=False, index=True)  # Whether this is system default
    is_active = Column(Boolean, default=True, index=True)   # Whether this prompt is currently active
    
    # Versioning and tracking
    version = Column(String(20), default="1.0")
    description = Column(String(500), nullable=True)  # Optional description of changes
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    # PostgreSQL: Indexes for prompt queries
    __table_args__ = (
        Index('idx_ai_prompts_model_active', 'model_name', 'is_active'),
        Index('idx_ai_prompts_default', 'is_default'),
    )


class BulkGenerationJob(Base):
    __tablename__ = "bulk_generation_jobs"
    
    id = Column(String(255), primary_key=True, index=True)  # Job ID string
    ppt_file_id = Column(Integer, ForeignKey("ppt_files.id"), index=True)
    
    # Job metadata
    total_slides = Column(Integer)
    completed_slides = Column(Integer, default=0)  # Fixed: was processed_slides
    failed_slides = Column(Integer, default=0)
    
    # Status and progress
    status = Column(String(50), default="pending", index=True)  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True, index=True)
    
    # Relationships
    ppt_file = relationship("PPTFile", back_populates="bulk_jobs")

class SlideVersion(Base):
    __tablename__ = "slide_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    ppt_file_id = Column(Integer, ForeignKey("ppt_files.id"), index=True)
    slide_number = Column(Integer, index=True)
    
    # Version tracking
    version_number = Column(Integer, default=1)
    content_hash = Column(String(64), index=True)  # SHA-256 of slide content
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    ppt_file = relationship("PPTFile")
    
    # PostgreSQL: Composite indexes
    __table_args__ = (
        Index('idx_slide_versions_ppt_slide', 'ppt_file_id', 'slide_number'),
    )

class PPTSlide(Base):
    """
    Model for individual slide data and AI-generated content.
    Stores extracted slide information and AI-generated notes for each slide.
    """
    __tablename__ = "ppt_slides"
    
    id = Column(Integer, primary_key=True, index=True)
    ppt_file_id = Column(Integer, ForeignKey("ppt_files.id"), index=True)
    slide_number = Column(Integer, index=True)
    
    # Slide metadata
    title = Column(Text, nullable=True)  # Slide title if extracted
    content = Column(Text, nullable=True)  # Raw slide content
    notes = Column(Text, nullable=True)  # Original speaker notes
    
    # AI-generated content fields
    ai_script = Column(Text, nullable=True)  # Generated script
    ai_instructor_notes = Column(Text, nullable=True)  # Generated instructor notes (HTML)
    ai_student_notes = Column(Text, nullable=True)  # Generated student notes (HTML)
    ai_alt_text = Column(Text, nullable=True)  # Generated alt text
    ai_slide_description = Column(Text, nullable=True)  # Generated slide description
    ai_references = Column(Text, nullable=True)  # Generated references (HTML)
    ai_developer_notes = Column(Text, nullable=True)  # Generated developer notes
    
    # AI generation tracking
    ai_generated = Column(Boolean, default=False, index=True)  # Whether AI content has been generated
    ai_generated_at = Column(DateTime, nullable=True, index=True)  # When AI content was generated
    ai_model_used = Column(String(100), nullable=True)  # Which AI model was used
    
    # Content tracking
    content_hash = Column(String(64), index=True, nullable=True)  # SHA-256 of slide content for change detection
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    # Relationships
    ppt_file = relationship("PPTFile", back_populates="slides")
    
    # PostgreSQL: Composite indexes for performance
    __table_args__ = (
        Index('idx_ppt_slides_ppt_slide', 'ppt_file_id', 'slide_number'),
        Index('idx_ppt_slides_ai_generated', 'ai_generated', 'ai_generated_at'),
        Index('idx_ppt_slides_content_hash', 'content_hash'),
    )

# PostgreSQL Migration Validation
# ================================
# This section ensures no regression back to SQLite column mapping issues

import logging
logger = logging.getLogger(__name__)

# CRITICAL: Prevent SQLite column mapping regression
# The old SQLite database used 'format' column which caused errors
# PostgreSQL correctly uses 'image_format' as defined in the model
if hasattr(SlideImage, 'format'):
    logger.warning("⚠️ Detected legacy 'format' column reference - removing to prevent SQLite regression")
    delattr(SlideImage, 'format')

# Validate PostgreSQL column mapping
def validate_postgresql_models():
    """Validate that models are correctly configured for PostgreSQL."""
    slide_image_columns = [col.name for col in SlideImage.__table__.columns]
    
    if 'image_format' not in slide_image_columns:
        raise RuntimeError("❌ SlideImage model missing 'image_format' column - PostgreSQL migration incomplete")
    
    if 'format' in slide_image_columns:
        raise RuntimeError("❌ SlideImage model still has legacy 'format' column - SQLite regression detected")
    
    logger.info("✅ PostgreSQL model validation passed - no SQLite regression detected")

# Run validation when models are imported
try:
    validate_postgresql_models()
except Exception as e:
    logger.critical(f"Model validation failed: {e}")
    raise
