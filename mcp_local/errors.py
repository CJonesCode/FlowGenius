"""
MCP-specific error classes for the BugIt MCP server.

This module defines error classes specific to MCP operations,
building on the existing BugIt error hierarchy.
"""

from typing import Any, Dict, Optional

from core.errors import BugItError, ExitCode

from .types import JSONRPCErrorCode


class MCPError(BugItError):
    """Base class for MCP-specific errors"""

    def __init__(
        self, message: str, code: Optional[int] = None, data: Optional[Any] = None
    ):
        super().__init__(message, exit_code=ExitCode.GENERAL_ERROR)
        self.code = code or JSONRPCErrorCode.INTERNAL_ERROR
        self.data = data

    def to_jsonrpc_error(self) -> Dict[str, Any]:
        """Convert to JSON-RPC error format"""
        error_dict = {"code": self.code, "message": self.message}
        if self.data is not None:
            error_dict["data"] = self.data
        return error_dict


class MCPProtocolError(MCPError):
    """Raised when MCP protocol violations occur"""

    def __init__(self, message: str, data: Optional[Any] = None):
        super().__init__(message, JSONRPCErrorCode.INVALID_REQUEST, data)


class MCPMethodNotFoundError(MCPError):
    """Raised when an unknown MCP method is called"""

    def __init__(self, method: str):
        super().__init__(
            f"Method not found: {method}", JSONRPCErrorCode.METHOD_NOT_FOUND
        )
        self.method = method


class MCPInvalidParamsError(MCPError):
    """Raised when invalid parameters are provided to an MCP method"""

    def __init__(self, message: str, data: Optional[Any] = None):
        super().__init__(message, JSONRPCErrorCode.INVALID_PARAMS, data)


class MCPParseError(MCPError):
    """Raised when JSON parsing fails"""

    def __init__(self, message: str = "Parse error"):
        super().__init__(message, JSONRPCErrorCode.PARSE_ERROR)


class MCPToolError(MCPError):
    """Raised when tool execution fails"""

    def __init__(self, tool_name: str, message: str, data: Optional[Any] = None):
        super().__init__(
            f"Tool '{tool_name}' failed: {message}", JSONRPCErrorCode.SERVER_ERROR, data
        )
        self.tool_name = tool_name


class MCPToolNotFoundError(MCPError):
    """Raised when a requested tool doesn't exist"""

    def __init__(self, tool_name: str):
        super().__init__(
            f"Tool not found: {tool_name}", JSONRPCErrorCode.METHOD_NOT_FOUND
        )
        self.tool_name = tool_name


class MCPServerError(MCPError):
    """Raised for general server errors"""

    def __init__(self, message: str, data: Optional[Any] = None):
        super().__init__(message, JSONRPCErrorCode.SERVER_ERROR, data)


class MCPInitializationError(MCPError):
    """Raised when server initialization fails"""

    def __init__(self, message: str, data: Optional[Any] = None):
        super().__init__(
            f"Initialization failed: {message}", JSONRPCErrorCode.SERVER_ERROR, data
        )


class MCPShutdownError(MCPError):
    """Raised when server shutdown fails"""

    def __init__(self, message: str, data: Optional[Any] = None):
        super().__init__(
            f"Shutdown failed: {message}", JSONRPCErrorCode.SERVER_ERROR, data
        )


class MCPFeatureNotEnabledError(MCPError):
    """Raised when a feature flag is disabled"""

    def __init__(self, feature_name: str):
        super().__init__(
            f"Feature '{feature_name}' is not enabled",
            JSONRPCErrorCode.METHOD_NOT_FOUND,
        )
        self.feature_name = feature_name


def convert_bugit_error_to_mcp(error: BugItError) -> MCPError:
    """
    Convert a BugIt error to an appropriate MCP error.

    Args:
        error: The original BugIt error

    Returns:
        An appropriate MCP error instance
    """
    # Import here to avoid circular imports
    from core.errors import APIError, StorageError, ValidationError

    if isinstance(error, APIError):
        return MCPToolError(
            "ai_processing", str(error), {"original_error": error.__class__.__name__}
        )
    elif isinstance(error, StorageError):
        return MCPToolError(
            "storage", str(error), {"original_error": error.__class__.__name__}
        )
    elif isinstance(error, ValidationError):
        return MCPInvalidParamsError(
            str(error), {"original_error": error.__class__.__name__}
        )
    else:
        return MCPServerError(str(error), {"original_error": error.__class__.__name__})
