# BugIt CLI

**Status: Phase 3 Complete ✅** - Production-ready CLI with real file operations, atomic writes, and cross-platform compatibility

AI-powered bug report management tool for developers.

## Overview

BugIt is a CLI-first tool that enables developers to quickly capture unstructured bug reports without interrupting their development flow. It integrates with LangGraph AI backend to transform freeform bug descriptions into structured JSON files with metadata such as title, severity, and tags.

**Current Implementation:** All 6 core commands are functional with **real LangGraph integration** using OpenAI API and **production file operations** with atomic writes. The CLI offers JSON output by default (perfect for automation) with optional `--pretty` flag for human-readable formatting. Features include retry logic, structured error handling, cross-platform file locking, and professional clean output.

## Interface Options

BugIt provides **two distinct interfaces** optimized for different use cases:

### 1. **Direct CLI Mode** (`python cli.py`) - Automation-First
Perfect for scripting, CI/CD, and automation workflows:
- **Default Output**: JSON format ideal for automation
- **Usage**: `python cli.py <command> [options]`
- **Best For**: Scripts, automation, CI/CD pipelines

### 2. **Interactive Shell Mode** (`python bugit.py`) - Human-First  
Perfect for interactive development workflows:
- **Default Output**: Pretty formatted output for humans
- **Usage**: `python bugit.py` then interactive commands
- **Best For**: Interactive development, exploring issues

## Current Feature Status

### **✅ IMPLEMENTED FEATURES**

| **Feature Category** | **Feature** | **Status** | **Notes** |
|---------------------|-------------|------------|-----------|
| **Core Commands** | | | |
| | `bugit new` | ✅ Complete | AI-powered bug creation with OpenAI API |
| | `bugit list` | ✅ Complete | Filtering, sorting, JSON/pretty output |
| | `bugit show` | ✅ Complete | Detailed issue display |
| | `bugit edit` | ✅ Complete | Full field editing capabilities |
| | `bugit delete` | ✅ Complete | Atomic deletion with backup |
| | `bugit config` | ✅ Complete | Configuration management |
| **AI Integration** | | | |
| | LangGraph framework | ✅ Complete | Real OpenAI API integration |
| | OpenAI API | ✅ Complete | GPT-4 processing with retry logic |
| | Structured output | ✅ Complete | Pydantic validation models |
| | Retry logic | ✅ Complete | Configurable retry attempts |
| | Multi-provider ready | 🔄 Architecture | Anthropic/Google support planned |
| **Storage & Persistence** | | | |
| | Atomic file operations | ✅ Complete | Write-then-rename pattern |
| | Cross-platform locking | ✅ Complete | Unix and Windows file locking |
| | JSON file storage | ✅ Complete | Individual files per issue |
| | Dynamic indexing | ✅ Complete | Runtime index generation |
| | Corrupted file handling | ✅ Complete | Graceful error handling |
| | Backup on delete | ✅ Complete | Optional backup system |
| **User Interface** | | | |
| | Direct CLI mode | ✅ Complete | JSON-first for automation |
| | Interactive shell | ✅ Complete | Human-friendly interface |
| | JSON output | ✅ Complete | Default for automation |
| | Pretty output | ✅ Complete | Rich formatting |
| | Short flags | ✅ Complete | `-p`, `-s`, `-t`, `-f`, etc. |
| | Professional styling | ✅ Complete | Consistent color scheme |
| **Configuration** | | | |
| | API key management | ✅ Complete | Secure `.env` storage |
| | User preferences | ✅ Complete | `.bugitrc` file |
| | Multi-provider config | ✅ Complete | OpenAI, Anthropic, Google ready |
| | Environment variables | ✅ Complete | API key support |
| | Import/export | ✅ Complete | JSON file operations |
| **Testing & Quality** | | | |
| | Comprehensive test suite | ✅ Complete | 19 test files with extensive coverage |
| | Unit & integration tests | ✅ Complete | Professional test infrastructure |
| | Performance benchmarks | ✅ Complete | Scalability testing |
| | Mock infrastructure | ✅ Complete | No external dependencies |
| **Security & Safety** | | | |
| | Secure API key storage | ✅ Complete | Git-ignored `.env` file |
| | Input validation | ✅ Complete | Pydantic models |
| | Error handling | ✅ Complete | Structured exceptions |
| | Data validation | ✅ Complete | Type checking |

### **🔄 PLANNED FEATURES (Phase 4)**

| **Feature Category** | **Feature** | **Status** | **Notes** |
|---------------------|-------------|------------|-----------|
| **Advanced Features** | | | |
| | Archive functionality | 🔄 Planned | Manual `bugit archive` command |
| | Duplicate detection | 🔄 Planned | Embedding-based similarity |
| | Custom sorting | 🔄 Planned | Advanced list options |
| | Performance optimization | 🔄 Planned | Large dataset handling |
| | Enhanced caching | 🔄 Planned | Memory optimization |
| **External Integrations** | | | |
| | GitHub integration | 🔄 Planned | Issue sync |
| | Notion integration | 🔄 Planned | Database sync |
| | Linear integration | 🔄 Planned | Project management |
| | Markdown export | 🔄 Planned | Human-readable reports |
| | Screenshot support | 🔄 Planned | Media attachments |
| **Workflow Features** | | | |
| | Schema migration | 🔄 Planned | Version compatibility |
| | MCP interface | 🔄 Planned | GUI/Cursor integration |
| | Embedding clustering | 🔄 Planned | AI-powered grouping |
| | Async operations | 🔄 Planned | Concurrent processing |

**Legend:**
- ✅ **Complete**: Fully implemented and working
- ⚠️ **Partial**: Implemented but with known limitations
- 🔄 **Planned**: Architecture ready but not implemented

## Setup

### Prerequisites

- Python 3.9 or higher (tested with Python 3.13)
- pip for dependency management
- OpenAI API key for AI processing

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

## Usage

### Direct CLI Mode (Automation-First)

Perfect for scripting, CI/CD, and automation:

```bash
# Create new issues - JSON output by default
python cli.py new "Critical login bug"
python cli.py new "UI button alignment issue" --pretty  # Human-readable

# List and filter issues
python cli.py list                                     # JSON array
python cli.py list --pretty                           # Pretty table
python cli.py list --severity critical | jq '.[] | .id'  # Automation

# Show issue details
python cli.py show 1                                   # JSON object
python cli.py show abc123 --pretty                    # Pretty panel

# Edit and delete issues
python cli.py edit 1 --severity high --add-tag urgent
python cli.py delete 1 --force                        # Skip confirmation

# Configuration
python cli.py config                                   # JSON object
python cli.py config --pretty                         # Pretty display
python cli.py config --get model                      # Get specific value
```

### Interactive Shell Mode (Human-First)

Perfect for interactive development workflows:

```bash
# Start interactive shell
python bugit.py

# Interactive commands (pretty output by default)
BugIt> new "Bug description"                    # Pretty confirmation
BugIt> list                                     # Pretty table
BugIt> show 1                                   # Pretty panel
BugIt> edit 1 --severity high                   # Pretty feedback
BugIt> delete 1                                 # Interactive confirmation

# Get JSON when needed for automation
BugIt> list --pretty                            # JSON output
BugIt> config --pretty                          # JSON for backup
```

### Short Flags for Power Users

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
# Direct CLI with short flags
python cli.py list -s critical -p              # Filter critical, pretty output
python cli.py edit 1 -a urgent -p              # Add tag, pretty output
python cli.py config -g model -p               # Get model setting

# Interactive shell with short flags
BugIt> list -s high                            # Filter high severity
BugIt> edit 1 -r old-tag                       # Remove tag
```

## Automation Examples

### JSON-First Automation
```bash
# Extract issue IDs for batch processing
python cli.py list | jq -r '.[].id'

# Filter and process critical issues
python cli.py list --severity critical | jq '.[] | select(.severity == "critical")'

# Create issue and get ID for follow-up
ISSUE_ID=$(python cli.py new "Critical bug" | jq -r '.id')
python cli.py edit $ISSUE_ID --add-tag urgent

# Batch process issues
python cli.py list -s critical | jq -r '.[] | .id' | \
  while read id; do
    python cli.py edit $id --add-tag needs-review
  done
```

### Mixed Workflow
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
  python cli.py edit $id --add-tag processed
done
```

## Development & Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage  
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html # Windows

# Run specific test categories
pytest tests/test_basic.py              # Infrastructure tests
pytest tests/test_commands_*.py         # Command-specific tests  
pytest tests/test_core_*.py             # Core module tests
pytest tests/test_integration.py        # End-to-end tests
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

### Testing the Implementation

Test all functionality with real AI processing and file persistence:

```bash
# Create sample issues (real AI + file operations)
python cli.py new "Critical login bug: users can't authenticate"
python cli.py new "Minor UI issue with button alignment" --pretty

# List and filter issues
python cli.py list | jq '.[] | select(.severity == "critical")'
python cli.py list --pretty                    # Pretty table
python cli.py list --severity critical --pretty

# Show detailed information
python cli.py show 1 --pretty                  # Pretty panel
python cli.py show abc123                      # JSON object

# Edit with AI validation
python cli.py edit 1 --severity low --add-tag ui --pretty

# Delete with backup
python cli.py delete 2 --force

# Configuration management
python cli.py config --set model gpt-3.5-turbo
python cli.py config --get model --pretty
python cli.py config --export backup.json
```

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

## Backup vs Archive

### **🛡️ Backup (✅ Implemented)**
- **Purpose**: Data safety and recovery
- **Trigger**: Automatic on delete
- **Location**: `.bugit/backups/`
- **Content**: Exact copy of deleted issue
- **Use**: Recovery from accidental deletion

### **📁 Archive (🔄 Planned)**
- **Purpose**: Workflow management
- **Trigger**: Manual `bugit archive` command
- **Location**: `.bugit/archived/` (planned)
- **Content**: Issue + resolution field
- **Use**: Organize completed work

## Contributing

1. Follow the implementation plan in `_docs/BugIt_Implementation_Plan.md`
2. Write tests for new functionality using pytest fixtures  
3. Ensure code quality with black, isort, and mypy
4. All commits should pass the full test suite
5. Maintain the security-first approach for configuration changes
6. **Consult `_docs/BugIt_Style_Guide.md` for coding standards**

## License

[Specify your license here] 