"""
Error handling and exit codes for BugIt CLI.
Implements standard POSIX exit codes and structured error responses.
"""

import sys
from enum import IntEnum
from typing import Optional


class ExitCode(IntEnum):
    """Standard POSIX exit codes for BugIt CLI"""

    SUCCESS = 0  # Command completed successfully
    GENERAL_ERROR = 1  # General error condition
    INVALID_USAGE = 2  # Invalid command line usage
    NOT_FOUND = 3  # Requested resource not found
    PERMISSION_ERROR = 4  # Permission denied
    VALIDATION_ERROR = 5  # Data validation failed
    API_ERROR = 6  # External API error
    STORAGE_ERROR = 7  # File system error


class BugItError(Exception):
    """Base exception with structured error information"""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        suggestion: Optional[str] = None,
        url: Optional[str] = None,
        exit_code: int = ExitCode.GENERAL_ERROR,
    ):
        self.message = message
        self.code = code or "GENERAL_ERROR"
        self.suggestion = suggestion
        self.url = url or "https://github.com/user/bugit/issues"
        self.exit_code = exit_code
        super().__init__(message)


class ValidationError(BugItError):
    """Data validation error"""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            suggestion=suggestion or "Check your input data format",
            exit_code=ExitCode.VALIDATION_ERROR,
        )


class NotFoundError(BugItError):
    """Resource not found error"""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            suggestion=suggestion or "Use 'bugit list' to see available issues",
            exit_code=ExitCode.NOT_FOUND,
        )


class StorageError(BugItError):
    """File system operation error"""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(
            message=message,
            code="STORAGE_ERROR",
            suggestion=suggestion or "Check file system permissions and disk space",
            exit_code=ExitCode.STORAGE_ERROR,
        )


class APIError(BugItError):
    """External API error"""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(
            message=message,
            code="API_ERROR",
            suggestion=suggestion or "Check your API key and network connection",
            exit_code=ExitCode.API_ERROR,
        )


def handle_command_error(error: Exception) -> int:
    """Convert exceptions to appropriate exit codes"""
    if isinstance(error, BugItError):
        return error.exit_code
    elif isinstance(error, KeyboardInterrupt):
        return ExitCode.GENERAL_ERROR
    elif isinstance(error, FileNotFoundError):
        return ExitCode.NOT_FOUND
    elif isinstance(error, PermissionError):
        return ExitCode.PERMISSION_ERROR
    else:
        return ExitCode.GENERAL_ERROR


def format_error(error: BugItError, pretty: bool = False) -> dict:
    """Format error consistently for JSON or pretty output"""
    error_data = {"success": False, "error": error.message, "code": error.code}

    if error.suggestion:
        error_data["suggestion"] = error.suggestion
    if error.url:
        error_data["help_url"] = error.url

    return error_data
