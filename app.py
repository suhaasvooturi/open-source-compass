"""OpenSource Compass: AI-Assisted Open-Source Contribution Finder.

Tagline: Find your first issue. Make your first contribution.
Author: Suhaas Vooturi
Repository: https://github.com/suhaasvooturi/ai-open-source-contribution-finder
"""

from __future__ import annotations

import os
from typing import Any, Dict, List
import streamlit as st
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

from finder.demo_data import get_demo_repository, list_demo_repositories
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


def run_live_analysis(repo_url: str, token: str) -> None:
    """Fetch and analyze a live public GitHub repository."""
    if not repo_url or not repo_url.strip():
        st.error("❌ Please provide a repository name or URL.")
        return

    st.session_state.suggested_user_repos = []
    client = GitHubClient(token=token if token.strip() else None)

    try:
        owner, repo = parse_github_url(repo_url)
    except UserProfileURLError as e:
        st.warning(f"⚠️ {str(e)}")
        with st.spinner(f"🔍 Checking public repositories for user @{e.username}..."):
            user_repos = client.get_user_repositories(e.username)
            if user_repos:
                st.info(f"Found {len(user_repos)} public repositories for @{e.username}! Select one below:")
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
            f"💡 Format should be 'owner/repo' (e.g. 'tiangolo/fastapi', 'psf/requests', or 'suhaasvooturi/ai-open-source-contribution-finder')."
        )
        return

    with st.spinner(f"🔍 Connecting to GitHub API for {owner}/{repo}..."):
        try:
            metadata = client.get_repository(owner, repo)
        except RepositoryNotFoundError as e:
            st.error(f"❌ Repository Not Found: {str(e)}")
            return
        except RateLimitExceededError as e:
            st.error(f"⚠️ {str(e)}")
            st.info("💡 Switch to Demo Mode in the sidebar to explore full functionality without rate limits.")
            return
        except NetworkConnectionError as e:
            st.error(f"🌐 Network Error: {str(e)}")
            return
        except GitHubAPIError as e:
            st.error(f"❌ GitHub API Error: {str(e)}")
            return

    with st.spinner("📦 Retrieving issues, README, root tree, and contribution guidelines..."):
        issues = client.get_open_issues(owner, repo, max_count=50)
        readme = client.get_readme(owner, repo)
        contributing = client.get_contributing_guide(owner, repo)
        root_files = client.get_root_files(owner, repo)

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
        demo_choice = st.selectbox(
            "Select Demo Repository:",
            list_demo_repositories(),
            index=list_demo_repositories().index(st.session_state.selected_demo_repo)
            if st.session_state.selected_demo_repo in list_demo_repositories()
            else 0,
            format_func=lambda x: f"📦 {x.replace('demo/', '')}",
        )
        st.session_state.selected_demo_repo = demo_choice
        if st.button("🚀 Load Demo Issues", type="primary", use_container_width=True):
            load_demo_analysis(st.session_state.selected_demo_repo)
            st.rerun()
    else:
        st.session_state.repo_url = st.text_input(
            "GitHub Repository URL / Slug:",
            value=st.session_state.repo_url,
            placeholder="e.g. psf/requests, tiangolo/fastapi",
            help="Enter in owner/repo format (e.g. psf/requests or https://github.com/tiangolo/fastapi)",
        )

        col_side1, col_side2 = st.columns([3, 1])
        with col_side1:
            if st.button("🚀 Analyze", type="primary", key="btn_side_analyze_top", use_container_width=True):
                run_live_analysis(st.session_state.repo_url, st.session_state.github_token)
                st.rerun()
        with col_side2:
            if st.button("🧹 Clear", key="btn_side_clear", use_container_width=True):
                st.session_state.repo_url = ""
                st.session_state.ranked_issues = []
                st.session_state.suggested_user_repos = []
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
    st.session_state.experience_level = st.selectbox(
        "Experience Level:",
        exp_levels,
        index=cur_exp_idx,
        help="Beginner targets 'good first issue' and docs. Intermediate targets features & bugfixes. Advanced targets architecture & performance.",
    )

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

# Landing view if no issues are loaded yet
if not st.session_state.ranked_issues:
    if "Demo" in st.session_state.mode:
        load_demo_analysis(st.session_state.selected_demo_repo)
        st.rerun()
    else:
        st.markdown(
            """
            <div style="background: rgba(30, 41, 59, 0.65); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 16px; padding: 24px 28px; margin-bottom: 24px;">
                <h3 style="margin-top: 0; color: #F8FAFC;">🔍 Enter a Public GitHub Repository</h3>
                <p style="color: #94A3B8; font-size: 0.95rem; margin-bottom: 0;">
                    Type any public GitHub repository (e.g. <code>tiangolo/fastapi</code> or <code>psf/requests</code>) to analyze its architecture, classify open issues, and match them with your skills.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Center input box and button
        col_inp, col_btn = st.columns([4, 1])
        with col_inp:
            main_input_val = st.text_input(
                "Enter repository URL or slug:",
                value=st.session_state.repo_url,
                placeholder="e.g. psf/requests, tiangolo/fastapi, or pallets/flask",
                label_visibility="collapsed",
                key="main_repo_input",
            )
        with col_btn:
            if st.button("🚀 Analyze Repository", type="primary", key="main_analyze_btn", use_container_width=True):
                st.session_state.repo_url = main_input_val
                run_live_analysis(main_input_val, st.session_state.github_token)
                st.rerun()

        # Display discovered public repos if a user profile was entered
        if getattr(st.session_state, "suggested_user_repos", None):
            st.markdown("### 📦 Public Repositories Found:")
            for r in st.session_state.suggested_user_repos[:6]:
                col_r_info, col_r_btn = st.columns([4, 1])
                with col_r_info:
                    st.markdown(
                        f"**[{r['full_name']}](https://github.com/{r['full_name']})** (`{r['language']}`) — "
                        f"⭐ {r['stargazers_count']} | 🎫 {r['open_issues_count']} issues\n\n"
                        f"<small style='color: #94A3B8;'>{r['description']}</small>",
                        unsafe_allow_html=True,
                    )
                with col_r_btn:
                    if st.button(f"Analyze {r['name']}", key=f"btn_pick_{r['full_name']}", use_container_width=True):
                        st.session_state.repo_url = r["full_name"]
                        run_live_analysis(r["full_name"], st.session_state.github_token)
                        st.rerun()
            st.markdown("---")

        # Quick start popular repositories
        st.markdown("#### 💡 Quick-Start with Popular Beginner-Friendly Repositories:")
        col_q1, col_q2, col_q3, col_q4, col_q5 = st.columns(5)
        with col_q1:
            if st.button("🐍 psf/requests", use_container_width=True):
                st.session_state.repo_url = "psf/requests"
                run_live_analysis("psf/requests", st.session_state.github_token)
                st.rerun()
        with col_q2:
            if st.button("⚡ tiangolo/fastapi", use_container_width=True):
                st.session_state.repo_url = "tiangolo/fastapi"
                run_live_analysis("tiangolo/fastapi", st.session_state.github_token)
                st.rerun()
        with col_q3:
            if st.button("🌶️ pallets/flask", use_container_width=True):
                st.session_state.repo_url = "pallets/flask"
                run_live_analysis("pallets/flask", st.session_state.github_token)
                st.rerun()
        with col_q4:
            if st.button("⚛️ facebook/react", use_container_width=True):
                st.session_state.repo_url = "facebook/react"
                run_live_analysis("facebook/react", st.session_state.github_token)
                st.rerun()
        with col_q5:
            if st.button("🧭 Our Repository", use_container_width=True):
                st.session_state.repo_url = "suhaasvooturi/ai-open-source-contribution-finder"
                run_live_analysis("suhaasvooturi/ai-open-source-contribution-finder", st.session_state.github_token)
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 You can also switch to **'Offline Demo Mode'** in the sidebar at any time to explore synthetic issues without hitting GitHub API limits.")
        st.stop()


metadata = st.session_state.repo_metadata or {}
analysis = st.session_state.repo_analysis or {}
ranked_issues: List[RankedIssue] = st.session_state.ranked_issues

# Repository Summary Card
with st.container():
    st.markdown(
        f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 14px; padding: 20px 24px; margin-bottom: 24px;">
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

# Quick stats columns
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

# Search & Filters
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
        ["Match Score (Highest first)", "Estimated Effort (Lowest first)", "Most Discussed", "Recently Updated"],
    )

# Filter issues
filtered_issues = list(ranked_issues)

if search_query:
    q = search_query.lower()
    filtered_issues = [
        i for i in filtered_issues if q in i.title.lower() or q in i.body.lower() or any(q in t.lower() for t in i.technologies_involved)
    ]

if diff_filter != "All Difficulties":
    filtered_issues = [i for i in filtered_issues if i.difficulty.lower() == diff_filter.lower()]

# Sort issues
if sort_choice == "Match Score (Highest first)":
    filtered_issues.sort(key=lambda x: x.match_score, reverse=True)
elif sort_choice == "Estimated Effort (Lowest first)":
    order = {"Beginner": 1, "Difficulty uncertain": 2, "Intermediate": 3, "Advanced": 4}
    filtered_issues.sort(key=lambda x: order.get(x.difficulty, 5))
elif sort_choice == "Most Discussed":
    filtered_issues.sort(key=lambda x: x.comments_count, reverse=True)
elif sort_choice == "Recently Updated":
    filtered_issues.sort(key=lambda x: x.updated_at, reverse=True)

# Render Issue Cards
if not filtered_issues:
    st.info("No open issues match your current filters. Try relaxing the difficulty or search criteria.")
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
