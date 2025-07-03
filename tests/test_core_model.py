"""
Comprehensive tests for core/model.py module.
Tests all LangGraph integration functions with proper mocking and error handling.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import json
from typing import Dict, Any

from core import model
from core.model import (
    create_llm_chain, analyze_bug_description, validate_and_clean_result,
    handle_retry_logic, should_retry, create_processing_graph,
    process_description, setup_langgraph, test_model_connection,
    ProcessingState, ModelError
)


class TestProcessingState:
    """Test the ProcessingState dataclass"""
    
    def test_processing_state_creation(self):
        """Test creating ProcessingState with all fields"""
        state = ProcessingState(
            input_description="Test bug",
            retry_count=1,
            max_retries=3,
            processed_result={"title": "Test"},
            error_message="Test error"
        )
        
        assert state.input_description == "Test bug"
        assert state.retry_count == 1
        assert state.max_retries == 3
        assert state.processed_result == {"title": "Test"}
        assert state.error_message == "Test error"
    
    def test_processing_state_defaults(self):
        """Test ProcessingState with minimal fields"""
        state = ProcessingState(input_description="Test bug")
        
        assert state.input_description == "Test bug"
        assert state.retry_count == 0
        assert state.max_retries == 3
        assert state.processed_result is None
        assert state.error_message is None


class TestCreateLlmChain:
    """Test the create_llm_chain function"""
    
    @patch('core.model.ChatOpenAI')
    @patch('core.model.load_config')
    def test_creates_openai_chain_with_config(self, mock_load_config, mock_chat_openai):
        """Test creating LLM chain with configuration"""
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        mock_load_config.return_value = {
            'model': 'gpt-4',
            'openai_api_key': 'test-key'
        }
        
        result = create_llm_chain()
        
        # Should create ChatOpenAI with correct parameters
        mock_chat_openai.assert_called_once()
        assert result == mock_llm
    
    @patch('core.model.load_config')
    def test_raises_error_without_api_key(self, mock_load_config):
        """Test that missing API key raises ModelError"""
        mock_load_config.return_value = {'model': 'gpt-4'}
        
        with pytest.raises(ModelError, match="API key not configured"):
            create_llm_chain()


class TestAnalyzeBugDescription:
    """Test the analyze_bug_description function"""
    
    @patch('core.model.create_llm_chain')
    def test_analyzes_bug_with_mock_llm(self, mock_create_llm):
        """Test bug analysis with mocked LLM response"""
        mock_response = Mock()
        mock_response.content = json.dumps({
            "title": "Login Bug",
            "severity": "high",
            "tags": ["auth", "login"],
            "type": "bug"
        })
        
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_create_llm.return_value = mock_llm
        
        state = ProcessingState(input_description="Users can't log in")
        
        result = analyze_bug_description(state)
        
        assert result.processed_result is not None
        assert result.processed_result['title'] == "Login Bug"
        assert result.processed_result['severity'] == "high"
        assert result.error_message is None
    
    @patch('core.model.create_llm_chain')
    def test_handles_llm_error_gracefully(self, mock_create_llm):
        """Test handling LLM errors during analysis"""
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("API Error")
        mock_create_llm.return_value = mock_llm
        
        state = ProcessingState(input_description="Test bug")
        
        result = analyze_bug_description(state)
        
        assert result.processed_result is None
        assert result.error_message is not None
        assert "API Error" in result.error_message


class TestValidateAndCleanResult:
    """Test the validate_and_clean_result function"""
    
    def test_validates_complete_result(self):
        """Test validation of complete, valid result"""
        result = {
            "title": "Valid Bug Title",
            "severity": "high",
            "tags": ["ui", "critical"],
            "type": "bug"
        }
        original_description = "Original bug description"
        
        cleaned = validate_and_clean_result(result, original_description)
        
        assert cleaned['title'] == "Valid Bug Title"
        assert cleaned['severity'] == "high"
        assert cleaned['tags'] == ["ui", "critical"]
        assert cleaned['type'] == "bug"
        assert cleaned['description'] == original_description
    
    def test_applies_defaults_for_missing_fields(self):
        """Test that missing fields get appropriate defaults"""
        result = {"title": "Minimal Bug"}
        original_description = "Test description"
        
        cleaned = validate_and_clean_result(result, original_description)
        
        assert cleaned['title'] == "Minimal Bug"
        assert cleaned['severity'] in ['low', 'medium', 'high', 'critical']
        assert isinstance(cleaned['tags'], list)
        assert cleaned['type'] in ['bug', 'feature', 'chore', 'unknown']
        assert cleaned['description'] == original_description
    
    def test_cleans_invalid_severity(self):
        """Test cleaning invalid severity values"""
        result = {
            "title": "Test Bug",
            "severity": "super-critical",  # Invalid
            "tags": ["test"],
            "type": "bug"
        }
        
        cleaned = validate_and_clean_result(result, "Test")
        
        assert cleaned['severity'] in ['low', 'medium', 'high', 'critical']
    
    def test_truncates_long_title(self):
        """Test truncation of overly long titles"""
        long_title = "A" * 150  # Longer than 120 chars
        result = {"title": long_title, "severity": "medium"}
        
        cleaned = validate_and_clean_result(result, "Test")
        
        assert len(cleaned['title']) <= 120
        assert cleaned['title'].endswith('...')


class TestRetryLogic:
    """Test retry logic functions"""
    
    def test_should_retry_with_success(self):
        """Test should_retry returns 'success' when result exists"""
        state = ProcessingState(
            input_description="Test",
            processed_result={"title": "Success"}
        )
        
        result = should_retry(state)
        assert result == "success"
    
    def test_should_retry_with_error_and_retries_available(self):
        """Test should_retry returns 'retry' when error exists and retries available"""
        state = ProcessingState(
            input_description="Test",
            error_message="Some error",
            retry_count=1,
            max_retries=3
        )
        
        result = should_retry(state)
        assert result == "retry"
    
    def test_should_retry_max_retries_exceeded(self):
        """Test should_retry returns proper value when max retries exceeded"""
        state = ProcessingState(
            input_description="Test",
            error_message="Some error",
            retry_count=3,
            max_retries=3
        )
        
        result = should_retry(state)
        assert result == "max_retries_exceeded"
    
    def test_handle_retry_logic_increments_count(self):
        """Test that handle_retry_logic increments retry count"""
        state = ProcessingState(
            input_description="Test",
            retry_count=1,
            max_retries=3
        )
        
        result = handle_retry_logic(state)
        
        assert result.retry_count == 2
        assert result.error_message is None  # Reset error for retry
    
    def test_handle_retry_logic_raises_on_max_retries(self):
        """Test that handle_retry_logic raises error when max retries exceeded"""
        state = ProcessingState(
            input_description="Test",
            retry_count=3,
            max_retries=3,
            error_message="Final error"
        )
        
        with pytest.raises(ModelError, match="failed after 3 retries"):
            handle_retry_logic(state)

    def test_handle_retry_logic_exceeds_max_retries(self):
        """Test handle_retry_logic when retry attempts exceed maximum allowed"""
        from core.model import handle_retry_logic, ProcessingState, ModelError
        
        # Create a state that has EXACTLY reached max retries (not exceeded)
        # This triggers the max retries exceeded condition
        state = ProcessingState(
            input_description="test description for max retry testing",
            retry_count=3,  # Exactly at max retries
            max_retries=3,
            error_message="Final error that triggers max retry handling"
        )
        
        # This should raise ModelError when max retries are exceeded
        with pytest.raises(ModelError) as exc_info:
            handle_retry_logic(state)
        
        # Verify the exact error message format
        error_msg = str(exc_info.value)
        assert "LLM processing failed after 3 retries" in error_msg
        assert "Last error: Final error that triggers max retry handling" in error_msg
        
        # Verify this is the exact format from the code
        expected_msg = "LLM processing failed after 3 retries. Last error: Final error that triggers max retry handling"
        assert error_msg == expected_msg


class TestProcessDescription:
    """Test the main process_description function"""
    
    @patch('core.model.create_processing_graph')
    @patch('core.model.load_config')
    def test_processes_description_successfully(self, mock_load_config, mock_create_graph):
        """Test successful processing of bug description"""
        mock_load_config.return_value = {
            'openai_api_key': 'test-key',
            'retry_limit': 3
        }
        
        # Mock the graph workflow
        mock_graph = Mock()
        mock_graph.invoke.return_value = {
            'processed_result': {
                'title': 'Processed Bug Title',
                'description': 'Original description',
                'severity': 'high',
                'tags': ['processed'],
                'type': 'bug'
            }
        }
        mock_create_graph.return_value = mock_graph
        
        result = process_description("Test bug description")
        
        assert result['title'] == 'Processed Bug Title'
        assert result['severity'] == 'high'
        assert result['tags'] == ['processed']
        assert result['type'] == 'bug'
    
    @patch('core.model.load_config')
    def test_handles_missing_api_key(self, mock_load_config):
        """Test handling of missing API key"""
        mock_load_config.return_value = {}  # No API key
        
        with pytest.raises(ModelError, match="API key not configured"):
            process_description("Test bug description")
    
    def test_validates_empty_description(self):
        """Test validation of empty description"""
        with pytest.raises(ModelError, match="Description cannot be empty"):
            process_description("")
        
        with pytest.raises(ModelError, match="Description cannot be empty"):
            process_description("   ")


class TestSetupLanggraph:
    """Test the setup_langgraph function"""
    
    @patch('core.model.create_llm_chain')
    @patch('core.model.load_config')
    def test_sets_up_langgraph_successfully(self, mock_load_config, mock_create_llm):
        """Test successful LangGraph setup"""
        mock_load_config.return_value = {
            'openai_api_key': 'test-key'
        }
        
        mock_response = Mock()
        mock_response.content = "Hello response"
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_create_llm.return_value = mock_llm
        
        result = setup_langgraph()
        
        assert result is True
        mock_create_llm.assert_called_once()
    
    @patch('core.model.load_config')
    def test_handles_missing_api_key(self, mock_load_config):
        """Test handling of missing API key"""
        mock_load_config.return_value = {}  # No API key
        
        result = setup_langgraph()
        assert result is False


class TestModelConnection:
    """Test the test_model_connection function"""
    
    @patch('core.model.create_llm_chain')
    @patch('core.model.load_config')
    def test_successful_connection(self, mock_load_config, mock_create_llm):
        """Test successful model connection test"""
        mock_load_config.return_value = {
            'openai_api_key': 'test-key'
        }
        
        mock_response = Mock()
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_create_llm.return_value = mock_llm
        
        result = test_model_connection()
        
        assert result is True
        mock_llm.invoke.assert_called_once()
    
    @patch('core.model.load_config')
    def test_connection_failure_no_api_key(self, mock_load_config):
        """Test model connection failure due to missing API key"""
        mock_load_config.return_value = {}  # No API key
        
        result = test_model_connection()
        
        assert result is False
    
    @patch('core.model.create_llm_chain')
    @patch('core.model.load_config')
    def test_connection_failure_llm_error(self, mock_load_config, mock_create_llm):
        """Test model connection failure due to LLM error"""
        mock_load_config.return_value = {
            'openai_api_key': 'test-key'
        }
        mock_create_llm.side_effect = Exception("Connection failed")
        
        result = test_model_connection()
        
        assert result is False


class TestModelError:
    """Test the ModelError exception class"""
    
    def test_model_error_creation(self):
        """Test creating ModelError with message"""
        error = ModelError("Test error message")
        
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
    
    def test_model_error_inheritance(self):
        """Test ModelError inheritance hierarchy"""
        assert issubclass(ModelError, Exception)
        
        # Should be raiseable and catchable
        try:
            raise ModelError("Test error")
        except ModelError as e:
            assert str(e) == "Test error"
        except Exception:
            pytest.fail("ModelError should be catchable as ModelError")


class TestCreateProcessingGraph:
    """Test the create_processing_graph function"""
    
    def test_creates_graph_successfully(self):
        """Test that processing graph is created successfully"""
        graph = create_processing_graph()
        
        # Should return a compiled graph
        assert graph is not None
        # Graph should be callable
        assert hasattr(graph, 'invoke')


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases"""
    
    def test_validation_and_cleaning_integration(self):
        """Test integration of validation and cleaning"""
        # Test with problematic data that needs cleaning
        result = {
            'title': 'A' * 150,  # Too long
            'severity': 'invalid-severity',  # Invalid
            'tags': ['valid', None, '', 123],  # Mixed valid/invalid
            'type': 'unknown-type'  # Invalid
        }
        
        cleaned = validate_and_clean_result(result, "Original description")
        
        # Should be cleaned and validated
        assert len(cleaned['title']) <= 120
        assert cleaned['severity'] in ['low', 'medium', 'high', 'critical']
        assert isinstance(cleaned['tags'], list)
        assert cleaned['type'] in ['bug', 'feature', 'chore', 'unknown']
        assert cleaned['description'] == "Original description"
    
    def test_empty_title_handling(self):
        """Test handling of empty or missing titles"""
        result = {"title": "", "severity": "medium"}
        
        cleaned = validate_and_clean_result(result, "This is the description")
        
        # Should generate title from description
        assert cleaned['title'] != ""
        assert len(cleaned['title']) > 0


class TestModelErrorPaths:
    """Test error paths and edge cases to improve coverage"""
    
    @patch('core.model.load_config')
    def test_create_llm_chain_initialization_error(self, mock_load_config):
        """Test lines 65-66: LLM initialization error handling"""
        mock_load_config.return_value = {
            'openai_api_key': 'sk-test-key',
            'model': 'gpt-4'
        }
        
        # Mock ChatOpenAI to raise an exception during initialization
        with patch('core.model.ChatOpenAI') as mock_chat:
            mock_chat.side_effect = Exception("API key format invalid")
            
            with pytest.raises(ModelError, match="Failed to initialize OpenAI model"):
                create_llm_chain()
    
    @patch('core.model.create_llm_chain')
    def test_analyze_bug_json_extraction_fallback(self, mock_create_llm):
        """Test line 124: JSON extraction when LLM returns extra text"""
        # Mock LLM to return text with JSON embedded (tests JSON extraction)
        mock_response = MagicMock()
        mock_response.content = 'Here is the analysis: {"title": "Test Issue", "description": "test", "severity": "high", "type": "bug", "tags": ["test"]} Hope this helps!'
        
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_create_llm.return_value = mock_llm
        
        state = ProcessingState(input_description="Test bug description")
        result_state = analyze_bug_description(state)
        
        # Should successfully extract and process the JSON
        assert result_state.processed_result is not None
        assert result_state.processed_result['title'] == 'Test Issue'
        assert result_state.error_message is None
    
    @patch('core.model.create_llm_chain')
    def test_analyze_bug_json_decode_error(self, mock_create_llm):
        """Test lines 135-136: JSON decode error handling"""
        # Mock LLM to return invalid JSON
        mock_response = MagicMock()
        mock_response.content = 'This is not JSON at all!'
        
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_create_llm.return_value = mock_llm
        
        state = ProcessingState(input_description="Test bug description")
        result_state = analyze_bug_description(state)
        
        # Should set error message
        assert result_state.error_message is not None
        assert "Invalid JSON response from LLM" in result_state.error_message
        assert result_state.processed_result is None
    
    def test_validate_empty_description_title_generation(self):
        """Test line 178: Title generation from description with no sentences"""
        # Test with description that has no proper sentences
        result = validate_and_clean_result({
            'title': '',  # Empty title to trigger generation
            'severity': 'low',
            'type': 'bug',
            'tags': []
        }, 'word1 word2 word3')  # No punctuation
        
        # Should use the whole description as title
        assert result['title'] == 'word1 word2 word3'
        
        # Test with completely empty description
        result2 = validate_and_clean_result({
            'title': '',
            'severity': 'medium',
            'type': 'bug', 
            'tags': []
        }, '')
        
        # Should use default title
        assert result2['title'] == 'Untitled Issue'
    
    def test_handle_retry_logic_max_retries_exceeded(self):
        """Test line 221: Max retries exceeded error"""
        state = ProcessingState(
            input_description="test",
            retry_count=3,  # At max retries
            max_retries=3,
            error_message="Previous error"
        )
        
        # Should raise ModelError when max retries exceeded
        with pytest.raises(ModelError, match="LLM processing failed after 3 retries"):
            handle_retry_logic(state)
    
    @patch('core.model.create_processing_graph')
    @patch('core.model.load_config')
    def test_process_description_missing_result_error(self, mock_load_config, mock_create_graph):
        """Test lines 298-299: Error when processed_result is None"""
        mock_load_config.return_value = {
            'openai_api_key': 'sk-test-key',
            'retry_limit': 3
        }
        
        # Mock graph.invoke to return state without processed_result
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {
            'processed_result': None,
            'error_message': 'Custom error message'
        }
        mock_create_graph.return_value = mock_graph
        
        with pytest.raises(ModelError, match="Processing failed: Custom error message"):
            process_description("Test description")
    
    @patch('core.model.create_processing_graph')
    @patch('core.model.load_config')
    def test_process_description_general_exception_wrapping(self, mock_load_config, mock_create_graph):
        """Test lines 303-308: General exception wrapping in ModelError"""
        mock_load_config.return_value = {
            'openai_api_key': 'sk-test-key',
            'retry_limit': 3
        }
        
        # Mock graph creation to raise a general exception
        mock_create_graph.side_effect = RuntimeError("Unexpected runtime error")
        
        with pytest.raises(ModelError, match="LLM processing failed: Unexpected runtime error"):
            process_description("Test description")
    
    @patch('core.model.create_llm_chain')
    @patch('core.model.load_config')
    def test_setup_langgraph_connection_test_error(self, mock_load_config, mock_create_llm):
        """Test lines 329-331: Error during connection testing in setup_langgraph"""
        mock_load_config.return_value = {
            'openai_api_key': 'sk-test-key'
        }
        
        # Mock create_llm_chain to succeed but llm.invoke to fail
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("Connection test failed")
        mock_create_llm.return_value = mock_llm
        
        result = setup_langgraph()
        
        # Should return False and not raise exception
        assert result is False


class TestModelValidationEdgeCases:
    """Test additional validation edge cases for complete coverage"""
    
    def test_validate_non_list_tags(self):
        """Test tags validation when tags is not a list"""
        result = validate_and_clean_result({
            'title': 'Test',
            'severity': 'low',
            'type': 'bug',
            'tags': 'not-a-list'  # String instead of list
        }, 'Test description')
        
        # Should convert to empty list
        assert result['tags'] == []
        
        # Test with None tags
        result2 = validate_and_clean_result({
            'title': 'Test',
            'severity': 'high',
            'type': 'feature',
            'tags': None
        }, 'Test description')
        
        assert result2['tags'] == []
    
    def test_validate_tag_cleaning_edge_cases(self):
        """Test tag cleaning with various edge cases"""
        result = validate_and_clean_result({
            'title': 'Test',
            'severity': 'medium',
            'type': 'bug',
            'tags': [
                123,  # Non-string
                '',   # Empty string
                '   ',  # Whitespace only
                'Valid Tag',  # Spaces (should become valid-tag)
                'duplicate',
                'DUPLICATE',  # Case variations (should dedupe)
                'a' * 25,  # Too long (should be excluded)
                'good-tag',
                'another-good-tag',
                'third-good-tag',
                'fourth-good-tag',
                'fifth-good-tag',
                'sixth-good-tag',
                'seventh-good-tag',
                'eighth-good-tag',
                'ninth-good-tag',
                'tenth-good-tag',
                'eleventh-tag',  # 11th tag, should be excluded due to 10 tag limit
            ]
        }, 'Test description')
        
        # Should clean and limit tags properly
        assert len(result['tags']) <= 10
        assert 'valid-tag' in result['tags']
        assert 'duplicate' in result['tags']
        assert 'DUPLICATE' not in result['tags']  # Should be deduped
        assert all(len(tag) <= 20 for tag in result['tags'])  # No long tags
        assert all(isinstance(tag, str) for tag in result['tags'])  # All strings
        assert all(tag.strip() for tag in result['tags'])  # No empty/whitespace
    
    def test_process_description_model_error_passthrough(self):
        """Test that ModelError exceptions are passed through unchanged"""
        # Test that ModelError from create_llm_chain is passed through
        with patch('core.model.load_config') as mock_config:
            mock_config.return_value = {'openai_api_key': 'sk-test'}
            
            with patch('core.model.create_processing_graph') as mock_graph:
                mock_graph.side_effect = ModelError("Original ModelError")
                
                # Should re-raise the same ModelError, not wrap it
                with pytest.raises(ModelError, match="Original ModelError"):
                    process_description("Test description")
    
    def test_handle_retry_logic_line_221_exact_coverage(self):
        """Test line 221: Exact coverage of the ModelError raise in handle_retry_logic"""
        # Create state at exactly max retries to hit line 221
        state = ProcessingState(
            input_description="test description",
            retry_count=3,  # Exactly at max retries
            max_retries=3,
            error_message="Final error that will be in exception"
        )
        
        # This should hit line 221 exactly: raise ModelError(
        with pytest.raises(ModelError) as exc_info:
            handle_retry_logic(state)
        
        # Verify the exception message contains the expected content from line 221-224
        assert "LLM processing failed after 3 retries" in str(exc_info.value)
        assert "Last error: Final error that will be in exception" in str(exc_info.value) 