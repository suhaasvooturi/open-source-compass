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


def test_get_snapshot_for_repo():
    """Verify get_snapshot_for_repo retrieves cached snapshots and returns None for unknown repos."""
    from finder.demo_data import get_snapshot_for_repo

    snap = get_snapshot_for_repo("psf", "requests")
    assert snap is not None
    assert snap["metadata"]["name"] == "requests"

    snap_fastapi = get_snapshot_for_repo("tiangolo", "fastapi")
    assert snap_fastapi is not None
    assert snap_fastapi["metadata"]["name"] == "fastapi"

    snap_compass = get_snapshot_for_repo("suhaasvooturi", "open-source-compass")
    assert snap_compass is not None

    assert get_snapshot_for_repo("unknown-org", "nonexistent-repo-xyz") is None

