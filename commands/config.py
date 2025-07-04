"""
Config command for managing BugIt configuration.
API keys are saved to .env file, preferences to .bugitrc.
Designed for future multi-provider support.
"""

import json
import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from core import config as config_core
from core.styles import Colors, PanelStyles, Styles

console = Console()


def _mask_api_key(api_key: str) -> str:
    """
    Mask API key for security, showing only first 3 characters followed by asterisk.

    Args:
        api_key: The API key to mask

    Returns:
        Masked API key string
    """
    if not api_key:
        return "***"

    # If key is very short, fully mask it for security
    if len(api_key) <= 3:
        return "***"

    return api_key[:3] + "*"


def config(
    get: Optional[str] = typer.Option(None, "-g", "--get", help="Get a config value"),
    set_key: Optional[str] = typer.Option(None, "--set", help="Config key to set"),
    set_api_key: Optional[str] = typer.Option(
        None,
        "--set-api-key",
        help="Set API key for provider (openai, anthropic, google)",
    ),
    import_file: Optional[Path] = typer.Option(
        None, "--import", help="Import preferences from JSON file"
    ),
    export_file: Optional[Path] = typer.Option(
        None, "--export", help="Export preferences to JSON file"
    ),
    pretty_output: bool = typer.Option(
        False, "-p", "--pretty", help="Output in human-readable format"
    ),
    value: Optional[str] = typer.Argument(
        None, help="Value to set (for --set or --set-api-key)"
    ),
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
                if pretty_output:
                    console.print(
                        Styles.error(
                            "API key value is required when using --set-api-key"
                        )
                    )
                    console.print(
                        f"[{Colors.SECONDARY}]Example:[/{Colors.SECONDARY}] [bold]bugit config --set-api-key openai sk-your-key[/bold]"
                    )
                else:
                    console.print(
                        json.dumps(
                            {
                                "success": False,
                                "error": "API key value is required when using --set-api-key",
                            }
                        )
                    )
                raise typer.Exit(1)

            try:
                config_core.set_api_key(set_api_key, value)
                if pretty_output:
                    console.print(
                        Styles.success(f"API key for {set_api_key} set successfully")
                    )
                    console.print(
                        f"[{Colors.SUCCESS}]✓[/{Colors.SUCCESS}] [dim]Saved to .env file for future sessions[/dim]"
                    )
                else:
                    console.print(
                        json.dumps(
                            {
                                "success": True,
                                "provider": set_api_key,
                                "message": "API key set successfully",
                            }
                        )
                    )
            except config_core.ConfigError as e:
                if pretty_output:
                    console.print(Styles.error(f"Error: {e}"))
                else:
                    console.print(json.dumps({"success": False, "error": str(e)}))
                raise typer.Exit(1)
            return

        # Import preferences from file
        if import_file:
            if not import_file.exists():
                if pretty_output:
                    console.print(Styles.error(f"File not found: {import_file}"))
                else:
                    console.print(
                        json.dumps(
                            {
                                "success": False,
                                "error": f"File not found: {import_file}",
                            }
                        )
                    )
                raise typer.Exit(1)

            with open(import_file, "r") as f:
                new_preferences = json.load(f)

            # Save preferences (automatically excludes API keys)
            config_core.save_preferences(new_preferences)
            if pretty_output:
                console.print(
                    Styles.success(f"Preferences imported from {import_file}")
                )
            else:
                console.print(
                    json.dumps({"success": True, "imported_from": str(import_file)})
                )
            return

        # Load current config
        current_config = config_core.load_config()

        # Export preferences to file (excluding API keys)
        if export_file:
            safe_preferences = {
                k: v for k, v in current_config.items() if not k.endswith("_api_key")
            }
            with open(export_file, "w") as f:
                json.dump(safe_preferences, f, indent=2)
            if pretty_output:
                console.print(Styles.success(f"Preferences exported to {export_file}"))
            else:
                console.print(
                    json.dumps({"success": True, "exported_to": str(export_file)})
                )
            return

        # Get specific config value
        if get:
            # Handle legacy 'api_key' request
            if get == "api_key":
                get = "openai_api_key"
                if pretty_output:
                    console.print(
                        f"[{Colors.WARNING}]INFO:[/{Colors.WARNING}] 'api_key' is now 'openai_api_key' for clarity"
                    )

            if get in current_config:
                value_result = current_config[get]

                if pretty_output:
                    # Human-readable output
                    if get.endswith("_api_key"):
                        if value_result:
                            # Mask API key for security
                            masked = _mask_api_key(value_result)
                            source = (
                                "(.env file)"
                                if Path(".env").exists()
                                else "(environment)"
                            )
                            console.print(
                                f"[{Colors.SECONDARY}]{get}:[/{Colors.SECONDARY}] [{Colors.IDENTIFIER}]{masked}[/{Colors.IDENTIFIER}] [dim]{source}[/dim]"
                            )
                        else:
                            provider = get.replace("_api_key", "")
                            console.print(
                                f"[{Colors.SECONDARY}]{get}:[/{Colors.SECONDARY}] [{Colors.ERROR}]Not set[/{Colors.ERROR}]"
                            )
                            console.print(
                                f"[{Colors.SECONDARY}]Set with:[/{Colors.SECONDARY}] [bold]bugit config --set-api-key {provider} <your-key>[/bold]"
                            )
                    else:
                        console.print(
                            f"[{Colors.SECONDARY}]{get}:[/{Colors.SECONDARY}] [{Colors.PRIMARY}]{value_result}[/{Colors.PRIMARY}]"
                        )
                else:
                    # JSON output
                    output_value = value_result
                    if get.endswith("_api_key") and value_result:
                        # Mask API key for security in JSON
                        output_value = _mask_api_key(value_result)

                    output = {
                        "key": get,
                        "value": output_value,
                        "set": bool(value_result) if get.endswith("_api_key") else True,
                    }
                    console.print(json.dumps(output, indent=2))
            else:
                if pretty_output:
                    console.print(Styles.error(f"Config key '{get}' not found."))
                else:
                    output = {
                        "key": get,
                        "value": None,
                        "set": False,
                        "error": "Key not found",
                    }
                    console.print(json.dumps(output, indent=2))
            return

        # Set config value
        if set_key:
            if not value:
                if pretty_output:
                    console.print(Styles.error("Value is required when using --set"))
                else:
                    console.print(
                        json.dumps(
                            {
                                "success": False,
                                "error": "Value is required when using --set",
                            }
                        )
                    )
                raise typer.Exit(1)

            # Handle legacy 'api_key' setting attempt
            if set_key == "api_key":
                if pretty_output:
                    console.print(
                        Styles.error(
                            "Use '--set-api-key openai <key>' instead of '--set api_key'"
                        )
                    )
                    console.print(
                        f"[{Colors.SECONDARY}]Example:[/{Colors.SECONDARY}] [bold]bugit config --set-api-key openai sk-your-key[/bold]"
                    )
                else:
                    console.print(
                        json.dumps(
                            {
                                "success": False,
                                "error": "Use '--set-api-key openai <key>' instead of '--set api_key'",
                            }
                        )
                    )
                raise typer.Exit(1)

            try:
                config_core.set_preference(set_key, value)
                if pretty_output:
                    console.print(Styles.success(f"Set {set_key}: {value}"))
                else:
                    console.print(
                        json.dumps({"success": True, "key": set_key, "value": value})
                    )
            except config_core.ConfigError as e:
                if pretty_output:
                    console.print(Styles.error(f"Error: {e}"))
                else:
                    console.print(json.dumps({"success": False, "error": str(e)}))
                raise typer.Exit(1)
            return

        # Show all config (default behavior)
        if pretty_output:
            _display_config_pretty(current_config)
        else:
            # JSON output for scripting (default)
            output_config = {}

            # Copy config with masked API keys for security in JSON output
            for key, value in current_config.items():
                if key.endswith("_api_key") and value:
                    # Create masked version without modifying original
                    output_config[key] = _mask_api_key(value)
                else:
                    output_config[key] = value

            console.print(json.dumps(output_config, indent=2))

    except typer.Exit:
        # Re-raise typer.Exit to preserve exit codes
        raise
    except Exception as e:
        if pretty_output:
            console.print(Styles.error(f"Error managing config: {e}"))
        else:
            console.print(json.dumps({"success": False, "error": str(e)}))
        raise typer.Exit(1)


def _display_config_pretty(current_config: dict):
    """Display configuration in a beautifully formatted panel"""
    content = Text()

    # API Keys section
    content.append("API Keys:\n", style=f"bold {Colors.BRAND}")

    # OpenAI API key
    if config_core.check_openai_api_key():
        api_key = current_config.get("openai_api_key", "")
        masked = _mask_api_key(api_key)
        source = "(.env file)" if Path(".env").exists() else "(environment)"
        content.append("  openai_api_key: ", style=Colors.SECONDARY)
        content.append(masked, style=Colors.IDENTIFIER)
        content.append(f" {source}\n", style="dim")
    else:
        content.append("  openai_api_key: ", style=Colors.SECONDARY)
        content.append("Not set", style=Colors.ERROR)
        content.append("\n")
        content.append("     Set with: ", style=Colors.SECONDARY)
        content.append("bugit config --set-api-key openai <your-key>\n", style="bold")

    # Future API keys can be added here
    content.append("\n")

    # Preferences section
    content.append("Preferences:\n", style=f"bold {Colors.BRAND}")

    preferences_found = False
    for key, val in current_config.items():
        if not key.endswith("_api_key"):
            preferences_found = True
            source = " (from .bugitrc)" if Path(".bugitrc").exists() else " (default)"
            content.append(f"  {key}: ", style=Colors.SECONDARY)
            content.append(str(val), style=Colors.PRIMARY)
            content.append(f"{source}\n", style="dim")

    if not preferences_found:
        content.append("  No custom preferences set\n", style=Colors.SECONDARY)

    content.append("\n")

    # Helpful commands section
    content.append("Quick Commands:\n", style=f"bold {Colors.BRAND}")
    commands = [
        ("Set OpenAI API key", "bugit config --set-api-key openai <key>"),
        ("Set model preference", "bugit config --set model gpt-4"),
        ("Export preferences", "bugit config --export config.json"),
        ("Import preferences", "bugit config --import config.json"),
    ]

    for description, command in commands:
        content.append(f"  {description}: ", style=Colors.SECONDARY)
        content.append(f"{command}\n", style=Colors.INTERACTIVE)

    # Display in a styled panel
    panel = Panel(content, title="BugIt Configuration", **PanelStyles.standard())
    console.print(panel)
