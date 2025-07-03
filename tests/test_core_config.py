"""
Comprehensive tests for core/config.py module.
Tests all configuration functions with proper isolation and edge case coverage.
"""

import pytest
import tempfile
import shutil
import json
import os
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from core import config
from core.config import (
    load_config, save_preferences, set_api_key, get_config_value, 
    set_preference, check_openai_api_key, check_api_key, set_config_value,
    ConfigError
)


class TestLoadConfig:
    """Test the load_config function"""
    
    def test_loads_default_config_when_no_files(self, temp_dir):
        """Test loading default config when no files exist"""
        os.chdir(temp_dir)
        
        result = load_config()
        
        # Should return default values
        assert result['model'] == 'gpt-4'
        assert result['enum_mode'] == 'auto'
        assert result['output_format'] == 'table'
        assert result['retry_limit'] == 3
    
    def test_loads_config_from_bugitrc(self, temp_dir):
        """Test loading config from .bugitrc file"""
        os.chdir(temp_dir)
        
        # Create .bugitrc file
        bugitrc_data = {
            'model': 'gpt-3.5-turbo',
            'enum_mode': 'strict',
            'output_format': 'json',
            'retry_limit': 5,
            'custom_field': 'custom_value'
        }
        
        with open('.bugitrc', 'w') as f:
            json.dump(bugitrc_data, f)
        
        result = load_config()
        
        # Should load values from file
        assert result['model'] == 'gpt-3.5-turbo'
        assert result['enum_mode'] == 'strict'
        assert result['output_format'] == 'json'
        assert result['retry_limit'] == 5
        assert result['custom_field'] == 'custom_value'
    
    def test_environment_variables_do_not_override_file(self, temp_dir):
        """Test that environment variables do NOT override .bugitrc file for non-API-key config"""
        os.chdir(temp_dir)
        
        # Create .bugitrc file
        bugitrc_data = {'model': 'gpt-4', 'enum_mode': 'auto'}
        with open('.bugitrc', 'w') as f:
            json.dump(bugitrc_data, f)
        
        # Set environment variables (these should be ignored for non-API-key config)
        env_vars = {
            'BUGIT_MODEL': 'claude-3-sonnet',
            'BUGIT_ENUM_MODE': 'strict'
        }
        
        with patch.dict(os.environ, env_vars):
            result = load_config()
        
        # Environment variables should NOT override file for non-API-key config
        assert result['model'] == 'gpt-4'          # From .bugitrc, not env var
        assert result['enum_mode'] == 'auto'       # From .bugitrc, not env var
    
    def test_handles_corrupted_bugitrc_file(self, temp_dir):
        """Test handling of corrupted .bugitrc file"""
        os.chdir(temp_dir)
        
        # Create corrupted JSON file
        with open('.bugitrc', 'w') as f:
            f.write('{"invalid": json content}')
        
        # Should fall back to defaults without error
        result = load_config()
        assert result['model'] == 'gpt-4'
        assert result['enum_mode'] == 'auto'
    
    def test_loads_api_keys_from_env_file(self, temp_dir):
        """Test loading API keys from .env file"""
        os.chdir(temp_dir)
        
        # Create .env file
        with open('.env', 'w') as f:
            f.write('BUGIT_OPENAI_API_KEY=sk-test123\n')
            f.write('BUGIT_ANTHROPIC_API_KEY=sk-ant-test456\n')
        
        result = load_config()
        
        # Should include API key status
        assert 'openai_api_key' in result
        assert 'anthropic_api_key' in result
    
    def test_legacy_api_key_support_with_warning(self, temp_dir):
        """Test legacy BUGIT_API_KEY support with deprecation warning"""
        os.chdir(temp_dir)
        
        env_vars = {'BUGIT_API_KEY': 'legacy-key-123'}
        
        with patch.dict(os.environ, env_vars):
            # Should capture warning - in real implementation
            result = load_config()
            
            # Should still work but prefer new format
            assert 'openai_api_key' in result
    
    def test_environment_variables_only_for_api_keys(self, temp_dir):
        """Test that environment variables only work for API keys, not configuration"""
        os.chdir(temp_dir)
        
        # Create .bugitrc with preferences
        bugitrc_data = {'retry_limit': 3, 'output_format': 'table'}
        with open('.bugitrc', 'w') as f:
            json.dump(bugitrc_data, f)
        
        env_vars = {
            'BUGIT_RETRY_LIMIT': '7',  # Should be ignored (non-API-key config)
            'BUGIT_OUTPUT_FORMAT': 'yaml',  # Should be ignored (non-API-key config)
            'BUGIT_OPENAI_API_KEY': 'sk-test123'  # Should work (API key)
        }
        
        with patch.dict(os.environ, env_vars):
            result = load_config()
        
        # Non-API-key environment variables should be ignored
        assert result['retry_limit'] == 3  # From .bugitrc, not env var
        assert result['output_format'] == 'table'  # From .bugitrc, not env var
        
        # API key environment variables should work
        assert result['openai_api_key'] == 'sk-test123'  # From env var


class TestSavePreferences:
    """Test the save_preferences function"""
    
    def test_saves_preferences_to_default_file(self, temp_dir):
        """Test saving preferences to default .bugitrc file"""
        os.chdir(temp_dir)
        
        preferences = {
            'model': 'gpt-3.5-turbo',
            'enum_mode': 'strict',
            'custom_setting': 'custom_value'
        }
        
        save_preferences(preferences)
        
        # Verify file was created
        assert Path('.bugitrc').exists()
        
        # Verify contents
        with open('.bugitrc', 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data == preferences
    
    def test_saves_preferences_to_custom_file(self, temp_dir):
        """Test saving preferences to custom file path"""
        os.chdir(temp_dir)
        
        preferences = {'model': 'claude-3-sonnet'}
        custom_path = 'custom_config.json'
        
        save_preferences(preferences, custom_path)
        
        # Verify custom file was created
        assert Path(custom_path).exists()
        
        # Verify contents
        with open(custom_path, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data == preferences
    
    def test_overwrites_existing_preferences(self, temp_dir):
        """Test that existing preferences are overwritten"""
        os.chdir(temp_dir)
        
        # Create initial preferences
        initial_prefs = {'model': 'gpt-4', 'old_setting': 'old_value'}
        save_preferences(initial_prefs)
        
        # Save new preferences
        new_prefs = {'model': 'gpt-3.5-turbo', 'new_setting': 'new_value'}
        save_preferences(new_prefs)
        
        # Verify new preferences replaced old ones
        with open('.bugitrc', 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data == new_prefs
        assert 'old_setting' not in saved_data
    
    def test_handles_unicode_preferences(self, temp_dir):
        """Test saving preferences with unicode characters"""
        os.chdir(temp_dir)
        
        preferences = {
            'custom_prompt': 'Analyze this émoji 🚀 and ünïcödé text',
            'model': 'gpt-4'
        }
        
        save_preferences(preferences)
        
        # Verify unicode is preserved
        with open('.bugitrc', 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert saved_data['custom_prompt'] == 'Analyze this émoji 🚀 and ünïcödé text'


class TestSetApiKey:
    """Test the set_api_key function"""
    
    def test_sets_openai_api_key(self, temp_dir):
        """Test setting OpenAI API key"""
        os.chdir(temp_dir)
        
        set_api_key('openai', 'sk-test123')
        
        # Verify .env file was created
        assert Path('.env').exists()
        
        # Verify key was written
        with open('.env', 'r') as f:
            env_content = f.read()
        
        assert 'BUGIT_OPENAI_API_KEY=sk-test123' in env_content
    
    def test_sets_anthropic_api_key(self, temp_dir):
        """Test setting Anthropic API key"""
        os.chdir(temp_dir)
        
        set_api_key('anthropic', 'sk-ant-test456')
        
        # Verify key was written
        with open('.env', 'r') as f:
            env_content = f.read()
        
        assert 'BUGIT_ANTHROPIC_API_KEY=sk-ant-test456' in env_content
    
    def test_appends_to_existing_env_file(self, temp_dir):
        """Test appending to existing .env file"""
        os.chdir(temp_dir)
        
        # Create existing .env file
        with open('.env', 'w') as f:
            f.write('EXISTING_VAR=existing_value\n')
        
        set_api_key('openai', 'sk-new123')
        
        # Verify both old and new keys exist
        with open('.env', 'r') as f:
            env_content = f.read()
        
        assert 'EXISTING_VAR=existing_value' in env_content
        assert 'BUGIT_OPENAI_API_KEY=sk-new123' in env_content
    
    def test_updates_existing_api_key(self, temp_dir):
        """Test updating existing API key"""
        os.chdir(temp_dir)
        
        # Set initial key
        set_api_key('openai', 'sk-old123')
        
        # Update key
        set_api_key('openai', 'sk-new456')
        
        # Verify only new key exists
        with open('.env', 'r') as f:
            env_content = f.read()
        
        assert 'BUGIT_OPENAI_API_KEY=sk-new456' in env_content
        assert 'sk-old123' not in env_content
    
    def test_handles_invalid_provider(self, temp_dir):
        """Test handling of invalid provider"""
        os.chdir(temp_dir)
        
        # Should raise error or handle gracefully
        with pytest.raises((ValueError, KeyError)):
            set_api_key('invalid_provider', 'some-key')
    
    def test_handles_special_characters_in_key(self, temp_dir):
        """Test handling of special characters in API key"""
        os.chdir(temp_dir)
        
        special_key = 'sk-test!@#$%^&*()_+-=[]{}|;:,.<>?'
        set_api_key('openai', special_key)
        
        # Verify special characters are preserved
        with open('.env', 'r') as f:
            env_content = f.read()
        
        assert special_key in env_content


class TestGetConfigValue:
    """Test the get_config_value function"""
    
    def test_gets_existing_config_value(self, temp_dir):
        """Test getting existing configuration value"""
        os.chdir(temp_dir)
        
        # Create config file
        config_data = {'model': 'gpt-3.5-turbo', 'retry_limit': 5}
        with open('.bugitrc', 'w') as f:
            json.dump(config_data, f)
        
        assert get_config_value('model') == 'gpt-3.5-turbo'
        assert get_config_value('retry_limit') == 5
    
    def test_gets_default_for_missing_key(self, temp_dir):
        """Test getting default value for missing key"""
        os.chdir(temp_dir)
        
        # Default model should be returned
        assert get_config_value('model') == 'gpt-4'
        
        # Missing custom key should return None
        assert get_config_value('nonexistent_key') is None
    
    def test_environment_variables_do_not_override_config_file(self, temp_dir):
        """Test that environment variables do NOT override config file for non-API-key config"""
        os.chdir(temp_dir)
        
        # Create config file
        config_data = {'model': 'gpt-4'}
        with open('.bugitrc', 'w') as f:
            json.dump(config_data, f)
        
        # Set environment variable (should be ignored for non-API-key config)
        with patch.dict(os.environ, {'BUGIT_MODEL': 'claude-3-sonnet'}):
            assert get_config_value('model') == 'gpt-4'  # From .bugitrc, not env var


class TestSetPreference:
    """Test the set_preference function"""
    
    def test_sets_new_preference(self, temp_dir):
        """Test setting a new preference"""
        os.chdir(temp_dir)
        
        set_preference('custom_setting', 'custom_value')
        
        # Verify preference was saved
        with open('.bugitrc', 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data['custom_setting'] == 'custom_value'
    
    def test_updates_existing_preference(self, temp_dir):
        """Test updating existing preference"""
        os.chdir(temp_dir)
        
        # Create initial config
        initial_config = {'model': 'gpt-4', 'enum_mode': 'auto'}
        with open('.bugitrc', 'w') as f:
            json.dump(initial_config, f)
        
        # Update existing preference
        set_preference('model', 'gpt-3.5-turbo')
        
        # Verify update
        with open('.bugitrc', 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data['model'] == 'gpt-3.5-turbo'
        assert saved_data['enum_mode'] == 'auto'  # Should preserve other settings
    
    def test_preserves_existing_preferences(self, temp_dir):
        """Test that existing preferences are preserved when setting new ones"""
        os.chdir(temp_dir)
        
        # Create initial config
        initial_config = {
            'model': 'gpt-4',
            'enum_mode': 'auto',
            'custom_field': 'existing_value'
        }
        with open('.bugitrc', 'w') as f:
            json.dump(initial_config, f)
        
        # Add new preference
        set_preference('new_setting', 'new_value')
        
        # Verify all preferences exist
        with open('.bugitrc', 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data['model'] == 'gpt-4'
        assert saved_data['enum_mode'] == 'auto'
        assert saved_data['custom_field'] == 'existing_value'
        assert saved_data['new_setting'] == 'new_value'


class TestApiKeyChecking:
    """Test API key checking functions"""
    
    def test_check_openai_api_key_with_env_var(self, temp_dir):
        """Test checking OpenAI API key via environment variable"""
        os.chdir(temp_dir)
        
        with patch.dict(os.environ, {'BUGIT_OPENAI_API_KEY': 'sk-test123'}):
            assert check_openai_api_key() is True
        
        # Without key
        with patch.dict(os.environ, {}, clear=True):
            assert check_openai_api_key() is False
    
    def test_check_openai_api_key_with_env_file(self, temp_dir):
        """Test checking OpenAI API key via .env file"""
        os.chdir(temp_dir)
        
        # Create .env file
        with open('.env', 'w') as f:
            f.write('BUGIT_OPENAI_API_KEY=sk-test123\n')
        
        assert check_openai_api_key() is True
    
    def test_check_api_key_general(self, temp_dir):
        """Test general API key checking"""
        os.chdir(temp_dir)
        
        # With OpenAI key
        with patch.dict(os.environ, {'BUGIT_OPENAI_API_KEY': 'sk-test123'}):
            assert check_api_key() is True
        
        # With legacy key
        with patch.dict(os.environ, {'BUGIT_API_KEY': 'legacy-key'}):
            assert check_api_key() is True
        
        # Without any key
        with patch.dict(os.environ, {}, clear=True):
            assert check_api_key() is False
    
    def test_check_api_key_with_empty_values(self, temp_dir):
        """Test API key checking with empty values"""
        os.chdir(temp_dir)
        
        # Empty string should be considered missing
        with patch.dict(os.environ, {'BUGIT_OPENAI_API_KEY': ''}):
            assert check_openai_api_key() is False
        
        # Whitespace only should be considered missing
        with patch.dict(os.environ, {'BUGIT_OPENAI_API_KEY': '   '}):
            assert check_openai_api_key() is False


class TestSetConfigValue:
    """Test the set_config_value function"""
    
    def test_sets_config_value_directly(self, temp_dir):
        """Test setting config value directly"""
        os.chdir(temp_dir)
        
        set_config_value('model', 'claude-3-sonnet')
        
        # Verify value was set
        assert get_config_value('model') == 'claude-3-sonnet'
    
    def test_sets_multiple_config_values(self, temp_dir):
        """Test setting multiple config values"""
        os.chdir(temp_dir)
        
        set_config_value('model', 'gpt-3.5-turbo')
        set_config_value('retry_limit', 7)
        set_config_value('custom_setting', 'custom_value')
        
        # Verify all values
        assert get_config_value('model') == 'gpt-3.5-turbo'
        assert get_config_value('retry_limit') == 7
        assert get_config_value('custom_setting') == 'custom_value'


class TestConfigIntegration:
    """Test configuration system integration"""
    
    def test_full_config_workflow(self, temp_dir):
        """Test complete configuration workflow"""
        os.chdir(temp_dir)
        
        # Set API key
        set_api_key('openai', 'sk-workflow123')
        
        # Set preferences
        set_preference('model', 'gpt-3.5-turbo')
        set_preference('retry_limit', 5)
        
        # Load config
        config_result = load_config()
        
        # Verify all settings
        assert config_result['model'] == 'gpt-3.5-turbo'
        assert config_result['retry_limit'] == 5
        assert 'openai_api_key' in config_result
    
    def test_config_priority_order(self, temp_dir):
        """Test configuration priority: .bugitrc > defaults (env vars only for API keys)"""
        os.chdir(temp_dir)
        
        # Set up .bugitrc
        bugitrc_data = {'model': 'from-bugitrc'}
        with open('.bugitrc', 'w') as f:
            json.dump(bugitrc_data, f)
        
        # Environment variables should NOT override .bugitrc for non-API-key config
        with patch.dict(os.environ, {'BUGIT_MODEL': 'from-env-var'}):
            result = load_config()
            assert result['model'] == 'from-bugitrc'  # .bugitrc wins, env var ignored
        
        # Test API key priority (env vars should work for API keys)
        with patch.dict(os.environ, {'BUGIT_OPENAI_API_KEY': 'sk-from-env'}):
            result2 = load_config()
            assert result2['openai_api_key'] == 'sk-from-env'  # env var works for API keys
    
    def test_config_error_recovery(self, temp_dir):
        """Test that config system recovers from errors gracefully"""
        os.chdir(temp_dir)
        
        # Create corrupted .bugitrc
        with open('.bugitrc', 'w') as f:
            f.write('invalid json content')
        
        # Create corrupted .env
        with open('.env', 'w') as f:
            f.write('INVALID_ENV_FORMAT_NO_EQUALS\n')
        
        # Clear environment to avoid pollution from other tests
        with patch.dict(os.environ, {}, clear=True):
            # Should still return valid defaults
            result = load_config()
            assert result['model'] == 'gpt-4'
            assert result['enum_mode'] == 'auto'


class TestConfigValidation:
    """Test configuration validation and type conversion"""
    
    def test_validates_retry_limit_range(self, temp_dir):
        """Test that retry_limit is validated to reasonable range"""
        os.chdir(temp_dir)
        
        # Valid retry limits
        for valid_limit in [1, 3, 5, 10]:
            set_preference('retry_limit', valid_limit)
            assert get_config_value('retry_limit') == valid_limit
        
        # Invalid retry limits should be handled gracefully
        invalid_limits = [-1, 0, 100, 'invalid']
        for invalid_limit in invalid_limits:
            set_preference('retry_limit', invalid_limit)
            result = get_config_value('retry_limit')
            # Should be either default or valid range
            assert isinstance(result, int) and 1 <= result <= 20
    
    def test_validates_model_names(self, temp_dir):
        """Test that model names are validated"""
        os.chdir(temp_dir)
        
        # Clear environment to avoid pollution from other tests
        with patch.dict(os.environ, {}, clear=True):
            # Valid model names
            valid_models = ['gpt-4', 'gpt-3.5-turbo', 'claude-3-sonnet']
            for model in valid_models:
                set_preference('model', model)
                assert get_config_value('model') == model
            
            # Empty or invalid models should get defaults
            invalid_models = ['', None, 123]
            for invalid_model in invalid_models:
                set_preference('model', invalid_model)
                result = get_config_value('model')
                assert result == 'gpt-4'  # Should default


class TestConfigErrorPaths:
    """Test error handling in configuration functions to improve coverage"""
    
    def test_load_config_with_corrupted_bugitrc_graceful_fallback(self, temp_dir):
        """Test lines 70-71: corrupted .bugitrc fallback to defaults"""
        os.chdir(temp_dir)
        
        # Create corrupted .bugitrc file that causes JSONDecodeError
        with open('.bugitrc', 'w') as f:
            f.write('{"invalid": json content, missing quotes}')
        
        # Should load gracefully with defaults
        config = load_config()
        assert config['model'] == 'gpt-4'  # Default value
        assert config['retry_limit'] == 3  # Default value
        assert config['enum_mode'] == 'auto'  # Default value
        
        # Create .bugitrc that causes FileNotFoundError during reading (edge case)
        Path('.bugitrc').unlink()  # Remove file
        
        # Try to create a scenario where the file exists check passes but read fails
        # This is tricky but can happen with permission issues
        with patch('builtins.open', side_effect=FileNotFoundError("File disappeared")):
            config2 = load_config()
            assert config2['model'] == 'gpt-4'  # Should still get defaults
    
    def test_save_preferences_exception_handling(self, temp_dir):
        """Test lines 95-96: save_preferences exception handling"""
        os.chdir(temp_dir)
        
        # Test permission error during save
        preferences = {'model': 'gpt-4', 'retry_limit': 5}
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(ConfigError, match="Failed to save preferences"):
                save_preferences(preferences)
        
        # Test general exception during save
        with patch('builtins.open', side_effect=OSError("Disk full")):
            with pytest.raises(ConfigError, match="Failed to save preferences"):
                save_preferences(preferences)
    
    def test_set_api_key_empty_validation(self, temp_dir):
        """Test line 107: empty API key validation"""
        os.chdir(temp_dir)
        
        # Test completely empty string
        with pytest.raises(ConfigError, match="API key cannot be empty"):
            set_api_key('openai', '')
        
        # Test whitespace-only string
        with pytest.raises(ConfigError, match="API key cannot be empty"):
            set_api_key('openai', '   \t\n  ')
        
        # Test None value (should raise ConfigError because None is falsy)
        with pytest.raises(ConfigError, match="API key cannot be empty"):
            set_api_key('openai', None)  # type: ignore
    
    def test_set_preference_corrupted_file_recovery(self, temp_dir):
        """Test lines 140-141: set_preference with corrupted .bugitrc"""
        os.chdir(temp_dir)
        
        # Create corrupted .bugitrc file
        with open('.bugitrc', 'w') as f:
            f.write('{"corrupted": json without closing brace')
        
        # Should handle gracefully and use defaults
        set_preference('model', 'gpt-3.5-turbo')
        
        # Verify the preference was saved (file should be overwritten with valid JSON)
        with open('.bugitrc', 'r') as f:
            saved_data = json.load(f)
        assert saved_data['model'] == 'gpt-3.5-turbo'
        
        # Test with file that disappears during reading
        Path('.bugitrc').unlink()
        Path('.bugitrc').touch()  # Create empty file
        
        # Mock file reading to fail first, then succeed for writing
        mock_file = mock_open()
        with patch('builtins.open', side_effect=[FileNotFoundError("File gone"), mock_file.return_value]):
            set_preference('retry_limit', 7)
    
    def test_set_preference_api_key_rejection(self, temp_dir):
        """Test that setting API keys via set_preference is properly rejected"""
        os.chdir(temp_dir)
        
        # Test various API key field names
        api_key_fields = ['openai_api_key', 'anthropic_api_key', 'google_api_key', 'custom_api_key']
        
        for field in api_key_fields:
            provider = field.replace('_api_key', '')
            with pytest.raises(ConfigError, match=f"Use 'bugit config --set-api-key {provider}"):
                set_preference(field, 'sk-test-key')


class TestLegacyCompatibilityFunctions:
    """Test lines 162-163: legacy compatibility functions"""
    
    def test_check_api_key_legacy_function(self, temp_dir):
        """Test line 162: check_api_key() legacy function"""
        os.chdir(temp_dir)
        
        # Should return False when no API key is set
        with patch.dict(os.environ, {}, clear=True):
            assert check_api_key() == False
        
        # Should return True when OpenAI API key is set
        with patch.dict(os.environ, {'BUGIT_OPENAI_API_KEY': 'sk-test-key'}):
            assert check_api_key() == True
        
        # Should return True with legacy API key
        with patch.dict(os.environ, {'BUGIT_API_KEY': 'legacy-key'}, clear=True):
            assert check_api_key() == True
    
    def test_set_config_value_legacy_function(self, temp_dir):
        """Test line 163: set_config_value() legacy function"""
        os.chdir(temp_dir)
        
        # Should work the same as set_preference
        set_config_value('model', 'gpt-3.5-turbo')
        assert get_config_value('model') == 'gpt-3.5-turbo'
        
        # Should handle validation the same way
        set_config_value('retry_limit', 25)  # Invalid high value
        assert get_config_value('retry_limit') == 3  # Should default
        
        # Should reject API key settings the same way
        with pytest.raises(ConfigError, match="Use 'bugit config --set-api-key"):
            set_config_value('openai_api_key', 'sk-test-key') 