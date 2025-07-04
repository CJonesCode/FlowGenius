# BugIt CLI

**Status: Production Ready ✅** - AI-powered bug report management with unified CLI and comprehensive automation features.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Interface Options](#interface-options)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Development](#development)
- [File Structure](#file-structure)
## Overview

BugIt is a CLI-first tool that enables developers to quickly capture unstructured bug reports without interrupting their development flow. It integrates with LangGraph AI backend to transform freeform bug descriptions into structured JSON files with professional styling and industry-standard CLI conventions.

**Current Implementation:** All 6 core commands are functional with **real LangGraph integration** using OpenAI API, **production file operations** with atomic writes, **CLI scriptability-first design**, and **comprehensive test coverage** (447 tests, 91% coverage).

## Key Features

### 🤖 AI Integration
- **LangGraph Framework**: Real OpenAI API integration with GPT-4 processing
- **Structured Output**: Pydantic validation with retry logic
- **Multi-provider Ready**: Architecture supports Anthropic/Google (planned)

### 🛠️ CLI Scriptability
- **JSON by Default**: Perfect for automation and CI/CD pipelines
- **POSIX Exit Codes**: Standard error codes (0=success, 1-7=specific errors)
- **Stream Separation**: stdout for data, stderr for messages (perfect for piping)
- **Standard Flags**: `--version`, `--verbose`, `--quiet`, `--no-color`, `--pretty`

### 💾 Storage & Safety
- **Atomic Operations**: Write-then-rename pattern with cross-platform locking
- **Individual JSON Files**: One file per issue with dynamic indexing
- **Backup System**: Automatic backups on delete with recovery
- **Corrupted File Handling**: Graceful error handling and recovery

### 🎨 Professional Interface
- **Rich Styling**: Beautiful panels, tables, and formatted output
- **Centralized Design**: Consistent colors and semantic formatting
- **Interactive Shell**: Human-optimized mode with pretty output by default
- **Typer Integration**: Auto-generated help with professional formatting

### 📊 Core Commands
| Command | Description | Example |
|---------|-------------|---------|
| `new` | Create AI-powered bug report | `bugit new "Critical login issue"` |
| `list` | List with filtering and sorting | `bugit list --severity critical` |
| `show` | Display detailed issue info | `bugit show 1 --pretty` |
| `edit` | Modify existing issues | `bugit edit 1 --add-tag urgent` |
| `delete` | Remove issues (with backup) | `bugit delete 1 --force` |
| `config` | Manage configuration | `bugit config --set-api-key openai <key>` |

## Interface Options

### 1. **Unified Entry Point** (Recommended)
```bash
# CLI Mode (with arguments) - JSON for automation
python bugit.py new "Critical bug" | jq '.issue.id'

# Human Mode (with --pretty) - Beautiful output
python bugit.py list --pretty

# Interactive Shell (no arguments) - Human-optimized
python bugit.py
BugIt> new "Bug description"
BugIt> list
BugIt> exit
```

### 2. **Direct CLI Mode** (Advanced)
```bash
# Direct CLI access for advanced automation
python cli.py new "Critical bug"
python cli.py list --severity critical | jq '.[] | .id'
```

## Quick Start

### Installation
```bash
# 1. Clone and setup
git clone <repository-url>
cd BugIt
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
python bugit.py config --set-api-key openai sk-your-openai-api-key-here
```

### First Bug Report
```bash
# Create your first bug report
python bugit.py new "Login page crashes on mobile devices" --pretty

# List all issues
python bugit.py list --pretty

# Show detailed view
python bugit.py show 1 --pretty
```

## Usage Examples

### Automation & Scripting
```bash
# Extract issue IDs for batch processing
python bugit.py list | jq -r '.[].id'

# Filter and process critical issues
python bugit.py list --severity critical | jq '.[] | select(.severity == "critical")'

# Create issue and get ID for follow-up
ISSUE_ID=$(python bugit.py new "Critical bug" | jq -r '.issue.id')
python bugit.py edit $ISSUE_ID --add-tag urgent

# CI/CD Integration
if [ "$TEST_FAILED" = "true" ]; then
  ISSUE_ID=$(python bugit.py new "Test failure in $BUILD_ID" | jq -r '.issue.id')
  python bugit.py edit $ISSUE_ID --severity critical --add-tag ci-cd
fi
```

### Interactive Usage
```bash
# Start interactive shell
python bugit.py

BugIt> new "Authentication fails after timeout"
BugIt> list -s critical
BugIt> show 1
BugIt> edit 1 --add-tag auth
BugIt> exit
```

### Mixed Workflows
```bash
# CLI for automation
python bugit.py list -s critical | jq -r '.[] | .id' > critical_issues.txt

# Shell for review
python bugit.py
BugIt> show 1              # Beautiful details
BugIt> edit 1 -a reviewed  # Interactive editing
BugIt> exit

# Back to CLI for batch processing
cat critical_issues.txt | while read id; do
  python bugit.py edit $id --add-tag processed
done
```

## Configuration

### API Keys (.env file - auto-created, git-ignored)
```bash
BUGIT_OPENAI_API_KEY=sk-your-openai-api-key-here
BUGIT_ANTHROPIC_API_KEY=sk-ant-your-key-here      # Future support
BUGIT_GOOGLE_API_KEY=your-google-key-here         # Future support
```

### User Preferences (.bugitrc file)
```json
{
  "model": "gpt-4", 
  "enum_mode": "auto",
  "output_format": "table",
  "retry_limit": 3,
  "default_severity": "medium",
  "backup_on_delete": true
}
```

### Quick Setup Commands
```bash
# Set API keys
python bugit.py config --set-api-key openai <key>

# Set preferences
python bugit.py config --set model gpt-4
python bugit.py config --set retry_limit 5

# Export/import configuration
python bugit.py config --export backup.json
python bugit.py config --import backup.json
```

## Enhanced Issue Schema

```json
{
  "id": "a1b2c3",
  "schema_version": "v1",
  "title": "AI-generated issue title",
  "description": "Original user description", 
  "type": "bug | feature | chore | unknown",
  "tags": ["auth", "ui", "critical"],
  "severity": "low | medium | high | critical",
  "status": "open | resolved | archived",
  "solution": "Resolution description (empty until resolved)",
  "created_at": "2025-01-03T10:30:00",
  "updated_at": "2025-01-03T10:30:00"
}
```

## Development

### Running Tests
```bash
# Run all tests (447 tests, 91% coverage)
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/test_commands_*.py     # Command tests
pytest tests/test_core_*.py         # Core module tests
pytest tests/test_integration.py    # End-to-end tests
pytest tests/test_shell_*.py        # Shell architecture tests
```

### Code Quality
```bash
# Format and type checking
black .
isort .
mypy .
```

### Testing Features
```bash
# Test core functionality
python bugit.py new "Critical login bug" --pretty
python bugit.py list --severity critical --pretty
python bugit.py show 1 --pretty
python bugit.py edit 1 --add-tag urgent --pretty
python bugit.py delete 2 --force

# Test automation features
python bugit.py list | jq '.[] | .id'
python bugit.py --version
python bugit.py show nonexistent; echo "Exit: $?"
```

## File Structure

```
.bugit/
├── issues/
│   ├── a1b2c3.json    # Individual issue files
│   ├── d4e5f6.json    
│   └── ...            
└── backups/           # Automatic backups on delete
    ├── a1b2c3_1672531200.json
    └── ...
```

## Implementation Status

### ✅ **Production Ready**
- **All 6 Core Commands**: new, list, show, edit, delete, config
- **Real AI Integration**: OpenAI API with LangGraph framework
- **CLI Scriptability**: JSON output, POSIX exit codes, stream separation
- **Professional Styling**: Rich panels, tables, consistent formatting
- **Atomic File Operations**: Cross-platform locking, corruption handling
- **Comprehensive Testing**: 447 tests with 91% coverage
- **Interactive Shell**: Human-optimized with beautiful output
- **Configuration System**: Secure API key storage, user preferences

### 🔄 **Planned Features**
- **Archive Functionality**: `bugit archive` command with solution tracking
- **External Integrations**: GitHub, Notion, Linear sync
- **Advanced Features**: Duplicate detection, custom sorting, stdin support
- **MCP Interface**: GUI/Cursor integration 