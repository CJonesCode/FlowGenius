"""
New command for creating bug reports.
Processes freeform descriptions using LangGraph and saves structured issues.
"""

import typer
import json
from core import model, storage, schema


def new(
    description: str,
    pretty_output: bool = typer.Option(False, "--pretty", help="Output in human-readable format")
):
    """
    Create a new bug report from a freeform description.
    
    Args:
        description: Freeform text description of the bug
        pretty_output: Show human-readable output instead of JSON
    
    Default output is JSON for easy scripting and automation.
    Use --pretty for human-readable output with emojis and formatting.
    """
    try:
        # Process description with LangGraph (stub)
        result = model.process_description(description)
        
        # Validate and apply defaults
        validated = schema.validate_or_default(result)
        
        # Save to storage
        uuid = storage.save_issue(validated)
        
        if pretty_output:
            # Display comprehensive AI-generated results (human-readable)
            typer.echo(f"Issue created: {uuid}")
            typer.echo(f"Title: {validated['title']}")
            typer.echo(f"Severity: {validated['severity']}")
            typer.echo(f"Type: {validated['type']}")
            
            if validated.get('tags'):
                tags_str = ", ".join(validated['tags'])
                typer.echo(f"Tags: {tags_str}")
            else:
                typer.echo("Tags: (none)")
            
            typer.echo(f"Created: {validated['created_at']}")
            typer.echo(f"Saved to: .bugit/issues/{uuid}.json")
        else:
            # Output JSON for scripting/automation (default)
            output = {
                "id": uuid,
                "success": True,
                "issue": validated
            }
            typer.echo(json.dumps(output, indent=2))
        
    except Exception as e:
        error_msg = f"Error creating issue: {e}"
        if pretty_output:
            typer.echo(error_msg, err=True)
        else:
            output = {
                "success": False,
                "error": error_msg
            }
            typer.echo(json.dumps(output, indent=2))
        raise typer.Exit(1) 