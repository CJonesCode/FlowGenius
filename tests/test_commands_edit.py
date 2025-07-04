"""
Comprehensive unit tests for commands/edit.py
Tests all branches and functionality for high code coverage.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from cli import app
from core.storage import StorageError
from core.schema import ValidationError


class TestEditCommand:
    """Test the edit command functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()
        self.sample_issue = {
            "id": "test123",
            "title": "Original Title",
            "description": "Original description",
            "severity": "medium",
            "type": "bug",
            "tags": ["original", "test"],
            "created_at": "2025-01-01T12:00:00",
            "schema_version": "v1",
        }

    def test_edit_title_by_uuid_json_output(self):
        """Test editing title by UUID with JSON output"""
        with patch(
            "core.storage.load_issue", return_value=self.sample_issue.copy()
        ) as mock_load, patch(
            "core.schema.validate_or_default", return_value=self.sample_issue.copy()
        ) as mock_validate, patch(
            "core.storage.save_issue"
        ) as mock_save:

            result = self.runner.invoke(
                app, ["edit", "test123", "--title", "New Title"]
            )

            assert result.exit_code == 0
            mock_load.assert_called_once_with("test123")
            mock_save.assert_called_once()

            # Verify JSON output
            output = json.loads(result.stdout)
            assert output["success"] is True
            assert output["id"] == "test123"
            assert "Updated title: New Title" in output["changes"]
            assert "updated_issue" in output

    def test_edit_title_by_index_pretty_output(self):
        """Test editing title by index with pretty output"""
        with patch(
            "core.storage.get_issue_by_index", return_value=self.sample_issue.copy()
        ) as mock_get, patch(
            "core.schema.validate_or_default", return_value=self.sample_issue.copy()
        ) as mock_validate, patch(
            "core.storage.save_issue"
        ) as mock_save:

            result = self.runner.invoke(
                app, ["edit", "1", "--title", "Pretty New Title", "--pretty"]
            )

            assert result.exit_code == 0
            mock_get.assert_called_once_with(1)
            mock_save.assert_called_once()

            # Verify pretty output
            assert "Updated title: Pretty New Title" in result.stdout
            assert "Issue test123 updated successfully." in result.stdout

    def test_edit_severity_valid_values(self):
        """Test editing severity with valid values"""
        valid_severities = ["low", "medium", "high", "critical"]

        for severity in valid_severities:
            with patch(
                "core.storage.load_issue", return_value=self.sample_issue.copy()
            ) as mock_load, patch(
                "core.schema.validate_or_default", return_value=self.sample_issue.copy()
            ) as mock_validate, patch(
                "core.storage.save_issue"
            ) as mock_save:

                result = self.runner.invoke(
                    app, ["edit", "test123", "--severity", severity]
                )

                assert result.exit_code == 0
                mock_save.assert_called_once()

                # Verify JSON output
                output = json.loads(result.stdout)
                assert output["success"] is True
                assert f"Updated severity: {severity}" in output["changes"]

    def test_edit_severity_case_insensitive(self):
        """Test editing severity with different cases"""
        test_cases = [
            ("Low", "low"),
            ("MEDIUM", "medium"),
            ("High", "high"),
            ("CRITICAL", "critical"),
        ]

        for input_severity, expected_severity in test_cases:
            with patch(
                "core.storage.load_issue", return_value=self.sample_issue.copy()
            ) as mock_load, patch(
                "core.schema.validate_or_default", return_value=self.sample_issue.copy()
            ) as mock_validate, patch(
                "core.storage.save_issue"
            ) as mock_save:

                result = self.runner.invoke(
                    app, ["edit", "test123", "--severity", input_severity]
                )

                assert result.exit_code == 0

                # Verify the saved issue has lowercase severity
                saved_issue = mock_validate.call_args[0][0]
                assert saved_issue["severity"] == expected_severity

    def test_edit_severity_invalid_value_json_mode(self):
        """Test editing with invalid severity in JSON mode"""
        with patch("core.storage.load_issue", return_value=self.sample_issue.copy()):
            result = self.runner.invoke(
                app, ["edit", "test123", "--severity", "invalid"]
            )

            assert result.exit_code == 1

            # Verify JSON error response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "Invalid severity: invalid" in output["error"]
            assert "Must be low, medium, high, or critical" in output["error"]

    def test_edit_severity_invalid_value_pretty_mode(self):
        """Test editing with invalid severity in pretty mode"""
        with patch("core.storage.load_issue", return_value=self.sample_issue.copy()):
            result = self.runner.invoke(
                app, ["edit", "test123", "--severity", "urgent", "--pretty"]
            )

            assert result.exit_code == 1

            # Verify pretty error output
            assert "Invalid severity: urgent" in result.stderr
            assert "Must be low, medium, high, or critical" in result.stderr

    def test_edit_add_tag_new_tag(self):
        """Test adding a new tag"""
        with patch(
            "core.storage.load_issue", return_value=self.sample_issue.copy()
        ) as mock_load, patch(
            "core.schema.validate_or_default", return_value=self.sample_issue.copy()
        ) as mock_validate, patch(
            "core.storage.save_issue"
        ) as mock_save:

            result = self.runner.invoke(app, ["edit", "test123", "--add-tag", "newtag"])

            assert result.exit_code == 0
            mock_save.assert_called_once()

            # Verify the tag was added
            saved_issue = mock_validate.call_args[0][0]
            assert "newtag" in saved_issue["tags"]

            # Verify JSON output
            output = json.loads(result.stdout)
            assert output["success"] is True
            assert "Added tag: newtag" in output["changes"]

    def test_edit_add_tag_existing_tag(self):
        """Test adding a tag that already exists"""
        with patch(
            "core.storage.load_issue", return_value=self.sample_issue.copy()
        ) as mock_load, patch(
            "core.schema.validate_or_default", return_value=self.sample_issue.copy()
        ) as mock_validate, patch(
            "core.storage.save_issue"
        ) as mock_save:

            result = self.runner.invoke(
                app, ["edit", "test123", "--add-tag", "original"]
            )

            assert result.exit_code == 0

            # Should not call save since no changes were made
            mock_save.assert_not_called()

            # Verify JSON output indicates no changes
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "No changes specified" in output["message"]
            assert "Tag 'original' already exists." in output["changes"]

    def test_edit_remove_tag_existing_tag(self):
        """Test removing an existing tag"""
        with patch(
            "core.storage.load_issue", return_value=self.sample_issue.copy()
        ) as mock_load, patch(
            "core.schema.validate_or_default", return_value=self.sample_issue.copy()
        ) as mock_validate, patch(
            "core.storage.save_issue"
        ) as mock_save:

            result = self.runner.invoke(
                app, ["edit", "test123", "--remove-tag", "original"]
            )

            assert result.exit_code == 0
            mock_save.assert_called_once()

            # Verify the tag was removed
            saved_issue = mock_validate.call_args[0][0]
            assert "original" not in saved_issue["tags"]

            # Verify JSON output
            output = json.loads(result.stdout)
            assert output["success"] is True
            assert "Removed tag: original" in output["changes"]

    def test_edit_remove_tag_nonexistent_tag(self):
        """Test removing a tag that doesn't exist"""
        with patch(
            "core.storage.load_issue", return_value=self.sample_issue.copy()
        ) as mock_load, patch(
            "core.schema.validate_or_default", return_value=self.sample_issue.copy()
        ) as mock_validate, patch(
            "core.storage.save_issue"
        ) as mock_save:

            result = self.runner.invoke(
                app, ["edit", "test123", "--remove-tag", "nonexistent"]
            )

            assert result.exit_code == 0

            # Should not call save since no changes were made
            mock_save.assert_not_called()

            # Verify JSON output indicates no changes
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "No changes specified" in output["message"]
            assert "Tag 'nonexistent' not found." in output["changes"]

    def test_edit_multiple_fields_simultaneously(self):
        """Test editing multiple fields in one command"""
        with patch(
            "core.storage.load_issue", return_value=self.sample_issue.copy()
        ) as mock_load, patch(
            "core.schema.validate_or_default", return_value=self.sample_issue.copy()
        ) as mock_validate, patch(
            "core.storage.save_issue"
        ) as mock_save:

            result = self.runner.invoke(
                app,
                [
                    "edit",
                    "test123",
                    "--title",
                    "Multi-field Update",
                    "--severity",
                    "high",
                    "--add-tag",
                    "multitag",
                    "--remove-tag",
                    "original",
                    "--pretty",
                ],
            )

            assert result.exit_code == 0
            mock_save.assert_called_once()

            # Verify pretty output shows all changes
            assert "Updated title: Multi-field Update" in result.stdout
            assert "Updated severity: high" in result.stdout
            assert "Added tag: multitag" in result.stdout
            assert "Removed tag: original" in result.stdout
            assert "Issue test123 updated successfully." in result.stdout

    def test_edit_short_flags(self):
        """Test edit command with short flags"""
        with patch(
            "core.storage.load_issue", return_value=self.sample_issue.copy()
        ) as mock_load, patch(
            "core.schema.validate_or_default", return_value=self.sample_issue.copy()
        ) as mock_validate, patch(
            "core.storage.save_issue"
        ) as mock_save:

            result = self.runner.invoke(
                app,
                [
                    "edit",
                    "test123",
                    "-s",
                    "critical",
                    "-a",
                    "shortflag",
                    "-r",
                    "test",
                    "-p",
                ],
            )

            assert result.exit_code == 0
            mock_save.assert_called_once()

            # Verify short flags work same as long flags
            assert "Updated severity: critical" in result.stdout
            assert "Added tag: shortflag" in result.stdout
            assert "Removed tag: test" in result.stdout

    def test_edit_no_changes_specified_json_mode(self):
        """Test edit with no changes in JSON mode"""
        with patch("core.storage.load_issue", return_value=self.sample_issue.copy()):
            result = self.runner.invoke(app, ["edit", "test123"])

            assert result.exit_code == 0

            # Verify JSON response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "No changes specified" in output["message"]
            assert "Use --help to see available options" in output["message"]

    def test_edit_no_changes_specified_pretty_mode(self):
        """Test edit with no changes in pretty mode"""
        with patch("core.storage.load_issue", return_value=self.sample_issue.copy()):
            result = self.runner.invoke(app, ["edit", "test123", "--pretty"])

            assert result.exit_code == 0

            # Verify pretty output
            assert "No changes specified" in result.stdout
            assert "Use --help to see available options" in result.stdout

    def test_edit_storage_error_json_mode(self):
        """Test edit with storage error in JSON mode"""
        with patch(
            "core.storage.load_issue", side_effect=StorageError("Issue not found")
        ):
            result = self.runner.invoke(
                app, ["edit", "missing123", "--title", "New Title"]
            )

            assert result.exit_code == 1

            # Verify JSON error response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "Issue not found" in output["error"]

    def test_edit_storage_error_pretty_mode(self):
        """Test edit with storage error in pretty mode"""
        with patch(
            "core.storage.load_issue", side_effect=StorageError("Permission denied")
        ):
            result = self.runner.invoke(
                app, ["edit", "test123", "--title", "New Title", "--pretty"]
            )

            assert result.exit_code == 1

            # Verify pretty error output
            assert "Error: Permission denied" in result.stderr

    def test_edit_validation_error_json_mode(self):
        """Test edit with validation error in JSON mode"""
        with patch(
            "core.storage.load_issue", return_value=self.sample_issue.copy()
        ), patch(
            "core.schema.validate_or_default",
            side_effect=ValidationError("Invalid data"),
        ):

            result = self.runner.invoke(
                app, ["edit", "test123", "--title", "New Title"]
            )

            assert result.exit_code == 1

            # Verify JSON error response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "Validation error: Invalid data" in output["error"]

    def test_edit_validation_error_pretty_mode(self):
        """Test edit with validation error in pretty mode"""
        with patch(
            "core.storage.load_issue", return_value=self.sample_issue.copy()
        ), patch(
            "core.schema.validate_or_default",
            side_effect=ValidationError("Invalid format"),
        ):

            result = self.runner.invoke(
                app, ["edit", "test123", "--title", "New Title", "--pretty"]
            )

            assert result.exit_code == 1

            # Verify pretty error output
            assert "Validation error: Invalid format" in result.stderr

    def test_edit_save_error_json_mode(self):
        """Test edit with save error in JSON mode"""
        with patch(
            "core.storage.load_issue", return_value=self.sample_issue.copy()
        ), patch(
            "core.schema.validate_or_default", return_value=self.sample_issue.copy()
        ), patch(
            "core.storage.save_issue", side_effect=StorageError("Disk full")
        ):

            result = self.runner.invoke(
                app, ["edit", "test123", "--title", "New Title"]
            )

            assert result.exit_code == 1

            # Verify JSON error response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "Disk full" in output["error"]

    def test_edit_unexpected_error_json_mode(self):
        """Test edit with unexpected error in JSON mode"""
        with patch("core.storage.load_issue", side_effect=Exception("Database error")):
            result = self.runner.invoke(
                app, ["edit", "test123", "--title", "New Title"]
            )

            assert result.exit_code == 1

            # Verify JSON error response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "Unexpected error: Database error" in output["error"]

    def test_edit_unexpected_error_pretty_mode(self):
        """Test edit with unexpected error in pretty mode"""
        with patch("core.storage.load_issue", side_effect=Exception("Network error")):
            result = self.runner.invoke(
                app, ["edit", "test123", "--title", "New Title", "--pretty"]
            )

            assert result.exit_code == 1

            # Verify pretty error output
            assert "Unexpected error: Network error" in result.stderr

    def test_edit_invalid_index_error(self):
        """Test edit with invalid index"""
        with patch(
            "core.storage.get_issue_by_index",
            side_effect=StorageError("Invalid index: 999"),
        ):
            result = self.runner.invoke(app, ["edit", "999", "--title", "New Title"])

            assert result.exit_code == 1

            # Verify JSON error response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "Invalid index: 999" in output["error"]

    def test_edit_issue_without_tags_field(self):
        """Test editing issue that doesn't have tags field"""
        issue_without_tags = {
            "id": "notags123",
            "title": "No Tags Issue",
            "description": "Issue without tags field",
            "severity": "low",
            "type": "bug",
            "created_at": "2025-01-01T12:00:00",
            "schema_version": "v1",
        }

        with patch(
            "core.storage.load_issue", return_value=issue_without_tags
        ) as mock_load, patch(
            "core.schema.validate_or_default", return_value=issue_without_tags
        ) as mock_validate, patch(
            "core.storage.save_issue"
        ) as mock_save:

            result = self.runner.invoke(
                app, ["edit", "notags123", "--add-tag", "firsttag"]
            )

            assert result.exit_code == 0
            mock_save.assert_called_once()

            # Verify the tag was added to empty tags list
            saved_issue = mock_validate.call_args[0][0]
            assert saved_issue["tags"] == ["firsttag"]

    def test_edit_command_help(self):
        """Test edit command help output"""
        result = self.runner.invoke(app, ["edit", "--help"])

        assert result.exit_code == 0
        assert "Edit an existing bug report" in result.stdout
        assert "--title" in result.stdout
        assert "--severity" in result.stdout
        assert "--add-tag" in result.stdout
        assert "--remove-tag" in result.stdout
        assert "--pretty" in result.stdout

    def test_edit_edge_case_empty_strings(self):
        """Test edit with empty string values"""
        with patch(
            "core.storage.load_issue", return_value=self.sample_issue.copy()
        ) as mock_load, patch(
            "core.schema.validate_or_default", return_value=self.sample_issue.copy()
        ) as mock_validate, patch(
            "core.storage.save_issue"
        ) as mock_save:

            result = self.runner.invoke(app, ["edit", "test123", "--title", ""])

            assert result.exit_code == 0
            mock_save.assert_called_once()

            # Verify empty string title was set
            saved_issue = mock_validate.call_args[0][0]
            assert saved_issue["title"] == ""

    def test_edit_tag_operations_edge_cases(self):
        """Test tag operations with edge cases"""
        # Test with special characters and spaces
        with patch(
            "core.storage.load_issue", return_value=self.sample_issue.copy()
        ) as mock_load, patch(
            "core.schema.validate_or_default", return_value=self.sample_issue.copy()
        ) as mock_validate, patch(
            "core.storage.save_issue"
        ) as mock_save:

            result = self.runner.invoke(
                app, ["edit", "test123", "--add-tag", "tag with spaces"]
            )

            assert result.exit_code == 0
            mock_save.assert_called_once()

            # Verify tag with spaces was added
            saved_issue = mock_validate.call_args[0][0]
            assert "tag with spaces" in saved_issue["tags"]
