"""Contribution guide reader and parser for extracting setup, test, and PR guidelines."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


class ContributionGuideReader:
    """Extracts actionable developer workflows from CONTRIBUTING.md or README files."""

    def __init__(self, raw_content: Optional[str], repo_name: str, repo_url: str):
        self.raw_content = raw_content or ""
        self.repo_name = repo_name
        self.repo_url = repo_url

    def parse(self) -> Dict[str, Any]:
        """Analyze markdown guide and extract key sections."""
        if not self.raw_content.strip():
            return {
                "available": False,
                "message": f"No dedicated CONTRIBUTING.md guide was found for {self.repo_name}.",
                "source_url": f"{self.repo_url}#readme",
                "setup_commands": [],
                "test_commands": [],
                "lint_commands": [],
                "pr_guidelines": [
                    "Always branch from the main/default branch.",
                    "Include unit tests covering any code changes.",
                    "Write clear, descriptive git commit messages.",
                    "Reference the issue number in your pull request description (e.g. 'Fixes #123').",
                    "Be polite and responsive to maintainer review comments.",
                ],
            }

        text = self.raw_content

        # Extract code blocks
        code_blocks = re.findall(r"```(?:bash|sh|shell|cmd|console)?\s*\n(.*?)\n```", text, flags=re.DOTALL)
        flat_commands: List[str] = []
        for block in code_blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip() and not l.strip().startswith("#")]
            flat_commands.extend(lines)

        setup_commands = []
        test_commands = []
        lint_commands = []

        for cmd in flat_commands:
            c_lower = cmd.lower()
            if any(k in c_lower for k in ("clone", "install", "pip ", "npm i", "yarn add", "poetry ", "venv", "pnpm ")):
                setup_commands.append(cmd)
            elif any(k in c_lower for k in ("test", "pytest", "jest", "unittest", "cargo test", "npm t")):
                test_commands.append(cmd)
            elif any(k in c_lower for k in ("lint", "ruff", "black", "flake8", "eslint", "prettier", "pre-commit")):
                lint_commands.append(cmd)

        # Pull request guidelines extraction
        pr_guidelines: List[str] = []
        pr_matches = re.findall(r"(?:pull request|pr|submitting changes|how to contribute).*?\n((?:[-*]\s+.*?\n)+)", text, flags=re.IGNORECASE)
        if pr_matches:
            bullet_lines = [b.strip("-* ").strip() for b in pr_matches[0].splitlines() if b.strip()]
            pr_guidelines.extend(bullet_lines[:6])

        if not pr_guidelines:
            pr_guidelines = [
                "Create a feature branch for your changes.",
                "Ensure local test suite passes before opening a PR.",
                "Reference the issue number in the PR title or description.",
                "Follow repository styling conventions and linter standards.",
            ]

        return {
            "available": True,
            "message": f"Successfully parsed contribution guidelines for {self.repo_name}.",
            "source_url": f"{self.repo_url}/blob/main/CONTRIBUTING.md",
            "setup_commands": list(dict.fromkeys(setup_commands))[:8],
            "test_commands": list(dict.fromkeys(test_commands))[:6],
            "lint_commands": list(dict.fromkeys(lint_commands))[:6],
            "pr_guidelines": pr_guidelines,
            "raw_snippet": text[:1500] + ("..." if len(text) > 1500 else ""),
        }
