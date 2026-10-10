"""Tests for repository architecture analysis, technology detection, and health indicators."""

from finder.repository_analyzer import (
    RepositoryAnalyzer,
    detect_technologies_from_text,
    normalize_skill,
    normalize_skills_list,
)


def test_skill_normalization():
    """Verify alias normalization and preservation of distinct technologies."""
    assert normalize_skill("py") == "Python"
    assert normalize_skill("python3") == "Python"
    assert normalize_skill("js") == "JavaScript"
    assert normalize_skill("ts") == "TypeScript"
    assert normalize_skill("reactjs") == "React"
    assert normalize_skill("tf") == "TensorFlow"

    # Must NOT merge unrelated technologies
    assert normalize_skill("java") == "Java"
    assert normalize_skill("javascript") == "JavaScript"
    assert normalize_skill("c++") == "C++"

    # List deduplication
    skills = ["py", "python", "javascript", "js", "Testing", "tests"]
    normalized = normalize_skills_list(skills)
    assert "Python" in normalized
    assert "JavaScript" in normalized
    assert "Testing" in normalized
    assert len(normalized) == 3


def test_detect_technologies_from_text():
    """Verify extraction of technologies mentioned in issue or readme text."""
    text = "We need to write pytest test cases for the FastAPI REST API and connect to PostgreSQL."
    detected = detect_technologies_from_text(text)
    assert "pytest" in detected
    assert "FastAPI" in detected
    assert "REST APIs" in detected
    assert "PostgreSQL" in detected
    assert "Testing" in detected


def test_repository_analyzer_full():
    """Verify repository analysis with full artifacts present."""
    metadata = {
        "name": "fastapi-taskflow",
        "language": "Python",
        "topics": ["docker", "fastapi"],
        "license": "MIT",
        "stargazers_count": 100,
        "forks_count": 20,
        "open_issues_count": 5,
        "archived": False,
    }
    root_files = ["pyproject.toml", "Dockerfile", "README.md", "CONTRIBUTING.md", "tests"]
    readme = "# FastAPI TaskFlow\nAsynchronous tasks with Python and pytest."
    contributing = "# Contributing\nRun pytest before opening a PR."

    analyzer = RepositoryAnalyzer(metadata, root_files, readme, contributing)
    result = analyzer.analyze()

    assert result["primary_language"] == "Python"
    assert "Python" in result["detected_technologies"]
    assert "FastAPI" in result["detected_technologies"]
    assert "Docker" in result["detected_technologies"]
    assert "Testing" in result["detected_technologies"]

    health = result["health"]
    assert health["has_readme"] is True
    assert health["has_contributing"] is True
    assert health["has_license"] is True
    assert health["has_tests_indicator"] is True
    assert health["health_score"] >= 80
    assert len(result["missing_artifacts"]) == 0


def test_repository_analyzer_missing_artifacts():
    """Verify analyzer transparently notes missing files and lowers health score."""
    metadata = {
        "name": "bare-repo",
        "language": "Python",
        "topics": [],
        "license": "Not specified",
        "stargazers_count": 2,
        "forks_count": 0,
        "open_issues_count": 1,
        "archived": False,
    }
    root_files = ["main.py"]  # No README, no CONTRIBUTING, no build config

    analyzer = RepositoryAnalyzer(metadata, root_files, readme=None, contributing=None)
    result = analyzer.analyze()

    health = result["health"]
    assert health["has_readme"] is False
    assert health["has_contributing"] is False
    assert health["has_license"] is False
    assert health["health_score"] < 50
    assert len(result["missing_artifacts"]) >= 3
