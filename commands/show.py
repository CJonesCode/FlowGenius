"""
Show command for displaying individual bug reports.
Supports both UUID and index-based selection.
"""

import typer
import json
from core import storage
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax


def show(
    id_or_index: str,
    pretty_output: bool = typer.Option(False, "--pretty", help="Output in human-readable format")
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
            # Human-readable output with Rich formatting
            console = Console()
            
            # Create a nice panel with issue details
            title = f"{issue.get('title', 'No title')} (ID: {issue.get('id', 'N/A')})"
            
            content_lines = []
            content_lines.append(f"**Severity:** {issue.get('severity', 'N/A')}")
            content_lines.append(f"**Type:** {issue.get('type', 'N/A')}")
            
            tags = issue.get('tags', [])
            if tags:
                content_lines.append(f"**Tags:** {', '.join(tags)}")
            else:
                content_lines.append("**Tags:** (none)")
                
            content_lines.append(f"**Created:** {issue.get('created_at', 'N/A')}")
            content_lines.append("")
            content_lines.append("**Description:**")
            content_lines.append(issue.get('description', 'No description'))
            
            panel = Panel(
                "\n".join(content_lines),
                title=title,
                border_style="blue",
                padding=(1, 2)
            )
            console.print(panel)
        else:
            # JSON output (default)
            typer.echo(json.dumps(issue, indent=2))
        
    except storage.StorageError as e:
        # Handle storage-specific errors
        error_msg = str(e)
        if pretty_output:
            typer.echo(f"Error: {error_msg}", err=True)
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
            typer.echo(error_msg, err=True)
        else:
            output = {
                "success": False,
                "error": error_msg
            }
            typer.echo(json.dumps(output, indent=2))
        raise typer.Exit(1) 