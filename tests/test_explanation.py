"""Tests for explanation engines, grounding, and unconfigured LLM fallback."""

from unittest.mock import patch

from finder.explanation import LLMExplainer, TemplateExplainer


def test_template_explainer_grounded():
    """Verify that TemplateExplainer generates grounded steps and file references without fabrication."""
    explainer = TemplateExplainer()
    result = explainer.explain(
        issue_title="Add input validation for task priority",
        issue_body="In `src/api/routes.py`, query parameters must be validated. Refer to `tests/test_routes.py`.",
        issue_number=102,
        difficulty="Intermediate",
        technologies=["FastAPI", "pytest"],
        relevant_skills=["FastAPI"],
        missing_skills=["pytest"],
        repo_name="demo/fastapi-taskflow",
        repo_language="Python",
    )

    assert result["is_ai_generated"] is False
    assert result["source"] == "Grounded Template Engine"
    assert len(result["implementation_steps"]) > 0

    # Verify that file paths explicitly mentioned in the body are extracted
    extracted_files = result["likely_files_to_inspect"]
    assert any("src/api/routes.py" in f for f in extracted_files)
    assert any("tests/test_routes.py" in f for f in extracted_files)

    # Verify missing skill recommendation
    assert any("pytest" in tip for tip in result["learning_roadmap"])


def test_llm_explainer_unconfigured_fallback():
    """Verify that LLMExplainer automatically and safely falls back to template when no key is set."""
    explainer = LLMExplainer(provider="", api_key="", model="")
    assert explainer.is_configured is False

    result = explainer.explain(
        issue_title="Fix typo in README",
        issue_body="Typo in introduction.",
        issue_number=5,
        difficulty="Beginner",
        technologies=["Documentation"],
        relevant_skills=["Documentation"],
        missing_skills=[],
        repo_name="demo/fastapi-taskflow",
        repo_language="Python",
    )

    assert result["is_ai_generated"] is False
    assert result["source"] == "Grounded Template Engine"
    assert len(result["implementation_steps"]) > 0


@patch("finder.explanation.requests.post")
def test_llm_explainer_api_error_fallback(mock_post):
    """Verify that when an LLM provider encounters an API error, it falls back to the template cleanly."""
    mock_post.side_effect = RuntimeError("OpenAI rate limit exceeded")

    explainer = LLMExplainer(provider="openai", api_key="sk-test-key", model="gpt-4o-mini")
    assert explainer.is_configured is True

    result = explainer.explain(
        issue_title="Fix typo in README",
        issue_body="Typo in introduction.",
        issue_number=5,
        difficulty="Beginner",
        technologies=["Documentation"],
        relevant_skills=["Documentation"],
        missing_skills=[],
        repo_name="demo/fastapi-taskflow",
        repo_language="Python",
    )

    # Should fall back cleanly without raising an exception to the user
    assert result["is_ai_generated"] is False
    assert "warning" in result
    assert "OpenAI rate limit exceeded" in result["warning"]
