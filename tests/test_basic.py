"""
Basic tests to verify test infrastructure and fixtures are working.
"""

import pytest
from core import storage, schema, model, config


class TestBasicInfrastructure:
    """Test that our basic infrastructure is working"""
    
    def test_fixtures_work(self, mock_config, sample_issue):
        """Test that our fixtures are properly configured"""
        assert mock_config['model'] == 'gpt-4'
        assert sample_issue['id'] == 'test123'
        assert sample_issue['severity'] == 'medium'
    
    def test_storage_production(self):
        """Test that production storage is functional"""
        # Create a test issue
        test_data = {
            'id': 'test-storage',
            'title': 'Test Storage Issue',
            'description': 'Testing production storage',
            'severity': 'medium',
            'tags': ['test'],
            'schema_version': 'v1'
        }
        
        # Test save_issue
        saved_id = storage.save_issue(test_data)
        assert saved_id == 'test-storage'
        
        # Test load_issue
        loaded_issue = storage.load_issue('test-storage')
        assert loaded_issue['id'] == 'test-storage'
        assert loaded_issue['title'] == 'Test Storage Issue'
        
        # Test list_issues includes our test issue
        issues = storage.list_issues()
        test_issue_found = any(issue['id'] == 'test-storage' for issue in issues)
        assert test_issue_found
        
        # Test delete_issue
        storage.delete_issue('test-storage')
        
        # Verify it's gone
        with pytest.raises(storage.StorageError):
            storage.load_issue('test-storage')
    
    def test_schema_validation(self):
        """Test that schema validation is working"""
        # Test valid data passes through
        valid_data = {
            'title': 'Test issue',
            'description': 'Test description',
            'severity': 'high',
            'tags': ['test']
        }
        
        result = schema.validate_or_default(valid_data)
        assert result['title'] == 'Test issue'
        assert result['severity'] == 'high'
        assert result['schema_version'] == 'v1'
        assert 'id' in result
        assert 'created_at' in result
    
    def test_model_processing(self):
        """Test that model processing is working"""
        # Test with critical keywords - should detect high severity
        result = model.process_description("System crash on startup")
        assert result['severity'] in ['critical', 'high']  # AI should detect severity
        assert result['title']  # Should generate a title
        assert isinstance(result['tags'], list)  # Should generate tags
        
        # Test with UI keywords - should detect UI-related tags or generate appropriate response
        result = model.process_description("UI interface looks wrong")
        # Just verify we get a valid response structure
        assert result['title']
        assert result['severity'] in ['low', 'medium', 'high', 'critical']
        assert isinstance(result['tags'], list)
        
        # Test title generation - should generate some kind of title
        result = model.process_description("This is a long description. It has multiple sentences.")
        assert result['title']  # Should generate a title (any title)
        assert len(result['title']) <= 120  # Should respect length limit
        assert result['description'] == "This is a long description. It has multiple sentences."  # Should preserve original
    
    def test_config_management(self):
        """Test that configuration management is working"""
        default_config = config.load_config()
        assert default_config['model'] == 'gpt-4'
        assert default_config['enum_mode'] == 'auto'


@pytest.mark.unit
class TestValidationEdgeCases:
    """Test edge cases for validation logic"""
    
    def test_empty_title_raises_error(self):
        """Test that empty title raises ValidationError"""
        with pytest.raises(schema.ValidationError):
            schema.validate_or_default({'title': ''})
    
    def test_long_title_truncated(self):
        """Test that long titles are properly truncated"""
        long_title = "a" * 150
        result = schema.validate_or_default({'title': long_title})
        assert len(result['title']) <= 120
        assert result['title'].endswith('...')
    
    def test_invalid_severity_defaults(self):
        """Test that invalid severity values default to medium"""
        result = schema.validate_or_default({
            'title': 'Test',
            'severity': 'invalid'
        })
        assert result['severity'] == 'medium'
    
    def test_empty_description_handling(self):
        """Test that model rejects empty descriptions"""
        with pytest.raises(model.ModelError):
            model.process_description("")
        
        with pytest.raises(model.ModelError):
            model.process_description("   ") 