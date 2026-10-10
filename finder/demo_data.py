"""Synthetic demonstration repositories and issues for offline evaluation.

Clearly labeled as synthetic demonstration data.
"""

from __future__ import annotations

from typing import Any, Dict, List

DEMO_REPOSITORIES: Dict[str, Dict[str, Any]] = {
    "demo/fastapi-taskflow": {
        "metadata": {
            "name": "fastapi-taskflow",
            "owner": "demo",
            "full_name": "demo/fastapi-taskflow [DEMO REPO]",
            "description": "High-throughput asynchronous task execution service built with FastAPI and PostgreSQL.",
            "language": "Python",
            "topics": ["python", "fastapi", "postgresql", "asyncio", "rest-api", "docker"],
            "default_branch": "main",
            "stargazers_count": 1420,
            "forks_count": 284,
            "open_issues_count": 18,
            "license": "MIT",
            "html_url": "https://github.com/demo/fastapi-taskflow",
            "archived": False,
        },
        "root_files": [
            "pyproject.toml",
            "requirements.txt",
            "Dockerfile",
            "docker-compose.yml",
            "README.md",
            "CONTRIBUTING.md",
            "tests",
            "src",
            ".github",
        ],
        "readme": """# FastAPI TaskFlow (Synthetic Demo Repository)
An asynchronous background task distribution framework with REST API endpoints and SQL persistence.

## Technologies
- Python 3.11+
- FastAPI & Pydantic v2
- SQLAlchemy & PostgreSQL
- Pytest for automated testing

## Getting Started
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```
""",
        "contributing": """# Contributing to FastAPI TaskFlow

Thank you for contributing! We welcome beginner and experienced contributors alike.

## Setup
```bash
git clone https://github.com/demo/fastapi-taskflow.git
cd fastapi-taskflow
pip install -e ".[dev]"
```

## Running Tests & Linters
```bash
pytest tests/ -v
ruff check .
black --check .
```

## Pull Request Guidelines
- Always link the corresponding issue (`Fixes #<number>`).
- Add unit tests for any bug fix or new endpoint.
- Keep commits concise and descriptive.
""",
        "issues": [
            {
                "number": 101,
                "title": "Fix typo in authentication documentation and update code example",
                "body": "The README section for JWT authentication has a typo in `Authorization: Bearer <token>` and references an outdated endpoint `/api/v1/login` instead of `/api/v1/auth/token`. Should fix documentation and verify sample curls.",
                "labels": [
                    {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
                    {"name": "documentation", "color": "0075ca", "description": "Improvements to docs"},
                ],
                "label_names": ["good first issue", "documentation"],
                "html_url": "https://github.com/demo/fastapi-taskflow/issues/101",
                "comments": 2,
                "created_at": "2026-03-01T10:00:00Z",
                "updated_at": "2026-03-04T12:00:00Z",
                "author": "maintainer_alice",
                "state": "open",
            },
            {
                "number": 102,
                "title": "Add input validation for task priority query parameter",
                "body": "In `src/api/routes.py`, the endpoint `GET /tasks` accepts a `priority` query parameter, but it does not validate that priority is between 1 and 5. When an invalid integer or negative number is passed, it causes an unhandled database query error.\n\n### Requirements\n- Validate using Pydantic `Query(ge=1, le=5)`.\n- Add pytest unit test in `tests/test_routes.py` asserting HTTP 422 Unprocessable Entity on invalid priority.",
                "labels": [
                    {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
                    {"name": "bug", "color": "d73a4a", "description": "Something isn't working"},
                    {"name": "pytest", "color": "fbca04", "description": "Testing tasks"},
                ],
                "label_names": ["good first issue", "bug", "pytest"],
                "html_url": "https://github.com/demo/fastapi-taskflow/issues/102",
                "comments": 4,
                "created_at": "2026-03-02T14:30:00Z",
                "updated_at": "2026-03-05T09:15:00Z",
                "author": "dev_bob",
                "state": "open",
            },
            {
                "number": 103,
                "title": "Implement Redis-backed sliding window rate limiter middleware",
                "body": "We need to protect the public REST API endpoints against abuse by implementing a token-bucket or sliding window rate limiter in `src/middleware/rate_limit.py` using Redis.\n\n### Tasks:\n- [ ] Implement Redis connection pool\n- [ ] Create sliding window counter with Redis sorted sets\n- [ ] Return 429 Too Many Requests with Retry-After header\n- [ ] Write integration test using pytest and fakeredis",
                "labels": [
                    {"name": "enhancement", "color": "a2eeef", "description": "New feature"},
                    {"name": "help wanted", "color": "008672", "description": "Extra attention needed"},
                ],
                "label_names": ["enhancement", "help wanted"],
                "html_url": "https://github.com/demo/fastapi-taskflow/issues/103",
                "comments": 7,
                "created_at": "2026-02-25T11:00:00Z",
                "updated_at": "2026-03-06T15:20:00Z",
                "author": "lead_carol",
                "state": "open",
            },
            {
                "number": 104,
                "title": "Resolve distributed race condition in worker heartbeat consensus",
                "body": "Under high network latency conditions, worker nodes can lose heartbeat lock simultaneously, leading to split-brain task executions and database transaction deadlocks. Requires redesigning the distributed leasing protocol using Postgres row-level locks or etcd distributed consensus.",
                "labels": [
                    {"name": "complex", "color": "b60205", "description": "High complexity"},
                    {"name": "architecture", "color": "5319e7", "description": "Core architecture change"},
                ],
                "label_names": ["complex", "architecture"],
                "html_url": "https://github.com/demo/fastapi-taskflow/issues/104",
                "comments": 15,
                "created_at": "2026-01-15T08:00:00Z",
                "updated_at": "2026-03-03T18:45:00Z",
                "author": "architect_dave",
                "state": "open",
            },
            {
                "number": 105,
                "title": "Add regression tests for SQL pagination cursor decoding",
                "body": "We recently had a bug report where base64 cursor strings with special characters failed to decode in `src/db/pagination.py`. We need a suite of unit tests in `tests/test_pagination.py` covering edge cases including unicode characters, empty strings, and corrupted cursor hashes.",
                "labels": [
                    {"name": "testing", "color": "fbca04", "description": "Test suite work"},
                    {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
                ],
                "label_names": ["testing", "good first issue"],
                "html_url": "https://github.com/demo/fastapi-taskflow/issues/105",
                "comments": 3,
                "created_at": "2026-03-04T16:00:00Z",
                "updated_at": "2026-03-07T11:10:00Z",
                "author": "qa_eve",
                "state": "open",
            },
        ],
    },
    "demo/react-metricshub": {
        "metadata": {
            "name": "react-metricshub",
            "owner": "demo",
            "full_name": "demo/react-metricshub [DEMO REPO]",
            "description": "Modern developer analytics dashboard built with TypeScript, React, and TailwindCSS.",
            "language": "TypeScript",
            "topics": ["typescript", "react", "dashboard", "frontend", "jest", "tailwindcss"],
            "default_branch": "main",
            "stargazers_count": 920,
            "forks_count": 140,
            "open_issues_count": 12,
            "license": "Apache-2.0",
            "html_url": "https://github.com/demo/react-metricshub",
            "archived": False,
        },
        "root_files": [
            "package.json",
            "tsconfig.json",
            "README.md",
            "src",
            "tests",
            ".github",
            ".prettierrc",
        ],
        "readme": """# React MetricsHub (Synthetic Demo Repository)
Interactive developer productivity dashboard with real-time charting.

## Stack
- React 18 & TypeScript
- Jest & React Testing Library
- TailwindCSS
""",
        "contributing": """# Contributing to React MetricsHub

```bash
npm install
npm test
npm run lint
```
""",
        "issues": [
            {
                "number": 201,
                "title": "Fix broken external documentation link in settings sidebar",
                "body": "The link pointing to the API documentation in `src/components/Sidebar.tsx` returns a 404 because the URL changed from docs.metricshub.io to docs.metricshub.com. Update the link and ensure it opens with `rel='noopener noreferrer'`.",
                "labels": [
                    {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
                    {"name": "documentation", "color": "0075ca", "description": "Docs and links"},
                ],
                "label_names": ["good first issue", "documentation"],
                "html_url": "https://github.com/demo/react-metricshub/issues/201",
                "comments": 1,
                "created_at": "2026-03-02T11:00:00Z",
                "updated_at": "2026-03-05T14:00:00Z",
                "author": "ui_fay",
                "state": "open",
            },
            {
                "number": 202,
                "title": "Add accessible ARIA labels to date range selector buttons",
                "body": "Lighthouse accessibility audit flags missing `aria-label` tags on the date filter button group in `src/components/DateRangePicker.tsx`. Add proper labels and write a test in `DateRangePicker.test.tsx` verifying screen reader accessibility.",
                "labels": [
                    {"name": "accessibility", "color": "0052cc", "description": "a11y improvements"},
                    {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
                    {"name": "react", "color": "61dafb", "description": "React component work"},
                ],
                "label_names": ["accessibility", "good first issue", "react"],
                "html_url": "https://github.com/demo/react-metricshub/issues/202",
                "comments": 3,
                "created_at": "2026-03-03T09:30:00Z",
                "updated_at": "2026-03-06T10:45:00Z",
                "author": "a11y_guru",
                "state": "open",
            },
            {
                "number": 203,
                "title": "Refactor chart state to use React Query for caching and auto-invalidation",
                "body": "Currently charts refetch full raw series on every tab switch. Refactor `useMetricsQuery` hook using TanStack React Query to implement stale-while-revalidate caching and background polling.",
                "labels": [
                    {"name": "enhancement", "color": "a2eeef", "description": "Feature enhancement"},
                    {"name": "react", "color": "61dafb", "description": "React framework"},
                ],
                "label_names": ["enhancement", "react"],
                "html_url": "https://github.com/demo/react-metricshub/issues/203",
                "comments": 5,
                "created_at": "2026-02-28T15:00:00Z",
                "updated_at": "2026-03-07T16:00:00Z",
                "author": "lead_george",
                "state": "open",
            },
        ],
    },
    "demo/scikit-mlpipe": {
        "metadata": {
            "name": "scikit-mlpipe",
            "owner": "demo",
            "full_name": "demo/scikit-mlpipe [DEMO REPO]",
            "description": "Modular machine learning pipelines, feature transformation, and evaluation framework for Python.",
            "language": "Python",
            "topics": ["machine-learning", "scikit-learn", "pandas", "numpy", "python", "data-science"],
            "default_branch": "main",
            "stargazers_count": 2150,
            "forks_count": 420,
            "open_issues_count": 24,
            "license": "BSD-3-Clause",
            "html_url": "https://github.com/demo/scikit-mlpipe",
            "archived": False,
        },
        "root_files": [
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            "README.md",
            "CONTRIBUTING.md",
            "mlpipe",
            "tests",
            ".github",
        ],
        "readme": """# Scikit MLPipe (Synthetic Demo Repository)
Reusable, reproducible machine learning transformers and metric evaluators.
""",
        "contributing": """# Contribution Guidelines
Install dependencies:
```bash
pip install -r requirements.txt
pytest tests/
```
""",
        "issues": [
            {
                "number": 301,
                "title": "Add docstrings and usage examples for RobustStandardScaler",
                "body": "The `RobustStandardScaler` transformer in `mlpipe/transformers/scaling.py` is missing standard Google-style docstrings, parameter type definitions, and a quick snippet showing usage with pandas DataFrames.",
                "labels": [
                    {"name": "documentation", "color": "0075ca", "description": "Documentation work"},
                    {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
                ],
                "label_names": ["documentation", "good first issue"],
                "html_url": "https://github.com/demo/scikit-mlpipe/issues/301",
                "comments": 2,
                "created_at": "2026-03-01T12:00:00Z",
                "updated_at": "2026-03-04T08:00:00Z",
                "author": "data_dan",
                "state": "open",
            },
            {
                "number": 302,
                "title": "Support pandas CategoricalDtype in OneHotEncoderWrapper",
                "body": "When a pandas DataFrame column with `category` dtype is passed to `OneHotEncoderWrapper`, it throws a ValueError because only object and string types were checked. Add support for pandas `category` dtypes and add unit tests in `tests/test_encoders.py`.",
                "labels": [
                    {"name": "bug", "color": "d73a4a", "description": "Bug fix"},
                    {"name": "pandas", "color": "150458", "description": "Pandas dataframe work"},
                    {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
                ],
                "label_names": ["bug", "pandas", "good first issue"],
                "html_url": "https://github.com/demo/scikit-mlpipe/issues/302",
                "comments": 6,
                "created_at": "2026-03-03T17:00:00Z",
                "updated_at": "2026-03-06T11:30:00Z",
                "author": "ml_helen",
                "state": "open",
            },
            {
                "number": 303,
                "title": "Implement multi-threaded cross-validation chunk caching for out-of-core datasets",
                "body": "When training cross-validation folds on large datasets exceeding available RAM, the pipeline currently re-reads chunks from disk repeatedly. Design an out-of-core mmap memory buffer cache supporting concurrent fold workers without memory bloat.",
                "labels": [
                    {"name": "advanced", "color": "b60205", "description": "High complexity"},
                    {"name": "performance", "color": "d4c5f9", "description": "Optimization"},
                ],
                "label_names": ["advanced", "performance"],
                "html_url": "https://github.com/demo/scikit-mlpipe/issues/303",
                "comments": 11,
                "created_at": "2026-02-18T10:00:00Z",
                "updated_at": "2026-03-07T14:15:00Z",
                "author": "dr_ian",
                "state": "open",
            },
        ],
    },
}


def get_demo_repository(key: str) -> Dict[str, Any]:
    """Retrieve demo repository data by key."""
    if key in DEMO_REPOSITORIES:
        return DEMO_REPOSITORIES[key]
    # Default to first
    return DEMO_REPOSITORIES["demo/fastapi-taskflow"]


def list_demo_repositories() -> List[str]:
    """List keys of all available synthetic demonstration repositories."""
    return list(DEMO_REPOSITORIES.keys())
