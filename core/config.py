"""
Configuration management for BugIt.
Uses .env files for secrets and .bugitrc for preferences.
Designed to support multiple AI providers in the future.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv, set_key, find_dotenv

class ConfigError(Exception):
    """Raised when configuration is invalid or missing"""
    pass

# Default user preferences (not secrets!)
DEFAULT_PREFERENCES = {
    'model': 'gpt-4',
    'enum_mode': 'auto',
    'output_format': 'table',  # 'table' or 'json'
    'retry_limit': 3,
    'default_severity': 'medium'
}

def load_config() -> Dict[str, Any]:
    """
    Load complete configuration from .env file, environment variables, and .bugitrc.
    
    Priority: Environment Variables > .env file > .bugitrc > Defaults
    
    .env file (secrets):
    - BUGIT_OPENAI_API_KEY: OpenAI API key
    - BUGIT_ANTHROPIC_API_KEY: Anthropic Claude API key (future)
    - BUGIT_GOOGLE_API_KEY: Google Gemini API key (future)
    
    Environment variables (overrides):
    - BUGIT_MODEL: Model override (optional, overrides .bugitrc)
    
    .bugitrc file (preferences):
    - model, enum_mode, output_format, retry_limit, etc.
    """
    # Load environment variables from .env file first
    load_dotenv()
    
    config = DEFAULT_PREFERENCES.copy()
    
    # Load user preferences from .bugitrc if it exists
    bugitrc_path = Path('.bugitrc')
    if bugitrc_path.exists():
        try:
            with open(bugitrc_path, 'r') as f:
                file_preferences = json.load(f)
                config.update(file_preferences)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ConfigError(f"Invalid .bugitrc file: {e}")
    
    # Add API keys from environment (loaded from .env or set manually)
    config['openai_api_key'] = os.environ.get('BUGIT_OPENAI_API_KEY')
    
    # Legacy support for old environment variable name (temporary)
    if not config['openai_api_key'] and 'BUGIT_API_KEY' in os.environ:
        config['openai_api_key'] = os.environ.get('BUGIT_API_KEY')
        print("[WARNING] BUGIT_API_KEY is deprecated. Please use BUGIT_OPENAI_API_KEY instead.")
    
    # Future: Add other provider API keys here
    # config['anthropic_api_key'] = os.environ.get('BUGIT_ANTHROPIC_API_KEY')
    # config['google_api_key'] = os.environ.get('BUGIT_GOOGLE_API_KEY')
    
    # Optional environment overrides for preferences
    if 'BUGIT_MODEL' in os.environ:
        config['model'] = os.environ['BUGIT_MODEL']
    
    return config

def save_preferences(preferences: Dict[str, Any], filepath: str = '.bugitrc') -> None:
    """
    Save user preferences to .bugitrc file.
    
    Note: This excludes API keys (which are saved to .env file).
    """
    # Filter out all API keys (current and future providers)
    safe_preferences = {
        k: v for k, v in preferences.items() 
        if not k.endswith('_api_key')  # Excludes openai_api_key, anthropic_api_key, etc.
    }
    
    try:
        with open(filepath, 'w') as f:
            json.dump(safe_preferences, f, indent=2)
        # print(f"[STUB] Preferences saved to {filepath}")
    except Exception as e:
        raise ConfigError(f"Failed to save preferences: {e}")

def set_api_key(provider: str, api_key: str) -> None:
    """
    Set API key for a provider persistently in .env file.
    
    Args:
        provider: Provider name (e.g., 'openai', 'anthropic', 'google')
        api_key: The API key to set
    """
    if not api_key or not api_key.strip():
        raise ConfigError("API key cannot be empty")
    
    env_var_name = f"BUGIT_{provider.upper()}_API_KEY"
    env_file = find_dotenv()
    
    # Create .env file if it doesn't exist
    if not env_file:
        env_file = '.env'
        Path(env_file).touch()
    
    # Set the API key in .env file
    set_key(env_file, env_var_name, api_key)
    
    # Also set in current environment for immediate use
    os.environ[env_var_name] = api_key
    
    print(f"API key for {provider} saved to .env file")

def get_config_value(key: str) -> Any:
    """Get specific configuration value"""
    config = load_config()
    return config.get(key)

def set_preference(key: str, value: Any) -> None:
    """
    Set a user preference.
    
    Note: For API keys, use set_api_key() instead
    """
    if key.endswith('_api_key'):
        provider = key.replace('_api_key', '')
        raise ConfigError(f"Use 'bugit config --set-api-key {provider} <key>' to set API keys")
    
    # Load current preferences from file
    current_preferences = DEFAULT_PREFERENCES.copy()
    bugitrc_path = Path('.bugitrc')
    if bugitrc_path.exists():
        try:
            with open(bugitrc_path, 'r') as f:
                current_preferences.update(json.load(f))
        except (json.JSONDecodeError, FileNotFoundError):
            pass  # Use defaults if file is corrupted
    
    # Update the preference
    current_preferences[key] = value
    save_preferences(current_preferences)

def check_openai_api_key() -> bool:
    """Check if OpenAI API key is properly configured"""
    config = load_config()
    api_key = config.get('openai_api_key')
    return api_key is not None and api_key.strip() != ''

def check_api_key() -> bool:
    """Legacy function - check if any API key is configured"""
    return check_openai_api_key()

# Legacy compatibility function
def set_config_value(key: str, value: Any) -> None:
    """Legacy function - use set_preference instead"""
    set_preference(key, value) 