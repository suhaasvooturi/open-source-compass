"""Explainable ranking engine for GitHub issue matching."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from finder.issue_classifier import IssueClassifier
from finder.repository_analyzer import normalize_skills_list
from finder.semantic_matcher import SemanticMatcher


@dataclass
class RankingWeights:
    """Configurable weights for the multi-signal recommendation engine."""

    skill_overlap: float = 0.30
    experience_fit: float = 0.25
    learning_goals: float = 0.20
    beginner_friendly_label: float = 0.15
    semantic_similarity: float = 0.10

    def normalize(self) -> Dict[str, float]:
        """Normalize weights to ensure they sum strictly to 1.0."""
        total = (
            self.skill_overlap
            + self.experience_fit
            + self.learning_goals
            + self.beginner_friendly_label
            + self.semantic_similarity
        )
        if total <= 0:
            return {
                "skill_overlap": 0.2,
                "experience_fit": 0.2,
                "learning_goals": 0.2,
                "beginner_friendly_label": 0.2,
                "semantic_similarity": 0.2,
            }
        return {
            "skill_overlap": round(self.skill_overlap / total, 4),
            "experience_fit": round(self.experience_fit / total, 4),
            "learning_goals": round(self.learning_goals / total, 4),
            "beginner_friendly_label": round(self.beginner_friendly_label / total, 4),
            "semantic_similarity": round(self.semantic_similarity / total, 4),
        }


# Experience compatibility matrix
EXPERIENCE_FIT_MATRIX: Dict[str, Dict[str, float]] = {
    "beginner": {
        "beginner": 1.0,
        "difficulty uncertain": 0.60,
        "intermediate": 0.35,
        "advanced": 0.10,
    },
    "intermediate": {
        "intermediate": 1.0,
        "difficulty uncertain": 0.70,
        "beginner": 0.75,
        "advanced": 0.50,
    },
    "advanced": {
        "advanced": 1.0,
        "intermediate": 0.85,
        "difficulty uncertain": 0.70,
        "beginner": 0.40,
    },
}


@dataclass
class RankedIssue:
    """Data class holding an analyzed, scored, and explained GitHub issue."""

    number: int
    title: str
    body: str
    html_url: str
    labels: List[Dict[str, str]]
    label_names: List[str]
    comments_count: int
    created_at: str
    updated_at: str
    author: str
    repository_full_name: str
    # Classification results
    difficulty: str
    difficulty_confidence: float
    difficulty_evidence: List[str]
    estimated_effort: str
    technologies_involved: List[str]
    beginner_friendly: bool
    # Match Scoring
    match_score: float  # [0.0, 1.0]
    match_score_percent: int  # [0, 100]
    score_breakdown: Dict[str, float]
    # Skill gap analysis
    relevant_user_skills: List[str]
    missing_skills: List[str]
    # Recommendation reasoning
    match_reasons: List[str]
    preparation_steps: List[str]


class RecommendationEngine:
    """Ranks and explains open GitHub issues against developer profile."""

    def __init__(
        self,
        weights: Optional[RankingWeights] = None,
        semantic_matcher: Optional[SemanticMatcher] = None,
    ):
        self.weights = weights or RankingWeights()
        self.semantic_matcher = semantic_matcher or SemanticMatcher()

    def rank_issues(
        self,
        issues: List[Dict[str, Any]],
        user_skills: List[str],
        experience_level: str,
        learning_goals: List[str],
        repo_metadata: Dict[str, Any],
        repo_analysis: Optional[Dict[str, Any]] = None,
    ) -> List[RankedIssue]:
        """Rank open issues against user profile and return ordered list of RankedIssue objects."""
        if not issues:
            return []

        norm_weights = self.weights.normalize()
        user_skills_clean = normalize_skills_list(user_skills)
        user_skills_set = {s.lower() for s in user_skills_clean}
        experience_clean = experience_level.strip().lower()
        goals_clean = normalize_skills_list(learning_goals)
        goals_set = {g.lower() for g in goals_clean}

        # Build query string for semantic matching
        query_text = (
            f"Skills: {', '.join(user_skills_clean)}. "
            f"Experience: {experience_level}. "
            f"Learning goals: {', '.join(goals_clean)}."
        )

        # Batch prepare issue document texts for semantic matcher
        issue_docs = [
            f"{iss.get('title', '')} {iss.get('body', '')[:1000]} {' '.join(iss.get('label_names', []))}"
            for iss in issues
        ]
        semantic_scores = self.semantic_matcher.compute_batch_similarities(query_text, issue_docs)

        ranked_list: List[RankedIssue] = []

        for idx, issue in enumerate(issues):
            # 1. Classify Issue
            classifier = IssueClassifier(issue, repo_context=repo_analysis or {})
            classification = classifier.classify()

            difficulty = classification["difficulty"]
            techs = classification["technologies_involved"]
            diff_evidence = classification["evidence"]
            estimated_effort = classification["estimated_effort"]
            beginner_friendly = classification["beginner_friendly"]

            # 2. Skill Overlap Calculation
            techs_set = {t.lower() for t in techs}
            overlap = user_skills_set.intersection(techs_set)
            primary_lang = (repo_metadata.get("language") or "").lower()

            if techs_set:
                skill_overlap_ratio = len(overlap) / len(techs_set)
            elif primary_lang and primary_lang in user_skills_set:
                skill_overlap_ratio = 0.8
            elif not user_skills_set:
                skill_overlap_ratio = 0.4
            else:
                skill_overlap_ratio = 0.2

            # Give a boost if repo's primary language is known
            if primary_lang and primary_lang in user_skills_set:
                skill_overlap_ratio = min(1.0, skill_overlap_ratio + 0.15)

            # 3. Experience Fit Calculation
            exp_row = EXPERIENCE_FIT_MATRIX.get(experience_clean, EXPERIENCE_FIT_MATRIX["intermediate"])
            exp_fit_score = exp_row.get(difficulty.lower(), 0.50)

            # 4. Learning Goals Alignment
            full_issue_text = f"{issue.get('title', '')} {issue.get('body', '')}".lower()
            goal_matches = 0
            for goal in goals_set:
                if goal in full_issue_text or any(goal in t for t in techs_set):
                    goal_matches += 1

            if goals_set:
                goal_score = min(1.0, goal_matches / len(goals_set) + (0.3 if goal_matches > 0 else 0.0))
            else:
                goal_score = 0.5  # Neutral if user set no specific goals

            # 5. Beginner Friendly Label Score
            label_score = 1.0 if beginner_friendly else 0.1

            # 6. Semantic Similarity
            sem_score = semantic_scores[idx] if idx < len(semantic_scores) else 0.0

            # 7. Aggregate Weighted Score
            final_score = (
                norm_weights["skill_overlap"] * skill_overlap_ratio
                + norm_weights["experience_fit"] * exp_fit_score
                + norm_weights["learning_goals"] * goal_score
                + norm_weights["beginner_friendly_label"] * label_score
                + norm_weights["semantic_similarity"] * sem_score
            )
            # Ensure strictly bounded in [0.0, 1.0]
            final_score = max(0.0, min(1.0, final_score))

            # 8. Skill Gap Computation
            relevant_skills = [
                s for s in user_skills_clean if s.lower() in techs_set or s.lower() == primary_lang
            ]
            missing_skills = [
                t for t in techs if t.lower() not in user_skills_set and t.lower() != primary_lang
            ]

            # 9. Explainability & Next Steps
            match_reasons: List[str] = []
            if relevant_skills:
                match_reasons.append(
                    f"Direct overlap with your skills in {', '.join(relevant_skills)}."
                )
            if primary_lang and primary_lang in user_skills_set:
                match_reasons.append(
                    f"Aligns with your knowledge of repository primary language ({repo_metadata.get('language')})."
                )
            if exp_fit_score >= 0.8:
                match_reasons.append(
                    f"Difficulty '{difficulty}' is well suited for your '{experience_level}' experience level."
                )
            if beginner_friendly:
                match_reasons.append(
                    "Labeled with beginner-friendly community tags (e.g., 'good first issue')."
                )
            if goal_matches > 0:
                match_reasons.append(
                    f"Matches your target learning goals ({goal_matches} topic matches)."
                )
            if not match_reasons:
                match_reasons.append("General exploration candidate based on repository context.")

            # Preparation Checklist
            prep_steps = [
                f"Read the issue discussion and check any linked pull requests or comments (Issue #{issue.get('number')}).",
                "Review the repository CONTRIBUTING guide, code style conventions, and testing instructions.",
            ]
            if missing_skills:
                prep_steps.append(
                    f"Brush up on missing tool/framework fundamentals: {', '.join(missing_skills)}."
                )
            prep_steps.extend([
                "Fork the repository, clone locally, and run the test suite to ensure a clean baseline.",
                "Reproduce or locate the affected code paths before writing your patch.",
                "Keep your pull request focused and write unit tests covering your change.",
            ])

            ranked_list.append(
                RankedIssue(
                    number=issue.get("number", 0),
                    title=issue.get("title", "Untitled Issue"),
                    body=issue.get("body", ""),
                    html_url=issue.get("html_url", ""),
                    labels=issue.get("labels", []),
                    label_names=issue.get("label_names", []),
                    comments_count=issue.get("comments", 0),
                    created_at=issue.get("created_at", ""),
                    updated_at=issue.get("updated_at", ""),
                    author=issue.get("author", "unknown"),
                    repository_full_name=repo_metadata.get("full_name", ""),
                    difficulty=difficulty,
                    difficulty_confidence=classification["confidence"],
                    difficulty_evidence=diff_evidence,
                    estimated_effort=estimated_effort,
                    technologies_involved=techs,
                    beginner_friendly=beginner_friendly,
                    match_score=round(final_score, 4),
                    match_score_percent=int(round(final_score * 100)),
                    score_breakdown={
                        "skill_overlap": round(skill_overlap_ratio, 3),
                        "experience_fit": round(exp_fit_score, 3),
                        "learning_goals": round(goal_score, 3),
                        "beginner_friendly_label": round(label_score, 3),
                        "semantic_similarity": round(sem_score, 3),
                    },
                    relevant_user_skills=relevant_skills,
                    missing_skills=missing_skills,
                    match_reasons=match_reasons,
                    preparation_steps=prep_steps,
                )
            )

        # Sort descending by match score
        ranked_list.sort(key=lambda x: x.match_score, reverse=True)
        return ranked_list
