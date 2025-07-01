"""
Config command for managing BugIt configuration.
Handles viewing, setting, importing, and exporting configuration.
"""

import typer
import json
from typing import Optional
from pathlib import Path
from core import config as config_core


def config(
    get: Optional[str] = typer.Option(None, "--get", help="Get a config value"),
    set_key: Optional[str] = typer.Option(None, "--set", help="Config key to set"),
    value: Optional[str] = typer.Argument(None, help="Value to set (when using --set)"),
    import_file: Optional[Path] = typer.Option(None, "--import", help="Import config from JSON file"),
    export_file: Optional[Path] = typer.Option(None, "--export", help="Export config to JSON file")
):
    """
    View or modify BugIt configuration.
    
    Examples:
        bugit config                    # Show current config
        bugit config --get model        # Get specific value
        bugit config --set model gpt-4  # Set specific value
        bugit config --export config.json  # Export to file
        bugit config --import config.json  # Import from file
    """
    try:
        # Import config from file
        if import_file:
            if not import_file.exists():
                typer.echo(f"File not found: {import_file}", err=True)
                raise typer.Exit(1)
            
            with open(import_file, 'r') as f:
                new_config = json.load(f)
            
            # Validate config
            config_core.save_config(new_config)
            typer.echo(f"Configuration imported from {import_file}")
            return
        
        # Load current config
        current_config = config_core.load_config()
        
        # Export config to file
        if export_file:
            with open(export_file, 'w') as f:
                json.dump(current_config, f, indent=2)
            typer.echo(f"Configuration exported to {export_file}")
            return
        
        # Get specific config value
        if get:
            if get in current_config:
                value = current_config[get]
                if get == 'api_key' and value:
                    # Mask API key for security
                    masked = value[:8] + "*" * (len(value) - 8) if len(value) > 8 else "***"
                    typer.echo(f"{get}: {masked}")
                else:
                    typer.echo(f"{get}: {value}")
            else:
                typer.echo(f"Config key '{get}' not found.")
            return
        
        # Set config value
        if set_key:
            if not value:
                typer.echo("Value is required when using --set", err=True)
                raise typer.Exit(1)
            
            config_core.set_config_value(set_key, value)
            typer.echo(f"Set {set_key}: {value}")
            return
        
        # Show all config (default behavior)
        typer.echo("Current configuration:")
        for key, val in current_config.items():
            if key == 'api_key' and val:
                # Mask API key for security
                masked = val[:8] + "*" * (len(val) - 8) if len(val) > 8 else "***"
                typer.echo(f"  {key}: {masked}")
            else:
                typer.echo(f"  {key}: {val}")
                
    except Exception as e:
        typer.echo(f"Error managing config: {e}", err=True)
        raise typer.Exit(1) 