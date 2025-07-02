"""
Delete command for removing bug reports.
Supports both UUID and index-based selection with confirmation.
"""

import typer
import json
from core import storage


def delete(
    id_or_index: str,
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompt"),
    pretty_output: bool = typer.Option(False, "--pretty", help="Output in human-readable format")
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
        # Get the issue to delete
        if id_or_index.isdigit():
            # Index-based selection
            issues = storage.list_issues()
            index = int(id_or_index) - 1  # Convert to 0-based
            
            if 0 <= index < len(issues):
                issue = issues[index]
                issue_id = issue['id']
            else:
                error_msg = f"Invalid index: {id_or_index}. Use 'bugit list' to see available issues."
                if pretty_output:
                    typer.echo(error_msg, err=True)
                else:
                    output = {
                        "success": False,
                        "error": error_msg
                    }
                    typer.echo(json.dumps(output, indent=2))
                raise typer.Exit(1)
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
        
        # Delete the issue
        success = storage.delete_issue(issue_id)
        
        if pretty_output:
            if success:
                typer.echo(f"Issue {issue_id} deleted successfully.")
            else:
                typer.echo(f"Failed to delete issue {issue_id}.", err=True)
                raise typer.Exit(1)
        else:
            output = {
                "success": success,
                "id": issue_id,
                "title": issue['title']
            }
            if not success:
                output["error"] = "Failed to delete issue"
            typer.echo(json.dumps(output, indent=2))
            
            if not success:
                raise typer.Exit(1)
            
    except typer.Exit:
        # Re-raise typer.Exit to preserve exit codes
        raise
    except Exception as e:
        error_msg = f"Error deleting issue: {e}"
        if pretty_output:
            typer.echo(error_msg, err=True)
        else:
            output = {
                "success": False,
                "error": error_msg
            }
            typer.echo(json.dumps(output, indent=2))
        raise typer.Exit(1) 