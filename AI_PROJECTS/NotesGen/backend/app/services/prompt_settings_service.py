"""
Service for managing AI prompt settings.
Provides dynamic prompt loading for AINotesService with fallback to defaults.
"""

import json
import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..models.models import AIPromptSettings

logger = logging.getLogger(__name__)

class PromptSettingsService:
    """Service for loading and managing AI prompt settings."""
    
    def __init__(self):
        self._cached_prompts: Dict[str, str] = {}
        self._cache_timestamp = None
        
    def get_prompt_for_model(self, model_name: str) -> str:
        """
        Get the active prompt template for a specific model.
        Returns custom prompt if available, otherwise returns default.
        
        Args:
            model_name: The model name ('nova_micro', 'nova_lite', 'nova_pro')
            
        Returns:
            The prompt template string with {context} placeholder
        """
        try:
            # Try to get from database first
            db = next(get_db())
            try:
                custom_prompt = db.query(AIPromptSettings).filter(
                    AIPromptSettings.model_name == model_name,
                    AIPromptSettings.is_active == True
                ).first()
                
                if custom_prompt and custom_prompt.prompt_template:
                    logger.info(f"✅ Using custom prompt for {model_name} (version {custom_prompt.version})")
                    return custom_prompt.prompt_template
                else:
                    logger.info(f"📋 Using default prompt for {model_name} (no custom found)")
                    return self._get_default_prompt(model_name)
                    
            finally:
                db.close()
                
        except Exception as e:
            logger.warning(f"⚠️ Error loading custom prompt for {model_name}: {e}, using default")
            return self._get_default_prompt(model_name)
    
    def _get_default_prompt(self, model_name: str) -> str:
        """Get default prompt template for a model."""
        
        # Default prompts (same as in ai_prompts.py)
        default_prompts = {
            "nova_micro": """Analyze this AWS slide content and provide specific, relevant documentation references and developer implementation notes.

SLIDE CONTENT:
{context}

CRITICAL REQUIREMENTS FOR REFERENCES:
- Provide 1-3 SPECIFIC, DEEP AWS documentation URLs (not generic home pages)
- URLs must be REAL and VALID (use actual AWS documentation structure)
- Focus on implementation guides, tutorials, and specific features mentioned in the slide
- Avoid top-level service home pages like docs.aws.amazon.com/sagemaker/
- Each reference must be directly relevant to the specific concepts in this slide
- One high-quality, relevant reference is better than multiple generic ones

EXAMPLE GOOD REFERENCES (for reference only - analyze the actual slide content):
- https://docs.aws.amazon.com/sagemaker/latest/dg/algos.html (for algorithm implementations)
- https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-training-algo.html (for custom algorithms)
- https://docs.aws.amazon.com/glue/latest/dg/author-job.html (for ETL job creation)

OUTPUT FORMAT:
REFERENCES:
[1-3 specific URLs relevant to the slide concepts - provide only as many as are truly relevant]

DEVELOPER NOTES:
[Brief overview notes about this slide concept. Write 2-3 plain text sentences describing what this slide covers and why it's important. Include 1-2 reference URLs if relevant. No markdown formatting - use plain text only. Keep it concise and focused on giving others a quick understanding of the slide's main concept.]""",

            "nova_lite": """Create educational content for this AWS training slide.

SLIDE CONTENT:
{context}

LANGUAGE GUIDELINES - STRICTLY AVOID:
Words: crucial, unlock, unleash, elevate, leverage, robust, revolutionize, seamless, holistic, empower, tailored
Phrases: "in today's fast-paced world", "delve into", "it is important to note that", "at the forefront of", "game-changing", "seamlessly integrated", "furthermore/moreover/therefore" (overuse), "the power of", "unparalleled excellence", "navigate the complexities"
Use direct, clear language instead of buzzwords and corporate jargon.

Generate instructor script, teaching notes, and student reference materials.

OUTPUT FORMAT:
SCRIPT:
[4-6 sentences that an instructor would say when presenting this slide. Jump directly into the educational content without lead-in phrases like "Today we're going to...", "Let's discuss...", "We're looking at...". Start immediately with the actual subject matter and concepts.]

INSTRUCTOR NOTES:
[EXACTLY 2-5 teaching points as bullet list. Each bullet must start with "- |" followed by content. MAXIMUM 5 bullets:
- |Key concept to emphasize
- |Common misconception to address
- |Discussion question for engagement]

STUDENT NOTES:
[2-3 paragraphs for student reference. Use *italics* for key terms. Include technical concepts, practical applications, and key takeaways. Maximum 250 words.]""",

            "nova_lite_enhanced": """
🚨 CRITICAL FORMAT REQUIREMENT 🚨
ABSOLUTE REQUIREMENT: Output MUST use the exact Speaker Notes format with ~ and | prefixes.
THIS FORMAT IS REQUIRED FOR POWERPOINT PARSING AND MUST NEVER BE CHANGED.
Any deviation will break the frontend parsing and user experience.

PHASE 1A OPTIMIZATION: Enhanced Nova Lite generating all 5 fields (eliminates Nova Pro throttling)

Create comprehensive educational content for this AWS training slide.

SLIDE CONTENT:
{context}

SLIDE TYPE GUIDANCE:
{slide_type_template}

LANGUAGE GUIDELINES - STRICTLY AVOID:
Words: crucial, unlock, unleash, elevate, leverage, robust, revolutionize, seamless, holistic, empower, tailored
Phrases: "in today's fast-paced world", "delve into", "it is important to note that", "at the forefront of", "game-changing", "seamlessly integrated", "furthermore/moreover/therefore" (overuse), "the power of", "unparalleled excellence", "navigate the complexities"
Use direct, clear language instead of buzzwords and corporate jargon.

🚨 CRITICAL: OUTPUT FORMAT - MUST BE EXACT 🚨
Generate ALL 5 sections using this EXACT format with proper ~ and | prefixes:

~Script:
~[A conversational narrative that the instructor reads aloud. Jump directly into educational content. 4-6 sentences maximum.]
~
|Instructor Notes:
- |Core concepts to emphasize during instruction
- |Common misconceptions to address
- |Discussion questions to encourage critical thinking
|
|Student Notes:
[2-3 comprehensive paragraphs for student reference. Maximum 250 words total. Plain text content without prefix markers.]
~Alttext: 
~1. [Brief description of first visual element for screen readers]
~
~Slide Description: 
~Slide [X]: [Detailed visual description for accessibility. Focus on HOW content is organized visually.]
~

🚨 CRITICAL FORMATTING RULES - NEVER CHANGE THESE 🚨:
1. Script section: Use ~Script: header with ~ prefix on content lines and ~ terminator
2. Instructor Notes: Use |Instructor Notes: header with - | prefix for bullets, end with | terminator
3. Student Notes: Use |Student Notes: header but content is plain text without prefix
4. Alt text: Use ~Alttext: header with numbered ~ prefixed descriptions and ~ terminator
5. Slide Description: Use ~Slide Description: header with ~ prefix and ~ terminator
6. Section terminators: Always end sections with ~ or | as shown
7. NO BLANK LINES between sections

This format is CRITICAL for PowerPoint integration and frontend parsing. 
NEVER modify these prefix patterns or section structures.
""",

            "nova_pro": """Analyze this slide and create accessibility content with focus on VISUAL LAYOUT, not data enumeration.

SLIDE CONTENT:
{context}

LANGUAGE GUIDELINES - STRICTLY AVOID:
Words: crucial, unlock, unleash, elevate, leverage, robust, revolutionize, seamless, holistic, empower, tailored
Phrases: "in today's fast-paced world", "delve into", "it is important to note that", "at the forefront of", "game-changing", "seamlessly integrated", "furthermore/moreover/therefore" (overuse), "the power of", "unparalleled excellence", "navigate the complexities"
Use direct, clear language instead of buzzwords and corporate jargon.

CRITICAL INSTRUCTIONS FOR SLIDE DESCRIPTION:
- FOCUS ON VISUAL LAYOUT AND STRUCTURE, NOT INDIVIDUAL DATA POINTS
- Describe what TYPE of content is shown (tables, diagrams, charts) and HOW it's arranged
- For data tables: describe column headers and row structure, NOT individual values
- For diagrams: describe shapes, arrows, connections, and spatial relationships
- For charts: describe chart type, axes, and general patterns, NOT specific numbers
- Emphasize visual hierarchy, positioning, and layout flow

EXAMPLES OF GOOD DESCRIPTIONS:
✅ "A comparison table with three columns showing different data storage approaches"
✅ "Two side-by-side diagrams illustrating workflow differences"
✅ "A bar chart displaying performance metrics across five categories"

EXAMPLES OF BAD DESCRIPTIONS (AVOID):
❌ "The first row shows 12345678, 87654321, 11223344..."
❌ "Customer ID 12345678 has age 32 and subscription false..."
❌ "The chart shows values of 1.2, 3.4, 5.6, 7.8..."

OUTPUT FORMAT:
ALT TEXT:
[Brief description for screen readers - focus on key visual elements only, NO specific data values]

SLIDE DESCRIPTION:
[Detailed VISUAL description for visually impaired users. Start with "Slide [number]: [title]" then describe visual layout, structure, and arrangement from upper left, reading left-to-right, top-to-bottom. Focus on HOW content is organized visually, not WHAT the specific data says. Include diagrams, charts, tables as structural elements. Be specific about visual hierarchy and spatial relationships. Maximum 300 words.]"""
        }
        
        if model_name in default_prompts:
            return default_prompts[model_name]
        else:
            logger.error(f"❌ Unknown model name: {model_name}")
            raise ValueError(f"Unknown model name: {model_name}")
    
    def get_all_active_prompts(self) -> Dict[str, str]:
        """Get all active prompts for all models."""
        return {
            "nova_micro": self.get_prompt_for_model("nova_micro"),
            "nova_lite": self.get_prompt_for_model("nova_lite"),
            "nova_lite_enhanced": self.get_prompt_for_model("nova_lite_enhanced"),
            "nova_pro": self.get_prompt_for_model("nova_pro")
        }
    
    def invalidate_cache(self):
        """Invalidate the prompt cache to force reload from database."""
        self._cached_prompts.clear()
        self._cache_timestamp = None
        logger.info("🔄 Prompt cache invalidated")

# Global singleton instance
_prompt_service_instance: Optional[PromptSettingsService] = None

def get_prompt_service() -> PromptSettingsService:
    """Get or create the global PromptSettingsService instance."""
    global _prompt_service_instance
    if _prompt_service_instance is None:
        _prompt_service_instance = PromptSettingsService()
    return _prompt_service_instance 