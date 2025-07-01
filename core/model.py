"""
LangGraph integration for processing bug descriptions into structured data.
This module interfaces with LLM APIs to transform freeform text into JSON.
"""

from typing import Dict, Any
import json
import re

class ModelError(Exception):
    """Raised when model processing fails"""
    pass

def process_description(description: str) -> Dict[str, Any]:
    """
    Process freeform bug description using LangGraph.
    Returns structured data ready for validation.
    """
    if not description or not description.strip():
        raise ModelError("Description cannot be empty")
    
    # Stub implementation - uses rule-based processing for testing
    # Real implementation will use LangGraph + LLM
    
    # Simple keyword-based severity detection
    desc_lower = description.lower()
    if any(word in desc_lower for word in ['crash', 'hang', 'critical', 'fatal', 'broken']):
        severity = 'critical'
    elif any(word in desc_lower for word in ['slow', 'minor', 'cosmetic']):
        severity = 'low'  
    elif any(word in desc_lower for word in ['error', 'bug', 'issue', 'problem']):
        severity = 'high'
    else:
        severity = 'medium'
    
    # Extract potential tags
    tags = []
    if 'login' in desc_lower or 'auth' in desc_lower:
        tags.append('auth')
    if 'ui' in desc_lower or 'interface' in desc_lower:
        tags.append('ui')
    if 'camera' in desc_lower:
        tags.append('camera')
    if 'logout' in desc_lower:
        tags.append('logout')
    
    # Generate title (first sentence or truncated description)
    sentences = re.split(r'[.!?]+', description.strip())
    title = sentences[0].strip() if sentences else description.strip()
    if len(title) > 80:
        title = title[:77] + "..."
    
    return {
        'title': title,
        'description': description.strip(),
        'severity': severity,
        'type': 'bug',  # Default for stub
        'tags': tags
    }

def setup_langgraph():
    """Initialize LangGraph pipeline - stub implementation"""
    print("[STUB] LangGraph pipeline initialized")
    return True

def test_model_connection() -> bool:
    """Test connection to LLM API"""
    print("[STUB] Model connection test passed")
    return True 