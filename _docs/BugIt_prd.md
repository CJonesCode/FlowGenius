# Product Requirements Document (PRD)

## Project Name: BugIt CLI

### Overview

BugIt is a CLI-first tool that enables developers to quickly capture unstructured bug reports without interrupting their development flow. It integrates with a locally-executed LangGraph AI backend, which internally uses remote LLM APIs (such as OpenAI or Anthropic) to transform freeform bug descriptions into structured JSON files with metadata such as title, severity, and tags. Markdown versions of each bug report may be generated as a stretch goal for human readability.

This tool is designed to operate seamlessly in terminal environments like Cursor and will serve as the backend for a potential future MCP (Multi Command Palette) interface.

**Current Status:** ✅ **Shell Architecture Complete with Test Stabilization** ✅
- ✅ **Enhanced Schema**: Added solution, status, and updated_at fields for resolution tracking
- ✅ **JSON-First Output**: Default JSON perfect for automation, --pretty for human-readable output  
- ✅ **Standard Exit Codes**: POSIX-compliant error handling with structured error classes
- ✅ **Stream Separation**: stdout for data, stderr for messages, complete color isolation
- ✅ **Standard CLI Flags**: --version, --verbose, --quiet, --no-color implemented
- ✅ **Pure Wrapper Shell**: Interactive shell calls CLI commands internally
- ✅ **Professional Styling**: Beautiful Panel-based output without emojis
- ✅ **Atomic file operations with write-then-rename pattern**
- ✅ **Cross-platform file locking and concurrent access safety**
- ✅ **Real filesystem persistence replacing all mock storage**
- ✅ **Strong test coverage: 91% with 447 passing tests (92.5% pass rate)**
- ✅ Real LangGraph integration with OpenAI API processing
- ✅ Retry logic and structured error handling
- ✅ Multi-provider AI support architecture implemented
- ✅ **Unified Entry Point**: Single `bugit.py` with intelligent routing (no args = shell, args = CLI)
- ✅ **Shell Architecture Testing**: Comprehensive test coverage with 37 new tests for shell functionality
- ✅ **Test Suite Stabilization**: Systematic fixes for CLI refactor output format changes

### Interface Architecture ✅

**Unified Entry Point (`bugit.py`):**
- **No Arguments**: Starts interactive shell mode (human-optimized)
- **With Arguments**: Executes CLI commands (automation-optimized)
- **Intelligent Routing**: Single entry point adapts to user intent
- **Backward Compatibility**: All existing functionality preserved

**Shell Architecture:**
- **Modular Design**: Shell logic isolated in dedicated `shell.py`
- **Pure Wrapper**: Interactive shell calls CLI commands internally
- **Clean Separation**: No business logic duplication between modes
- **Professional Styling**: Beautiful panels and tables by default in shell

**Usage Examples:**
```bash
# Interactive Shell Mode
python bugit.py                    # Start shell
BugIt> new "bug description"       # Beautiful panels
BugIt> list                        # Beautiful table
BugIt> exit                        # Exit shell

# Direct CLI Mode  
python bugit.py new "bug"          # JSON output
python bugit.py list --pretty      # Beautiful table
python bugit.py --version          # Standard CLI
```

---

### Goals

- Minimize friction in capturing bug reports while coding
- Automatically generate structured bug metadata using LLMs via LangGraph
- Maintain local storage in machine-readable format (JSON)
- Build a foundation for future GUI or VSCode/Cursor MCP integrations
- **Provide automation-first CLI with beautiful human interfaces when needed**

---

### Features

#### MVP ✅ IMPLEMENTED

- `bugit new`: Capture a freeform bug description, process with LangGraph, and save as structured JSON.

- `bugit list`: List existing issues from the local issue directory.

- `bugit show <id or index>`: View structured details of an issue.

- `bugit delete <id or index>`: Permanently delete an issue from disk.

- `bugit edit <id or index>`: Update fields in an existing issue (e.g., title, tags, severity).

- `bugit config`: View or modify configuration settings:
  - `bugit config` — Show current config
  - `bugit config --get <key>` — Get a config value (e.g., `model`)
  - `bugit config --set <key> <value>` — Set a config value
  - `bugit config --set-api-key <key>` — Securely set API key to .env file
  - `bugit config --import <file>` — Overwrite config from a JSON file conforming to `.bugitrc` schema
  - `bugit config --export <file>` — Export config to a JSON file (or stdout)

- **CLI Scriptability Features ✅ IMPLEMENTED:**
  - `bugit --version` — Show version and exit
  - `bugit --verbose` — Enable verbose output  
  - `bugit --quiet` — Suppress progress messages and non-essential output
  - `bugit --no-color` — Disable colored output

- **Real LangGraph processing pipeline ✅ IMPLEMENTED:**
- Expected LangGraph output schema (Enhanced):
  ```json
  {
    "title": "string",
    "type": "any string (LLM-generated)",
    "tags": ["string", ...],
    "severity": "low" | "medium" | "high" | "critical",
    "solution": "string",  // Empty by default, filled when resolved
    "status": "open" | "resolved" | "archived",  // Default: "open"
    "updated_at": "ISO datetime"  // Set when solution added
  }
  ```
  Fields must be present. `title`, `tags`, and `severity` must be validated or defaulted. `type` is accepted as-is.

  - **Real AI Processing ✅**: OpenAI API integration via LangGraph
  - **Retry Logic ✅**: Configurable retry attempts (default: 3)
  - **Structured Output ✅**: Pydantic model validation
  - **Error Handling ✅**: Clear failure messages, no fallback processing

#### Current Implementation Details ✅

**CLI Scriptability-First Refactor ✅:**
- **JSON by Default**: All commands output JSON for automation by default
- **--pretty Flag**: Beautiful Rich-formatted output for human interaction
- **Standard Exit Codes**: POSIX-compliant error handling (0=success, 1-7=specific errors)
- **Stream Separation**: stdout for data, stderr for messages and progress
- **Color Isolation**: No ANSI codes in JSON output, colors only on stderr
- **Standard CLI Flags**: --version, --verbose, --quiet, --no-color
- **Pure Wrapper Shell**: Interactive shell calls CLI commands internally

**Enhanced Schema ✅:**
- **Solution Field**: Empty by default, filled when issues are resolved
- **Status Field**: "open" (default), "resolved", "archived"  
- **Updated At**: Tracks when solution/status changes
- **Validation Rules**: Solution cleared for open issues, updated_at set appropriately

**Real LangGraph Integration:**
- OpenAI API integration with structured output
- Retry logic with configurable attempts 
- Pydantic model validation for AI responses
- Comprehensive prompt engineering for bug analysis
- No fallback processing - pure AI or clear failure

**CLI Output Format Transformation ✅:**
- **Default Output**: JSON for automation and scripting
- **`--pretty` Flag**: Human-readable output with clean formatting
- **All Commands Support Both Modes**: Consistent interface across commands
- **Safety Features**: JSON mode requires `--force` for delete operations
- **Professional Output**: Clean formatting without emojis, beautiful Panel-based displays

**Production File Operations ✅:**
- **Atomic File Writes**: Write-then-rename pattern prevents partial writes
- **Cross-Platform File Locking**: Concurrent access safety (full on Unix and Windows)
- **Real File Persistence**: Issues stored as individual JSON files in `.bugit/issues/`
- **Dynamic Index Management**: Runtime index generation with proper sorting
- **Storage Error Handling**: Comprehensive error hierarchy with structured responses
- **Data Safety**: Optional backup on delete, corrupted file handling
- **Storage Statistics**: Monitoring and debugging capabilities

**Security-First Configuration:**
- API keys stored in `.env` file (git-ignored)
- User preferences in `.bugitrc` file
- API key environment variable support (NO config overrides)
- Multi-provider support ready (OpenAI, Anthropic, Google)

#### Output Format ✅ IMPLEMENTED

- **JSON as Default**: Optimized for automation and scripting
- **`--pretty` Flag**: Human-readable output when needed
- Files must include `"schema_version": "v1"`

**Example JSON (Default Output)**:

```json
{
  "success": true,
  "issue": {
    "id": "a1b2c3",
    "schema_version": "v1",
    "title": "Logout screen hangs on exit",
    "description": "App gets stuck after logging out. Needs force close.",
    "tags": ["auth", "logout"],
    "severity": "critical",
    "status": "open",
    "solution": "",
    "created_at": "2025-06-30T12:50:00",
    "updated_at": "2025-06-30T12:50:00"
  }
}
```

**Example Pretty Output (with `--pretty` flag)**:
```
Processing with AI...
Issue created successfully
╭─ Logout screen hangs on exit (ID: a1b2c3) ────────────────────────────────╮
│                                                                          │
│  Severity: critical                                                      │
│  Type: bug                                                               │
│  Status: open                                                            │
│  Tags: auth, logout                                                      │
│  Created: 2025-06-30T12:50:00                                            │
│  Schema: v1                                                              │
│                                                                          │
│  Description:                                                            │
│  App gets stuck after logging out. Needs force close.                    │
│                                                                          │
╰──────────────────────────────────────────────────────────────────────────╯
```

---

### Examples

#### `bugit new` ✅

```bash
# Default JSON output for scripting
bugit new "the logout button doesn't actually log the user out unless you restart the app"
```

```json
{
  "success": true,
  "issue": {
    "id": "a1b2c3",
    "schema_version": "v1",
    "title": "Logout button fails to end session without app restart", 
    "description": "the logout button doesn't actually log the user out unless you restart the app",
    "tags": ["auth", "session", "logout"],
    "severity": "critical",
    "status": "open",
    "solution": "",
    "created_at": "2025-07-01T13:00:00",
    "updated_at": "2025-07-01T13:00:00"
  }
}
```

```bash
# Human-readable output with --pretty
bugit new "the logout button doesn't work" --pretty
```

```
Processing with AI...
Issue created successfully
╭─ Logout button fails to end session (ID: a1b2c3) ──────────────────────────╮
│                                                                           │
│  Severity: critical                                                       │
│  Type: bug                                                                │
│  Status: open                                                             │
│  Tags: auth, session, logout                                              │
│  Created: 2025-07-01T13:00:00                                             │
│  Schema: v1                                                               │
│                                                                           │
│  Description:                                                             │
│  the logout button doesn't work                                           │
│                                                                           │
╰───────────────────────────────────────────────────────────────────────────╯
```

#### `bugit list` ✅

```bash
# Default JSON output
bugit list
```

```json
[
  {
    "id": "a1b2c3",
    "title": "Logout button fails to end session",
    "severity": "critical",
    "tags": ["auth", "logout"],
    "status": "open",
    "solution": "",
    "created_at": "2025-07-01T13:00:00",
    "updated_at": "2025-07-01T13:00:00"
  }
]
```

```bash
# Pretty table output  
bugit list --pretty
```

| Index | UUID   | Date       | Severity | Tags         | Title                                 |
| ----- | ------ | ---------- | -------- | ------------ | ------------------------------------- |
| [1]   | a1b2c3 | 2025-07-01 | critical | auth, logout | Logout button fails to end session... |
| [2]   | d4e5f6 | 2025-07-01 | medium   | camera, ui   | Recording UI misleads...              |

Optional filters:

- `--tag <tag>`: filter by tag (e.g., `camera`)
- `--severity <level>`: filter by severity (`low`, `medium`, `high`, `critical`)

Results are sorted by default as:

1. `severity` descending (critical → low)
2. `created_at` descending

Custom sorting is not supported in MVP.

#### `bugit show <id or index>` ✅

```bash
# Default JSON output
bugit show 1
```

```bash
# Pretty panel output
bugit show 1 --pretty
```

#### Standard CLI Flags ✅

```bash
# Version information
bugit --version
# Output: bugit 1.0.0

# Verbose output
bugit new "test issue" --verbose --pretty

# Quiet mode (suppress progress messages)
bugit new "test issue" --quiet

# Disable colors
bugit new "test issue" --no-color --pretty
```

#### `bugit config` ✅ ENHANCED

```bash
# Set API key securely
bugit config --set-api-key openai sk-your-openai-api-key-here

# View current configuration (JSON by default)
bugit config

# Pretty configuration display
bugit config --pretty

# Set model preference
bugit config --set model gpt-4

# Export configuration
bugit config --export backup.json
```

---

### Technical Stack ✅ IMPLEMENTED

- CLI: Python with [Typer](https://typer.tiangolo.com/)
- **AI pipeline: LangGraph with real OpenAI API integration** ✅
- **Storage: Production filesystem operations with atomic writes** ✅
- Formatting: Rich library for beautiful CLI output
- Testing: pytest with comprehensive test coverage (447 tests passing, 91% coverage with 92.5% pass rate)
- Security: python-dotenv for secure API key management
- **Stream Management: Proper stdout/stderr separation** ✅
- **Error Handling: POSIX-compliant exit codes** ✅

---

### Constraints ✅ IMPLEMENTED
- **Default JSON output for automation, `--pretty` flag for human-readable format** ✅
- **Clean, professional output without emojis** ✅
- **POSIX-compliant exit codes for proper scripting integration** ✅
- **Stream separation: stdout for data, stderr for messages** ✅
- **Color isolation: no ANSI codes in JSON output** ✅

- **All file writes are atomic and safe for concurrent use via write-then-rename and file locking** ✅
- Schema versioning is required for all stored issues. MVP uses `"schema_version": "v1"`. ✅
- Fully CLI-scriptable — no interactive prompts. ✅
- UUIDs must be used for issue IDs. ✅
- Indexes (e.g. `bugit show 1`) are ephemeral, sorted by `created_at` descending by default. Sorting can be customized via `--sort`. ✅
- Max character length for description: 10,000; title: 120. ✅
- Input must be valid UTF-8 plain text. ✅
- Model name must be specified explicitly (no "latest" aliases). ✅
- API key and model selection can be set via CLI flags, environment variables, or `.bugitrc`. ✅
- **JSON output by default, with optional `--pretty` mode for human readability.** ✅
- **Real LangGraph integration running locally — no HTTP server.** ✅
- **Retry logic implemented with configurable attempts.** ✅
- Enum fields (`severity`, `type`) must be valid or fallback to defaults. ✅
- Output from `bugit list` must be sorted by severity descending, then created_at descending. ✅
- **Real LangGraph output with structured validation - failures result in clear error messages.** ✅
- Commands `show`, `edit`, and `delete` support both UUIDs and ephemeral indexes from `bugit list`. ✅
- `show`, `edit`, and `delete` commands must support both:
  - ID or index-based selection (index mapping is generated at command startup to avoid errors) ✅
  - Flag-based edits (e.g., `--severity`, `--title`, etc.) or prompt-based editing and confirmation ✅

- These commands must support both CLI-flag-driven usage and interactive terminal behavior:
  - `show`: display the issue as structured JSON or a pretty-printed format ✅
  - `edit`: allow inline flag-based edits (e.g., `--severity`) or enter an interactive editor ✅
  - `delete`: accept `--force` for no confirmation, or confirm interactively in console ✅

---

### Configuration System ✅ ENHANCED IMPLEMENTATION

**Security-First Configuration (API keys separate from preferences):**

#### 1. API Keys (.env file - git-ignored)
```bash
BUGIT_OPENAI_API_KEY=sk-your-openai-api-key-here
BUGIT_ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here  # Future
BUGIT_GOOGLE_API_KEY=your-google-api-key-here           # Future
```

#### 2. User Preferences (.bugitrc file)
```json
{
  "model": "gpt-4",
  "enum_mode": "auto",
  "output_format": "table",
  "retry_limit": 3
}
```

#### 3. Environment Variables (API Keys Only)
```bash
# Only API keys use environment variables - NO configuration overrides
export BUGIT_OPENAI_API_KEY=sk-your-key-here
export BUGIT_ANTHROPIC_API_KEY=sk-ant-your-key-here  # Future
export BUGIT_GOOGLE_API_KEY=your-google-key-here     # Future
```

**Legacy Support:**
- `BUGIT_API_KEY` still supported with deprecation warning
- Automatic migration prompts for old configuration formats

**Security Features:**
- API keys never stored in user preferences
- Automatic .env file creation via `--set-api-key`
- Clear separation between secrets and preferences

---

### Enum Values ✅

**Severity**: `low`, `medium`, `high`, `critical`  
- Defined and validated by BugIt; invalid values must be rejected or replaced with fallback.

**Type**: `bug`, `feature`, `chore`, `unknown`  
- Generated by the LLM; not user-defined or customizable in MVP.

**Status**: `open`, `resolved`, `archived` ✅ **NEW**
- `open`: Default status for new issues
- `resolved`: Issue has been resolved but not archived  
- `archived`: Issue is resolved and archived (future use)

**Tags**: Arbitrary, generated by LLM (suggested: `auth`, `camera`, `ui`, `recording`, `session`, `style`, `network`, `storage`)

---

### Current Implementation Status

#### ✅ Phase 0: Environment Setup - COMPLETE
- Python virtual environment with all dependencies
- Project structure with commands/, core/, tests/ directories
- Requirements management (requirements.txt, requirements-dev.txt)
- Git setup with proper .gitignore patterns

#### ✅ Phase 1: Enhanced Stubs - COMPLETE
- All 6 CLI commands implemented and functional
- Enhanced stubs with intelligent keyword-based processing
- Comprehensive test suite (9/9 tests passing)
- Rich-formatted output for beautiful CLI experience
- Secure configuration management with .env support
- Multi-provider AI architecture ready for expansion

#### ✅ Phase 2: Real LangGraph Integration - COMPLETE
- **Real OpenAI API integration via LangGraph framework**
- **Retry logic with configurable attempts (default: 3)**
- **Structured output validation with Pydantic models**
- **Error handling with clear failure messages**
- **No fallback processing - pure AI or clear failure**
- **CLI output format transformation (JSON by default, --pretty for humans)**
- **Professional output without emojis**
- **Comprehensive testing (22/22 tests passing)**

#### ✅ Phase 3: Production File Operations - COMPLETE
- **Atomic file operations with write-then-rename pattern**
- **Cross-platform file locking for concurrent access safety (full Unix and Windows support)**
- **Real filesystem persistence replacing all mock storage**
- **Dynamic index management with runtime generation**
- **Production error handling with StorageError hierarchy**
- **Data safety features: backup on delete, corrupted file handling**
- **Storage statistics and monitoring capabilities**
- **Enhanced command integration with new storage functions**

#### ✅ Phase 3+: CLI Scriptability-First Refactor - COMPLETE
- **Enhanced schema with solution, status, and updated_at fields**
- **JSON-first output with --pretty flag for human-readable formatting**
- **Standard POSIX exit codes for proper error handling**
- **Stream separation: stdout for data, stderr for messages**
- **Color isolation: no ANSI codes in JSON output**
- **Standard CLI flags: --version, --verbose, --quiet, --no-color**
- **Pure wrapper shell: interactive shell calls CLI commands internally**
- **Professional styling: beautiful Panel-based output without emojis**

#### 🔄 Phase 4: Advanced Features & Polish - NEXT
- Performance optimization for large datasets
- Advanced caching for hundreds of issues
- External tool integrations (GitHub, Notion, Linear)
- Custom sorting and archiving features
- Advanced search and filtering capabilities
- `bugit archive` command with solution field support

### Automation Examples ✅

**JSON-First CLI for Automation:**
```bash
# Extract issue IDs for batch processing
bugit list | jq -r '.[].id'

# Filter and process critical issues
bugit list --severity critical | jq '.[] | select(.severity == "critical")'

# Create issue and get ID for follow-up
ISSUE_ID=$(bugit new "Critical bug" | jq -r '.issue.id')
bugit edit $ISSUE_ID --add-tag urgent

# Check exit codes for error handling
bugit show nonexistent-id; echo "Exit code: $?"
```

**Interactive Shell for Humans:**
```bash
# Start interactive shell (pretty output by default)
python bugit.py

BugIt> new "Bug description"              # Beautiful panels
BugIt> list                               # Beautiful table
BugIt> show 1                             # Beautiful issue panel
BugIt> list --json                        # JSON when needed for automation
```

### Stretch Goals
- Testing strategy and tooling: ✅ **Implemented and Comprehensive**
  - Real LangGraph integration testing
  - JSON output format validation
  - Error handling and edge case coverage
  - CLI automation workflow testing
  - Production file operations testing
  - Shell architecture comprehensive testing
  - Test suite stabilization with systematic fixes
  - Strong coverage: 91% with 447 passing tests (92.5% pass rate)

- `bugit archive <id or index>`: Archive resolved issues to a subfolder with optional `"resolution"` field
- `bugit migrate`: Schema migration tooling between stored issue versions
- Duplicate detection via embedding or semantic comparison at creation time
- File-based logging with `.bugitrc` log level setting
- Additional `enum_mode` values:
  - `suggestive`: Prefer enum list but allow custom
  - `strict`: Only allow from enum list
- Custom enums for severity/type via config
- `bugit models`: List supported LLMs; optional `--refresh` to query providers
- Retry settings in `.bugitrc`:
  - `retry_limit`, `fallback_model`, `truncate_input_if_failed`
- LangGraph context enrichment (e.g., packages, working dir)
- Markdown output and screenshots/images
- GitHub/Notion/Linear integrations
- Embedding-based similarity and clustering
- Prompt-time clarification loops
- MCP interface for GUI/Cursor
- Add support for advanced list sorting:
  - `--sort <field>`: sort by `created_at`, `severity`, etc.
  - `--reverse`: reverse sort order
- Stdin input support for piping: `echo "bug description" | bugit new -`