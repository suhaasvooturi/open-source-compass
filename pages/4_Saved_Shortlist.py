"""Saved Shortlist: View, export, and manage candidate open-source issues."""

from __future__ import annotations

import streamlit as st

from finder.state import init_session_state
from finder.ui_components import inject_custom_styles, render_difficulty_badge, render_hero_banner

st.set_page_config(
    page_title="Saved Shortlist | OpenSource Compass",
    page_icon="⭐",
    layout="wide",
)

inject_custom_styles()
init_session_state()

shortlist_manager = st.session_state.shortlist_manager
saved_items = shortlist_manager.list_all()

render_hero_banner(
    title="Saved Shortlist",
    tagline="Your curated list of open-source contribution opportunities.",
)

with st.sidebar:
    st.page_link("app.py", label="← Back to Main Dashboard", icon="🏠")
    st.page_link("pages/1_Issue_Explorer.py", label="Issue Explorer", icon="🔎")
    st.page_link("pages/2_Repository_Analysis.py", label="Repository Analysis", icon="🏛️")
    st.page_link("pages/3_Skill_Gap_Analysis.py", label="Skill Gap Analysis", icon="📈")

if not saved_items:
    st.info("⭐ Your shortlist is currently empty. Explore issues on the Dashboard or Issue Explorer and click 'Save to Shortlist' to bookmark them!")
else:
    st.markdown(f"### You have `{len(saved_items)}` issues bookmarked")

    # Export toolbar
    col_exp_json, col_exp_csv, col_clear = st.columns([2, 2, 2])
    with col_exp_json:
        st.download_button(
            label="📥 Export Shortlist as JSON",
            data=shortlist_manager.to_json(),
            file_name="opensource_compass_shortlist.json",
            mime="application/json",
            use_container_width=True,
        )
    with col_exp_csv:
        st.download_button(
            label="📥 Export Shortlist as CSV",
            data=shortlist_manager.to_csv(),
            file_name="opensource_compass_shortlist.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_clear:
        if st.button("🗑️ Clear Entire Shortlist", use_container_width=True):
            shortlist_manager.clear()
            st.rerun()

    st.markdown("---")

    # Display items
    for item in saved_items:
        num = item["number"]
        col_content, col_actions = st.columns([5, 2])

        with col_content:
            diff_badge = render_difficulty_badge(item.get("difficulty", "Uncertain"))
            st.markdown(
                f"""
                <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 12px; padding: 18px 20px; margin-bottom: 12px;">
                    <div style="margin-bottom: 6px;">
                        {diff_badge}
                        <span style="font-weight: 700; color: #10B981; margin-left: 8px;">{item.get('match_score_percent', 0)}% Match</span>
                        <span style="color: #64748B; font-size: 0.85rem; margin-left: 8px;">• {item.get('repository', '')}</span>
                    </div>
                    <h4 style="margin: 0 0 6px 0; color: #F8FAFC;">
                        <a href="{item.get('html_url')}" target="_blank" style="color: #F8FAFC; text-decoration: none;">#{num}: {item.get('title')}</a>
                    </h4>
                    <p style="color: #94A3B8; font-size: 0.88rem; margin: 0;">⏱️ <b>Effort:</b> {item.get('estimated_effort', '')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_actions:
            st.link_button(f"🔗 Open on GitHub", item.get("html_url", "#"), use_container_width=True)
            if st.button("❌ Remove", key=f"remove_btn_{num}", use_container_width=True):
                shortlist_manager.remove(num)
                st.rerun()
