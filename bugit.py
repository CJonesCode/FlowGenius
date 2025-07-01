#!/usr/bin/env python
"""
BugIt CLI Interactive Shell
Interactive command-line interface for BugIt bug report management.
"""

import sys
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
    welcome_text.append("🐛 BugIt Interactive Shell\n", style="bold blue")
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
    
    console.print(Panel(welcome_text, title="Welcome", border_style="blue"))

def run_command(command_line: str):
    """Execute a bugit command"""
    if not command_line.strip():
        return True
        
    command_line = command_line.strip()
    
    # Handle special shell commands
    if command_line.lower() in ['exit', 'quit', 'q']:
        console.print("👋 Goodbye!", style="bold blue")
        return False
    
    if command_line.lower() in ['help', '?']:
        show_welcome()
        return True
    
    # Parse command line into arguments
    args = command_line.split()
    
    try:
        # Create a new Typer app context and run the command
        from typer.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(app, args)
        
        if result.output:
            console.print(result.output, end='')
        
        if result.exit_code != 0:
            console.print(f"❌ Command failed with exit code {result.exit_code}", style="bold red")
            
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="bold red")
        console.print("💡 Type 'help' for available commands", style="dim")
    
    return True

def main():
    """Main interactive shell loop"""
    show_welcome()
    
    try:
        while True:
            try:
                # Get user input with prompt
                command = input("\n🐛 bugit> ")
                
                # Process the command
                if not run_command(command):
                    break
                    
            except KeyboardInterrupt:
                console.print("\n\n👋 Goodbye! (Ctrl+C to exit)", style="bold blue")
                break
            except EOFError:
                console.print("\n\n👋 Goodbye!", style="bold blue") 
                break
                
    except Exception as e:
        console.print(f"\n❌ Unexpected error: {str(e)}", style="bold red")
        sys.exit(1)

if __name__ == "__main__":
    main() 