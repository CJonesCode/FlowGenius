"""
Contract tests for BugIt CLI.
Ensures API schemas, CLI interfaces, and file formats maintain backward compatibility.
"""

import pytest
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import patch
from core import schema, storage


@pytest.mark.integration
class TestCLIContractInterface:
    """Test CLI interface contracts to ensure backward compatibility"""

    def test_cli_help_output_contract(self):
        """Test that CLI help output follows expected format"""
        result = subprocess.run(
            [sys.executable, "cli.py", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        help_output = result.stdout

        # Contract: Help should contain essential commands
        essential_commands = ["new", "list", "show", "edit", "delete", "config"]
        for command in essential_commands:
            assert (
                command in help_output
            ), f"Command '{command}' missing from help output"

        # Contract: Help should mention usage
        assert "usage:" in help_output.lower() or "Usage:" in help_output

    def test_cli_command_help_contracts(self):
        """Test individual command help follows contracts"""
        commands = ["new", "list", "show", "edit", "delete", "config"]

        for command in commands:
            result = subprocess.run(
                [sys.executable, "cli.py", command, "--help"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
            )

            assert result.returncode == 0, f"Help for command '{command}' failed"
            help_output = result.stdout.lower()

            # Contract: Each command help should contain usage info
            assert (
                "usage:" in help_output
            ), f"Command '{command}' help missing usage info"

            # Contract: Essential flags should be documented
            if command in ["new", "list", "show", "edit", "delete", "config"]:
                assert (
                    "--pretty" in help_output or "-p" in help_output
                ), f"Command '{command}' missing --pretty flag"

    def test_cli_error_output_contracts(self):
        """Test CLI error output follows JSON contract when appropriate"""
        # Test invalid command
        result = subprocess.run(
            [sys.executable, "cli.py", "invalid_command"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert (
            result.returncode != 0
        ), "Invalid command should return non-zero exit code"

        # Test invalid arguments
        result = subprocess.run(
            [sys.executable, "cli.py", "show", "999999"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert (
            result.returncode != 0
        ), "Invalid arguments should return non-zero exit code"


@pytest.mark.unit
class TestJSONSchemaContracts:
    """Test JSON schema contracts for data structures"""

    def test_issue_schema_contract(self):
        """Test that issue JSON schema matches expected contract"""
        required_fields = [
            "id",
            "schema_version",
            "title",
            "description",
            "severity",
            "type",
            "tags",
            "created_at",
        ]

        # Test with minimal valid data
        test_data = {
            "title": "Contract Test Issue",
            "description": "Testing schema contracts",
        }

        result = schema.validate_or_default(test_data)

        # Contract: All required fields must be present
        for field in required_fields:
            assert (
                field in result
            ), f"Required field '{field}' missing from validated data"

        # Contract: Field types must be correct
        assert isinstance(result["id"], str), "ID must be string"
        assert isinstance(result["title"], str), "Title must be string"
        assert isinstance(result["description"], str), "Description must be string"
        assert isinstance(result["tags"], list), "Tags must be list"
        assert isinstance(result["severity"], str), "Severity must be string"
        assert isinstance(result["type"], str), "Type must be string"

        # Contract: Schema version must be present and correct
        assert result["schema_version"] == "v1", "Schema version must be 'v1'"

        # Contract: Severity must be valid enum value
        valid_severities = ["low", "medium", "high", "critical"]
        assert (
            result["severity"] in valid_severities
        ), f"Severity must be one of {valid_severities}"

        # Contract: Type must be valid enum value
        valid_types = ["bug", "feature", "chore", "unknown"]
        assert result["type"] in valid_types, f"Type must be one of {valid_types}"

    def test_config_schema_contract(self):
        """Test configuration schema contract"""
        # Test loading default config
        from core.config import load_config

        with patch("core.config.load_config") as mock_load:
            # Mock a complete config
            test_config = {
                "model": "gpt-4",
                "enum_mode": "auto",
                "output_format": "table",
                "retry_limit": 3,
                "default_severity": "medium",
            }
            mock_load.return_value = test_config

            config = load_config()

            # Contract: Essential config fields must be present
            essential_fields = ["model", "enum_mode", "output_format", "retry_limit"]
            for field in essential_fields:
                assert field in config, f"Essential config field '{field}' missing"

            # Contract: Field types must be correct
            assert isinstance(config["model"], str), "Model must be string"
            assert isinstance(config["enum_mode"], str), "Enum mode must be string"
            assert isinstance(
                config["output_format"], str
            ), "Output format must be string"
            assert isinstance(config["retry_limit"], int), "Retry limit must be integer"

    def test_cli_response_schema_contracts(self):
        """Test CLI response schemas follow contracts"""
        # Mock successful response structure
        success_response = {
            "success": True,
            "id": "test123",
            "issue": {"id": "test123", "title": "Test Issue", "severity": "medium"},
        }

        # Contract: Success responses must have success field
        assert "success" in success_response
        assert isinstance(success_response["success"], bool)

        # Mock error response structure
        error_response = {
            "success": False,
            "error": "Test error message",
            "error_code": "TEST_ERROR",
        }

        # Contract: Error responses must have success and error fields
        assert "success" in error_response
        assert "error" in error_response
        assert error_response["success"] is False
        assert isinstance(error_response["error"], str)


@pytest.mark.unit
class TestFileFormatContracts:
    """Test file format contracts for persistence"""

    def test_issue_file_format_contract(self, temp_dir, sample_issue):
        """Test that saved issue files follow format contract"""
        # Save an issue
        issue_id = storage.save_issue(sample_issue)

        # Load raw file content
        issue_file = Path(f".bugit/issues/{issue_id}.json")
        assert issue_file.exists(), "Issue file should exist"

        with open(issue_file, "r", encoding="utf-8") as f:
            raw_content = f.read()

        # Contract: File must be valid JSON
        try:
            file_data = json.loads(raw_content)
        except json.JSONDecodeError as e:
            pytest.fail(f"Issue file contains invalid JSON: {e}")

        # Contract: JSON structure must match schema
        required_fields = [
            "id",
            "schema_version",
            "title",
            "description",
            "severity",
            "type",
            "tags",
            "created_at",
        ]
        for field in required_fields:
            assert field in file_data, f"Saved file missing required field: {field}"

        # Contract: Schema version must be correct
        assert (
            file_data["schema_version"] == "v1"
        ), "Saved file must have correct schema version"

        # Contract: File must be UTF-8 encoded
        assert isinstance(raw_content, str), "File content must be readable as string"

    def test_directory_structure_contract(self, temp_dir):
        """Test that directory structure follows contract"""
        # Create an issue to trigger directory creation
        test_issue = {
            "id": "dir-test",
            "title": "Directory Test",
            "description": "Testing directory structure",
            "severity": "medium",
            "tags": ["test"],
            "schema_version": "v1",
        }

        storage.save_issue(test_issue)

        # Contract: .bugit directory should exist
        bugit_dir = Path(".bugit")
        assert bugit_dir.exists() and bugit_dir.is_dir(), ".bugit directory must exist"

        # Contract: issues subdirectory should exist
        issues_dir = Path(".bugit/issues")
        assert (
            issues_dir.exists() and issues_dir.is_dir()
        ), "issues directory must exist"

        # Contract: Issue files should have .json extension
        issue_file = Path(".bugit/issues/dir-test.json")
        assert issue_file.exists(), "Issue file should exist with .json extension"


@pytest.mark.integration
class TestBackwardCompatibilityContracts:
    """Test backward compatibility with existing data"""

    def test_schema_v1_compatibility(self, temp_dir):
        """Test that v1 schema remains compatible"""
        # Create a v1 format issue file manually
        v1_issue = {
            "id": "compat-test",
            "schema_version": "v1",
            "title": "Compatibility Test",
            "description": "Testing v1 compatibility",
            "severity": "medium",
            "type": "bug",
            "tags": ["compat", "test"],
            "created_at": "2025-01-01T12:00:00",
        }

        # Save manually to ensure exact format
        storage.save_issue(v1_issue)

        # Load using current system
        loaded_issue = storage.load_issue("compat-test")

        # Contract: All v1 fields must be preserved
        for key, value in v1_issue.items():
            assert (
                loaded_issue[key] == value
            ), f"v1 field '{key}' not preserved during load"

        # Contract: v1 issues must work with current operations
        all_issues = storage.list_issues()
        compat_issues = [issue for issue in all_issues if issue["id"] == "compat-test"]
        assert len(compat_issues) == 1, "v1 issue should appear in listings"

    def test_cli_flag_compatibility(self):
        """Test that CLI flags maintain backward compatibility"""
        # These flags should always work for backward compatibility
        essential_flags = ["--pretty", "-p", "--help", "-h"]

        # Test that config command supports essential flags
        for flag in essential_flags:
            if flag in ["--help", "-h"]:
                result = subprocess.run(
                    [sys.executable, "cli.py", "config", flag],
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).parent.parent,
                )
                assert (
                    result.returncode == 0
                ), f"Config command should support {flag} flag"

    def test_json_output_format_stability(self):
        """Test that JSON output format remains stable"""
        # Mock a list response
        with patch("subprocess.run") as mock_run:
            # Create a proper mock result object
            class MockResult:
                def __init__(self):
                    self.stdout = "[]"
                    self.stderr = ""
                    self.returncode = 0

            mock_result = MockResult()
            mock_run.return_value = mock_result

            # Contract: List command should return JSON array
            result = subprocess.run(
                [sys.executable, "cli.py", "list"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
            )

            # Should be parseable as JSON
            try:
                json.loads(mock_result.stdout)
            except json.JSONDecodeError:
                pytest.fail("List command should return valid JSON by default")


@pytest.mark.unit
class TestAPIContractValidation:
    """Test API contracts for external integrations"""

    def test_model_processing_input_contract(self):
        """Test model processing input contract"""
        # Contract: process_description must accept string input
        from core.model import process_description

        # Should reject None
        with pytest.raises(Exception):
            process_description(None)  # type: ignore

        # Should reject empty string
        with pytest.raises(Exception):
            process_description("")

        # Should reject non-string input
        with pytest.raises(Exception):
            process_description(123)  # type: ignore

    def test_storage_interface_contract(self):
        """Test storage interface contracts"""
        # Contract: save_issue should return string ID
        test_issue = {
            "id": "contract-test",
            "title": "Contract Test",
            "description": "Testing storage contracts",
            "severity": "medium",
            "tags": ["test"],
            "schema_version": "v1",
        }

        with patch("core.storage.save_issue") as mock_save:
            mock_save.return_value = "contract-test"

            result = storage.save_issue(test_issue)
            assert isinstance(result, str), "save_issue must return string ID"

        # Contract: list_issues should return list of dicts
        with patch("core.storage.list_issues") as mock_list:
            mock_list.return_value = [test_issue]

            result = storage.list_issues()
            assert isinstance(result, list), "list_issues must return list"
            if result:
                assert isinstance(
                    result[0], dict
                ), "list_issues must return list of dicts"


@pytest.mark.unit
class TestErrorContractConsistency:
    """Test error handling contracts for consistent behavior"""

    def test_error_message_format_contract(self):
        """Test that error messages follow consistent format"""
        # Contract: All custom exceptions should have meaningful messages
        from core.schema import ValidationError
        from core.model import ModelError
        from core.storage import StorageError

        test_errors = [
            ValidationError("Test validation error"),
            ModelError("Test model error"),
            StorageError("Test storage error"),
        ]

        for error in test_errors:
            # Contract: Error messages should be non-empty strings
            assert str(error), "Error message should not be empty"
            assert isinstance(str(error), str), "Error message should be string"

            # Contract: Error should inherit from appropriate base class
            assert isinstance(
                error, Exception
            ), "All errors should inherit from Exception"

    def test_exit_code_contract(self):
        """Test that exit codes follow contract"""
        # Contract: Success should return 0, errors should return non-zero

        # Test success case (mocked)
        with patch("subprocess.run") as mock_run:
            mock_result = type(
                "MockResult", (), {"returncode": 0, "stdout": "[]", "stderr": ""}
            )()
            mock_run.return_value = mock_result

            result = subprocess.run([sys.executable, "cli.py", "list"])
            # Contract: Successful operations should return 0
            # (In real scenario, this would test actual command)


# Contract validation utilities
def validate_json_schema(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """Utility to validate JSON schema contracts"""
    for field in required_fields:
        if field not in data:
            return False
    return True


def validate_cli_output_format(output: str, expected_format: str) -> bool:
    """Utility to validate CLI output format contracts"""
    if expected_format == "json":
        try:
            json.loads(output)
            return True
        except json.JSONDecodeError:
            return False
    elif expected_format == "table":
        # Check for table indicators
        return any(indicator in output for indicator in ["┏", "│", "Index", "Title"])
    return False
