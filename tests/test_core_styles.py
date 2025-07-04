"""
Comprehensive tests for core/styles.py module.
Tests all formatting and styling functions with various input types.
"""

from datetime import datetime
from typing import Any

import pytest

from core import styles
from core.styles import Colors, Styles, TableStyles


class TestColorsDefinition:
    """Test the Colors class definitions"""

    def test_colors_are_defined(self):
        """Test that all required colors are defined"""
        required_colors = [
            "BRAND",
            "INTERACTIVE",
            "ERROR",
            "SUCCESS",
            "WARNING",
            "IDENTIFIER",
            "PRIMARY",
            "SECONDARY",
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "LOW",
        ]

        for color in required_colors:
            assert hasattr(Colors, color)
            assert isinstance(getattr(Colors, color), str)


class TestStylesFormatting:
    """Test the Styles class formatting functions"""

    def test_uuid_formatting(self):
        """Test UUID formatting function"""
        result = Styles.uuid("abc123")
        assert isinstance(result, str)
        assert "abc123" in result

        # Test with None
        result = Styles.uuid(None)
        assert isinstance(result, str)

    def test_index_formatting(self):
        """Test index formatting function"""
        result = Styles.index(1)
        assert isinstance(result, str)
        assert "1" in result

        result = Styles.index("5")
        assert isinstance(result, str)
        assert "5" in result

    def test_date_formatting(self):
        """Test date formatting function"""
        test_date = "2025-01-01T12:00:00"
        result = Styles.date(test_date)
        assert isinstance(result, str)
        assert "2025" in result

        # Test with datetime object
        dt = datetime(2025, 1, 1, 12, 0, 0)
        result = Styles.date(dt)
        assert isinstance(result, str)

    def test_severity_formatting(self):
        """Test severity formatting with all levels"""
        severities = ["low", "medium", "high", "critical"]

        for sev in severities:
            result = Styles.severity(sev)
            assert isinstance(result, str)
            assert sev.lower() in result.lower()

        # Test invalid severity
        result = Styles.severity("invalid")
        assert isinstance(result, str)

        # Test None severity
        result = Styles.severity(None)
        assert isinstance(result, str)

    def test_get_severity_color(self):
        """Test get_severity_color function"""
        severities = ["low", "medium", "high", "critical"]

        for sev in severities:
            result = Styles.get_severity_color(sev)
            assert isinstance(result, str)
            # Should return a color name without markup

        # Test invalid input
        result = Styles.get_severity_color("invalid")
        assert isinstance(result, str)

        result = Styles.get_severity_color(None)
        assert isinstance(result, str)

    def test_tags_formatting(self):
        """Test tags formatting function"""
        test_tags = ["ui", "auth", "critical"]
        result = Styles.tags(test_tags)
        assert isinstance(result, str)

        # Test empty tags
        result = Styles.tags([])
        assert isinstance(result, str)

        # Test None tags
        result = Styles.tags(None)
        assert isinstance(result, str)

    def test_title_formatting(self):
        """Test title formatting function"""
        test_title = "Test Bug Title"
        result = Styles.title(test_title)
        assert isinstance(result, str)
        assert "Test Bug Title" in result

        # Test empty title
        result = Styles.title("")
        assert isinstance(result, str)

        # Test None title
        result = Styles.title(None)
        assert isinstance(result, str)

    def test_description_formatting(self):
        """Test description formatting function"""
        test_desc = "This is a test description"
        result = Styles.description(test_desc)
        assert isinstance(result, str)
        assert "test description" in result

        # Test empty description
        result = Styles.description("")
        assert isinstance(result, str)

        # Test None description
        result = Styles.description(None)
        assert isinstance(result, str)

    def test_brand_formatting(self):
        """Test brand formatting function"""
        test_brand = "BugIt"
        result = Styles.brand(test_brand)
        assert isinstance(result, str)
        assert "BugIt" in result

        # Test empty brand
        result = Styles.brand("")
        assert isinstance(result, str)

    def test_status_formatting(self):
        """Test status formatting functions"""
        test_message = "Test message"

        # Test success
        result = Styles.success(test_message)
        assert isinstance(result, str)
        assert "Test message" in result

        # Test error
        result = Styles.error(test_message)
        assert isinstance(result, str)
        assert "Test message" in result

        # Test warning
        result = Styles.warning(test_message)
        assert isinstance(result, str)
        assert "Test message" in result

        # Test with empty strings
        assert isinstance(Styles.success(""), str)
        assert isinstance(Styles.error(""), str)
        assert isinstance(Styles.warning(""), str)

        # Test with None
        assert isinstance(Styles.success(None), str)
        assert isinstance(Styles.error(None), str)
        assert isinstance(Styles.warning(None), str)


class TestTableStyles:
    """Test the TableStyles class"""

    def test_issue_list_styles(self):
        """Test issue list table styles"""
        styles_dict = TableStyles.issue_list()

        assert isinstance(styles_dict, dict)

        # Check expected columns
        expected_columns = ["Index", "UUID", "Date", "Severity", "Tags", "Title"]
        for column in expected_columns:
            assert column in styles_dict

        # Verify color assignments
        assert styles_dict["Index"] == Colors.INTERACTIVE
        assert styles_dict["UUID"] == Colors.IDENTIFIER
        assert styles_dict["Date"] == Colors.SUCCESS
        assert styles_dict["Tags"] == Colors.WARNING
        assert styles_dict["Title"] == Colors.PRIMARY


class TestFormattingConsistency:
    """Test consistency across all formatting functions"""

    def test_all_functions_return_strings(self):
        """Test that all formatting functions return strings"""
        test_data = "test"

        formatting_functions = [
            Styles.uuid,
            Styles.index,
            Styles.date,
            Styles.severity,
            Styles.tags,
            Styles.title,
            Styles.description,
            Styles.brand,
            Styles.success,
            Styles.error,
            Styles.warning,
        ]

        for func in formatting_functions:
            result = func(test_data)
            assert isinstance(result, str), f"{func.__name__} should return string"

    def test_all_functions_handle_none(self):
        """Test that all formatting functions handle None gracefully"""
        formatting_functions = [
            Styles.uuid,
            Styles.index,
            Styles.date,
            Styles.severity,
            Styles.tags,
            Styles.title,
            Styles.description,
            Styles.brand,
            Styles.success,
            Styles.error,
            Styles.warning,
        ]

        for func in formatting_functions:
            result = func(None)
            assert isinstance(result, str), f"{func.__name__} should handle None"

    def test_all_functions_handle_empty_string(self):
        """Test that all formatting functions handle empty strings"""
        formatting_functions = [
            Styles.uuid,
            Styles.index,
            Styles.date,
            Styles.severity,
            Styles.tags,
            Styles.title,
            Styles.description,
            Styles.brand,
            Styles.success,
            Styles.error,
            Styles.warning,
        ]

        for func in formatting_functions:
            result = func("")
            assert isinstance(
                result, str
            ), f"{func.__name__} should handle empty string"


class TestEdgeCases:
    """Test edge cases and special inputs"""

    def test_severity_color_mapping(self):
        """Test that severity colors map correctly"""
        # Test that each severity level gets the correct color
        assert Styles.get_severity_color("critical") == Colors.CRITICAL
        assert Styles.get_severity_color("high") == Colors.HIGH
        assert Styles.get_severity_color("medium") == Colors.MEDIUM
        assert Styles.get_severity_color("low") == Colors.LOW

        # Test case insensitivity
        assert Styles.get_severity_color("CRITICAL") == Colors.CRITICAL
        assert Styles.get_severity_color("High") == Colors.HIGH

    def test_unicode_handling(self):
        """Test handling of unicode characters"""
        unicode_text = "Text with émojis 🚀 and ünïcödé"

        text_functions = [
            Styles.title,
            Styles.description,
            Styles.brand,
            Styles.success,
            Styles.error,
            Styles.warning,
        ]

        for func in text_functions:
            result = func(unicode_text)
            assert isinstance(result, str)
            assert "émojis" in result

    def test_large_inputs(self):
        """Test handling of large inputs"""
        large_text = "A" * 1000

        # Should handle large inputs without crashing
        result = Styles.title(large_text)
        assert isinstance(result, str)

        result = Styles.description(large_text)
        assert isinstance(result, str)

    def test_special_characters(self):
        """Test handling of special characters"""
        special_text = "Text with @#$%^&*()[]{}|\\;:'\",.<>?/`~"

        text_functions = [
            Styles.title,
            Styles.description,
            Styles.brand,
            Styles.success,
            Styles.error,
            Styles.warning,
        ]

        for func in text_functions:
            result = func(special_text)
            assert isinstance(result, str)


class TestRichMarkupGeneration:
    """Test that Rich markup is properly generated"""

    def test_markup_structure(self):
        """Test that markup follows Rich format"""
        test_text = "test"

        # UUID should use IDENTIFIER color
        result = Styles.uuid(test_text)
        assert f"[{Colors.IDENTIFIER}]" in result
        assert f"[/{Colors.IDENTIFIER}]" in result

        # Title should use PRIMARY color
        result = Styles.title(test_text)
        assert f"[{Colors.PRIMARY}]" in result
        assert f"[/{Colors.PRIMARY}]" in result

        # Error should use ERROR color
        result = Styles.error(test_text)
        assert f"[{Colors.ERROR}]" in result
        assert f"[/{Colors.ERROR}]" in result

    def test_severity_specific_colors(self):
        """Test that severity uses the correct colors"""
        # Critical should use CRITICAL color
        result = Styles.severity("critical")
        assert f"[{Colors.CRITICAL}]" in result

        # High should use HIGH color
        result = Styles.severity("high")
        assert f"[{Colors.HIGH}]" in result

        # Medium should use MEDIUM color
        result = Styles.severity("medium")
        assert f"[{Colors.MEDIUM}]" in result

        # Low should use LOW color
        result = Styles.severity("low")
        assert f"[{Colors.LOW}]" in result
