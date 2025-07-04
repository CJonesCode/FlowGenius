"""
Delete command for removing bug reports.
Supports both UUID and index-based selection with confirmation.
"""

import json

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from core import storage
from core.styles import Colors, PanelStyles, Styles

console = Console()


def delete(
    id_or_index: str,
    force: bool = typer.Option(False, "-f", "--force", help="Skip confirmation prompt"),
    pretty_output: bool = typer.Option(
        False, "-p", "--pretty", help="Output in human-readable format"
    ),
):
    """
    Delete a bug report permanently.

    Args:
        id_or_index: Either the UUID or index (from list command) of the issue
        force: Skip confirmation prompt
        pretty_output: Show human-readable output instead of JSON

    Default output is JSON for easy scripting and automation.
    Use --pretty for human-readable output with confirmation prompts.
    """
    try:
        # Get the issue to delete using new storage functions
        if id_or_index.isdigit():
            # Index-based selection - use new storage function
            issue = storage.get_issue_by_index(int(id_or_index))
        else:
            # UUID-based selection
            issue = storage.load_issue(id_or_index)

        issue_id = issue["id"]

        # Show what will be deleted and handle confirmation
        if pretty_output:
            _display_deletion_preview(issue)

            # Confirm deletion unless --force is used
            if not force:
                confirm = typer.confirm(
                    f"[{Colors.ERROR}]Are you sure you want to delete this issue?[/{Colors.ERROR}]"
                )
                if not confirm:
                    console.print(
                        f"[{Colors.WARNING}]ℹ[/{Colors.WARNING}] Deletion cancelled."
                    )
                    return
        else:
            # In JSON mode, --force is required for safety
            if not force:
                output = {
                    "success": False,
                    "error": "Confirmation required. Use --force to delete without confirmation in JSON mode.",
                    "issue_to_delete": {"id": issue_id, "title": issue["title"]},
                }
                console.print(json.dumps(output, indent=2))
                return

        # Delete the issue (new storage function raises exception on failure)
        storage.delete_issue(issue_id)

        if pretty_output:
            _display_deletion_success(issue)
        else:
            output = {"success": True, "id": issue_id, "title": issue["title"]}
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


def _display_deletion_preview(issue: dict):
    """Display what will be deleted in a styled panel"""
    content = Text()

    content.append(
        "⚠️  WARNING: This action cannot be undone!\n\n", style=f"bold {Colors.ERROR}"
    )

    content.append("Issue to delete:\n", style=f"bold {Colors.BRAND}")
    content.append("  Title: ", style=Colors.SECONDARY)
    content.append(issue.get("title", "No title"), style=Colors.PRIMARY)
    content.append("\n")

    content.append("  ID: ", style=Colors.SECONDARY)
    content.append(issue["id"], style=Colors.IDENTIFIER)
    content.append("\n")

    if issue.get("severity"):
        content.append("  Severity: ", style=Colors.SECONDARY)
        content.append(
            issue["severity"], style=Styles.get_severity_color(issue["severity"])
        )
        content.append("\n")

    if issue.get("tags"):
        content.append("  Tags: ", style=Colors.SECONDARY)
        content.append(", ".join(issue["tags"]), style=Colors.WARNING)
        content.append("\n")

    content.append("  Created: ", style=Colors.SECONDARY)
    content.append(issue.get("created_at", "Unknown"), style=Colors.SUCCESS)

    # Display in a styled panel
    panel = Panel(content, title="Confirm Deletion", **PanelStyles.warning())
    console.print(panel)


def _display_deletion_success(issue: dict):
    """Display successful deletion message"""
    content = Text()

    content.append("Issue deleted successfully:\n", style=f"bold {Colors.SUCCESS}")
    content.append("  Title: ", style=Colors.SECONDARY)
    content.append(issue.get("title", "No title"), style=Colors.PRIMARY)
    content.append("\n")
    content.append("  ID: ", style=Colors.SECONDARY)
    content.append(issue["id"], style=Colors.IDENTIFIER)
    content.append(
        f"\n\n[{Colors.SUCCESS}]✓[/{Colors.SUCCESS}] [dim]Issue permanently removed[/dim]"
    )

    # Display in a styled panel
    panel = Panel(content, title="Deletion Complete", **PanelStyles.success())
    console.print(panel)
