"""Tests for recommendation engine, weight normalization, and scoring bounds."""

from finder.ranking import RankingWeights, RecommendationEngine


def test_ranking_weights_normalization():
    """Verify that configurable weights normalize to sum exactly to 1.0."""
    w = RankingWeights(
        skill_overlap=3.0,
        experience_fit=2.5,
        learning_goals=2.0,
        beginner_friendly_label=1.5,
        semantic_similarity=1.0,
    )
    norm = w.normalize()
    total = sum(norm.values())
    assert abs(total - 1.0) < 1e-3

    # Edge case: zero total defaults safely
    w_zero = RankingWeights(0, 0, 0, 0, 0)
    norm_zero = w_zero.normalize()
    assert abs(sum(norm_zero.values()) - 1.0) < 1e-3


def test_recommendation_ranking_and_bounds():
    """Verify recommendation ranking consistency, skill gap isolation, and score bounds."""
    issues = [
        {
            "number": 1,
            "title": "Fix typo in tutorial documentation",
            "body": "Spelling mistake in docs.",
            "label_names": ["good first issue", "documentation"],
            "html_url": "https://github.com/foo/bar/issues/1",
        },
        {
            "number": 2,
            "title": "Resolve distributed consensus race condition",
            "body": "Complex memory leak in raft consensus protocol.",
            "label_names": ["complex", "architecture"],
            "html_url": "https://github.com/foo/bar/issues/2",
        },
        {
            "number": 3,
            "title": "Add validation and pytest tests for REST API endpoint",
            "body": "Validate parameters in FastAPI and write unit tests.",
            "label_names": ["enhancement"],
            "html_url": "https://github.com/foo/bar/issues/3",
        },
    ]

    engine = RecommendationEngine()
    ranked = engine.rank_issues(
        issues=issues,
        user_skills=["Python", "Testing", "Documentation"],
        experience_level="Beginner",
        learning_goals=["Testing", "REST APIs"],
        repo_metadata={"name": "bar", "language": "Python", "full_name": "foo/bar"},
        repo_analysis={"primary_language": "Python"},
    )

    assert len(ranked) == 3

    # All match scores must be strictly bounded between 0.0 and 1.0
    for r in ranked:
        assert 0.0 <= r.match_score <= 1.0
        assert 0 <= r.match_score_percent <= 100
        assert len(r.preparation_steps) > 0
        assert len(r.match_reasons) > 0

    # For a Beginner user with skills in Docs and Testing, Issue #1 or #3 should outrank the advanced issue #2
    top_issue = ranked[0]
    assert top_issue.number in (1, 3)
    assert ranked[-1].number == 2  # Advanced race condition issue is at bottom for beginner

    # Verify skill gap computation on issue #3 (requires REST APIs or FastAPI if detected)
    for r in ranked:
        if r.number == 3:
            assert "Testing" in r.relevant_user_skills or "Python" in r.relevant_user_skills
