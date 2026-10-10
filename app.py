"""OpenSource Compass: AI-Assisted Open-Source Contribution Finder.

Tagline: Find your first issue. Make your first contribution.
Author: Suhaas Vooturi
Repository: https://github.com/suhaasvooturi/open-source-compass
"""

from __future__ import annotations

import os
from typing import Any, Dict, List
import streamlit as st
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

from finder.demo_data import get_demo_repository, get_snapshot_for_repo, list_demo_repositories
from finder.explanation import LLMExplainer, TemplateExplainer
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
from finder.ranking import RankedIssue, RecommendationEngine
from finder.repository_analyzer import RepositoryAnalyzer, normalize_skill, normalize_skills_list
from finder.state import DEFAULT_SKILLS, init_session_state, load_demo_analysis
from finder.ui_components import (
    inject_custom_styles,
    render_hero_banner,
    render_issue_card,
    render_sidebar_nav,
)


# Page configuration
st.set_page_config(
    page_title="OpenSource Compass | Find Your First Issue",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom styles & initialize session state
inject_custom_styles()
init_session_state()

# Explainer engine instance
explainer = LLMExplainer()

# Common alias dictionary for instant resolution
POPULAR_ALIASES = {
    "fastapi": "tiangolo/fastapi",
    "requests": "psf/requests",
    "flask": "pallets/flask",
    "react": "facebook/react",
    "compass": "suhaasvooturi/open-source-compass",
    "open-source-compass": "suhaasvooturi/open-source-compass",
    "ai-open-source-contribution-finder": "suhaasvooturi/open-source-compass",
    "django": "django/django",
    "numpy": "numpy/numpy",
    "pandas": "pandas-dev/pandas",
}


def run_live_analysis(repo_input: str, token: str) -> None:
    """Fetch and analyze a live public GitHub repository or fallback gracefully to cached snapshot."""
    if not repo_input or not repo_input.strip():
        st.error("❌ Please provide a repository name or URL.")
        return

    cleaned_input = repo_input.strip()
    if cleaned_input.lower() in POPULAR_ALIASES:
        cleaned_input = POPULAR_ALIASES[cleaned_input.lower()]

    st.session_state.suggested_user_repos = []
    client = GitHubClient(token=token if token.strip() else None)

    try:
        owner, repo = parse_github_url(cleaned_input)
    except UserProfileURLError as e:
        st.warning(f"⚠️ {str(e)}")
        with st.spinner(f"🔍 Discovering public repositories for user @{e.username}..."):
            user_repos = client.get_user_repositories(e.username)
            if user_repos:
                st.info(f"Discovered **{len(user_repos)}** public repositories for @{e.username}! Click any repository below to analyze:")
                st.session_state.suggested_user_repos = user_repos
            else:
                st.error(
                    f"No public repositories found for user '@{e.username}'. "
                    f"Please enter in 'owner/repo' format (e.g. 'tiangolo/fastapi' or 'psf/requests')."
                )
        return
    except InvalidRepositoryURLError as e:
        st.error(
            f"❌ Invalid Repository URL: {str(e)}\n\n"
            f"💡 Format should be 'owner/repo' (e.g. 'tiangolo/fastapi', 'psf/requests', or 'suhaasvooturi/open-source-compass')."
        )
        return

    use_cached_snapshot = False

    with st.spinner(f"🔍 Connecting to GitHub for {owner}/{repo}..."):
        try:
            metadata = client.get_repository(owner, repo)
        except (RateLimitExceededError, NetworkConnectionError, GitHubAPIError) as e:
            snapshot = get_snapshot_for_repo(owner, repo)
            if snapshot:
                st.warning(
                    f"ℹ️ GitHub Live API Note: {str(e)}\n\n"
                    f"✨ Automatically loaded cached live snapshot for **{owner}/{repo}** so you can continue testing all features without interruption!"
                )
                use_cached_snapshot = True
                metadata = snapshot["metadata"]
                root_files = snapshot.get("root_files", [])
                readme = snapshot.get("readme")
                contributing = snapshot.get("contributing")
                issues = snapshot.get("issues", [])
            else:
                st.error(f"❌ GitHub API Error: {str(e)}")
                st.info("💡 You can explore popular pre-cached repositories below or switch to Offline Demo Mode in the sidebar.")
                return
        except RepositoryNotFoundError as e:
            snapshot = get_snapshot_for_repo(owner, repo)
            if snapshot:
                use_cached_snapshot = True
                metadata = snapshot["metadata"]
                root_files = snapshot.get("root_files", [])
                readme = snapshot.get("readme")
                contributing = snapshot.get("contributing")
                issues = snapshot.get("issues", [])
            else:
                st.error(f"❌ Repository Not Found: {str(e)}")
                return

    if not use_cached_snapshot:
        with st.spinner("📦 Retrieving issues, README, root tree, and contribution guidelines..."):
            try:
                issues = client.get_open_issues(owner, repo, max_count=50)
                readme = client.get_readme(owner, repo)
                contributing = client.get_contributing_guide(owner, repo)
                root_files = client.get_root_files(owner, repo)
            except (RateLimitExceededError, NetworkConnectionError) as e:
                snapshot = get_snapshot_for_repo(owner, repo)
                if snapshot:
                    st.warning(f"ℹ️ Live API rate limited while retrieving issues. Loaded cached snapshot for **{owner}/{repo}**.")
                    metadata = snapshot["metadata"]
                    root_files = snapshot.get("root_files", [])
                    readme = snapshot.get("readme")
                    contributing = snapshot.get("contributing")
                    issues = snapshot.get("issues", [])
                else:
                    st.error(f"⚠️ {str(e)}")
                    return

    with st.spinner("🧠 Performing architecture analysis and matching issues to your profile..."):
        analyzer = RepositoryAnalyzer(metadata, root_files, readme, contributing)
        analysis = analyzer.analyze()

        engine = RecommendationEngine()
        ranked = engine.rank_issues(
            issues=issues,
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
        st.session_state.last_analyzed_target = f"{owner}/{repo}"


# Ensure initial state has an active repository so user never lands on a blank empty screen
if not st.session_state.ranked_issues:
    load_demo_analysis(st.session_state.selected_demo_repo)


# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("### 🧭 OpenSource Compass")
    st.caption("AI-Assisted Contribution Finder")

    st.markdown("---")
    st.subheader("1. Data Source")
    mode = st.radio(
        "Mode:",
        ["Offline Demo Mode", "Live GitHub Repository"],
        index=0 if "Demo" in st.session_state.mode else 1,
        help="Demo mode allows testing offline with synthetic repositories without burning GitHub rate limits.",
    )
    st.session_state.mode = mode

    if "Demo" in mode:
        demo_options = list_demo_repositories()
        cur_demo_idx = demo_options.index(st.session_state.selected_demo_repo) if st.session_state.selected_demo_repo in demo_options else 0
        demo_choice = st.selectbox(
            "Select Demo / Snapshot Repository:",
            demo_options,
            index=cur_demo_idx,
            format_func=lambda x: f"📦 {x.replace('demo/', '')}",
        )
        if demo_choice != st.session_state.selected_demo_repo:
            st.session_state.selected_demo_repo = demo_choice
            load_demo_analysis(demo_choice)
            st.rerun()

        if st.button("🚀 Re-Load Demo Issues", type="primary", use_container_width=True):
            load_demo_analysis(st.session_state.selected_demo_repo)
            st.rerun()
    else:
        with st.form("sidebar_repo_form", clear_on_submit=False):
            side_url_val = st.text_input(
                "GitHub Repository URL / Slug:",
                value=st.session_state.repo_url,
                placeholder="e.g. psf/requests, tiangolo/fastapi",
                help="Enter in owner/repo format (e.g. psf/requests or https://github.com/tiangolo/fastapi)",
            )
            col_side1, col_side2 = st.columns([3, 1])
            with col_side1:
                side_btn_analyze = st.form_submit_button("🚀 Analyze", type="primary", use_container_width=True)
            with col_side2:
                side_btn_clear = st.form_submit_button("🧹 Clear", use_container_width=True)

        if side_btn_analyze:
            st.session_state.repo_url = side_url_val
            run_live_analysis(side_url_val, st.session_state.github_token)
            st.rerun()
        if side_btn_clear:
            st.session_state.repo_url = ""
            st.session_state.suggested_user_repos = []
            load_demo_analysis("demo/fastapi-taskflow")
            st.rerun()

        with st.expander("🔑 GitHub Token (Optional)", expanded=False):
            st.session_state.github_token = st.text_input(
                "Personal Access Token:",
                value=st.session_state.github_token,
                type="password",
                help="Optional. Increases GitHub rate limit from 60 to 5,000 requests/hr. No write permissions required.",
            )

    st.markdown("---")
    st.subheader("2. Developer Profile")
    st.session_state.github_username = st.text_input(
        "GitHub Username (Optional):",
        value=st.session_state.github_username,
        placeholder="e.g. suhaasvooturi",
        help="Read-only context. We will never ask for your password.",
    )

    # Experience level
    exp_levels = ["Beginner", "Intermediate", "Advanced"]
    cur_exp_idx = exp_levels.index(st.session_state.experience_level) if st.session_state.experience_level in exp_levels else 0
    new_exp = st.selectbox(
        "Experience Level:",
        exp_levels,
        index=cur_exp_idx,
        help="Beginner targets 'good first issue' and docs. Intermediate targets features & bugfixes. Advanced targets architecture & performance.",
    )
    if new_exp != st.session_state.experience_level:
        st.session_state.experience_level = new_exp

    # Current Skills
    selected_skills = st.multiselect(
        "Current Skills & Tools:",
        options=sorted(list(set(DEFAULT_SKILLS + st.session_state.user_skills))),
        default=st.session_state.user_skills,
    )
    custom_skill = st.text_input("Add custom skill (press Enter):", placeholder="e.g. FastAPI, GraphQL")
    if custom_skill:
        canon = normalize_skill(custom_skill)
        if canon not in selected_skills:
            selected_skills.append(canon)
    st.session_state.user_skills = normalize_skills_list(selected_skills)

    # Learning Goals
    goals = st.multiselect(
        "Target Learning Goals:",
        options=sorted(list(set(DEFAULT_SKILLS + st.session_state.learning_goals))),
        default=st.session_state.learning_goals,
        help="What technologies or topics do you want to practice in this contribution?",
    )
    st.session_state.learning_goals = normalize_skills_list(goals)

    # Primary Trigger
    st.markdown("---")
    if st.button("🚀 Re-Rank with Profile", key="btn_side_bottom", use_container_width=True):
        if "Demo" in st.session_state.mode:
            load_demo_analysis(st.session_state.selected_demo_repo)
            st.rerun()
        else:
            run_live_analysis(st.session_state.repo_url, st.session_state.github_token)
            st.rerun()

    render_sidebar_nav()


# ==========================================
# MAIN DASHBOARD CONTENT
# ==========================================
render_hero_banner()

# Prominent Center Search and Discovery Form
with st.container():
    with st.form("hero_search_bar_form", clear_on_submit=False):
        col_inp, col_btn = st.columns([5, 1])
        with col_inp:
            hero_search_val = st.text_input(
                "Search & Analyze Any GitHub Repository:",
                value=st.session_state.repo_url,
                placeholder="Enter repository (e.g. psf/requests, tiangolo/fastapi, pallets/flask) or paste GitHub URL...",
                label_visibility="collapsed",
            )
        with col_btn:
            hero_btn_submit = st.form_submit_button("🚀 Analyze", type="primary", use_container_width=True)

    if hero_btn_submit:
        st.session_state.repo_url = hero_search_val
        st.session_state.mode = "Live GitHub Repository"
        run_live_analysis(hero_search_val, st.session_state.github_token)
        st.rerun()

# Quick-Start repository chips
st.markdown("##### ⚡ Quick-Start Repositories:")
col_q1, col_q2, col_q3, col_q4, col_q5 = st.columns(5)
with col_q1:
    if st.button("🐍 psf/requests", use_container_width=True):
        st.session_state.repo_url = "psf/requests"
        st.session_state.mode = "Live GitHub Repository"
        run_live_analysis("psf/requests", st.session_state.github_token)
        st.rerun()
with col_q2:
    if st.button("⚡ tiangolo/fastapi", use_container_width=True):
        st.session_state.repo_url = "tiangolo/fastapi"
        st.session_state.mode = "Live GitHub Repository"
        run_live_analysis("tiangolo/fastapi", st.session_state.github_token)
        st.rerun()
with col_q3:
    if st.button("🌶️ pallets/flask", use_container_width=True):
        st.session_state.repo_url = "pallets/flask"
        st.session_state.mode = "Live GitHub Repository"
        run_live_analysis("pallets/flask", st.session_state.github_token)
        st.rerun()
with col_q4:
    if st.button("🧭 OpenSource Compass", use_container_width=True):
        st.session_state.repo_url = "suhaasvooturi/open-source-compass"
        st.session_state.mode = "Live GitHub Repository"
        run_live_analysis("suhaasvooturi/open-source-compass", st.session_state.github_token)
        st.rerun()
with col_q5:
    if st.button("📦 FastAPI TaskFlow (Demo)", use_container_width=True):
        st.session_state.selected_demo_repo = "demo/fastapi-taskflow"
        st.session_state.mode = "Offline Demo Mode"
        load_demo_analysis("demo/fastapi-taskflow")
        st.rerun()

# Display discovered user repositories if a username profile was searched
if getattr(st.session_state, "suggested_user_repos", None):
    st.markdown("### 📦 Public Repositories Found:")
    cols_user_repos = st.columns(2)
    for idx, r in enumerate(st.session_state.suggested_user_repos[:6]):
        col_card = cols_user_repos[idx % 2]
        with col_card:
            st.markdown(
                f"""
                <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 12px; padding: 16px; margin-bottom: 12px;">
                    <div style="font-weight: 700; font-size: 1.05rem; color: #F1F5F9;">{r['name']} <span style="font-size: 0.85rem; color: #60A5FA;">({r.get('language') or 'General'})</span></div>
                    <div style="color: #94A3B8; font-size: 0.85rem; margin: 4px 0 8px 0;">{r.get('description') or 'No description provided.'}</div>
                    <div style="font-size: 0.82rem; color: #CBD5E1;">⭐ {r.get('stargazers_count', 0)} stars • 🎫 {r.get('open_issues_count', 0)} open issues</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"🚀 Analyze {r['name']}", key=f"btn_analyze_user_{r['full_name']}", use_container_width=True):
                st.session_state.repo_url = r["full_name"]
                st.session_state.mode = "Live GitHub Repository"
                st.session_state.suggested_user_repos = []
                run_live_analysis(r["full_name"], st.session_state.github_token)
                st.rerun()
    st.markdown("---")

metadata = st.session_state.repo_metadata or {}
analysis = st.session_state.repo_analysis or {}
ranked_issues: List[RankedIssue] = st.session_state.ranked_issues

# Repository Summary Header Card
with st.container():
    st.markdown(
        f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 14px; padding: 20px 24px; margin-top: 16px; margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px;">
                <h2 style="margin: 0; color: #F8FAFC;">📦 {metadata.get('full_name', 'Repository')}</h2>
                <span style="color: #60A5FA; font-weight: 600; font-size: 0.95rem;">Primary Language: <b>{metadata.get('language', 'Unknown')}</b></span>
            </div>
            <p style="color: #94A3B8; margin-top: 8px; margin-bottom: 12px; font-size: 0.95rem;">{metadata.get('description', '')}</p>
            <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 4px;">
                {' '.join([f'<span class="badge badge-tech">{t}</span>' for t in analysis.get('detected_technologies', [])[:8]])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Quick stats metrics
col1, col2, col3, col4 = st.columns(4)
health_score = (analysis.get("health") or {}).get("health_score", 70)
beginner_count = sum(1 for i in ranked_issues if i.beginner_friendly or i.difficulty == "Beginner")
top_score = ranked_issues[0].match_score_percent if ranked_issues else 0

with col1:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">Issues Analyzed</div>
            <div class="stat-val">{len(ranked_issues)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">Top Match Score</div>
            <div class="stat-val" style="color: #10B981;">{top_score}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">Beginner Friendly</div>
            <div class="stat-val" style="color: #38BDF8;">{beginner_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">Repo Health Rating</div>
            <div class="stat-val" style="color: #A78BFA;">{health_score}/100</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Missing artifacts notice if any
missing = analysis.get("missing_artifacts", [])
if missing:
    with st.expander("ℹ️ Repository Artifact Notice", expanded=False):
        for m in missing:
            st.markdown(f"- ⚠️ {m}")

# Search & Filters Toolbar
st.subheader("🎯 Recommended Issues for You")
col_search, col_diff, col_sort = st.columns([4, 3, 3])

with col_search:
    search_query = st.text_input("🔍 Search issues:", placeholder="Keywords in title or description...")

with col_diff:
    diff_filter = st.selectbox(
        "Filter by Difficulty:",
        ["All Difficulties", "Beginner", "Intermediate", "Advanced", "Difficulty uncertain"],
    )

with col_sort:
    sort_choice = st.selectbox(
        "Sort Issues by:",
        ["Match Score (Highest first)", "Fewest Comments (Unclaimed first)", "Estimated Effort (Lowest first)", "Most Discussed", "Recently Updated"],
    )

col_min_score, col_save_all = st.columns([3, 1])
with col_min_score:
    min_score = st.slider("Minimum Match Score Filter:", min_value=0, max_value=100, value=0, format="%d%%")
with col_save_all:
    st.write("")
    st.write("")
    if st.button("⭐ Shortlist All Visible", use_container_width=True):
        count_saved = 0
        for item in ranked_issues:
            if st.session_state.shortlist_manager.add(item):
                count_saved += 1
        st.toast(f"Bookmarked {count_saved} visible issues to your shortlist! ⭐")
        st.rerun()

# Apply Filters
filtered_issues = list(ranked_issues)

if search_query:
    q = search_query.lower()
    filtered_issues = [
        i for i in filtered_issues if q in i.title.lower() or q in i.body.lower() or any(q in t.lower() for t in i.technologies_involved)
    ]

if diff_filter != "All Difficulties":
    filtered_issues = [i for i in filtered_issues if i.difficulty.lower() == diff_filter.lower()]

if min_score > 0:
    filtered_issues = [i for i in filtered_issues if i.match_score_percent >= min_score]

# Sort issues
if sort_choice == "Match Score (Highest first)":
    filtered_issues.sort(key=lambda x: x.match_score, reverse=True)
elif sort_choice == "Fewest Comments (Unclaimed first)":
    filtered_issues.sort(key=lambda x: x.comments_count)
elif sort_choice == "Estimated Effort (Lowest first)":
    order = {"Beginner": 1, "Difficulty uncertain": 2, "Intermediate": 3, "Advanced": 4}
    filtered_issues.sort(key=lambda x: order.get(x.difficulty, 5))
elif sort_choice == "Most Discussed":
    filtered_issues.sort(key=lambda x: x.comments_count, reverse=True)
elif sort_choice == "Recently Updated":
    filtered_issues.sort(key=lambda x: x.updated_at, reverse=True)

# Render Issue Cards
if not filtered_issues:
    st.info("No open issues match your current filters. Try relaxing the difficulty or score slider.")
else:
    st.caption(f"Displaying **{len(filtered_issues)}** issues matching your criteria:")

    def handle_save_shortlist(iss: RankedIssue):
        added = st.session_state.shortlist_manager.add(iss)
        if added:
            st.toast(f"Saved Issue #{iss.number} to shortlist! ⭐")
        else:
            st.toast(f"Issue #{iss.number} is already in your shortlist.")

    def explain_issue(iss: RankedIssue) -> Dict[str, Any]:
        return explainer.explain(
            issue_title=iss.title,
            issue_body=iss.body,
            issue_number=iss.number,
            difficulty=iss.difficulty,
            technologies=iss.technologies_involved,
            relevant_skills=iss.relevant_user_skills,
            missing_skills=iss.missing_skills,
            repo_name=metadata.get("full_name", ""),
            repo_language=metadata.get("language", ""),
        )

    for iss in filtered_issues:
        saved_status = st.session_state.shortlist_manager.is_saved(iss.number)
        render_issue_card(
            iss,
            is_saved=saved_status,
            on_save_clicked=handle_save_shortlist,
            explainer_func=explain_issue,
        )
