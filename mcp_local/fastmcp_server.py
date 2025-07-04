"""
Official MCP server implementation using FastMCP SDK.

This replaces our custom implementation with the official Model Context Protocol
Python SDK, which uses @tool decorators and proper protocol compliance.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

from mcp.server.fastmcp import FastMCP

from core import config, model, schema, storage
from core.errors import BugItError

# Create the FastMCP server
mcp = FastMCP(
    name="bugit-mcp-server",
    description="BugIt MCP Server - AI-powered bug tracking tools",
)


@mcp.tool()
def create_issue(description: str) -> Dict[str, Any]:
    """
    Create a new bug report from a freeform description.

    Args:
        description: Freeform text description of the bug

    Returns:
        Dictionary containing success status and issue data
    """
    try:
        # Process description with LangGraph
        result = model.process_description(description)

        # Validate and apply defaults
        validated = schema.validate_or_default(result)

        # Save to storage
        issue_id = storage.save_issue(validated)

        return {"success": True, "issue": validated, "id": issue_id}

    except BugItError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def list_issues(
    tag: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List all bug reports with optional filtering.

    Args:
        tag: Filter by tag (optional)
        severity: Filter by severity (optional)
        status: Filter by status (optional)

    Returns:
        List of issue dictionaries
    """
    try:
        issues = storage.list_issues()

        # Apply filters
        if tag:
            issues = [i for i in issues if tag in i.get("tags", [])]
        if severity:
            issues = [i for i in issues if i.get("severity") == severity.lower()]
        if status:
            issues = [i for i in issues if i.get("status") == status.lower()]

        return issues

    except BugItError as e:
        return [{"error": str(e)}]
    except Exception as e:
        return [{"error": f"Unexpected error: {str(e)}"}]


@mcp.tool()
def get_issue(id_or_index: Union[str, int]) -> Dict[str, Any]:
    """
    Get a single issue by ID or index.

    Args:
        id_or_index: Either the UUID or numeric index of the issue

    Returns:
        Dictionary containing success status and issue data
    """
    try:
        if isinstance(id_or_index, int) or (
            isinstance(id_or_index, str) and id_or_index.isdigit()
        ):
            # Index-based selection
            index = int(id_or_index)
            issue = storage.get_issue_by_index(index)
        else:
            # UUID-based selection
            issue = storage.load_issue(str(id_or_index))

        return {"success": True, "issue": issue}

    except BugItError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def update_issue(
    id_or_index: Union[str, int],
    title: Optional[str] = None,
    description: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    solution: Optional[str] = None,
    add_tags: Optional[List[str]] = None,
    remove_tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Update an existing issue with new field values.

    Args:
        id_or_index: Either the UUID or numeric index of the issue
        title: New title (optional)
        description: New description (optional)
        severity: New severity level (optional)
        status: New status (optional)
        solution: New solution (optional)
        add_tags: Tags to add (optional)
        remove_tags: Tags to remove (optional)

    Returns:
        Dictionary containing success status, changes made, and updated issue
    """
    try:
        # Get the issue to edit
        if isinstance(id_or_index, int) or (
            isinstance(id_or_index, str) and id_or_index.isdigit()
        ):
            # Index-based selection
            index = int(id_or_index)
            issue = storage.get_issue_by_index(index)
        else:
            # UUID-based selection
            issue = storage.load_issue(str(id_or_index))

        # Track changes
        changes_made = False
        changes_log = []

        # Update fields
        if title is not None:
            issue["title"] = title
            changes_made = True
            changes_log.append(f"Updated title: {title}")

        if description is not None:
            issue["description"] = description
            changes_made = True
            changes_log.append(f"Updated description")

        if severity is not None:
            if severity.lower() in ["low", "medium", "high", "critical"]:
                issue["severity"] = severity.lower()
                changes_made = True
                changes_log.append(f"Updated severity: {severity.lower()}")
            else:
                return {
                    "success": False,
                    "error": f"Invalid severity: {severity}. Must be low, medium, high, or critical.",
                }

        if status is not None:
            if status.lower() in ["open", "resolved", "archived"]:
                issue["status"] = status.lower()
                changes_made = True
                changes_log.append(f"Updated status: {status.lower()}")
            else:
                return {
                    "success": False,
                    "error": f"Invalid status: {status}. Must be open, resolved, or archived.",
                }

        if solution is not None:
            issue["solution"] = solution
            changes_made = True
            changes_log.append(f"Updated solution")

        # Handle tags
        tags = issue.get("tags", [])

        if add_tags:
            for tag in add_tags:
                if tag not in tags:
                    tags.append(tag)
                    changes_made = True
                    changes_log.append(f"Added tag: {tag}")
                else:
                    changes_log.append(f"Tag '{tag}' already exists")

        if remove_tags:
            for tag in remove_tags:
                if tag in tags:
                    tags.remove(tag)
                    changes_made = True
                    changes_log.append(f"Removed tag: {tag}")
                else:
                    changes_log.append(f"Tag '{tag}' not found")

        issue["tags"] = tags

        if not changes_made:
            return {
                "success": False,
                "message": "No changes specified",
                "changes": changes_log,
            }

        # Validate and save
        validated = schema.validate_or_default(issue)
        storage.save_issue(validated)

        return {
            "success": True,
            "id": issue["id"],
            "changes": changes_log,
            "updated_issue": validated,
        }

    except BugItError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def delete_issue(id_or_index: Union[str, int]) -> Dict[str, Any]:
    """
    Delete an issue by ID or index.

    Args:
        id_or_index: Either the UUID or numeric index of the issue

    Returns:
        Dictionary containing success status and deletion info
    """
    try:
        # Get the issue first to validate it exists
        if isinstance(id_or_index, int) or (
            isinstance(id_or_index, str) and id_or_index.isdigit()
        ):
            # Index-based selection
            index = int(id_or_index)
            issue = storage.get_issue_by_index(index)
            issue_id = issue["id"]
        else:
            # UUID-based selection
            issue_id = str(id_or_index)
            issue = storage.load_issue(issue_id)

        # Attempt deletion
        deleted = storage.delete_issue(issue_id)

        if deleted:
            return {
                "success": True,
                "message": f"Issue {issue_id} deleted successfully",
                "deleted_issue": {
                    "id": issue_id,
                    "title": issue.get("title", "No title"),
                },
            }
        else:
            return {"success": False, "message": f"Issue {issue_id} not found"}

    except BugItError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def get_config() -> Dict[str, Any]:
    """
    Get current configuration settings.

    Returns:
        Dictionary containing configuration data
    """
    try:
        # Get configuration from core.config
        config_data = {}

        # Safe way to get config values
        try:
            config_data["model"] = config.get_config_value("model")
        except:
            config_data["model"] = "gpt-4"

        try:
            config_data["enum_mode"] = config.get_config_value("enum_mode")
        except:
            config_data["enum_mode"] = "auto"

        try:
            config_data["output_format"] = config.get_config_value("output_format")
        except:
            config_data["output_format"] = "table"

        try:
            config_data["retry_limit"] = config.get_config_value("retry_limit")
        except:
            config_data["retry_limit"] = 3

        try:
            config_data["default_severity"] = config.get_config_value(
                "default_severity"
            )
        except:
            config_data["default_severity"] = "medium"

        try:
            config_data["backup_on_delete"] = config.get_config_value(
                "backup_on_delete"
            )
        except:
            config_data["backup_on_delete"] = True

        return {"success": True, "config": config_data}

    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def set_config(key: str, value: Any) -> Dict[str, Any]:
    """
    Set a configuration value.

    Args:
        key: Configuration key to set
        value: Value to set

    Returns:
        Dictionary containing success status and updated config
    """
    try:
        # Valid configuration keys
        valid_keys = {
            "model",
            "enum_mode",
            "output_format",
            "retry_limit",
            "default_severity",
            "backup_on_delete",
        }

        if key not in valid_keys:
            return {
                "success": False,
                "error": f"Invalid configuration key: {key}. Valid keys: {', '.join(valid_keys)}",
            }

        # Type validation
        if key == "retry_limit" and not isinstance(value, int):
            return {
                "success": False,
                "error": f"retry_limit must be an integer, got {type(value).__name__}",
            }

        if key == "backup_on_delete" and not isinstance(value, bool):
            return {
                "success": False,
                "error": f"backup_on_delete must be a boolean, got {type(value).__name__}",
            }

        if key == "default_severity" and value not in [
            "low",
            "medium",
            "high",
            "critical",
        ]:
            return {
                "success": False,
                "error": f"default_severity must be one of: low, medium, high, critical",
            }

        # Set the configuration value
        config.set_config_value(key, value)

        # Get updated configuration
        updated_config = get_config()

        return {
            "success": True,
            "message": f"Configuration updated: {key} = {value}",
            "config": updated_config.get("config", {}),
        }

    except BugItError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def get_storage_stats() -> Dict[str, Any]:
    """
    Get storage statistics for monitoring and debugging.

    Returns:
        Dictionary containing storage statistics
    """
    try:
        stats = storage.get_storage_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


# Entry point for the server
if __name__ == "__main__":
    # Setup logging for debug mode
    logging.basicConfig(level=logging.INFO)
    
    # Run the server
    mcp.run() 