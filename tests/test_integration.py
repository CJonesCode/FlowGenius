"""
End-to-end integration tests for BugIt CLI.
Tests complete workflows across multiple components working together.
"""

import json
import subprocess
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch


def run_cli_command(command_args, cwd=None):
    """Run CLI command and return stdout, stderr, and exit code"""
    import sys
    
    if cwd is None:
        cwd = Path(__file__).parent.parent
    
    # Use the same Python executable that's running the tests (with venv)
    result = subprocess.run(
        [sys.executable, "cli.py"] + command_args,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        cwd=cwd
    )
    return result.stdout, result.stderr, result.returncode


@pytest.mark.integration
class TestCompleteWorkflows:
    """Test complete end-to-end workflows"""
    
    def test_complete_issue_lifecycle(self):
        """Test complete issue lifecycle: create, list, show, edit, delete"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # 1. Create a new issue
                stdout, stderr, exit_code = run_cli_command(["new", "Critical bug in authentication system"], cwd=temp_dir)
                assert exit_code == 0, f"Failed to create issue: {stderr}"
                
                create_response = json.loads(stdout)
                assert create_response["success"] is True
                issue_id = create_response["id"]
                
                # 2. List issues and verify it appears
                stdout, stderr, exit_code = run_cli_command(["list"], cwd=temp_dir)
                assert exit_code == 0, f"Failed to list issues: {stderr}"
                
                issues_list = json.loads(stdout)
                assert len(issues_list) == 1
                assert issues_list[0]["id"] == issue_id
                
                # 3. Show the issue details
                stdout, stderr, exit_code = run_cli_command(["show", "1"], cwd=temp_dir)
                assert exit_code == 0, f"Failed to show issue: {stderr}"
                
                issue_details = json.loads(stdout)
                assert issue_details["id"] == issue_id
                assert "Critical bug in authentication system" in issue_details["description"]
                
                # 4. Edit the issue
                stdout, stderr, exit_code = run_cli_command(["edit", "1", "--severity", "high", "--add-tag", "urgent"], cwd=temp_dir)
                assert exit_code == 0, f"Failed to edit issue: {stderr}"
                
                edit_response = json.loads(stdout)
                assert edit_response["success"] is True
                assert edit_response["updated_issue"]["severity"] == "high"
                assert "urgent" in edit_response["updated_issue"]["tags"]
                
                # 5. Verify changes persist
                stdout, stderr, exit_code = run_cli_command(["show", issue_id], cwd=temp_dir)
                assert exit_code == 0, f"Failed to verify changes: {stderr}"
                
                updated_issue = json.loads(stdout)
                assert updated_issue["severity"] == "high"
                assert "urgent" in updated_issue["tags"]
                
                # 6. Delete the issue
                stdout, stderr, exit_code = run_cli_command(["delete", "1", "--force"], cwd=temp_dir)
                assert exit_code == 0, f"Failed to delete issue: {stderr}"
                
                delete_response = json.loads(stdout)
                assert delete_response["success"] is True
                
                # 7. Verify it's gone
                stdout, stderr, exit_code = run_cli_command(["list"], cwd=temp_dir)
                assert exit_code == 0, f"Failed to list after delete: {stderr}"
                
                final_list = json.loads(stdout)
                assert len(final_list) == 0
                
            finally:
                os.chdir(original_cwd)
    
    def test_multiple_issues_management(self):
        """Test managing multiple issues with different severities"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create multiple issues
                issues_data = [
                    ("Critical system crash", "critical"),
                    ("Medium UI bug", "medium"), 
                    ("Low priority typo", "low")
                ]
                
                created_ids = []
                for description, severity in issues_data:
                    stdout, stderr, exit_code = run_cli_command(["new", description], cwd=temp_dir)
                    assert exit_code == 0, f"Failed to create issue: {stderr}"
                    
                    response = json.loads(stdout)
                    created_ids.append(response["id"])
                    
                    # Set severity after creation
                    stdout, stderr, exit_code = run_cli_command(["edit", response["id"], "--severity", severity], cwd=temp_dir)
                    assert exit_code == 0, f"Failed to set severity: {stderr}"
                
                # List all issues
                stdout, stderr, exit_code = run_cli_command(["list"], cwd=temp_dir)
                assert exit_code == 0, f"Failed to list issues: {stderr}"
                
                all_issues = json.loads(stdout)
                assert len(all_issues) == 3
                
                # Issues should be sorted by severity (critical, medium, low)
                assert all_issues[0]["severity"] == "critical"
                assert all_issues[1]["severity"] == "medium"
                assert all_issues[2]["severity"] == "low"
                
                # Test filtering by severity
                stdout, stderr, exit_code = run_cli_command(["list", "--severity", "critical"], cwd=temp_dir)
                assert exit_code == 0, f"Failed to filter by severity: {stderr}"
                
                critical_issues = json.loads(stdout)
                assert len(critical_issues) == 1
                assert critical_issues[0]["severity"] == "critical"
                
            finally:
                os.chdir(original_cwd)
    
    def test_configuration_workflow(self):
        """Test configuration management workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Check default config
                stdout, stderr, exit_code = run_cli_command(["config"], cwd=temp_dir)
                assert exit_code == 0, f"Failed to get config: {stderr}"
                
                config_data = json.loads(stdout)
                assert "model" in config_data
                assert "retry_limit" in config_data
                
                # Set a preference
                stdout, stderr, exit_code = run_cli_command(["config", "--set", "retry_limit", "5"], cwd=temp_dir)
                assert exit_code == 0, f"Failed to set config: {stderr}"
                
                # Verify the change
                stdout, stderr, exit_code = run_cli_command(["config", "--get", "retry_limit"], cwd=temp_dir)
                assert exit_code == 0, f"Failed to get config value: {stderr}"
                
                value_response = json.loads(stdout)
                assert value_response["value"] == 5
                
                # Export configuration
                stdout, stderr, exit_code = run_cli_command(["config", "--export", "backup.json"], cwd=temp_dir)
                assert exit_code == 0, f"Failed to export config: {stderr}"
                
                # Verify exported file exists and has correct content
                backup_file = Path(temp_dir) / "backup.json"
                assert backup_file.exists()
                
                with open(backup_file, 'r') as f:
                    exported_config = json.load(f)
                assert exported_config["retry_limit"] == 5
                
            finally:
                os.chdir(original_cwd)


@pytest.mark.integration 
class TestCLIOutputFormats:
    """Test CLI output format consistency across commands"""
    
    def test_json_output_by_default(self):
        """Test that all commands return JSON by default"""
        commands_to_test = [
            (["list"], list),
            (["config"], dict),
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create a test issue first
                stdout, stderr, exit_code = run_cli_command(["new", "Test issue for output format"], cwd=temp_dir)
                assert exit_code == 0
                
                # Test each command
                for command_args, expected_type in commands_to_test:
                    stdout, stderr, exit_code = run_cli_command(command_args, cwd=temp_dir)
                    assert exit_code == 0, f"Command {command_args} failed: {stderr}"
        
        # Should be valid JSON
                    try:
                        parsed = json.loads(stdout)
                        assert isinstance(parsed, expected_type), f"Expected {expected_type}, got {type(parsed)}"
                    except json.JSONDecodeError:
                        pytest.fail(f"Command {command_args} did not return valid JSON")
                        
            finally:
                os.chdir(original_cwd)
    
    def test_pretty_output_is_human_readable(self):
        """Test that --pretty flag produces human-readable output"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create a test issue
                stdout, stderr, exit_code = run_cli_command(["new", "Test issue", "--pretty"], cwd=temp_dir)
                assert exit_code == 0, f"Failed to create issue: {stderr}"
                
                # Pretty output should not be JSON
                try:
                    json.loads(stdout)
                    pytest.fail("Pretty output should not be valid JSON")
                except json.JSONDecodeError:
                    pass  # Expected
                
                # Should contain human-readable elements
                assert "Issue created:" in stdout
                
                # Test list pretty output
                stdout, stderr, exit_code = run_cli_command(["list", "--pretty"], cwd=temp_dir)
                assert exit_code == 0, f"Failed to list issues: {stderr}"
                
                # Should contain table formatting
                assert ("┏" in stdout or "Index" in stdout or "UUID" in stdout)
                
            finally:
                os.chdir(original_cwd)


@pytest.mark.integration
class TestDataPersistence:
    """Test data persistence across CLI sessions"""
    
    def test_issues_persist_across_sessions(self):
        """Test that issues are properly saved and persist across CLI invocations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create an issue in one CLI session
                stdout, stderr, exit_code = run_cli_command(["new", "Persistent test issue"], cwd=temp_dir)
                assert exit_code == 0, f"Failed to create issue: {stderr}"
                
                create_response = json.loads(stdout)
                issue_id = create_response["id"]
                
                # In a separate CLI session, verify the issue exists
                stdout, stderr, exit_code = run_cli_command(["show", issue_id], cwd=temp_dir)
                assert exit_code == 0, f"Failed to show persisted issue: {stderr}"
                
                issue_data = json.loads(stdout)
                assert issue_data["id"] == issue_id
                assert "Persistent test issue" in issue_data["description"]
                
                # Verify the actual file was created
                issues_dir = Path(temp_dir) / ".bugit" / "issues"
                issue_file = issues_dir / f"{issue_id}.json"
                assert issue_file.exists(), "Issue file was not created on disk"
                
                # Verify file content
                with open(issue_file, 'r') as f:
                    file_data = json.load(f)
                assert file_data["id"] == issue_id
                
            finally:
                os.chdir(original_cwd)
    
    def test_config_persistence(self):
        """Test that configuration changes persist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Set a configuration value
                stdout, stderr, exit_code = run_cli_command(["config", "--set", "retry_limit", "7"], cwd=temp_dir)
                assert exit_code == 0, f"Failed to set config: {stderr}"
                
                # In a separate CLI session, verify the value persists
                stdout, stderr, exit_code = run_cli_command(["config", "--get", "retry_limit"], cwd=temp_dir)
                assert exit_code == 0, f"Failed to get config: {stderr}"
                
                response = json.loads(stdout)
                assert response["value"] == 7
                
                # Verify config file was created
                config_file = Path(temp_dir) / ".bugitrc"
                assert config_file.exists(), "Config file was not created"
                
            finally:
                os.chdir(original_cwd)


@pytest.mark.integration
class TestErrorHandlingWorkflows:
    """Test error handling in complete workflows"""
    
    def test_graceful_handling_of_missing_issues(self):
        """Test graceful handling when trying to operate on non-existent issues"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Try to show non-existent issue
                stdout, stderr, exit_code = run_cli_command(["show", "nonexistent"], cwd=temp_dir)
                assert exit_code == 1, "Should fail when showing non-existent issue"
                
                response = json.loads(stdout)
                assert response["success"] is False
                assert "not found" in response["error"].lower()
                
                # Try to edit non-existent issue
                stdout, stderr, exit_code = run_cli_command(["edit", "nonexistent", "--severity", "high"], cwd=temp_dir)
                assert exit_code == 1, "Should fail when editing non-existent issue"
                
                response = json.loads(stdout)
                assert response["success"] is False
                
            finally:
                os.chdir(original_cwd) 