"""
Comprehensive unit tests for commands/delete.py
Tests all branches and functionality for high code coverage.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from cli import app
from core.schema import validate_or_default
from core.storage import StorageError


class TestDeleteCommand:
    """Test the delete command functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()

    def test_delete_by_uuid_with_force_json_output(self):
        """Test deleting by UUID with --force flag returns JSON"""
        sample_issue = {
            "id": "abc123",
            "title": "Test Issue",
            "description": "Test description",
            "severity": "medium",
            "type": "bug",
            "tags": ["test"],
        }

        with patch(
            "core.storage.load_issue", return_value=sample_issue
        ) as mock_load, patch(
            "core.storage.delete_issue", return_value=True
        ) as mock_delete:

            result = self.runner.invoke(app, ["delete", "abc123", "--force"])

            assert result.exit_code == 0
            mock_load.assert_called_once_with("abc123")
            mock_delete.assert_called_once_with("abc123")

            # Verify JSON output
            output = json.loads(result.stdout)
            assert output["success"] is True
            assert output["id"] == "abc123"
            assert output["title"] == "Test Issue"

    def test_delete_by_index_with_force_json_output(self):
        """Test deleting by index with --force flag returns JSON"""
        sample_issue = {
            "id": "xyz789",
            "title": "Index Test Issue",
            "description": "Test description",
            "severity": "high",
            "type": "bug",
            "tags": ["index-test"],
        }

        with patch(
            "core.storage.get_issue_by_index", return_value=sample_issue
        ) as mock_get, patch(
            "core.storage.delete_issue", return_value=True
        ) as mock_delete:

            result = self.runner.invoke(app, ["delete", "2", "--force"])

            assert result.exit_code == 0
            mock_get.assert_called_once_with(2)
            mock_delete.assert_called_once_with("xyz789")

            # Verify JSON output
            output = json.loads(result.stdout)
            assert output["success"] is True
            assert output["id"] == "xyz789"
            assert output["title"] == "Index Test Issue"

    def test_delete_without_force_json_mode_returns_error(self):
        """Test that delete without --force in JSON mode returns error"""
        sample_issue = {
            "id": "def456",
            "title": "Safety Test Issue",
            "description": "Test description",
            "severity": "critical",
            "type": "bug",
            "tags": ["safety"],
        }

        with patch("core.storage.load_issue", return_value=sample_issue):
            result = self.runner.invoke(app, ["delete", "def456"])

            assert result.exit_code == 0  # No error, just requires confirmation

            # Verify JSON error response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "Confirmation required" in output["error"]
            assert "Use --force" in output["error"]
            assert output["issue_to_delete"]["id"] == "def456"
            assert output["issue_to_delete"]["title"] == "Safety Test Issue"

    def test_delete_with_pretty_flag_and_force(self):
        """Test delete with --pretty and --force flags"""
        sample_issue = {
            "id": "pretty123",
            "title": "Pretty Delete Test",
            "description": "Test description",
            "severity": "low",
            "type": "bug",
            "tags": ["pretty"],
        }

        with patch(
            "core.storage.load_issue", return_value=sample_issue
        ) as mock_load, patch(
            "core.storage.delete_issue", return_value=True
        ) as mock_delete:

            result = self.runner.invoke(
                app, ["delete", "pretty123", "--pretty", "--force"]
            )

            assert result.exit_code == 0
            mock_load.assert_called_once_with("pretty123")
            mock_delete.assert_called_once_with("pretty123")

            # Verify pretty output
            assert "Issue pretty123 deleted successfully." in result.stdout

    def test_delete_with_pretty_flag_no_force_confirmed(self):
        """Test delete with --pretty flag and user confirmation"""
        sample_issue = {
            "id": "confirm123",
            "title": "Confirmation Test",
            "description": "Test description",
            "severity": "medium",
            "type": "bug",
            "tags": ["confirm"],
        }

        with patch(
            "core.storage.load_issue", return_value=sample_issue
        ) as mock_load, patch(
            "core.storage.delete_issue", return_value=True
        ) as mock_delete, patch(
            "typer.confirm", return_value=True
        ) as mock_confirm:

            result = self.runner.invoke(app, ["delete", "confirm123", "--pretty"])

            assert result.exit_code == 0
            mock_load.assert_called_once_with("confirm123")
            mock_confirm.assert_called_once_with(
                "Are you sure you want to delete this issue?"
            )
            mock_delete.assert_called_once_with("confirm123")

            # Verify pretty output
            assert "Issue to delete: Confirmation Test" in result.stdout
            assert "Issue confirm123 deleted successfully." in result.stdout

    def test_delete_with_pretty_flag_no_force_cancelled(self):
        """Test delete with --pretty flag and user cancellation"""
        sample_issue = {
            "id": "cancel123",
            "title": "Cancellation Test",
            "description": "Test description",
            "severity": "high",
            "type": "bug",
            "tags": ["cancel"],
        }

        with patch(
            "core.storage.load_issue", return_value=sample_issue
        ) as mock_load, patch("core.storage.delete_issue") as mock_delete, patch(
            "typer.confirm", return_value=False
        ) as mock_confirm:

            result = self.runner.invoke(app, ["delete", "cancel123", "--pretty"])

            assert result.exit_code == 0
            mock_load.assert_called_once_with("cancel123")
            mock_confirm.assert_called_once_with(
                "Are you sure you want to delete this issue?"
            )
            mock_delete.assert_not_called()

            # Verify cancellation message
            assert "Deletion cancelled." in result.stdout

    def test_delete_storage_error_json_mode(self):
        """Test delete with storage error in JSON mode"""
        sample_issue = {
            "id": "error123",
            "title": "Error Test",
            "description": "Test description",
            "severity": "critical",
            "type": "bug",
            "tags": ["error"],
        }

        with patch("core.storage.load_issue", return_value=sample_issue), patch(
            "core.storage.delete_issue", side_effect=StorageError("File not found")
        ):

            result = self.runner.invoke(app, ["delete", "error123", "--force"])

            assert result.exit_code == 1

            # Verify JSON error response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "File not found" in output["error"]

    def test_delete_storage_error_pretty_mode(self):
        """Test delete with storage error in pretty mode"""
        sample_issue = {
            "id": "error456",
            "title": "Pretty Error Test",
            "description": "Test description",
            "severity": "low",
            "type": "bug",
            "tags": ["error", "pretty"],
        }

        with patch("core.storage.load_issue", return_value=sample_issue), patch(
            "core.storage.delete_issue", side_effect=StorageError("Permission denied")
        ):

            result = self.runner.invoke(
                app, ["delete", "error456", "--pretty", "--force"]
            )

            assert result.exit_code == 1

            # Verify pretty error output
            assert "Error: Permission denied" in result.stderr

    def test_delete_issue_not_found_json_mode(self):
        """Test delete with issue not found in JSON mode"""
        with patch(
            "core.storage.load_issue", side_effect=StorageError("Issue not found")
        ):

            result = self.runner.invoke(app, ["delete", "missing123", "--force"])

            assert result.exit_code == 1

            # Verify JSON error response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "Issue not found" in output["error"]

    def test_delete_issue_not_found_pretty_mode(self):
        """Test delete with issue not found in pretty mode"""
        with patch(
            "core.storage.load_issue", side_effect=StorageError("Issue not found")
        ):

            result = self.runner.invoke(
                app, ["delete", "missing456", "--pretty", "--force"]
            )

            assert result.exit_code == 1

            # Verify pretty error output
            assert "Error: Issue not found" in result.stderr

    def test_delete_invalid_index_error(self):
        """Test delete with invalid index"""
        with patch(
            "core.storage.get_issue_by_index", side_effect=StorageError("Invalid index")
        ):

            result = self.runner.invoke(app, ["delete", "999", "--force"])

            assert result.exit_code == 1

            # Verify JSON error response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "Invalid index" in output["error"]

    def test_delete_unexpected_error_json_mode(self):
        """Test delete with unexpected error in JSON mode"""
        sample_issue = {
            "id": "unexpected123",
            "title": "Unexpected Error Test",
            "description": "Test description",
            "severity": "medium",
            "type": "bug",
            "tags": ["unexpected"],
        }

        with patch("core.storage.load_issue", return_value=sample_issue), patch(
            "core.storage.delete_issue", side_effect=Exception("Unexpected error")
        ):

            result = self.runner.invoke(app, ["delete", "unexpected123", "--force"])

            assert result.exit_code == 1

            # Verify JSON error response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "Unexpected error: Unexpected error" in output["error"]

    def test_delete_unexpected_error_pretty_mode(self):
        """Test delete with unexpected error in pretty mode"""
        sample_issue = {
            "id": "unexpected456",
            "title": "Pretty Unexpected Error Test",
            "description": "Test description",
            "severity": "high",
            "type": "bug",
            "tags": ["unexpected", "pretty"],
        }

        with patch("core.storage.load_issue", return_value=sample_issue), patch(
            "core.storage.delete_issue", side_effect=Exception("Database error")
        ):

            result = self.runner.invoke(
                app, ["delete", "unexpected456", "--pretty", "--force"]
            )

            assert result.exit_code == 1

            # Verify pretty error output
            assert "Unexpected error: Database error" in result.stderr

    def test_delete_short_flags(self):
        """Test delete command with short flags (-f and -p)"""
        sample_issue = {
            "id": "short123",
            "title": "Short Flags Test",
            "description": "Test description",
            "severity": "critical",
            "type": "bug",
            "tags": ["short", "flags"],
        }

        with patch(
            "core.storage.load_issue", return_value=sample_issue
        ) as mock_load, patch(
            "core.storage.delete_issue", return_value=True
        ) as mock_delete:

            result = self.runner.invoke(app, ["delete", "short123", "-f", "-p"])

            assert result.exit_code == 0
            mock_load.assert_called_once_with("short123")
            mock_delete.assert_called_once_with("short123")

            # Verify pretty output with short flags
            assert "Issue short123 deleted successfully." in result.stdout

    def test_delete_by_index_edge_cases(self):
        """Test delete by index with edge cases"""
        test_cases = [
            ("0", 0),  # Zero index
            ("1", 1),  # Single digit
            ("10", 10),  # Double digit
            ("999", 999),  # Large number
        ]

        for index_str, expected_index in test_cases:
            sample_issue = {
                "id": f"index{expected_index}",
                "title": f"Index {expected_index} Test",
                "description": "Test description",
                "severity": "medium",
                "type": "bug",
                "tags": ["index-test"],
            }

            with patch(
                "core.storage.get_issue_by_index", return_value=sample_issue
            ) as mock_get, patch("core.storage.delete_issue", return_value=True):

                result = self.runner.invoke(app, ["delete", index_str, "--force"])

                assert result.exit_code == 0
                mock_get.assert_called_once_with(expected_index)

                # Verify JSON output
                output = json.loads(result.stdout)
                assert output["success"] is True
                assert output["id"] == f"index{expected_index}"

    def test_delete_command_help(self):
        """Test delete command help output"""
        result = self.runner.invoke(app, ["delete", "--help"])

        assert result.exit_code == 0
        assert "Delete a bug report permanently" in result.stdout
        assert "--force" in result.stdout
        assert "--pretty" in result.stdout
        assert "id_or_index" in result.stdout

    def test_delete_unexpected_exception_json_mode(self, temp_dir, mock_config):
        """Test delete command with unexpected exception in JSON mode"""
        import typer

        from commands.delete import delete

        # Create a test that will definitely hit the general exception handler
        # This tests the final exception handling path when pretty_output=False

        with patch("commands.delete.storage.load_issue") as mock_load:
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
                    # Call in JSON mode (pretty_output=False) with force=True
                    delete(id_or_index="test123", force=True, pretty_output=False)

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
