# BugIt Style Guide

*Version 2.0 - Updated with PanelStyles and Enhanced Styling System*

This style guide ensures BugIt maintains a consistent, professional appearance across all interfaces while supporting both automation workflows and human interaction patterns.

---

## Centralized Styling System

### Overview

BugIt uses a comprehensive centralized styling system (`core/styles.py`) that provides consistent color schemes, formatting, and component styling across all commands. This system ensures:

- **Single Source of Truth**: All colors and styles defined in one place
- **Semantic Styling**: Colors have meaning (UUID = magenta, errors = red)
- **Component Consistency**: Panels, tables, and messages use standardized styling
- **Easy Maintenance**: Change the entire appearance by updating one file
- **Professional Appearance**: Left-aligned panels, consistent borders, proper spacing

### Using the Styling System

**Import the complete styling system:**
```python
from core.styles import Styles, Colors, TableStyles, PanelStyles
from rich.console import Console
from rich.panel import Panel
```

**Apply semantic styles:**
```python
# Format specific data types
Styles.uuid(issue_id)           # Magenta UUIDs
Styles.severity(severity)       # Dynamic severity coloring
Styles.date(created_at)         # Green dates
Styles.tags(tag_list)           # Yellow tags
Styles.title(title)             # White titles
Styles.error(error_msg)         # Red errors
Styles.success(success_msg)     # Green success messages
Styles.warning(warning_msg)     # Yellow warnings

# Get raw colors for Rich components
Colors.BRAND                    # Blue for borders, prompts
Colors.IDENTIFIER              # Magenta for UUIDs
Colors.SUCCESS                 # Green for dates, success
```

**Panel styling with PanelStyles:**
```python
# Use standardized panel configurations
panel = Panel(
    content,
    title="Panel Title",
    **PanelStyles.standard()    # Blue border, left-aligned, consistent padding
)

# Different panel types for different contexts
success_panel = Panel(content, title="Success", **PanelStyles.success())
error_panel = Panel(content, title="Error", **PanelStyles.error())
warning_panel = Panel(content, title="Warning", **PanelStyles.warning())
```

**Table styling example:**
```python
# Use predefined table styles
styles = TableStyles.issue_list()
table.add_column("UUID", style=styles["UUID"])
table.add_column("Date", style=styles["Date"])

# Dynamic severity coloring in table rows
table.add_row(
    issue_id,
    Styles.severity(severity_value),  # Auto-colored by severity
    date_value
)
```

---

## Color Palette

### Core Palette (Centralized in `Colors` class)

| Color    | Usage | Examples |
|----------|-------|----------|
| **Blue** (`BRAND`) | Brand identity, prompts, borders | Panel borders, "BugIt>" prompt, standard panels |
| **Cyan** (`INTERACTIVE`) | Interactive elements, commands | Index numbers `[1]`, command names, help text |
| **Red** (`ERROR`) | Errors, critical severity | Error messages, critical issues, error panels |
| **Green** (`SUCCESS`) | Success messages, dates | Creation dates, success confirmations, success panels |
| **Yellow** (`WARNING`) | Tags, warnings, medium severity | Issue tags, medium severity, warning panels |
| **Magenta** (`IDENTIFIER`) | UUIDs, unique identifiers | Issue IDs, file paths, unique values |
| **White** (`PRIMARY`) | Primary content, titles | Issue titles, main text, panel content |
| **Dim** (`SECONDARY`) | Secondary text, labels | Field labels, descriptions, metadata |

### Severity-Specific Colors

| Severity | Color | Usage |
|----------|-------|-------|
| **Critical** | Red | Critical severity issues, urgent items |
| **High** | Red | High severity issues, important items |
| **Medium** | Yellow | Medium severity issues, moderate priority |
| **Low** | Dim | Low severity issues, minor items |

---

## Component Standards

### Panels with PanelStyles

**Use the centralized PanelStyles system for consistency:**

```python
from core.styles import PanelStyles

# Standard panels (blue border)
panel = Panel(
    content,
    title="Issue Details",
    **PanelStyles.standard()
)

# Success panels (green border)
success_panel = Panel(
    content,
    title="Edit Complete",
    **PanelStyles.success()
)

# Error panels (red border)
error_panel = Panel(
    content,
    title="Error",
    **PanelStyles.error()
)

# Warning panels (yellow border)
warning_panel = Panel(
    content,
    title="Confirm Deletion",
    **PanelStyles.warning()
)
```

**PanelStyles provides:**
- **Consistent left alignment**: `title_align="left"`
- **Semantic border colors**: Different colors for different contexts
- **Standard padding**: `padding=(1, 2)` for all panels
- **Easy maintenance**: Change all panels by updating one place

### Tables

**Semantic Column Colors:**
```python
# Use TableStyles for consistency
styles = TableStyles.issue_list()
table.add_column("Index", style=styles["Index"])      # Cyan
table.add_column("UUID", style=styles["UUID"])        # Magenta  
table.add_column("Date", style=styles["Date"])        # Green
table.add_column("Severity", style=None)              # Dynamic
table.add_column("Tags", style=styles["Tags"])        # Yellow
table.add_column("Title", style=styles["Title"])      # White

# Dynamic content styling
table.add_row(
    f"[{index}]",
    uuid,
    date,
    Styles.severity(severity),  # Auto-colored by value
    tags,
    title
)
```

### Messages

**Consistent Message Types:**
```python
# Success messages
console.print(Styles.success("Issue created successfully"))

# Error messages  
console.print(Styles.error("Failed to save issue"))

# Warning messages
console.print(Styles.warning("Configuration not found"))

# Brand/prompt messages
console.print(f"[bold {Colors.BRAND}]BugIt>[/bold {Colors.BRAND}] ", end="")
```

---

## CLI Interface Standards

### Command Structure
```
bugit <command> [arguments] [options]
```

### Output Mode Design Philosophy

**Direct CLI Usage (Automation-First):**
- Default: JSON output for scripting and automation
- `--pretty` or `-p`: Beautiful Rich-formatted output when needed

**Interactive Shell (Human-First):** 
- Default: Beautiful Rich-formatted output for human interaction
- `-p` or `--pretty` flag: JSON output for copy-paste into automation

This dual approach optimizes for both automation workflows and human productivity.

### Short Flags for Efficiency

BugIt provides short flags for commonly used options to improve user experience:

| Short Flag | Long Flag | Commands | Purpose |
|------------|-----------|----------|---------|
| `-p` | `--pretty` | All | Human-readable output |
| `-s` | `--severity` | `list`, `edit` | Filter/set severity levels |
| `-t` | `--tag` | `list` | Filter by tag |
| `-a` | `--add-tag` | `edit` | Add tag to issue |
| `-r` | `--remove-tag` | `edit` | Remove tag from issue |
| `-f` | `--force` | `delete` | Skip confirmation prompts |
| `-g` | `--get` | `config` | Get specific config value |

**Design Principles:**
- Short flags use intuitive single characters
- Both short and long flags work identically
- Consistent across commands where applicable
- No conflicts between flag meanings

---

## Output Format Standards

### JSON Output (Default for CLI)

**Structure:** Clean, consistent JSON with proper indentation (`indent=2`)

**Example:**
```json
{
  "success": true,
  "id": "a1b2c3",
  "issue": {
    "title": "Bug title",
    "severity": "high"
  }
}
```

### Pretty Output (--pretty flag / Shell default)

**Styling:** Rich formatting with semantic colors and clear hierarchy

**Components:**
- **Tables**: Semantic column colors with dynamic content styling
- **Panels**: Consistent borders, left-aligned titles, proper padding
- **Messages**: Color-coded by type (success=green, error=red, etc.)

---

## Implementation Guidelines

### Adding New Commands

1. **Import the complete styling system:**
   ```python
   from core.styles import Styles, Colors, TableStyles, PanelStyles
   from rich.console import Console
   from rich.panel import Panel
   ```

2. **Use PanelStyles for all panels:**
   ```python
   # Standard panels
   panel = Panel(content, title="Title", **PanelStyles.standard())
   
   # Context-specific panels
   success_panel = Panel(content, title="Success", **PanelStyles.success())
   ```

3. **Use semantic styling functions:**
   ```python
   console.print("UUID: ", style=Colors.SECONDARY, end="")
   console.print(uuid, style=Colors.IDENTIFIER)
   console.print(Styles.severity(severity_value))  # Dynamic coloring
   ```

4. **Follow established patterns:**
   - Use `Colors.BRAND` for borders and prompts
   - Use `Styles.severity()` for dynamic severity coloring
   - Use `Colors.SECONDARY` for labels and descriptions
   - Use `Colors.PRIMARY` for main content
   - Use `PanelStyles.standard()` for most panels

### Modifying Colors or Styles

**To change the entire color scheme:**
1. Update the `Colors` class in `core/styles.py`
2. All commands automatically use the new colors
3. No other files need modification

**To add new panel types:**
1. Add new methods to `PanelStyles` class
2. Use the new panel type in relevant commands

**Example style modification:**
```python
class PanelStyles:
    @staticmethod
    def info():
        """Info panel styling for informational content"""
        return {
            "title_align": "left",
            "border_style": Colors.INTERACTIVE,  # Cyan border
            "padding": (1, 2)
        }
```

### Interactive Shell Best Practices

**Command Execution:**
- Execute commands directly (not through CliRunner) to preserve Rich formatting
- Default to pretty output for human interaction
- Support JSON mode with `-p` flag for automation needs

**Help System:**
- Leverage Typer's auto-generated help with Rich markup
- Dynamically extract command information from the app
- Provide both shell-specific and command-specific help

**Welcome Interface:**
- Use centralized styling for consistent appearance
- Show both shell commands and BugIt commands
- Provide usage examples and tips

---

## Professional Output Examples

### Beautiful Configuration Panel
```python
def _display_config_pretty(current_config: dict):
    content = Text()
    
    # API Keys section with brand styling
    content.append("API Keys:\n", style=f"bold {Colors.BRAND}")
    content.append("  openai_api_key: ", style=Colors.SECONDARY)
    content.append(masked_key, style=Colors.IDENTIFIER)
    
    # Use standard panel styling
    panel = Panel(
        content,
        title="BugIt Configuration",
        **PanelStyles.standard()
    )
    console.print(panel)
```

### Styled Edit Results
```python
def _display_edit_results(issue: dict, changes_log: list):
    content = Text()
    
    # Issue identification
    content.append("Issue: ", style=Colors.SECONDARY)
    content.append(issue.get('title', 'No title'), style=Colors.PRIMARY)
    content.append(f" ({issue['id']})\n\n", style=Colors.IDENTIFIER)
    
    # Changes with success styling
    content.append("Changes Made:\n", style=f"bold {Colors.BRAND}")
    for change in changes_log:
        content.append(f"  • {change}\n", style=Colors.SUCCESS)
    
    # Success panel for completion
    panel = Panel(
        content,
        title="Edit Complete",
        **PanelStyles.success()
    )
    console.print(panel)
```

---

This enhanced style guide ensures BugIt maintains a consistent, professional appearance across all interfaces while supporting both automation workflows and human interaction patterns. The centralized styling system with PanelStyles makes it easy to maintain consistency and create beautiful, functional CLI interfaces. 