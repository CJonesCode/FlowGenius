# BugIt CLI

**Status: Phase 2 Complete ✅** - Production-ready CLI with real LangGraph integration and automation-friendly output

AI-powered bug report management tool for developers.

## Overview

BugIt is a CLI-first tool that enables developers to quickly capture unstructured bug reports without interrupting their development flow. It integrates with LangGraph AI backend to transform freeform bug descriptions into structured JSON files with metadata such as title, severity, and tags.

**Current Implementation:** All 6 core commands are functional with **real LangGraph integration** using OpenAI API. The CLI offers JSON output by default (perfect for automation) with optional `--pretty` flag for human-readable formatting. Features include retry logic, structured error handling, and professional clean output.

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
- **JSON-First Output**: Default JSON format perfect for automation and scripting
- **Pretty Human Output**: Clean, professional formatting with `--pretty` flag
- **Retry Logic**: Configurable retry attempts (default: 3) with error recovery
- **Secure Configuration**: API keys stored in `.env` file (git-ignored)
- **Multi-Provider Ready**: Architecture supports OpenAI, Anthropic, and Google APIs
- **Comprehensive Testing**: 22/22 tests passing with real AI integration coverage
- **Production Error Handling**: Structured error responses for automation

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

BugIt uses a multi-layer configuration system with this priority order:
**Environment Variables > .env file > .bugitrc file > defaults**

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

**3. Environment Variable Overrides:**
```bash
export BUGIT_MODEL=gpt-3.5-turbo
export BUGIT_OUTPUT_FORMAT=json
```

**Legacy Support:**
- `BUGIT_API_KEY` environment variable still supported with deprecation warning

## Usage

### CLI Output Formats

BugIt supports two output modes:

**Default JSON Output (perfect for automation):**
```bash
python cli.py new "Critical login bug"
# Returns JSON object for scripting
```

**Pretty Human-Readable Output:**
```bash
python cli.py new "Critical login bug" --pretty
# Returns clean, formatted text for humans
```

### Create a new bug report
```bash
# JSON output (default)
python cli.py new "The logout button doesn't work on mobile devices"

# Pretty output for humans
python cli.py new "The logout button doesn't work on mobile devices" --pretty
```

### List all issues
```bash
# JSON array (default)
python cli.py list

# Pretty table for humans
python cli.py list --pretty
```

### Filter issues  
```bash
python cli.py list --severity critical
python cli.py list --tag auth
python cli.py list --severity critical --pretty  # Pretty table output
```

### Show issue details
```bash
# JSON object (default)
python cli.py show abc123      # By UUID
python cli.py show 1           # By index from list

# Pretty panel for humans
python cli.py show 1 --pretty
```

### Edit an issue
```bash
# JSON response (default)
python cli.py edit abc123 --severity high

# Pretty feedback for humans
python cli.py edit 1 --add-tag urgent --pretty
python cli.py edit abc123 --title "New title" --pretty
```

### Delete an issue
```bash
# JSON mode requires --force flag for safety
python cli.py delete abc123 --force

# Pretty mode has interactive confirmation
python cli.py delete 1 --pretty
```

### Manage configuration
```bash
python cli.py config                                      # JSON object (default)
python cli.py config --pretty                             # Pretty formatted display
python cli.py config --get model                          # Get specific value
python cli.py config --set model gpt-4                    # Set value
python cli.py config --set-api-key openai sk-...          # Set API key securely
python cli.py config --export config.json                 # Export to file
```

## Automation Examples

The JSON-first output makes BugIt perfect for automation:

```bash
# Extract issue IDs for processing
python cli.py list | jq -r '.[].id'

# Filter critical issues
python cli.py list | jq '.[] | select(.severity == "critical")'

# Create issue and get ID for follow-up
ISSUE_ID=$(python cli.py new "Critical bug" | jq -r '.issue.id')
python cli.py edit $ISSUE_ID --add-tag urgent

# Batch process issues by severity
python cli.py list | jq -r '.[] | select(.severity == "critical") | .id' | \
  while read id; do
    python cli.py edit $id --add-tag needs-review
  done
```

## Development

### Running Tests

```bash
# Run all tests (22/22 passing)
pytest

# Run with coverage  
pytest --cov=. --cov-report=html

# Run specific test suites
pytest tests/test_basic.py       # Basic functionality (9/9)
pytest tests/test_json_output.py # JSON output and automation (13/13)
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
│   ├── storage.py         # File system operations
│   ├── schema.py          # Data validation and defaults
│   ├── model.py           # Real LangGraph integration
│   └── config.py          # Configuration management
├── tests/                 # Test suite (22/22 passing)
│   ├── conftest.py        # Test fixtures
│   ├── test_basic.py      # Core functionality tests (9/9)
│   └── test_json_output.py # JSON output and automation tests (13/13)
├── .bugit/               # Runtime directory (auto-created)
│   └── issues/           # Issue storage
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
- **Expanded testing** with 22/22 tests passing (real AI integration coverage)

### What Works Right Now:
- ✅ **Complete CLI interface** with dual output modes (JSON/pretty)
- ✅ **Real AI processing** with OpenAI API integration
- ✅ **Automation-ready** JSON output for scripting and CI/CD
- ✅ **Human-friendly** pretty output for interactive use
- ✅ **Production error handling** with retry logic and structured responses
- ✅ **Full command functionality** (new, list, show, edit, delete, config)
- ✅ **Secure API key management** with automatic .env file creation
- ✅ **Multi-provider support** architecture for future AI service expansion
- ✅ **Comprehensive testing** with real AI integration coverage

### 🔄 Phase 3: Production File Operations - NEXT
- Atomic file writes with write-then-rename pattern
- Concurrent access safety with proper file locking
- Real filesystem operations replacing mock storage
- Index management and caching for performance
- Backup and recovery mechanisms

### 🔄 Phase 4: Advanced Features - NEXT  
- Performance optimization for large issue lists
- Advanced filtering and search capabilities
- Integration with external tools (GitHub, Notion, Linear)
- Custom sorting and archiving features

## Testing the Current Implementation

You can fully test all functionality with the current real LangGraph implementation:

```bash
# Create sample issues (real AI processing)
python cli.py new "Critical login bug: users can't authenticate"
python cli.py new "Minor UI issue with button alignment" --pretty
python cli.py new "Camera crash when switching modes"

# List issues - JSON for automation
python cli.py list | jq '.[] | select(.severity == "critical")'

# List issues - pretty table for humans
python cli.py list --pretty

# Filter by severity or tags  
python cli.py list --severity critical --pretty
python cli.py list --tag auth

# Show detailed issue information
python cli.py show 1 --pretty     # Pretty panel
python cli.py show abc123         # JSON object

# Edit issues with real AI validation
python cli.py edit 1 --severity low --add-tag ui --pretty

# Delete issues (JSON mode requires --force)
python cli.py delete 2 --force

# Configuration management
python cli.py config --set model gpt-3.5-turbo
python cli.py config --set-api-key openai sk-your-key-here
python cli.py config --export backup.json
```

## Architecture Highlights

### Real AI Integration
- **LangGraph Framework**: Production-ready AI processing pipeline
- **OpenAI API**: Real AI-powered bug analysis and categorization
- **Retry Logic**: Robust error handling with configurable retry attempts
- **Structured Validation**: Pydantic models ensure consistent AI output

### Automation-First Design
- **JSON by Default**: Perfect for scripting, CI/CD, and automation workflows
- **Pretty Flag**: Human-readable output when needed
- **Consistent Interface**: All commands support both output modes
- **Safety Features**: Destructive operations require explicit confirmation in JSON mode

### Security-First Design
- API keys never stored in version control (.env file auto-created)
- Clear separation between secrets (.env) and preferences (.bugitrc)
- Environment variable override system for deployment flexibility

### Production Quality CLI
- Rich library integration for beautiful terminal output
- Comprehensive error handling with structured responses
- Full scriptability with no interactive prompts required
- Proper exit codes and error propagation

### Testing & Quality
- 22/22 tests passing with real AI integration coverage
- Test fixtures for isolation and repeatability  
- Real LangGraph testing with API validation
- Pytest configuration with proper markers

## Contributing

1. Follow the implementation plan in `_docs/BugIt_Implementation_Plan.md`
2. Write tests for new functionality using pytest fixtures  
3. Ensure code quality with black, isort, and mypy
4. All commits should pass the full test suite
5. Maintain the security-first approach for any configuration changes

## Next Steps

Ready for **Phase 3** implementation:
1. **Atomic File Operations**: Implement write-then-rename and concurrent access
2. **Performance Optimization**: Add caching and efficient operations for large datasets
3. **Advanced Features**: Custom sorting, archiving, and external integrations
4. **Deployment**: Package for distribution and CI/CD integration

The current implementation provides a complete AI-powered CLI tool with real LangGraph integration, automation-friendly JSON output, and production-quality error handling.

## License

[Specify your license here] 