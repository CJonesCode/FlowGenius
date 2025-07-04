"""
Console utilities for BugIt CLI with proper stream separation and color isolation.
Implements the scriptability-first approach with stdout for data and stderr for messages.
"""

import sys
import os
import json
from typing import Any, Dict, Optional
from rich.console import Console
from .errors import BugItError, format_error


def should_use_colors() -> bool:
    """Determine if colors should be used based on environment and settings"""
    # Check NO_COLOR environment variable
    if os.getenv("NO_COLOR"):
        return False

    # Check --no-color flag (from app state if available)
    try:
        import cli

        if hasattr(cli, "app_state") and getattr(cli.app_state, "no_color", False):
            return False
    except ImportError:
        pass

    # Check if stderr is a TTY (for messages)
    return sys.stderr.isatty()


def get_consoles():
    """Get properly configured consoles for different purposes"""
    use_colors = should_use_colors()

    # stdout console: NEVER use colors for data output
    stdout_console = Console(
        file=sys.stdout,
        force_terminal=False,  # Never force colors
        no_color=True,  # Explicitly disable colors for data
        stderr=False,
    )

    # stderr console: Colors OK for messages if appropriate
    stderr_console = Console(file=sys.stderr, no_color=not use_colors, stderr=True)

    return stdout_console, stderr_console


def output_json(data: Dict[str, Any]) -> None:
    """Output JSON data to stdout with no colors"""
    # Use plain print to ensure no Rich formatting
    print(json.dumps(data, indent=2))


def output_message(message: str, style: Optional[str] = None) -> None:
    """Output a message to stderr with optional styling"""
    _, stderr_console = get_consoles()
    if style:
        stderr_console.print(message, style=style)
    else:
        stderr_console.print(message)


def output_error(error: Exception, pretty: bool = False) -> None:
    """Output error information to stderr"""
    _, stderr_console = get_consoles()

    if isinstance(error, BugItError):
        if pretty:
            # Pretty error output to stderr
            stderr_console.print(f"❌ Error: {error.message}", style="red")
            if error.suggestion:
                stderr_console.print(
                    f"💡 Suggestion: {error.suggestion}", style="yellow"
                )
            if error.url:
                stderr_console.print(f"🔗 Help: {error.url}", style="dim")
        else:
            # JSON error output to stdout for automation
            output_json(format_error(error))
    else:
        # Generic error handling
        if pretty:
            stderr_console.print(f"❌ Error: {str(error)}", style="red")
        else:
            output_json(
                {"success": False, "error": str(error), "code": "GENERAL_ERROR"}
            )


def output_success(data: Dict[str, Any], pretty: bool = False) -> None:
    """Output success response"""
    if pretty:
        # Pretty success messages go to stderr, data to stdout with colors
        _, stderr_console = get_consoles()
        stderr_console.print("✅ Success", style="green")

        # Use stdout console with colors for pretty data display
        stdout_console = Console(
            file=sys.stdout, no_color=not should_use_colors(), stderr=False
        )

        # Display the data in pretty format
        if "issue" in data:
            issue = data["issue"]
            stdout_console.print(
                f"Issue created: {issue.get('id', 'N/A')}", style="bold"
            )
            stdout_console.print(f"Title: {issue.get('title', 'N/A')}")
            stdout_console.print(
                f"Severity: {issue.get('severity', 'N/A')}",
                style=_get_severity_color(issue.get("severity", "medium")),
            )
            # ... more pretty formatting
    else:
        # JSON output to stdout (clean, no colors)
        output_json(data)


def _get_severity_color(severity: str) -> str:
    """Get color for severity level"""
    colors = {"critical": "red", "high": "yellow", "medium": "cyan", "low": "green"}
    return colors.get(severity, "white")
