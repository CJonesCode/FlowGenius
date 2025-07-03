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

console = Console()

def show_welcome():
    """Display welcome message and help"""
    welcome_text = Text()
    welcome_text.append("BugIt Interactive Shell\n", style="bold blue")
    welcome_text.append("AI-powered bug report management CLI\n\n", style="dim")
    welcome_text.append("Available commands:\n", style="bold")
    welcome_text.append("  new <description>     - Create a new bug report\n", style="cyan")
    welcome_text.append("  list [options]        - List bug reports\n", style="cyan")
    welcome_text.append("  show <id>            - Show bug report details\n", style="cyan")
    welcome_text.append("  edit <id> [options]   - Edit a bug report\n", style="cyan")
    welcome_text.append("  delete <id>          - Delete a bug report\n", style="cyan")
    welcome_text.append("  config [options]      - Manage configuration\n", style="cyan")
    welcome_text.append("  help                 - Show this help\n", style="cyan")
    welcome_text.append("  exit                 - Exit BugIt shell\n", style="cyan")
    welcome_text.append("\nShell Mode: Pretty output by default, use -p or --pretty for JSON\n", style="yellow")
    welcome_text.append("Quote arguments with spaces: new \"long bug description\"\n", style="dim")
    
    console.print(Panel(welcome_text, title="Welcome", border_style="blue"))

def run_command(command_line: str):
    """Execute a BugIt command"""
    if not command_line.strip():
        return True
        
    command_line = command_line.strip()
    
    # Handle special shell commands
    if command_line.lower() in ['exit', 'quit', 'q']:
        console.print("Goodbye!", style="bold blue")
        return False
    
    if command_line.lower() in ['help', '?']:
        show_welcome()
        return True
    
    try:
        # Parse command line using shlex to properly handle quotes
        args = shlex.split(command_line)
    except ValueError:
        console.print("Use quotes for arguments with spaces: new \"bug description\"", style="dim")
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
            # Only add if not already present
            if '--pretty' not in modified_args:
                modified_args.append('--pretty')
        
        # Create a new Typer app context and run the command
        from typer.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(app, modified_args)
        
        if result.output:
            console.print(result.output, end='')
            
    except Exception:
        console.print("Type 'help' for available commands", style="dim")
    
    return True

def main():
    """Main interactive shell loop"""
    show_welcome()
    
    try:
        while True:
            try:
                # Get user input with styled prompt
                console.print("\nBugIt> ", style="bold blue", end="")
                command = input()
                
                # Process the command
                if not run_command(command):
                    break
                    
            except KeyboardInterrupt:
                console.print("\n\nGoodbye! (Ctrl+C to exit)", style="bold blue")
                break
            except EOFError:
                console.print("\n\nGoodbye!", style="bold blue") 
                break
                
    except Exception as e:
        console.print(f"\nUnexpected error: {str(e)}", style="bold red")
        sys.exit(1)

if __name__ == "__main__":
    main() 