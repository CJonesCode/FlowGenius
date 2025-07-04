#!/usr/bin/env python
"""
BugIt CLI - Main Entry Point
AI-powered bug report management tool.

This is the main entry point for the BugIt application.
- With no arguments: starts the interactive shell
- With arguments: executes CLI commands
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Main entry point - routes to shell or CLI based on arguments"""

    # Check if we have command line arguments (excluding script name)
    if len(sys.argv) > 1:
        # We have arguments - execute CLI command
        from cli import app

        app()
    else:
        # No arguments - start interactive shell
        from shell import main as shell_main

        shell_main()


if __name__ == "__main__":
    main()
