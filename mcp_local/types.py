"""
Shared type aliases and interfaces for MCP tools and business logic.

This module defines the core types used by MCP tools and the registry,
focusing on BugIt-specific data structures and tool interfaces.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict


# MCP Tool Types (used by registry)
class MCPTool(TypedDict):
    """MCP tool definition"""

    name: str
    description: str
    inputSchema: Dict[str, Any]  # JSON Schema


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
