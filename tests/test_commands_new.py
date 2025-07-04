"""
Comprehensive unit tests for commands/new.py
Tests all branches and functionality for high code coverage.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from cli import app


class TestNewCommand:
    """Test the new command functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()
        self.sample_processed = {
            "title": "Login button not working",
            "description": "User cannot login to the application",
            "severity": "high",
            "type": "bug",
            "tags": ["login", "authentication"],
        }
        self.sample_validated = {
            "id": "new123",
            "title": "Login button not working",
            "description": "User cannot login to the application",
            "severity": "high",
            "type": "bug",
            "tags": ["login", "authentication"],
            "created_at": "2025-01-01T12:00:00",
            "schema_version": "v1",
        }

    def test_new_issue_json_output(self):
        """Test creating new issue with JSON output (default)"""
        with patch(
            "core.model.process_description", return_value=self.sample_processed
        ) as mock_process, patch(
            "core.schema.validate_or_default", return_value=self.sample_validated
        ) as mock_validate, patch(
            "core.storage.save_issue", return_value="new123"
        ) as mock_save:

            result = self.runner.invoke(
                app, ["new", "User cannot login to the application"]
            )

            assert result.exit_code == 0
            mock_process.assert_called_once_with("User cannot login to the application")
            mock_validate.assert_called_once_with(self.sample_processed)
            mock_save.assert_called_once_with(self.sample_validated)

            # Verify JSON output
            output = json.loads(result.stdout)
            assert output["success"] is True
            assert output["issue"]["id"] == "new123"
            assert output["issue"]["title"] == "Login button not working"
            assert output["issue"]["severity"] == "high"
            assert output["issue"]["type"] == "bug"
            assert output["issue"]["tags"] == ["login", "authentication"]

    def test_new_issue_pretty_output(self):
        """Test creating new issue with pretty output"""
        with patch(
            "core.model.process_description", return_value=self.sample_processed
        ) as mock_process, patch(
            "core.schema.validate_or_default", return_value=self.sample_validated
        ) as mock_validate, patch(
            "core.storage.save_issue", return_value="new123"
        ) as mock_save:

            result = self.runner.invoke(
                app, ["new", "User cannot login to the application", "--pretty"]
            )

            assert result.exit_code == 0
            mock_process.assert_called_once_with("User cannot login to the application")
            mock_validate.assert_called_once_with(self.sample_processed)
            mock_save.assert_called_once_with(self.sample_validated)

            # Verify pretty output contains key elements (Panel format)
            assert "new123" in result.stdout  # ID should be in panel title
            assert "Login button not working" in result.stdout  # Title in panel
            assert "Severity: high" in result.stdout
            assert "Type: bug" in result.stdout
            assert "Tags: login, authentication" in result.stdout
            assert "Created: 2025-01-01T12:00:00" in result.stdout
            assert (
                "User cannot login to the application" in result.stdout
            )  # Description

    def test_new_issue_short_flag(self):
        """Test creating new issue with short flag (-p)"""
        with patch(
            "core.model.process_description", return_value=self.sample_processed
        ), patch(
            "core.schema.validate_or_default", return_value=self.sample_validated
        ), patch(
            "core.storage.save_issue", return_value="new123"
        ):

            result = self.runner.invoke(app, ["new", "Bug description", "-p"])

            assert result.exit_code == 0
            assert "new123" in result.stdout  # ID in panel title
            assert "Login button not working" in result.stdout  # Title in panel

    def test_new_issue_with_no_tags_pretty(self):
        """Test creating issue with no tags in pretty mode"""
        processed_no_tags = self.sample_processed.copy()
        processed_no_tags["tags"] = []

        validated_no_tags = self.sample_validated.copy()
        validated_no_tags["tags"] = []

        with patch(
            "core.model.process_description", return_value=processed_no_tags
        ), patch(
            "core.schema.validate_or_default", return_value=validated_no_tags
        ), patch(
            "core.storage.save_issue", return_value="notags123"
        ):

            result = self.runner.invoke(app, ["new", "Bug with no tags", "--pretty"])

            assert result.exit_code == 0
            assert "Tags: (none)" in result.stdout

    def test_new_issue_with_missing_tags_field_pretty(self):
        """Test creating issue with missing tags field in pretty mode"""
        processed_missing_tags = self.sample_processed.copy()
        del processed_missing_tags["tags"]

        validated_missing_tags = self.sample_validated.copy()
        del validated_missing_tags["tags"]

        with patch(
            "core.model.process_description", return_value=processed_missing_tags
        ), patch(
            "core.schema.validate_or_default", return_value=validated_missing_tags
        ), patch(
            "core.storage.save_issue", return_value="missing123"
        ):

            result = self.runner.invoke(
                app, ["new", "Bug with missing tags field", "--pretty"]
            )

            assert result.exit_code == 0
            assert "Tags: (none)" in result.stdout

    def test_new_issue_different_severities_pretty(self):
        """Test creating issues with different severities in pretty mode"""
        severities = ["low", "medium", "high", "critical"]

        for severity in severities:
            processed = self.sample_processed.copy()
            processed["severity"] = severity

            validated = self.sample_validated.copy()
            validated["severity"] = severity

            with patch("core.model.process_description", return_value=processed), patch(
                "core.schema.validate_or_default", return_value=validated
            ), patch("core.storage.save_issue", return_value=f"{severity}123"):

                result = self.runner.invoke(
                    app, ["new", f"Bug with {severity} severity", "--pretty"]
                )

                assert result.exit_code == 0
                assert f"Severity: {severity}" in result.stdout

    def test_new_issue_long_description(self):
        """Test creating issue with very long description"""
        long_description = "A" * 1000  # Very long description

        with patch(
            "core.model.process_description", return_value=self.sample_processed
        ) as mock_process, patch(
            "core.schema.validate_or_default", return_value=self.sample_validated
        ), patch(
            "core.storage.save_issue", return_value="long123"
        ):

            result = self.runner.invoke(app, ["new", long_description])

            assert result.exit_code == 0
            mock_process.assert_called_once_with(long_description)

            # Verify JSON output
            output = json.loads(result.stdout)
            assert output["success"] is True

    def test_new_issue_special_characters(self):
        """Test creating issue with special characters"""
        special_description = 'Bug with émojis 🐛 and "quotes" & symbols @#$%^&*()'

        with patch(
            "core.model.process_description", return_value=self.sample_processed
        ) as mock_process, patch(
            "core.schema.validate_or_default", return_value=self.sample_validated
        ), patch(
            "core.storage.save_issue", return_value="special123"
        ):

            result = self.runner.invoke(app, ["new", special_description, "--pretty"])

            assert result.exit_code == 0
            mock_process.assert_called_once_with(special_description)

            # Verify the special characters don't cause issues
            assert "special123" in result.stdout  # ID should be in panel

    def test_new_issue_model_error_json_mode(self):
        """Test new command with model processing error in JSON mode"""
        with patch(
            "core.model.process_description", side_effect=Exception("LLM API error")
        ):

            result = self.runner.invoke(app, ["new", "Bug description"])

            assert result.exit_code == 6  # APIError exit code

            # Verify JSON error response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "AI processing failed" in output["error"]

    def test_new_issue_model_error_pretty_mode(self):
        """Test new command with model processing error in pretty mode"""
        with patch(
            "core.model.process_description", side_effect=Exception("Model timeout")
        ):

            result = self.runner.invoke(app, ["new", "Bug description", "--pretty"])

            assert result.exit_code == 6  # APIError exit code

            # In pretty mode, errors are output to stderr via the error handling system
            # The stdout might be empty or contain formatted error output
            assert result.exit_code != 0  # Should fail

    def test_new_issue_validation_error_json_mode(self):
        """Test new command with validation error in JSON mode"""
        with patch(
            "core.model.process_description", return_value=self.sample_processed
        ), patch(
            "core.schema.validate_or_default",
            side_effect=Exception("Validation failed"),
        ):

            result = self.runner.invoke(app, ["new", "Bug description"])

            assert result.exit_code == 1

            # Verify JSON error response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "Error creating issue: Validation failed" in output["error"]

    def test_new_issue_validation_error_pretty_mode(self):
        """Test new command with validation error in pretty mode"""
        with patch(
            "core.model.process_description", return_value=self.sample_processed
        ), patch(
            "core.schema.validate_or_default", side_effect=Exception("Invalid schema")
        ):

            result = self.runner.invoke(app, ["new", "Bug description", "--pretty"])

            assert result.exit_code == 1  # Generic error

            # In pretty mode, errors are handled by the error system
            assert result.exit_code != 0  # Should fail

    def test_new_issue_storage_error_json_mode(self):
        """Test new command with storage error in JSON mode"""
        with patch(
            "core.model.process_description", return_value=self.sample_processed
        ), patch(
            "core.schema.validate_or_default", return_value=self.sample_validated
        ), patch(
            "core.storage.save_issue", side_effect=Exception("Disk full")
        ):

            result = self.runner.invoke(app, ["new", "Bug description"])

            assert result.exit_code == 1

            # Verify JSON error response
            output = json.loads(result.stdout)
            assert output["success"] is False
            assert "Error creating issue: Disk full" in output["error"]

    def test_new_issue_storage_error_pretty_mode(self):
        """Test new command with storage error in pretty mode"""
        with patch(
            "core.model.process_description", return_value=self.sample_processed
        ), patch(
            "core.schema.validate_or_default", return_value=self.sample_validated
        ), patch(
            "core.storage.save_issue", side_effect=Exception("Permission denied")
        ):

            result = self.runner.invoke(app, ["new", "Bug description", "--pretty"])

            assert result.exit_code == 4  # StorageError exit code

            # In pretty mode, errors are handled by the error system
            assert result.exit_code != 0  # Should fail

    def test_new_issue_empty_description(self):
        """Test creating issue with empty description"""
        with patch(
            "core.model.process_description", return_value=self.sample_processed
        ) as mock_process, patch(
            "core.schema.validate_or_default", return_value=self.sample_validated
        ), patch(
            "core.storage.save_issue", return_value="empty123"
        ):

            result = self.runner.invoke(app, ["new", ""])

            assert result.exit_code == 0
            mock_process.assert_called_once_with("")

            # Verify JSON output
            output = json.loads(result.stdout)
            assert output["success"] is True

    def test_new_issue_single_word_description(self):
        """Test creating issue with single word description"""
        with patch(
            "core.model.process_description", return_value=self.sample_processed
        ) as mock_process, patch(
            "core.schema.validate_or_default", return_value=self.sample_validated
        ), patch(
            "core.storage.save_issue", return_value="single123"
        ):

            result = self.runner.invoke(app, ["new", "crash"])

            assert result.exit_code == 0
            mock_process.assert_called_once_with("crash")

            # Verify JSON output
            output = json.loads(result.stdout)
            assert output["success"] is True

    def test_new_issue_whitespace_description(self):
        """Test creating issue with whitespace-only description"""
        with patch(
            "core.model.process_description", return_value=self.sample_processed
        ) as mock_process, patch(
            "core.schema.validate_or_default", return_value=self.sample_validated
        ), patch(
            "core.storage.save_issue", return_value="whitespace123"
        ):

            result = self.runner.invoke(app, ["new", "   \n\t  "])

            assert result.exit_code == 0
            mock_process.assert_called_once_with("   \n\t  ")

            # Verify JSON output
            output = json.loads(result.stdout)
            assert output["success"] is True

    def test_new_issue_multiline_description(self):
        """Test creating issue with multiline description"""
        multiline_desc = """This is a bug
        that spans multiple lines
        with various details"""

        with patch(
            "core.model.process_description", return_value=self.sample_processed
        ) as mock_process, patch(
            "core.schema.validate_or_default", return_value=self.sample_validated
        ), patch(
            "core.storage.save_issue", return_value="multiline123"
        ):

            result = self.runner.invoke(app, ["new", multiline_desc])

            assert result.exit_code == 0
            mock_process.assert_called_once_with(multiline_desc)

            # Verify JSON output
            output = json.loads(result.stdout)
            assert output["success"] is True

    def test_new_issue_different_types_pretty(self):
        """Test creating issues with different types in pretty mode"""
        types = ["bug", "feature", "chore", "unknown"]

        for issue_type in types:
            processed = self.sample_processed.copy()
            processed["type"] = issue_type

            validated = self.sample_validated.copy()
            validated["type"] = issue_type

            with patch("core.model.process_description", return_value=processed), patch(
                "core.schema.validate_or_default", return_value=validated
            ), patch("core.storage.save_issue", return_value=f"{issue_type}123"):

                result = self.runner.invoke(
                    app, ["new", f"Issue of type {issue_type}", "--pretty"]
                )

                assert result.exit_code == 0
                assert f"Type: {issue_type}" in result.stdout

    def test_new_issue_many_tags_pretty(self):
        """Test creating issue with many tags in pretty mode"""
        processed_many_tags = self.sample_processed.copy()
        processed_many_tags["tags"] = [f"tag{i}" for i in range(10)]

        validated_many_tags = self.sample_validated.copy()
        validated_many_tags["tags"] = [f"tag{i}" for i in range(10)]

        with patch(
            "core.model.process_description", return_value=processed_many_tags
        ), patch(
            "core.schema.validate_or_default", return_value=validated_many_tags
        ), patch(
            "core.storage.save_issue", return_value="manytags123"
        ):

            result = self.runner.invoke(app, ["new", "Bug with many tags", "--pretty"])

            assert result.exit_code == 0
            assert (
                "Tags: tag0, tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8, tag9"
                in result.stdout
            )

    def test_new_command_help(self):
        """Test new command help output"""
        result = self.runner.invoke(app, ["new", "--help"])

        assert result.exit_code == 0
        assert "Create a new bug report from a freeform description" in result.stdout
        assert "--pretty" in result.stdout
        assert "description" in result.stdout
        # Help text is formatted in a panel, so exact text might vary
        assert "description" in result.stdout.lower()

    def test_new_issue_json_output_structure(self):
        """Test that JSON output has correct structure"""
        validated_structure = self.sample_validated.copy()
        validated_structure["id"] = "structure123"

        with patch(
            "core.model.process_description", return_value=self.sample_processed
        ), patch(
            "core.schema.validate_or_default", return_value=validated_structure
        ), patch(
            "core.storage.save_issue", return_value="structure123"
        ):

            result = self.runner.invoke(app, ["new", "Test structure"])

            assert result.exit_code == 0

            # Verify complete JSON structure
            output = json.loads(result.stdout)
            assert "success" in output
            assert "issue" in output
            assert output["success"] is True

            # Verify issue structure
            issue = output["issue"]
            assert "id" in issue
            assert issue["id"] == "structure123"
            assert "title" in issue
            assert "description" in issue
            assert "severity" in issue
            assert "type" in issue
            assert "tags" in issue
            assert "created_at" in issue
            assert "schema_version" in issue
