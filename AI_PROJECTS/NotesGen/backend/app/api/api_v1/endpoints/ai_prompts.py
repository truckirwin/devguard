"""
API endpoints for managing AI prompt settings and notes templates.
Allows users to customize, save, and reset AI prompts and speaker notes templates used by Nova models.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
import logging
from datetime import datetime
from pathlib import Path

from ....models.models import AIPromptSettings
from ....db.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

class PromptSettingsRequest(BaseModel):
    """Request model for updating AI prompt settings."""
    model_name: str  # 'nova_micro', 'nova_lite', 'nova_pro'
    prompt_template: str
    description: str = None

class PromptSettingsResponse(BaseModel):
    """Response model for AI prompt settings."""
    model_name: str
    generated_fields: List[str]  # Renamed to avoid Pydantic conflict
    prompt_template: str
    is_default: bool
    version: str
    description: str = None
    updated_at: str

class NotesTemplate(BaseModel):
    """Model for a single notes template."""
    name: str
    description: str
    template: str

class NotesTemplatesRequest(BaseModel):
    """Request model for updating notes templates."""
    templates: Dict[str, NotesTemplate]

# Storage path for templates
TEMPLATES_CONFIG_PATH = Path("config/notes_templates.json")
TEMPLATES_CONFIG_PATH.parent.mkdir(exist_ok=True)

# Default Notes Templates based on actual PowerPoint analysis
DEFAULT_NOTES_TEMPLATES = {
    "module_title": {
        "name": "Module Title Slide",
        "description": "Opening slides with module introduction and timing",
        "template": """SLIDE TYPE: Module Title Slide

LENGTH INSTRUCTION: Very brief notes (2-3 bullet points maximum)
CONTENT FOCUS: Focus on module overview and learning objectives
TIME INSTRUCTION: Include estimated time prominently

FORMAT EXAMPLE:
~Developer Notes:
~Ref: [relevant AWS documentation]
~
|INSTRUCTOR NOTES:
|Timing estimate: [X] min
|Introduce the module on [topic]
|Highlight the importance of [key concept]
|
|STUDENT NOTES:
This module focuses on [main topic]. [Brief overview of what students will learn and why it's important. Keep to 2-3 sentences maximum.]"""
    },
    "agenda": {
        "name": "Agenda/Overview Slide", 
        "description": "Agenda and module overview slides",
        "template": """SLIDE TYPE: Agenda/Overview Slide

LENGTH INSTRUCTION: Very brief notes (1-2 lines per agenda item)
CONTENT FOCUS: List agenda items concisely, focus on flow
TIME INSTRUCTION: Keep timing brief, mention overall structure

FORMAT EXAMPLE:
~Developer Notes:
~Ref: [relevant AWS documentation]
~
|INSTRUCTOR NOTES:
|Outline the module's main topics
|Briefly introduce each section
|
|STUDENT NOTES:
This module is structured into [X] main topics:
Topic A: [Brief description]
Topic B: [Brief description]
Topic C: [Brief description]"""
    },
    "content": {
        "name": "Standard Content Slide",
        "description": "Regular content slides with full detail",
        "template": """SLIDE TYPE: Standard Content Slide

LENGTH INSTRUCTION: Standard detailed notes (unchanged from current)
CONTENT FOCUS: Full content coverage as normal
TIME INSTRUCTION: Standard timing guidance

FORMAT EXAMPLE:
~Developer Notes:
~Ref: [relevant AWS documentation]
~
|INSTRUCTOR NOTES:
|[Detailed teaching guidance]
|[Key concepts to emphasize]
|[Examples and demonstrations]
|
|STUDENT NOTES:
[Comprehensive learning content with full explanations, technical details, and practical applications. Standard length and depth.]"""
    },
    "knowledge_check_intro": {
        "name": "Knowledge Check Introduction", 
        "description": "Slides introducing knowledge check sections",
        "template": """SLIDE TYPE: Knowledge Check Introduction

LENGTH INSTRUCTION: Brief notes focusing on section introduction
CONTENT FOCUS: Setup for knowledge check engagement
TIME INSTRUCTION: Include time for setup and engagement

FORMAT EXAMPLE:
~Developer Notes:
This slide introduces a knowledge check section
~
|INSTRUCTOR NOTES:
|Prepare to administer knowledge check questions
|Encourage student participation and discussion
|
|STUDENT NOTES:
You will now have a brief knowledge check to review key concepts from this module. This is an opportunity to reinforce your understanding and clarify any areas of confusion before moving on."""
    },
    "knowledge_check_question": {
        "name": "Knowledge Check Question",
        "description": "Question slides for assessment",
        "template": """SLIDE TYPE: Knowledge Check Question

LENGTH INSTRUCTION: Brief notes focusing on question mechanics
CONTENT FOCUS: Question setup and learning objectives
TIME INSTRUCTION: Include time for thinking and discussion

FORMAT EXAMPLE:
~Developer Notes:
~This question tests understanding of [concept]
~
|INSTRUCTOR NOTES:
|Give students time to consider their answer
|Encourage discussions on why each option might or might not be suitable
|Do not provide the correct answer yet
|
|STUDENT NOTES:
This question asks you to [identify/explain/choose] [key concept]. Consider [guidance for thinking through the question]. Think about [relevant factors or criteria]."""
    },
    "knowledge_check_answer": {
        "name": "Knowledge Check Answer",
        "description": "Answer explanation slides", 
        "template": """SLIDE TYPE: Knowledge Check Answer

LENGTH INSTRUCTION: Follow the existing patterns in the PowerPoint exactly
CONTENT FOCUS: Clear explanation of correct answer and why others are incorrect
TIME INSTRUCTION: Time for explanation and clarification

FORMAT EXAMPLE:
~Developer Notes:
~Provide clear explanation for correct and incorrect answers
~
|INSTRUCTOR NOTES:
|Explain why [correct option] is the best choice for this scenario
|Discuss why the other options are less suitable
|Reinforce the importance of [key concept]
|
|STUDENT NOTES:
The correct answer is [X]: [option]. [Explanation of why this is correct with specific reasoning].
The other options are less suitable:
[A]. [Why this is incorrect]
[B]. [Why this is incorrect]
[C]. [Why this is incorrect]"""
    },
    "knowledge_check_wrapup": {
        "name": "Knowledge Check Wrap-up",
        "description": "Learning objectives and module summary slides",
        "template": """SLIDE TYPE: Knowledge Check Wrap-up

LENGTH INSTRUCTION: Objectives summary with achievement review
CONTENT FOCUS: Learning outcomes and key takeaways
TIME INSTRUCTION: Time for review and questions

FORMAT EXAMPLE:
~Developer Notes:
~No specific references needed for this slide
~Alt text: This slide lists the learning objectives achieved in the module
~
|INSTRUCTOR NOTES:
|Review each learning objective
|Highlight key takeaways for each point
|Encourage students to ask questions if any objectives are unclear
|
|STUDENT NOTES:
You should now be able to do the following:
[Objective 1]: [Description of achieved capability]
[Objective 2]: [Description of achieved capability]
[Objective 3]: [Description of achieved capability]
These skills form the foundation for [broader context]."""
    },
    "section": {
        "name": "Section/Transition Slide",
        "description": "Section breaks and transition slides",
        "template": """SLIDE TYPE: Section/Transition Slide

LENGTH INSTRUCTION: Very brief notes (1-3 bullet points)
CONTENT FOCUS: Section introduction or summary
TIME INSTRUCTION: Brief transition timing

FORMAT EXAMPLE:
~Developer Notes:
~Ref: [relevant AWS documentation]
~
|INSTRUCTOR NOTES:
|Brief transition to next section
|Set context for upcoming content
|
|STUDENT NOTES:
[Brief overview of what's coming next in this section or summary of completed section. Keep very concise.]"""
    }
}

def load_templates_config() -> Dict[str, Any]:
    """Load notes templates configuration from file or return defaults"""
    try:
        if TEMPLATES_CONFIG_PATH.exists():
            with open(TEMPLATES_CONFIG_PATH, 'r') as f:
                return json.load(f)
        else:
            logger.info("No templates config found, using defaults")
            return DEFAULT_NOTES_TEMPLATES
    except Exception as e:
        logger.error(f"Error loading templates config: {e}")
        return DEFAULT_NOTES_TEMPLATES

def save_templates_config(templates: Dict[str, Any]) -> bool:
    """Save notes templates configuration to file"""
    try:
        with open(TEMPLATES_CONFIG_PATH, 'w') as f:
            json.dump(templates, f, indent=2)
        logger.info(f"Saved {len(templates)} notes template configurations")
        return True
    except Exception as e:
        logger.error(f"Error saving templates config: {e}")
        return False

def get_template_for_slide_type(slide_type: str) -> str:
    """Get the template pattern for a specific slide type"""
    templates = load_templates_config()
    
    # Map slide type analyzer names to template keys
    type_mapping = {
        "module_title": "module_title",
        "agenda": "agenda", 
        "content": "content",
        "section": "section",
        "knowledge_check": "knowledge_check_question",
        "knowledge_check_answers": "knowledge_check_answer"
    }
    
    template_key = type_mapping.get(slide_type, "content")
    template_data = templates.get(template_key, templates["content"])
    
    return template_data["template"]

# Default prompts extracted from the current AINotesService
DEFAULT_PROMPTS = {
    "nova_micro": {
        "fields": ["references", "developerNotes"],
        "prompt": """
🚨 CRITICAL FORMAT REQUIREMENT 🚨
ABSOLUTE REQUIREMENT: Output MUST use the exact Speaker Notes format with ~ prefixes.
THIS FORMAT IS REQUIRED FOR POWERPOINT PARSING AND MUST NEVER BE CHANGED.

Analyze this AWS slide content and provide specific, relevant documentation references and developer implementation notes.

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

🚨 CRITICAL: OUTPUT FORMAT - MUST BE EXACT 🚨
Generate BOTH sections using this EXACT format with proper ~ prefixes:

~Developernotes: 
~[Technical implementation guidance using natural paragraph flow with key points highlighted. NO numbered lists. Include best practices, architecture decisions, and technical considerations focused on practical guidance for AWS services mentioned in the slide. Focus on actionable implementation tips and operational insights.]
~

~References
~[Page Title] ([Full AWS Documentation URL])
~[Page Title] ([Full AWS Documentation URL])
~[Page Title] ([Full AWS Documentation URL])
~   

🚨 CRITICAL FORMATTING RULES - NEVER CHANGE THESE 🚨:
1. Developer Notes: Use ~Developernotes: header, numbered tips with **bold titles**, ~ terminator
2. References: Use ~References header, URL with description in parentheses, ~    terminator with spaces
3. Always end sections with proper ~ terminators as shown
4. Maintain exact spacing and line breaks as demonstrated

This format is CRITICAL for PowerPoint integration and frontend parsing. 
NEVER modify these prefix patterns or section structures.
"""
    },
    "nova_lite": {
        "fields": ["script", "instructorNotes", "studentNotes"],
        "prompt": """Create educational content for this AWS training slide.

SLIDE CONTENT:
{context}

LANGUAGE GUIDELINES - STRICTLY AVOID:
Words: crucial, unlock, unleash, elevate, leverage, robust, revolutionize, seamless, holistic, empower, tailored
Phrases: "in today's fast-paced world", "delve into", "it is important to note that", "at the forefront of", "game-changing", "seamlessly integrated", "furthermore/moreover/therefore" (overuse), "the power of", "unparalleled excellence", "navigate the complexities"
Use direct, clear language instead of buzzwords and corporate jargon.

Generate instructor script, teaching notes, and student reference materials.

{slide_type_template}

OUTPUT FORMAT:
SCRIPT:
[Complete instructor delivery script written by AWS Technical Trainers. This is the ENTIRE script an instructor would say to deliver this content. Include clear explanations, practical insights, useful anecdotes, use cases, and references. Be comprehensive but concise. Jump directly into the educational content without lead-in phrases like "Today we're going to...", "Let's discuss...", "We're looking at...". Start immediately with the actual subject matter. As AWS Technical Trainers, share real-world experience and practical guidance.]

INSTRUCTOR NOTES:
[EXACTLY 2-5 teaching points as bullet list. Each bullet must start with "- |" followed by content. MAXIMUM 5 bullets:
- |Key concept to emphasize
- |Common misconception to address
- |Discussion question for engagement]

STUDENT NOTES:
[2-3 paragraphs for student reference. Use *italics* for key terms. Include technical concepts, practical applications, and key takeaways. Maximum 250 words.]"""
    },
    "nova_lite_enhanced": {
        "fields": ["script", "instructorNotes", "studentNotes", "altText", "slideDescription"],
        "prompt": """
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
~[Complete instructor delivery script written by AWS Technical Trainers. This is the ENTIRE script an instructor would say to deliver this content. Include clear explanations, practical insights, useful anecdotes, use cases, and references. Be comprehensive but concise. Jump directly into the educational content. As AWS Technical Trainers, share real-world experience and practical guidance.]
~
|Instructor Notes:
- |Core concepts to emphasize during instruction
- |Common misconceptions to address
- |Discussion questions to encourage critical thinking
|
|Student Notes:
[2-3 comprehensive paragraphs for student reference. Maximum 250 words total. Plain text content without prefix markers.]
~Alttext: 
~[ONLY if there are actual images, diagrams, charts, or tables on the slide: Provide clear visual descriptions for screen readers. If the slide has NO visual elements, leave this section empty.]
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
"""
    },
    "nova_pro": {
        "fields": ["altText", "slideDescription"],
        "prompt": """Analyze this slide and create accessibility content with focus on VISUAL LAYOUT, not data enumeration.

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
}

# AI Prompts endpoints
@router.get("/prompts", response_model=List[PromptSettingsResponse])
async def get_all_prompts(db: Session = Depends(get_db)) -> List[PromptSettingsResponse]:
    """Get all AI prompt settings, including defaults if no custom ones exist."""
    
    try:
        # Get existing custom prompts from database
        custom_prompts = db.query(AIPromptSettings).filter(AIPromptSettings.is_active == True).all()
        
        # Convert to dict for easy lookup
        custom_prompt_dict = {prompt.model_name: prompt for prompt in custom_prompts}
        
        result = []
        
        # For each default model, return either custom or default prompt
        for model_name, default_data in DEFAULT_PROMPTS.items():
            if model_name in custom_prompt_dict:
                # Use custom prompt
                custom = custom_prompt_dict[model_name]
                result.append(PromptSettingsResponse(
                    model_name=model_name,
                    generated_fields=json.loads(custom.model_fields) if custom.model_fields else default_data["fields"],
                    prompt_template=custom.prompt_template,
                    is_default=custom.is_default,
                    version=custom.version,
                    description=custom.description,
                    updated_at=custom.updated_at.isoformat()
                ))
            else:
                # Use default prompt
                result.append(PromptSettingsResponse(
                    model_name=model_name,
                    generated_fields=default_data["fields"],
                    prompt_template=default_data["prompt"],
                    is_default=True,
                    version="1.0",
                    description="Default system prompt",
                    updated_at=datetime.utcnow().isoformat()
                ))
        
        logger.info(f"✅ Retrieved {len(result)} AI prompt settings")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error retrieving AI prompts: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving prompts: {str(e)}")

@router.post("/prompts/save", response_model=Dict[str, str])
async def save_prompt_settings(
    prompts: List[PromptSettingsRequest], 
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Save custom AI prompt settings."""
    
    try:
        saved_count = 0
        
        for prompt_request in prompts:
            # Validate model name
            if prompt_request.model_name not in DEFAULT_PROMPTS:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid model name: {prompt_request.model_name}"
                )
            
            # Check if custom prompt already exists
            existing = db.query(AIPromptSettings).filter(
                AIPromptSettings.model_name == prompt_request.model_name,
                AIPromptSettings.is_active == True
            ).first()
            
            if existing:
                # Update existing prompt
                existing.prompt_template = prompt_request.prompt_template
                existing.description = prompt_request.description
                existing.updated_at = datetime.utcnow()
                existing.version = f"{float(existing.version) + 0.1:.1f}"  # Increment version
            else:
                # Create new custom prompt
                new_prompt = AIPromptSettings(
                    model_name=prompt_request.model_name,
                    model_fields=json.dumps(DEFAULT_PROMPTS[prompt_request.model_name]["fields"]),
                    prompt_template=prompt_request.prompt_template,
                    description=prompt_request.description,
                    is_default=False,
                    is_active=True,
                    version="1.1"  # Custom version
                )
                db.add(new_prompt)
            
            saved_count += 1
        
        db.commit()
        logger.info(f"✅ Saved {saved_count} custom AI prompt settings")
        
        return {
            "message": f"Successfully saved {saved_count} prompt settings",
            "saved_count": str(saved_count)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error saving AI prompts: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving prompts: {str(e)}")

@router.post("/prompts/reset", response_model=Dict[str, str])
async def reset_prompts_to_default(db: Session = Depends(get_db)) -> Dict[str, str]:
    """Reset all prompts to system defaults."""
    
    try:
        # Deactivate all custom prompts (soft delete)
        custom_prompts = db.query(AIPromptSettings).filter(AIPromptSettings.is_active == True)
        reset_count = custom_prompts.count()
        
        custom_prompts.update({
            "is_active": False,
            "updated_at": datetime.utcnow()
        })
        
        db.commit()
        logger.info(f"✅ Reset {reset_count} custom prompts to defaults")
        
        return {
            "message": f"Successfully reset {reset_count} prompts to defaults",
            "reset_count": str(reset_count)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error resetting prompts: {e}")
        raise HTTPException(status_code=500, detail=f"Error resetting prompts: {str(e)}")

@router.get("/prompts/{model_name}", response_model=PromptSettingsResponse)
async def get_prompt_by_model(model_name: str, db: Session = Depends(get_db)) -> PromptSettingsResponse:
    """Get prompt settings for a specific model."""
    
    try:
        if model_name not in DEFAULT_PROMPTS:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
        
        # Try to get custom prompt first
        custom_prompt = db.query(AIPromptSettings).filter(
            AIPromptSettings.model_name == model_name,
            AIPromptSettings.is_active == True
        ).first()
        
        if custom_prompt:
            return PromptSettingsResponse(
                model_name=model_name,
                generated_fields=json.loads(custom_prompt.model_fields) if custom_prompt.model_fields else DEFAULT_PROMPTS[model_name]["fields"],
                prompt_template=custom_prompt.prompt_template,
                is_default=custom_prompt.is_default,
                version=custom_prompt.version,
                description=custom_prompt.description,
                updated_at=custom_prompt.updated_at.isoformat()
            )
        else:
            # Return default prompt
            default_data = DEFAULT_PROMPTS[model_name]
            return PromptSettingsResponse(
                model_name=model_name,
                generated_fields=default_data["fields"],
                prompt_template=default_data["prompt"],
                is_default=True,
                version="1.0",
                description="Default system prompt",
                updated_at=datetime.utcnow().isoformat()
            )
        
    except Exception as e:
        logger.error(f"❌ Error retrieving prompt for {model_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving prompt: {str(e)}")

# Notes Templates endpoints
@router.get("/notes-templates")
async def get_notes_templates():
    """Get current notes templates configuration"""
    try:
        templates = load_templates_config()
        logger.info(f"✅ Retrieved {len(templates)} notes template configurations")
        return templates
    except Exception as e:
        logger.error(f"❌ Error retrieving notes templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve notes templates")

@router.post("/notes-templates/save")
async def save_notes_templates(templates: Dict[str, Any]):
    """Save notes templates configuration"""
    try:
        if not templates:
            raise HTTPException(status_code=400, detail="No templates provided")
        
        # Validate required fields
        for template_type, template_data in templates.items():
            if not all(key in template_data for key in ["name", "description", "template"]):
                raise HTTPException(status_code=400, detail=f"Missing required fields in template configuration for {template_type}")
        
        success = save_templates_config(templates)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save notes templates")
        
        logger.info(f"✅ Successfully saved {len(templates)} notes template configurations")
        return {"message": f"Successfully saved {len(templates)} notes template configurations", "count": len(templates)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error saving notes templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to save notes templates")

@router.post("/notes-templates/reset")
async def reset_notes_templates():
    """Reset notes templates to default configuration"""
    try:
        success = save_templates_config(DEFAULT_NOTES_TEMPLATES)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to reset notes templates")
        
        logger.info("✅ Successfully reset notes templates to defaults")
        return {"message": "Notes templates reset to default configuration", "count": len(DEFAULT_NOTES_TEMPLATES)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error resetting notes templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset notes templates") 