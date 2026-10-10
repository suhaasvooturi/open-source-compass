"""Saved shortlist manager supporting session storage, JSON/CSV exports, and removal."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from finder.ranking import RankedIssue


class ShortlistManager:
    """Manages the user's shortlisted GitHub issues."""

    def __init__(self, initial_items: Optional[List[Dict[str, Any]]] = None):
        self._items: Dict[int, Dict[str, Any]] = {}
        if initial_items:
            for it in initial_items:
                num = it.get("number")
                if num:
                    self._items[int(num)] = it

    def add(self, issue: RankedIssue | Dict[str, Any]) -> bool:
        """Add an issue to the shortlist. Returns True if newly added, False if already present."""
        if isinstance(issue, RankedIssue):
            data = {
                "number": issue.number,
                "title": issue.title,
                "html_url": issue.html_url,
                "repository": issue.repository_full_name,
                "difficulty": issue.difficulty,
                "match_score_percent": issue.match_score_percent,
                "estimated_effort": issue.estimated_effort,
                "technologies": issue.technologies_involved,
                "relevant_skills": issue.relevant_user_skills,
                "missing_skills": issue.missing_skills,
                "notes": "",
            }
        else:
            data = dict(issue)

        num = data.get("number")
        if not num:
            return False

        if num in self._items:
            return False

        self._items[int(num)] = data
        return True

    def remove(self, issue_number: int) -> bool:
        """Remove an issue from the shortlist by number."""
        num = int(issue_number)
        if num in self._items:
            del self._items[num]
            return True
        return False

    def clear(self) -> None:
        """Clear all shortlisted items."""
        self._items.clear()

    def is_saved(self, issue_number: int) -> bool:
        """Check if an issue number is currently in the shortlist."""
        return int(issue_number) in self._items

    def list_all(self) -> List[Dict[str, Any]]:
        """Return all shortlisted items."""
        return list(self._items.values())

    def to_json(self) -> str:
        """Export shortlist as a formatted JSON string."""
        return json.dumps(self.list_all(), indent=2)

    def to_csv(self) -> str:
        """Export shortlist as CSV text."""
        items = self.list_all()
        if not items:
            return ""

        output = io.StringIO()
        fieldnames = [
            "number",
            "title",
            "repository",
            "difficulty",
            "match_score_percent",
            "estimated_effort",
            "technologies",
            "html_url",
            "missing_skills",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for item in items:
            row = dict(item)
            if isinstance(row.get("technologies"), list):
                row["technologies"] = ", ".join(row["technologies"])
            if isinstance(row.get("missing_skills"), list):
                row["missing_skills"] = ", ".join(row["missing_skills"])
            writer.writerow(row)

        return output.getvalue()
