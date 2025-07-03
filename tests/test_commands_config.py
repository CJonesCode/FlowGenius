"""
Comprehensive tests for commands/config.py module.
Tests all config command functionality with proper isolation and edge case coverage.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from typer.testing import CliRunner
import typer

from commands.config import config
from core.config import ConfigError


class TestConfigCommand:
    """Test the config command functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()
        self.mock_config_data = {
            'openai_api_key': 'sk-test123456789',
            'model': 'gpt-4',
            'enum_mode': 'auto',
            'output_format': 'table',
            'retry_limit': 3,
            'default_severity': 'medium'
        }

    @patch('commands.config.config_core.set_api_key')
    def test_set_api_key_success(self, mock_set_api_key):
        """Test setting API key successfully"""
        mock_set_api_key.return_value = None
        
        # Create a Typer app for testing
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--set-api-key', 'openai', 'sk-newkey123'])
        
        assert result.exit_code == 0
        assert 'API key for openai set successfully' in result.stdout
        assert 'Saved to .env file' in result.stdout
        mock_set_api_key.assert_called_once_with('openai', 'sk-newkey123')

    def test_set_api_key_missing_value(self):
        """Test setting API key without providing value"""
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--set-api-key', 'openai'])
        
        assert result.exit_code == 1
        # Check both stdout and stderr for error messages
        error_output = result.stdout + result.stderr
        assert 'API key value is required' in error_output

    @patch('commands.config.config_core.set_api_key')
    def test_set_api_key_config_error(self, mock_set_api_key):
        """Test handling ConfigError when setting API key"""
        mock_set_api_key.side_effect = ConfigError("Invalid provider")
        
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--set-api-key', 'invalid', 'key'])
        
        assert result.exit_code == 1
        # Check both stdout and stderr for error messages
        error_output = result.stdout + result.stderr
        assert 'Error: Invalid provider' in error_output

    @patch('commands.config.config_core.load_config')
    def test_import_preferences_success(self, mock_load_config, tmp_path):
        """Test importing preferences from file"""
        mock_load_config.return_value = self.mock_config_data
        
        # Create test file
        import_file = tmp_path / "test_config.json"
        test_prefs = {'model': 'gpt-3.5-turbo', 'retry_limit': 5}
        import_file.write_text(json.dumps(test_prefs))
        
        with patch('commands.config.config_core.save_preferences') as mock_save:
            app = typer.Typer()
            app.command()(config)
            
            result = self.runner.invoke(app, ['--import', str(import_file)])
            
            assert result.exit_code == 0
            assert f'Preferences imported from {import_file}' in result.stdout
            mock_save.assert_called_once_with(test_prefs)

    def test_import_preferences_file_not_found(self):
        """Test importing from non-existent file"""
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--import', '/nonexistent/file.json'])
        
        assert result.exit_code == 1
        # Check both stdout and stderr for error messages
        error_output = result.stdout + result.stderr
        assert 'File not found' in error_output

    @patch('commands.config.config_core.load_config')
    def test_export_preferences_success(self, mock_load_config, tmp_path):
        """Test exporting preferences to file"""
        mock_load_config.return_value = self.mock_config_data
        
        export_file = tmp_path / "export_config.json"
        
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--export', str(export_file)])
        
        assert result.exit_code == 0
        assert f'Preferences exported to {export_file}' in result.stdout
        
        # Verify file contents (should exclude API keys)
        with open(export_file, 'r') as f:
            exported_data = json.load(f)
        
        assert 'openai_api_key' not in exported_data
        assert exported_data['model'] == 'gpt-4'

    @patch('commands.config.config_core.load_config')
    def test_get_config_value_json(self, mock_load_config):
        """Test getting specific config value in JSON format"""
        mock_load_config.return_value = self.mock_config_data
        
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--get', 'model'])
        
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output['key'] == 'model'
        assert output['value'] == 'gpt-4'
        assert output['set'] is True

    @patch('commands.config.config_core.load_config')
    def test_get_config_value_pretty(self, mock_load_config):
        """Test getting specific config value in pretty format"""
        mock_load_config.return_value = self.mock_config_data
        
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--get', 'model', '--pretty'])
        
        assert result.exit_code == 0
        assert 'model: gpt-4' in result.stdout

    @patch('commands.config.config_core.load_config')
    def test_get_api_key_masked(self, mock_load_config):
        """Test getting API key returns masked value"""
        mock_load_config.return_value = self.mock_config_data
        
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--get', 'openai_api_key'])
        
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output['key'] == 'openai_api_key'
        assert output['value'].startswith('sk-test1')
        assert output['value'].endswith('***')

    @patch('commands.config.config_core.load_config')
    @patch('pathlib.Path.exists')
    def test_get_api_key_pretty_with_env_file(self, mock_exists, mock_load_config):
        """Test getting API key in pretty format shows source"""
        mock_load_config.return_value = self.mock_config_data
        mock_exists.return_value = True  # .env file exists
        
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--get', 'openai_api_key', '--pretty'])
        
        assert result.exit_code == 0
        assert 'sk-test1***' in result.stdout
        assert '(.env file)' in result.stdout

    @patch('commands.config.config_core.load_config')
    def test_get_api_key_not_set(self, mock_load_config):
        """Test getting unset API key"""
        config_without_key = self.mock_config_data.copy()
        config_without_key['openai_api_key'] = None
        mock_load_config.return_value = config_without_key
        
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--get', 'openai_api_key', '--pretty'])
        
        assert result.exit_code == 0
        assert 'openai_api_key: Not set' in result.stdout
        assert 'Set with: bugit config --set-api-key openai' in result.stdout

    @patch('commands.config.config_core.load_config')
    def test_get_legacy_api_key_request(self, mock_load_config):
        """Test requesting legacy 'api_key' redirects to 'openai_api_key'"""
        mock_load_config.return_value = self.mock_config_data
        
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--get', 'api_key', '--pretty'])
        
        assert result.exit_code == 0
        assert "'api_key' is now 'openai_api_key'" in result.stdout
        assert 'sk-test1***' in result.stdout

    @patch('commands.config.config_core.load_config')
    def test_get_nonexistent_key_json(self, mock_load_config):
        """Test getting non-existent key in JSON format"""
        mock_load_config.return_value = self.mock_config_data
        
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--get', 'nonexistent'])
        
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output['key'] == 'nonexistent'
        assert output['value'] is None
        assert output['set'] is False
        assert output['error'] == 'Key not found'

    @patch('commands.config.config_core.load_config')
    def test_get_nonexistent_key_pretty(self, mock_load_config):
        """Test getting non-existent key in pretty format"""
        mock_load_config.return_value = self.mock_config_data
        
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--get', 'nonexistent', '--pretty'])
        
        assert result.exit_code == 0
        assert "Config key 'nonexistent' not found" in result.stdout

    @patch('commands.config.config_core.set_preference')
    def test_set_preference_success(self, mock_set_preference):
        """Test setting preference successfully"""
        mock_set_preference.return_value = None
        
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--set', 'model', 'gpt-3.5-turbo'])
        
        assert result.exit_code == 0
        assert 'Set model: gpt-3.5-turbo' in result.stdout
        mock_set_preference.assert_called_once_with('model', 'gpt-3.5-turbo')

    def test_set_preference_missing_value(self):
        """Test setting preference without value"""
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--set', 'model'])
        
        assert result.exit_code == 1
        # Check both stdout and stderr for error messages
        error_output = result.stdout + result.stderr
        assert 'Value is required when using --set' in error_output

    def test_set_legacy_api_key_attempt(self):
        """Test attempting to set API key via --set (legacy behavior)"""
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--set', 'api_key', 'sk-test'])
        
        assert result.exit_code == 1
        # Check both stdout and stderr for error messages
        error_output = result.stdout + result.stderr
        assert "Use '--set-api-key openai" in error_output

    @patch('commands.config.config_core.set_preference')
    def test_set_preference_config_error(self, mock_set_preference):
        """Test handling ConfigError when setting preference"""
        mock_set_preference.side_effect = ConfigError("Invalid preference")
        
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--set', 'invalid_key', 'value'])
        
        assert result.exit_code == 1
        # Check both stdout and stderr for error messages
        error_output = result.stdout + result.stderr
        assert 'Error: Invalid preference' in error_output

    @patch('commands.config.config_core.load_config')
    @patch('commands.config.config_core.check_openai_api_key')
    @patch('pathlib.Path.exists')
    def test_show_all_config_pretty(self, mock_path_exists, mock_check_key, mock_load_config):
        """Test showing all config in pretty format"""
        mock_load_config.return_value = self.mock_config_data
        mock_check_key.return_value = True
        mock_path_exists.return_value = True  # Both .env and .bugitrc exist
        
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--pretty'])
        
        assert result.exit_code == 0
        assert 'Current configuration:' in result.stdout
        assert 'openai_api_key: sk-test1***' in result.stdout
        assert '(.env file)' in result.stdout
        assert 'model: gpt-4' in result.stdout
        assert '(from .bugitrc)' in result.stdout
        assert 'Helpful commands:' in result.stdout

    @patch('commands.config.config_core.load_config')
    @patch('commands.config.config_core.check_openai_api_key')
    def test_show_all_config_pretty_no_api_key(self, mock_check_key, mock_load_config):
        """Test showing all config in pretty format when API key not set"""
        config_no_key = self.mock_config_data.copy()
        config_no_key['openai_api_key'] = None
        mock_load_config.return_value = config_no_key
        mock_check_key.return_value = False
        
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, ['--pretty'])
        
        assert result.exit_code == 0
        assert 'openai_api_key: Not set' in result.stdout
        assert 'Set with: bugit config --set-api-key openai' in result.stdout

    @patch('commands.config.config_core.load_config')
    def test_show_all_config_pretty_api_key_from_env(self, mock_load_config):
        """Test showing config with API key from environment (only API keys use env vars)"""
        config_with_env_api_key = self.mock_config_data.copy()
        config_with_env_api_key['openai_api_key'] = 'sk-env123456789'
        mock_load_config.return_value = config_with_env_api_key
        
        with patch('commands.config.config_core.check_openai_api_key', return_value=True):
            with patch.dict(os.environ, {'BUGIT_OPENAI_API_KEY': 'sk-env123456789'}):
                app = typer.Typer()
                app.command()(config)
                
                result = self.runner.invoke(app, ['--pretty'])
                
                assert result.exit_code == 0
                assert 'sk-env12***' in result.stdout  # Should show masked API key from env

    @patch('commands.config.config_core.load_config')
    def test_show_all_config_json(self, mock_load_config):
        """Test showing all config in JSON format (default)"""
        mock_load_config.return_value = self.mock_config_data
        
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, [])
        
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert 'model' in output
        assert output['model'] == 'gpt-4'
        # API key should be masked in JSON output
        assert output['openai_api_key'].startswith('sk-test1')
        assert output['openai_api_key'].endswith('***')

    @patch('commands.config.config_core.load_config')
    def test_show_all_config_json_no_api_key(self, mock_load_config):
        """Test showing all config in JSON format when API key is None"""
        config_no_key = self.mock_config_data.copy()
        config_no_key['openai_api_key'] = None
        mock_load_config.return_value = config_no_key
        
        app = typer.Typer()
        app.command()(config)
        
        result = self.runner.invoke(app, [])
        
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output['openai_api_key'] is None

    def test_unexpected_error_handling(self):
        """Test handling of unexpected errors"""
        with patch('commands.config.config_core.load_config') as mock_load:
            mock_load.side_effect = Exception("Unexpected error")
            
            app = typer.Typer()
            app.command()(config)
            
            result = self.runner.invoke(app, ['--get', 'model'])
            
            assert result.exit_code == 1
            # Check both stdout and stderr for error messages
            error_output = result.stdout + result.stderr
            assert 'Error managing config: Unexpected error' in error_output


class TestConfigCommandIntegration:
    """Integration tests for config command with file operations"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()

    def test_import_export_round_trip(self, tmp_path):
        """Test importing and exporting preferences"""
        # Create test preferences file
        test_prefs = {
            'model': 'gpt-3.5-turbo',
            'retry_limit': 5,
            'output_format': 'json'
        }
        import_file = tmp_path / "import.json"
        import_file.write_text(json.dumps(test_prefs))
        
        export_file = tmp_path / "export.json"
        
        # Mock the config operations
        with patch('commands.config.config_core.save_preferences') as mock_save, \
             patch('commands.config.config_core.load_config') as mock_load:
            
            mock_load.return_value = test_prefs
            
            app = typer.Typer()
            app.command()(config)
            
            # Test import
            result = self.runner.invoke(app, ['--import', str(import_file)])
            assert result.exit_code == 0
            mock_save.assert_called_once_with(test_prefs)
            
            # Test export
            result = self.runner.invoke(app, ['--export', str(export_file)])
            assert result.exit_code == 0
            
            # Verify exported content
            exported = json.loads(export_file.read_text())
            assert exported == test_prefs

    def test_api_key_masking_edge_cases(self):
        """Test API key masking with different key lengths"""
        test_cases = [
            ('sk-short', '***'),  # Short key (8 chars) gets fully masked
            ('sk-mediumkey123', 'sk-mediu*******'),  # Medium key: first 8 + asterisks for remaining 7
            ('sk-verylongapikey1234567890', 'sk-veryl*******************'),  # Long key: first 8 + asterisks for remaining 19
        ]
        
        for original_key, expected_masked in test_cases:
            config_data = {'openai_api_key': original_key, 'model': 'gpt-4'}
            
            with patch('commands.config.config_core.load_config') as mock_load:
                mock_load.return_value = config_data
                
                app = typer.Typer()
                app.command()(config)
                
                result = self.runner.invoke(app, ['--get', 'openai_api_key'])
                
                assert result.exit_code == 0
                output = json.loads(result.stdout)
                assert output['value'] == expected_masked 