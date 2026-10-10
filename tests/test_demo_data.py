"""Tests for synthetic demo mode data integrity and offline independence."""

from finder.demo_data import get_demo_repository, list_demo_repositories


def test_list_demo_repositories():
    """Verify demo repository registry returns available synthetic projects."""
    repos = list_demo_repositories()
    assert len(repos) >= 3
    assert "demo/fastapi-taskflow" in repos
    assert "demo/react-metricshub" in repos
    assert "demo/scikit-mlpipe" in repos


def test_demo_repository_contents():
    """Ensure every demo repository contains full realistic data structures for offline testing."""
    for repo_key in list_demo_repositories():
        data = get_demo_repository(repo_key)
        assert "metadata" in data
        assert "root_files" in data
        assert "readme" in data
        assert "contributing" in data
        assert "issues" in data

        meta = data["metadata"]
        assert "DEMO" in meta["full_name"]
        assert meta["stargazers_count"] > 0
        assert meta["language"] != ""

        issues = data["issues"]
        assert len(issues) >= 3
        for iss in issues:
            assert "number" in iss
            assert "title" in iss
            assert "body" in iss
            assert "labels" in iss
            assert "html_url" in iss
