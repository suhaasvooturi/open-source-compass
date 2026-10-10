"""Tests for issue classification, multi-signal evidence, and effort estimation."""

from finder.issue_classifier import IssueClassifier


def test_classify_beginner_issue():
    """Verify classification of beginner-friendly issue with label and text clues."""
    issue = {
        "number": 10,
        "title": "Fix typo in tutorial documentation",
        "body": "The link in tutorial.md has a spelling error: recieve instead of receive.",
        "label_names": ["good first issue", "documentation"],
    }
    classifier = IssueClassifier(issue)
    result = classifier.classify()

    assert result["difficulty"] == "Beginner"
    assert result["beginner_friendly"] is True
    assert "1 - 3 hours" in result["estimated_effort"]
    assert any("good first issue" in ev for ev in result["evidence"])


def test_classify_intermediate_issue():
    """Verify classification of standard intermediate feature/bug work."""
    issue = {
        "number": 20,
        "title": "Add input validation for task priority endpoint",
        "body": "Validate that query parameters are bounded between 1 and 5 and write pytest regression test.",
        "label_names": ["enhancement"],
    }
    classifier = IssueClassifier(issue)
    result = classifier.classify()

    assert result["difficulty"] == "Intermediate"
    assert "3 - 8 hours" in result["estimated_effort"]
    assert "pytest" in result["technologies_involved"] or "Testing" in result["technologies_involved"]


def test_classify_advanced_issue():
    """Verify classification of architectural, concurrency, or performance issue."""
    issue = {
        "number": 30,
        "title": "Worker heartbeat race condition and deadlock in distributed state machine",
        "body": "Under high network latency, distributed workers encounter a memory leak and race condition in consensus.",
        "label_names": ["complex", "architecture"],
    }
    classifier = IssueClassifier(issue)
    result = classifier.classify()

    assert result["difficulty"] == "Advanced"
    assert "8 - 20+ hours" in result["estimated_effort"]
    assert any("complex" in ev or "architecture" in ev for ev in result["evidence"])


def test_classify_insufficient_evidence():
    """Verify that insufficient detail yields 'Difficulty uncertain' rather than false confidence."""
    issue = {
        "number": 40,
        "title": "broken",
        "body": "",
        "label_names": [],
    }
    classifier = IssueClassifier(issue)
    result = classifier.classify()

    assert result["difficulty"] == "Difficulty uncertain"
    assert result["confidence"] <= 0.3
    assert "insufficient detail" in result["evidence"][0].lower()
