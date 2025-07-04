#!/usr/bin/env python
"""
BugIt CLI Interactive Shell - Pure Wrapper Implementation
Interactive command-line interface for BugIt bug report management.
This is a pure wrapper that calls CLI commands internally with shell-friendly defaults.
"""

import sys
import shlex
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from cli import app
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from core.styles import Colors, Styles, PanelStyles

console = Console()


def show_welcome():
    """Display welcome message with dynamic command extraction"""
    welcome_text = Text()
    welcome_text.append("BugIt Interactive Shell\n", style=f"bold {Colors.BRAND}")
    welcome_text.append(
        "AI-powered bug report management CLI\n\n", style=Colors.SECONDARY
    )

    # Shell Commands (specific to interactive shell)
    welcome_text.append("Shell Commands:\n", style="bold")
    welcome_text.append(
        "  help                 - Show command help\n", style=Colors.INTERACTIVE
    )
    welcome_text.append(
        "  <command> --help     - Show help for specific command\n",
        style=Colors.INTERACTIVE,
    )
    welcome_text.append(
        "  exit                 - Exit BugIt shell\n", style=Colors.INTERACTIVE
    )

    # BugIt Commands - dynamically extracted from CLI
    welcome_text.append("\nBugIt Commands:\n", style="bold")

    try:
        # Get Typer's help output
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        if result.exit_code == 0 and result.output:
            # Parse and display commands
            commands = _parse_typer_help_for_commands(result.output)
            for cmd_name, help_text in commands:
                welcome_text.append(
                    f"  {cmd_name:<18} - {help_text}\n", style=Colors.INTERACTIVE
                )
        else:
            _add_fallback_commands(welcome_text)

    except Exception:
        _add_fallback_commands(welcome_text)

    welcome_text.append(
        f"\nShell Mode: Pretty output by default, use --json for JSON output\n",
        style=Colors.WARNING,
    )
    welcome_text.append(
        'Quote arguments with spaces: new "long bug description"\n',
        style=Colors.SECONDARY,
    )

    console.print(Panel(welcome_text, title="Welcome", **PanelStyles.standard()))


def _parse_typer_help_for_commands(help_output: str) -> list[tuple[str, str]]:
    """Parse Typer's help output to extract command names and descriptions"""
    commands = []
    lines = help_output.split("\n")

    in_commands_section = False

    for line in lines:
        if "─ Commands ─" in line or "Commands:" in line:
            in_commands_section = True
            continue

        if in_commands_section and ("─" in line and "Commands" not in line):
            break

        if in_commands_section and line.strip() and "│" in line:
            content = line.replace("│", "").strip()

            if not content or "─" in content:
                continue

            parts = content.split()
            if len(parts) >= 2:
                cmd_name = parts[0]
                description_start = content.find(cmd_name) + len(cmd_name)
                help_text = content[description_start:].strip()

                if cmd_name and help_text and not cmd_name.startswith("-"):
                    commands.append((cmd_name, help_text))

    return sorted(commands)


def _add_fallback_commands(welcome_text: Text):
    """Fallback command list if dynamic extraction fails"""
    fallback_commands = [
        ("config", "View or modify BugIt configuration"),
        ("delete", "Delete a bug report permanently"),
        ("edit", "Edit an existing bug report"),
        ("list", "List all bug reports with optional filtering"),
        ("new", "Create a new bug report from a freeform description"),
        ("show", "Show detailed information about a specific bug report"),
    ]

    for cmd_name, help_text in fallback_commands:
        welcome_text.append(
            f"  {cmd_name:<18} - {help_text}\n", style=Colors.INTERACTIVE
        )


def run_command(command_line: str):
    """Execute BugIt command as pure wrapper - calls CLI internally"""
    if not command_line.strip():
        return True

    command_line = command_line.strip()

    # Handle shell-specific commands
    if command_line.lower() in ["exit", "quit", "q"]:
        console.print(f"[bold {Colors.BRAND}]Goodbye![/bold {Colors.BRAND}]")
        return False

    if command_line.lower() in ["help", "?"]:
        show_welcome()
        return True

    try:
        # Parse command line
        args = shlex.split(command_line)
    except ValueError:
        console.print(
            f"[{Colors.ERROR}]Error:[/{Colors.ERROR}] Use quotes for arguments with spaces",
            style=Colors.ERROR,
        )
        return True

    if not args:
        return True

    try:
        # Shell Mode Logic - Pure Wrapper Pattern
        shell_args = args.copy()

        # Check for shell override flags
        json_mode = "--json" in shell_args
        if json_mode:
            # User wants JSON output in shell - remove --json flag
            shell_args = [arg for arg in shell_args if arg != "--json"]
            # Don't add --pretty (will get default JSON output)
        else:
            # Default shell behavior: pretty output
            # Add --pretty flag if not already present and not a help command
            if (
                "--pretty" not in shell_args
                and "--help" not in shell_args
                and "-h" not in shell_args
            ):
                shell_args.append("--pretty")

        # Execute CLI command directly by setting sys.argv
        original_argv = sys.argv.copy()

        try:
            # Set sys.argv to invoke the CLI
            sys.argv = ["bugit"] + shell_args

            # Execute the actual CLI app
            app()

        except SystemExit as e:
            # Handle command completion
            if e.code != 0:
                console.print(
                    f"[{Colors.ERROR}]Command failed with exit code: {e.code}[/{Colors.ERROR}]"
                )
        finally:
            # Restore original sys.argv
            sys.argv = original_argv

    except Exception as e:
        console.print(
            f"[{Colors.ERROR}]Error executing command: {str(e)}[/{Colors.ERROR}]"
        )
        console.print(
            f"[{Colors.SECONDARY}]Type 'help' for available commands[/{Colors.SECONDARY}]"
        )

    return True


def main():
    """Main interactive shell loop"""
    show_welcome()

    try:
        while True:
            try:
                # Styled prompt
                console.print(
                    f"\n[bold {Colors.BRAND}]BugIt>[/bold {Colors.BRAND}] ", end=""
                )
                command = input()

                # Process command
                if not run_command(command):
                    break

            except KeyboardInterrupt:
                console.print(
                    f"\n\n[bold {Colors.BRAND}]Goodbye! (Ctrl+C to exit)[/bold {Colors.BRAND}]"
                )
                break
            except EOFError:
                console.print(
                    f"\n\n[bold {Colors.BRAND}]Goodbye![/bold {Colors.BRAND}]"
                )
                break

    except Exception as e:
        console.print(f"[{Colors.ERROR}]Unexpected error: {str(e)}[/{Colors.ERROR}]")
        sys.exit(1)


if __name__ == "__main__":
    main()
