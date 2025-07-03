"""
New command for creating bug reports.
Processes freeform descriptions using LangGraph and saves structured issues.
"""

import typer
import json
from core import model, storage, schema
from core.styles import Styles, Colors
from rich.console import Console


def new(
    description: str,
    pretty_output: bool = typer.Option(False, "-p", "--pretty", help="Output in human-readable format")
):
    """
    Create a new bug report from a freeform description.
    
    Args:
        description: Freeform text description of the bug
        pretty_output: Show human-readable output instead of JSON
    
    Default output is JSON for easy scripting and automation.
    Use --pretty for human-readable output with clean formatting.
    """
    try:
        # Process description with LangGraph (stub)
        result = model.process_description(description)
        
        # Validate and apply defaults
        validated = schema.validate_or_default(result)
        
        # Save to storage
        uuid = storage.save_issue(validated)
        
        if pretty_output:
            # Display comprehensive AI-generated results (human-readable) with styling
            console = Console()
            
            console.print("Issue created: ", style=Colors.SECONDARY, end="")
            console.print(uuid, style=Colors.IDENTIFIER)
            
            console.print("Title: ", style=Colors.SECONDARY, end="")
            console.print(validated['title'], style=Colors.PRIMARY)
            
            console.print("Severity: ", style=Colors.SECONDARY, end="")
            console.print(validated['severity'], style=Styles.get_severity_color(validated['severity']))
            
            console.print("Type: ", style=Colors.SECONDARY, end="")
            console.print(validated['type'], style=Colors.PRIMARY)
            
            console.print("Tags: ", style=Colors.SECONDARY, end="")
            if validated.get('tags'):
                tags_str = ", ".join(validated['tags'])
                console.print(tags_str, style=Colors.WARNING)
            else:
                console.print("(none)", style=Colors.SECONDARY)
            
            console.print("Created: ", style=Colors.SECONDARY, end="")
            console.print(validated['created_at'], style=Colors.SUCCESS)
            
            console.print("Saved to: ", style=Colors.SECONDARY, end="")
            console.print(f".bugit/issues/{uuid}.json", style=Colors.SECONDARY)
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
            console = Console()
            console.print(Styles.error(error_msg))
        else:
            output = {
                "success": False,
                "error": error_msg
            }
            typer.echo(json.dumps(output, indent=2))
        raise typer.Exit(1) 