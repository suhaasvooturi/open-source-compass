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
    "psf/requests": {
        "metadata": {
            "name": "requests",
            "owner": "psf",
            "full_name": "psf/requests [DEMO / CACHED SNAPSHOT]",
            "description": "A simple, yet elegant, HTTP library for Python, built for human beings.",
            "language": "Python",
            "topics": ["python", "http", "requests", "client", "networking"],
            "default_branch": "main",
            "stargazers_count": 51200,
            "forks_count": 9200,
            "open_issues_count": 24,
            "license": "Apache-2.0",
            "html_url": "https://github.com/psf/requests",
            "archived": False,
        },
        "root_files": [
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            "README.md",
            "CONTRIBUTING.md",
            "tests",
            "src/requests",
            "docs",
            "Makefile",
        ],
        "readme": """# Requests: HTTP for Humans™
Requests is an elegant and simple HTTP library for Python, built for human beings.

## Features
- Keep-Alive & Connection Pooling
- International Domains and URLs
- Sessions with Cookie Persistence
- Browser-style SSL Verification
- Automatic Content Decompression
- Basic/Digest Authentication

## Installation
```bash
pip install requests
```
""",
        "contributing": """# Contributing to Requests
We love contributions from everyone.

## Development Setup
```bash
git clone https://github.com/psf/requests.git
cd requests
pip install -e ".[dev]"
```

## Running Tests
```bash
pytest tests/
pytest tests/test_requests.py
tox
```

## Pull Request Guidelines
- Follow PEP 8 guidelines.
- Add unit tests for bug fixes and new behaviors.
- Keep commits focused and provide clear descriptions.
""",
        "issues": [
            {
                "number": 1001,
                "title": "Fix missing timeout warning in documentation examples",
                "body": "The quickstart guide examples for `requests.get()` in `docs/user/quickstart.rst` do not specify a timeout parameter. According to security recommendations, examples should always show `timeout=5` or mention timeout best practices to prevent newcomers from writing hanging network calls.",
                "labels": [
                    {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
                    {"name": "documentation", "color": "0075ca", "description": "Improvements to docs"},
                ],
                "label_names": ["good first issue", "documentation"],
                "html_url": "https://github.com/psf/requests/issues/1001",
                "comments": 1,
                "created_at": "2026-03-01T10:00:00Z",
                "updated_at": "2026-03-03T11:00:00Z",
                "author": "security_enthusiast",
                "state": "open",
            },
            {
                "number": 1002,
                "title": "Add retry strategy test case with custom backoff factor",
                "body": "In `tests/test_requests.py`, we need a dedicated test verifying that `HTTPAdapter` configured with `urllib3.util.retry.Retry(backoff_factor=0.5)` properly respects custom delays during simulated HTTP 503 Service Unavailable responses.\n\n### Acceptance Criteria\n- Use pytest and unittest.mock to simulate server responses.\n- Verify backoff sleep intervals match expected values.",
                "labels": [
                    {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
                    {"name": "testing", "color": "fbca04", "description": "Testing tasks"},
                ],
                "label_names": ["good first issue", "testing"],
                "html_url": "https://github.com/psf/requests/issues/1002",
                "comments": 2,
                "created_at": "2026-03-02T15:00:00Z",
                "updated_at": "2026-03-04T09:00:00Z",
                "author": "qa_tester",
                "state": "open",
            },
            {
                "number": 1003,
                "title": "Support HTTP/2 stream prioritization flags in custom transport adapter",
                "body": "Allow users implementing HTTP/2 transport adapters to pass stream priority headers without them being stripped during session header normalization.",
                "labels": [
                    {"name": "enhancement", "color": "a2eeef", "description": "New feature"},
                    {"name": "help wanted", "color": "008672", "description": "Extra attention needed"},
                ],
                "label_names": ["enhancement", "help wanted"],
                "html_url": "https://github.com/psf/requests/issues/1003",
                "comments": 5,
                "created_at": "2026-02-28T12:00:00Z",
                "updated_at": "2026-03-05T16:00:00Z",
                "author": "net_engineer",
                "state": "open",
            },
            {
                "number": 1004,
                "title": "Refactor connection pool lock contention in multi-threaded session dispatcher",
                "body": "Profile thread contention across `requests.Session` instances sharing an adapter with a large `pool_maxsize`. Optimize lock acquisition paths in `requests/adapters.py`.",
                "labels": [
                    {"name": "advanced", "color": "b60205", "description": "High complexity"},
                    {"name": "performance", "color": "d4c5f9", "description": "Optimization"},
                ],
                "label_names": ["advanced", "performance"],
                "html_url": "https://github.com/psf/requests/issues/1004",
                "comments": 14,
                "created_at": "2026-02-20T08:00:00Z",
                "updated_at": "2026-03-06T18:00:00Z",
                "author": "perf_lead",
                "state": "open",
            },
        ],
    },
    "tiangolo/fastapi": {
        "metadata": {
            "name": "fastapi",
            "owner": "tiangolo",
            "full_name": "tiangolo/fastapi [DEMO / CACHED SNAPSHOT]",
            "description": "FastAPI framework, high performance, easy to learn, fast to code, ready for production.",
            "language": "Python",
            "topics": ["python", "fastapi", "pydantic", "starlette", "asyncio", "rest-api"],
            "default_branch": "master",
            "stargazers_count": 78000,
            "forks_count": 6400,
            "open_issues_count": 45,
            "license": "MIT",
            "html_url": "https://github.com/tiangolo/fastapi",
            "archived": False,
        },
        "root_files": [
            "pyproject.toml",
            "requirements.txt",
            "README.md",
            "CONTRIBUTING.md",
            "fastapi",
            "tests",
            "docs",
        ],
        "readme": """# FastAPI
FastAPI is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints.

## Key Features
- Fast: Very high performance, on par with NodeJS and Go.
- Fast to code: Increase speed to develop features by about 200% to 300%.
- Fewer bugs: Reduce about 40% of human (developer) induced errors.
- Intuitive: Great editor support. Completion everywhere. Less time debugging.
""",
        "contributing": """# Contributing to FastAPI
Thank you for your interest in contributing to FastAPI!

## Development Setup
```bash
git clone https://github.com/tiangolo/fastapi.git
cd fastapi
pdm install
```

## Running Tests
```bash
pytest tests/
bash scripts/test.sh
```
""",
        "issues": [
            {
                "number": 2001,
                "title": "Update tutorial documentation for Pydantic v2 field validator decorators",
                "body": "The tutorial in `docs/tutorial/body-nested-models.md` still demonstrates `@validator` instead of `@field_validator(mode='before')` from Pydantic v2. Update the doc code snippet and verify the example script runs without deprecation warnings.",
                "labels": [
                    {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
                    {"name": "documentation", "color": "0075ca", "description": "Improvements to docs"},
                ],
                "label_names": ["good first issue", "documentation"],
                "html_url": "https://github.com/tiangolo/fastapi/issues/2001",
                "comments": 2,
                "created_at": "2026-03-02T11:00:00Z",
                "updated_at": "2026-03-05T14:00:00Z",
                "author": "doc_writer",
                "state": "open",
            },
            {
                "number": 2002,
                "title": "Add test assertion for query parameter alias with special characters",
                "body": "In `tests/test_query.py`, write a unit test demonstrating that query parameters with kebab-case or alias like `filter-by` and `order_by` parse properly through OpenAPI specs and dependency injections.",
                "labels": [
                    {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
                    {"name": "testing", "color": "fbca04", "description": "Testing tasks"},
                ],
                "label_names": ["good first issue", "testing"],
                "html_url": "https://github.com/tiangolo/fastapi/issues/2002",
                "comments": 3,
                "created_at": "2026-03-03T16:00:00Z",
                "updated_at": "2026-03-06T10:00:00Z",
                "author": "test_lover",
                "state": "open",
            },
            {
                "number": 2003,
                "title": "Support streaming multipart file uploads with custom chunk size",
                "body": "Add support for configuring custom chunk buffer sizes when processing large multipart file uploads via `UploadFile` to prevent spikes in memory consumption.",
                "labels": [
                    {"name": "enhancement", "color": "a2eeef", "description": "New feature"},
                    {"name": "help wanted", "color": "008672", "description": "Extra attention needed"},
                ],
                "label_names": ["enhancement", "help wanted"],
                "html_url": "https://github.com/tiangolo/fastapi/issues/2003",
                "comments": 8,
                "created_at": "2026-02-25T14:00:00Z",
                "updated_at": "2026-03-07T12:00:00Z",
                "author": "api_architect",
                "state": "open",
            },
        ],
    },
    "suhaasvooturi/open-source-compass": {
        "metadata": {
            "name": "open-source-compass",
            "owner": "suhaasvooturi",
            "full_name": "suhaasvooturi/open-source-compass [DEMO / CACHED SNAPSHOT]",
            "description": "AI-Assisted Open-Source Contribution Finder. Find your first issue. Make your first contribution.",
            "language": "Python",
            "topics": ["python", "streamlit", "open-source", "machine-learning", "scikit-learn", "ai"],
            "default_branch": "main",
            "stargazers_count": 152,
            "forks_count": 28,
            "open_issues_count": 12,
            "license": "MIT",
            "html_url": "https://github.com/suhaasvooturi/open-source-compass",
            "archived": False,
        },
        "root_files": [
            "pyproject.toml",
            "requirements.txt",
            "README.md",
            "CONTRIBUTING.md",
            "app.py",
            "finder",
            "pages",
            "tests",
        ],
        "readme": """# OpenSource Compass 🧭
AI-Assisted Open-Source Contribution Finder. Find your first issue. Make your first contribution.
""",
        "contributing": """# Contributing to OpenSource Compass
Welcome! We love first-time contributors.

## Local Setup
```bash
git clone https://github.com/suhaasvooturi/open-source-compass.git
cd open-source-compass
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest tests/ -v
streamlit run app.py
```
""",
        "issues": [
            {
                "number": 501,
                "title": "Add copy-to-clipboard button for recommended git commands in issue card",
                "body": "In `finder/ui_components.py`, add a clean copyable code block or button allowing newcomers to immediately copy the git commands needed to clone and branch for that specific issue.",
                "labels": [
                    {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
                    {"name": "ui", "color": "0075ca", "description": "UI improvements"},
                ],
                "label_names": ["good first issue", "ui"],
                "html_url": "https://github.com/suhaasvooturi/open-source-compass/issues/501",
                "comments": 1,
                "created_at": "2026-03-01T12:00:00Z",
                "updated_at": "2026-03-04T10:00:00Z",
                "author": "suhaasvooturi",
                "state": "open",
            },
            {
                "number": 502,
                "title": "Add unit tests verifying alias resolution for common repository names",
                "body": "In `tests/test_github_api.py`, write tests verifying that typing shorthand aliases like 'fastapi', 'requests', and 'flask' correctly resolves to their official owner/repo pairs.",
                "labels": [
                    {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
                    {"name": "testing", "color": "fbca04", "description": "Testing tasks"},
                ],
                "label_names": ["good first issue", "testing"],
                "html_url": "https://github.com/suhaasvooturi/open-source-compass/issues/502",
                "comments": 2,
                "created_at": "2026-03-02T14:00:00Z",
                "updated_at": "2026-03-05T11:00:00Z",
                "author": "suhaasvooturi",
                "state": "open",
            },
            {
                "number": 503,
                "title": "Add CSV export for filtered issues in the Issue Explorer view",
                "body": "Allow users to download their filtered issues as a clean CSV table with columns for Issue #, Title, Difficulty, Score, Effort, and URL.",
                "labels": [
                    {"name": "enhancement", "color": "a2eeef", "description": "New feature"},
                    {"name": "help wanted", "color": "008672", "description": "Extra attention needed"},
                ],
                "label_names": ["enhancement", "help wanted"],
                "html_url": "https://github.com/suhaasvooturi/open-source-compass/issues/503",
                "comments": 3,
                "created_at": "2026-03-03T18:00:00Z",
                "updated_at": "2026-03-06T15:00:00Z",
                "author": "suhaasvooturi",
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
    """List keys of all available demonstration and snapshot repositories."""
    return list(DEMO_REPOSITORIES.keys())


def get_snapshot_for_repo(owner: str, repo: str) -> Optional[Dict[str, Any]]:
    """Return a pre-cached offline snapshot for a known popular repository if available."""
    target_slug = f"{owner.lower().strip()}/{repo.lower().strip()}"
    for key, data in DEMO_REPOSITORIES.items():
        if key.lower() == target_slug:
            return data
        if key.lower().endswith(f"/{repo.lower().strip()}"):
            return data
    return None

