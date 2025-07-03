"""
Basic infrastructure tests to verify test fixtures and foundational setup.
These tests ensure that the testing infrastructure itself is working correctly.
For comprehensive module testing, see the module-specific test files:
- test_core_storage.py (storage functionality)
- test_core_schema.py (schema validation)
- test_core_model.py (AI model processing)
- test_core_config.py (configuration management)
- test_commands_*.py (CLI command functionality)
"""

import pytest
from unittest.mock import patch
from core import storage, schema, model, config


@pytest.mark.unit
class TestBasicInfrastructure:
    """Test that our basic test infrastructure is working correctly"""
    
    def test_fixtures_work(self, mock_config, sample_issue):
        """Test that our pytest fixtures are properly configured"""
        assert mock_config['model'] == 'gpt-4'
        assert mock_config['openai_api_key'] == 'test-key-123'
        assert sample_issue['id'] == 'test123'
        assert sample_issue['severity'] == 'medium'
        assert sample_issue['type'] == 'bug'
    
    def test_temp_dir_fixture(self, temp_dir):
        """Test that temporary directory fixture is working"""
        import os
        assert temp_dir.exists()
        assert temp_dir.is_dir()
        
        # Should be able to create files in temp dir
        test_file = temp_dir / 'test.txt'
        test_file.write_text('test content')
        assert test_file.exists()
        assert test_file.read_text() == 'test content'
    
    def test_mock_fixtures_isolated(self, mock_config_operations):
        """Test that mock fixtures provide proper isolation"""
        # Mock fixtures should prevent real API calls
        assert mock_config_operations is not None
        
        # This should not make a real API call due to mocking
        with patch('core.model.ChatOpenAI') as mock_openai:
            mock_openai.return_value.invoke.return_value.content = '{"title": "test"}'
            # This would normally fail without API key, but should work with mocks
            try:
                result = model.process_description("test description")
                # If we get here, mocking is working
                assert isinstance(result, dict)
            except Exception as e:
                # If mocking isn't working properly, this test should catch it
                pytest.fail(f"Mock isolation failed: {e}")


@pytest.mark.integration
class TestBasicIntegration:
    """Basic smoke tests for critical system integration points"""
    
    def test_full_workflow_smoke_test(self, temp_dir):
        """Smoke test that basic workflow components can work together"""
        import os
        os.chdir(temp_dir)
        
        # Test that storage directory creation works
        issues_dir = storage.ensure_issues_directory()
        assert issues_dir.exists()
        
        # Test that schema validation produces valid structure
        test_data = {'title': 'Test Issue', 'description': 'Test Description'}
        validated = schema.validate_or_default(test_data)
        assert 'id' in validated
        assert 'schema_version' in validated
        assert validated['schema_version'] == 'v1'
        
        # Test that storage can save and load the validated data
        issue_id = storage.save_issue(validated)
        loaded = storage.load_issue(issue_id)
        assert loaded['title'] == 'Test Issue'
        
        # Test that list functionality works
        issues = storage.list_issues()
        assert len(issues) == 1
        assert issues[0]['id'] == issue_id
        
        # Clean up
        storage.delete_issue(issue_id)
        final_issues = storage.list_issues()
        assert len(final_issues) == 0


@pytest.mark.unit
class TestImportStructure:
    """Test that all modules can be imported correctly"""
    
    def test_core_modules_import(self):
        """Test that all core modules can be imported without errors"""
        from core import storage, schema, model, config, styles
        
        # Verify key functions exist
        assert hasattr(storage, 'save_issue')
        assert hasattr(storage, 'load_issue')
        assert hasattr(schema, 'validate_or_default')
        assert hasattr(model, 'process_description')
        assert hasattr(config, 'load_config')
        assert hasattr(styles, 'Styles')
        assert hasattr(styles, 'Colors')
    
    def test_command_modules_import(self):
        """Test that all command modules can be imported without errors"""
        from commands import new, list, show, edit, delete, config
        
        # Verify main functions exist
        assert hasattr(new, 'new')
        assert hasattr(list, 'list_issues')
        assert hasattr(show, 'show')
        assert hasattr(edit, 'edit')
        assert hasattr(delete, 'delete')
        assert hasattr(config, 'config') 