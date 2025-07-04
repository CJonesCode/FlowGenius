"""
Error classes for MCP tool operations.

This module defines custom exceptions for MCP tool execution
and error conversion utilities.
"""

from typing import Any, Dict, Optional

from core.errors import BugItError, ExitCode


class MCPError(BugItError):
    """Base class for all MCP-related errors"""

    def __init__(
        self,
        message: str,
        code: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
        exit_code: ExitCode = ExitCode.GENERAL_ERROR,
    ):
        super().__init__(message, exit_code=exit_code)
        self.code = code or -32000
        self.data = data or {}

    def to_jsonrpc_error(self) -> Dict[str, Any]:
        """Convert to JSON-RPC error format"""
        return {"code": self.code, "message": str(self), "data": self.data}


class MCPToolError(MCPError):
    """Error during tool execution"""

    def __init__(self, tool_name: str, message: str, data: Optional[Dict[str, Any]] = None):
        super().__init__(f"Tool '{tool_name}' failed: {message}", -32001, data)
        self.tool_name = tool_name


class MCPToolNotFoundError(MCPError):
    """Tool not found in registry"""

    def __init__(self, tool_name: str):
        super().__init__(f"Tool '{tool_name}' not found", -32002)
        self.tool_name = tool_name


def convert_bugit_error_to_mcp(error: BugItError) -> MCPError:
    """
    Convert BugIt domain errors to MCP errors.

    Args:
        error: The BugIt error to convert

    Returns:
        Corresponding MCP error
    """
    # Import here to avoid circular imports
    from core.errors import APIError, StorageError, ValidationError

    if isinstance(error, ValidationError):
        return MCPToolError(
            "validation", str(error), {"original_error": error.__class__.__name__}
        )

    if isinstance(error, (StorageError, APIError)):
        return MCPToolError(
            "storage", str(error), {"original_error": error.__class__.__name__}
        )

    # Generic conversion for other BugIt errors
    return MCPToolError("unknown", str(error), {"original_error": error.__class__.__name__})
