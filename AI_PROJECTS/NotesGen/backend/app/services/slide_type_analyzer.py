"""
Slide Type Analyzer Service

Analyzes slide content to determine slide type and select appropriate AI prompts.
Supports various slide types: module title, agenda, content, section, knowledge check, etc.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class SlideType(Enum):
    """Enumeration of different slide types"""
    MODULE_TITLE = "module_title"
    AGENDA = "agenda" 
    CONTENT = "content"
    SECTION = "section"
    KNOWLEDGE_CHECK = "knowledge_check"
    KNOWLEDGE_CHECK_ANSWERS = "knowledge_check_answers"

@dataclass
class SlideTypeAnalysis:
    """Result of slide type analysis"""
    slide_type: SlideType
    confidence: float
    reasoning: str
    estimated_time_minutes: Optional[int] = None

class SlideTypeAnalyzer:
    """Analyzes slide content to determine slide type and appropriate prompts"""
    
    def __init__(self):
        # Pattern definitions for slide type detection
        self.module_title_patterns = [
            r'\bmodule\s+\d+\b',
            r'\bmod\s+\d+\b', 
            r'\blesson\s+\d+\b',
            r'\bchapter\s+\d+\b',
            r'learning\s+objectives?',
            r'module\s+objectives?',
            r'agenda',
            r'outline',
            r'overview',
            r'introduction\s+to',
            r'estimated\s+time',
            r'\d+\s+minutes?',
            # Enhanced title slide patterns
            r'data\s+engineering',
            r'aws',
            r'amazon\s+web\s+services',
            r'optimizing',
            r'securing',
            r'data\s+lake',
            r'solution'
        ]
        
        self.agenda_patterns = [
            r'\bagenda\b',
            r'\boutline\b', 
            r'\boverview\b',
            r'\btopics?\b',
            r'what\s+we\s*\'?ll\s+cover',
            r'in\s+this\s+module',
            r'learning\s+objectives?',
            r'bullet\s+points?'
        ]
        
        self.section_patterns = [
            r'\bsection\s+\d+\b',
            r'\bpart\s+\d+\b',
            r'\bchapter\s+\d+\b',
            r'introduction',
            r'summary',
            r'wrap[-\s]?up',
            r'conclusion',
            r'review',
            r'recap'
        ]
        
        self.knowledge_check_patterns = [
            r'knowledge\s+check',
            r'quiz',
            r'question\s*\d*',
            r'assessment',
            r'test\s+your\s+knowledge',
            r'which\s+of\s+the\s+following',
            r'what\s+is\s+the',
            r'how\s+do\s+you',
            r'select\s+all\s+that\s+apply',
            r'true\s+or\s+false',
            r'multiple\s+choice'
        ]
        
        self.knowledge_check_answer_patterns = [
            r'correct\s+answer',
            r'explanation',
            r'feedback',
            r'because',
            r'the\s+answer\s+is',
            r'incorrect.*because',
            r'correct.*because',
            r'rationale'
        ]
        
        # Time estimation patterns
        self.time_patterns = [
            r'(\d+)\s*[-–]\s*(\d+)\s+min(?:ute)?s?',
            r'(\d+)\s+min(?:ute)?s?',
            r'approximately\s+(\d+)\s+min(?:ute)?s?',
            r'estimated\s+time\s*:?\s*(\d+)\s+min(?:ute)?s?'
        ]
    
    def analyze_slide_type(self, slide_content: str, slide_text_elements: List = None, 
                          slide_number: int = 1, total_slides: int = 1) -> SlideTypeAnalysis:
        """
        Analyze slide content to determine its type
        
        Args:
            slide_content: Combined text content from the slide
            slide_text_elements: List of text elements (if available)
            slide_number: Current slide number
            total_slides: Total number of slides in presentation
            
        Returns:
            SlideTypeAnalysis with detected type and metadata
        """
        
        content_lower = slide_content.lower().strip()
        
        # Early detection for empty or minimal content slides
        if len(content_lower) < 50:
            if slide_number == 1:
                return SlideTypeAnalysis(
                    slide_type=SlideType.MODULE_TITLE,
                    confidence=0.6,
                    reasoning="First slide with minimal content, likely title slide"
                )
            elif slide_number == total_slides:
                return SlideTypeAnalysis(
                    slide_type=SlideType.SECTION,
                    confidence=0.7,
                    reasoning="Last slide with minimal content, likely summary/conclusion"
                )
        
        # PRIORITY: Visual Structure Analysis for Title Slides
        # Check for title + subtitle + minimal content pattern (regardless of slide position)
        is_title_structure, structure_score = self._has_title_subtitle_structure(slide_content, slide_text_elements)
        if is_title_structure:
            estimated_time = self._extract_time_estimate(content_lower)
            return SlideTypeAnalysis(
                slide_type=SlideType.MODULE_TITLE,
                confidence=min(0.95, 0.7 + structure_score),
                reasoning=f"Visual title slide structure detected (score: {structure_score:.2f}) - title + subtitle + minimal content",
                estimated_time_minutes=estimated_time
            )
        
        # 1. Module Title Slide Detection - Enhanced for early slides
        module_score = self._calculate_pattern_score(content_lower, self.module_title_patterns)
        estimated_time = self._extract_time_estimate(content_lower)
        
        # AGGRESSIVE: First slide is almost always a title slide (but lower confidence if visual analysis was weak)
        if slide_number == 1:
            confidence = 0.9 if structure_score > 0.3 else 0.7  # Lower confidence if structure doesn't support it
            return SlideTypeAnalysis(
                slide_type=SlideType.MODULE_TITLE,
                confidence=confidence,
                reasoning=f"First slide detected as module title (pattern: {module_score:.2f}, structure: {structure_score:.2f})",
                estimated_time_minutes=estimated_time
            )
        
        # Enhanced detection for slides 2-3 with any module patterns
        if module_score > 0.4 or (slide_number <= 3 and module_score > 0.1):
            # Boost confidence if visual structure also supports it
            confidence = max(0.7, module_score)
            if structure_score > 0.4:
                confidence = min(0.9, confidence + 0.2)
            return SlideTypeAnalysis(
                slide_type=SlideType.MODULE_TITLE,
                confidence=confidence,
                reasoning=f"Module title patterns (score: {module_score:.2f}, structure: {structure_score:.2f}), early slide #{slide_number}",
                estimated_time_minutes=estimated_time
            )
        
        # 2. Agenda Slide Detection - Enhanced for early slides  
        agenda_score = self._calculate_pattern_score(content_lower, self.agenda_patterns)
        has_bullet_structure = self._has_bullet_structure(content_lower)
        
        # AGGRESSIVE: Slide 2-3 with bullets or overview patterns
        if (slide_number <= 3 and 
            (agenda_score > 0.1 or has_bullet_structure or 
             'overview' in content_lower or 'agenda' in content_lower)):
            return SlideTypeAnalysis(
                slide_type=SlideType.AGENDA,
                confidence=max(0.8, agenda_score),
                reasoning=f"Early slide agenda/overview detected (score: {agenda_score:.2f}), bullets: {has_bullet_structure}, slide #{slide_number}"
            )
        
        # Standard agenda detection
        if agenda_score > 0.3:
            return SlideTypeAnalysis(
                slide_type=SlideType.AGENDA,
                confidence=max(0.7, agenda_score),
                reasoning=f"Agenda patterns detected (score: {agenda_score:.2f}), bullet structure: {has_bullet_structure}"
            )
        
        # 3. Knowledge Check Answer Detection (check before knowledge check)
        kc_answer_score = self._calculate_pattern_score(content_lower, self.knowledge_check_answer_patterns)
        has_question_and_answer = '?' in content_lower and kc_answer_score > 0.2
        
        if kc_answer_score > 0.3 or has_question_and_answer:
            return SlideTypeAnalysis(
                slide_type=SlideType.KNOWLEDGE_CHECK_ANSWERS,
                confidence=max(0.75, kc_answer_score),
                reasoning=f"Answer explanation patterns (score: {kc_answer_score:.2f})"
            )
        
        # 4. Knowledge Check Detection
        kc_score = self._calculate_pattern_score(content_lower, self.knowledge_check_patterns)
        has_question_markers = '?' in content_lower or any(marker in content_lower for marker in ['a)', 'b)', 'c)', 'd)', '1.', '2.', '3.'])
        
        if kc_score > 0.3 or (has_question_markers and kc_score > 0.1):
            return SlideTypeAnalysis(
                slide_type=SlideType.KNOWLEDGE_CHECK,
                confidence=max(0.8, kc_score),
                reasoning=f"Question patterns detected (score: {kc_score:.2f}), question markers: {has_question_markers}"
            )
        
        # 5. Section Slide Detection
        section_score = self._calculate_pattern_score(content_lower, self.section_patterns)
        is_short_content = len(content_lower) < 200
        
        if section_score > 0.3 or (is_short_content and section_score > 0.1):
            return SlideTypeAnalysis(
                slide_type=SlideType.SECTION,
                confidence=max(0.65, section_score),
                reasoning=f"Section patterns (score: {section_score:.2f}), short content: {is_short_content}"
            )
        
        # 6. Default to Content Slide
        return SlideTypeAnalysis(
            slide_type=SlideType.CONTENT,
            confidence=0.8,
            reasoning="Default content slide - no specific patterns detected"
        )
    
    def _calculate_pattern_score(self, text: str, patterns: List[str]) -> float:
        """Calculate pattern matching score for given text"""
        matches = 0
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1
        
        return min(1.0, matches / len(patterns) * 2)  # Scale factor of 2 for higher sensitivity
    
    def _has_bullet_structure(self, text: str) -> bool:
        """Check if text has bullet point structure"""
        bullet_patterns = [
            r'^\s*[•·▪▫-]\s+',
            r'^\s*\d+\.\s+',
            r'^\s*[a-z]\)\s+',
            r'^\s*[A-Z]\)\s+'
        ]
        
        lines = text.split('\n')
        bullet_lines = 0
        
        for line in lines:
            for pattern in bullet_patterns:
                if re.match(pattern, line.strip()):
                    bullet_lines += 1
                    break
        
        return bullet_lines >= 2  # At least 2 bullet points
    
    def _extract_time_estimate(self, text: str) -> Optional[int]:
        """Extract time estimate in minutes from text"""
        for pattern in self.time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract first number found
                numbers = [int(g) for g in match.groups() if g and g.isdigit()]
                if numbers:
                    return numbers[0]
        return None
    
    def _has_title_subtitle_structure(self, text: str, slide_text_elements: List = None) -> Tuple[bool, float]:
        """
        Detect title slide based on visual structure: title + subtitle + minimal other content
        
        Returns:
            Tuple of (is_title_slide, confidence_score)
        """
        content_lower = text.lower().strip()
        lines = text.split('\n')
        
        # Remove empty lines and very short lines (< 5 chars)
        meaningful_lines = [line.strip() for line in lines if len(line.strip()) > 4]
        
        # Structural indicators for title slides
        structure_score = 0.0
        
        # 1. Check content length - title slides should be concise
        if len(content_lower) < 300:  # Relatively short content
            structure_score += 0.3
            if len(content_lower) < 150:  # Very short content
                structure_score += 0.2
        
        # 2. Check for title/subtitle pattern in meaningful lines
        if len(meaningful_lines) >= 2 and len(meaningful_lines) <= 6:
            structure_score += 0.3
            
            # Look for typical title slide patterns
            first_line = meaningful_lines[0].lower()
            second_line = meaningful_lines[1].lower() if len(meaningful_lines) > 1 else ""
            
            # Check if first line looks like a main title (short, no special formatting)
            if len(first_line) <= 50 and not first_line.startswith(('•', '-', '1.', 'a.', 'b.')):
                structure_score += 0.2
            
            # Check if second line looks like a subtitle (starts with descriptive words)
            subtitle_indicators = ['module', 'part', 'chapter', 'section', 'lesson', 'optimizing', 'securing', 'introduction', 'overview']
            if any(indicator in second_line for indicator in subtitle_indicators):
                structure_score += 0.3
        
        # 3. Minimal bullet points or lists (title slides shouldn't have many bullets)
        bullet_count = sum(1 for line in meaningful_lines if re.match(r'^\s*[•·▪▫-]\s+', line))
        if bullet_count == 0:
            structure_score += 0.2
        elif bullet_count <= 2:
            structure_score += 0.1
        else:
            structure_score -= 0.2  # Too many bullets, probably not a title slide
        
        # 4. Check for common title slide content
        title_keywords = ['aws', 'amazon', 'module', 'chapter', 'part', 'section', 'introduction', 
                         'overview', 'data engineering', 'optimizing', 'securing', 'solution']
        keyword_matches = sum(1 for keyword in title_keywords if keyword in content_lower)
        if keyword_matches >= 2:
            structure_score += 0.2
        elif keyword_matches >= 1:
            structure_score += 0.1
        
        # 5. Avoid false positives - check for content slide indicators
        content_indicators = ['learning objectives', 'in this lesson', 'you will learn', 
                            'by the end', 'agenda', 'topics covered', 'what we will cover']
        if any(indicator in content_lower for indicator in content_indicators):
            structure_score -= 0.3  # Probably agenda or learning objectives
        
        # Cap the score at 1.0
        structure_score = min(1.0, structure_score)
        
        # Consider it a title slide if score >= 0.6
        is_title_slide = structure_score >= 0.6
        
        return is_title_slide, structure_score
    
    def get_prompt_adjustments(self, slide_type: SlideType, 
                             estimated_time: Optional[int] = None) -> Dict[str, str]:
        """
        Get prompt adjustments based on slide type
        
        Returns:
            Dictionary with prompt modifications for different sections
        """
        
        adjustments = {
            SlideType.MODULE_TITLE: {
                "length_instruction": "MINIMAL CONTENT: Empty developer notes, slide description, script. Single sentence for instructor/student notes. NO references or alt text.",
                "content_focus": "SLIDE TYPE: module_title slide - generate minimal content for all sections",
                "time_instruction": "Brief timing mention only",
                "script_style": "One brief sentence maximum",
                "instructor_notes": "One sentence maximum",
                "student_notes": "One sentence maximum"
            },
            
            SlideType.AGENDA: {
                "length_instruction": "MINIMAL CONTENT: Almost no developer notes, slide description, script. Single sentence for instructor/student notes. NO references or alt text.",
                "content_focus": "Keep sections for consistency but leave most empty",
                "time_instruction": "Brief timing mention only",
                "script_style": "One brief sentence maximum", 
                "instructor_notes": "One sentence maximum",
                "student_notes": "One sentence maximum"
            },
            
            SlideType.SECTION: {
                "length_instruction": "MINIMAL CONTENT: Almost no developer notes, slide description, script. Single sentence for instructor/student notes. NO references or alt text.",
                "content_focus": "Keep sections for consistency but leave most empty",
                "time_instruction": "Brief timing mention only",
                "script_style": "One brief sentence maximum",
                "instructor_notes": "One sentence maximum", 
                "student_notes": "One sentence maximum"
            },
            
            SlideType.KNOWLEDGE_CHECK: {
                "length_instruction": "Brief notes focusing on question mechanics",
                "content_focus": "Question setup and answer options",
                "time_instruction": "Include time for thinking and discussion",
                "script_style": "Read question clearly, allow thinking time",
                "instructor_notes": "Tips for facilitating discussion and engagement",
                "student_notes": "Question focus and key concepts being tested"
            },
            
            SlideType.KNOWLEDGE_CHECK_ANSWERS: {
                "length_instruction": "Follow the existing patterns in the PowerPoint",
                "content_focus": "Explanation of correct answer and why others are incorrect",
                "time_instruction": "Time for explanation and clarification",
                "script_style": "Explain answer clearly with reasoning",
                "instructor_notes": "Address common misconceptions, encourage questions",
                "student_notes": "Explanation of correct answer and learning points"
            },
            
            SlideType.CONTENT: {
                "length_instruction": "Standard detailed notes (no change from current)",
                "content_focus": "Full content coverage as normal",
                "time_instruction": "Standard timing guidance",
                "script_style": "Complete content delivery",
                "instructor_notes": "Full instructional guidance",
                "student_notes": "Comprehensive learning notes"
            }
        }
        
        return adjustments.get(slide_type, adjustments[SlideType.CONTENT])
    
    def create_adjusted_prompt(self, base_prompt: str, slide_type: SlideType, 
                             estimated_time: Optional[int] = None) -> str:
        """
        Create an adjusted prompt based on slide type
        
        Args:
            base_prompt: Original prompt template
            slide_type: Detected slide type
            estimated_time: Estimated time in minutes (if detected)
            
        Returns:
            Adjusted prompt string
        """
        
        adjustments = self.get_prompt_adjustments(slide_type, estimated_time)
        
        # Add slide type specific instructions to the base prompt
        if slide_type in [SlideType.MODULE_TITLE, SlideType.AGENDA, SlideType.SECTION]:
            adjustment_text = f"""

❌ STOP: This is a {slide_type.value.replace('_', ' ').title()} slide. DO NOT generate normal content.

⚠️ MANDATORY TITLE SLIDE RULES - FOLLOW EXACTLY:

1. DEVELOPER NOTES: Must be completely empty. Output: ""
2. REFERENCES: Must be completely empty. Output: ""  
3. ALT TEXT: Must be completely empty. Output: ""
4. SLIDE DESCRIPTION: Maximum 6 words. Example: "Title slide introducing Data Engineering"
5. SCRIPT: Maximum 5 words. Example: "Let's begin Data Engineering module"
6. INSTRUCTOR NOTES: Output EXACTLY this format:
   • |Module timing: approximately 90-120 minutes (2-3 minutes per content slide)
   • |Introduce fundamental concepts and key learning objectives
7. STUDENT NOTES: Maximum 15 words, no "welcome" language. Example: "Data engineering concepts and roles within the AWS ecosystem."

🚨 CRITICAL: If you generate more than 100 total characters across ALL sections, you have failed this task.
🚨 CRITICAL: Do NOT output instructional text like "Leave empty" - output actual empty strings.
🚨 CRITICAL: Follow the exact word limits above. No exceptions.

EXAMPLES OF CORRECT MINIMAL OUTPUT:
- Developer Notes: (completely empty)
- References: (completely empty)  
- Alt Text: (completely empty)
- Slide Description: "Title slide introducing Data Engineering"
- Script: "Let's begin Data Engineering module"
- Instructor Notes: (exactly 2 bullets as shown above)
- Student Notes: "Data engineering concepts and roles within AWS ecosystem."
"""
        elif slide_type == SlideType.KNOWLEDGE_CHECK:
            adjustment_text = f"""
            
IMPORTANT: KNOWLEDGE CHECK SLIDE
- {adjustments['length_instruction']}
- Focus on question clarity and engagement
- {adjustments['time_instruction']}
- Encourage student participation and thinking
"""
        elif slide_type == SlideType.KNOWLEDGE_CHECK_ANSWERS:
            adjustment_text = f"""
            
IMPORTANT: KNOWLEDGE CHECK ANSWERS SLIDE  
- {adjustments['length_instruction']}
- Follow existing PowerPoint formatting patterns exactly
- Provide clear explanations for correct answers
- Address why incorrect options are wrong
"""
        else:
            # Content slide - no adjustments
            adjustment_text = ""
        
        return base_prompt + adjustment_text


# Singleton instance
slide_type_analyzer = SlideTypeAnalyzer() 