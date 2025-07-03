"""
Show command for displaying individual bug reports.
Supports both UUID and index-based selection.
"""

import typer
import json
from core import storage
from core.styles import Styles, Colors, PanelStyles
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


def show(
    id_or_index: str,
    pretty_output: bool = typer.Option(False, "-p", "--pretty", help="Output in human-readable format")
):
    """
    Show detailed information about a specific bug report.
    
    Args:
        id_or_index: Either the UUID or index (from list command) of the issue
        pretty_output: Show human-readable output instead of JSON
    
    Default output is JSON for easy scripting and automation.
    Use --pretty for human-readable output with syntax highlighting.
    """
    try:
        # Handle both UUID and index using new storage functions
        if id_or_index.isdigit():
            # Index-based selection - use new storage function
            issue = storage.get_issue_by_index(int(id_or_index))
        else:
            # UUID-based selection
            issue = storage.load_issue(id_or_index)
        
        # Display issue details
        if pretty_output:
            # Human-readable output with Rich formatting and consistent styling
            console = Console()
            
            # Create a nice panel with issue details using centralized styles
            title_text = Text()
            title_text.append(issue.get('title', 'No title'), style=Colors.PRIMARY)
            title_text.append(" (ID: ", style=Colors.SECONDARY)
            title_text.append(issue.get('id', 'N/A'), style=Colors.IDENTIFIER)
            title_text.append(")", style=Colors.SECONDARY)
            
            content = Text()
            
            # Severity with dynamic coloring
            content.append("Severity: ", style=Colors.SECONDARY)
            severity_value = issue.get('severity', 'N/A')
            content.append(severity_value, style=Styles.get_severity_color(severity_value))
            content.append("\n")
            
            # Type
            content.append("Type: ", style=Colors.SECONDARY)
            content.append(issue.get('type', 'N/A'), style=Colors.PRIMARY)
            content.append("\n")
            
            # Tags
            content.append("Tags: ", style=Colors.SECONDARY)
            tags = issue.get('tags', [])
            if tags:
                content.append(', '.join(tags), style=Colors.WARNING)
            else:
                content.append("(none)", style=Colors.SECONDARY)
            content.append("\n")
            
            # Created date
            content.append("Created: ", style=Colors.SECONDARY)
            content.append(issue.get('created_at', 'N/A'), style=Colors.SUCCESS)
            content.append("\n\n")
            
            # Description
            content.append("Description:\n", style=Colors.SECONDARY)
            content.append(issue.get('description', 'No description'), style=Colors.PRIMARY)
            
            panel = Panel(
                content,
                title=title_text,
                **PanelStyles.standard()
            )
            console.print(panel)
        else:
            # JSON output (default)
            typer.echo(json.dumps(issue, indent=2))
        
    except storage.StorageError as e:
        # Handle storage-specific errors
        error_msg = str(e)
        if pretty_output:
            console = Console()
            console.print(Styles.error(f"Error: {error_msg}"))
        else:
            output = {
                "success": False,
                "error": error_msg
            }
            typer.echo(json.dumps(output, indent=2))
        raise typer.Exit(1)
    except typer.Exit:
        # Re-raise typer.Exit to preserve exit codes
        raise
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        if pretty_output:
            console = Console()
            console.print(Styles.error(error_msg))
        else:
            output = {
                "success": False,
                "error": error_msg
            }
            typer.echo(json.dumps(output, indent=2))
        raise typer.Exit(1) 