"""Issue Explorer: Interactive search, filtering, and detailed inspection of open issues."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from finder.ranking import RankedIssue
from finder.state import init_session_state, load_demo_analysis
from finder.ui_components import (
    inject_custom_styles,
    render_difficulty_badge,
    render_hero_banner,
    render_issue_card,
    render_score_pill,
)

st.set_page_config(
    page_title="Issue Explorer | OpenSource Compass",
    page_icon="🔎",
    layout="wide",
)

inject_custom_styles()
init_session_state()

# Ensure data exists
if not st.session_state.ranked_issues:
    load_demo_analysis(st.session_state.selected_demo_repo)

ranked_issues = st.session_state.ranked_issues
metadata = st.session_state.repo_metadata or {}

render_hero_banner(
    title="Issue Explorer",
    tagline=f"Deep search and filtering across open issues in {metadata.get('full_name', 'repository')}",
)

# Sidebar navigation link
with st.sidebar:
    st.page_link("app.py", label="← Back to Main Dashboard", icon="🏠")
    st.markdown("---")
    st.subheader("Explorer Filters")

    # Search keyword
    search_term = st.text_input("🔍 Search title or text:", "")

    # Difficulty filter
    diff_options = ["All", "Beginner", "Intermediate", "Advanced", "Difficulty uncertain"]
    selected_diff = st.selectbox("Difficulty Estimate:", diff_options)

    # Technology filter
    all_techs = sorted(list({t for i in ranked_issues for t in i.technologies_involved}))
    selected_techs = st.multiselect("Technologies Involved:", all_techs)

    # Labels filter
    all_labels = sorted(list({lbl for i in ranked_issues for lbl in i.label_names}))
    selected_labels = st.multiselect("Issue Labels:", all_labels)

    # Beginner friendly only checkbox
    only_beginner = st.checkbox("Show only 'Good First Issues' / Beginner", value=False)

    # View Mode toggle
    view_mode = st.radio("Display View:", ["Card Cards View", "Structured Table View"])

# Apply filters
filtered = list(ranked_issues)

if search_term:
    q = search_term.lower()
    filtered = [
        i for i in filtered
        if q in i.title.lower() or q in i.body.lower() or any(q in t.lower() for t in i.technologies_involved)
    ]

if selected_diff != "All":
    filtered = [i for i in filtered if i.difficulty.lower() == selected_diff.lower()]

if selected_techs:
    filtered = [i for i in filtered if any(t in i.technologies_involved for t in selected_techs)]

if selected_labels:
    filtered = [i for i in filtered if any(lbl in i.label_names for lbl in selected_labels)]

if only_beginner:
    filtered = [i for i in filtered if i.beginner_friendly or i.difficulty == "Beginner"]

st.markdown(f"### Results ({len(filtered)} matching issues)")

if not filtered:
    st.warning("No issues found matching the selected filters. Please broaden your criteria.")
elif view_mode == "Structured Table View":
    # Prepare DataFrame
    table_data = []
    for i in filtered:
        table_data.append(
            {
                "Issue #": i.number,
                "Title": i.title,
                "Difficulty": i.difficulty,
                "Match Score": f"{i.match_score_percent}%",
                "Estimated Effort": i.estimated_effort.split("(")[0].strip(),
                "Technologies": ", ".join(i.technologies_involved) or "General",
                "Comments": i.comments_count,
                "URL": i.html_url,
            }
        )
    df = pd.DataFrame(table_data)
    st.dataframe(
        df,
        column_config={
            "URL": st.column_config.LinkColumn("GitHub Link"),
            "Match Score": st.column_config.ProgressColumn(
                "Match Score",
                min_value=0,
                max_value=100,
                format="%d%%",
            ),
        },
        use_container_width=True,
        hide_index=True,
    )
else:
    def handle_save_shortlist(iss: RankedIssue):
        added = st.session_state.shortlist_manager.add(iss)
        if added:
            st.toast(f"Saved Issue #{iss.number} to shortlist! ⭐")
        else:
            st.toast(f"Issue #{iss.number} already saved.")

    for iss in filtered:
        saved_status = st.session_state.shortlist_manager.is_saved(iss.number)
        render_issue_card(
            iss,
            is_saved=saved_status,
            on_save_clicked=handle_save_shortlist,
        )
