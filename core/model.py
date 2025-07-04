"""
LangGraph integration for processing bug descriptions into structured data.
This module interfaces with LLM APIs to transform freeform text into JSON.
"""

import json
import re
from datetime import datetime
from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from core.config import load_config


class ModelError(Exception):
    """Raised when model processing fails"""

    pass


class BugAnalysis(BaseModel):
    """Structured output model for bug analysis"""

    title: str = Field(description="Concise title summarizing the bug (max 120 chars)")
    description: str = Field(description="Original bug description")
    severity: str = Field(description="Bug severity: low, medium, high, or critical")
    type: str = Field(description="Bug type: bug, feature, chore, or unknown")
    tags: list[str] = Field(description="Relevant tags for categorization")


class ProcessingState(BaseModel):
    """State for the LangGraph processing pipeline"""

    input_description: str
    processed_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


def create_llm_chain():
    """Create and configure the LLM chain"""
    config = load_config()

    # Check if API key is configured
    api_key = config.get("openai_api_key")
    if not api_key:
        raise ModelError(
            "OpenAI API key not configured. Please run: "
            "bugit config --set-api-key openai YOUR_API_KEY"
        )

    # Initialize OpenAI model
    model_name = config.get("model", "gpt-4")

    try:
        llm = ChatOpenAI(
            model=model_name,
            temperature=0.1,  # Low temperature for consistent structured output
            api_key=api_key,
            timeout=30.0,
            max_retries=2,
        )
        return llm
    except Exception as e:
        raise ModelError(f"Failed to initialize OpenAI model: {e}")


def analyze_bug_description(state: ProcessingState) -> ProcessingState:
    """LangGraph node: Analyze bug description using LLM"""

    try:
        llm = create_llm_chain()

        # Construct the prompt for structured bug analysis
        system_prompt = """You are a expert software engineer analyzing bug reports.
        
Your task is to analyze a freeform bug description and extract structured information.

Return a JSON object with these exact fields:
{
  "title": "Concise summary (max 120 characters)",
  "description": "The original description as provided",
  "severity": "low|medium|high|critical",
  "type": "bug|feature|chore|unknown", 
  "tags": ["relevant", "tags", "for", "categorization"]
}

Severity guidelines:
- critical: System crashes, data loss, security issues, complete feature failure
- high: Major functionality broken, significant user impact
- medium: Moderate issues, workarounds available
- low: Minor issues, cosmetic problems, enhancement requests

Type guidelines:
- bug: Something is broken or not working as expected
- feature: Request for new functionality
- chore: Maintenance, refactoring, documentation
- unknown: Unclear or ambiguous reports

Tag suggestions (use relevant ones): auth, ui, api, database, performance, security, mobile, web, camera, recording, login, logout, network, storage, validation, error-handling

Be concise but descriptive. Focus on the core issue."""

        user_prompt = f"Analyze this bug report:\n\n{state.input_description}"

        # Create messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        # Get LLM response
        response = llm.invoke(messages)
        response_text = str(response.content).strip()

        # Parse JSON response
        try:
            # Extract JSON from response (in case there's extra text)
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
            else:
                json_str = response_text

            result = json.loads(json_str)

            # Validate and clean the result
            processed_result = validate_and_clean_result(
                result, state.input_description
            )

            state.processed_result = processed_result
            state.error_message = None  # Clear any previous errors
            return state

        except json.JSONDecodeError as e:
            raise ModelError(f"Invalid JSON response from LLM: {e}")

    except Exception as e:
        state.error_message = str(e)
        return state


def validate_and_clean_result(
    result: Dict[str, Any], original_description: str
) -> Dict[str, Any]:
    """Validate and clean LLM output to ensure it meets our schema requirements"""

    # Ensure all required fields are present with defaults
    cleaned = {
        "title": result.get("title", "Untitled Issue"),
        "description": original_description,  # Always use original description
        "severity": result.get("severity", "medium").lower(),
        "type": result.get("type", "bug").lower(),
        "tags": result.get("tags", []),
    }

    # Validate and fix severity
    valid_severities = ["low", "medium", "high", "critical"]
    if cleaned["severity"] not in valid_severities:
        cleaned["severity"] = "medium"

    # Validate and fix type
    valid_types = ["bug", "feature", "chore", "unknown"]
    if cleaned["type"] not in valid_types:
        cleaned["type"] = "bug"

    # Validate and clean title
    title = cleaned["title"].strip()
    if not title or len(title) == 0:
        # Generate title from first sentence of description
        sentences = re.split(r"[.!?]+", original_description.strip())
        title = (
            sentences[0].strip()
            if sentences and sentences[0].strip()
            else "Untitled Issue"
        )

    if len(title) > 120:
        title = title[:117] + "..."
    cleaned["title"] = title

    # Validate and clean tags
    if not isinstance(cleaned["tags"], list):
        cleaned["tags"] = []

    # Clean and deduplicate tags
    clean_tags = []
    for tag in cleaned["tags"]:
        if isinstance(tag, str) and tag.strip():
            clean_tag = tag.strip().lower().replace(" ", "-")
            if clean_tag not in clean_tags and len(clean_tag) <= 20:
                clean_tags.append(clean_tag)

    # Limit to 10 tags maximum
    cleaned["tags"] = clean_tags[:10]

    return cleaned


def handle_retry_logic(state: ProcessingState) -> ProcessingState:
    """LangGraph node: Handle retry logic for failed processing"""

    if state.retry_count < state.max_retries:
        # Increment retry count and try again
        state.retry_count += 1
        state.error_message = None  # Clear error for retry
        return state
    else:
        # Max retries exceeded - fail with error
        original_error = state.error_message or "Unknown processing error"
        raise ModelError(
            f"LLM processing failed after {state.max_retries} retries. "
            f"Last error: {original_error}"
        )


def should_retry(state: ProcessingState) -> str:
    """Determine the next step in processing"""
    if state.processed_result is not None:
        return "success"
    elif state.error_message is not None:
        if state.retry_count < state.max_retries:
            return "retry"
        else:
            return "max_retries_exceeded"
    else:
        return "continue"


def create_processing_graph():
    """Create the LangGraph processing pipeline with retry logic"""

    workflow = StateGraph(ProcessingState)

    # Add nodes
    workflow.add_node("analyze", analyze_bug_description)
    workflow.add_node("handle_retry", handle_retry_logic)

    # Set entry point
    workflow.set_entry_point("analyze")

    # Add conditional edges
    workflow.add_conditional_edges(
        "analyze",
        should_retry,
        {
            "success": END,
            "retry": "handle_retry",
            "max_retries_exceeded": "handle_retry",
            "continue": "analyze",
        },
    )

    # Retry handler routes back to analysis
    workflow.add_edge("handle_retry", "analyze")

    return workflow.compile()


def process_description(description: str) -> Dict[str, Any]:
    """
    Process freeform bug description using LangGraph with retry logic.
    Returns structured data ready for validation.

    Args:
        description: Freeform bug description from user

    Returns:
        Dictionary with title, description, severity, type, and tags

    Raises:
        ModelError: If processing fails after all retries are exhausted
    """
    if not description or not description.strip():
        raise ModelError("Description cannot be empty")

    # Check if API key is configured
    config = load_config()
    api_key = config.get("openai_api_key")

    if not api_key:
        raise ModelError(
            "OpenAI API key not configured. Please run: "
            "bugit config --set-api-key openai YOUR_API_KEY"
        )

    try:
        # Create and run the LangGraph pipeline
        graph = create_processing_graph()

        # Get retry limit from config
        max_retries = config.get("retry_limit", 3)

        # Initialize state
        initial_state = ProcessingState(
            input_description=description.strip(), max_retries=max_retries
        )

        # Run the graph
        final_state = graph.invoke(initial_state)

        if final_state.get("processed_result") is None:
            error_msg = final_state.get("error_message", "Unknown error")
            raise ModelError(f"Processing failed: {error_msg}")

        return final_state["processed_result"]

    except ModelError:
        # Re-raise ModelErrors as-is
        raise
    except Exception as e:
        # Wrap other exceptions in ModelError
        raise ModelError(f"LLM processing failed: {e}")


def setup_langgraph():
    """Initialize LangGraph pipeline"""
    try:
        config = load_config()
        api_key = config.get("openai_api_key")

        if not api_key:
            print("[WARNING] OpenAI API key not configured.")
            print("To configure: bugit config --set-api-key openai YOUR_API_KEY")
            return False

        # Test the connection
        llm = create_llm_chain()
        test_response = llm.invoke([HumanMessage(content="Hello")])

        print("[SUCCESS] LangGraph pipeline initialized with OpenAI")
        return True

    except Exception as e:
        print(f"[ERROR] LangGraph initialization failed: {e}")
        return False


def test_model_connection() -> bool:
    """Test connection to LLM API"""
    try:
        config = load_config()
        api_key = config.get("openai_api_key")

        if not api_key:
            return False

        llm = create_llm_chain()
        response = llm.invoke([HumanMessage(content="Test connection")])
        return True

    except Exception:
        return False
