"""
Centralized styling system for BugIt CLI.
Provides consistent color schemes and formatting across all commands.
"""

from rich.console import Console
from rich.text import Text
from typing import Any

# BugIt Color Palette - Centralized Definition
class Colors:
    """Centralized color definitions for consistent styling"""
    
    # Core palette from style guide
    BRAND = "blue"           # Brand identity, prompts, borders
    INTERACTIVE = "cyan"     # Interactive elements, commands, indices
    ERROR = "red"           # Errors, critical severity
    SUCCESS = "green"       # Success, dates, confirmations
    WARNING = "yellow"      # Tags, warnings, medium severity
    IDENTIFIER = "magenta"  # UUIDs, identifiers
    PRIMARY = "white"       # Primary content, titles
    SECONDARY = "dim"       # Secondary text, descriptions
    
    # Severity-specific colors
    CRITICAL = "red"
    HIGH = "red"
    MEDIUM = "yellow" 
    LOW = "dim"

class Styles:
    """Semantic styling functions for consistent formatting"""
    
    @staticmethod
    def uuid(value: Any) -> str:
        """Format UUID with consistent styling"""
        return f"[{Colors.IDENTIFIER}]{value}[/{Colors.IDENTIFIER}]"
    
    @staticmethod
    def index(value: Any) -> str:
        """Format index with consistent styling"""
        return f"[{Colors.INTERACTIVE}]{value}[/{Colors.INTERACTIVE}]"
    
    @staticmethod
    def date(value: Any) -> str:
        """Format date with consistent styling"""
        return f"[{Colors.SUCCESS}]{value}[/{Colors.SUCCESS}]"
    
    @staticmethod
    def severity(value: Any) -> str:
        """Format severity with appropriate color"""
        if not value:
            return f"[{Colors.SECONDARY}]N/A[/{Colors.SECONDARY}]"
        
        value_lower = str(value).lower()
        if value_lower == "critical":
            color = Colors.CRITICAL
        elif value_lower == "high":
            color = Colors.HIGH
        elif value_lower == "medium":
            color = Colors.MEDIUM
        elif value_lower == "low":
            color = Colors.LOW
        else:
            color = Colors.SECONDARY
            
        return f"[{color}]{value}[/{color}]"
    
    @staticmethod
    def get_severity_color(value: Any) -> str:
        """Get just the color name for severity (without Rich markup)"""
        if not value:
            return Colors.SECONDARY
        
        value_lower = str(value).lower()
        if value_lower == "critical":
            return Colors.CRITICAL
        elif value_lower == "high":
            return Colors.HIGH
        elif value_lower == "medium":
            return Colors.MEDIUM
        elif value_lower == "low":
            return Colors.LOW
        else:
            return Colors.SECONDARY
    
    @staticmethod
    def tags(value: Any) -> str:
        """Format tags with consistent styling"""
        return f"[{Colors.WARNING}]{value}[/{Colors.WARNING}]"
    
    @staticmethod
    def title(value: Any) -> str:
        """Format title with consistent styling"""
        return f"[{Colors.PRIMARY}]{value}[/{Colors.PRIMARY}]"
    
    @staticmethod
    def description(value: Any) -> str:
        """Format description with consistent styling"""
        return f"[{Colors.SECONDARY}]{value}[/{Colors.SECONDARY}]"
    
    @staticmethod
    def brand(value: Any) -> str:
        """Format brand/prompt text with consistent styling"""
        return f"[{Colors.BRAND}]{value}[/{Colors.BRAND}]"
    
    @staticmethod
    def success(value: Any) -> str:
        """Format success messages with consistent styling"""
        return f"[{Colors.SUCCESS}]{value}[/{Colors.SUCCESS}]"
    
    @staticmethod
    def error(value: Any) -> str:
        """Format error messages with consistent styling"""
        return f"[{Colors.ERROR}]{value}[/{Colors.ERROR}]"
    
    @staticmethod
    def warning(value: Any) -> str:
        """Format warning messages with consistent styling"""
        return f"[{Colors.WARNING}]{value}[/{Colors.WARNING}]"

# Table styling configurations
class TableStyles:
    """Predefined table styling configurations"""
    
    @staticmethod
    def issue_list():
        """Standard issue list table column styles"""
        return {
            "Index": Colors.INTERACTIVE,
            "UUID": Colors.IDENTIFIER, 
            "Date": Colors.SUCCESS,
            "Severity": None,  # Will be handled by Styles.severity()
            "Tags": Colors.WARNING,
            "Title": Colors.PRIMARY
        }

# Export commonly used items
__all__ = ['Colors', 'Styles', 'TableStyles'] 