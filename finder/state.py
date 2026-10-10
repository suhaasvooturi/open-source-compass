"""Shared Streamlit session state management for OpenSource Compass."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import streamlit as st

from finder.demo_data import get_demo_repository
from finder.github_api import GitHubClient, parse_github_url
from finder.ranking import RankedIssue, RankingWeights, RecommendationEngine
from finder.repository_analyzer import RepositoryAnalyzer, normalize_skills_list
from finder.semantic_matcher import SemanticMatcher
from finder.shortlist import ShortlistManager


DEFAULT_SKILLS = [
    "Python",
    "JavaScript",
    "TypeScript",
    "React",
    "REST APIs",
    "SQL",
    "Docker",
    "Testing",
    "Machine Learning",
    "Git",
    "Documentation",
    "Debugging",
]


def init_session_state() -> None:
    """Initialize default session state keys."""
    if "shortlist_manager" not in st.session_state:
        st.session_state.shortlist_manager = ShortlistManager()

    if "user_skills" not in st.session_state:
        st.session_state.user_skills = ["Python", "Testing", "Git"]

    if "experience_level" not in st.session_state:
        st.session_state.experience_level = "Beginner"

    if "learning_goals" not in st.session_state:
        st.session_state.learning_goals = ["REST APIs", "Testing"]

    if "github_username" not in st.session_state:
        st.session_state.github_username = ""

    if "mode" not in st.session_state:
        st.session_state.mode = "Demo Mode (Offline)"

    if "selected_demo_repo" not in st.session_state:
        st.session_state.selected_demo_repo = "demo/fastapi-taskflow"

    if "repo_url" not in st.session_state:
        st.session_state.repo_url = "https://github.com/psf/requests"

    if "github_token" not in st.session_state:
        st.session_state.github_token = ""

    if "ranked_issues" not in st.session_state:
        st.session_state.ranked_issues = []

    if "repo_metadata" not in st.session_state:
        st.session_state.repo_metadata = None

    if "repo_analysis" not in st.session_state:
        st.session_state.repo_analysis = None

    if "repo_readme" not in st.session_state:
        st.session_state.repo_readme = None

    if "repo_contributing" not in st.session_state:
        st.session_state.repo_contributing = None

    if "last_analyzed_target" not in st.session_state:
        st.session_state.last_analyzed_target = ""


def load_demo_analysis(demo_key: str) -> None:
    """Load and process synthetic demo repository data."""
    demo_data = get_demo_repository(demo_key)
    metadata = demo_data["metadata"]
    root_files = demo_data.get("root_files", [])
    readme = demo_data.get("readme")
    contributing = demo_data.get("contributing")
    raw_issues = demo_data.get("issues", [])

    analyzer = RepositoryAnalyzer(metadata, root_files, readme, contributing)
    analysis = analyzer.analyze()

    engine = RecommendationEngine()
    ranked = engine.rank_issues(
        issues=raw_issues,
        user_skills=st.session_state.user_skills,
        experience_level=st.session_state.experience_level,
        learning_goals=st.session_state.learning_goals,
        repo_metadata=metadata,
        repo_analysis=analysis,
    )

    st.session_state.repo_metadata = metadata
    st.session_state.repo_analysis = analysis
    st.session_state.repo_readme = readme
    st.session_state.repo_contributing = contributing
    st.session_state.ranked_issues = ranked
    st.session_state.last_analyzed_target = demo_key
