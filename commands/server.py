"""
Server command for starting the MCP server.
Provides a way to run the BugIt MCP server through the CLI.
"""

import typer

from mcp_local.fastmcp_server import mcp


def server(
    debug: bool = typer.Option(
        False, "--debug", help="Enable debug logging for the MCP server"
    ),
):
    """
    Start the BugIt MCP server.

    The MCP server exposes BugIt's functionality through the Model Context Protocol,
    allowing AI models and other clients to use BugIt as a tool.

    The server communicates via JSON-RPC 2.0 over stdio and will run until
    interrupted with Ctrl+C.

    Args:
        debug: Enable debug logging to stderr
    """
    try:
        if not debug:
            # Output startup message to stderr for user feedback
            typer.echo("Starting BugIt MCP server...", err=True)
            typer.echo(
                "Server will communicate via stdin/stdout using JSON-RPC 2.0", err=True
            )
            typer.echo("Press Ctrl+C to stop the server", err=True)

        # Run the FastMCP server
        mcp.run()

    except KeyboardInterrupt:
        if not debug:
            typer.echo("\nMCP server stopped by user", err=True)
        raise typer.Exit(0)
    except Exception as e:
        typer.echo(f"Error starting MCP server: {e}", err=True)
        raise typer.Exit(1)
 