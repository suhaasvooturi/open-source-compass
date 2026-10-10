"""GitHub REST API integration client with validation, caching, and robust error handling."""

from __future__ import annotations

import base64
import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests


class GitHubAPIError(Exception):
    """Base exception for GitHub API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class RepositoryNotFoundError(GitHubAPIError):
    """Raised when repository does not exist or is private."""
    pass


class RateLimitExceededError(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded."""

    def __init__(self, message: str, reset_time: Optional[int] = None):
        super().__init__(message, status_code=403)
        self.reset_time = reset_time


class NetworkConnectionError(GitHubAPIError):
    """Raised when network connection fails or times out."""
    pass


class InvalidRepositoryURLError(ValueError):
    """Raised when a provided repository URL or slug is invalid."""
    pass


class UserProfileURLError(InvalidRepositoryURLError):
    """Raised when a user profile URL or single username was entered instead of a repository URL."""

    def __init__(self, username: str):
        self.username = username
        super().__init__(
            f"Input '{username}' appears to be a user profile rather than a repository. "
            f"Please provide an 'owner/repository' format."
        )


def parse_github_url(url_or_slug: str) -> Tuple[str, str]:
    """Parse a GitHub repository URL or slug into (owner, repo).

    Supports:
        - https://github.com/owner/repo
        - http://github.com/owner/repo
        - github.com/owner/repo
        - owner/repo
        - https://github.com/owner/repo.git
        - https://github.com/owner/repo/issues
    """
    if not url_or_slug or not isinstance(url_or_slug, str):
        raise InvalidRepositoryURLError("Repository input cannot be empty.")

    cleaned = url_or_slug.strip()

    # If it's a slug like owner/repo
    if re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", cleaned):
        owner, repo = cleaned.split("/", 1)
        if repo.endswith(".git"):
            repo = repo[:-4]
        return owner, repo

    # If user entered just a username slug without slash
    if re.match(r"^[A-Za-z0-9_.-]+$", cleaned):
        raise UserProfileURLError(cleaned)

    # Add scheme if missing but starts with github.com
    if cleaned.startswith("github.com/"):
        cleaned = "https://" + cleaned

    parsed = urlparse(cleaned)
    if not parsed.netloc:
        raise InvalidRepositoryURLError(f"Invalid URL or repository format: '{url_or_slug}'")

    if parsed.netloc.lower() not in ("github.com", "www.github.com"):
        raise InvalidRepositoryURLError(
            f"Unsupported host '{parsed.netloc}'. Only public GitHub repositories are supported."
        )

    parts = [p for p in parsed.path.strip("/").split("/") if p]
    if len(parts) == 1:
        raise UserProfileURLError(parts[0])
    if len(parts) < 2:
        raise InvalidRepositoryURLError(
            f"URL must contain both owner and repository name: '{url_or_slug}'"
        )

    owner = parts[0]
    repo = parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]

    # Sanitize owner and repo
    if not re.match(r"^[A-Za-z0-9_.-]+$", owner) or not re.match(r"^[A-Za-z0-9_.-]+$", repo):
        raise InvalidRepositoryURLError(f"Invalid characters in repository path: '{owner}/{repo}'")

    return owner, repo


class GitHubClient:
    """Client for querying the GitHub REST API (v3) with caching and rate limit monitoring."""

    def __init__(
        self,
        token: Optional[str] = None,
        timeout: int = 15,
        cache_ttl_seconds: int = 1800,
    ):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.timeout = timeout
        self.cache_ttl = cache_ttl_seconds
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self.rate_limit_remaining: Optional[int] = None
        self.rate_limit_reset: Optional[int] = None

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OpenSourceCompass-ContributionFinder/1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token.strip()}"
        return headers

    def _get_from_cache(self, key: str) -> Optional[Any]:
        if key in self._cache:
            ts, val = self._cache[key]
            if time.time() - ts < self.cache_ttl:
                return val
            del self._cache[key]
        return None

    def _set_cache(self, key: str, val: Any) -> None:
        self._cache[key] = (time.time(), val)

    def clear_cache(self) -> None:
        """Clear all in-memory cached responses."""
        self._cache.clear()

    def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"https://api.github.com{endpoint}"
        cache_key = f"{url}?{sorted((params or {}).items())}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        headers = self._get_headers()
        try:
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
        except requests.exceptions.Timeout as err:
            raise NetworkConnectionError(
                f"GitHub API request timed out after {self.timeout}s: {endpoint}"
            ) from err
        except requests.exceptions.RequestException as err:
            raise NetworkConnectionError(
                f"Failed to connect to GitHub API: {str(err)}"
            ) from err

        # Update rate limit trackers
        if "X-RateLimit-Remaining" in response.headers:
            try:
                self.rate_limit_remaining = int(response.headers["X-RateLimit-Remaining"])
            except ValueError:
                pass
        if "X-RateLimit-Reset" in response.headers:
            try:
                self.rate_limit_reset = int(response.headers["X-RateLimit-Reset"])
            except ValueError:
                pass

        if response.status_code == 404:
            raise RepositoryNotFoundError(
                f"Resource not found (404) at '{endpoint}'. Please verify the repository exists and is public."
            )
        elif response.status_code == 403:
            msg = response.json().get("message", "Forbidden") if response.content else "Forbidden"
            if "rate limit exceeded" in msg.lower() or self.rate_limit_remaining == 0:
                reset_min = ""
                if self.rate_limit_reset:
                    diff = max(0, int(self.rate_limit_reset - time.time()))
                    reset_min = f" Limit resets in approximately {diff // 60} minutes."
                raise RateLimitExceededError(
                    f"GitHub API rate limit exceeded.{reset_min} Add a personal access token (GITHUB_TOKEN) to increase your hourly quota.",
                    reset_time=self.rate_limit_reset,
                )
            raise GitHubAPIError(f"GitHub API forbidden (403): {msg}", status_code=403)
        elif not response.ok:
            raise GitHubAPIError(
                f"GitHub API returned error HTTP {response.status_code}: {response.text}",
                status_code=response.status_code,
            )

        data = response.json()
        self._set_cache(cache_key, data)
        return data

    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch repository metadata."""
        data = self._request(f"/repos/{owner}/{repo}")
        return {
            "name": data.get("name", repo),
            "owner": owner,
            "full_name": data.get("full_name", f"{owner}/{repo}"),
            "description": data.get("description") or "No description provided.",
            "language": data.get("language") or "Unspecified",
            "topics": data.get("topics", []),
            "default_branch": data.get("default_branch", "main"),
            "stargazers_count": data.get("stargazers_count", 0),
            "forks_count": data.get("forks_count", 0),
            "open_issues_count": data.get("open_issues_count", 0),
            "license": (data.get("license") or {}).get("spdx_id") or "Not specified",
            "html_url": data.get("html_url", f"https://github.com/{owner}/{repo}"),
            "archived": data.get("archived", False),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
        }

    def get_open_issues(
        self, owner: str, repo: str, max_count: int = 50
    ) -> List[Dict[str, Any]]:
        """Fetch open issues from the repository, explicitly filtering out pull requests."""
        issues: List[Dict[str, Any]] = []
        page = 1
        per_page = min(max_count, 100)

        while len(issues) < max_count:
            data = self._request(
                f"/repos/{owner}/{repo}/issues",
                params={"state": "open", "per_page": per_page, "page": page, "sort": "updated"},
            )
            if not data or not isinstance(data, list):
                break

            for item in data:
                # GitHub issues API returns pull requests as well; filter them out!
                if "pull_request" in item:
                    continue

                labels_raw = item.get("labels", [])
                labels = [
                    {
                        "name": lbl.get("name", "") if isinstance(lbl, dict) else str(lbl),
                        "color": lbl.get("color", "cccccc") if isinstance(lbl, dict) else "cccccc",
                        "description": lbl.get("description", "") if isinstance(lbl, dict) else "",
                    }
                    for lbl in labels_raw
                ]

                issues.append(
                    {
                        "number": item.get("number"),
                        "title": item.get("title", ""),
                        "body": item.get("body") or "",
                        "labels": labels,
                        "label_names": [lbl["name"] for lbl in labels],
                        "html_url": item.get("html_url", f"https://github.com/{owner}/{repo}/issues/{item.get('number')}"),
                        "comments": item.get("comments", 0),
                        "created_at": item.get("created_at"),
                        "updated_at": item.get("updated_at"),
                        "author": (item.get("user") or {}).get("login", "unknown"),
                        "state": item.get("state", "open"),
                    }
                )

                if len(issues) >= max_count:
                    break

            if len(data) < per_page:
                break
            page += 1

        return issues

    def get_readme(self, owner: str, repo: str) -> Optional[str]:
        """Fetch and decode the repository README content."""
        try:
            data = self._request(f"/repos/{owner}/{repo}/readme")
            if "content" in data and data.get("encoding") == "base64":
                raw_bytes = base64.b64decode(data["content"])
                return raw_bytes.decode("utf-8", errors="replace")
            return None
        except RepositoryNotFoundError:
            return None
        except Exception:
            return None

    def get_contributing_guide(self, owner: str, repo: str) -> Optional[str]:
        """Attempt to locate CONTRIBUTING guide across common repository locations."""
        candidates = [
            "CONTRIBUTING.md",
            ".github/CONTRIBUTING.md",
            "docs/CONTRIBUTING.md",
            "contributing.md",
            "CONTRIBUTING.rst",
        ]
        for path in candidates:
            try:
                data = self._request(f"/repos/{owner}/{repo}/contents/{path}")
                if "content" in data and data.get("encoding") == "base64":
                    raw_bytes = base64.b64decode(data["content"])
                    return raw_bytes.decode("utf-8", errors="replace")
            except Exception:
                continue
        return None

    def get_root_files(self, owner: str, repo: str) -> List[str]:
        """Fetch list of root file and directory names."""
        try:
            data = self._request(f"/repos/{owner}/{repo}/contents")
            if isinstance(data, list):
                return [item.get("name", "") for item in data if "name" in item]
            return []
        except Exception:
            return []

    def get_user_repositories(self, username: str, max_count: int = 15) -> List[Dict[str, Any]]:
        """Fetch public repositories for a given user or organization."""
        try:
            data = self._request(
                f"/users/{username}/repos",
                params={"sort": "updated", "per_page": min(max_count, 30), "type": "owner"},
            )
            if isinstance(data, list):
                return [
                    {
                        "name": r.get("name", ""),
                        "full_name": r.get("full_name", f"{username}/{r.get('name')}"),
                        "description": r.get("description") or "No description provided",
                        "language": r.get("language") or "Unspecified",
                        "stargazers_count": r.get("stargazers_count", 0),
                        "open_issues_count": r.get("open_issues_count", 0),
                        "html_url": r.get("html_url", ""),
                        "fork": r.get("fork", False),
                    }
                    for r in data
                    if not r.get("fork") and r.get("name")
                ]
            return []
        except Exception:
            return []

