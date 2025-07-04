"""
Smoke tests for MCP server functionality.

Tests basic MCP protocol compliance and tool integration without
requiring a full MCP client setup.
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp.errors import MCPError, MCPInvalidParamsError, MCPMethodNotFoundError
from mcp.server import MCPServer


class TestMCPServer:
    """Test MCP server basic functionality"""

    def setup_method(self):
        """Setup for each test"""
        self.server = MCPServer(debug=False)

    @pytest.mark.asyncio
    async def test_handle_initialize_success(self):
        """Test successful initialization"""
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"},
        }

        result = await self.server._handle_initialize(params)

        assert result["protocolVersion"] == "2024-11-05"
        assert "capabilities" in result
        assert "serverInfo" in result
        assert result["serverInfo"]["name"] == "bugit-mcp-server"

    @pytest.mark.asyncio
    async def test_handle_initialize_missing_params(self):
        """Test initialization with missing parameters"""
        with pytest.raises(MCPInvalidParamsError):
            await self.server._handle_initialize(None)

    @pytest.mark.asyncio
    async def test_handle_initialize_missing_protocol_version(self):
        """Test initialization with missing protocol version"""
        params = {"capabilities": {}, "clientInfo": {"name": "test-client"}}

        with pytest.raises(MCPInvalidParamsError):
            await self.server._handle_initialize(params)

    @pytest.mark.asyncio
    async def test_handle_tools_list(self):
        """Test tools/list request"""
        result = await self.server._handle_tools_list(None)

        assert "tools" in result
        assert isinstance(result["tools"], list)

        # Check that we have the expected tools
        tool_names = [tool["name"] for tool in result["tools"]]
        expected_tools = [
            "create_issue",
            "list_issues",
            "get_issue",
            "update_issue",
            "delete_issue",
            "get_config",
            "set_config",
            "get_storage_stats",
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

        # Check tool structure
        for tool in result["tools"]:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            assert isinstance(tool["inputSchema"], dict)

    @pytest.mark.asyncio
    async def test_handle_tools_call_success(self):
        """Test successful tool call"""
        with patch("mcp.tools.get_config") as mock_get_config:
            mock_get_config.return_value = {
                "success": True,
                "config": {"model": "gpt-4"},
            }

            params = {"name": "get_config", "arguments": {}}

            result = await self.server._handle_tools_call(params)

            assert "content" in result
            assert "isError" in result
            assert result["isError"] is False
            assert len(result["content"]) == 1
            assert result["content"][0]["type"] == "text"

            # Verify the content is valid JSON
            content_text = result["content"][0]["text"]
            parsed_content = json.loads(content_text)
            assert parsed_content["success"] is True

    @pytest.mark.asyncio
    async def test_handle_tools_call_missing_params(self):
        """Test tool call with missing parameters"""
        with pytest.raises(MCPInvalidParamsError):
            await self.server._handle_tools_call(None)

    @pytest.mark.asyncio
    async def test_handle_tools_call_missing_tool_name(self):
        """Test tool call with missing tool name"""
        params = {"arguments": {}}

        with pytest.raises(MCPInvalidParamsError):
            await self.server._handle_tools_call(params)

    @pytest.mark.asyncio
    async def test_handle_tools_call_tool_error(self):
        """Test tool call with tool execution error"""
        # Patch at the registry level to ensure the exception is raised
        with patch.object(self.server.tool_registry, "call_tool") as mock_call:
            mock_call.side_effect = Exception("Tool failed")

            params = {"name": "get_config", "arguments": {}}

            result = await self.server._handle_tools_call(params)

            assert result["isError"] is True
            assert len(result["content"]) == 1

            # Verify the error content
            content_text = result["content"][0]["text"]
            parsed_content = json.loads(content_text)
            assert "error" in parsed_content
            assert "Tool failed" in parsed_content["error"]

    @pytest.mark.asyncio
    async def test_handle_shutdown(self):
        """Test shutdown request"""
        result = await self.server._handle_shutdown(None)

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_dispatch_method_unknown(self):
        """Test dispatching unknown method"""
        with pytest.raises(MCPMethodNotFoundError):
            await self.server._dispatch_method("unknown_method", {})

    def test_create_success_response(self):
        """Test creating success response"""
        result = self.server._create_success_response("test-id", {"data": "test"})

        assert result["jsonrpc"] == "2.0"
        assert result["id"] == "test-id"
        assert result["result"]["data"] == "test"
        # Successful responses should not contain an 'error' key
        assert "error" not in result

    def test_create_error_response(self):
        """Test creating error response"""
        error = MCPError("Test error", 123, {"extra": "data"})
        result = self.server._create_error_response("test-id", error)

        assert result["jsonrpc"] == "2.0"
        assert result["id"] == "test-id"
        # Error responses should not contain a 'result' key
        assert "result" not in result
        assert result["error"]["code"] == 123
        assert result["error"]["message"] == "Test error"
        assert result["error"]["data"]["extra"] == "data"

    @pytest.mark.asyncio
    async def test_handle_request_valid_json_rpc(self):
        """Test handling valid JSON-RPC request"""
        request_data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test"},
                },
                "id": 1,
            }
        )

        response = await self.server._handle_request(request_data)

        assert response is not None
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response

    @pytest.mark.asyncio
    async def test_handle_request_invalid_json(self):
        """Test handling invalid JSON"""
        request_data = "invalid json"

        response = await self.server._handle_request(request_data)

        assert response is not None
        assert response["jsonrpc"] == "2.0"
        assert "error" in response
        assert response["error"]["code"] == -32700  # Parse error

    @pytest.mark.asyncio
    async def test_handle_request_missing_jsonrpc(self):
        """Test handling request without jsonrpc field"""
        request_data = json.dumps({"method": "test", "id": 1})

        response = await self.server._handle_request(request_data)

        assert response is not None
        assert "error" in response
        assert response["error"]["code"] == -32600  # Invalid request

    @pytest.mark.asyncio
    async def test_handle_request_notification(self):
        """Test handling notification (no id)"""
        request_data = json.dumps(
            {"jsonrpc": "2.0", "method": "notifications/initialized"}
        )

        response = await self.server._handle_request(request_data)

        # Notifications should not return a response
        assert response is None
        assert self.server.initialized is True

    @pytest.mark.asyncio
    async def test_handle_notification_initialized(self):
        """Test initialized notification"""
        await self.server._handle_notification("notifications/initialized", None)

        assert self.server.initialized is True

    @pytest.mark.asyncio
    async def test_handle_notification_unknown(self):
        """Test unknown notification"""
        # Should not raise an error, just log a warning
        await self.server._handle_notification("unknown/notification", None)


class TestMCPServerIntegration:
    """Integration tests for MCP server with real tools"""

    def setup_method(self):
        """Setup for each test"""
        self.server = MCPServer(debug=False)

    @pytest.mark.asyncio
    async def test_full_initialize_and_list_tools_flow(self):
        """Test full initialization and tools listing flow"""
        # Initialize
        init_params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "test-client", "version": "1.0.0"},
        }

        init_result = await self.server._handle_initialize(init_params)
        assert init_result["protocolVersion"] == "2024-11-05"

        # List tools
        tools_result = await self.server._handle_tools_list(None)
        assert "tools" in tools_result
        assert len(tools_result["tools"]) > 0

        # Verify specific tool exists
        tool_names = [tool["name"] for tool in tools_result["tools"]]
        assert "create_issue" in tool_names
        assert "list_issues" in tool_names

    @pytest.mark.asyncio
    async def test_tool_call_with_mocked_storage(self):
        """Test tool call with mocked storage operations"""
        with patch("mcp.tools.storage.list_issues") as mock_list:
            mock_list.return_value = [
                {"id": "test1", "title": "Test Issue 1", "severity": "high"},
                {"id": "test2", "title": "Test Issue 2", "severity": "low"},
            ]

            params = {"name": "list_issues", "arguments": {"severity": "high"}}

            result = await self.server._handle_tools_call(params)

            assert result["isError"] is False
            content = json.loads(result["content"][0]["text"])
            assert len(content) == 1  # Only high severity issue
            assert content[0]["severity"] == "high"
