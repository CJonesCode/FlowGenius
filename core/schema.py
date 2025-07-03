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
    Returns a new dictionary without modifying the original.
    """
    if not isinstance(data, dict):
        raise ValidationError("Issue data must be a dictionary")
    
    # Make a copy to avoid modifying the original
    result = data.copy()
    
    # Generate ID if missing
    if 'id' not in result:
        result['id'] = str(uuid.uuid4())[:6]
    
    # Required schema version - preserve existing or default to v1
    if 'schema_version' not in result or not isinstance(result['schema_version'], str):
        result['schema_version'] = 'v1'
    
    # Validate and default title
    if 'title' not in result or not result['title']:
        raise ValidationError("Title is required")
    
    title = str(result['title']).strip()
    if len(title) > 120:
        title = title[:117] + "..."
    result['title'] = title
    
    # Validate description
    if 'description' not in result:
        result['description'] = ''
    
    description = str(result['description']).strip()
    if len(description) > 10000:
        description = description[:9997] + "..."
    result['description'] = description
    
    # Validate severity
    severity = result.get('severity', 'medium')
    if severity is None:
        severity = 'medium'
    else:
        severity = str(severity).lower()
    if severity not in VALID_SEVERITIES:
        severity = 'medium'
    result['severity'] = severity
    
    # Validate type
    issue_type = result.get('type', 'unknown')
    if issue_type not in VALID_TYPES:
        issue_type = 'unknown'
    result['type'] = issue_type
    
    # Validate tags
    tags = result.get('tags', [])
    if not isinstance(tags, list):
        tags = []
    # Make a copy of the tags list to avoid modifying the original
    result['tags'] = [str(tag).strip() for tag in tags if str(tag).strip() and str(tag).strip() != 'None']
    
    # Add timestamp
    if 'created_at' not in result:
        result['created_at'] = datetime.now().isoformat()
    
    return result

def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate .bugitrc configuration data with defaults"""
    if config is None:
        config = {}
    
    if not isinstance(config, dict):
        config = {}
    
    # Apply defaults for common config fields
    defaults = {
        'model': 'gpt-4',
        'enum_mode': 'auto', 
        'output_format': 'table',
        'retry_limit': 3
    }
    
    # Start with defaults and update with provided config
    result = defaults.copy()
    result.update(config)
    
    # Validate specific fields
    if not isinstance(result.get('model'), str) or not result['model']:
        result['model'] = 'gpt-4'
    
    if result.get('enum_mode') not in ['auto', 'strict', 'suggestive']:
        result['enum_mode'] = 'auto'
    
    if result.get('output_format') not in ['table', 'json', 'yaml']:
        result['output_format'] = 'table'
    
    if not isinstance(result.get('retry_limit'), int) or result['retry_limit'] < 1 or result['retry_limit'] > 20:
        result['retry_limit'] = 3
    
    return result 