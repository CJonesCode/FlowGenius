# BugIt CLI

**Status: Phase 3 Complete ✅** - Production-ready CLI with real file operations, atomic writes, and cross-platform compatibility

AI-powered bug report management tool for developers.

## Overview

BugIt is a CLI-first tool that enables developers to quickly capture unstructured bug reports without interrupting their development flow. It integrates with LangGraph AI backend to transform freeform bug descriptions into structured JSON files with metadata such as title, severity, and tags.

**Current Implementation:** All 6 core commands are functional with **real LangGraph integration** using OpenAI API and **production file operations** with atomic writes. The CLI offers JSON output by default (perfect for automation) with optional `--pretty` flag for human-readable formatting. Features include retry logic, structured error handling, cross-platform file locking, and professional clean output.

## Features

### Core Commands ✅ Implemented
- `bugit new` - Create a new bug report from freeform description
- `bugit list` - List existing issues with filtering options  
- `bugit show` - Display detailed information about a specific issue
- `bugit edit` - Modify existing bug reports
- `bugit delete` - Remove bug reports permanently
- `bugit config` - Manage configuration settings

### Production Capabilities ✅
- **Real AI Processing**: OpenAI API integration via LangGraph framework
- **Atomic File Operations**: Write-then-rename pattern prevents partial writes
- **Cross-Platform File Locking**: Concurrent access safety (full on Unix, simplified on Windows)
- **Real Filesystem Persistence**: Issues stored as individual JSON files
- **JSON-First Output**: Default JSON format perfect for automation and scripting
- **Pretty Human Output**: Clean, professional formatting with `--pretty` flag
- **Dynamic Index Management**: Runtime index generation with proper sorting
- **Retry Logic**: Configurable retry attempts (default: 3) with error recovery
- **Secure Configuration**: API keys stored in `.env` file (git-ignored)
- **Multi-Provider Ready**: Architecture supports OpenAI, Anthropic, and Google APIs
- **World-Class Testing**: 96% test coverage with 447 passing tests
- **Production Error Handling**: Structured error responses for automation
- **Data Safety**: Optional backup on delete, corrupted file handling

## Setup

### Prerequisites

- Python 3.9 or higher
- pip or poetry for dependency management
- OpenAI API key for real AI processing

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd BugIt
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install development dependencies (optional):**
   ```bash
   pip install -r requirements-dev.txt
   ```

### Configuration

**Set up OpenAI API key:**
```bash
python cli.py config --set-api-key openai sk-your-openai-api-key-here
```

**Create user preferences (optional):**
```bash
cp .bugitrc.example .bugitrc
# Edit .bugitrc with your preferences
```

#### Configuration System

BugIt uses a simple, security-first configuration system:
**API keys in .env file (git-ignored) | Preferences in .bugitrc file | defaults**

**1. API Keys (.env file - automatically created, git-ignored):**
```bash
BUGIT_OPENAI_API_KEY=sk-your-openai-api-key-here
BUGIT_ANTHROPIC_API_KEY=sk-ant-your-key-here      # Future support
BUGIT_GOOGLE_API_KEY=your-google-key-here         # Future support
```

**2. User Preferences (.bugitrc file):**
```json
{
  "model": "gpt-4", 
  "enum_mode": "auto",
  "output_format": "table",
  "retry_limit": 3
}
```

**Environment Variables (API Keys Only):**
```bash
# Only API keys use environment variables
export BUGIT_OPENAI_API_KEY=sk-your-key-here
export BUGIT_ANTHROPIC_API_KEY=sk-ant-your-key-here  # Future
export BUGIT_GOOGLE_API_KEY=your-google-key-here     # Future

# Configuration does NOT use environment variables - use .bugitrc instead
```

**Legacy Support:**
- `BUGIT_API_KEY` environment variable still supported with deprecation warning

## Usage

### CLI vs Interactive Shell

BugIt provides two distinct experiences optimized for different use cases:

#### 1. Direct CLI Usage (Automation-First)
Perfect for scripting, CI/CD, and automation:
```bash
# JSON output by default (perfect for automation)
python cli.py new "Critical login bug"
python cli.py list | jq '.[] | select(.severity == "critical")'

# Pretty output when needed
python cli.py list --pretty
python cli.py new "Bug description" -p
```

#### 2. Interactive Shell (Human-First)  
Perfect for interactive use by developers:
```bash
# Start the interactive shell
python bugit.py

# Pretty output by default (human-friendly)
BugIt> list
BugIt> new "Bug description"

# JSON output when needed (both flags work)
BugIt> list -p
BugIt> list --pretty
BugIt> new "Bug description" -p
BugIt> new "Bug description" --pretty
```

### CLI Output Formats

**Direct CLI Mode (Automation-First):**
- **Default**: JSON output perfect for scripting
- **`--pretty` or `-p`**: Human-readable output

**Interactive Shell Mode (Human-First):**
- **Default**: Pretty output perfect for humans  
- **`-p` or `--pretty` flag**: JSON output for copy-paste into automation

### Short Flags for Power Users

BugIt supports convenient short flags for commonly used options:

| Short Flag | Long Flag | Used In | Description |
|------------|-----------|---------|-------------|
| `-p` | `--pretty` | All commands | Human-readable output |
| `-s` | `--severity` | `list`, `edit` | Filter/set severity |
| `-t` | `--tag` | `list` | Filter by tag |
| `-a` | `--add-tag` | `edit` | Add tag to issue |
| `-r` | `--remove-tag` | `edit` | Remove tag from issue |
| `-f` | `--force` | `delete` | Skip confirmation |
| `-g` | `--get` | `config` | Get config value |

**Examples:**
```bash
# These are equivalent
python cli.py list --severity critical --pretty
python cli.py list -s critical -p

# These are equivalent  
python cli.py edit 1 --add-tag urgent --pretty
python cli.py edit 1 -a urgent -p

# These are equivalent
python cli.py config --get model --pretty
python cli.py config -g model -p
```

### Create a new bug report
```bash
# JSON output (default)
python cli.py new "The logout button doesn't work on mobile devices"

# Pretty output for humans (using short flag)
python cli.py new "The logout button doesn't work on mobile devices" -p
```

### List all issues
```bash
# JSON array (default)
python cli.py list

# Pretty table for humans (using short flag)
python cli.py list -p
```

### Filter issues  
```bash
# Using long flags
python cli.py list --severity critical --pretty

# Using short flags for faster typing
python cli.py list -s critical -p
python cli.py list -t auth -p
```

### Show issue details
```bash
# JSON object (default)
python cli.py show abc123      # By UUID
python cli.py show 1           # By index from list

# Pretty panel for humans (using short flag)
python cli.py show 1 -p
```

### Edit an issue
```bash
# JSON response (default)
python cli.py edit abc123 --severity high

# Using short flags for efficiency
python cli.py edit 1 -s high -a urgent -p
python cli.py edit abc123 --title "New title" -p
```

### Delete an issue
```bash
# JSON mode requires --force flag for safety (using short flag)
python cli.py delete abc123 -f

# Pretty mode has interactive confirmation
python cli.py delete 1 -p
```

### Manage configuration
```bash
python cli.py config                                      # JSON object (default)
python cli.py config -p                                   # Pretty formatted display (short flag)
python cli.py config -g model                             # Get specific value (short flag)
python cli.py config --set model gpt-4                    # Set value
python cli.py config --set-api-key openai sk-...          # Set API key securely
python cli.py config --export config.json                 # Export to file
```

## Automation Examples

### Scripting with Direct CLI (Automation-First)

The JSON-first output makes BugIt perfect for automation:

```bash
# Extract issue IDs for processing (CLI mode - JSON by default)
python cli.py list | jq -r '.[].id'

# Filter critical issues (CLI mode)
python cli.py list --severity critical | jq '.[] | select(.severity == "critical")'
python cli.py list -s critical | jq '.[] | select(.severity == "critical")'

# Create issue and get ID for follow-up (CLI mode)
ISSUE_ID=$(python cli.py new "Critical bug" | jq -r '.issue.id')
python cli.py edit $ISSUE_ID -a urgent

# Batch process issues by severity (CLI mode with short flags)
python cli.py list -s critical | jq -r '.[] | .id' | \
  while read id; do
    python cli.py edit $id -a needs-review
  done
```

### Interactive Shell Workflow (Human-First)

The shell provides a human-friendly experience:

```bash
# Start interactive shell
python bugit.py

# Inside shell - pretty output by default
BugIt> list                    # Shows nice table
BugIt> list -s critical        # Filtered pretty table
BugIt> new "Bug description"   # Pretty confirmation
BugIt> edit 1 -s high          # Pretty edit feedback

# Get JSON when needed for automation
BugIt> list -p | jq '.[] | .id'      # Copy-paste to scripts
BugIt> list --pretty | jq '.[] | .id' # Both flags work the same
BugIt> config -p                     # JSON config for backup
```

### Mixed Workflow Examples

```bash
# CLI for automation tasks
python cli.py list -s critical | jq -r '.[] | .id' > critical_issues.txt

# Shell for interactive review
python bugit.py
BugIt> show 1              # Pretty details for human review
BugIt> edit 1 -a reviewed  # Interactive editing
BugIt> exit

# Back to CLI for batch processing
cat critical_issues.txt | while read id; do
  python cli.py edit $id -a processed
done
```

## Development

### Running Tests

```bash
# Run all tests (447 tests passing, 96% coverage)
pytest

# Run with coverage  
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html

# Run specific test suites
pytest tests/test_basic.py          # Infrastructure tests
pytest tests/test_commands_*.py     # Command-specific tests  
pytest tests/test_core_*.py         # Core module tests
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy .
```

### Project Structure

```
BugIt/
├── cli.py                 # Main CLI entry point
├── commands/              # CLI command implementations
│   ├── new.py            # Create new issues
│   ├── list.py           # List and filter issues  
│   ├── show.py           # Show issue details
│   ├── edit.py           # Edit existing issues
│   ├── delete.py         # Delete issues
│   └── config.py         # Configuration management
├── core/                  # Core business logic
│   ├── storage.py         # Production file operations with atomic writes
│   ├── schema.py          # Data validation and defaults
│   ├── model.py           # Real LangGraph integration
│   └── config.py          # Configuration management
├── tests/                 # Test suite (447 tests, 96% coverage)
│   ├── conftest.py        # Test fixtures
│   ├── test_basic.py      # Infrastructure tests
│   ├── test_commands_*.py # Command-specific tests
│   ├── test_core_*.py     # Core module tests
│   ├── test_integration.py # End-to-end workflow tests
│   └── test_performance.py # Performance benchmarks
├── .bugit/               # Runtime directory (auto-created)
│   ├── issues/           # Issue storage (JSON files)
│   └── backups/          # Optional backup storage
├── .env                  # API keys (git-ignored, auto-created)
├── .bugitrc              # User preferences
└── requirements.txt      # Dependencies
```

## Current Implementation Status

### ✅ Phase 0: Environment Setup - COMPLETE
- Python virtual environment with all dependencies
- Project structure with proper module organization
- Requirements management and version control
- Comprehensive .gitignore with security patterns

### ✅ Phase 1: Enhanced Stubs Implementation - COMPLETE  
- All 6 CLI commands implemented and fully functional
- Enhanced stub system with intelligent keyword-based processing
- Production CLI experience with Rich formatting and proper error handling
- Comprehensive testing with 9/9 tests passing
- Secure configuration with .env file API key management
- Multi-provider architecture ready for future AI service expansion

### ✅ Phase 2: Real LangGraph Integration - COMPLETE
- **Real OpenAI API integration** via LangGraph framework
- **Retry logic with configurable attempts** (default: 3)
- **Structured output validation** with Pydantic models
- **JSON-first output format** perfect for automation and scripting
- **Professional clean output** without emojis
- **Comprehensive error handling** with structured responses
- **World-class testing** with 96% coverage and 447 passing tests

### ✅ Phase 3: Production File Operations - COMPLETE
- **Atomic file operations** with write-then-rename pattern
- **Cross-platform file locking** for concurrent access safety (full on Unix, simplified on Windows)
- **Real filesystem persistence** with individual JSON files replacing all mock storage
- **Dynamic index management** with runtime generation and proper sorting
- **Production error handling** with StorageError hierarchy and structured responses
- **Data safety features**: Optional backup on delete, corrupted file handling
- **Storage statistics** and monitoring capabilities for debugging
- **Enhanced command integration** using new storage functions

### What Works Right Now:
- ✅ **Complete CLI interface** with dual output modes (JSON/pretty)
- ✅ **Real AI processing** with OpenAI API integration
- ✅ **Production file operations** with atomic writes and file locking
- ✅ **Automation-ready** JSON output for scripting and CI/CD
- ✅ **Human-friendly** pretty output for interactive use
- ✅ **Data persistence** with real JSON files stored in `.bugit/issues/`
- ✅ **Concurrent access safety** with cross-platform file locking
- ✅ **Production error handling** with retry logic and structured responses
- ✅ **Full command functionality** (new, list, show, edit, delete, config)
- ✅ **Secure API key management** with automatic .env file creation
- ✅ **Multi-provider support** architecture for future AI service expansion
- ✅ **World-class testing** with 96% coverage, 447 tests, real AI integration

### 🔄 Phase 4: Advanced Features & Polish - NEXT
- Performance optimization for large issue lists (100+ issues)
- Advanced caching mechanisms for efficient operations
- Enhanced Windows file locking implementation
- Advanced filtering and search capabilities
- Integration with external tools (GitHub, Notion, Linear)
- Custom sorting and archiving features
- Duplicate detection and similarity analysis

## Testing the Current Implementation

You can fully test all functionality with the current production implementation:

```bash
# Create sample issues (real AI processing with file persistence)
python cli.py new "Critical login bug: users can't authenticate"
python cli.py new "Minor UI issue with button alignment" -p
python cli.py new "Camera crash when switching modes"

# List issues - JSON for automation
python cli.py list | jq '.[] | select(.severity == "critical")'

# List issues - pretty table for humans (short flag)
python cli.py list -p

# Filter by severity or tags (short flags for efficiency)
python cli.py list -s critical -p
python cli.py list -t auth

# Show detailed issue information (reads from actual files)
python cli.py show 1 -p              # Pretty panel (short flag)
python cli.py show abc123            # JSON object

# Edit issues with real AI validation (atomic file updates, short flags)
python cli.py edit 1 -s low -a ui -p

# Delete issues with backup (atomic file operations, short flag)
python cli.py delete 2 -f

# Configuration management (short flags)
python cli.py config --set model gpt-3.5-turbo
python cli.py config --set-api-key openai sk-your-key-here
python cli.py config -g model -p
python cli.py config --export backup.json

# Check storage statistics
python -c "from core.storage import get_storage_stats; import json; print(json.dumps(get_storage_stats(), indent=2))"
```

## Architecture Highlights

### Real AI Integration
- **LangGraph Framework**: Production-ready AI processing pipeline
- **OpenAI API**: Real AI-powered bug analysis and categorization
- **Retry Logic**: Robust error handling with configurable retry attempts
- **Structured Validation**: Pydantic models ensure consistent AI output

### Production File Operations
- **Atomic Writes**: Write-then-rename pattern prevents partial writes and data corruption
- **Cross-Platform Locking**: Concurrent access safety on Unix and Windows
- **Real Persistence**: Individual JSON files in `.bugit/issues/` directory
- **Data Safety**: Optional backup on delete, graceful handling of corrupted files
- **Error Handling**: Comprehensive StorageError hierarchy for structured responses

### Automation-First Design
- **JSON by Default**: Perfect for scripting, CI/CD, and automation workflows
- **Pretty Flag**: Human-readable output when needed
- **Consistent Interface**: All commands support both output modes
- **Safety Features**: Destructive operations require explicit confirmation in JSON mode

### Security-First Design
- API keys never stored in version control (.env file auto-created)
- Clear separation between secrets (.env) and preferences (.bugitrc)
- API key environment variables for deployment flexibility (NO configuration overrides)

### Production Quality CLI
- Rich library integration for beautiful terminal output
- Comprehensive error handling with structured responses
- Full scriptability with no interactive prompts required
- Proper exit codes and error propagation

### Testing & Quality
- **96% test coverage** with 447 passing tests
- **Systematic test enhancement** covering all major code paths
- **Real AI integration testing** with OpenAI API validation
- **Production file operations** testing with atomic writes and concurrency
- **Comprehensive error handling** coverage including edge cases
- **Performance benchmarks** and integration testing

## File Storage Structure

Issues are stored as individual JSON files:

```
.bugit/
├── issues/
│   ├── a1b2c3.json    # Individual issue file
│   ├── d4e5f6.json    # Another issue
│   └── ...            # More issues
└── backups/           # Optional backup directory
    ├── a1b2c3_1672531200.json  # Timestamped backup
    └── ...
```

Each issue file contains:
```json
{
  "id": "a1b2c3",
  "schema_version": "v1",
  "title": "Logout screen hangs on exit",
  "description": "App gets stuck after logging out. Needs force close.",
  "tags": ["auth", "logout"],
  "severity": "critical",
  "type": "bug",
  "created_at": "2025-07-01T13:00:00"
}
```

## Contributing

1. Follow the implementation plan in `_docs/BugIt_Implementation_Plan.md`
2. Write tests for new functionality using pytest fixtures  
3. Ensure code quality with black, isort, and mypy
4. All commits should pass the full test suite
5. Maintain the security-first approach for any configuration changes
6. **Consult `_docs/BugIt_Style_Guide.md` for color scheme and visual consistency guidelines**

## Next Steps

Ready for **Phase 4** implementation:
1. **Performance Optimization**: Caching and efficient operations for large datasets
2. **Advanced Features**: Custom sorting, archiving, and search capabilities
3. **External Integrations**: GitHub, Notion, Linear integrations
4. **Enhanced Windows Support**: Improved file locking implementation
5. **Deployment**: Package for distribution and CI/CD integration

The current implementation provides a complete AI-powered CLI tool with real LangGraph integration, production-quality file operations with atomic writes, cross-platform compatibility, and automation-friendly JSON output.

## License

[Specify your license here] 