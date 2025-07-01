"""
Edit command for modifying bug reports.
Supports field-specific updates and validation.
"""

import typer
from typing import Optional
from core import storage, schema


def edit(
    id_or_index: str,
    title: Optional[str] = typer.Option(None, "--title", help="Update title"),
    severity: Optional[str] = typer.Option(None, "--severity", help="Update severity"),
    add_tag: Optional[str] = typer.Option(None, "--add-tag", help="Add a tag"),
    remove_tag: Optional[str] = typer.Option(None, "--remove-tag", help="Remove a tag")
):
    """
    Edit an existing bug report.
    
    Args:
        id_or_index: Either the UUID or index (from list command) of the issue
        title: New title for the issue
        severity: New severity level
        add_tag: Tag to add to the issue
        remove_tag: Tag to remove from the issue
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
                typer.echo(f"Invalid index: {id_or_index}. Use 'bugit list' to see available issues.", err=True)
                raise typer.Exit(1)
        else:
            # UUID-based selection
            issue = storage.load_issue(id_or_index)
        
        # Track changes
        changes_made = False
        
        # Update fields
        if title:
            issue['title'] = title
            changes_made = True
            typer.echo(f"Updated title: {title}")
            
        if severity:
            if severity.lower() in ['low', 'medium', 'high', 'critical']:
                issue['severity'] = severity.lower()
                changes_made = True
                typer.echo(f"Updated severity: {severity.lower()}")
            else:
                typer.echo(f"Invalid severity: {severity}. Must be low, medium, high, or critical.", err=True)
                raise typer.Exit(1)
        
        # Handle tags
        tags = issue.get('tags', [])
        
        if add_tag:
            if add_tag not in tags:
                tags.append(add_tag)
                issue['tags'] = tags
                changes_made = True
                typer.echo(f"Added tag: {add_tag}")
            else:
                typer.echo(f"Tag '{add_tag}' already exists.")
                
        if remove_tag:
            if remove_tag in tags:
                tags.remove(remove_tag)
                issue['tags'] = tags
                changes_made = True
                typer.echo(f"Removed tag: {remove_tag}")
            else:
                typer.echo(f"Tag '{remove_tag}' not found.")
        
        if not changes_made:
            typer.echo("No changes specified. Use --help to see available options.")
            return
        
        # Validate and save
        validated = schema.validate_or_default(issue)
        storage.save_issue(validated)
        
        typer.echo(f"Issue {issue['id']} updated successfully.")
        
    except Exception as e:
        typer.echo(f"Error editing issue: {e}", err=True)
        raise typer.Exit(1) 