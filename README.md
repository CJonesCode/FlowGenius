# BugIt CLI

**Status: Phase 3+ Complete ✅** - Production-ready CLI with centralized styling, Typer integration, and professional interfaces

AI-powered bug report management tool for developers with a beautiful, consistent CLI experience.

## Overview

BugIt is a CLI-first tool that enables developers to quickly capture unstructured bug reports without interrupting their development flow. It integrates with LangGraph AI backend to transform freeform bug descriptions into structured JSON files with metadata such as title, severity, and tags.

**Current Implementation:** All 6 core commands are functional with **real LangGraph integration** using OpenAI API, **production file operations** with atomic writes, and a **professional styling system** with centralized color management. The CLI offers JSON output by default (perfect for automation) with optional `--pretty` flag for human-readable formatting. Features include retry logic, structured error handling, cross-platform file locking, and a beautiful Rich-powered interface.

## Interface Options

BugIt provides **two distinct interfaces** optimized for different use cases, both featuring consistent styling and professional appearance:

### 1. **Direct CLI Mode** (`python cli.py`) - Automation-First
Perfect for scripting, CI/CD, and automation workflows:
- **Default Output**: JSON format ideal for automation
- **Pretty Mode**: Rich-formatted output with panels, tables, and colors
- **Usage**: `python cli.py <command> [options]`
- **Best For**: Scripts, automation, CI/CD pipelines
- **Styling**: Typer's auto-generated help with Rich markup

### 2. **Interactive Shell Mode** (`python bugit.py`) - Human-First  
Perfect for interactive development workflows:
- **Default Output**: Pretty formatted output for humans
- **JSON Mode**: Use `-p` flag for JSON output when needed
- **Usage**: `python bugit.py` then interactive commands  
- **Best For**: Interactive development, exploring issues
- **Features**: Dynamic command extraction, styled panels, clean output

## Current Feature Status

### **✅ IMPLEMENTED FEATURES**

| **Feature Category** | **Feature** | **Status** | **Notes** |
|---------------------|-------------|------------|-----------|
| **Core Commands** | | | |
| | `bugit new` | ✅ Complete | AI-powered bug creation with OpenAI API |
| | `bugit list` | ✅ Complete | Filtering, sorting, JSON/pretty output |
| | `bugit show` | ✅ Complete | Detailed issue display with styled panels |
| | `bugit edit` | ✅ Complete | Full field editing with styled feedback |
| | `bugit delete` | ✅ Complete | Atomic deletion with confirmation panels |
| | `bugit config` | ✅ Complete | Configuration management with styled display |
| **User Interface & Styling** | | | |
| | Centralized styling system | ✅ Complete | `core/styles.py` with Colors, Styles, PanelStyles |
| | Rich console integration | ✅ Complete | Beautiful panels, tables, and formatted output |
| | Typer framework | ✅ Complete | Auto-generated help, proper argument handling |
| | Interactive shell | ✅ Complete | Clean interface with dynamic command extraction |
| | Semantic color coding | ✅ Complete | Consistent colors for UUIDs, severity, etc. |
| | Professional panels | ✅ Complete | Left-aligned titles, consistent borders |
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

## Styling System

BugIt features a **centralized styling system** that ensures consistent, professional appearance across all interfaces:

### **Centralized Design**
- **Single Source of Truth**: All colors and styles defined in `core/styles.py`
- **Semantic Colors**: Consistent meaning (UUIDs = magenta, errors = red, success = green)
- **Professional Panels**: Left-aligned titles, consistent borders, proper padding
- **Rich Integration**: Beautiful tables, panels, and formatted text

### **Color Palette**
- **Blue** (Brand): Borders, prompts, branding
- **Cyan** (Interactive): Commands, indices, interactive elements  
- **Red** (Error): Errors, critical severity, warnings
- **Green** (Success): Dates, confirmations, completed actions
- **Yellow** (Warning): Tags, medium severity, notifications
- **Magenta** (Identifier): UUIDs, unique identifiers
- **White** (Primary): Titles, main content
- **Dim** (Secondary): Labels, descriptions, metadata

### **Panel Types**
- **Standard**: Blue border for regular content
- **Success**: Green border for completion messages
- **Error**: Red border for error messages  
- **Warning**: Yellow border for confirmations

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

Perfect for scripting, CI/CD, and automation with beautiful styled output when needed:

```bash
# Create new issues - JSON output by default
python cli.py new "Critical login bug"
python cli.py new "UI button alignment issue" --pretty  # Beautiful panel

# List and filter issues
python cli.py list                                     # JSON array
python cli.py list --pretty                           # Beautiful table
python cli.py list --severity critical | jq '.[] | .id'  # Automation

# Show issue details
python cli.py show 1                                   # JSON object
python cli.py show abc123 --pretty                    # Beautiful panel

# Edit and delete issues
python cli.py edit 1 --severity high --add-tag urgent --pretty  # Styled feedback
python cli.py delete 1 --force                        # Skip confirmation

# Configuration
python cli.py config                                   # JSON object
python cli.py config --pretty                         # Beautiful configuration panel
python cli.py config --get model --pretty             # Styled value display
```

### Interactive Shell Mode (Human-First)

Perfect for interactive development workflows with beautiful styling by default:

```bash
# Start interactive shell
python bugit.py

# Interactive commands (beautiful output by default)
BugIt> new "Bug description"                    # Styled confirmation panel
BugIt> list                                     # Beautiful table
BugIt> show 1                                   # Styled issue panel
BugIt> edit 1 --severity high                   # Styled edit results
BugIt> delete 1                                 # Interactive confirmation with styling

# Get JSON when needed for automation
BugIt> list -p                                  # JSON output
BugIt> config -p                                # JSON for backup
```

### Beautiful Help System

BugIt leverages Typer's excellent help generation with Rich formatting:

```bash
# Main help with styled output
python cli.py --help

# Command-specific help
python cli.py new --help
python cli.py config --help

# Interactive shell help
python bugit.py
BugIt> help                                     # Beautiful welcome panel
BugIt> config --help                            # Styled command help
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
python cli.py list -s critical -p              # Filter critical, beautiful table
python cli.py edit 1 -a urgent -p              # Add tag, styled feedback
python cli.py config -g model -p               # Get model setting, styled

# Interactive shell with short flags
BugIt> list -s high                            # Filter high severity, beautiful table
BugIt> edit 1 -r old-tag                       # Remove tag, styled results
```

## Professional Output Examples

### Beautiful Tables
```bash
python cli.py list --pretty
```
```
┏━━━━━━━┳━━━━━━━━┳━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Index ┃ UUID   ┃ Date ┃ Severity ┃ Tags          ┃ Title                     ┃
┡━━━━━━━╇━━━━━━━━╇━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ [1]   │ 72e466 │ 2024 │ critical │ auth, login   │ Authentication Failure    │
│ [2]   │ a8f9b3 │ 2024 │ medium   │ ui, layout    │ Button Alignment Issue    │
└───────┴────────┴──────┴──────────┴───────────────┴───────────────────────────┘
```

### Styled Configuration Panel
```bash
python cli.py config --pretty
```
```
╭─ BugIt Configuration ────────────────────────────────────────────────────────────╮
│                                                                                  │
│  API Keys:                                                                       │
│    openai_api_key: sk-workf****** (.env file)                                    │
│                                                                                  │
│  Preferences:                                                                    │
│    model: gpt-4 (from .bugitrc)                                                  │
│    retry_limit: 3 (from .bugitrc)                                                │
│                                                                                  │
│  Quick Commands:                                                                 │
│    Set OpenAI API key: bugit config --set-api-key openai <key>                   │
│    Set model preference: bugit config --set model gpt-4                          │
│    Export preferences: bugit config --export config.json                         │
│                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────╯
```

### Interactive Shell Welcome
```bash
python bugit.py
```
```
╭─ Welcome ────────────────────────────────────────────────────────────────────────╮
│                                                                                  │
│  BugIt Interactive Shell                                                         │
│  AI-powered bug report management CLI                                            │
│                                                                                  │
│  Shell Commands:                                                                 │
│    help                 - Show command help                                      │
│    <command> --help     - Show help for specific command                         │
│    exit                 - Exit BugIt shell                                       │
│                                                                                  │
│  BugIt Commands:                                                                 │
│    config             - View or modify BugIt configuration                       │
│    delete             - Delete a bug report permanently                          │
│    edit               - Edit an existing bug report                              │
│    list               - List all bug reports with optional filtering             │
│    new                - Create a new bug report from a freeform description      │
│    show               - Show detailed information about a specific bug report    │
│                                                                                  │
│  Shell Mode: Pretty output by default, use -p for JSON                           │
│  Quote arguments with spaces: new "long bug description"                         │
│                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────╯

BugIt> 
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

# Batch process issues with styled feedback
python cli.py list -s critical | jq -r '.[] | .id' | \
  while read id; do
    python cli.py edit $id --add-tag needs-review --pretty
  done
```

### Mixed Workflow
```bash
# CLI for automation tasks
python cli.py list -s critical | jq -r '.[] | .id' > critical_issues.txt

# Shell for interactive review with beautiful interface
python bugit.py
BugIt> show 1              # Beautiful details panel for human review
BugIt> edit 1 -a reviewed  # Interactive editing with styled feedback
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

Test all functionality with real AI processing, file persistence, and beautiful styling:

```bash
# Create sample issues (real AI + file operations + styling)
python cli.py new "Critical login bug: users can't authenticate" --pretty
python cli.py new "Minor UI issue with button alignment" --pretty

# List and filter issues with beautiful tables
python cli.py list --pretty                    # Beautiful table
python cli.py list --severity critical --pretty

# Show detailed information with styled panels
python cli.py show 1 --pretty                  # Beautiful issue panel
python cli.py show abc123                      # JSON object

# Edit with styled feedback
python cli.py edit 1 --severity low --add-tag ui --pretty

# Delete with styled confirmation
python cli.py delete 2 --force

# Configuration management with beautiful panels
python cli.py config --set model gpt-3.5-turbo
python cli.py config --get model --pretty
python cli.py config --export backup.json
python cli.py config --pretty                  # Beautiful configuration panel
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
6. **Consult `_docs/BugIt_Style_Guide.md` for coding standards and styling guidelines**
7. **Use centralized styling system** - import from `core.styles` for consistency

## License

[Specify your license here] 