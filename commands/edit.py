"""
Edit command for modifying bug reports.
Supports field-specific updates and validation.
"""

import typer
import json
from typing import Optional
from core import storage, schema
from core.styles import Colors, Styles, PanelStyles
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def edit(
    id_or_index: str,
    title: Optional[str] = typer.Option(None, "--title", help="Update title"),
    severity: Optional[str] = typer.Option(
        None, "-s", "--severity", help="Update severity"
    ),
    add_tag: Optional[str] = typer.Option(None, "-a", "--add-tag", help="Add a tag"),
    remove_tag: Optional[str] = typer.Option(
        None, "-r", "--remove-tag", help="Remove a tag"
    ),
    pretty_output: bool = typer.Option(
        False, "-p", "--pretty", help="Output in human-readable format"
    ),
):
    """
    Edit an existing bug report.

    Args:
        id_or_index: Either the UUID or index (from list command) of the issue
        title: New title for the issue
        severity: New severity level
        add_tag: Tag to add to the issue
        remove_tag: Tag to remove from the issue
        pretty_output: Show human-readable output instead of JSON

    Default output is JSON for easy scripting and automation.
    Use --pretty for human-readable output with detailed messages.
    """
    try:
        # Get the issue to edit using new storage functions
        if id_or_index.isdigit():
            # Index-based selection - use new storage function
            issue = storage.get_issue_by_index(int(id_or_index))
        else:
            # UUID-based selection
            issue = storage.load_issue(id_or_index)

        # Track changes
        changes_made = False
        changes_log = []

        # Update fields
        if title:
            issue["title"] = title
            changes_made = True
            changes_log.append(f"Updated title: {title}")

        if severity:
            if severity.lower() in ["low", "medium", "high", "critical"]:
                issue["severity"] = severity.lower()
                changes_made = True
                changes_log.append(f"Updated severity: {severity.lower()}")
            else:
                error_msg = f"Invalid severity: {severity}. Must be low, medium, high, or critical."
                if pretty_output:
                    console.print(Styles.error(error_msg))
                else:
                    output = {"success": False, "error": error_msg}
                    console.print(json.dumps(output, indent=2))
                raise typer.Exit(1)

        # Handle tags
        tags = issue.get("tags", [])

        if add_tag:
            if add_tag not in tags:
                tags.append(add_tag)
                issue["tags"] = tags
                changes_made = True
                changes_log.append(f"Added tag: {add_tag}")
            else:
                changes_log.append(f"Tag '{add_tag}' already exists.")

        if remove_tag:
            if remove_tag in tags:
                tags.remove(remove_tag)
                issue["tags"] = tags
                changes_made = True
                changes_log.append(f"Removed tag: {remove_tag}")
            else:
                changes_log.append(f"Tag '{remove_tag}' not found.")

        if not changes_made:
            message = "No changes specified. Use --help to see available options."
            if pretty_output:
                console.print(f"[{Colors.WARNING}]ℹ[/{Colors.WARNING}] {message}")
            else:
                output = {"success": False, "message": message, "changes": changes_log}
                console.print(json.dumps(output, indent=2))
            return

        # Validate and save
        validated = schema.validate_or_default(issue)
        storage.save_issue(validated)

        if pretty_output:
            # Display changes in a styled format
            _display_edit_results(issue, changes_log)
        else:
            # JSON output
            output = {
                "success": True,
                "id": issue["id"],
                "changes": changes_log,
                "updated_issue": validated,
            }
            console.print(json.dumps(output, indent=2))

    except storage.StorageError as e:
        # Handle storage-specific errors
        error_msg = str(e)
        if pretty_output:
            console.print(Styles.error(f"Error: {error_msg}"))
        else:
            output = {"success": False, "error": error_msg}
            console.print(json.dumps(output, indent=2))
        raise typer.Exit(1)
    except schema.ValidationError as e:
        # Handle validation errors
        error_msg = f"Validation error: {e}"
        if pretty_output:
            console.print(Styles.error(error_msg))
        else:
            output = {"success": False, "error": error_msg}
            console.print(json.dumps(output, indent=2))
        raise typer.Exit(1)
    except typer.Exit:
        # Re-raise typer.Exit to preserve exit codes
        raise
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        if pretty_output:
            console.print(Styles.error(error_msg))
        else:
            output = {"success": False, "error": error_msg}
            console.print(json.dumps(output, indent=2))
        raise typer.Exit(1)


def _display_edit_results(issue: dict, changes_log: list):
    """Display edit results in a styled panel"""
    content = Text()

    # Issue identification
    content.append("Issue: ", style=Colors.SECONDARY)
    content.append(issue.get("title", "No title"), style=Colors.PRIMARY)
    content.append(f" ({issue['id']})\n\n", style=Colors.IDENTIFIER)

    # Changes made
    content.append("Changes Made:\n", style=f"bold {Colors.BRAND}")
    for change in changes_log:
        content.append(f"  • {change}\n", style=Colors.SUCCESS)

    content.append(
        f"\n[{Colors.SUCCESS}]✓[/{Colors.SUCCESS}] [dim]Issue updated successfully[/dim]"
    )

    # Display in a styled panel
    panel = Panel(content, title="Edit Complete", **PanelStyles.success())
    console.print(panel)
