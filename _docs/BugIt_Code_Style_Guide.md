# BugIt CLI Code Style Guide

## Overview

This document establishes the coding standards, architecture principles, and conventions for BugIt CLI. These guidelines ensure consistency, maintainability, and production quality across the codebase.

**Philosophy**: Write clean, functional, AI-readable code that prioritizes clarity, modularity, and testability.

---

## Architecture Principles

### 1. **Functional Programming First**
- ✅ **Prefer functions over classes** - Use classes only when managing complex state
- ✅ **Pure functions** - Functions should have predictable inputs/outputs
- ✅ **Immutability** - Avoid modifying data in place; return new objects
- ✅ **Declarative over imperative** - Express what you want, not how to do it

```python
# ✅ Good - Functional approach
def validate_severity(severity: str) -> str:
    """Validate and normalize severity value."""
    severity_map = {
        'low': 'low',
        'medium': 'medium', 
        'high': 'high',
        'critical': 'critical'
    }
    return severity_map.get(severity.lower(), 'medium')

# ❌ Avoid - Class for simple validation
class SeverityValidator:
    def validate(self, severity: str) -> str:
        # Implementation...
```

### 2. **Module Organization**
```
project/
├── cli.py              # Entry point only
├── commands/           # CLI layer - user interface
├── core/              # Business logic layer  
├── tests/             # Test layer
└── _docs/             # Documentation
```

**Layer Responsibilities:**
- **`commands/`**: CLI parsing, output formatting, orchestration
- **`core/`**: Business logic, data processing, storage
- **`tests/`**: Comprehensive testing with clear organization

### 3. **Error Handling Strategy**
- ✅ **Throw errors instead of fallback values** - Make failures explicit
- ✅ **Structured error hierarchy** - Custom exceptions for different error types
- ✅ **Consistent error responses** - JSON errors for automation, pretty errors for humans

```python
# ✅ Good - Explicit error handling
def load_issue(issue_id: str) -> dict:
    """Load issue by ID or raise StorageError."""
    if not issue_file.exists():
        raise StorageError(f"Issue {issue_id} not found")
    return read_json_file(issue_file)

# ❌ Avoid - Silent fallbacks
def load_issue(issue_id: str) -> dict:
    """Load issue by ID or return empty dict."""
    try:
        return read_json_file(issue_file)
    except:
        return {}  # Silent failure hides problems
```

---

## Code Conventions

### 1. **Function Design**

**Every function must have:**
- ✅ **Descriptive docstring** with purpose and parameters
- ✅ **Type hints** for all parameters and return values
- ✅ **Single responsibility** - One clear purpose per function
- ✅ **Descriptive name** with auxiliary verbs when appropriate

```python
def validate_or_default(raw_data: dict) -> dict:
    """
    Validate issue data and apply defaults for missing fields.
    
    Args:
        raw_data: Raw issue data from user input or AI processing
        
    Returns:
        Validated issue dict with all required fields and defaults applied
        
    Raises:
        ValidationError: If required fields are missing or invalid
    """
    # Implementation...
```

### 2. **Variable Naming**

**Use descriptive names with auxiliary verbs:**
```python
# ✅ Good - Descriptive with auxiliary verbs
is_loading = True
has_error = False
can_process = check_api_key()
should_retry = attempt_count < max_retries

# ✅ Good - Clear descriptive names
issue_file_path = get_issue_path(issue_id)
validated_severity = normalize_severity(raw_severity)
storage_stats = calculate_storage_statistics()

# ❌ Avoid - Unclear abbreviations
data = get_stuff()
res = process_thing()
tmp = create_temp()
```

### 3. **Data Structures**

**Use maps/dicts instead of enums:**
```python
# ✅ Good - Maps for flexibility
SEVERITY_LEVELS = {
    'low': 1,
    'medium': 2, 
    'high': 3,
    'critical': 4
}

SEVERITY_COLORS = {
    'low': 'dim',
    'medium': 'yellow',
    'high': 'red', 
    'critical': 'red'
}

# ❌ Avoid - Enums are less flexible
from enum import Enum
class Severity(Enum):
    LOW = 1
    MEDIUM = 2
    # Harder to extend and modify
```

### 4. **Control Flow**

**Avoid unnecessary braces; use concise syntax:**
```python
# ✅ Good - Concise conditionals
if not issue_id:
    raise ValueError("Issue ID required")

severity = 'critical' if is_system_crash else 'medium'

# Return early to reduce nesting
if not api_key:
    return {"error": "API key required"}

# ✅ Good - Simple conditions without extra braces
result = process_data() if has_valid_input else None
```

---

## File Organization

### 1. **File Structure Standards**

**Every Python file must have:**
```python
"""
Module description explaining purpose and main functionality.
Include any important usage notes or architectural decisions.
"""

# Standard library imports
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Third-party imports  
import typer
from rich.console import Console

# Local imports
from core import storage, schema
from core.styles import Colors, Styles

# Module constants
DEFAULT_CONFIG = {
    'model': 'gpt-4',
    'retry_limit': 3
}

# Function definitions with proper spacing
def main_function():
    """Function description."""
    pass
```

### 2. **File Length Limits**
- ✅ **Maximum 500 lines per file** - For AI tool compatibility
- ✅ **Split large files** into logical modules
- ✅ **Group related functions** in the same file

### 3. **Import Organization**
```python
# 1. Standard library (alphabetical)
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# 2. Third-party packages (alphabetical)
import typer
from rich.console import Console

# 3. Local imports (alphabetical)
from core import storage, schema
from core.styles import Colors, Styles
```

---

## Documentation Standards

### 1. **Docstring Format**
```python
def complex_function(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """
    Brief description of what the function does.
    
    Longer description if needed explaining the approach,
    important behavior, or architectural decisions.
    
    Args:
        param1: Description of first parameter
        param2: Description of optional parameter (default: None)
        
    Returns:
        Description of return value and structure
        
    Raises:
        SpecificError: When this specific condition occurs
        AnotherError: When this other condition occurs
        
    Example:
        >>> result = complex_function("test", 42)
        >>> assert result["status"] == "success"
    """
```

### 2. **Module Documentation**
```python
"""
Module name and primary responsibility.

This module handles [specific functionality] and provides the main
interface for [specific operations]. Key architectural decisions:

- Decision 1: Rationale and implications
- Decision 2: Rationale and implications

Usage:
    from module import main_function
    result = main_function(data)
"""
```

### 3. **Code Comments**
```python
# Explain WHY, not WHAT
def process_issue(data: dict) -> dict:
    # AI responses sometimes include extra fields - filter to schema
    filtered_data = {k: v for k, v in data.items() if k in REQUIRED_FIELDS}
    
    # Generate UUID here rather than in AI to ensure uniqueness
    filtered_data['id'] = generate_unique_id()
    
    return filtered_data
```

---

## Testing Standards

### 1. **Test Organization**
```python
"""
Test module for specific functionality.
Tests cover [what aspects] with focus on [key behaviors].
"""

import pytest
from unittest.mock import patch, MagicMock

# Group related tests in classes
class TestFunctionGroup:
    """Test related functionality together."""
    
    def test_normal_case(self):
        """Test the expected happy path."""
        pass
        
    def test_edge_case(self):
        """Test boundary conditions."""
        pass
        
    def test_error_case(self):
        """Test error handling."""
        pass
```

### 2. **Test Patterns**
- ✅ **Arrange, Act, Assert** pattern
- ✅ **Descriptive test names** explaining the scenario
- ✅ **One assertion per test** when possible
- ✅ **Mock external dependencies** for unit tests

```python
def test_validate_severity_with_invalid_input_returns_default():
    """Test that invalid severity values return 'medium' default."""
    # Arrange
    invalid_severity = "invalid_value"
    expected_default = "medium"
    
    # Act
    result = validate_severity(invalid_severity)
    
    # Assert
    assert result == expected_default
```

---

## CLI Design Patterns

### 1. **Dual Output Format Standard**

**Every command must support both JSON and pretty output:**
```python
def command_function(
    args: str,
    pretty_output: bool = typer.Option(False, "-p", "--pretty", help="Human-readable output")
):
    """
    Command description.
    
    Default output is JSON for automation.
    Use --pretty for human-readable output.
    """
    try:
        # Process command logic
        result = process_command(args)
        
        if pretty_output:
            # Human-readable output with Rich formatting
            console = Console()
            console.print("Success:", style=Colors.SUCCESS)
            display_pretty_result(result)
        else:
            # JSON output for automation
            output = {"success": True, "data": result}
            typer.echo(json.dumps(output, indent=2))
            
    except Exception as e:
        error_msg = f"Error: {e}"
        if pretty_output:
            console = Console()
            console.print(Styles.error(error_msg))
        else:
            output = {"success": False, "error": error_msg}
            typer.echo(json.dumps(output, indent=2))
        raise typer.Exit(1)
```

### 2. **Error Response Consistency**
```python
# JSON error format (for automation)
{
    "success": false,
    "error": "Issue not found: abc123",
    "code": "STORAGE_ERROR"
}

# Pretty error format (for humans)
# Red colored text with clear messaging
```

### 3. **Short Flag Support**
```python
# Support both long and short flags for common options
pretty_output: bool = typer.Option(False, "-p", "--pretty")
severity: str = typer.Option(None, "-s", "--severity") 
force: bool = typer.Option(False, "-f", "--force")
```

---

## Security Guidelines

### 1. **Configuration Separation**
```python
# API keys ONLY use environment variables, configuration uses .bugitrc
def load_config() -> Dict[str, Any]:
    """Load configuration with clear separation."""
    config = DEFAULT_PREFERENCES.copy()
    
    # 1. Load preferences from .bugitrc only
    if Path('.bugitrc').exists():
        with open('.bugitrc', 'r') as f:
            config.update(json.load(f))
    
    # 2. API keys ONLY from environment variables
    config['openai_api_key'] = os.environ.get('BUGIT_OPENAI_API_KEY')
    config['anthropic_api_key'] = os.environ.get('BUGIT_ANTHROPIC_API_KEY')
    config['google_api_key'] = os.environ.get('BUGIT_GOOGLE_API_KEY')
    
    # NO environment variable overrides for configuration
    return config
```

### 2. **Secrets Management**
- ✅ **API keys in .env file only** (git-ignored)
- ✅ **User preferences in .bugitrc** (version controlled)
- ✅ **NO environment variable overrides for configuration** (security principle)
- ✅ **Environment variables ONLY for API keys** (clear separation)
- ✅ **Never log sensitive data**
- ✅ **Mask API keys in output**

---

## Performance Guidelines

### 1. **File Operations**
```python
# ✅ Good - Atomic operations
def save_issue_atomically(issue_data: dict) -> str:
    """Save issue with atomic write-then-rename pattern."""
    temp_file = issue_file.with_suffix('.tmp')
    
    # Write to temporary file first
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(issue_data, f, indent=2)
    
    # Atomic rename
    temp_file.rename(issue_file)
    return issue_data['id']
```

### 2. **Memory Management**
```python
# ✅ Good - Process files incrementally for large datasets
def list_issues_efficiently() -> List[dict]:
    """Load issues without keeping all in memory simultaneously."""
    issues = []
    for issue_file in get_issue_files():
        # Load only what we need
        issue_summary = load_issue_summary(issue_file)
        issues.append(issue_summary)
    return sorted(issues, key=sort_key)
```

---

## Code Quality Checklist

### Before Committing:
- [ ] ✅ All functions have descriptive docstrings
- [ ] ✅ Type hints on all parameters and return values  
- [ ] ✅ Variable names use auxiliary verbs where appropriate
- [ ] ✅ Error handling throws explicit exceptions
- [ ] ✅ Tests cover normal, edge, and error cases
- [ ] ✅ Commands support both JSON and pretty output
- [ ] ✅ No sensitive data in version control
- [ ] ✅ File length under 500 lines
- [ ] ✅ Imports properly organized
- [ ] ✅ No unnecessary complexity or abstractions

### Code Review Focus:
- [ ] ✅ **Functionality**: Does it work correctly?
- [ ] ✅ **Readability**: Is the intent clear?
- [ ] ✅ **Testability**: Can it be easily tested?
- [ ] ✅ **Security**: Are secrets handled properly?
- [ ] ✅ **Performance**: Are file operations atomic?
- [ ] ✅ **Consistency**: Does it follow established patterns?

---

## AI-First Development

### 1. **AI Tool Compatibility**
- ✅ **File length limits** - Maximum 500 lines for optimal AI processing
- ✅ **Clear module boundaries** - Easy for AI to understand scope
- ✅ **Comprehensive docstrings** - AI can understand functionality
- ✅ **Consistent patterns** - AI can recognize and extend patterns

### 2. **Modular Architecture**
```python
# ✅ Good - Clear module responsibilities
# core/storage.py - File operations only
# core/schema.py - Data validation only  
# core/model.py - AI processing only
# commands/new.py - CLI parsing and orchestration only
```

### 3. **Self-Documenting Code**
```python
# ✅ Good - Code explains itself
def validate_or_default(raw_data: dict) -> dict:
    """Apply validation rules and generate defaults for missing fields."""
    validated_issue = ensure_required_fields(raw_data)
    validated_issue = normalize_field_values(validated_issue)
    validated_issue = add_missing_defaults(validated_issue)
    return validated_issue

# Each function name clearly indicates its purpose
```

---

## Output Standards

### 1. **Professional Output**
- ✅ **No emojis** - Professional, clean appearance
- ✅ **Consistent colors** - Use established color scheme
- ✅ **Structured formatting** - Tables, panels, clear hierarchy

### 2. **Color Scheme** (from core/styles.py)
```python
COLORS = {
    'BRAND': 'blue',           # Prompts, borders
    'INTERACTIVE': 'cyan',     # Commands, indices  
    'ERROR': 'red',           # Errors, critical severity
    'SUCCESS': 'green',       # Success, dates
    'WARNING': 'yellow',      # Tags, warnings
    'IDENTIFIER': 'magenta',  # UUIDs, identifiers
    'PRIMARY': 'white',       # Titles, main content
    'SECONDARY': 'dim'        # Descriptions, secondary text
}
```

---

This style guide ensures consistency, maintainability, and production quality across the BugIt CLI codebase. Follow these patterns to maintain the established architecture and make the code AI-friendly for future development. 