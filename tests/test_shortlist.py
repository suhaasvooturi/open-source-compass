"""Tests for ShortlistManager add, remove, deduplication, and JSON/CSV exports."""

import json

from finder.shortlist import ShortlistManager


def test_shortlist_crud():
    """Verify adding, checking, removing, and clearing shortlisted issues."""
    manager = ShortlistManager()
    assert len(manager.list_all()) == 0

    item1 = {
        "number": 101,
        "title": "Fix authentication bug",
        "html_url": "https://github.com/foo/bar/issues/101",
        "repository": "foo/bar",
        "difficulty": "Beginner",
        "match_score_percent": 88,
        "estimated_effort": "1 - 3 hours",
        "technologies": ["Python", "FastAPI"],
        "missing_skills": [],
    }

    # Add item
    assert manager.add(item1) is True
    assert manager.is_saved(101) is True
    assert len(manager.list_all()) == 1

    # Duplicate add returns False
    assert manager.add(item1) is False
    assert len(manager.list_all()) == 1

    # Remove item
    assert manager.remove(101) is True
    assert manager.is_saved(101) is False
    assert len(manager.list_all()) == 0

    # Clear
    manager.add(item1)
    manager.clear()
    assert len(manager.list_all()) == 0


def test_shortlist_json_export():
    """Verify exporting shortlist to valid JSON string."""
    manager = ShortlistManager()
    manager.add({"number": 202, "title": "Add docs", "repository": "owner/repo"})

    json_str = manager.to_json()
    parsed = json.loads(json_str)
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["number"] == 202


def test_shortlist_csv_export():
    """Verify exporting shortlist to CSV."""
    manager = ShortlistManager()
    manager.add({
        "number": 303,
        "title": "Add tests",
        "repository": "owner/repo",
        "difficulty": "Intermediate",
        "match_score_percent": 75,
        "estimated_effort": "3 - 8 hours",
        "technologies": ["Python", "pytest"],
        "missing_skills": ["pytest"],
        "html_url": "https://github.com/owner/repo/issues/303",
    })

    csv_str = manager.to_csv()
    lines = csv_str.strip().splitlines()
    assert len(lines) == 2  # Header + 1 data line
    assert "number,title,repository" in lines[0]
    assert "303" in lines[1]
    assert "Python, pytest" in lines[1]
