"""
List command for displaying bug reports.
Shows issues in a formatted table with filtering options.
"""

import typer
from typing import Optional
from core import storage
from rich.console import Console
from rich.table import Table


def list_issues(
    tag: Optional[str] = typer.Option(None, "--tag", help="Filter by tag"),
    severity: Optional[str] = typer.Option(None, "--severity", help="Filter by severity"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    """
    List all bug reports with optional filtering.
    
    Args:
        tag: Filter by specific tag
        severity: Filter by severity level  
        json_output: Output in JSON format instead of table
    """
    try:
        issues = storage.list_issues()
        
        # Apply filters
        if tag:
            issues = [i for i in issues if tag in i.get('tags', [])]
        if severity:
            issues = [i for i in issues if i.get('severity') == severity.lower()]
            
        if json_output:
            import json
            typer.echo(json.dumps(issues, indent=2))
        else:
            _display_table(issues)
            
    except Exception as e:
        typer.echo(f"Error listing issues: {e}", err=True)
        raise typer.Exit(1)


def _display_table(issues):
    """Display issues in a formatted table"""
    console = Console()
    table = Table()
    
    table.add_column("Index", style="cyan")
    table.add_column("UUID", style="magenta")
    table.add_column("Date", style="green")
    table.add_column("Severity", style="red")
    table.add_column("Tags", style="yellow")
    table.add_column("Title", style="white")
    
    for i, issue in enumerate(issues, 1):
        tags_str = ", ".join(issue.get('tags', []))
        title = issue.get('title', 'No title')
        if len(title) > 35:
            title = title[:32] + "..."
            
        table.add_row(
            f"[{i}]",
            issue.get('id', 'N/A'),
            issue.get('created_at', 'N/A')[:10],  # Just date part
            issue.get('severity', 'N/A'),
            tags_str,
            title
        )
    
    console.print(table) 