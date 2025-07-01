"""
Schema validation and data transformation for BugIt issues.
Ensures all data conforms to the expected structure with proper defaults.
"""

from typing import Dict, List, Any
from datetime import datetime
import uuid

VALID_SEVERITIES = ["low", "medium", "high", "critical"]
VALID_TYPES = ["bug", "feature", "chore", "unknown"]

class ValidationError(Exception):
    """Raised when data validation fails"""
    pass

def validate_or_default(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate issue data and apply defaults where needed.
    Throws ValidationError for critical validation failures.
    """
    if not isinstance(data, dict):
        raise ValidationError("Issue data must be a dictionary")
    
    # Generate ID if missing
    if 'id' not in data:
        data['id'] = str(uuid.uuid4())[:6]
    
    # Required schema version
    data['schema_version'] = 'v1'
    
    # Validate and default title
    if 'title' not in data or not data['title']:
        raise ValidationError("Title is required")
    
    title = str(data['title']).strip()
    if len(title) > 120:
        title = title[:117] + "..."
    data['title'] = title
    
    # Validate description
    if 'description' not in data:
        data['description'] = data.get('title', 'No description provided')
    
    description = str(data['description']).strip()
    if len(description) > 10000:
        description = description[:9997] + "..."
    data['description'] = description
    
    # Validate severity
    severity = data.get('severity', 'medium').lower()
    if severity not in VALID_SEVERITIES:
        severity = 'medium'
    data['severity'] = severity
    
    # Validate type
    issue_type = data.get('type', 'unknown')
    if issue_type not in VALID_TYPES:
        issue_type = 'unknown'
    data['type'] = issue_type
    
    # Validate tags
    tags = data.get('tags', [])
    if not isinstance(tags, list):
        tags = []
    data['tags'] = [str(tag).strip() for tag in tags if str(tag).strip()]
    
    # Add timestamp
    if 'created_at' not in data:
        data['created_at'] = datetime.now().isoformat()
    
    return data

def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate .bugitrc configuration data"""
    # Stub implementation
    required_fields = ['api_key', 'model']
    
    for field in required_fields:
        if field not in config:
            raise ValidationError(f"Missing required config field: {field}")
    
    return config 