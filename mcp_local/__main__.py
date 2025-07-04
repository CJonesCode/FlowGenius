#!/usr/bin/env python3
"""
MCP server entry point for BugIt.

This module provides the main entry point for running the BugIt MCP server
using the official FastMCP SDK.
"""

import sys
from .fastmcp_server import mcp

if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run()
