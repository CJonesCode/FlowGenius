#!/usr/bin/env python
"""
BugIt CLI Interactive Shell
Interactive command-line interface for BugIt bug report management.
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
    """Display welcome message using Typer's help but with custom formatting"""
    welcome_text = Text()
    welcome_text.append("BugIt Interactive Shell\n", style=f"bold {Colors.BRAND}")
    welcome_text.append("AI-powered bug report management CLI\n\n", style=Colors.SECONDARY)
    
    # Shell Commands (these are specific to our interactive shell)
    welcome_text.append("Shell Commands:\n", style="bold")
    welcome_text.append("  help                 - Show command help\n", style=Colors.INTERACTIVE)
    welcome_text.append("  <command> --help     - Show help for specific command\n", style=Colors.INTERACTIVE)
    welcome_text.append("  exit                 - Exit BugIt shell\n", style=Colors.INTERACTIVE)
    
    # BugIt Commands - extracted from Typer's actual help
    welcome_text.append("\nBugIt Commands:\n", style="bold")
    
    try:
        # Get Typer's help output
        from typer.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(app, ['--help'])
        
        if result.exit_code == 0 and result.output:
            # Parse the help output to extract commands
            commands = _parse_typer_help_for_commands(result.output)
            
            # Format commands with our styling
            for cmd_name, help_text in commands:
                welcome_text.append(f"  {cmd_name:<18} - {help_text}\n", style=Colors.INTERACTIVE)
        else:
            # Fallback if help generation fails
            _add_fallback_commands(welcome_text)
            
    except Exception:
        # Fallback to manual list if anything goes wrong
        _add_fallback_commands(welcome_text)
    
    welcome_text.append(f"\nShell Mode: Pretty output by default, use -p or --pretty for JSON\n", style=Colors.WARNING)
    welcome_text.append("Quote arguments with spaces: new \"long bug description\"\n", style=Colors.SECONDARY)
    
    console.print(Panel(welcome_text, title="Welcome", **PanelStyles.standard()))

def _parse_typer_help_for_commands(help_output: str) -> list[tuple[str, str]]:
    """Parse Typer's help output to extract command names and descriptions"""
    commands = []
    lines = help_output.split('\n')
    
    # Look for the Commands section
    in_commands_section = False
    
    for line in lines:
        # Check if we're entering the Commands section
        if '─ Commands ─' in line or 'Commands:' in line:
            in_commands_section = True
            continue
            
        # Check if we're leaving the Commands section (next section starts)
        if in_commands_section and ('─' in line and 'Commands' not in line):
            break
            
        # Parse command lines in the Commands section
        if in_commands_section and line.strip():
            # Look for lines that start with │ and contain command info
            if '│' in line:
                # Remove the │ characters and strip
                content = line.replace('│', '').strip()
                
                # Skip empty lines and separator lines
                if not content or '─' in content:
                    continue
                    
                # Parse command format: "command_name    Description text"
                # Commands have multiple spaces between name and description
                parts = content.split()
                if len(parts) >= 2:
                    cmd_name = parts[0]
                    # Join the rest as description, handling multiple spaces
                    description_start = content.find(cmd_name) + len(cmd_name)
                    help_text = content[description_start:].strip()
                    
                    if cmd_name and help_text and not cmd_name.startswith('-'):
                        commands.append((cmd_name, help_text))
    
    # Sort commands alphabetically
    return sorted(commands)

def _add_fallback_commands(welcome_text: Text):
    """Fallback command list if dynamic extraction fails"""
    fallback_commands = [
        ("config", "View or modify BugIt configuration"),
        ("delete", "Delete a bug report permanently"),
        ("edit", "Edit an existing bug report"),
        ("list", "List all bug reports with optional filtering"),
        ("new", "Create a new bug report from a freeform description"),
        ("show", "Show detailed information about a specific bug report")
    ]
    
    for cmd_name, help_text in fallback_commands:
        welcome_text.append(f"  {cmd_name:<18} - {help_text}\n", style=Colors.INTERACTIVE)

def _print_shell_message(message: str, style: str = Colors.SECONDARY):
    """Print a shell message with consistent styling"""
    console.print(f"[{Colors.SECONDARY}]Shell:[/{Colors.SECONDARY}] {message}", style=style)

def run_command(command_line: str):
    """Execute a BugIt command with consistent styling"""
    if not command_line.strip():
        return True
        
    command_line = command_line.strip()
    
    # Handle special shell commands
    if command_line.lower() in ['exit', 'quit', 'q']:
        console.print(f"[bold {Colors.BRAND}]Goodbye![/bold {Colors.BRAND}]")
        return False
    
    if command_line.lower() in ['help', '?']:
        # Show our custom welcome screen instead of raw Typer help
        show_welcome()
        return True
    
    try:
        # Parse command line using shlex to properly handle quotes
        args = shlex.split(command_line)
    except ValueError:
        _print_shell_message("Use quotes for arguments with spaces: new \"bug description\"")
        return True
    
    # Skip empty commands
    if not args:
        return True
    
    try:
        # Modify arguments for shell mode:
        # - Default to pretty output (add --pretty)
        # - If -p or --pretty is used, remove it and don't add --pretty (gives JSON)
        modified_args = args.copy()
        
        # Check if user explicitly wants JSON output with -p or --pretty
        json_mode = '-p' in modified_args or '--pretty' in modified_args
        if json_mode:
            # Remove both -p and --pretty flags since they mean "show JSON" in shell mode
            modified_args = [arg for arg in modified_args if arg not in ['-p', '--pretty']]
        else:
            # Add --pretty flag for human-readable output (default in shell)
            # Only add if not already present and not a help command
            if '--pretty' not in modified_args and '--help' not in modified_args and '-h' not in modified_args:
                modified_args.append('--pretty')
        
        # Execute the command directly instead of using CliRunner to preserve Rich formatting
        import sys
        from io import StringIO
        
        # Save original sys.argv
        original_argv = sys.argv.copy()
        
        try:
            # Set sys.argv to our command arguments
            sys.argv = ['bugit'] + modified_args
            
            # Execute the command directly through the app
            app()
                
        except SystemExit as e:
            # Handle command completion - only show error messages for failures
            if e.code != 0:
                console.print(f"[{Colors.ERROR}]✗[/{Colors.ERROR}] [dim]Command failed (exit code: {e.code})[/dim]")
        finally:
            # Restore original sys.argv
            sys.argv = original_argv
            
    except Exception as e:
        console.print(Styles.error(f"Error executing command: {e}"))
        _print_shell_message("Type 'help' for available commands or '<command> --help' for specific command help")
    
    return True

def main():
    """Main interactive shell loop with consistent styling"""
    show_welcome()
    
    try:
        while True:
            try:
                # Get user input with styled prompt using our brand color
                console.print(f"\n[bold {Colors.BRAND}]BugIt>[/bold {Colors.BRAND}] ", end="")
                command = input()
                
                # Process the command
                if not run_command(command):
                    break
                    
            except KeyboardInterrupt:
                console.print(f"\n\n[bold {Colors.BRAND}]Goodbye! (Ctrl+C to exit)[/bold {Colors.BRAND}]")
                break
            except EOFError:
                console.print(f"\n\n[bold {Colors.BRAND}]Goodbye![/bold {Colors.BRAND}]") 
                break
                
    except Exception as e:
        console.print(Styles.error(f"Unexpected error: {str(e)}"))
        sys.exit(1)

if __name__ == "__main__":
    main() 