"""
Config command for managing BugIt configuration.
API keys are saved to .env file, preferences to .bugitrc.
Designed for future multi-provider support.
"""

import typer
import json
import os
from typing import Optional
from pathlib import Path
from core import config as config_core


def config(
    get: Optional[str] = typer.Option(None, "-g", "--get", help="Get a config value"),
    set_key: Optional[str] = typer.Option(None, "--set", help="Config key to set"),
    set_api_key: Optional[str] = typer.Option(None, "--set-api-key", help="Set API key for provider (openai, anthropic, google)"),
    import_file: Optional[Path] = typer.Option(None, "--import", help="Import preferences from JSON file"),
    export_file: Optional[Path] = typer.Option(None, "--export", help="Export preferences to JSON file"),
    pretty_output: bool = typer.Option(False, "-p", "--pretty", help="Output in human-readable format"),
    value: Optional[str] = typer.Argument(None, help="Value to set (for --set or --set-api-key)")
):
    """
    View or modify BugIt configuration.
    
    Use --get to retrieve values, --set for preferences, --set-api-key for API keys.
    API keys are saved to .env file and loaded automatically.
    
    Default output is JSON for easy scripting and automation.
    Use --pretty for human-readable output with helpful information.
    """
    try:
        # Set API key persistently to .env file
        if set_api_key:
            if not value:
                typer.echo("API key value is required when using --set-api-key", err=True)
                typer.echo("Example: bugit config --set-api-key openai sk-your-key", err=True)
                raise typer.Exit(1)
            
            try:
                config_core.set_api_key(set_api_key, value)
                typer.echo(f"API key for {set_api_key} set successfully")
                typer.echo(f"Saved to .env file for future sessions")
            except config_core.ConfigError as e:
                typer.echo(f"Error: {e}", err=True)
                raise typer.Exit(1)
            return
        
        # Import preferences from file
        if import_file:
            if not import_file.exists():
                typer.echo(f"File not found: {import_file}", err=True)
                raise typer.Exit(1)
            
            with open(import_file, 'r') as f:
                new_preferences = json.load(f)
            
            # Save preferences (automatically excludes API keys)
            config_core.save_preferences(new_preferences)
            typer.echo(f"Preferences imported from {import_file}")
            return
        
        # Load current config
        current_config = config_core.load_config()
        
        # Export preferences to file (excluding API keys)
        if export_file:
            safe_preferences = {
                k: v for k, v in current_config.items() 
                if not k.endswith('_api_key')
            }
            with open(export_file, 'w') as f:
                json.dump(safe_preferences, f, indent=2)
            typer.echo(f"Preferences exported to {export_file}")
            return
        
        # Get specific config value
        if get:
            # Handle legacy 'api_key' request
            if get == 'api_key':
                get = 'openai_api_key'
                if pretty_output:
                    typer.echo("[INFO] 'api_key' is now 'openai_api_key' for clarity")
            
            if get in current_config:
                value_result = current_config[get]
                
                if pretty_output:
                    # Human-readable output
                    if get.endswith('_api_key'):
                        if value_result:
                            # Mask API key for security
                            masked = value_result[:8] + "*" * (len(value_result) - 8) if len(value_result) > 8 else "***"
                            source = "(.env file)" if Path('.env').exists() else "(environment)"
                            typer.echo(f"{get}: {masked} {source}")
                        else:
                            provider = get.replace('_api_key', '')
                            typer.echo(f"{get}: Not set")
                            typer.echo(f"Set with: bugit config --set-api-key {provider} <your-key>")
                    else:
                        typer.echo(f"{get}: {value_result}")
                else:
                    # JSON output
                    output_value = value_result
                    if get.endswith('_api_key') and value_result:
                        # Mask API key for security in JSON
                        output_value = value_result[:8] + "*" * (len(value_result) - 8) if len(value_result) > 8 else "***"
                    
                    output = {
                        "key": get,
                        "value": output_value,
                        "set": bool(value_result) if get.endswith('_api_key') else True
                    }
                    typer.echo(json.dumps(output, indent=2))
            else:
                if pretty_output:
                    typer.echo(f"Config key '{get}' not found.")
                else:
                    output = {
                        "key": get,
                        "value": None,
                        "set": False,
                        "error": "Key not found"
                    }
                    typer.echo(json.dumps(output, indent=2))
            return
        
        # Set config value
        if set_key:
            if not value:
                typer.echo("Value is required when using --set", err=True)
                raise typer.Exit(1)
            
            # Handle legacy 'api_key' setting attempt
            if set_key == 'api_key':
                typer.echo("Error: Use '--set-api-key openai <key>' instead of '--set api_key'", err=True)
                typer.echo("Example: bugit config --set-api-key openai sk-your-key", err=True)
                raise typer.Exit(1)
            
            try:
                config_core.set_preference(set_key, value)
                typer.echo(f"Set {set_key}: {value}")
            except config_core.ConfigError as e:
                typer.echo(f"Error: {e}", err=True)
                raise typer.Exit(1)
            return
        
        # Show all config (default behavior)
        if pretty_output:
            # Human-readable output with helpful information
            typer.echo("Current configuration:")
            typer.echo()
            
            # Show OpenAI API key status
            if config_core.check_openai_api_key():
                api_key = current_config.get('openai_api_key', '')
                masked = api_key[:8] + "*" * (len(api_key) - 8) if len(api_key) > 8 else "***"
                source = "(.env file)" if Path('.env').exists() else "(environment)"
                typer.echo(f"  openai_api_key: {masked} {source}")
            else:
                typer.echo(f"  openai_api_key: Not set")
                typer.echo(f"     Set with: bugit config --set-api-key openai <your-key>")
            
            # Future: Show other provider API keys here
            # typer.echo(f"  anthropic_api_key: {masked if anthropic_key else 'Not set'}")
            # typer.echo(f"  google_api_key: {masked if google_key else 'Not set'}")
            
            typer.echo()
            typer.echo("Preferences:")
            
            # Show preferences
            for key, val in current_config.items():
                if not key.endswith('_api_key'):
                    # Only API keys use environment variables, preferences come from .bugitrc or defaults
                    source = " (from .bugitrc)" if Path('.bugitrc').exists() else " (default)"
                    typer.echo(f"  {key}: {val}{source}")
            
            # Show helpful hints
            typer.echo()
            typer.echo("Helpful commands:")
            typer.echo("   bugit config --set-api-key openai <key>   # Set OpenAI API key")
            typer.echo("   bugit config --set model gpt-4            # Set model preference")
            typer.echo("   bugit config --export config.json        # Export preferences")
        else:
            # JSON output for scripting (default)
            output_config = current_config.copy()
            
            # Mask API keys for security in JSON output
            for key in output_config.keys():
                if key.endswith('_api_key') and output_config[key]:
                    output_config[key] = output_config[key][:8] + "*" * (len(output_config[key]) - 8) if len(output_config[key]) > 8 else "***"
            
            typer.echo(json.dumps(output_config, indent=2))
                
    except typer.Exit:
        # Re-raise typer.Exit to preserve exit codes
        raise
    except Exception as e:
        typer.echo(f"Error managing config: {e}", err=True)
        raise typer.Exit(1) 