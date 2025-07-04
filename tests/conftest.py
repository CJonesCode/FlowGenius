"""
Pytest configuration and shared fixtures for BugIt tests.
Provides test isolation, mock data, and common test utilities following industry standards.
"""

import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def temp_dir():
    """Create temporary directory for test isolation"""
    temp_dir = tempfile.mkdtemp()
    old_cwd = os.getcwd()
    os.chdir(temp_dir)
    yield Path(temp_dir)
    os.chdir(old_cwd)
    shutil.rmtree(temp_dir)


@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment variables for test isolation"""
    # Clear any existing BugIt environment variables
    # Note: Only API keys should use environment variables, not configuration
    env_vars_to_clear = [
        "BUGIT_OPENAI_API_KEY",
        "BUGIT_ANTHROPIC_API_KEY",
        "BUGIT_GOOGLE_API_KEY",
        "BUGIT_API_KEY",  # Legacy support
        "BUGIT_DEBUG",  # Debug flag is acceptable for development
    ]

    for var in env_vars_to_clear:
        monkeypatch.delenv(var, raising=False)

    yield


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return {
        "openai_api_key": "test-key-123",
        "model": "gpt-4",
        "enum_mode": "auto",
        "output_format": "table",
        "retry_limit": 3,
        "default_severity": "medium",
    }


@pytest.fixture
def mock_config_no_api_key():
    """Mock configuration without API key for testing error cases"""
    return {
        "model": "gpt-4",
        "enum_mode": "auto",
        "output_format": "table",
        "retry_limit": 3,
        "default_severity": "medium",
    }


@pytest.fixture
def mock_config_custom():
    """Factory for creating custom mock configurations"""

    def _create_config(**overrides):
        """Create a custom config with overrides"""
        base_config = {
            "openai_api_key": "test-key-123",
            "model": "gpt-4",
            "enum_mode": "auto",
            "output_format": "table",
            "retry_limit": 3,
            "default_severity": "medium",
        }
        base_config.update(overrides)
        return base_config

    return _create_config


@pytest.fixture
def sample_issue():
    """Sample issue data for testing"""
    return {
        "id": "test123",
        "schema_version": "v1",
        "title": "Test issue",
        "description": "This is a test issue",
        "tags": ["test"],
        "severity": "medium",
        "type": "bug",
        "created_at": "2025-01-01T12:00:00",
    }


@pytest.fixture
def sample_issues():
    """Multiple sample issues for list testing"""
    return [
        {
            "id": "critical1",
            "schema_version": "v1",
            "title": "Critical system crash",
            "description": "System crashes on startup",
            "tags": ["crash", "startup"],
            "severity": "critical",
            "type": "bug",
            "created_at": "2025-01-01T10:00:00",
        },
        {
            "id": "low1",
            "schema_version": "v1",
            "title": "Minor UI issue",
            "description": "Button text is slightly misaligned",
            "tags": ["ui", "cosmetic"],
            "severity": "low",
            "type": "bug",
            "created_at": "2025-01-01T11:00:00",
        },
    ]


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing AI processing"""
    return {
        "title": "Mock Generated Title",
        "description": "Original description passed through",
        "severity": "high",
        "type": "bug",
        "tags": ["mock", "testing"],
    }


@pytest.fixture
def mock_openai_client(mock_llm_response):
    """Mock OpenAI client that returns predictable responses"""
    with patch("core.model.ChatOpenAI") as mock_openai:
        # Create a mock response object
        mock_response = MagicMock()
        mock_response.content = json.dumps(mock_llm_response)

        # Configure the mock client
        mock_client = MagicMock()
        mock_client.invoke.return_value = mock_response
        mock_openai.return_value = mock_client

        yield mock_client


@pytest.fixture
def mock_storage_operations():
    """Mock storage operations for testing without file I/O"""
    with patch("core.storage.save_issue") as mock_save, patch(
        "core.storage.load_issue"
    ) as mock_load, patch("core.storage.list_issues") as mock_list, patch(
        "core.storage.delete_issue"
    ) as mock_delete, patch(
        "core.storage.get_issue_by_index"
    ) as mock_get_by_index:

        # Configure default return values
        mock_save.return_value = "mocked-issue-id"
        mock_load.return_value = {"id": "mocked-issue-id", "title": "Mocked Issue"}
        mock_list.return_value = []
        mock_delete.return_value = True
        mock_get_by_index.return_value = {
            "id": "mocked-issue-id",
            "title": "Mocked Issue",
        }

        yield {
            "save": mock_save,
            "load": mock_load,
            "list": mock_list,
            "delete": mock_delete,
            "get_by_index": mock_get_by_index,
        }


@pytest.fixture
def mock_config_operations(mock_config):
    """Mock configuration operations for testing"""
    with patch("core.config.load_config") as mock_load_config, patch(
        "core.config.get_config_value"
    ) as mock_get_config, patch(
        "core.config.save_preferences"
    ) as mock_save_prefs, patch(
        "core.config.set_api_key"
    ) as mock_set_api_key, patch(
        "core.config.set_preference"
    ) as mock_set_pref, patch(
        "core.config.check_openai_api_key"
    ) as mock_check_key:

        # Configure default behaviors
        mock_load_config.return_value = mock_config
        mock_get_config.side_effect = lambda key: mock_config.get(key)
        mock_save_prefs.return_value = None
        mock_set_api_key.return_value = None
        mock_set_pref.return_value = None
        mock_check_key.return_value = True

        yield {
            "load_config": mock_load_config,
            "get_config_value": mock_get_config,
            "save_preferences": mock_save_prefs,
            "set_api_key": mock_set_api_key,
            "set_preference": mock_set_pref,
            "check_openai_api_key": mock_check_key,
        }


@pytest.fixture
def mock_config_with_custom(mock_config_custom):
    """Mock configuration operations with custom config factory"""

    def _create_mock_config(**config_overrides):
        """Create mock config operations with custom configuration"""
        custom_config = mock_config_custom(**config_overrides)

        with patch("core.config.load_config") as mock_load_config, patch(
            "core.config.get_config_value"
        ) as mock_get_config, patch(
            "core.config.save_preferences"
        ) as mock_save_prefs, patch(
            "core.config.set_api_key"
        ) as mock_set_api_key, patch(
            "core.config.set_preference"
        ) as mock_set_pref, patch(
            "core.config.check_openai_api_key"
        ) as mock_check_key:

            # Configure behaviors with custom config
            mock_load_config.return_value = custom_config
            mock_get_config.side_effect = lambda key: custom_config.get(key)
            mock_save_prefs.return_value = None
            mock_set_api_key.return_value = None
            mock_set_pref.return_value = None
            mock_check_key.return_value = bool(custom_config.get("openai_api_key"))

            return {
                "load_config": mock_load_config,
                "get_config_value": mock_get_config,
                "save_preferences": mock_save_prefs,
                "set_api_key": mock_set_api_key,
                "set_preference": mock_set_pref,
                "check_openai_api_key": mock_check_key,
                "config_data": custom_config,
            }

    return _create_mock_config


@pytest.fixture
def mock_file_operations():
    """Mock file operations for testing without actual file I/O"""
    with patch("builtins.open", create=True) as mock_open, patch(
        "os.path.exists"
    ) as mock_exists, patch("os.makedirs") as mock_makedirs, patch(
        "os.rename"
    ) as mock_rename, patch(
        "os.remove"
    ) as mock_remove:

        # Configure default behaviors
        mock_exists.return_value = True
        mock_makedirs.return_value = None
        mock_rename.return_value = None
        mock_remove.return_value = None

        yield {
            "open": mock_open,
            "exists": mock_exists,
            "makedirs": mock_makedirs,
            "rename": mock_rename,
            "remove": mock_remove,
        }


@pytest.fixture
def isolated_test_environment(
    temp_dir, clean_env, mock_config_operations, mock_storage_operations
):
    """Complete isolated test environment with all mocks"""
    yield {
        "temp_dir": temp_dir,
        "config": mock_config_operations,
        "storage": mock_storage_operations,
    }


# Test data factories following industry standards
class IssueFactory:
    """Factory for creating test issue data with various configurations"""

    @staticmethod
    def create_issue(
        title: str = "Test Issue",
        description: str = "Test description",
        severity: str = "medium",
        tags: Optional[List[str]] = None,
        issue_type: str = "bug",
        issue_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a test issue with specified or default values"""
        if tags is None:
            tags = ["test"]
        if issue_id is None:
            issue_id = f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        return {
            "id": issue_id,
            "schema_version": "v1",
            "title": title,
            "description": description,
            "tags": tags,
            "severity": severity,
            "type": issue_type,
            "created_at": datetime.now().isoformat(),
        }

    @staticmethod
    def create_issues(count: int, **kwargs) -> List[Dict[str, Any]]:
        """Create multiple test issues"""
        return [
            IssueFactory.create_issue(
                title=f"Test Issue {i+1}", issue_id=f"test-{i+1}", **kwargs
            )
            for i in range(count)
        ]


@pytest.fixture
def issue_factory():
    """Provide access to IssueFactory in tests"""
    return IssueFactory


# Error simulation fixtures
@pytest.fixture
def simulate_api_error():
    """Simulate API errors for testing error handling"""

    def _simulate_error(error_type="rate_limit"):
        if error_type == "rate_limit":
            from openai import RateLimitError

            return RateLimitError(
                message="Rate limit exceeded", response=MagicMock(), body={}
            )
        elif error_type == "invalid_key":
            from openai import AuthenticationError

            return AuthenticationError(
                message="Invalid API key", response=MagicMock(), body={}
            )
        elif error_type == "timeout":
            import asyncio

            return asyncio.TimeoutError("Request timeout")
        else:
            return Exception(f"Simulated {error_type} error")

    return _simulate_error


# Performance testing fixtures
@pytest.fixture
def performance_monitor():
    """Monitor test performance for benchmarking"""
    import time

    start_time = time.time()
    yield
    end_time = time.time()

    execution_time = end_time - start_time
    # Could log to performance database or file
    print(f"\nTest execution time: {execution_time:.3f}s")
