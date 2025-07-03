#!/usr/bin/env python3
"""
BugIt CLI - AI-powered bug report management tool.

This is the main entry point for the BugIt CLI application.
Provides commands for creating, listing, showing, editing, and deleting bug reports.
"""

import typer
from typing import Optional
from commands import new, list, show, delete, edit
from commands import config as config_cmd

def help_callback(value: bool):
    """Show help message."""
    if value:
        print("AI-powered bug report management CLI")
        print("\nUsage: cli.py [OPTIONS] COMMAND [ARGS]...")
        print("\nCommands:")
        print("  new      Create a new bug report from a freeform description")
        print("  list     List all bug reports with optional filtering")
        print("  show     Show detailed information about a specific bug report")
        print("  edit     Edit an existing bug report")
        print("  delete   Delete a bug report permanently")
        print("  config   View or modify BugIt configuration")
        print("\nOptions:")
        print("  -h, --help    Show help message")
        raise typer.Exit()

app = typer.Typer(
    name="bugit",
    help="AI-powered bug report management CLI", 
    add_completion=False,
    context_settings={
        "help_option_names": ["-h", "--help"],
        "max_content_width": 120,
        # Note: The "and exit" text is built into Click/Typer and cannot be easily customized
        # This is a known limitation of the Typer framework
    }
)

# Add custom help option
@app.callback()
def main(
    help: Optional[bool] = typer.Option(None, "-h", "--help", callback=help_callback, is_eager=True, help="Show help message")
):
    """AI-powered bug report management CLI"""
    pass

# Register commands
app.command("new")(new.new)
app.command("list")(list.list_issues)
app.command("show")(show.show)
app.command("delete")(delete.delete)
app.command("edit")(edit.edit)
app.command("config")(config_cmd.config)

if __name__ == "__main__":
    app() 