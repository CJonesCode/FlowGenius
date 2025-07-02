"""
Storage layer for BugIt issues.
Handles filesystem operations with atomic writes and proper error handling.
"""

import json
import uuid
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class StorageError(Exception):
    """Raised when storage operations fail"""
    pass

def ensure_issues_directory() -> Path:
    """Ensure .bugit/issues directory exists"""
    issues_dir = Path(".bugit/issues")
    issues_dir.mkdir(parents=True, exist_ok=True)
    return issues_dir

def save_issue(data: Dict) -> str:
    """
    Save issue data to filesystem with atomic write.
    Returns the UUID of the saved issue.
    """
    if not isinstance(data, dict):
        raise StorageError("Issue data must be a dictionary")
    
    # For stub: return predictable UUID for testing
    issue_id = data.get('id', str(uuid.uuid4())[:6])
    
    # Mock file write - actual implementation will use atomic writes
    # print(f"[STUB] Would save issue {issue_id} to .bugit/issues/{issue_id}.json")
    return issue_id

def load_issue(issue_id: str) -> Dict:
    """Load issue by ID from filesystem"""
    # Stub implementation - returns mock data
    return {
        "id": issue_id,
        "schema_version": "v1",
        "title": f"Mock Issue {issue_id}",
        "description": "This is a mock issue for testing",
        "tags": ["mock", "test"],
        "severity": "medium",
        "created_at": datetime.now().isoformat()
    }

def list_issues() -> List[Dict]:
    """Return list of all issues sorted by severity then created_at"""
    # Stub returns predictable test data
    return [
        {
            "id": "abc123",
            "schema_version": "v1", 
            "title": "Critical login issue",
            "description": "Users cannot log in",
            "tags": ["auth", "login"],
            "severity": "critical",
            "created_at": "2025-01-01T10:00:00"
        },
        {
            "id": "def456",
            "schema_version": "v1",
            "title": "UI rendering bug", 
            "description": "Button not displaying correctly",
            "tags": ["ui", "frontend"],
            "severity": "low",
            "created_at": "2025-01-01T11:00:00"
        }
    ]

def delete_issue(issue_id: str) -> bool:
    """Delete issue by ID. Returns True if successful."""
    # print(f"[STUB] Would delete issue {issue_id}")
    return True 