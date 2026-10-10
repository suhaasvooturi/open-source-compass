"""Skill Gap Analysis: Identifies required skills vs developer profile and builds learning checklists."""

from __future__ import annotations

import streamlit as st

from finder.ranking import RankedIssue
from finder.state import init_session_state, load_demo_analysis
from finder.ui_components import inject_custom_styles, render_hero_banner, render_sidebar_nav

st.set_page_config(
    page_title="Skill Gap Analysis | OpenSource Compass",
    page_icon="📈",
    layout="wide",
)

inject_custom_styles()
init_session_state()

if not st.session_state.ranked_issues:
    load_demo_analysis(st.session_state.selected_demo_repo)

ranked_issues = st.session_state.ranked_issues
metadata = st.session_state.repo_metadata or {}
user_skills = set(s.lower() for s in st.session_state.user_skills)

render_hero_banner(
    title="Skill Gap & Learning Pathways",
    tagline="Identify what skills you already have, where the gaps lie, and actionable preparation steps.",
)

with st.sidebar:
    render_sidebar_nav()


# Summary of Developer Profile
col_prof1, col_prof2 = st.columns(2)
with col_prof1:
    st.markdown("### 👤 Your Current Profile")
    st.write(f"- **Experience Level:** `{st.session_state.experience_level}`")
    st.write(f"- **Documented Skills:** {', '.join(st.session_state.user_skills) or 'None listed'}")
with col_prof2:
    st.markdown("### 🎯 Your Learning Goals")
    st.write(f"- **Goals:** {', '.join(st.session_state.learning_goals) or 'None set'}")
    st.write(f"- **Target Repository:** `{metadata.get('full_name', 'Unknown')}`")

st.markdown("---")

# Aggregate all missing technologies across analyzed issues
missing_freq = {}
for iss in ranked_issues:
    for m in iss.missing_skills:
        missing_freq[m] = missing_freq.get(m, 0) + 1

st.subheader("📊 Skill Gaps Across This Repository's Open Issues")

DOC_LINKS = {
    "python": "https://docs.python.org/3/",
    "fastapi": "https://fastapi.tiangolo.com/",
    "react": "https://react.dev/",
    "typescript": "https://www.typescriptlang.org/docs/",
    "javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
    "docker": "https://docs.docker.com/",
    "pytest": "https://docs.pytest.org/",
    "postgresql": "https://www.postgresql.org/docs/",
    "sql": "https://www.w3schools.com/sql/",
    "rest apis": "https://restfulapi.net/",
    "git": "https://git-scm.com/doc",
    "machine learning": "https://scikit-learn.org/stable/",
    "flask": "https://flask.palletsprojects.com/",
    "pydantic": "https://docs.pydantic.dev/",
    "redis": "https://redis.io/docs/",
}

if not missing_freq:
    st.success("🎉 Outstanding! Your documented skills cover all detected technologies required across the open issues in this repository!")
else:
    st.write("These technologies appear in open issues but are currently not listed in your skills profile. Click to add them to your profile:")

    cols = st.columns(min(4, len(missing_freq)))
    for idx, (tech, count) in enumerate(sorted(missing_freq.items(), key=lambda x: x[1], reverse=True)):
        col = cols[idx % len(cols)]
        with col:
            st.metric(label=f"Learn {tech}", value=f"{count} Issues", delta=f"{int(count/len(ranked_issues)*100)}% of repo")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button(f"➕ Add", key=f"btn_add_skill_{tech}", help=f"Add {tech} to your developer profile", use_container_width=True):
                    if tech not in st.session_state.user_skills:
                        st.session_state.user_skills.append(tech)
                        st.toast(f"Added {tech} to your profile! Recalculating match scores... ✨")
                        st.rerun()
            with col_b2:
                doc_url = DOC_LINKS.get(tech.lower(), f"https://www.google.com/search?q={tech}+documentation")
                st.link_button("📚 Docs", doc_url, use_container_width=True)

st.markdown("---")
st.subheader("📋 Issue-Specific Skill Gap Explorer")

issue_options = {f"#{i.number}: {i.title}": i for i in ranked_issues}
selected_issue_title = st.selectbox("Select an issue to inspect skill alignment:", list(issue_options.keys()))
issue: RankedIssue = issue_options[selected_issue_title]

col_have, col_need = st.columns(2)
with col_have:
    st.markdown("#### ✅ Skills You Already Bring:")
    if issue.relevant_user_skills:
        for s in issue.relevant_user_skills:
            st.markdown(f"- **{s}**: Direct match for this issue's requirements.")
    else:
        st.write("No direct technology keyword overlap. General problem-solving and programming basics apply.")

with col_need:
    st.markdown("#### 🚀 Skills You Will Learn / Practice:")
    if issue.missing_skills:
        for m in issue.missing_skills:
            st.markdown(f"- **{m}**: Recommended to review before contributing.")
            if st.button(f"➕ Add '{m}' to My Profile", key=f"btn_add_specific_{issue.number}_{m}"):
                if m not in st.session_state.user_skills:
                    st.session_state.user_skills.append(m)
                    st.toast(f"Added {m} to your profile! ⭐")
                    st.rerun()
    else:
        st.write("You already have all detected technologies required for this issue!")

st.markdown("#### 🛠️ Interactive Preparation Checklist:")
checklist_md = f"### Preparation Checklist for Issue #{issue.number} ({issue.title})\n\n"
for idx, step in enumerate(issue.preparation_steps):
    st.checkbox(step, key=f"prep_check_{issue.number}_{idx}")
    checklist_md += f"- [ ] {step}\n"

with st.expander("📄 Export Checklist as Markdown"):
    st.code(checklist_md, language="markdown")

