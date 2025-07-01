# BugIt CLI Implementation Plan

## Overview

This implementation plan follows a systematic, incremental approach where each component can be tested independently before integration. The architecture prioritizes modularity, testability, and reliability - core tenets of solid software engineering.

---

## Phase 0: Environment Setup & Foundation

### Step 0.1: Development Environment

**Prerequisites:**
- Python 3.9+ 
- pip or poetry for dependency management
- Git for version control

**Setup Instructions:**

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install typer rich langchain-core langchain-openai python-dotenv pydantic

# Development dependencies
pip install pytest pytest-cov black isort mypy types-requests

# Create requirements.txt
pip freeze > requirements.txt
```

**Project Structure:**
```
BugIt/
├── .venv/                    # Virtual environment
├── .gitignore               # Python, IDE, OS ignores
├── requirements.txt         # Production dependencies  
├── requirements-dev.txt     # Development dependencies
├── .bugitrc.example         # Example configuration
├── README.md               # Setup and usage instructions
├── cli.py                  # Main CLI entry point
├── commands/               # CLI command implementations
├── core/                   # Core business logic
├── tests/                  # Test suite
└── .bugit/                 # Runtime directory (created by app)
    └── issues/             # Issue storage
```

### Step 0.2: Testing Infrastructure

**Test Categories:**
1. **Unit Tests**: Individual function/class testing
2. **Integration Tests**: Component interaction testing  
3. **CLI Tests**: End-to-end command testing
4. **Mock Tests**: LLM API mocking for deterministic testing

**Test Configuration:**
- pytest.ini for test discovery
- conftest.py for shared fixtures
- Mock LLM responses for deterministic testing
- Temporary directory fixtures for file operations

---

## Phase 1: Core Infrastructure & Stubs

### Step 1.1: Enhanced Stubs with Contracts

Create testable stubs that define clear interfaces and return predictable data structures. Each stub should:
- Have proper type hints
- Include docstrings with expected behavior
- Return realistic mock data
- Include basic validation
- Raise appropriate exceptions for invalid inputs

**core/storage.py - Enhanced Storage Stub:**
```python
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
    print(f"[STUB] Would save issue {issue_id} to .bugit/issues/{issue_id}.json")
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
    print(f"[STUB] Would delete issue {issue_id}")
    return True
```

### Step 1.2: Schema Validation Stub

**core/schema.py - Schema Validation:**
```python
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
```

### Step 1.3: Model Processing Stub

**core/model.py - LangGraph Integration Stub:**
```python
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
```

### Step 1.4: Configuration Management Stub

**core/config.py - Configuration Handling:**
```python
"""
Configuration management for BugIt.
Handles .bugitrc file parsing, environment variables, and CLI overrides.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigError(Exception):
    """Raised when configuration is invalid or missing"""
    pass

DEFAULT_CONFIG = {
    'model': 'gpt-4',
    'enum_mode': 'auto',
    'api_key': None
}

def load_config() -> Dict[str, Any]:
    """
    Load configuration from .bugitrc, environment variables, and defaults.
    Priority: CLI args > env vars > .bugitrc > defaults
    """
    config = DEFAULT_CONFIG.copy()
    
    # Load from .bugitrc if it exists
    bugitrc_path = Path('.bugitrc')
    if bugitrc_path.exists():
        try:
            with open(bugitrc_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ConfigError(f"Invalid .bugitrc file: {e}")
    
    # Override with environment variables
    if 'BUGIT_API_KEY' in os.environ:
        config['api_key'] = os.environ['BUGIT_API_KEY']
    if 'BUGIT_MODEL' in os.environ:
        config['model'] = os.environ['BUGIT_MODEL']
    
    return config

def save_config(config: Dict[str, Any], filepath: str = '.bugitrc') -> None:
    """Save configuration to file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"[STUB] Configuration saved to {filepath}")
    except Exception as e:
        raise ConfigError(f"Failed to save config: {e}")

def get_config_value(key: str) -> Any:
    """Get specific configuration value"""
    config = load_config()
    return config.get(key)

def set_config_value(key: str, value: Any) -> None:
    """Set specific configuration value"""
    config = load_config()
    config[key] = value
    save_config(config)
```

---

## Phase 2: Command Implementation

### Step 2.1: Testing Infrastructure Setup

**tests/conftest.py - Test Fixtures:**
```python
import pytest
import tempfile
import shutil
from pathlib import Path
import os

@pytest.fixture
def temp_dir():
    """Create temporary directory for test isolation"""
    temp_dir = tempfile.mkdtemp()
    old_cwd = os.getcwd()
    os.chdir(temp_dir)
    yield Path(temp_dir)
    os.chdir(old_cwd) 
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return {
        'api_key': 'test-key-123',
        'model': 'gpt-4',
        'enum_mode': 'auto'
    }

@pytest.fixture  
def sample_issue():
    """Sample issue data for testing"""
    return {
        'id': 'test123',
        'schema_version': 'v1',
        'title': 'Test issue',
        'description': 'This is a test issue',
        'tags': ['test'],
        'severity': 'medium',
        'created_at': '2025-01-01T12:00:00'
    }
```

### Step 2.2: Individual Command Implementation

**Implementation Order:**
1. `bugit new` - Core functionality first
2. `bugit list` - Basic data retrieval  
3. `bugit show` - Single item display
4. `bugit config` - Configuration management
5. `bugit edit` - Data modification
6. `bugit delete` - Data removal

Each command will be implemented with:
- Full functionality
- Comprehensive error handling
- Unit tests
- Integration tests
- CLI integration tests

---

## Phase 3: Integration & LangGraph Implementation

### Step 3.1: LangGraph Pipeline

**Real LangGraph Implementation:**
- Define processing graph with nodes for:
  - Input validation
  - LLM processing  
  - Output validation
  - Error recovery
- Implement retry logic and fallback models
- Add proper API key management
- Include token usage tracking

### Step 3.2: File System Operations

**Atomic File Operations:**
- Implement write-then-rename for atomic updates
- Add file locking for concurrent access
- Include proper error handling and rollback
- Add backup/recovery mechanisms

### Step 3.3: Index Management

**Issue Indexing System:**
- Dynamic index generation for `show`, `edit`, `delete` commands
- Consistent sorting (severity desc, created_at desc)
- Index caching with invalidation
- Support for filtering and search

---

## Phase 4: Polish & Production Readiness

### Step 4.1: Error Handling & Validation

**Comprehensive Error Handling:**
- Custom exception hierarchy
- Graceful degradation for API failures
- User-friendly error messages
- Debug mode with detailed logging

### Step 4.2: Performance & Reliability

**Optimization:**
- Lazy loading for large issue lists
- Efficient JSON parsing
- Memory usage optimization
- Concurrent operation safety

### Step 4.3: User Experience

**CLI Experience:**
- Rich formatting with colors and tables
- Progress indicators for LLM processing
- Helpful error messages and suggestions
- Comprehensive help text

---

## Testing Strategy

### Unit Tests (70% coverage target)
- All core functions tested in isolation
- Mock external dependencies (LLM APIs, filesystem)
- Test edge cases and error conditions
- Validate data transformations

### Integration Tests (20% coverage target)  
- Component interaction testing
- End-to-end workflow validation
- Configuration loading and validation
- File system operations

### CLI Tests (10% coverage target)
- Command line interface testing
- Argument parsing and validation
- Output format verification
- Error message testing

### Test Execution
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/cli/
```

---

## Deployment & Distribution

### Step 5.1: Package Structure
- Setup.py for pip installation
- Entry point configuration
- Dependency management
- Version management

### Step 5.2: Documentation
- README with quick start guide
- API documentation
- Configuration reference
- Troubleshooting guide

---

## Success Criteria

**Phase 1 Complete:**
- All stubs implemented and testable
- Basic test infrastructure working
- Clean imports and module structure

**Phase 2 Complete:**  
- All CLI commands functional
- Core workflows working end-to-end
- Comprehensive test coverage

**Phase 3 Complete:**
- LangGraph integration working
- Production-quality file operations
- Reliable concurrent usage

**Phase 4 Complete:**
- User-ready CLI experience
- Comprehensive error handling
- Performance optimized

This plan ensures each phase builds on solid foundations while maintaining testability and modularity throughout the development process. 