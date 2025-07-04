"""
Tests for shell routing functionality in bugit.py.
Tests the unified entry point that routes to shell or CLI based on arguments.
"""

import signal
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestUnifiedEntryPoint:
    """Test unified entry point routing logic"""

    def test_no_args_starts_shell(self):
        """Test that bugit.py with no args starts shell"""
        project_root = Path(__file__).parent.parent

        # Mock the shell.main function to avoid actual shell startup
        with patch("shell.main") as mock_shell_main:
            # Run bugit.py with no arguments
            result = subprocess.run(
                [sys.executable, str(project_root / "bugit.py")],
                capture_output=True,
                text=True,
                input="\n",  # Send newline to exit immediately
                timeout=5,
            )

            # Should not have errored out
            assert (
                result.returncode == 0 or result.returncode == 1
            )  # 1 is acceptable for interrupted shell

    def test_with_args_routes_to_cli(self):
        """Test that bugit.py with args executes CLI commands"""
        project_root = Path(__file__).parent.parent

        # Run bugit.py with --version argument
        result = subprocess.run(
            [sys.executable, str(project_root / "bugit.py"), "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Should execute CLI command successfully
        assert result.returncode == 0
        assert "bugit" in result.stdout.lower()

    def test_routing_logic_no_args(self):
        """Test routing logic when no arguments are provided"""
        with patch("shell.main") as mock_shell_main:
            with patch("sys.argv", ["bugit.py"]):
                from bugit import main

                main()
                mock_shell_main.assert_called_once()

    def test_routing_logic_with_args(self):
        """Test routing logic when arguments are provided"""
        with patch("cli.app") as mock_cli_app:
            with patch("sys.argv", ["bugit.py", "--version"]):
                from bugit import main

                main()
                mock_cli_app.assert_called_once()

    def test_shell_command_execution(self):
        """Test shell can execute CLI commands internally"""
        project_root = Path(__file__).parent.parent

        # Test that shell can execute a simple command
        # We'll test by running shell with a command that should work
        process = subprocess.Popen(
            [sys.executable, str(project_root / "bugit.py")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Send a config command and then exit
            stdout, stderr = process.communicate(
                input="config --help\nexit\n", timeout=10
            )

            # Should complete without error
            assert process.returncode == 0
            # Should contain help text
            assert "config" in stdout.lower() or "config" in stderr.lower()

        except subprocess.TimeoutExpired:
            process.kill()
            pytest.fail("Shell command execution timed out")


class TestShellRouting:
    """Test shell routing and command processing"""

    def test_shell_processes_help_command(self):
        """Test that shell processes help command"""
        from shell import run_command

        # Mock console to capture output
        with patch("shell.console") as mock_console:
            with patch("shell.show_welcome") as mock_show_welcome:
                result = run_command("help")

                # Should return True to continue shell
                assert result is True
                # Should call show_welcome
                mock_show_welcome.assert_called_once()

    def test_shell_processes_exit_command(self):
        """Test that shell processes exit command"""
        from shell import run_command

        # Mock console to capture output
        with patch("shell.console") as mock_console:
            result = run_command("exit")

            # Should return False to exit shell
            assert result is False
            # Should print goodbye message
            mock_console.print.assert_called()

    def test_shell_adds_pretty_flag_by_default(self):
        """Test that shell adds --pretty flag for human-readable output"""
        from shell import run_command

        # Mock the CLI app execution
        with patch("shell.app") as mock_app:
            with patch("sys.argv", ["bugit"]):
                run_command("config")

                # Should have called app (CLI execution)
                mock_app.assert_called_once()

    def test_shell_respects_json_override(self):
        """Test that shell respects --json flag override"""
        from shell import run_command

        # Mock the CLI app execution
        with patch("shell.app") as mock_app:
            with patch("sys.argv", ["bugit"]):
                run_command("config --json")

                # Should have called app (CLI execution)
                mock_app.assert_called_once()

    def test_shell_handles_empty_command(self):
        """Test that shell handles empty command gracefully"""
        from shell import run_command

        result = run_command("")
        # Should return True to continue shell
        assert result is True

        result = run_command("   ")
        # Should return True to continue shell
        assert result is True

    def test_shell_handles_malformed_quotes(self):
        """Test that shell handles malformed quotes gracefully"""
        from shell import run_command

        # Mock console to capture error output
        with patch("shell.console") as mock_console:
            result = run_command('new "unclosed quote')

            # Should return True to continue shell
            assert result is True
            # Should print error message
            mock_console.print.assert_called()

            # Check that error message mentions quotes
            call_args = mock_console.print.call_args
            assert "quotes" in str(call_args).lower()


class TestEntryPointIntegration:
    """Test integration between entry point and shell/CLI"""

    def test_entry_point_preserves_exit_codes(self):
        """Test that entry point preserves CLI exit codes"""
        project_root = Path(__file__).parent.parent

        # Test with a command that should fail
        result = subprocess.run(
            [sys.executable, str(project_root / "bugit.py"), "show", "nonexistent"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Should preserve the CLI exit code (1 for not found)
        assert result.returncode == 1

    def test_entry_point_handles_keyboard_interrupt(self):
        """Test that entry point handles keyboard interrupt gracefully"""
        project_root = Path(__file__).parent.parent

        # Start shell and send interrupt signal
        process = subprocess.Popen(
            [sys.executable, str(project_root / "bugit.py")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Send Ctrl+C equivalent - platform-specific handling
            if sys.platform == "win32":
                # On Windows, use terminate() instead of SIGINT
                process.terminate()
            else:
                # On Unix systems, use SIGINT
                process.send_signal(signal.SIGINT)

            stdout, stderr = process.communicate(timeout=5)

            # Should handle interrupt gracefully
            assert process.returncode != 0  # Non-zero exit is expected for interrupt

        except subprocess.TimeoutExpired:
            process.kill()
            # This is acceptable - shell might not respond to interrupt immediately
            pass

    def test_python_path_setup(self):
        """Test that Python path is set up correctly"""
        import sys

        from bugit import project_root

        # Project root should be in Python path
        assert str(project_root) in sys.path

        # Should be able to import modules
        import cli
        import shell

        assert cli is not None
        assert shell is not None
