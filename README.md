# BugIt CLI

AI-powered bug report management tool for developers.

## Overview

BugIt is a CLI-first tool that enables developers to quickly capture unstructured bug reports without interrupting their development flow. It integrates with LangGraph AI backend to transform freeform bug descriptions into structured JSON files with metadata such as title, severity, and tags.

## Features

- `bugit new` - Create a new bug report from freeform description
- `bugit list` - List existing issues with filtering options
- `bugit show` - Display detailed information about a specific issue
- `bugit edit` - Modify existing bug reports
- `bugit delete` - Remove bug reports permanently
- `bugit config` - Manage configuration settings

## Setup

### Prerequisites

- Python 3.9 or higher
- pip or poetry for dependency management

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

5. **Configure BugIt:**
   ```bash
   cp .bugitrc.example .bugitrc
   # Edit .bugitrc with your API key and preferences
   ```

### Configuration

Create a `.bugitrc` file in the project root:

```json
{
  "api_key": "sk-your-openai-api-key-here",
  "model": "gpt-4",
  "enum_mode": "auto"
}
```

You can also set environment variables:
- `BUGIT_API_KEY` - Your OpenAI API key
- `BUGIT_MODEL` - Model to use (e.g., "gpt-4")

## Usage

### Create a new bug report
```bash
python cli.py new "The logout button doesn't work on mobile devices"
```

### List all issues
```bash
python cli.py list
```

### Filter issues
```bash
python cli.py list --severity critical
python cli.py list --tag auth
python cli.py list --json  # JSON output
```

### Show issue details
```bash
python cli.py show abc123      # By UUID
python cli.py show 1           # By index from list
```

### Edit an issue
```bash
python cli.py edit abc123 --severity high
python cli.py edit 1 --add-tag urgent
python cli.py edit abc123 --title "New title"
```

### Delete an issue
```bash
python cli.py delete abc123    # With confirmation
python cli.py delete 1 --force # Skip confirmation
```

### Manage configuration
```bash
python cli.py config                    # Show current config
python cli.py config --get model        # Get specific value
python cli.py config --set model gpt-4  # Set value
python cli.py config --export config.json  # Export to file
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test types
pytest -m unit        # Unit tests only
pytest -m integration # Integration tests only
pytest -m cli         # CLI tests only
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
│   ├── new.py
│   ├── list.py
│   ├── show.py
│   ├── edit.py
│   ├── delete.py
│   └── config.py
├── core/                  # Core business logic
│   ├── storage.py         # File system operations
│   ├── schema.py          # Data validation
│   ├── model.py           # LangGraph integration
│   └── config.py          # Configuration management
├── tests/                 # Test suite
├── .bugit/               # Runtime directory (auto-created)
│   └── issues/           # Issue storage
└── requirements.txt      # Dependencies
```

## Current Status

This is currently in **Phase 1** implementation with enhanced stubs. All CLI commands are functional with mock data for development and testing purposes.

### What Works Now:
- ✅ Complete CLI structure with all commands
- ✅ Enhanced stubs with realistic mock data
- ✅ Test infrastructure and fixtures
- ✅ Configuration management
- ✅ Schema validation with proper defaults
- ✅ Rich formatted output for list command

### Next Steps:
- 🔄 Real LangGraph integration for AI processing
- 🔄 Actual file system operations with atomic writes
- 🔄 Production error handling and validation
- 🔄 Performance optimization and concurrency safety

## Testing the Current Implementation

You can test all current functionality with the stub implementations:

```bash
# Create a sample issue
python cli.py new "Sample bug description with login issue"

# List issues (shows mock data)
python cli.py list

# Show issue details
python cli.py show abc123

# Test configuration
python cli.py config --set model gpt-3.5-turbo
python cli.py config
```

## Contributing

1. Follow the implementation plan in `_docs/BugIt_Implementation_Plan.md`
2. Write tests for new functionality
3. Ensure code quality with black, isort, and mypy
4. All commits should pass the test suite

## License

[Specify your license here] 