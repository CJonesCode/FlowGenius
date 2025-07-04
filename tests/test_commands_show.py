"""
Comprehensive unit tests for commands/show.py
Tests all branches and functionality for high code coverage.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from cli import app
from core.storage import StorageError


class TestShowCommand:
    """Test the show command functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()
        self.sample_issue = {
            "id": "show123",
            "title": "Sample Show Issue",
            "description": "This is a sample issue for testing the show command",
            "severity": "high",
            "type": "bug",
            "tags": ["show", "test", "sample"],
            "created_at": "2025-01-01T12:00:00",
            "schema_version": "v1",
        }

    def test_show_by_uuid_json_output(self):
        """Test showing issue by UUID with JSON output (default)"""
        with patch(
            "core.storage.load_issue", return_value=self.sample_issue
        ) as mock_load:
            result = self.runner.invoke(app, ["show", "show123"])

            assert result.exit_code == 0
            mock_load.assert_called_once_with("show123")

            # Verify JSON output
            output = json.loads(result.stdout)
            assert output["id"] == "show123"
            assert output["title"] == "Sample Show Issue"
            assert output["severity"] == "high"
            assert output["type"] == "bug"
            assert output["tags"] == ["show", "test", "sample"]
            assert output["created_at"] == "2025-01-01T12:00:00"

    def test_show_by_index_json_output(self):
        """Test showing issue by index with JSON output"""
        with patch(
            "core.storage.get_issue_by_index", return_value=self.sample_issue
        ) as mock_get:
            result = self.runner.invoke(app, ["show", "2"])

            assert result.exit_code == 0
            mock_get.assert_called_once_with(2)

            # Verify JSON output
            output = json.loads(result.stdout)
            assert output["id"] == "show123"
            assert output["title"] == "Sample Show Issue"

    def test_show_by_uuid_pretty_output(self):
        """Test showing issue by UUID with pretty output"""
        with patch(
            "core.storage.load_issue", return_value=self.sample_issue
        ) as mock_load:
            result = self.runner.invoke(app, ["show", "show123", "--pretty"])

            assert result.exit_code == 0
            mock_load.assert_called_once_with("show123")

            # Verify pretty output contains key elements
            assert "Sample Show Issue" in result.stdout
            assert "show123" in result.stdout
            assert "Severity: high" in result.stdout
            assert "Type: bug" in result.stdout
            assert "Tags: show, test, sample" in result.stdout
            assert "Created: 2025-01-01T12:00:00" in result.stdout
            assert "Description:" in result.stdout
            assert "This is a sample issue for testing" in result.stdout

    def test_show_by_index_pretty_output(self):
        """Test showing issue by index with pretty output"""
        with patch(
            "core.storage.get_issue_by_index", return_value=self.sample_issue
        ) as mock_get:
            result = self.runner.invoke(app, ["show", "1", "--pretty"])

            assert result.exit_code == 0
            mock_get.assert_called_once_with(1)

            # Verify pretty output contains key elements
            assert "Sample Show Issue" in result.stdout
            assert "show123" in result.stdout
            assert "Severity: high" in result.stdout

    def test_show_short_flag(self):
        """Test show command with short flag (-p)"""
        with patch("core.storage.load_issue", return_value=self.sample_issue):
            result = self.runner.invoke(app, ["show", "show123", "-p"])

            assert result.exit_code == 0

            # Verify pretty output
            assert "Sample Show Issue" in result.stdout
            assert "Severity: high" in result.stdout

    def test_show_issue_with_no_tags_pretty(self):
        """Test showing issue with no tags in pretty mode"""
        issue_no_tags = self.sample_issue.copy()
        issue_no_tags["tags"] = []

        with patch("core.storage.load_issue", return_value=issue_no_tags):
            result = self.runner.invoke(app, ["show", "show123", "--pretty"])

            assert result.exit_code == 0
            assert "Tags: (none)" in result.stdout

    def test_show_issue_with_missing_tags_field_pretty(self):
        """Test showing issue with missing tags field in pretty mode"""
        issue_missing_tags = self.sample_issue.copy()
        del issue_missing_tags["tags"]

        with patch("core.storage.load_issue", return_value=issue_missing_tags):
            result = self.runner.invoke(app, ["show", "show123", "--pretty"])

            assert result.exit_code == 0
            assert "Tags: (none)" in result.stdout

    def test_show_issue_with_missing_fields_json(self):
        """Test showing issue with missing fields in JSON mode"""
        minimal_issue = {"id": "minimal123"}

        with patch("core.storage.load_issue", return_value=minimal_issue):
            result = self.runner.invoke(app, ["show", "minimal123"])

            assert result.exit_code == 0

            # Verify JSON output handles missing fields
            output = json.loads(result.stdout)
            assert output["id"] == "minimal123"
            assert "title" not in output or output.get("title") is None

    def test_show_issue_with_missing_fields_pretty(self):
        """Test showing issue with missing fields in pretty mode"""
        minimal_issue = {"id": "minimal123"}

        with patch("core.storage.load_issue", return_value=minimal_issue):
            result = self.runner.invoke(app, ["show", "minimal123", "--pretty"])

            assert result.exit_code == 0

            # Verify pretty output handles missing fields gracefully
            assert "minimal123" in result.stdout
            assert "Severity: N/A" in result.stdout
            assert "Type: N/A" in result.stdout
            assert "Created: N/A" in result.stdout
            assert "No title" in result.stdout
            assert "No description" in result.stdout

    def test_show_issue_not_found_json_mode(self):
        """Test show with issue not found in JSON mode"""
        with patch(
            "core.storage.load_issue",
            side_effect=StorageError("Issue not found: missing123"),
        ):
            result = self.runner.invoke(app, ["show", "missing123"])

            assert result.exit_code == 1

            # Verify JSON error response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "Issue not found: missing123" in output["error"]

    def test_show_issue_not_found_pretty_mode(self):
        """Test show with issue not found in pretty mode"""
        with patch(
            "core.storage.load_issue",
            side_effect=StorageError("Issue not found: missing456"),
        ):
            result = self.runner.invoke(app, ["show", "missing456", "--pretty"])

            assert result.exit_code == 1

            # Verify pretty error output
            assert "Error: Issue not found: missing456" in result.stdout

    def test_show_invalid_index_json_mode(self):
        """Test show with invalid index in JSON mode"""
        with patch(
            "core.storage.get_issue_by_index",
            side_effect=StorageError("Invalid index: 999"),
        ):
            result = self.runner.invoke(app, ["show", "999"])

            assert result.exit_code == 1

            # Verify JSON error response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "Invalid index: 999" in output["error"]

    def test_show_invalid_index_pretty_mode(self):
        """Test show with invalid index in pretty mode"""
        with patch(
            "core.storage.get_issue_by_index",
            side_effect=StorageError("Index out of range: 0"),
        ):
            result = self.runner.invoke(app, ["show", "0", "--pretty"])

            assert result.exit_code == 1

            # Verify pretty error output
            assert "Error: Index out of range: 0" in result.stdout

    def test_show_storage_error_json_mode(self):
        """Test show with storage error in JSON mode"""
        with patch(
            "core.storage.load_issue", side_effect=StorageError("Permission denied")
        ):
            result = self.runner.invoke(app, ["show", "test123"])

            assert result.exit_code == 1

            # Verify JSON error response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "Permission denied" in output["error"]

    def test_show_storage_error_pretty_mode(self):
        """Test show with storage error in pretty mode"""
        with patch("core.storage.load_issue", side_effect=StorageError("Disk error")):
            result = self.runner.invoke(app, ["show", "test123", "--pretty"])

            assert result.exit_code == 1

            # Verify pretty error output
            assert "Error: Disk error" in result.stdout

    def test_show_unexpected_exception_json_mode(self, temp_dir, mock_config):
        """Test show command with unexpected exception in JSON mode"""
        from commands.show import show
        import typer

        # Create a test that will definitely hit the general exception handler
        # This tests the final exception handling path when pretty_output=False

        with patch("commands.show.storage.load_issue") as mock_load:
            # Make sure this raises a general Exception, not StorageError or typer.Exit
            mock_load.side_effect = RuntimeError(
                "This will trigger general exception handler"
            )

            # Capture stdout to verify JSON output
            import io
            import sys

            captured_output = io.StringIO()

            with patch("sys.stdout", captured_output):
                # This should raise typer.Exit(1) from the general exception handler
                with pytest.raises(typer.Exit) as exc_info:
                    # Call in JSON mode (pretty_output=False)
                    show(id_or_index="test123", pretty_output=False)

            # Verify it was typer.Exit with code 1
            assert exc_info.value.exit_code == 1

            # Verify JSON output was generated
            output_text = captured_output.getvalue()
            assert output_text.strip()  # Should have output

            # Parse and verify JSON structure
            output = json.loads(output_text)
            assert output["success"] is False
            assert (
                "Unexpected error: This will trigger general exception handler"
                in output["error"]
            )

    def test_show_different_severities_pretty(self):
        """Test show with different severity levels in pretty mode"""
        severities = ["low", "medium", "high", "critical"]

        for severity in severities:
            issue = self.sample_issue.copy()
            issue["severity"] = severity

            with patch("core.storage.load_issue", return_value=issue):
                result = self.runner.invoke(app, ["show", "test123", "--pretty"])

                assert result.exit_code == 0
                assert f"Severity: {severity}" in result.stdout

    def test_show_index_edge_cases(self):
        """Test show with various index formats"""
        test_cases = [
            ("0", 0),  # Zero index
            ("1", 1),  # Single digit
            ("10", 10),  # Double digit
            ("999", 999),  # Large number
        ]

        for index_str, expected_index in test_cases:
            with patch(
                "core.storage.get_issue_by_index", return_value=self.sample_issue
            ) as mock_get:
                result = self.runner.invoke(app, ["show", index_str])

                assert result.exit_code == 0
                mock_get.assert_called_once_with(expected_index)

                # Verify JSON output
                output = json.loads(result.stdout)
                assert output["id"] == "show123"

    def test_show_uuid_formats(self):
        """Test show with various UUID formats"""
        test_uuids = [
            "abc123",
            "test-issue-123",
            "issue_with_underscores",
            "UPPERCASE123",
            "mix3d-C4se_UUID",
        ]

        for uuid in test_uuids:
            with patch(
                "core.storage.load_issue", return_value=self.sample_issue
            ) as mock_load:
                result = self.runner.invoke(app, ["show", uuid])

                assert result.exit_code == 0
                mock_load.assert_called_once_with(uuid)

    def test_show_issue_with_long_content_pretty(self):
        """Test show with issue containing long content in pretty mode"""
        long_issue = self.sample_issue.copy()
        long_issue["title"] = "A" * 200  # Very long title
        long_issue["description"] = "B" * 1000  # Very long description
        long_issue["tags"] = [f"tag{i}" for i in range(20)]  # Many tags

        with patch("core.storage.load_issue", return_value=long_issue):
            result = self.runner.invoke(app, ["show", "long123", "--pretty"])

            assert result.exit_code == 0

            # Verify long content is displayed
            assert "A" * 200 in result.stdout
            assert "B" * 1000 in result.stdout
            assert "tag0, tag1, tag2" in result.stdout  # Some of the tags

    def test_show_issue_with_special_characters_pretty(self):
        """Test show with issue containing special characters in pretty mode"""
        special_issue = {
            "id": "special123",
            "title": "Issue with émojis 🐛 and ñ",
            "description": 'Description with quotes "test" and symbols: @#$%^&*()',
            "severity": "medium",
            "type": "bug",
            "tags": ["utf-8", "émojis", "special-chars"],
            "created_at": "2025-01-01T12:00:00",
            "schema_version": "v1",
        }

        with patch("core.storage.load_issue", return_value=special_issue):
            result = self.runner.invoke(app, ["show", "special123", "--pretty"])

            assert result.exit_code == 0

            # Verify special characters are displayed correctly
            assert "Issue with émojis 🐛 and ñ" in result.stdout
            assert 'quotes "test" and symbols: @#$%^&*()' in result.stdout
            assert "utf-8, émojis, special-chars" in result.stdout

    def test_show_command_help(self):
        """Test show command help output"""
        result = self.runner.invoke(app, ["show", "--help"])

        assert result.exit_code == 0
        assert "Show detailed information about a specific bug report" in result.stdout
        assert "--pretty" in result.stdout
        assert "id_or_index" in result.stdout
        assert "Either the UUID or index" in result.stdout

    def test_show_issue_with_null_values_json(self):
        """Test show with issue containing null values in JSON mode"""
        null_issue = {
            "id": "null123",
            "title": None,
            "description": None,
            "severity": None,
            "type": None,
            "tags": None,
            "created_at": None,
            "schema_version": "v1",
        }

        with patch("core.storage.load_issue", return_value=null_issue):
            result = self.runner.invoke(app, ["show", "null123"])

            assert result.exit_code == 0

            # Verify JSON output preserves null values
            output = json.loads(result.stdout)
            assert output["id"] == "null123"
            assert output["title"] is None
            assert output["description"] is None
            assert output["severity"] is None

    def test_show_issue_with_null_values_pretty(self):
        """Test show with issue containing null values in pretty mode"""
        null_issue = {
            "id": "null456",
            "title": None,
            "description": None,
            "severity": None,
            "type": None,
            "tags": None,
            "created_at": None,
            "schema_version": "v1",
        }

        with patch("core.storage.load_issue", return_value=null_issue):
            result = self.runner.invoke(app, ["show", "null456", "--pretty"])

            assert result.exit_code == 0

            # Verify pretty output handles null values gracefully
            assert "null456" in result.stdout
            assert "Severity: N/A" in result.stdout
            assert "Type: N/A" in result.stdout
            assert "Tags: (none)" in result.stdout
            assert "Created: N/A" in result.stdout
            assert "No title" in result.stdout
            assert "No description" in result.stdout

    def test_show_general_exception_json_mode(self, temp_dir, mock_config):
        """Test show command with general exception in JSON mode to hit line 107"""
        from commands.show import show
        import typer

        # Create a test that will definitely hit line 107
        # Line 107 is: raise typer.Exit(1)
        # It's in the general exception handler when pretty_output=False

        with patch("commands.show.storage.load_issue") as mock_load:
            # Make sure this raises a general Exception, not StorageError or typer.Exit
            mock_load.side_effect = RuntimeError(
                "This will trigger general exception handler"
            )

            # Capture stdout to verify JSON output
            import io
            import sys

            captured_output = io.StringIO()

            with patch("sys.stdout", captured_output):
                # This MUST raise typer.Exit(1) due to line 107
                with pytest.raises(typer.Exit) as exc_info:
                    # Call in JSON mode (pretty_output=False)
                    show(id_or_index="test123", pretty_output=False)

            # Verify it was typer.Exit with code 1 (from line 107)
            assert exc_info.value.exit_code == 1

            # Verify JSON output was generated
            output_text = captured_output.getvalue()
            assert output_text.strip()  # Should have output

            # Parse and verify JSON structure
            output = json.loads(output_text)
            assert output["success"] is False
            assert (
                "Unexpected error: This will trigger general exception handler"
                in output["error"]
            )
