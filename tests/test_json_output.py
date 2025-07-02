"""
JSON Output Tests - Verify all CLI commands return valid JSON by default.
Critical for CLI automation and scripting compatibility.
"""

import json
import subprocess
import pytest
from pathlib import Path


def run_cli_command(command_args):
    """Run CLI command and return stdout, stderr, and exit code"""
    import sys
    
    # Use the same Python executable that's running the tests (with venv)
    result = subprocess.run(
        [sys.executable, "cli.py"] + command_args,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        cwd=Path(__file__).parent.parent
    )
    return result.stdout, result.stderr, result.returncode


def validate_json_output(output):
    """Validate that output is valid JSON and return parsed object"""
    try:
        return json.loads(output.strip())
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON output: {e}\nOutput was: {repr(output)}")


class TestJSONOutputDefault:
    """Test that all commands return JSON by default (without --pretty)"""
    
    def test_list_returns_json(self):
        """Test that 'list' command returns JSON array by default"""
        stdout, stderr, exit_code = run_cli_command(["list"])
        
        assert exit_code == 0, f"Command failed with stderr: {stderr}"
        
        # Should be valid JSON
        parsed = validate_json_output(stdout)
        
        # Should be a list/array
        assert isinstance(parsed, list), f"Expected list, got {type(parsed)}"
        
        # Each item should be an issue object with required fields
        for issue in parsed:
            assert isinstance(issue, dict), f"Expected dict, got {type(issue)}"
            assert "id" in issue, "Issue missing 'id' field"
            assert "title" in issue, "Issue missing 'title' field"
            assert "severity" in issue, "Issue missing 'severity' field"
            assert "created_at" in issue, "Issue missing 'created_at' field"
    
    def test_new_returns_json(self):
        """Test that 'new' command returns JSON object by default"""
        stdout, stderr, exit_code = run_cli_command(["new", "Test JSON output for new command"])
        
        assert exit_code == 0, f"Command failed with stderr: {stderr}"
        
        # Should be valid JSON
        parsed = validate_json_output(stdout)
        
        # Should be an object with success info
        assert isinstance(parsed, dict), f"Expected dict, got {type(parsed)}"
        assert "success" in parsed, "Response missing 'success' field"
        assert "id" in parsed, "Response missing 'id' field"
        assert "issue" in parsed, "Response missing 'issue' field"
        
        # Success should be True
        assert parsed["success"] is True, f"Expected success=True, got {parsed['success']}"
        
        # Issue should be a complete issue object
        issue = parsed["issue"]
        assert isinstance(issue, dict), f"Expected issue dict, got {type(issue)}"
        assert "title" in issue, "Issue missing 'title' field"
        assert "severity" in issue, "Issue missing 'severity' field"
        assert "tags" in issue, "Issue missing 'tags' field"
        assert "type" in issue, "Issue missing 'type' field"
    
    def test_show_returns_json(self):
        """Test that 'show' command returns JSON object by default"""
        # First create an issue to show
        stdout, stderr, exit_code = run_cli_command(["new", "Test issue for show command"])
        assert exit_code == 0, f"Failed to create test issue: {stderr}"
        
        # Now test showing by index
        stdout, stderr, exit_code = run_cli_command(["show", "1"])
        
        assert exit_code == 0, f"Command failed with stderr: {stderr}"
        
        # Should be valid JSON
        parsed = validate_json_output(stdout)
        
        # Should be an issue object
        assert isinstance(parsed, dict), f"Expected dict, got {type(parsed)}"
        assert "id" in parsed, "Issue missing 'id' field"
        assert "title" in parsed, "Issue missing 'title' field"
        assert "description" in parsed, "Issue missing 'description' field"
        assert "severity" in parsed, "Issue missing 'severity' field"
        assert "tags" in parsed, "Issue missing 'tags' field"
        assert "created_at" in parsed, "Issue missing 'created_at' field"
    
    def test_config_returns_json(self):
        """Test that 'config' command returns JSON object by default"""
        stdout, stderr, exit_code = run_cli_command(["config"])
        
        assert exit_code == 0, f"Command failed with stderr: {stderr}"
        
        # Should be valid JSON
        parsed = validate_json_output(stdout)
        
        # Should be a configuration object
        assert isinstance(parsed, dict), f"Expected dict, got {type(parsed)}"
        
        # Should have common config fields
        expected_fields = ["model", "enum_mode", "output_format", "retry_limit"]
        for field in expected_fields:
            assert field in parsed, f"Config missing '{field}' field"
    
    def test_config_get_returns_json(self):
        """Test that 'config --get' returns JSON object by default"""
        stdout, stderr, exit_code = run_cli_command(["config", "--get", "model"])
        
        assert exit_code == 0, f"Command failed with stderr: {stderr}"
        
        # Should be valid JSON
        parsed = validate_json_output(stdout)
        
        # Should be a response object
        assert isinstance(parsed, dict), f"Expected dict, got {type(parsed)}"
        assert "key" in parsed, "Response missing 'key' field"
        assert "value" in parsed, "Response missing 'value' field"
        assert "set" in parsed, "Response missing 'set' field"
        
        # Key should match what we requested
        assert parsed["key"] == "model", f"Expected key='model', got {parsed['key']}"
    
    def test_edit_returns_json(self):
        """Test that 'edit' command returns JSON object by default"""
        # First create an issue to edit
        stdout, stderr, exit_code = run_cli_command(["new", "Test issue for edit command"])
        assert exit_code == 0, f"Failed to create test issue: {stderr}"
        
        # Now test editing
        stdout, stderr, exit_code = run_cli_command(["edit", "1", "--severity", "high"])
        
        assert exit_code == 0, f"Command failed with stderr: {stderr}"
        
        # Should be valid JSON
        parsed = validate_json_output(stdout)
        
        # Should be a success response
        assert isinstance(parsed, dict), f"Expected dict, got {type(parsed)}"
        assert "success" in parsed, "Response missing 'success' field"
        assert "id" in parsed, "Response missing 'id' field"
        assert "changes" in parsed, "Response missing 'changes' field"
        assert "updated_issue" in parsed, "Response missing 'updated_issue' field"
        
        # Success should be True
        assert parsed["success"] is True, f"Expected success=True, got {parsed['success']}"
        
        # Changes should be a list
        assert isinstance(parsed["changes"], list), f"Expected changes list, got {type(parsed['changes'])}"
        
        # Updated issue should be complete
        issue = parsed["updated_issue"]
        assert isinstance(issue, dict), f"Expected issue dict, got {type(issue)}"
        assert issue["severity"] == "high", f"Expected severity='high', got {issue['severity']}"
    
    def test_delete_with_force_returns_json(self):
        """Test that 'delete --force' command returns JSON object by default"""
        # First create an issue to delete
        stdout, stderr, exit_code = run_cli_command(["new", "Test issue for delete command"])
        assert exit_code == 0, f"Failed to create test issue: {stderr}"
        
        # Now test deleting with --force (required in JSON mode)
        stdout, stderr, exit_code = run_cli_command(["delete", "1", "--force"])
        
        assert exit_code == 0, f"Command failed with stderr: {stderr}"
        
        # Should be valid JSON
        parsed = validate_json_output(stdout)
        
        # Should be a success response
        assert isinstance(parsed, dict), f"Expected dict, got {type(parsed)}"
        assert "success" in parsed, "Response missing 'success' field"
        assert "id" in parsed, "Response missing 'id' field"
        assert "title" in parsed, "Response missing 'title' field"
        
        # Success should be True
        assert parsed["success"] is True, f"Expected success=True, got {parsed['success']}"
    
    def test_delete_without_force_returns_json_error(self):
        """Test that 'delete' without --force returns JSON error in default mode"""
        # First create an issue to delete
        stdout, stderr, exit_code = run_cli_command(["new", "Test issue for delete safety"])
        assert exit_code == 0, f"Failed to create test issue: {stderr}"
        
        # Now test deleting without --force (should fail in JSON mode)
        stdout, stderr, exit_code = run_cli_command(["delete", "1"])
        
        # Should succeed (exit 0) but return error in JSON
        assert exit_code == 0, f"Command had unexpected exit code: {exit_code}"
        
        # Should be valid JSON
        parsed = validate_json_output(stdout)
        
        # Should be an error response
        assert isinstance(parsed, dict), f"Expected dict, got {type(parsed)}"
        assert "success" in parsed, "Response missing 'success' field"
        assert "error" in parsed, "Response missing 'error' field"
        assert "issue_to_delete" in parsed, "Response missing 'issue_to_delete' field"
        
        # Success should be False
        assert parsed["success"] is False, f"Expected success=False, got {parsed['success']}"
        
        # Error should mention confirmation
        assert "confirmation" in parsed["error"].lower(), f"Error should mention confirmation: {parsed['error']}"


class TestJSONOutputErrorCases:
    """Test that error cases also return JSON by default"""
    
    def test_invalid_command_args_return_json_errors(self):
        """Test that invalid command arguments return JSON errors"""
        # Test invalid index
        stdout, stderr, exit_code = run_cli_command(["show", "999"])
        
        assert exit_code == 1, f"Expected exit code 1 for invalid index"
        
        # Should be valid JSON error
        parsed = validate_json_output(stdout)
        assert isinstance(parsed, dict), f"Expected dict, got {type(parsed)}"
        assert "success" in parsed, "Error response missing 'success' field"
        assert "error" in parsed, "Error response missing 'error' field"
        assert parsed["success"] is False, f"Expected success=False, got {parsed['success']}"
    
    def test_invalid_severity_returns_json_error(self):
        """Test that invalid severity values return JSON errors"""
        # First create an issue
        stdout, stderr, exit_code = run_cli_command(["new", "Test issue"])
        assert exit_code == 0, f"Failed to create test issue: {stderr}"
        
        # Try to set invalid severity
        stdout, stderr, exit_code = run_cli_command(["edit", "1", "--severity", "invalid"])
        
        assert exit_code == 1, f"Expected exit code 1 for invalid severity"
        
        # Should be valid JSON error
        parsed = validate_json_output(stdout)
        assert isinstance(parsed, dict), f"Expected dict, got {type(parsed)}"
        assert "success" in parsed, "Error response missing 'success' field"
        assert "error" in parsed, "Error response missing 'error' field"
        assert parsed["success"] is False, f"Expected success=False, got {parsed['success']}"


class TestPrettyFlagContrast:
    """Test that --pretty flag produces human-readable output (not JSON)"""
    
    def test_list_pretty_is_not_json(self):
        """Test that 'list --pretty' produces table output, not JSON"""
        stdout, stderr, exit_code = run_cli_command(["list", "--pretty"])
        
        assert exit_code == 0, f"Command failed with stderr: {stderr}"
        
        # Should NOT be valid JSON (should be table)
        try:
            json.loads(stdout.strip())
            pytest.fail("--pretty output should not be JSON, but it was parseable as JSON")
        except json.JSONDecodeError:
            # This is expected - pretty output should not be JSON
            pass
        
        # Should contain table elements
        assert "┏" in stdout or "Index" in stdout, "Pretty output should contain table formatting"
    
    def test_new_pretty_is_not_json(self):
        """Test that 'new --pretty' produces emoji output, not JSON"""
        stdout, stderr, exit_code = run_cli_command(["new", "Test pretty output", "--pretty"])
        
        assert exit_code == 0, f"Command failed with stderr: {stderr}"
        
        # Should NOT be valid JSON
        try:
            json.loads(stdout.strip())
            pytest.fail("--pretty output should not be JSON, but it was parseable as JSON")
        except json.JSONDecodeError:
            # This is expected - pretty output should not be JSON
            pass
        
        # Should contain human-readable indicators
        assert "Issue created:" in stdout or "Title:" in stdout, "Pretty output should contain readable labels"
    
    def test_config_pretty_is_not_json(self):
        """Test that 'config --pretty' produces formatted output, not JSON"""
        stdout, stderr, exit_code = run_cli_command(["config", "--pretty"])
        
        assert exit_code == 0, f"Command failed with stderr: {stderr}"
        
        # Should NOT be valid JSON
        try:
            json.loads(stdout.strip())
            pytest.fail("--pretty output should not be JSON, but it was parseable as JSON")
        except json.JSONDecodeError:
            # This is expected - pretty output should not be JSON
            pass
        
        # Should contain configuration formatting
        assert ("Current configuration:" in stdout or 
                "openai_api_key:" in stdout or 
                "Preferences:" in stdout), "Pretty output should contain formatted config display" 