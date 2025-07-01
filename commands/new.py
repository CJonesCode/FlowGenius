"""
New command for creating bug reports.
Processes freeform descriptions using LangGraph and saves structured issues.
"""

import typer
from core import model, storage, schema


def new(description: str):
    """
    Create a new bug report from a freeform description.
    
    Args:
        description: Freeform text description of the bug
    """
    try:
        # Process description with LangGraph (stub)
        result = model.process_description(description)
        
        # Validate and apply defaults
        validated = schema.validate_or_default(result)
        
        # Save to storage
        uuid = storage.save_issue(validated)
        
        typer.echo(f"Issue created: {uuid}")
        typer.echo(f"Title: {validated['title']}")
        typer.echo(f"Severity: {validated['severity']}")
        
    except Exception as e:
        typer.echo(f"Error creating issue: {e}", err=True)
        raise typer.Exit(1) 