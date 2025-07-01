# Product Requirements Document (PRD)

## Project Name: BugIt CLI

### Overview

BugIt is a CLI-first tool that enables developers to quickly capture unstructured bug reports without interrupting their development flow. It integrates with a locally-executed LangGraph AI backend, which internally uses remote LLM APIs (such as OpenAI or Anthropic) to transform freeform bug descriptions into structured JSON files with metadata such as title, severity, and tags. Markdown versions of each bug report may be generated as a stretch goal for human readability.

This tool is designed to operate seamlessly in terminal environments like Cursor and will serve as the backend for a potential future MCP (Multi Command Palette) interface.

**Current Status:** Phase 1 Implementation Complete ✅
- All 6 core commands implemented with enhanced stubs
- Production-ready CLI experience with Rich formatting
- Comprehensive test suite (9/9 tests passing)
- Secure API key management with .env persistence
- Multi-provider AI support architecture ready

---

### Goals

- Minimize friction in capturing bug reports while coding
- Automatically generate structured bug metadata using LLMs via LangGraph
- Maintain local storage in machine-readable format (JSON)
- Build a foundation for future GUI or VSCode/Cursor MCP integrations

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

- LangGraph processing pipeline:
- Expected LangGraph output schema (MVP):
  ```json
  {
    "title": "string",
    "type": "any string (LLM-generated)",
    "tags": ["string", ...],
    "severity": "low" | "medium" | "high" | "critical"
  }
  ```
  Fields must be present. `title`, `tags`, and `severity` must be validated or defaulted. `type` is accepted as-is.

  - Summarize bug description into a title
  - Auto-classify report type (`bug`, `feature`, etc.)
  - Suggest tags
  - Estimate severity

#### Current Implementation Details ✅

**Enhanced Stub System:**
- Intelligent keyword-based processing for realistic AI simulation
- Predictable mock data for development and testing
- Full CLI functionality with proper error handling
- Rich-formatted table output for `bugit list`

**Security-First Configuration:**
- API keys stored in `.env` file (git-ignored)
- User preferences in `.bugitrc` file
- Environment variable override support
- Multi-provider support ready (OpenAI, Anthropic, Google)

#### Output Format ✅ IMPLEMENTED

- JSON as the source of truth  
- Files must include `"schema_version": "v1"`

**Example JSON**:

```json
{
  "id": "a1b2c3",
  "schema_version": "v1",
  "title": "Logout screen hangs on exit",
  "description": "App gets stuck after logging out. Needs force close.",
  "tags": ["auth", "logout"],
  "severity": "critical",
  "created_at": "2025-06-30T12:50:00"
}
```

---

### Examples

#### `bugit new` ✅

```bash
bugit new "the logout button doesn't actually log the user out unless you restart the app"
```

```json
{
  "id": "a1b2c3",
  "schema_version": "v1",
  "title": "Logout button fails to end session without app restart",
  "description": "Pressing the logout button does not actually end the session. The app requires a restart to complete logout.",
  "tags": ["auth", "session", "logout"],
  "severity": "critical",
  "created_at": "2025-07-01T13:00:00"
}
```

#### `bugit list` ✅

```bash
bugit list
```

| Index | UUID   | Date       | Severity | Tags         | Title                                 |
| ----- | ------ | ---------- | -------- | ------------ | ------------------------------------- |
| [1]   | a1b2c3 | 2025-07-01 | critical | auth, logout | Logout button fails to end session... |
| [2]   | d4e5f6 | 2025-07-01 | medium   | camera, ui   | Recording UI misleads...              |

Optional filters:

- `--json`: return full list in JSON format
- `--tag <tag>`: filter by tag (e.g., `camera`)
- `--severity <level>`: filter by severity (`low`, `medium`, `high`, `critical`)

Results are sorted by default as:

1. `severity` descending (critical → low)
2. `created_at` descending

Custom sorting is not supported in MVP.

#### `bugit show <id or index>` ✅

```bash
bugit show 1
bugit show a1b2c3
```

#### `bugit config` ✅ ENHANCED

```bash
# Set API key securely
bugit config --set-api-key sk-your-openai-api-key-here

# View current configuration
bugit config

# Set model preference
bugit config --set model gpt-4

# Export configuration
bugit config --export backup.json
```

---

### Technical Stack ✅ IMPLEMENTED

- CLI: Python with [Typer](https://typer.tiangolo.com/)
- AI pipeline: LangGraph (Python, running in-process) - **Enhanced stubs implemented**
- Storage: Local filesystem (JSON) — issues saved to `./.bugit/issues/<uuid>.json`
- Formatting: Rich library for beautiful CLI output
- Testing: pytest with comprehensive test coverage
- Security: python-dotenv for secure API key management

---

### Constraints ✅ IMPLEMENTED
- All CLI outputs should be plain, human-readable text in table or JSON format.
- Colorized output, table wrapping/truncation, and UI enhancements may be added as a stretch goal.

- All file writes must be atomic and safe for concurrent use. This is achieved via OS-level file locking or write-then-rename behavior. **🔄 Next Phase**
- Schema versioning is required for all stored issues. MVP uses `"schema_version": "v1"`. ✅
- Fully CLI-scriptable — no interactive prompts. ✅
- UUIDs must be used for issue IDs. ✅
- Indexes (e.g. `bugit show 1`) are ephemeral, sorted by `created_at` descending by default. Sorting can be customized via `--sort`. ✅
- Max character length for description: 10,000; title: 120. ✅
- Input must be valid UTF-8 plain text. ✅
- Model name must be specified explicitly (no "latest" aliases). ✅
- API key and model selection can be set via CLI flags, environment variables, or `.bugitrc`. ✅
- Pretty-printed JSON output by default, with optional compact mode. ✅
- LangGraph must run locally — no HTTP server. ✅
- Enum fields (`severity`, `type`) must be valid or fallback to defaults. ✅
- Output from `bugit list` must be sorted by severity descending, then created_at descending. ✅
- Malformed LangGraph output must be caught. In MVP, a single failure will abort the command and print an error. ✅
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

**Multi-Layer Configuration (Priority: Environment > .env > .bugitrc > defaults):**

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

#### 3. Environment Variable Overrides
```bash
export BUGIT_MODEL=gpt-3.5-turbo
export BUGIT_OUTPUT_FORMAT=json
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

#### 🔄 Phase 2: Real LangGraph Integration - NEXT
- Replace stubs with actual LangGraph pipeline
- Implement real LLM API calls via LangGraph
- Add retry logic and error recovery
- Token usage tracking and cost management

#### 🔄 Phase 3: Production File Operations - NEXT
- Atomic file writes with write-then-rename
- Concurrent access safety with file locking
- Real issue storage and retrieval
- Index management and caching

### Stretch Goals
- Testing strategy and tooling: ✅ **Implemented**
  - Simulated LangGraph inputs and malformed output tests
  - Schema validation for stored issues and config
  - CLI integration tests for concurrency and file safety

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