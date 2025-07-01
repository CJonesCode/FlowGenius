#!/usr/bin/env python3
"""
BugIt CLI - AI-powered bug report management tool.

This is the main entry point for the BugIt CLI application.
Provides commands for creating, listing, showing, editing, and deleting bug reports.
"""

import typer
from commands import new, list, show, delete, edit
from commands import config as config_cmd

app = typer.Typer(
    name="bugit",
    help="AI-powered bug report management CLI",
    add_completion=False
)

# Register commands
app.command("new")(new.new)
app.command("list")(list.list_issues)
app.command("show")(show.show)
app.command("delete")(delete.delete)
app.command("edit")(edit.edit)
app.command("config")(config_cmd.config)

if __name__ == "__main__":
    app() 