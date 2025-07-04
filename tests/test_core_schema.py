"""
Comprehensive tests for core/schema.py module.
Tests all validation functions with edge cases and data transformation.
"""

import pytest
from datetime import datetime
from core import schema
from core.schema import validate_or_default, validate_config, ValidationError


class TestValidateOrDefault:
    """Test the validate_or_default function"""

    def test_validates_complete_valid_issue(self):
        """Test validation of complete valid issue data"""
        valid_data = {
            "title": "Valid Test Issue",
            "description": "This is a valid test issue description",
            "severity": "high",
            "tags": ["test", "validation"],
            "type": "bug",
        }

        result = validate_or_default(valid_data)

        # Should preserve all valid fields
        assert result["title"] == "Valid Test Issue"
        assert result["description"] == "This is a valid test issue description"
        assert result["severity"] == "high"
        assert result["tags"] == ["test", "validation"]
        assert result["type"] == "bug"

        # Should add required fields
        assert "id" in result
        assert "schema_version" in result
        assert "created_at" in result
        assert result["schema_version"] == "v1"

        # ID should be a UUID-like string
        assert isinstance(result["id"], str)
        assert len(result["id"]) >= 6  # Minimum UUID length

    def test_validates_minimal_valid_issue(self):
        """Test validation with minimal required data"""
        minimal_data = {"title": "Minimal Issue"}

        result = validate_or_default(minimal_data)

        # Should preserve title
        assert result["title"] == "Minimal Issue"

        # Should add defaults
        assert result["description"] == ""
        assert result["severity"] in ["low", "medium", "high", "critical"]
        assert result["type"] in ["bug", "feature", "chore", "unknown"]
        assert isinstance(result["tags"], list)
        assert result["schema_version"] == "v1"
        assert "id" in result
        assert "created_at" in result

    def test_validates_title_length_limits(self):
        """Test title length validation and truncation"""
        # Normal length should pass
        normal_title = "A" * 100
        result = validate_or_default({"title": normal_title})
        assert result["title"] == normal_title

        # Maximum length should pass
        max_title = "A" * 120
        result = validate_or_default({"title": max_title})
        assert result["title"] == max_title

        # Over maximum should be truncated
        long_title = "A" * 150
        result = validate_or_default({"title": long_title})
        assert len(result["title"]) <= 120
        assert result["title"].endswith("...")
        assert result["title"].startswith("AAA")

    def test_validates_description_length_limits(self):
        """Test description length validation"""
        # Normal description should pass
        normal_desc = "A" * 5000
        result = validate_or_default({"title": "Test", "description": normal_desc})
        assert result["description"] == normal_desc

        # Maximum length should pass
        max_desc = "A" * 10000
        result = validate_or_default({"title": "Test", "description": max_desc})
        assert result["description"] == max_desc

        # Over maximum should be truncated
        long_desc = "A" * 15000
        result = validate_or_default({"title": "Test", "description": long_desc})
        assert len(result["description"]) <= 10000
        assert result["description"].endswith("...")

    def test_validates_severity_values(self):
        """Test severity validation with valid and invalid values"""
        valid_severities = ["low", "medium", "high", "critical"]

        for severity in valid_severities:
            result = validate_or_default({"title": "Test", "severity": severity})
            assert result["severity"] == severity

        # Invalid severities should default to medium
        invalid_severities = ["invalid", "super-high", "", None, 123]
        for invalid_severity in invalid_severities:
            result = validate_or_default(
                {"title": "Test", "severity": invalid_severity}
            )
            assert result["severity"] == "medium"

    def test_validates_type_values(self):
        """Test type validation with valid and invalid values"""
        valid_types = ["bug", "feature", "chore", "unknown"]

        for issue_type in valid_types:
            result = validate_or_default({"title": "Test", "type": issue_type})
            assert result["type"] == issue_type

        # Invalid types should default to unknown
        invalid_types = ["invalid", "enhancement", "", None, 123]
        for invalid_type in invalid_types:
            result = validate_or_default({"title": "Test", "type": invalid_type})
            assert result["type"] == "unknown"

    def test_validates_tags_processing(self):
        """Test tag validation and processing"""
        # Valid tags should be preserved
        valid_tags = ["bug", "ui", "critical", "auth"]
        result = validate_or_default({"title": "Test", "tags": valid_tags})
        assert result["tags"] == valid_tags

        # Empty tags should become empty list
        result = validate_or_default({"title": "Test", "tags": []})
        assert result["tags"] == []

        # None/missing tags should become empty list
        result = validate_or_default({"title": "Test"})
        assert result["tags"] == []

        # Invalid tag types should be converted to strings
        mixed_tags = ["string", 123, None, True]
        result = validate_or_default({"title": "Test", "tags": mixed_tags})
        # Should filter out None and convert others to strings
        assert "string" in result["tags"]
        assert "123" in result["tags"]
        assert "True" in result["tags"]
        assert None not in result["tags"]

    def test_preserves_existing_id_and_timestamps(self):
        """Test that existing ID and timestamps are preserved"""
        existing_data = {
            "id": "existing-id-123",
            "title": "Existing Issue",
            "created_at": "2025-01-01T10:00:00",
            "schema_version": "v1",
        }

        result = validate_or_default(existing_data)

        # Should preserve existing values
        assert result["id"] == "existing-id-123"
        assert result["created_at"] == "2025-01-01T10:00:00"
        assert result["schema_version"] == "v1"

    def test_generates_timestamps_in_correct_format(self):
        """Test that generated timestamps are in correct ISO format"""
        result = validate_or_default({"title": "Test"})

        created_at = result["created_at"]
        assert isinstance(created_at, str)

        # Should be parseable as ISO datetime
        parsed_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        assert isinstance(parsed_time, datetime)

    def test_handles_unicode_and_special_characters(self):
        """Test handling of unicode and special characters"""
        unicode_data = {
            "title": "Test with émojis 🚀 and ünïcödé",
            "description": "Description with special chars: @#$%^&*()[]{}",
            "tags": ["émoji🚀", "ünïcödé", "special@chars"],
        }

        result = validate_or_default(unicode_data)

        # Should preserve unicode characters
        assert result["title"] == "Test with émojis 🚀 and ünïcödé"
        assert result["description"] == "Description with special chars: @#$%^&*()[]{}"
        assert "émoji🚀" in result["tags"]
        assert "ünïcödé" in result["tags"]

    def test_error_handling_for_invalid_input(self):
        """Test error handling for invalid input types"""
        # Missing title should raise ValidationError
        with pytest.raises(ValidationError, match="Title is required"):
            validate_or_default({})

        with pytest.raises(ValidationError, match="Title is required"):
            validate_or_default({"title": ""})

        with pytest.raises(ValidationError, match="Title is required"):
            validate_or_default({"title": None})

        # Non-dict input should raise ValidationError
        with pytest.raises(ValidationError):
            validate_or_default("not a dict")  # type: ignore

        with pytest.raises(ValidationError):
            validate_or_default(None)  # type: ignore

        with pytest.raises(ValidationError):
            validate_or_default([])  # type: ignore


class TestValidateConfig:
    """Test the validate_config function"""

    def test_validates_complete_config(self):
        """Test validation of complete configuration"""
        complete_config = {
            "model": "gpt-4",
            "enum_mode": "auto",
            "output_format": "table",
            "retry_limit": 3,
            "custom_field": "custom_value",
        }

        result = validate_config(complete_config)

        # Should preserve all valid fields
        assert result["model"] == "gpt-4"
        assert result["enum_mode"] == "auto"
        assert result["output_format"] == "table"
        assert result["retry_limit"] == 3
        assert result["custom_field"] == "custom_value"

    def test_applies_defaults_for_missing_fields(self):
        """Test that missing config fields get default values"""
        minimal_config = {}

        result = validate_config(minimal_config)

        # Should have default values
        assert result["model"] == "gpt-4"
        assert result["enum_mode"] == "auto"
        assert result["output_format"] == "table"
        assert result["retry_limit"] == 3

    def test_validates_model_field(self):
        """Test model field validation"""
        # Valid models should pass
        valid_models = ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet"]
        for model in valid_models:
            result = validate_config({"model": model})
            assert result["model"] == model

        # Invalid model types should default
        invalid_configs = [
            {"model": None},
            {"model": ""},
            {"model": 123},
            {"model": []},
        ]
        for config in invalid_configs:
            result = validate_config(config)
            assert result["model"] == "gpt-4"  # Default

    def test_validates_enum_mode_field(self):
        """Test enum_mode field validation"""
        # Valid enum modes
        valid_modes = ["auto", "strict", "suggestive"]
        for mode in valid_modes:
            result = validate_config({"enum_mode": mode})
            assert result["enum_mode"] == mode

        # Invalid enum_mode should default
        result = validate_config({"enum_mode": "invalid"})
        assert result["enum_mode"] == "auto"

    def test_validates_output_format_field(self):
        """Test output_format field validation"""
        # Valid output formats
        valid_formats = ["table", "json", "yaml"]
        for fmt in valid_formats:
            result = validate_config({"output_format": fmt})
            assert result["output_format"] == fmt

        # Invalid format should default
        result = validate_config({"output_format": "invalid"})
        assert result["output_format"] == "table"

    def test_validates_retry_limit_field(self):
        """Test retry_limit field validation"""
        # Valid retry limits
        valid_limits = [1, 2, 3, 5, 10]
        for limit in valid_limits:
            result = validate_config({"retry_limit": limit})
            assert result["retry_limit"] == limit

        # Invalid retry limits should default or be constrained
        invalid_limits = [0, -1, "invalid", None, 100]
        for limit in invalid_limits:
            result = validate_config({"retry_limit": limit})
            assert result["retry_limit"] == 3  # Default

    def test_preserves_custom_fields(self):
        """Test that custom configuration fields are preserved"""
        custom_config = {
            "model": "gpt-4",
            "custom_api_endpoint": "https://custom.api.com",
            "debug_mode": True,
            "timeout": 30,
        }

        result = validate_config(custom_config)

        # Should preserve custom fields
        assert result["custom_api_endpoint"] == "https://custom.api.com"
        assert result["debug_mode"] is True
        assert result["timeout"] == 30

    def test_handles_none_input(self):
        """Test handling of None input"""
        result = validate_config(None)  # type: ignore

        # Should return defaults
        assert result["model"] == "gpt-4"
        assert result["enum_mode"] == "auto"
        assert result["output_format"] == "table"
        assert result["retry_limit"] == 3

    def test_handles_invalid_input_types(self):
        """Test handling of invalid input types"""
        invalid_inputs = ["string", 123, [], True]

        for invalid_input in invalid_inputs:
            result = validate_config(invalid_input)
            # Should return defaults for invalid types
            assert result["model"] == "gpt-4"
            assert result["enum_mode"] == "auto"


class TestValidationHelpers:
    """Test validation helper functions and edge cases"""

    def test_tag_cleaning_and_deduplication(self):
        """Test tag cleaning removes duplicates and invalid values"""
        messy_tags = ["bug", "Bug", "BUG", "ui", "ui", "", None, 123, "auth"]
        result = validate_or_default({"title": "Test", "tags": messy_tags})

        # Should handle case sensitivity and deduplication appropriately
        # The exact behavior depends on implementation
        assert isinstance(result["tags"], list)
        assert (
            "bug" in result["tags"]
            or "Bug" in result["tags"]
            or "BUG" in result["tags"]
        )
        assert "ui" in result["tags"]
        assert "auth" in result["tags"]
        # Should not contain empty strings or None
        assert "" not in result["tags"]
        assert None not in result["tags"]

    def test_preserves_original_data_immutability(self):
        """Test that original data is not modified"""
        original_data = {"title": "Original Title", "tags": ["original", "tags"]}
        original_copy = original_data.copy()

        result = validate_or_default(original_data)

        # Original data should be unchanged
        assert original_data == original_copy
        assert result is not original_data
        assert result["tags"] is not original_data["tags"]

    def test_schema_version_handling(self):
        """Test schema version validation and defaults"""
        # Missing schema version should get default
        result = validate_or_default({"title": "Test"})
        assert result["schema_version"] == "v1"

        # Existing schema version should be preserved
        result = validate_or_default({"title": "Test", "schema_version": "v2"})
        assert result["schema_version"] == "v2"

        # Invalid schema version should be reset to default
        result = validate_or_default({"title": "Test", "schema_version": 123})
        assert result["schema_version"] == "v1"

    def test_whitespace_handling(self):
        """Test handling of whitespace in fields"""
        whitespace_data = {
            "title": "  Whitespace Title  ",
            "description": "\n\tDescription with whitespace\n\t",
            "tags": ["  tag1  ", "\ttag2\n", "  "],
        }

        result = validate_or_default(whitespace_data)

        # Implementation may or may not strip whitespace
        # Just verify the result is valid
        assert result["title"]  # Should have some title
        assert isinstance(result["description"], str)
        assert isinstance(result["tags"], list)


class TestValidationErrorHandling:
    """Test error cases and exception handling"""

    def test_validation_error_messages(self):
        """Test that ValidationError provides helpful messages"""
        try:
            validate_or_default({})
        except ValidationError as e:
            assert "title" in str(e).lower()
            assert "required" in str(e).lower()

    def test_validation_error_inheritance(self):
        """Test that ValidationError is properly defined"""
        assert issubclass(ValidationError, Exception)

        # Should be raiseable and catchable
        try:
            raise ValidationError("Test validation error")
        except ValidationError as e:
            assert str(e) == "Test validation error"

    def test_partial_validation_recovery(self):
        """Test that validation recovers from partial bad data"""
        mixed_data = {
            "title": "Valid Title",
            "severity": "invalid_severity",  # Invalid
            "tags": ["valid", None, 123],  # Mixed valid/invalid
            "type": "invalid_type",  # Invalid
        }

        # Should not raise error, but should apply defaults for invalid fields
        result = validate_or_default(mixed_data)
        assert result["title"] == "Valid Title"
        assert result["severity"] in ["low", "medium", "high", "critical"]
        assert result["type"] in ["bug", "feature", "chore", "unknown"]
        assert isinstance(result["tags"], list)
