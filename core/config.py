"""
Configuration management for BugIt.
Uses .env files for secrets and .bugitrc for preferences.
Designed to support multiple AI providers in the future.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import find_dotenv, load_dotenv, set_key


class ConfigError(Exception):
    """Raised when configuration is invalid or missing"""

    pass


# Default user preferences (not secrets!)
DEFAULT_PREFERENCES = {
    "model": "gpt-4",
    "enum_mode": "auto",
    "output_format": "table",  # 'table' or 'json'
    "retry_limit": 3,
    "default_severity": "medium",
    "backup_on_delete": True,  # Whether to create backups when deleting issues
}

# Valid providers for API key management
VALID_PROVIDERS = {"openai", "anthropic", "google"}


def load_config() -> Dict[str, Any]:
    """
    Load complete configuration from .env file and .bugitrc.

    Priority: .env file > .bugitrc > Defaults

    .env file (API keys only - git-ignored):
    - BUGIT_OPENAI_API_KEY: OpenAI API key
    - BUGIT_ANTHROPIC_API_KEY: Anthropic Claude API key (future)
    - BUGIT_GOOGLE_API_KEY: Google Gemini API key (future)
    - BUGIT_API_KEY: Legacy API key (deprecated)

    .bugitrc file (user preferences - version controlled):
    - model, enum_mode, output_format, retry_limit, etc.

    Environment variables are ONLY used for API keys, not configuration.
    """
    # Load environment variables from .env file first
    load_dotenv()

    config = DEFAULT_PREFERENCES.copy()

    # Load user preferences from .bugitrc if it exists
    bugitrc_path = Path(".bugitrc")
    if bugitrc_path.exists():
        try:
            with open(bugitrc_path, "r") as f:
                file_preferences = json.load(f)
                config.update(file_preferences)
        except (json.JSONDecodeError, FileNotFoundError):
            # Fall back to defaults gracefully
            pass

    # Add API keys from environment (loaded from .env or set manually)
    config["openai_api_key"] = os.environ.get("BUGIT_OPENAI_API_KEY")

    # Legacy support for old environment variable name (temporary)
    if not config["openai_api_key"] and "BUGIT_API_KEY" in os.environ:
        config["openai_api_key"] = os.environ.get("BUGIT_API_KEY")
        print(
            "[WARNING] BUGIT_API_KEY is deprecated. Please use BUGIT_OPENAI_API_KEY instead."
        )

    # Add other provider API keys
    config["anthropic_api_key"] = os.environ.get("BUGIT_ANTHROPIC_API_KEY")
    config["google_api_key"] = os.environ.get("BUGIT_GOOGLE_API_KEY")

    return config


def save_preferences(preferences: Dict[str, Any], filepath: str = ".bugitrc") -> None:
    """
    Save user preferences to .bugitrc file.

    Note: This excludes API keys (which are saved to .env file).
    """
    # Filter out all API keys (current and future providers)
    safe_preferences = {
        k: v
        for k, v in preferences.items()
        if not k.endswith(
            "_api_key"
        )  # Excludes openai_api_key, anthropic_api_key, etc.
    }

    try:
        with open(filepath, "w") as f:
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

    if provider not in VALID_PROVIDERS:
        raise ValueError(
            f"Invalid provider '{provider}'. Valid providers are: {', '.join(VALID_PROVIDERS)}"
        )

    env_var_name = f"BUGIT_{provider.upper()}_API_KEY"
    env_file = find_dotenv()

    # Create .env file if it doesn't exist
    if not env_file:
        env_file = ".env"
        Path(env_file).touch()

    # Set the API key in .env file (without quotes to match test expectations)
    set_key(env_file, env_var_name, api_key, quote_mode="never")

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
    if key.endswith("_api_key"):
        provider = key.replace("_api_key", "")
        raise ConfigError(
            f"Use 'bugit config --set-api-key {provider} <key>' to set API keys"
        )

    # Validate and convert value if needed
    if key == "retry_limit":
        try:
            value = int(value)
            if not (1 <= value <= 20):
                value = 3  # Use default if out of range
        except (ValueError, TypeError):
            value = 3  # Use default if invalid
    elif key == "model":
        if not value or not isinstance(value, str) or not value.strip():
            value = "gpt-4"  # Use default if invalid

    # Load current preferences from file
    current_preferences = DEFAULT_PREFERENCES.copy()
    bugitrc_path = Path(".bugitrc")
    if bugitrc_path.exists():
        try:
            with open(bugitrc_path, "r") as f:
                current_preferences.update(json.load(f))
        except (json.JSONDecodeError, FileNotFoundError):
            pass  # Use defaults if file is corrupted

    # Update the preference
    current_preferences[key] = value
    save_preferences(current_preferences)


def check_openai_api_key() -> bool:
    """Check if OpenAI API key is properly configured"""
    config = load_config()
    api_key = config.get("openai_api_key")
    return api_key is not None and api_key.strip() != ""


def check_api_key() -> bool:
    """Legacy function - check if any API key is configured"""
    return check_openai_api_key()


# Legacy compatibility function
def set_config_value(key: str, value: Any) -> None:
    """Legacy function - use set_preference instead"""
    set_preference(key, value)
