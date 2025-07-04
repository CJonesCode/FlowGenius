"""
Shared type aliases and interfaces for MCP server implementation.

This module defines the core types used throughout the MCP server,
including JSON-RPC protocol types and BugIt-specific data structures.
"""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union


# JSON-RPC 2.0 Types
class JSONRPCRequest(TypedDict):
    """JSON-RPC 2.0 request structure"""

    jsonrpc: Literal["2.0"]
    method: str
    params: Optional[Dict[str, Any]]
    id: Optional[Union[str, int]]


class JSONRPCResponse(TypedDict):
    """JSON-RPC 2.0 response structure"""

    jsonrpc: Literal["2.0"]
    id: Optional[Union[str, int]]
    result: Optional[Any]
    error: Optional[Dict[str, Any]]


class JSONRPCError(TypedDict):
    """JSON-RPC 2.0 error structure"""

    code: int
    message: str
    data: Optional[Any]


# MCP Protocol Types
class MCPInitializeParams(TypedDict):
    """MCP initialize request parameters"""

    protocolVersion: str
    capabilities: Dict[str, Any]
    clientInfo: Dict[str, Any]


class MCPInitializeResult(TypedDict):
    """MCP initialize response result"""

    protocolVersion: str
    capabilities: Dict[str, Any]
    serverInfo: Dict[str, Any]


class MCPTool(TypedDict):
    """MCP tool definition"""

    name: str
    description: str
    inputSchema: Dict[str, Any]  # JSON Schema


class MCPToolsListResult(TypedDict):
    """MCP tools/list response result"""

    tools: List[MCPTool]


class MCPToolCallParams(TypedDict):
    """MCP tools/call request parameters"""

    name: str
    arguments: Dict[str, Any]


class MCPToolCallResult(TypedDict):
    """MCP tools/call response result"""

    content: List[Dict[str, Any]]
    isError: Optional[bool]


# BugIt-specific Types
class IssueSeverity(str, Enum):
    """Bug severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueStatus(str, Enum):
    """Bug status values"""

    OPEN = "open"
    RESOLVED = "resolved"
    ARCHIVED = "archived"


class IssueType(str, Enum):
    """Bug type categories"""

    BUG = "bug"
    FEATURE = "feature"
    CHORE = "chore"
    UNKNOWN = "unknown"


class IssueData(TypedDict):
    """Complete issue data structure"""

    id: str
    schema_version: str
    title: str
    description: str
    type: str
    tags: List[str]
    severity: str
    status: str
    solution: str
    created_at: str
    updated_at: str


class IssueFilter(TypedDict, total=False):
    """Issue filtering parameters"""

    tag: Optional[str]
    severity: Optional[str]
    status: Optional[str]


class IssueUpdate(TypedDict, total=False):
    """Issue update parameters"""

    title: Optional[str]
    description: Optional[str]
    severity: Optional[str]
    status: Optional[str]
    solution: Optional[str]
    add_tags: Optional[List[str]]
    remove_tags: Optional[List[str]]


class ConfigData(TypedDict, total=False):
    """Configuration data structure"""

    model: Optional[str]
    enum_mode: Optional[str]
    output_format: Optional[str]
    retry_limit: Optional[int]
    default_severity: Optional[str]
    backup_on_delete: Optional[bool]


# Tool Function Types
ToolFunction = Any  # Function that implements a tool
ToolRegistry = Dict[str, ToolFunction]  # Registry of available tools


# Common JSON-RPC Error Codes
class JSONRPCErrorCode(int, Enum):
    """Standard JSON-RPC error codes"""

    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR = -32000  # Range -32000 to -32099
