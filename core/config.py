"""
Configuration management for BugIt.
Handles .bugitrc file parsing, environment variables, and CLI overrides.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigError(Exception):
    """Raised when configuration is invalid or missing"""
    pass

DEFAULT_CONFIG = {
    'model': 'gpt-4',
    'enum_mode': 'auto',
    'api_key': None
}

def load_config() -> Dict[str, Any]:
    """
    Load configuration from .bugitrc, environment variables, and defaults.
    Priority: CLI args > env vars > .bugitrc > defaults
    """
    config = DEFAULT_CONFIG.copy()
    
    # Load from .bugitrc if it exists
    bugitrc_path = Path('.bugitrc')
    if bugitrc_path.exists():
        try:
            with open(bugitrc_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ConfigError(f"Invalid .bugitrc file: {e}")
    
    # Override with environment variables
    if 'BUGIT_API_KEY' in os.environ:
        config['api_key'] = os.environ['BUGIT_API_KEY']
    if 'BUGIT_MODEL' in os.environ:
        config['model'] = os.environ['BUGIT_MODEL']
    
    return config

def save_config(config: Dict[str, Any], filepath: str = '.bugitrc') -> None:
    """Save configuration to file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"[STUB] Configuration saved to {filepath}")
    except Exception as e:
        raise ConfigError(f"Failed to save config: {e}")

def get_config_value(key: str) -> Any:
    """Get specific configuration value"""
    config = load_config()
    return config.get(key)

def set_config_value(key: str, value: Any) -> None:
    """Set specific configuration value"""
    config = load_config()
    config[key] = value
    save_config(config) 