"""
New command for creating bug reports.
Processes freeform descriptions using LangGraph and saves structured issues.
"""

import typer
from core import model, storage, schema
from core.console import output_json, output_message, output_error, output_success
from core.errors import BugItError, APIError, StorageError, ExitCode
from core.styles import Styles, Colors, PanelStyles
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


def new(
    description: str,
    pretty_output: bool = typer.Option(
        False, "-p", "--pretty", help="Output in human-readable format"
    ),
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
        # Progress message to stderr
        if pretty_output:
            output_message("Processing with AI...", "dim")

        # Process description with LangGraph
        result = model.process_description(description)

        # Validate and apply defaults
        validated = schema.validate_or_default(result)

        # Save to storage
        uuid = storage.save_issue(validated)

        # Success feedback to stderr for pretty mode
        if pretty_output:
            output_message("Issue created successfully", "green")

        # Output the actual data
        if pretty_output:
            # Pretty output using same Panel style as show command
            console = Console()

            # Create title with ID similar to show command
            title_text = Text()
            title_text.append(validated.get("title", "No title"), style=Colors.PRIMARY)
            title_text.append(" (ID: ", style=Colors.SECONDARY)
            title_text.append(validated.get("id", "N/A"), style=Colors.IDENTIFIER)
            title_text.append(")", style=Colors.SECONDARY)

            content = Text()

            # Severity with dynamic coloring
            content.append("Severity: ", style=Colors.SECONDARY)
            severity_value = validated.get("severity", "N/A")
            content.append(
                severity_value, style=Styles.get_severity_color(severity_value)
            )
            content.append("\n")

            # Type
            content.append("Type: ", style=Colors.SECONDARY)
            content.append(validated.get("type", "N/A"), style=Colors.PRIMARY)
            content.append("\n")

            # Status
            content.append("Status: ", style=Colors.SECONDARY)
            content.append(validated.get("status", "N/A"), style=Colors.PRIMARY)
            content.append("\n")

            # Tags
            content.append("Tags: ", style=Colors.SECONDARY)
            tags = validated.get("tags", [])
            if tags:
                content.append(", ".join(tags), style=Colors.WARNING)
            else:
                content.append("(none)", style=Colors.SECONDARY)
            content.append("\n")

            # Solution (if any)
            solution = validated.get("solution", "")
            if solution:
                content.append("Solution: ", style=Colors.SECONDARY)
                content.append(solution, style=Colors.SUCCESS)
                content.append("\n")

            # Created date
            content.append("Created: ", style=Colors.SECONDARY)
            content.append(validated.get("created_at", "N/A"), style=Colors.SUCCESS)
            content.append("\n")

            # Updated date (if different from created)
            updated_at = validated.get("updated_at", "")
            created_at = validated.get("created_at", "")
            if updated_at and updated_at != created_at:
                content.append("Updated: ", style=Colors.SECONDARY)
                content.append(updated_at, style=Colors.SUCCESS)
                content.append("\n")

            # Schema version (for debugging/technical info)
            content.append("Schema: ", style=Colors.SECONDARY)
            content.append(
                validated.get("schema_version", "N/A"), style=Colors.SECONDARY
            )
            content.append("\n\n")

            # Description
            content.append("Description:\n", style=Colors.SECONDARY)
            content.append(
                validated.get("description", "No description"), style=Colors.PRIMARY
            )

            panel = Panel(content, title=title_text, **PanelStyles.standard())
            console.print(panel)
        else:
            # JSON output to stdout (clean, no colors)
            output_data = {"success": True, "issue": validated}
            output_json(output_data)

    except Exception as e:
        # Handle errors with proper exit codes
        if isinstance(e, BugItError):
            output_error(e, pretty_output)
            raise typer.Exit(e.exit_code)
        else:
            # Convert to appropriate BugIt error
            if "API" in str(e) or "openai" in str(e).lower():
                api_error = APIError(f"AI processing failed: {str(e)}")
                output_error(api_error, pretty_output)
                raise typer.Exit(api_error.exit_code)
            elif "storage" in str(e).lower() or "file" in str(e).lower():
                storage_error = StorageError(f"Storage operation failed: {str(e)}")
                output_error(storage_error, pretty_output)
                raise typer.Exit(storage_error.exit_code)
            else:
                generic_error = BugItError(f"Error creating issue: {str(e)}")
                output_error(generic_error, pretty_output)
                raise typer.Exit(generic_error.exit_code)
