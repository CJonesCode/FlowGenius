"""
MCP Server implementation for BugIt.

This module provides a JSON-RPC 2.0 server over stdio that exposes
BugIt's functionality as MCP tools for AI models and other clients.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional

from .errors import (MCPError, MCPInvalidParamsError, MCPMethodNotFoundError,
                     MCPParseError, MCPProtocolError, MCPServerError)
from .registry import ToolRegistry
from .types import (JSONRPCError, JSONRPCErrorCode, JSONRPCRequest,
                    JSONRPCResponse, MCPInitializeParams, MCPInitializeResult,
                    MCPToolCallParams, MCPToolCallResult, MCPToolsListResult)


class MCPServer:
    """
    MCP Server implementation using JSON-RPC 2.0 over stdio.

    Handles MCP protocol lifecycle and dispatches tool calls to the registry.
    """

    def __init__(self, debug: bool = False):
        """Initialize the MCP server"""
        self.debug = debug
        self.initialized = False
        self.tool_registry = ToolRegistry()
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the MCP server"""
        logger = logging.getLogger("mcp.server")
        if self.debug:
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    async def start(self):
        """Start the MCP server and handle incoming requests"""
        self.logger.info("Starting MCP server...")

        try:
            # Use asyncio's built-in stdin/stdout support (cross-platform)
            import platform
            
            # Read from stdin line by line
            while True:
                try:
                    # Read JSON-RPC request from stdin (using executor for cross-platform compatibility)
                    line = await asyncio.get_event_loop().run_in_executor(
                        None, sys.stdin.readline
                    )
                    
                    if not line:
                        break

                    request_data = line.strip()
                    if not request_data:
                        continue

                    self.logger.debug(f"Received request: {request_data}")

                    # Process the request
                    response = await self._handle_request(request_data)

                    # Send response to stdout
                    if response:
                        response_json = json.dumps(response, ensure_ascii=False)
                        print(response_json, flush=True)
                        self.logger.debug(f"Sent response: {response_json}")

                except Exception as e:
                    self.logger.error(f"Error processing request: {e}")
                    error_response = self._create_error_response(
                        None, MCPServerError(str(e))
                    )
                    print(json.dumps(error_response), flush=True)

        except KeyboardInterrupt:
            self.logger.info("Server interrupted by user")
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            raise
        finally:
            self.logger.info("MCP server stopped")

    async def _handle_request(self, request_data: str) -> Optional[Dict[str, Any]]:
        """Handle a single JSON-RPC request"""
        try:
            # Parse JSON-RPC request
            try:
                request = json.loads(request_data)
            except json.JSONDecodeError as e:
                return self._create_error_response(
                    None, MCPParseError(f"Invalid JSON: {e}")
                )

            # Validate JSON-RPC structure
            if not isinstance(request, dict):
                return self._create_error_response(
                    None, MCPProtocolError("Request must be a JSON object")
                )

            if request.get("jsonrpc") != "2.0":
                return self._create_error_response(
                    request.get("id"), MCPProtocolError("Invalid JSON-RPC version")
                )

            method = request.get("method")
            if not method:
                return self._create_error_response(
                    request.get("id"), MCPProtocolError("Missing method")
                )

            params = request.get("params")
            request_id = request.get("id")

            # Handle notifications (requests without id)
            if request_id is None:
                await self._handle_notification(method, params)
                return None

            # Handle method calls
            try:
                result = await self._dispatch_method(method, params)
                return self._create_success_response(request_id, result)
            except MCPError as e:
                return self._create_error_response(request_id, e)
            except Exception as e:
                return self._create_error_response(request_id, MCPServerError(str(e)))

        except Exception as e:
            self.logger.error(f"Unexpected error handling request: {e}")
            return self._create_error_response(None, MCPServerError(str(e)))

    async def _handle_notification(self, method: str, params: Optional[Dict[str, Any]]):
        """Handle JSON-RPC notifications (no response expected)"""
        self.logger.debug(f"Received notification: {method}")

        if method == "notifications/initialized":
            self.initialized = True
            self.logger.info("MCP server initialized")
        elif method == "notifications/cancelled":
            # Handle request cancellation
            self.logger.info("Request cancelled")
        else:
            self.logger.warning(f"Unknown notification: {method}")

    async def _dispatch_method(
        self, method: str, params: Optional[Dict[str, Any]]
    ) -> Any:
        """Dispatch method calls to appropriate handlers"""
        if method == "initialize":
            return await self._handle_initialize(params)
        elif method == "tools/list":
            return await self._handle_tools_list(params)
        elif method == "tools/call":
            return await self._handle_tools_call(params)
        elif method == "shutdown":
            return await self._handle_shutdown(params)
        else:
            raise MCPMethodNotFoundError(method)

    async def _handle_initialize(
        self, params: Optional[Dict[str, Any]]
    ) -> MCPInitializeResult:
        """Handle MCP initialize request"""
        if not params:
            raise MCPInvalidParamsError("Initialize requires parameters")

        protocol_version = params.get("protocolVersion")
        if not protocol_version:
            raise MCPInvalidParamsError("protocolVersion is required")

        # For now, we support the basic MCP protocol
        if protocol_version != "2024-11-05":
            self.logger.warning(f"Unsupported protocol version: {protocol_version}")

        self.logger.info(
            f"Initializing MCP server with protocol version: {protocol_version}"
        )

        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": False  # We don't support dynamic tool updates yet
                }
            },
            "serverInfo": {
                "name": "bugit-mcp-server",
                "version": "1.0.0",
                "description": "BugIt MCP Server - AI-powered bug tracking tools",
            },
        }

    async def _handle_tools_list(
        self, params: Optional[Dict[str, Any]]
    ) -> MCPToolsListResult:
        """Handle tools/list request"""
        tools = self.tool_registry.list_tools()
        return {"tools": tools}

    async def _handle_tools_call(
        self, params: Optional[Dict[str, Any]]
    ) -> MCPToolCallResult:
        """Handle tools/call request"""
        if not params:
            raise MCPInvalidParamsError("tools/call requires parameters")

        tool_name = params.get("name")
        if not tool_name:
            raise MCPInvalidParamsError("Tool name is required")

        arguments = params.get("arguments", {})

        try:
            result = await self.tool_registry.call_tool(tool_name, arguments)
            return {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                "isError": False,
            }
        except Exception as e:
            error_content = {"error": str(e), "tool": tool_name, "arguments": arguments}
            return {
                "content": [
                    {"type": "text", "text": json.dumps(error_content, indent=2)}
                ],
                "isError": True,
            }

    async def _handle_shutdown(
        self, params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle shutdown request"""
        self.logger.info("Received shutdown request")
        return {}

    def _create_success_response(self, request_id: Any, result: Any) -> Dict[str, Any]:
        """Create a successful JSON-RPC response adhering to the spec (no `error` key)."""
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    def _create_error_response(
        self, request_id: Any, error: MCPError
    ) -> Dict[str, Any]:
        """Create an error JSON-RPC response adhering to the spec (no `result` key)."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": error.to_jsonrpc_error(),
        }


async def main():
    """Main entry point for the MCP server"""
    import argparse

    parser = argparse.ArgumentParser(description="BugIt MCP Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    server = MCPServer(debug=args.debug)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
 