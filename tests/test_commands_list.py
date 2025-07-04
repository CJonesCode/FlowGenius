"""
Comprehensive unit tests for commands/list.py
Tests all branches and functionality for high code coverage.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from cli import app
from core.storage import StorageError


class TestListCommand:
    """Test the list command functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()
        self.sample_issues = [
            {
                "id": "critical1",
                "title": "Critical system crash on startup",
                "description": "System fails to start",
                "tags": ["crash", "startup", "critical"],
                "severity": "critical",
                "type": "bug",
                "created_at": "2025-01-01T10:00:00",
            },
            {
                "id": "medium1",
                "title": "Feature request for dark mode",
                "description": "Users want dark mode",
                "tags": ["ui", "feature"],
                "severity": "medium",
                "type": "feature",
                "created_at": "2025-01-01T11:00:00",
            },
            {
                "id": "low1",
                "title": "Minor button alignment issue",
                "description": "Button is slightly misaligned",
                "tags": ["ui", "cosmetic"],
                "severity": "low",
                "type": "bug",
                "created_at": "2025-01-01T12:00:00",
            },
        ]

    def test_list_all_issues_json_output(self):
        """Test listing all issues with default JSON output"""
        with patch("core.storage.list_issues", return_value=self.sample_issues):
            result = self.runner.invoke(app, ["list"])

            assert result.exit_code == 0

            # Verify JSON output
            output = json.loads(result.stdout)
            assert len(output) == 3
            assert output[0]["id"] == "critical1"
            assert output[1]["id"] == "medium1"
            assert output[2]["id"] == "low1"

    def test_list_all_issues_pretty_output(self):
        """Test listing all issues with pretty table output"""
        with patch("core.storage.list_issues", return_value=self.sample_issues):
            result = self.runner.invoke(app, ["list", "--pretty"])

            assert result.exit_code == 0

            # Verify table output contains issue data
        assert "critical1" in result.stdout
        assert "medium1" in result.stdout
        assert "low1" in result.stdout
        assert "Critical" in result.stdout  # Title might be split across lines
        assert "system crash" in result.stdout
        assert "Feature" in result.stdout
        assert "[1]" in result.stdout  # Index column
        assert "[2]" in result.stdout
        assert "[3]" in result.stdout

    def test_list_with_short_flag(self):
        """Test list command with short pretty flag"""
        with patch("core.storage.list_issues", return_value=self.sample_issues):
            result = self.runner.invoke(app, ["list", "-p"])

            assert result.exit_code == 0
            assert "critical1" in result.stdout
            assert "[1]" in result.stdout  # Pretty table format

    def test_list_empty_issues(self):
        """Test listing when no issues exist"""
        with patch("core.storage.list_issues", return_value=[]):
            # JSON output
            result = self.runner.invoke(app, ["list"])
            assert result.exit_code == 0
            assert json.loads(result.stdout) == []

            # Pretty output
            result = self.runner.invoke(app, ["list", "--pretty"])
            assert result.exit_code == 0
            # Should show empty table (no data rows)

    def test_filter_by_tag_json_output(self):
        """Test filtering by tag with JSON output"""
        with patch("core.storage.list_issues", return_value=self.sample_issues):
            result = self.runner.invoke(app, ["list", "--tag", "ui"])

            assert result.exit_code == 0

            # Should return only issues with 'ui' tag
            output = json.loads(result.stdout)
            assert len(output) == 2  # medium1 and low1 have 'ui' tag
            assert output[0]["id"] == "medium1"
            assert output[1]["id"] == "low1"

    def test_filter_by_tag_pretty_output(self):
        """Test filtering by tag with pretty output"""
        with patch("core.storage.list_issues", return_value=self.sample_issues):
            result = self.runner.invoke(app, ["list", "--tag", "ui", "--pretty"])

            assert result.exit_code == 0

            # Should show only UI-tagged issues
            assert "medium1" in result.stdout
            assert "low1" in result.stdout
            assert "critical1" not in result.stdout  # No 'ui' tag

    def test_filter_by_tag_short_flag(self):
        """Test filtering by tag with short flag"""
        with patch("core.storage.list_issues", return_value=self.sample_issues):
            result = self.runner.invoke(app, ["list", "-t", "crash"])

            assert result.exit_code == 0

            # Should return only issues with 'crash' tag
            output = json.loads(result.stdout)
            assert len(output) == 1
            assert output[0]["id"] == "critical1"

    def test_filter_by_severity_json_output(self):
        """Test filtering by severity with JSON output"""
        with patch("core.storage.list_issues", return_value=self.sample_issues):
            result = self.runner.invoke(app, ["list", "--severity", "critical"])

            assert result.exit_code == 0

            # Should return only critical issues
            output = json.loads(result.stdout)
            assert len(output) == 1
            assert output[0]["id"] == "critical1"
            assert output[0]["severity"] == "critical"

    def test_filter_by_severity_pretty_output(self):
        """Test filtering by severity with pretty output"""
        with patch("core.storage.list_issues", return_value=self.sample_issues):
            result = self.runner.invoke(
                app, ["list", "--severity", "medium", "--pretty"]
            )

            assert result.exit_code == 0

            # Should show only medium severity issues
            assert "medium1" in result.stdout
            assert "Feature request" in result.stdout
            assert "critical1" not in result.stdout
            assert "low1" not in result.stdout

    def test_filter_by_severity_short_flag(self):
        """Test filtering by severity with short flag"""
        with patch("core.storage.list_issues", return_value=self.sample_issues):
            result = self.runner.invoke(app, ["list", "-s", "low"])

            assert result.exit_code == 0

            # Should return only low severity issues
            output = json.loads(result.stdout)
            assert len(output) == 1
            assert output[0]["id"] == "low1"
            assert output[0]["severity"] == "low"

    def test_filter_by_severity_case_insensitive(self):
        """Test severity filtering is case insensitive"""
        with patch("core.storage.list_issues", return_value=self.sample_issues):
            result = self.runner.invoke(app, ["list", "--severity", "CRITICAL"])

            assert result.exit_code == 0

            # Should work with uppercase
            output = json.loads(result.stdout)
            assert len(output) == 1
            assert output[0]["severity"] == "critical"

    def test_filter_by_both_tag_and_severity(self):
        """Test filtering by both tag and severity"""
        with patch("core.storage.list_issues", return_value=self.sample_issues):
            result = self.runner.invoke(
                app, ["list", "--tag", "ui", "--severity", "low"]
            )

            assert result.exit_code == 0

            # Should return only issues that match both filters
            output = json.loads(result.stdout)
            assert len(output) == 1
            assert output[0]["id"] == "low1"  # Has both 'ui' tag and 'low' severity

    def test_filter_with_no_matches(self):
        """Test filtering with no matching results"""
        with patch("core.storage.list_issues", return_value=self.sample_issues):
            result = self.runner.invoke(app, ["list", "--tag", "nonexistent"])

            assert result.exit_code == 0

            # Should return empty array
            output = json.loads(result.stdout)
            assert output == []

    def test_combined_short_flags(self):
        """Test using multiple short flags together"""
        with patch("core.storage.list_issues", return_value=self.sample_issues):
            result = self.runner.invoke(app, ["list", "-t", "ui", "-s", "medium", "-p"])

            assert result.exit_code == 0

            # Should show filtered results in pretty format
            assert "medium1" in result.stdout
            assert "Feature request" in result.stdout
            assert "[1]" in result.stdout  # Pretty table format

    def test_pretty_table_truncates_long_titles(self):
        """Test that long titles are properly truncated in pretty output"""
        long_title_issue = {
            "id": "long1",
            "title": "This is a very long title that should be truncated because it exceeds the display limit",
            "description": "Long description",
            "tags": ["test"],
            "severity": "medium",
            "type": "bug",
            "created_at": "2025-01-01T13:00:00",
        }

        with patch("core.storage.list_issues", return_value=[long_title_issue]):
            result = self.runner.invoke(app, ["list", "--pretty"])

            assert result.exit_code == 0

            # Should truncate title with "..." (Rich table may split across lines)
            assert "This is a very long title" in result.stdout
            assert "that s..." in result.stdout  # Rich table truncation format
            assert "exceeds the display limit" not in result.stdout

    def test_pretty_table_handles_missing_fields(self):
        """Test pretty table handles issues with missing optional fields"""
        incomplete_issue = {
            "id": "incomplete1",
            "severity": "medium",
            "created_at": "2025-01-01T14:00:00",
            # Missing: title, tags
        }

        with patch("core.storage.list_issues", return_value=[incomplete_issue]):
            result = self.runner.invoke(app, ["list", "--pretty"])

            assert result.exit_code == 0

            # Should handle missing fields gracefully
            assert "incomplete1" in result.stdout
            assert "No title" in result.stdout  # Default for missing title
            # Tags column should be empty

    def test_pretty_table_formats_dates(self):
        """Test that dates are properly formatted in pretty output"""
        with patch("core.storage.list_issues", return_value=[self.sample_issues[0]]):
            result = self.runner.invoke(app, ["list", "--pretty"])

            assert result.exit_code == 0

            # Should show just the date part (first 10 chars)
            assert "2025-01-01" in result.stdout
            assert "T10:00:00" not in result.stdout

    def test_storage_error_handling_json_mode(self):
        """Test error handling when storage fails in JSON mode"""
        with patch(
            "core.storage.list_issues", side_effect=StorageError("Storage failed")
        ):
            result = self.runner.invoke(app, ["list"])

            assert result.exit_code == 1
            assert "Error listing issues: Storage failed" in result.stderr

    def test_storage_error_handling_pretty_mode(self):
        """Test error handling when storage fails in pretty mode"""
        with patch(
            "core.storage.list_issues", side_effect=StorageError("Storage failed")
        ):
            result = self.runner.invoke(app, ["list", "--pretty"])

            assert result.exit_code == 1
            assert "Error listing issues: Storage failed" in result.stderr

    def test_unexpected_error_handling(self):
        """Test handling of unexpected errors"""
        with patch(
            "core.storage.list_issues", side_effect=Exception("Unexpected error")
        ):
            result = self.runner.invoke(app, ["list"])

            assert result.exit_code == 1
            assert "Error listing issues: Unexpected error" in result.stderr

    def test_list_command_help(self):
        """Test list command help output"""
        result = self.runner.invoke(app, ["list", "--help"])

        assert result.exit_code == 0
        assert "List all bug reports" in result.stdout
        assert "--tag" in result.stdout
        assert "--severity" in result.stdout
        assert "--pretty" in result.stdout
        assert "-t" in result.stdout  # Short flags
        assert "-s" in result.stdout
        assert "-p" in result.stdout

    def test_json_output_structure_validation(self):
        """Test that JSON output has correct structure"""
        with patch("core.storage.list_issues", return_value=self.sample_issues):
            result = self.runner.invoke(app, ["list"])

            assert result.exit_code == 0

            # Verify JSON structure
            output = json.loads(result.stdout)
            assert isinstance(output, list)

            for issue in output:
                assert isinstance(issue, dict)
                assert "id" in issue
                assert "title" in issue
                assert "severity" in issue
                assert "created_at" in issue

    def test_empty_filter_results_json(self):
        """Test JSON output when filters return no results"""
        with patch("core.storage.list_issues", return_value=self.sample_issues):
            result = self.runner.invoke(app, ["list", "--severity", "nonexistent"])

            assert result.exit_code == 0

            # Should return valid empty JSON array
            output = json.loads(result.stdout)
            assert output == []
            assert isinstance(output, list)

    def test_edge_case_tag_filtering(self):
        """Test edge cases in tag filtering"""
        issues_with_edge_cases = [
            {
                "id": "notags1",
                "title": "Issue with no tags",
                "tags": [],  # Empty tags array
                "severity": "medium",
                "created_at": "2025-01-01T15:00:00",
            },
            {
                "id": "missing_tags1",
                "title": "Issue with missing tags field",
                "severity": "low",
                "created_at": "2025-01-01T16:00:00",
                # No tags field at all
            },
        ]

        with patch("core.storage.list_issues", return_value=issues_with_edge_cases):
            result = self.runner.invoke(app, ["list", "--tag", "test"])

            assert result.exit_code == 0

            # Should return empty results since no issues have the tag
            output = json.loads(result.stdout)
            assert output == []
