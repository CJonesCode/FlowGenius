"""
Show command for displaying individual bug reports.
Supports both UUID and index-based selection.
"""

import typer
import json
from core import storage


def show(id_or_index: str):
    """
    Show detailed information about a specific bug report.
    
    Args:
        id_or_index: Either the UUID or index (from list command) of the issue
    """
    try:
        # Try to get issue by ID first, then by index
        if id_or_index.isdigit():
            # Index-based selection
            issues = storage.list_issues()
            index = int(id_or_index) - 1  # Convert to 0-based
            
            if 0 <= index < len(issues):
                issue = issues[index]
            else:
                typer.echo(f"Invalid index: {id_or_index}. Use 'bugit list' to see available issues.", err=True)
                raise typer.Exit(1)
        else:
            # UUID-based selection
            issue = storage.load_issue(id_or_index)
        
        # Display issue details
        typer.echo(json.dumps(issue, indent=2))
        
    except Exception as e:
        typer.echo(f"Error showing issue: {e}", err=True)
        raise typer.Exit(1) 