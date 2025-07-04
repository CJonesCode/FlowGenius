#!/usr/bin/env python3
"""
BugIt CLI - AI-powered bug report management tool.

This is the main entry point for the BugIt CLI application.
Provides commands for creating, listing, showing, editing, and deleting bug reports.
"""

import typer

from commands import config as config_cmd
from commands import delete, edit, list, new, server, show

# Version information
__version__ = "1.0.0"

# Create the main Typer app with proper configuration
app = typer.Typer(
    name="bugit",
    help="AI-powered bug report management CLI that processes freeform descriptions into structured bug reports.",
    add_completion=False,
    context_settings={
        "help_option_names": ["-h", "--help"],
        "max_content_width": 120,
    },
    rich_markup_mode="rich",  # Enable rich markup for better help formatting
)


# Global app state for flags
class AppState:
    def __init__(self):
        self.verbose = False
        self.quiet = False
        self.no_color = False


app_state = AppState()


def version_callback(value: bool):
    """Handle version flag"""
    if value:
        typer.echo(f"bugit {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=version_callback,
        help="Show version and exit",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress progress messages and non-essential output",
    ),
    no_color: bool = typer.Option(False, "--no-color", help="Disable colored output"),
):
    """
    AI-powered bug report management CLI.

    Processes freeform bug descriptions into structured JSON reports using AI.
    Default output is JSON (perfect for automation). Use --pretty for human-readable output.

    Examples:
        bugit new "login fails with timeout error"
        bugit list --severity critical
        bugit show 1 --pretty
    """
    # Set global flags for use in commands
    app_state.verbose = verbose
    app_state.quiet = quiet
    app_state.no_color = no_color

    # Validate flag combinations
    if verbose and quiet:
        typer.echo("Error: --verbose and --quiet cannot be used together", err=True)
        raise typer.Exit(2)


# Register commands with proper names and enhanced help
app.command("new", help="Create a new bug report from a freeform description")(new.new)

app.command("list", help="List all bug reports with optional filtering")(
    list.list_issues
)

app.command("show", help="Show detailed information about a specific bug report")(
    show.show
)

app.command("delete", help="Delete a bug report permanently")(delete.delete)

app.command("edit", help="Edit an existing bug report")(edit.edit)

app.command("config", help="View or modify BugIt configuration")(config_cmd.config)

app.command("server", help="Start the BugIt MCP server for AI model integration")(
    server.server
)

if __name__ == "__main__":
    app()
