"""Tests for GitHub REST API integration, URL parsing, caching, and error handling."""

from unittest.mock import MagicMock, patch
import pytest
import requests

from finder.github_api import (
    GitHubAPIError,
    GitHubClient,
    InvalidRepositoryURLError,
    NetworkConnectionError,
    RateLimitExceededError,
    RepositoryNotFoundError,
    UserProfileURLError,
    parse_github_url,
)


def test_parse_github_url_valid():
    """Test URL parsing across various valid GitHub URL formats."""
    assert parse_github_url("https://github.com/facebook/react") == ("facebook", "react")
    assert parse_github_url("http://github.com/facebook/react") == ("facebook", "react")
    assert parse_github_url("github.com/facebook/react") == ("facebook", "react")
    assert parse_github_url("facebook/react") == ("facebook", "react")
    assert parse_github_url("https://github.com/facebook/react.git") == ("facebook", "react")
    assert parse_github_url("https://github.com/psf/requests/issues") == ("psf", "requests")
    assert parse_github_url("psf/requests.git") == ("psf", "requests")


def test_parse_github_url_invalid():
    """Test URL parsing rejection for invalid inputs."""
    with pytest.raises(InvalidRepositoryURLError):
        parse_github_url("")

    with pytest.raises(InvalidRepositoryURLError):
        parse_github_url("https://gitlab.com/foo/bar")

    with pytest.raises(UserProfileURLError) as excinfo:
        parse_github_url("https://github.com/onlyowner")
    assert excinfo.value.username == "onlyowner"

    with pytest.raises(UserProfileURLError) as excinfo:
        parse_github_url("just-a-username")
    assert excinfo.value.username == "just-a-username"


@patch("finder.github_api.requests.get")
def test_get_repository_success(mock_get):
    """Test successful repository metadata retrieval."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.ok = True
    mock_resp.headers = {"X-RateLimit-Remaining": "59"}
    mock_resp.json.return_value = {
        "name": "fastapi",
        "full_name": "tiangolo/fastapi",
        "description": "FastAPI framework, high performance",
        "language": "Python",
        "topics": ["python", "fastapi"],
        "default_branch": "master",
        "stargazers_count": 75000,
        "forks_count": 6000,
        "open_issues_count": 120,
        "license": {"spdx_id": "MIT"},
        "html_url": "https://github.com/tiangolo/fastapi",
    }
    mock_get.return_value = mock_resp

    client = GitHubClient()
    repo = client.get_repository("tiangolo", "fastapi")
    assert repo["name"] == "fastapi"
    assert repo["language"] == "Python"
    assert repo["stargazers_count"] == 75000
    assert repo["license"] == "MIT"
    assert client.rate_limit_remaining == 59


@patch("finder.github_api.requests.get")
def test_get_open_issues_excludes_pull_requests(mock_get):
    """Ensure that pull requests returned by the issues endpoint are filtered out."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.ok = True
    mock_resp.headers = {}
    mock_resp.json.return_value = [
        {
            "number": 1,
            "title": "Bug in query parser",
            "body": "Detailed explanation of bug.",
            "labels": [{"name": "bug", "color": "f00"}],
            "user": {"login": "alice"},
            "comments": 2,
            # Normal issue, NO 'pull_request' key
        },
        {
            "number": 2,
            "title": "Fix: update query parser regex",
            "body": "Closes #1",
            "labels": [{"name": "enhancement", "color": "0f0"}],
            "user": {"login": "bob"},
            "pull_request": {"url": "https://api.github.com/repos/foo/bar/pulls/2"},  # Pull request!
        },
        {
            "number": 3,
            "title": "Documentation update",
            "body": "Add example curl commands",
            "labels": [{"name": "documentation", "color": "00f"}],
            "user": {"login": "charlie"},
            "comments": 0,
        },
    ]
    mock_get.return_value = mock_resp

    client = GitHubClient()
    issues = client.get_open_issues("foo", "bar")
    assert len(issues) == 2
    issue_numbers = [i["number"] for i in issues]
    assert 1 in issue_numbers
    assert 3 in issue_numbers
    assert 2 not in issue_numbers  # Excluded!


@patch("finder.github_api.requests.get")
def test_repository_not_found_error(mock_get):
    """Test 404 response translates to RepositoryNotFoundError."""
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.ok = False
    mock_get.return_value = mock_resp

    client = GitHubClient()
    with pytest.raises(RepositoryNotFoundError):
        client.get_repository("nonexistent", "repo")


@patch("finder.github_api.requests.get")
def test_rate_limit_exceeded_error(mock_get):
    """Test 403 rate limit response translates to RateLimitExceededError."""
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.ok = False
    mock_resp.headers = {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1700000000"}
    mock_resp.json.return_value = {"message": "API rate limit exceeded for IP"}
    mock_get.return_value = mock_resp

    client = GitHubClient()
    with pytest.raises(RateLimitExceededError):
        client.get_repository("owner", "repo")


@patch("finder.github_api.requests.get")
def test_network_connection_error(mock_get):
    """Test requests.exceptions translates to NetworkConnectionError."""
    mock_get.side_effect = requests.exceptions.ConnectTimeout("Connection timed out")

    client = GitHubClient()
    with pytest.raises(NetworkConnectionError):
        client.get_repository("owner", "repo")


@patch("finder.github_api.requests.get")
def test_cache_functionality(mock_get):
    """Verify that caching prevents repeated requests for the same endpoint."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.ok = True
    mock_resp.headers = {}
    mock_resp.json.return_value = {"name": "cached_repo"}
    mock_get.return_value = mock_resp

    client = GitHubClient()
    r1 = client.get_repository("owner", "repo")
    r2 = client.get_repository("owner", "repo")

    assert r1 == r2
    assert mock_get.call_count == 1  # Only 1 network call made!
    client.clear_cache()
    client.get_repository("owner", "repo")
    assert mock_get.call_count == 2
