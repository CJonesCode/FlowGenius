"""
Pytest configuration and shared fixtures for BugIt tests.
Provides test isolation, mock data, and common test utilities.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import os


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
def mock_config():
    """Mock configuration for testing"""
    return {
        'api_key': 'test-key-123',
        'model': 'gpt-4',
        'enum_mode': 'auto'
    }


@pytest.fixture  
def sample_issue():
    """Sample issue data for testing"""
    return {
        'id': 'test123',
        'schema_version': 'v1',
        'title': 'Test issue',
        'description': 'This is a test issue',
        'tags': ['test'],
        'severity': 'medium',
        'created_at': '2025-01-01T12:00:00'
    }


@pytest.fixture
def sample_issues():
    """Multiple sample issues for list testing"""
    return [
        {
            'id': 'critical1',
            'schema_version': 'v1',
            'title': 'Critical system crash',
            'description': 'System crashes on startup',
            'tags': ['crash', 'startup'],
            'severity': 'critical',
            'created_at': '2025-01-01T10:00:00'
        },
        {
            'id': 'low1',
            'schema_version': 'v1',
            'title': 'Minor UI issue',
            'description': 'Button text is slightly misaligned',
            'tags': ['ui', 'cosmetic'],
            'severity': 'low',
            'created_at': '2025-01-01T11:00:00'
        }
    ] 