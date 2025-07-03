# BugIt Style Guide

*Version 1.1 - Updated with Centralized Styling System*

This style guide ensures BugIt maintains a consistent, professional appearance across all interfaces while supporting both automation workflows and human interaction patterns.

---

## Centralized Styling System

### Overview

BugIt uses a centralized styling system (`core/styles.py`) that provides consistent color schemes and formatting across all commands. This system ensures:

- **Single Source of Truth**: All colors defined in one place
- **Semantic Styling**: Colors have meaning (UUID = magenta, errors = red)
- **Easy Maintenance**: Change the entire color scheme by updating one file
- **Consistent Experience**: Same elements look the same everywhere

### Using the Styling System

**Import the styling system:**
```python
from core.styles import Styles, Colors, TableStyles
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

# Get raw colors for Rich components
Colors.BRAND                    # Blue for borders, prompts
Colors.IDENTIFIER              # Magenta for UUIDs
Colors.SUCCESS                 # Green for dates, success
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
| **Blue** (`BRAND`) | Brand identity, prompts, borders | Panel borders, "BugIt>" prompt |
| **Cyan** (`INTERACTIVE`) | Interactive elements, commands | Index numbers `[1]`, command names |
| **Red** (`ERROR`) | Errors, critical severity | Error messages, critical issues |
| **Green** (`SUCCESS`) | Success messages, dates | Creation dates, success confirmations |
| **Yellow** (`WARNING`) | Tags, warnings, medium severity | Issue tags, medium severity |
| **Magenta** (`IDENTIFIER`) | UUIDs, unique identifiers | Issue IDs, file paths |
| **White** (`PRIMARY`) | Primary content, titles | Issue titles, main text |
| **Dim** (`SECONDARY`) | Secondary text, labels | Field labels, descriptions |

### Severity-Specific Colors

| Severity | Color | Usage |
|----------|-------|-------|
| **Critical** | Red | Critical severity issues |
| **High** | Red | High severity issues |
| **Medium** | Yellow | Medium severity issues |
| **Low** | Dim | Low severity issues |

---

## Component Standards

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

### Panels

**Consistent Panel Styling:**
```python
# Use centralized border color
panel = Panel(
    content,
    title=title_text,
    border_style=Colors.BRAND,  # Consistent blue borders
    padding=(1, 2)
)

# Rich Text content with semantic styling
content = Text()
content.append("Severity: ", style=Colors.SECONDARY)
content.append(severity, style=Styles.get_severity_color(severity))
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
console.print(Styles.brand("BugIt> "))
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
- `--pretty` or `-p`: Human-readable output when needed

**Interactive Shell (Human-First):** 
- Default: Pretty output for human interaction
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

### JSON Output (Default)

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

### Pretty Output (--pretty flag)

**Styling:** Rich formatting with semantic colors and clear hierarchy

**Components:**
- **Tables**: Semantic column colors with dynamic content styling
- **Panels**: Blue borders with consistent internal formatting  
- **Messages**: Color-coded by type (success=green, error=red, etc.)

---

## Implementation Guidelines

### Adding New Commands

1. **Import styling system:**
   ```python
   from core.styles import Styles, Colors, TableStyles
   ```

2. **Use semantic styling functions:**
   ```python
   console.print("UUID: ", style=Colors.SECONDARY, end="")
   console.print(uuid, style=Colors.IDENTIFIER)
   ```

3. **Follow established patterns:**
   - Use `Colors.BRAND` for borders and prompts
   - Use `Styles.severity()` for dynamic severity coloring
   - Use `Colors.SECONDARY` for labels and descriptions
   - Use `Colors.PRIMARY` for main content

### Modifying Colors

**To change the entire color scheme:**
1. Update the `Colors` class in `core/styles.py`
2. All commands automatically use the new colors
3. No other files need modification

**Example color scheme change:**
```python
class Colors:
    BRAND = "purple"        # Changed from blue
    IDENTIFIER = "cyan"     # Changed from magenta
    # ... other colors
```

---

This style guide ensures BugIt maintains a consistent, professional appearance across all interfaces while supporting both automation workflows and human interaction patterns. The centralized styling system makes it easy to maintain consistency and adapt the visual design as needed. 