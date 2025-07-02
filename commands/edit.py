"""
Edit command for modifying bug reports.
Supports field-specific updates and validation.
"""

import typer
import json
from typing import Optional
from core import storage, schema


def edit(
    id_or_index: str,
    title: Optional[str] = typer.Option(None, "--title", help="Update title"),
    severity: Optional[str] = typer.Option(None, "--severity", help="Update severity"),
    add_tag: Optional[str] = typer.Option(None, "--add-tag", help="Add a tag"),
    remove_tag: Optional[str] = typer.Option(None, "--remove-tag", help="Remove a tag"),
    pretty_output: bool = typer.Option(False, "--pretty", help="Output in human-readable format")
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
        # Get the issue to edit
        if id_or_index.isdigit():
            # Index-based selection
            issues = storage.list_issues()
            index = int(id_or_index) - 1  # Convert to 0-based
            
            if 0 <= index < len(issues):
                issue = issues[index]
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
        
        # Track changes
        changes_made = False
        changes_log = []
        
        # Update fields
        if title:
            issue['title'] = title
            changes_made = True
            changes_log.append(f"Updated title: {title}")
            
        if severity:
            if severity.lower() in ['low', 'medium', 'high', 'critical']:
                issue['severity'] = severity.lower()
                changes_made = True
                changes_log.append(f"Updated severity: {severity.lower()}")
            else:
                error_msg = f"Invalid severity: {severity}. Must be low, medium, high, or critical."
                if pretty_output:
                    typer.echo(error_msg, err=True)
                else:
                    output = {
                        "success": False,
                        "error": error_msg
                    }
                    typer.echo(json.dumps(output, indent=2))
                raise typer.Exit(1)
        
        # Handle tags
        tags = issue.get('tags', [])
        
        if add_tag:
            if add_tag not in tags:
                tags.append(add_tag)
                issue['tags'] = tags
                changes_made = True
                changes_log.append(f"Added tag: {add_tag}")
            else:
                changes_log.append(f"Tag '{add_tag}' already exists.")
                
        if remove_tag:
            if remove_tag in tags:
                tags.remove(remove_tag)
                issue['tags'] = tags
                changes_made = True
                changes_log.append(f"Removed tag: {remove_tag}")
            else:
                changes_log.append(f"Tag '{remove_tag}' not found.")
        
        if not changes_made:
            message = "No changes specified. Use --help to see available options."
            if pretty_output:
                typer.echo(message)
            else:
                output = {
                    "success": False,
                    "message": message,
                    "changes": changes_log
                }
                typer.echo(json.dumps(output, indent=2))
            return
        
        # Validate and save
        validated = schema.validate_or_default(issue)
        storage.save_issue(validated)
        
        if pretty_output:
            # Human-readable output
            for change in changes_log:
                typer.echo(change)
            typer.echo(f"Issue {issue['id']} updated successfully.")
        else:
            # JSON output
            output = {
                "success": True,
                "id": issue['id'],
                "changes": changes_log,
                "updated_issue": validated
            }
            typer.echo(json.dumps(output, indent=2))
        
    except typer.Exit:
        # Re-raise typer.Exit to preserve exit codes
        raise
    except Exception as e:
        error_msg = f"Error editing issue: {e}"
        if pretty_output:
            typer.echo(error_msg, err=True)
        else:
            output = {
                "success": False,
                "error": error_msg
            }
            typer.echo(json.dumps(output, indent=2))
        raise typer.Exit(1) 