"""Issue classification engine for determining difficulty levels and effort estimation."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from finder.repository_analyzer import detect_technologies_from_text

# Label hints
BEGINNER_LABEL_HINTS = {
    "good first issue",
    "good-first-issue",
    "good_first_issue",
    "beginner",
    "beginner friendly",
    "starter",
    "starter-issue",
    "first-timers-only",
    "first timers only",
    "easy",
    "e-easy",
    "difficulty: easy",
    "difficulty/easy",
    "level: beginner",
    "low hanging fruit",
    "low-hanging-fruit",
    "documentation",
    "docs",
    "type: docs",
    "type: documentation",
    "quick fix",
    "quick-fix",
    "trivial",
    "up-for-grabs",
    "hacktoberfest",
    "newcomer",
    "first contribution",
    "good-first-bug",
}

INTERMEDIATE_LABEL_HINTS = {
    "help wanted",
    "help-wanted",
    "enhancement",
    "feature",
    "bug",
    "type: bug",
    "type: feature",
    "type: enhancement",
    "refactor",
    "testing",
    "test",
    "intermediate",
    "moderate",
    "needs-pr",
    "ready for dev",
}

ADVANCED_LABEL_HINTS = {
    "complex",
    "advanced",
    "architecture",
    "hard",
    "difficulty: hard",
    "performance",
    "perf",
    "security",
    "breaking-change",
    "breaking change",
    "core",
    "concurrency",
    "rfc",
    "design",
}

# Regex text hints
BEGINNER_TEXT_PATTERNS = [
    r"\btypo\b",
    r"\bfix typo\b",
    r"\bdocumentation\b",
    r"\bupdate readme\b",
    r"\bdocstring\b",
    r"\blint(?:ing)?\b",
    r"\bformatting\b",
    r"\badd test\b",
    r"\bsmall fix\b",
    r"\bminor\b",
    r"\bexample\b",
    r"\bspelling\b",
    r"\bbroken link\b",
    r"\bcomment\b",
]

ADVANCED_TEXT_PATTERNS = [
    r"\barchitect(?:ure)?\b",
    r"\bconcurrency\b",
    r"\brace condition\b",
    r"\bdeadlock\b",
    r"\bmemory leak\b",
    r"\bredesign\b",
    r"\bdistributed\b",
    r"\bconsensus\b",
    r"\bprotocol\b",
    r"\bsecurity vulnerability\b",
    r"\bcve\b",
    r"\bcompiler\b",
    r"\bparser\b",
    r"\bthread-safe\b",
    r"\basync runtime\b",
    r"\boptimization\b",
    r"\bbenchmark\b",
]

INTERMEDIATE_TEXT_PATTERNS = [
    r"\badd endpoint\b",
    r"\bvalidation\b",
    r"\berror handling\b",
    r"\brefactor\b",
    r"\bdatabase schema\b",
    r"\bmigrat(?:e|ion)\b",
    r"\bapi\b",
    r"\bfeature\b",
    r"\bquery\b",
    r"\bserialize\b",
    r"\bdeserializ\b",
    r"\bcaching\b",
]


class IssueClassifier:
    """Classifies GitHub issues into difficulty levels (Beginner, Intermediate, Advanced, Uncertain)

    using multi-signal heuristics and transparent evidence logging.
    """

    def __init__(self, issue: Dict[str, Any], repo_context: Optional[Dict[str, Any]] = None):
        self.issue = issue
        self.repo_context = repo_context or {}
        self.title = (issue.get("title") or "").strip()
        self.body = (issue.get("body") or "").strip()
        self.labels = [lbl.lower() for lbl in issue.get("label_names", [])]
        self.full_text = f"{self.title}\n{self.body}".lower()

    def classify(self) -> Dict[str, Any]:
        """Perform classification returning difficulty, confidence score, evidence list, and effort."""
        evidence: List[str] = []
        beginner_points = 0
        intermediate_points = 0
        advanced_points = 0

        # Check for insufficient information
        total_words = len(self.full_text.split())
        if total_words < 5 and not self.labels:
            return {
                "difficulty": "Difficulty uncertain",
                "confidence": 0.2,
                "evidence": ["Issue title and description contain insufficient detail (< 5 words, no labels)."],
                "estimated_effort": "Uncertain (depends on clarification)",
                "technologies_involved": [],
                "beginner_friendly": False,
            }

        # 1. Label Analysis
        label_matched = False
        for lbl in self.labels:
            if any(b in lbl for b in BEGINNER_LABEL_HINTS):
                beginner_points += 3
                evidence.append(f"Label '{lbl}' indicates a beginner-friendly or first-timer task.")
                label_matched = True
            elif any(a in lbl for a in ADVANCED_LABEL_HINTS):
                advanced_points += 3
                evidence.append(f"Label '{lbl}' signals complex or architectural work.")
                label_matched = True
            elif any(i in lbl for i in INTERMEDIATE_LABEL_HINTS):
                intermediate_points += 1
                evidence.append(f"Label '{lbl}' typically represents standard engineering work.")
                label_matched = True

        # 2. Text Pattern Analysis
        for pat in BEGINNER_TEXT_PATTERNS:
            if re.search(pat, self.full_text):
                beginner_points += 2
                evidence.append(f"Found introductory keyword pattern matching '{pat.strip(r'\\b')}'.")
                break

        for pat in ADVANCED_TEXT_PATTERNS:
            if re.search(pat, self.full_text):
                advanced_points += 2
                evidence.append(f"Found advanced/system-level keyword pattern matching '{pat.strip(r'\\b')}'.")
                break

        for pat in INTERMEDIATE_TEXT_PATTERNS:
            if re.search(pat, self.full_text):
                intermediate_points += 1.5
                evidence.append(f"Found core feature/improvement pattern matching '{pat.strip(r'\\b')}'.")
                break

        # 3. Structural Complexity Signals
        code_blocks = len(re.findall(r"```", self.body)) // 2
        checkboxes = len(re.findall(r"- \[[ xX]\]", self.body))

        if checkboxes > 6:
            advanced_points += 1.5
            evidence.append(f"Issue has a multi-step checklist with {checkboxes} task items.")
        elif checkboxes in (1, 2, 3):
            intermediate_points += 1
            evidence.append(f"Issue defines a focused checklist with {checkboxes} tasks.")

        if code_blocks > 3:
            intermediate_points += 1
            evidence.append(f"Issue contains multiple ({code_blocks}) code snippets or stack traces.")

        # 4. Technologies involved
        technologies = detect_technologies_from_text(f"{self.title}\n{self.body}")
        if not technologies and self.repo_context.get("primary_language"):
            technologies = [self.repo_context["primary_language"]]

        # 5. Difficulty arbitration
        difficulty: str
        confidence: float
        estimated_effort: str

        max_score = max(beginner_points, intermediate_points, advanced_points)

        if max_score == 0:
            difficulty = "Difficulty uncertain"
            confidence = 0.3
            estimated_effort = "Estimated effort varies (requires repo review)"
            evidence.append("Insufficient distinct keyword or label signals to assign high confidence.")
        elif advanced_points > intermediate_points and advanced_points > beginner_points:
            difficulty = "Advanced"
            confidence = min(0.9, 0.5 + (advanced_points * 0.1))
            estimated_effort = "8 - 20+ hours (architectural review, tests, edge cases)"
        elif beginner_points > advanced_points and beginner_points >= intermediate_points:
            difficulty = "Beginner"
            confidence = min(0.95, 0.6 + (beginner_points * 0.1))
            estimated_effort = "1 - 3 hours (reading guide, quick patch, verify tests)"
        else:
            difficulty = "Intermediate"
            confidence = min(0.85, 0.5 + (intermediate_points * 0.1))
            estimated_effort = "3 - 8 hours (implementation, unit tests, PR cycle)"

        beginner_friendly = difficulty == "Beginner" or any(
            any(b in lbl for b in BEGINNER_LABEL_HINTS) for lbl in self.labels
        )

        return {
            "difficulty": difficulty,
            "confidence": round(confidence, 2),
            "evidence": evidence,
            "estimated_effort": estimated_effort,
            "technologies_involved": technologies,
            "beginner_friendly": beginner_friendly,
        }
