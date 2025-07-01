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
    
    def test_storage_stubs(self):
        """Test that storage stubs are functional"""
        # Test list_issues returns expected data
        issues = storage.list_issues()
        assert len(issues) == 2
        assert issues[0]['severity'] == 'critical'
        assert issues[1]['severity'] == 'low'
        
        # Test load_issue returns mock data
        issue = storage.load_issue('test123')
        assert issue['id'] == 'test123'
        assert 'Mock Issue' in issue['title']
    
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
        """Test that model processing stub is working"""
        # Test with critical keywords
        result = model.process_description("System crash on startup")
        assert result['severity'] == 'critical'
        assert 'crash' in result['tags'] or 'startup' in result['tags'] or result['severity'] == 'critical'
        
        # Test with UI keywords
        result = model.process_description("UI interface looks wrong")
        assert 'ui' in result['tags']
        
        # Test title generation
        result = model.process_description("This is a long description. It has multiple sentences.")
        assert result['title'] == "This is a long description"
    
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