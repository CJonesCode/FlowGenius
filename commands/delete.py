"""
Delete command for removing bug reports.
Supports both UUID and index-based selection with confirmation.
"""

import typer
from core import storage


def delete(
    id_or_index: str,
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompt")
):
    """
    Delete a bug report permanently.
    
    Args:
        id_or_index: Either the UUID or index (from list command) of the issue
        force: Skip confirmation prompt
    """
    try:
        # Get the issue to delete
        if id_or_index.isdigit():
            # Index-based selection
            issues = storage.list_issues()
            index = int(id_or_index) - 1  # Convert to 0-based
            
            if 0 <= index < len(issues):
                issue = issues[index]
                issue_id = issue['id']
            else:
                typer.echo(f"Invalid index: {id_or_index}. Use 'bugit list' to see available issues.", err=True)
                raise typer.Exit(1)
        else:
            # UUID-based selection
            issue = storage.load_issue(id_or_index)
            issue_id = issue['id']
        
        # Show what will be deleted
        typer.echo(f"Issue to delete: {issue['title']}")
        
        # Confirm deletion unless --force is used
        if not force:
            confirm = typer.confirm("Are you sure you want to delete this issue?")
            if not confirm:
                typer.echo("Deletion cancelled.")
                return
        
        # Delete the issue
        success = storage.delete_issue(issue_id)
        
        if success:
            typer.echo(f"Issue {issue_id} deleted successfully.")
        else:
            typer.echo(f"Failed to delete issue {issue_id}.", err=True)
            raise typer.Exit(1)
            
    except Exception as e:
        typer.echo(f"Error deleting issue: {e}", err=True)
        raise typer.Exit(1) 