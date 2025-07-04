"""
Tool registry for MCP server.

This module provides dynamic tool discovery and execution capabilities,
automatically introspecting available tools and generating their schemas.
"""

import asyncio
import inspect
from typing import Any, Callable, Dict, List, Union, get_type_hints

from . import tools
from .errors import MCPToolError, MCPToolNotFoundError
from .types import MCPTool
from .types import ToolRegistry as ToolRegistryType


class ToolRegistry:
    """
    Registry for MCP tools with automatic discovery and schema generation.

    Discovers tools by introspecting the tools module and generates
    JSON schemas for their parameters automatically.
    """

    def __init__(self):
        """Initialize the tool registry"""
        self._tools: ToolRegistryType = {}
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._discover_tools()

    def _discover_tools(self):
        """Automatically discover tools from the tools module"""
        # Get all functions from the tools module
        for name, obj in inspect.getmembers(tools, inspect.isfunction):
            # Skip private functions
            if name.startswith("_"):
                continue
            
            # Skip utility functions that shouldn't be exposed as tools
            if name in ["convert_bugit_error_to_mcp"]:
                continue

            # Register the tool
            self._tools[name] = obj
            self._schemas[name] = self._generate_schema(obj)

    def _generate_schema(self, func: Callable) -> Dict[str, Any]:
        """
        Generate JSON schema for a function's parameters.

        Args:
            func: The function to generate schema for

        Returns:
            JSON schema dictionary
        """
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)

        schema = {"type": "object", "properties": {}, "required": []}

        for param_name, param in sig.parameters.items():
            param_type = type_hints.get(param_name, str)
            param_schema = self._type_to_schema(param_type)

            # Add parameter to schema
            schema["properties"][param_name] = param_schema

            # Add to required if no default value
            if param.default == inspect.Parameter.empty:
                schema["required"].append(param_name)

        return schema

    def _type_to_schema(self, python_type: Any) -> Dict[str, Any]:
        """
        Convert Python type to JSON schema.

        Args:
            python_type: Python type to convert

        Returns:
            JSON schema for the type
        """
        # Handle basic types
        if python_type == str:
            return {"type": "string"}
        elif python_type == int:
            return {"type": "integer"}
        elif python_type == float:
            return {"type": "number"}
        elif python_type == bool:
            return {"type": "boolean"}

        # Handle Optional types (Union with None)
        origin = getattr(python_type, "__origin__", None)
        if origin is Union:
            args = getattr(python_type, "__args__", ())
            if len(args) == 2 and type(None) in args:
                # This is Optional[T]
                non_none_type = args[0] if args[1] is type(None) else args[1]
                return self._type_to_schema(non_none_type)

        # Handle List types
        if origin is list:
            args = getattr(python_type, "__args__", ())
            if args:
                item_schema = self._type_to_schema(args[0])
                return {"type": "array", "items": item_schema}
            else:
                return {"type": "array"}

        # Default to string for unknown types
        return {"type": "string"}

    def list_tools(self) -> List[MCPTool]:
        """
        List all available tools with their schemas.

        Returns:
            List of tool definitions
        """
        tool_list = []

        for name, func in self._tools.items():
            # Get function docstring for description
            description = func.__doc__ or f"Execute {name} operation"

            # Clean up description (first line only)
            description = description.strip().split("\n")[0]

            tool_definition: MCPTool = {
                "name": name,
                "description": description,
                "inputSchema": self._schemas[name],
            }

            tool_list.append(tool_definition)

        return tool_list

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool with the given arguments.

        Args:
            name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            Result of the tool execution

        Raises:
            MCPToolNotFoundError: If tool doesn't exist
            MCPToolError: If tool execution fails
        """
        if name not in self._tools:
            raise MCPToolNotFoundError(name)

        tool_func = self._tools[name]

        try:
            # Check if the function is async
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**arguments)
            else:
                result = tool_func(**arguments)

            return result

        except TypeError as e:
            # Handle parameter mismatch
            raise MCPToolError(name, f"Invalid arguments: {e}")
        except Exception as e:
            # Handle any other errors
            raise MCPToolError(name, str(e))

    def get_tool_schema(self, name: str) -> Dict[str, Any]:
        """
        Get the schema for a specific tool.

        Args:
            name: Name of the tool

        Returns:
            JSON schema for the tool

        Raises:
            MCPToolNotFoundError: If tool doesn't exist
        """
        if name not in self._schemas:
            raise MCPToolNotFoundError(name)

        return self._schemas[name]

    def register_tool(self, name: str, func: Callable):
        """
        Manually register a tool function.

        Args:
            name: Name of the tool
            func: Function to register
        """
        self._tools[name] = func
        self._schemas[name] = self._generate_schema(func)

    def unregister_tool(self, name: str):
        """
        Unregister a tool.

        Args:
            name: Name of the tool to remove
        """
        self._tools.pop(name, None)
        self._schemas.pop(name, None)
