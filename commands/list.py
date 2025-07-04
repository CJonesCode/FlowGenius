"""
List command for displaying bug reports.
Shows issues in a formatted table with filtering options.
"""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from core import storage
from core.styles import Styles, TableStyles


def list_issues(
    tag: Optional[str] = typer.Option(None, "-t", "--tag", help="Filter by tag"),
    severity: Optional[str] = typer.Option(
        None, "-s", "--severity", help="Filter by severity"
    ),
    pretty_output: bool = typer.Option(
        False, "-p", "--pretty", help="Output in human-readable table format"
    ),
):
    """
    List all bug reports with optional filtering.

    Use --tag and --severity to filter results. Use --pretty for human-readable table output.
    Default output is JSON for easy scripting and automation.
    """
    try:
        issues = storage.list_issues()

        # Apply filters
        if tag:
            issues = [i for i in issues if tag in i.get("tags", [])]
        if severity:
            issues = [i for i in issues if i.get("severity") == severity.lower()]

        if pretty_output:
            _display_table(issues)
        else:
            import json

            typer.echo(json.dumps(issues, indent=2))

    except Exception as e:
        typer.echo(f"Error listing issues: {e}", err=True)
        raise typer.Exit(1)


def _display_table(issues):
    """Display issues in a formatted table with consistent styling"""
    console = Console()
    table = Table()

    # Use centralized table styles
    styles = TableStyles.issue_list()
    table.add_column("Index", style=styles["Index"])
    table.add_column("UUID", style=styles["UUID"])
    table.add_column("Date", style=styles["Date"])
    table.add_column(
        "Severity", style=styles["Severity"]
    )  # None - handled by Styles.severity()
    table.add_column("Tags", style=styles["Tags"])
    table.add_column("Title", style=styles["Title"])

    for i, issue in enumerate(issues, 1):
        tags_str = ", ".join(issue.get("tags", []))
        title = issue.get("title", "No title")
        if len(title) > 35:
            title = title[:32] + "..."

        # Apply semantic styling for content
        table.add_row(
            f"[{i}]",
            issue.get("id", "N/A"),
            issue.get("created_at", "N/A")[:10],  # Just date part
            Styles.severity(issue.get("severity", "N/A")),  # Dynamic severity coloring
            tags_str,
            title,
        )

    console.print(table)
