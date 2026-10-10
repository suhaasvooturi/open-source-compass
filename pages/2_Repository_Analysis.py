"""Repository Analysis: Architecture, frameworks, health indicators, and contribution instructions."""

from __future__ import annotations

import streamlit as st

from finder.contribution_guide import ContributionGuideReader
from finder.state import init_session_state, load_demo_analysis
from finder.ui_components import inject_custom_styles, render_hero_banner

st.set_page_config(
    page_title="Repository Analysis | OpenSource Compass",
    page_icon="🏛️",
    layout="wide",
)

inject_custom_styles()
init_session_state()

if not st.session_state.ranked_issues:
    load_demo_analysis(st.session_state.selected_demo_repo)

metadata = st.session_state.repo_metadata or {}
analysis = st.session_state.repo_analysis or {}
contributing_raw = st.session_state.repo_contributing
repo_url = metadata.get("html_url", "https://github.com")

render_hero_banner(
    title="Repository Architecture & Health",
    tagline=f"Deep architectural analysis and contribution guidelines for {metadata.get('full_name', 'repository')}",
)

with st.sidebar:
    st.page_link("app.py", label="← Back to Main Dashboard", icon="🏠")
    st.page_link("pages/1_Issue_Explorer.py", label="Issue Explorer", icon="🔎")
    st.page_link("pages/3_Skill_Gap_Analysis.py", label="Skill Gap Analysis", icon="📈")
    st.page_link("pages/4_Saved_Shortlist.py", label="Saved Shortlist", icon="⭐")

tab_arch, tab_health, tab_guide = st.tabs(["🏗️ Architecture & Stack", "🩺 Health Indicators", "📖 Contribution Guide Reader"])

# -------------------------------------------------------------
# TAB 1: Architecture & Stack
# -------------------------------------------------------------
with tab_arch:
    st.subheader("Detected Technologies & Frameworks")
    detected = analysis.get("detected_technologies", [])
    if detected:
        st.write("The following languages, libraries, and frameworks were identified from metadata, build files, and documentation:")
        badges_html = " ".join([f'<span class="badge badge-tech">{t}</span>' for t in detected])
        st.markdown(badges_html, unsafe_allow_html=True)
    else:
        st.info("No specific framework signatures could be detected from inspected files.")

    st.markdown("---")
    st.subheader("Build & Configuration Files")
    build_files = analysis.get("detected_build_files", [])
    if build_files:
        st.write(f"Identified **{len(build_files)}** build or environment configuration files:")
        for bf in build_files:
            st.markdown(f"- 📄 `{bf}`")
    else:
        st.info("No common build files (e.g. `pyproject.toml`, `package.json`, `Cargo.toml`) found in root.")

    st.markdown("---")
    st.subheader("Repository Scope & Inspection Limits")
    st.write(
        f"- **Files Inspected at Root:** `{analysis.get('inspected_files_count', 0)}`\n"
        f"- **README Status:** {'✅ Available' if analysis.get('readme_available') else '❌ Not detected'}\n"
        f"- **CONTRIBUTING Guide:** {'✅ Available' if analysis.get('contributing_available') else '❌ Not detected'}\n"
    )
    st.caption("Note: OpenSource Compass inspects public root files, issues, and metadata. It avoids making unwarranted claims about unretrieved directories.")

# -------------------------------------------------------------
# TAB 2: Health Indicators
# -------------------------------------------------------------
with tab_health:
    health = analysis.get("health", {})
    score = health.get("health_score", 0)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Health Score", f"{score}/100")
    with col2:
        st.metric("GitHub Stars", f"{metadata.get('stargazers_count', 0):,}")
    with col3:
        st.metric("Community Forks", f"{metadata.get('forks_count', 0):,}")

    st.markdown("### Health Signals Checklist")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"- {'✅' if health.get('has_readme') else '❌'} **Comprehensive README:** Explains project purpose and getting started.")
        st.markdown(f"- {'✅' if health.get('has_contributing') else '❌'} **Contribution Guide:** Dedicated CONTRIBUTING.md instructions.")
        st.markdown(f"- {'✅' if health.get('has_license') else '❌'} **Open-Source License:** `{metadata.get('license', 'Unspecified')}`.")
    with c2:
        st.markdown(f"- {'✅' if health.get('has_tests_indicator') else '❌'} **Automated Tests:** Test suite or config detected in repository.")
        st.markdown(f"- {'✅' if health.get('has_ci_indicator') else '❌'} **Continuous Integration:** CI workflow or configuration detected.")
        st.markdown(f"- {'✅' if not metadata.get('archived') else '⚠️'} **Active Maintenance:** Repository is {'not archived' if not metadata.get('archived') else 'archived'}.")

    missing = analysis.get("missing_artifacts", [])
    if missing:
        st.markdown("### ⚠️ Areas for Improvement")
        for m in missing:
            st.warning(m)

# -------------------------------------------------------------
# TAB 3: Contribution Guide Reader
# -------------------------------------------------------------
with tab_guide:
    guide_reader = ContributionGuideReader(
        raw_content=contributing_raw or st.session_state.repo_readme,
        repo_name=metadata.get("full_name", "Repository"),
        repo_url=repo_url,
    )
    guide_info = guide_reader.parse()

    st.markdown(f"**Guide Source:** [{guide_info['source_url']}]({guide_info['source_url']})")
    st.info(guide_info["message"])

    col_setup, col_test = st.columns(2)
    with col_setup:
        st.markdown("#### ⚙️ Setup & Installation Commands")
        if guide_info["setup_commands"]:
            for cmd in guide_info["setup_commands"]:
                st.code(cmd, language="bash")
        else:
            st.write("No automated setup commands explicitly extracted. Check the repository README.")

    with col_test:
        st.markdown("#### 🧪 Test & Lint Commands")
        if guide_info["test_commands"] or guide_info["lint_commands"]:
            for cmd in guide_info["test_commands"]:
                st.code(cmd, language="bash")
            for cmd in guide_info["lint_commands"]:
                st.code(cmd, language="bash")
        else:
            st.write("No explicit test execution commands detected.")

    st.markdown("#### 🚀 Pull Request Expectations")
    for req in guide_info["pr_guidelines"]:
        st.markdown(f"- {req}")

    if guide_info.get("raw_snippet"):
        with st.expander("📄 View Guide Raw Excerpt"):
            st.markdown(guide_info["raw_snippet"])
