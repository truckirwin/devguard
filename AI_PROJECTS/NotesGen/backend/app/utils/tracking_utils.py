"""
Tracking utilities for generating meaningful operation tracking IDs.

This module provides utilities to generate unique tracking identifiers
for operations on PowerPoint files, using meaningful abbreviations
and timestamps for better debugging and log analysis.
"""

import time
import re
from pathlib import Path
from typing import Optional


def generate_tracking_id(ppt_filename: str, operation: str = "", slide_number: Optional[int] = None) -> str:
    """
    Generate a meaningful tracking ID for PPT operations.
    
    Format: {filename_abbrev}_{operation}_{slide}_{timestamp}
    Example: MLMLEA_M05_EXTRACT_S12_1749572449
    
    Args:
        ppt_filename: Name of the PowerPoint file
        operation: Operation type (EXTRACT, SAVE, GENERATE, etc.)
        slide_number: Slide number if applicable
        
    Returns:
        Meaningful tracking ID string
    """
    # Create filename abbreviation
    file_abbrev = _create_filename_abbreviation(ppt_filename)
    
    # Generate timestamp
    timestamp = int(time.time())
    
    # Build tracking ID components
    components = [file_abbrev]
    
    if operation:
        components.append(operation.upper())
    
    if slide_number is not None:
        components.append(f"S{slide_number}")
    
    components.append(str(timestamp))
    
    return "_".join(components)


def resolve_ppt_file_id(ppt_identifier: str, db) -> Optional[int]:
    """
    Resolve a PPT file ID from either tracking_id or numeric ID.
    
    Args:
        ppt_identifier: Either a tracking_id (string) or numeric ID (as string)
        db: Database session
        
    Returns:
        PPT file ID if found, None otherwise
    """
    from app.models.models import PPTFile
    
    # First try as tracking ID (preferred)
    ppt_file = db.query(PPTFile).filter(PPTFile.tracking_id == ppt_identifier).first()
    
    # If not found and identifier looks numeric, try as numeric ID (backward compatibility)
    if not ppt_file and ppt_identifier.isdigit():
        ppt_file = db.query(PPTFile).filter(PPTFile.id == int(ppt_identifier)).first()
    
    return ppt_file.id if ppt_file else None


def _create_filename_abbreviation(filename: str) -> str:
    """
    Create a meaningful abbreviation from a PowerPoint filename.
    
    Examples:
        - "MLMLEA_Mod05_Choosing_a_Modeling_Approach.pptx" -> "MLMLEA_M05"
        - "ILT-TF-200-DEA-10-EN_M01.pptx" -> "ILT_TF_200_M01"
        - "Master Generative AI Essentials v1.pptx" -> "MASTER_GEN_AI"
        - "Complex-Document_Name_With_Many_Parts.pptx" -> "COMPLEX_DOC_NAME"
    
    Args:
        filename: PowerPoint filename
        
    Returns:
        Abbreviated filename string
    """
    # Remove file extension
    name = Path(filename).stem
    
    # Replace common separators with underscores
    name = re.sub(r'[-\s\.]+', '_', name)
    
    # Remove common words and keep meaningful parts
    parts = name.upper().split('_')
    
    # Filter out common words but keep module/version indicators
    meaningful_parts = []
    for part in parts:
        if not part:
            continue
            
        # Keep module indicators
        if re.match(r'^M(OD)?\d+', part):  # M01, MOD05, etc.
            meaningful_parts.append(part.replace('MOD', 'M'))
            continue
            
        # Keep version indicators
        if re.match(r'^V\d+', part):  # V1, V2, etc.
            meaningful_parts.append(part)
            continue
            
        # Keep course codes and meaningful acronyms
        if len(part) >= 2 and (part.isalpha() or any(c.isdigit() for c in part)):
            # Skip common words
            if part not in ['THE', 'AND', 'OR', 'WITH', 'TO', 'FOR', 'OF', 'IN', 'ON', 'AT', 'BY']:
                meaningful_parts.append(part)
    
    # Limit to first 3-4 most meaningful parts to keep ID readable
    if len(meaningful_parts) > 4:
        # Try to keep the first part (likely course code) and last parts (likely module/version)
        if any(re.match(r'^M(OD)?\d+', part) for part in meaningful_parts[-2:]):
            # Keep first 2 and last 2 if module number is at the end
            abbreviated = meaningful_parts[:2] + meaningful_parts[-2:]
        else:
            # Keep first 4 parts
            abbreviated = meaningful_parts[:4]
    else:
        abbreviated = meaningful_parts
    
    # Join and limit total length
    result = '_'.join(abbreviated)
    
    # If still too long, truncate words but keep structure
    if len(result) > 20:
        truncated_parts = []
        for part in abbreviated:
            if re.match(r'^M(OD)?\d+', part) or re.match(r'^V\d+', part):
                # Keep module/version indicators intact
                truncated_parts.append(part)
            elif len(part) > 6:
                # Truncate long words but keep first letters
                truncated_parts.append(part[:6])
            else:
                truncated_parts.append(part)
        result = '_'.join(truncated_parts)
    
    # Ensure we have at least something meaningful
    if not result or len(result) < 3:
        # Fallback to first 8 chars of original name
        result = re.sub(r'[^A-Z0-9]', '', name.upper())[:8]
    
    return result


def parse_tracking_id(tracking_id: str) -> dict:
    """
    Parse a tracking ID back into its components.
    
    Args:
        tracking_id: Tracking ID string
        
    Returns:
        Dictionary with parsed components
    """
    parts = tracking_id.split('_')
    
    result = {
        'full_id': tracking_id,
        'filename_abbrev': None,
        'operation': None,
        'slide_number': None,
        'timestamp': None
    }
    
    if len(parts) < 2:
        return result
    
    # Last part should be timestamp
    try:
        result['timestamp'] = int(parts[-1])
        remaining_parts = parts[:-1]
    except ValueError:
        remaining_parts = parts
    
    # Look for slide number (format: S{number})
    slide_parts = [p for p in remaining_parts if p.startswith('S') and p[1:].isdigit()]
    if slide_parts:
        slide_part = slide_parts[-1]  # Take the last one
        result['slide_number'] = int(slide_part[1:])
        remaining_parts = [p for p in remaining_parts if p != slide_part]
    
    # Look for operation (common operations)
    operations = ['EXTRACT', 'SAVE', 'GENERATE', 'LOAD', 'PROCESS', 'CONVERT', 'ANALYZE']
    operation_parts = [p for p in remaining_parts if p in operations]
    if operation_parts:
        result['operation'] = operation_parts[-1]  # Take the last one
        remaining_parts = [p for p in remaining_parts if p not in operations]
    
    # Remaining parts form the filename abbreviation
    if remaining_parts:
        result['filename_abbrev'] = '_'.join(remaining_parts)
    
    return result


def format_tracking_log(tracking_id: str, message: str, level: str = "INFO") -> str:
    """
    Format a log message with tracking ID for consistent logging.
    
    Args:
        tracking_id: Tracking ID
        message: Log message
        level: Log level indicator
        
    Returns:
        Formatted log message
    """
    # Parse tracking ID for context
    parsed = parse_tracking_id(tracking_id)
    
    # Create context string
    context_parts = []
    if parsed['filename_abbrev']:
        context_parts.append(f"File:{parsed['filename_abbrev']}")
    if parsed['operation']:
        context_parts.append(f"Op:{parsed['operation']}")
    if parsed['slide_number']:
        context_parts.append(f"Slide:{parsed['slide_number']}")
    
    context = " | ".join(context_parts) if context_parts else "General"
    
    # Format with appropriate emoji
    emoji_map = {
        'INFO': '🔍',
        'SUCCESS': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'DEBUG': '🐛'
    }
    
    emoji = emoji_map.get(level.upper(), '📝')
    
    return f"{emoji} TRACK[{tracking_id}] {context} - {message}" 