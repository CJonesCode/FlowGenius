"""
Test suite for MCP tools business logic.

Tests the pure business logic functions extracted from CLI commands,
ensuring they work correctly without CLI dependencies.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.errors import APIError, StorageError, ValidationError
from mcp_local import tools
from mcp_local.errors import MCPToolError


class TestCreateIssue:
    """Test create_issue function"""

    @patch("mcp.tools.storage.save_issue")
    @patch("mcp.tools.schema.validate_or_default")
    @patch("mcp.tools.model.process_description")
    def test_create_issue_success(self, mock_process, mock_validate, mock_save):
        """Test successful issue creation"""
        # Mock the AI processing
        mock_process.return_value = {
            "title": "Test Issue",
            "description": "Test description",
            "severity": "medium",
            "tags": ["test"],
        }

        # Mock validation
        validated_issue = {
            "id": "test123",
            "title": "Test Issue",
            "description": "Test description",
            "severity": "medium",
            "tags": ["test"],
            "status": "open",
            "solution": "",
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
            "schema_version": "v1",
        }
        mock_validate.return_value = validated_issue

        # Mock storage
        mock_save.return_value = "test123"

        # Call the function
        result = tools.create_issue("Test description")

        # Verify result
        assert result["success"] is True
        assert result["id"] == "test123"
        assert result["issue"] == validated_issue

        # Verify mocks were called
        mock_process.assert_called_once_with("Test description")
        mock_validate.assert_called_once()
        mock_save.assert_called_once_with(validated_issue)

    @patch("mcp.tools.model.process_description")
    def test_create_issue_api_error(self, mock_process):
        """Test API error handling"""
        mock_process.side_effect = APIError("API failed")

        with pytest.raises(MCPToolError) as exc_info:
            tools.create_issue("Test description")

        assert "API failed" in str(exc_info.value)

    @patch("mcp.tools.model.process_description")
    def test_create_issue_generic_error(self, mock_process):
        """Test generic error handling"""
        mock_process.side_effect = Exception("Unexpected error")

        with pytest.raises(MCPToolError) as exc_info:
            tools.create_issue("Test description")

        assert "Unexpected error" in str(exc_info.value)


class TestListIssues:
    """Test list_issues function"""

    @patch("mcp.tools.storage.list_issues")
    def test_list_issues_no_filters(self, mock_list):
        """Test listing issues without filters"""
        mock_issues = [
            {
                "id": "1",
                "title": "Issue 1",
                "severity": "high",
                "tags": ["bug"],
                "status": "open",
            },
            {
                "id": "2",
                "title": "Issue 2",
                "severity": "low",
                "tags": ["feature"],
                "status": "resolved",
            },
        ]
        mock_list.return_value = mock_issues

        result = tools.list_issues()

        assert result == mock_issues
        mock_list.assert_called_once()

    @patch("mcp.tools.storage.list_issues")
    def test_list_issues_with_filters(self, mock_list):
        """Test listing issues with filters"""
        mock_issues = [
            {
                "id": "1",
                "title": "Issue 1",
                "severity": "high",
                "tags": ["bug"],
                "status": "open",
            },
            {
                "id": "2",
                "title": "Issue 2",
                "severity": "low",
                "tags": ["feature"],
                "status": "open",
            },
            {
                "id": "3",
                "title": "Issue 3",
                "severity": "high",
                "tags": ["bug", "urgent"],
                "status": "resolved",
            },
        ]
        mock_list.return_value = mock_issues

        # Test severity filter
        result = tools.list_issues(severity="high")
        assert len(result) == 2
        assert all(issue["severity"] == "high" for issue in result)

        # Test tag filter
        result = tools.list_issues(tag="bug")
        assert len(result) == 2
        assert all("bug" in issue["tags"] for issue in result)

        # Test status filter
        result = tools.list_issues(status="open")
        assert len(result) == 2
        assert all(issue["status"] == "open" for issue in result)

        # Test combined filters
        result = tools.list_issues(severity="high", tag="bug", status="open")
        assert len(result) == 1
        assert result[0]["id"] == "1"

    @patch("mcp.tools.storage.list_issues")
    def test_list_issues_storage_error(self, mock_list):
        """Test storage error handling"""
        mock_list.side_effect = StorageError("Storage failed")

        with pytest.raises(MCPToolError) as exc_info:
            tools.list_issues()

        assert "Storage failed" in str(exc_info.value)


class TestGetIssue:
    """Test get_issue function"""

    @patch("mcp.tools.storage.load_issue")
    def test_get_issue_by_id(self, mock_load):
        """Test getting issue by ID"""
        mock_issue = {"id": "test123", "title": "Test Issue"}
        mock_load.return_value = mock_issue

        result = tools.get_issue("test123")

        assert result["success"] is True
        assert result["issue"] == mock_issue
        mock_load.assert_called_once_with("test123")

    @patch("mcp.tools.storage.get_issue_by_index")
    def test_get_issue_by_index(self, mock_get_by_index):
        """Test getting issue by index"""
        mock_issue = {"id": "test123", "title": "Test Issue"}
        mock_get_by_index.return_value = mock_issue

        result = tools.get_issue(1)

        assert result["success"] is True
        assert result["issue"] == mock_issue
        mock_get_by_index.assert_called_once_with(1)

    @patch("mcp.tools.storage.get_issue_by_index")
    def test_get_issue_by_string_index(self, mock_get_by_index):
        """Test getting issue by string index"""
        mock_issue = {"id": "test123", "title": "Test Issue"}
        mock_get_by_index.return_value = mock_issue

        result = tools.get_issue("1")

        assert result["success"] is True
        assert result["issue"] == mock_issue
        mock_get_by_index.assert_called_once_with(1)

    @patch("mcp.tools.storage.load_issue")
    def test_get_issue_not_found(self, mock_load):
        """Test issue not found error"""
        mock_load.side_effect = StorageError("Issue not found")

        with pytest.raises(MCPToolError) as exc_info:
            tools.get_issue("nonexistent")

        assert "Issue not found" in str(exc_info.value)


class TestUpdateIssue:
    """Test update_issue function"""

    @patch("mcp.tools.storage.save_issue")
    @patch("mcp.tools.schema.validate_or_default")
    @patch("mcp.tools.storage.load_issue")
    def test_update_issue_success(self, mock_load, mock_validate, mock_save):
        """Test successful issue update"""
        # Mock loading the issue
        mock_issue = {
            "id": "test123",
            "title": "Old Title",
            "description": "Old description",
            "severity": "low",
            "tags": ["old"],
            "status": "open",
            "solution": "",
        }
        mock_load.return_value = mock_issue

        # Mock validation
        mock_validate.return_value = mock_issue

        # Update the issue
        result = tools.update_issue(
            "test123",
            title="New Title",
            severity="high",
            add_tags=["new"],
            remove_tags=["old"],
        )

        assert result["success"] is True
        assert result["id"] == "test123"
        assert len(result["changes"]) == 4  # title, severity, add tag, remove tag

        # Verify the issue was updated
        mock_save.assert_called_once()
        updated_issue = mock_save.call_args[0][0]
        assert updated_issue["title"] == "New Title"
        assert updated_issue["severity"] == "high"
        assert "new" in updated_issue["tags"]
        assert "old" not in updated_issue["tags"]

    @patch("mcp.tools.storage.load_issue")
    def test_update_issue_invalid_severity(self, mock_load):
        """Test invalid severity validation"""
        mock_load.return_value = {"id": "test123", "tags": []}

        with pytest.raises(MCPToolError) as exc_info:
            tools.update_issue("test123", severity="invalid")

        assert "Invalid severity" in str(exc_info.value)

    @patch("mcp.tools.storage.load_issue")
    def test_update_issue_invalid_status(self, mock_load):
        """Test invalid status validation"""
        mock_load.return_value = {"id": "test123", "tags": []}

        with pytest.raises(MCPToolError) as exc_info:
            tools.update_issue("test123", status="invalid")

        assert "Invalid status" in str(exc_info.value)

    @patch("mcp.tools.storage.load_issue")
    def test_update_issue_no_changes(self, mock_load):
        """Test update with no changes"""
        mock_load.return_value = {"id": "test123", "tags": []}

        result = tools.update_issue("test123")

        assert result["success"] is False
        assert "No changes specified" in result["message"]


class TestDeleteIssue:
    """Test delete_issue function"""

    @patch("mcp.tools.storage.delete_issue")
    @patch("mcp.tools.storage.load_issue")
    def test_delete_issue_success(self, mock_load, mock_delete):
        """Test successful issue deletion"""
        mock_issue = {"id": "test123", "title": "Test Issue"}
        mock_load.return_value = mock_issue
        mock_delete.return_value = True

        result = tools.delete_issue("test123")

        assert result["success"] is True
        assert "deleted successfully" in result["message"]
        assert result["deleted_issue"]["id"] == "test123"

        mock_load.assert_called_once_with("test123")
        mock_delete.assert_called_once_with("test123")

    @patch("mcp.tools.storage.delete_issue")
    @patch("mcp.tools.storage.get_issue_by_index")
    def test_delete_issue_by_index(self, mock_get_by_index, mock_delete):
        """Test deleting issue by index"""
        mock_issue = {"id": "test123", "title": "Test Issue"}
        mock_get_by_index.return_value = mock_issue
        mock_delete.return_value = True

        result = tools.delete_issue(1)

        assert result["success"] is True
        mock_get_by_index.assert_called_once_with(1)
        mock_delete.assert_called_once_with("test123")

    @patch("mcp.tools.storage.delete_issue")
    @patch("mcp.tools.storage.load_issue")
    def test_delete_issue_not_found(self, mock_load, mock_delete):
        """Test deletion when issue not found"""
        mock_issue = {"id": "test123", "title": "Test Issue"}
        mock_load.return_value = mock_issue
        mock_delete.return_value = False

        result = tools.delete_issue("test123")

        assert result["success"] is False
        assert "not found" in result["message"]


class TestConfig:
    """Test configuration functions"""

    @patch("mcp.tools.config.get_config_value")
    def test_get_config_success(self, mock_get_config):
        """Test successful config retrieval"""
        mock_get_config.side_effect = lambda key: {
            "model": "gpt-4",
            "enum_mode": "auto",
            "output_format": "table",
            "retry_limit": 3,
            "default_severity": "medium",
            "backup_on_delete": True,
        }.get(key)

        result = tools.get_config()

        assert result["success"] is True
        assert result["config"]["model"] == "gpt-4"
        assert result["config"]["retry_limit"] == 3

    @patch("mcp.tools.config.get_config_value")
    def test_get_config_with_defaults(self, mock_get_config):
        """Test config retrieval with missing values using defaults"""
        mock_get_config.side_effect = Exception("Config not found")

        result = tools.get_config()

        assert result["success"] is True
        assert result["config"]["model"] == "gpt-4"  # Default
        assert result["config"]["retry_limit"] == 3  # Default

    @patch("mcp.tools.config.set_config_value")
    @patch("mcp.tools.get_config")
    def test_set_config_success(self, mock_get_config, mock_set_config):
        """Test successful config setting"""
        mock_get_config.return_value = {
            "success": True,
            "config": {"model": "gpt-3.5-turbo"},
        }

        result = tools.set_config("model", "gpt-3.5-turbo")

        assert result["success"] is True
        assert "Configuration updated" in result["message"]
        mock_set_config.assert_called_once_with("model", "gpt-3.5-turbo")

    def test_set_config_invalid_key(self):
        """Test setting invalid config key"""
        with pytest.raises(MCPToolError) as exc_info:
            tools.set_config("invalid_key", "value")

        assert "Invalid configuration key" in str(exc_info.value)

    def test_set_config_invalid_retry_limit(self):
        """Test setting invalid retry limit"""
        with pytest.raises(MCPToolError) as exc_info:
            tools.set_config("retry_limit", "not_a_number")

        assert "must be an integer" in str(exc_info.value)

    def test_set_config_invalid_backup_setting(self):
        """Test setting invalid backup setting"""
        with pytest.raises(MCPToolError) as exc_info:
            tools.set_config("backup_on_delete", "not_a_boolean")

        assert "must be a boolean" in str(exc_info.value)

    def test_set_config_invalid_severity(self):
        """Test setting invalid default severity"""
        with pytest.raises(MCPToolError) as exc_info:
            tools.set_config("default_severity", "invalid")

        assert "must be one of" in str(exc_info.value)


class TestStorageStats:
    """Test storage statistics function"""

    @patch("mcp.tools.storage.get_storage_stats")
    def test_get_storage_stats_success(self, mock_get_stats):
        """Test successful stats retrieval"""
        mock_stats = {
            "total_issues": 5,
            "total_size_bytes": 1024,
            "issues_by_severity": {"low": 1, "medium": 2, "high": 1, "critical": 1},
        }
        mock_get_stats.return_value = mock_stats

        result = tools.get_storage_stats()

        assert result["success"] is True
        assert result["stats"] == mock_stats

    @patch("mcp.tools.storage.get_storage_stats")
    def test_get_storage_stats_error(self, mock_get_stats):
        """Test stats retrieval error"""
        mock_get_stats.side_effect = Exception("Stats failed")

        with pytest.raises(MCPToolError) as exc_info:
            tools.get_storage_stats()

        assert "Stats failed" in str(exc_info.value)
