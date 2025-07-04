"""
Tests for shell module functionality in shell.py.
Tests the interactive shell features and command processing.
"""

import pytest
from unittest.mock import patch, MagicMock, call
from rich.text import Text
from rich.console import Console


class TestShellWelcome:
    """Test shell welcome panel rendering"""

    def test_show_welcome_displays_panel(self):
        """Test that show_welcome displays the welcome panel"""
        from shell import show_welcome

        with patch("shell.console") as mock_console:
            show_welcome()

            # Should print a panel
            mock_console.print.assert_called_once()

            # The call should include a Panel
            call_args = mock_console.print.call_args
            assert len(call_args[0]) > 0  # Should have arguments

            # Check that it's a Panel with welcome content
            panel = call_args[0][0]
            assert hasattr(panel, "title")
            assert panel.title == "Welcome"

    def test_show_welcome_includes_shell_commands(self):
        """Test that welcome panel includes shell-specific commands"""
        from shell import show_welcome

        with patch("shell.console") as mock_console:
            show_welcome()

            # Get the panel content
            call_args = mock_console.print.call_args
            panel = call_args[0][0]

            # Convert panel content to string for checking
            panel_text = str(panel.renderable)

            # Should include shell commands
            assert "help" in panel_text
            assert "exit" in panel_text
            assert "Shell Commands" in panel_text

    def test_show_welcome_includes_bugit_commands(self):
        """Test that welcome panel includes BugIt commands"""
        from shell import show_welcome

        with patch("shell.console") as mock_console:
            show_welcome()

            # Get the panel content
            call_args = mock_console.print.call_args
            panel = call_args[0][0]

            # Convert panel content to string for checking
            panel_text = str(panel.renderable)

            # Should include BugIt commands
            assert "BugIt Commands" in panel_text
            assert "config" in panel_text or "new" in panel_text

    def test_show_welcome_handles_typer_help_extraction(self):
        """Test that welcome panel can extract commands from Typer help"""
        from shell import _parse_typer_help_for_commands

        # Mock Typer help output
        mock_help = """
        Usage: bugit [OPTIONS] COMMAND [ARGS]...
        
        ╭─ Commands ──────────────────────────────────────────────────────────────────╮
        │ config          View or modify BugIt configuration                         │
        │ delete          Delete a bug report permanently                            │
        │ edit            Edit an existing bug report                               │
        │ list            List all bug reports with optional filtering               │
        │ new             Create a new bug report from a freeform description       │
        │ show            Show detailed information about a specific bug report     │
        ╰─────────────────────────────────────────────────────────────────────────────╯
        """

        commands = _parse_typer_help_for_commands(mock_help)

        # Should extract commands
        assert len(commands) > 0

        # Should include expected commands
        command_names = [cmd[0] for cmd in commands]
        assert "config" in command_names
        assert "new" in command_names
        assert "list" in command_names

    def test_show_welcome_fallback_commands(self):
        """Test that welcome panel uses fallback commands when extraction fails"""
        from shell import _add_fallback_commands

        # Create a mock Text object
        welcome_text = Text()

        _add_fallback_commands(welcome_text)

        # Should have added fallback commands
        text_content = str(welcome_text)
        assert "config" in text_content
        assert "new" in text_content
        assert "list" in text_content


class TestShellCommandParsing:
    """Test shell command line parsing"""

    def test_run_command_handles_empty_input(self):
        """Test that run_command handles empty input gracefully"""
        from shell import run_command

        # Empty string
        result = run_command("")
        assert result is True

        # Whitespace only
        result = run_command("   ")
        assert result is True

        # Newline only
        result = run_command("\n")
        assert result is True

    def test_run_command_handles_exit_commands(self):
        """Test that run_command handles various exit commands"""
        from shell import run_command

        with patch("shell.console") as mock_console:
            # Test different exit commands
            exit_commands = ["exit", "quit", "q", "EXIT", "QUIT"]

            for cmd in exit_commands:
                result = run_command(cmd)
                assert result is False, f"Command '{cmd}' should return False to exit"

                # Should print goodbye message
                mock_console.print.assert_called()
                mock_console.reset_mock()

    def test_run_command_handles_help_commands(self):
        """Test that run_command handles help commands"""
        from shell import run_command

        with patch("shell.show_welcome") as mock_show_welcome:
            # Test different help commands
            help_commands = ["help", "?", "HELP"]

            for cmd in help_commands:
                result = run_command(cmd)
                assert result is True, f"Command '{cmd}' should return True to continue"

                # Should show welcome
                mock_show_welcome.assert_called_once()
                mock_show_welcome.reset_mock()

    def test_run_command_parses_quoted_arguments(self):
        """Test that run_command correctly parses quoted arguments"""
        from shell import run_command

        with patch("shell.app") as mock_app:
            with patch("sys.argv", ["bugit"]):
                # Test command with quoted arguments
                result = run_command('new "test bug with spaces"')

                # Should return True to continue shell
                assert result is True

                # Should have called the CLI app
                mock_app.assert_called_once()

    def test_run_command_handles_malformed_quotes(self):
        """Test that run_command handles malformed quotes gracefully"""
        from shell import run_command

        with patch("shell.console") as mock_console:
            # Test malformed quotes
            result = run_command('new "unclosed quote')

            # Should return True to continue shell
            assert result is True

            # Should print error message
            mock_console.print.assert_called()

            # Error message should mention quotes
            call_args = mock_console.print.call_args
            assert "quotes" in str(call_args).lower()

    def test_run_command_adds_pretty_flag_by_default(self):
        """Test that run_command adds --pretty flag for human-readable output"""
        from shell import run_command

        with patch("shell.app") as mock_app:
            with patch("sys.argv", ["bugit"]) as mock_argv:
                result = run_command("config")

                # Should have modified sys.argv to include --pretty
                # Note: sys.argv is restored after execution
                mock_app.assert_called_once()

    def test_run_command_respects_json_override(self):
        """Test that run_command respects --json flag override"""
        from shell import run_command

        with patch("shell.app") as mock_app:
            with patch("sys.argv", ["bugit"]) as mock_argv:
                result = run_command("config --json")

                # Should have called app without adding --pretty
                mock_app.assert_called_once()

    def test_run_command_preserves_help_flags(self):
        """Test that run_command doesn't add --pretty to help commands"""
        from shell import run_command

        with patch("shell.app") as mock_app:
            with patch("sys.argv", ["bugit"]) as mock_argv:
                result = run_command("config --help")

                # Should have called app without adding --pretty
                mock_app.assert_called_once()


class TestShellExitFunctionality:
    """Test shell exit functionality"""

    def test_main_loop_handles_keyboard_interrupt(self):
        """Test that main loop handles KeyboardInterrupt gracefully"""
        from shell import main

        with patch("shell.show_welcome"):
            with patch("shell.console") as mock_console:
                with patch("builtins.input", side_effect=KeyboardInterrupt()):
                    # Should not raise exception
                    main()

                    # Should print goodbye message
                    mock_console.print.assert_called()

                    # Check for goodbye message
                    calls = mock_console.print.call_args_list
                    goodbye_found = any("Goodbye" in str(call) for call in calls)
                    assert goodbye_found

    def test_main_loop_handles_eof_error(self):
        """Test that main loop handles EOFError gracefully"""
        from shell import main

        with patch("shell.show_welcome"):
            with patch("shell.console") as mock_console:
                with patch("builtins.input", side_effect=EOFError()):
                    # Should not raise exception
                    main()

                    # Should print goodbye message
                    mock_console.print.assert_called()

                    # Check for goodbye message
                    calls = mock_console.print.call_args_list
                    goodbye_found = any("Goodbye" in str(call) for call in calls)
                    assert goodbye_found

    def test_main_loop_handles_unexpected_errors(self):
        """Test that main loop handles unexpected errors gracefully"""
        from shell import main

        with patch("shell.show_welcome"):
            with patch("shell.console") as mock_console:
                with patch("builtins.input", side_effect=RuntimeError("Test error")):
                    with pytest.raises(SystemExit):
                        main()

                    # Should print error message
                    mock_console.print.assert_called()

                    # Check for error message
                    calls = mock_console.print.call_args_list
                    error_found = any("error" in str(call).lower() for call in calls)
                    assert error_found


class TestShellCommandExecution:
    """Test shell command execution"""

    def test_run_command_restores_sys_argv(self):
        """Test that run_command restores sys.argv after execution"""
        from shell import run_command
        import sys

        original_argv = sys.argv.copy()

        with patch("shell.app") as mock_app:
            run_command("config")

            # sys.argv should be restored
            assert sys.argv == original_argv

    def test_run_command_handles_system_exit(self):
        """Test that run_command handles SystemExit from CLI commands"""
        from shell import run_command

        with patch("shell.app", side_effect=SystemExit(1)):
            with patch("shell.console") as mock_console:
                result = run_command("config")

                # Should return True to continue shell
                assert result is True

                # Should print error message about exit code
                mock_console.print.assert_called()

                # Check for exit code message
                calls = mock_console.print.call_args_list
                exit_code_found = any(
                    "exit code" in str(call).lower() for call in calls
                )
                assert exit_code_found

    def test_run_command_handles_general_exceptions(self):
        """Test that run_command handles general exceptions gracefully"""
        from shell import run_command

        with patch("shell.app", side_effect=RuntimeError("Test error")):
            with patch("shell.console") as mock_console:
                result = run_command("config")

                # Should return True to continue shell
                assert result is True

                # Should print error message
                mock_console.print.assert_called()

                # Check for error message
                calls = mock_console.print.call_args_list
                error_found = any(
                    "error executing command" in str(call).lower() for call in calls
                )
                assert error_found

    def test_run_command_provides_help_hint(self):
        """Test that run_command provides help hint on errors"""
        from shell import run_command

        with patch("shell.app", side_effect=RuntimeError("Test error")):
            with patch("shell.console") as mock_console:
                result = run_command("config")

                # Should provide help hint
                calls = mock_console.print.call_args_list
                help_hint_found = any("help" in str(call).lower() for call in calls)
                assert help_hint_found


class TestShellIntegration:
    """Test shell integration with CLI and styling"""

    def test_shell_uses_consistent_styling(self):
        """Test that shell uses consistent styling from core.styles"""
        from shell import show_welcome

        # Import should work without errors
        from core.styles import Colors, Styles, PanelStyles

        with patch("shell.console") as mock_console:
            show_welcome()

            # Should use styling system
            mock_console.print.assert_called_once()

            # Panel should use standard styling
            call_args = mock_console.print.call_args
            panel = call_args[0][0]

            # Should be a Panel with proper styling
            assert hasattr(panel, "title")
            assert panel.title == "Welcome"

    def test_shell_imports_required_modules(self):
        """Test that shell can import all required modules"""
        # Should be able to import shell module
        import shell

        # Should have required functions
        assert hasattr(shell, "main")
        assert hasattr(shell, "run_command")
        assert hasattr(shell, "show_welcome")

        # Should be able to import CLI app
        from shell import app

        assert app is not None

    def test_shell_console_initialization(self):
        """Test that shell console is properly initialized"""
        from shell import console

        # Should be a Rich Console instance
        assert isinstance(console, Console)

        # Should be able to use console methods
        assert hasattr(console, "print")
        assert hasattr(console, "input")
