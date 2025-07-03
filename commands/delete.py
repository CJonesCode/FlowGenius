"""
Delete command for removing bug reports.
Supports both UUID and index-based selection with confirmation.
"""

import typer
import json
from core import storage


def delete(
    id_or_index: str,
    force: bool = typer.Option(False, "-f", "--force", help="Skip confirmation prompt"),
    pretty_output: bool = typer.Option(False, "-p", "--pretty", help="Output in human-readable format")
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
        
        issue_id = issue['id']
        
        # Show what will be deleted and handle confirmation
        if pretty_output:
            typer.echo(f"Issue to delete: {issue['title']}")
            
            # Confirm deletion unless --force is used
            if not force:
                confirm = typer.confirm("Are you sure you want to delete this issue?")
                if not confirm:
                    typer.echo("Deletion cancelled.")
                    return
        else:
            # In JSON mode, --force is required for safety
            if not force:
                output = {
                    "success": False,
                    "error": "Confirmation required. Use --force to delete without confirmation in JSON mode.",
                    "issue_to_delete": {
                        "id": issue_id,
                        "title": issue['title']
                    }
                }
                typer.echo(json.dumps(output, indent=2))
                return
        
        # Delete the issue (new storage function raises exception on failure)
        storage.delete_issue(issue_id)
        
        if pretty_output:
            typer.echo(f"Issue {issue_id} deleted successfully.")
        else:
            output = {
                "success": True,
                "id": issue_id,
                "title": issue['title']
            }
            typer.echo(json.dumps(output, indent=2))
            
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