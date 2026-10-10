"""UI component helpers, custom styling, badge renderers, and card designs for OpenSource Compass."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import streamlit as st

from finder.ranking import RankedIssue


def inject_custom_styles() -> None:
    """Inject modern, responsive, dark/light-friendly CSS styles."""
    st.markdown(
        """
        <style>
        /* Base typography and layout */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Hero Header */
        .hero-container {
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.12) 0%, rgba(99, 102, 241, 0.08) 50%, rgba(168, 85, 247, 0.05) 100%);
            border: 1px solid rgba(59, 130, 246, 0.25);
            border-radius: 16px;
            padding: 24px 28px;
            margin-bottom: 24px;
            backdrop-filter: blur(8px);
        }
        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #60A5FA 0%, #A78BFA 50%, #F472B6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }
        .hero-tagline {
            font-size: 1.05rem;
            color: #94A3B8;
            font-weight: 500;
            margin-bottom: 0px;
        }

        /* Metric & Stat Cards */
        .stat-card {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 12px;
            padding: 16px 20px;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .stat-card:hover {
            border-color: rgba(96, 165, 250, 0.4);
            transform: translateY(-2px);
        }
        .stat-label {
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94A3B8;
            margin-bottom: 4px;
        }
        .stat-val {
            font-size: 1.6rem;
            font-weight: 700;
            color: #F8FAFC;
        }

        /* Badges */
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-right: 6px;
            margin-bottom: 6px;
        }
        .badge-beginner {
            background-color: rgba(16, 185, 129, 0.18);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.35);
        }
        .badge-intermediate {
            background-color: rgba(245, 158, 11, 0.18);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.35);
        }
        .badge-advanced {
            background-color: rgba(239, 68, 68, 0.18);
            color: #F87171;
            border: 1px solid rgba(239, 68, 68, 0.35);
        }
        .badge-uncertain {
            background-color: rgba(148, 163, 184, 0.18);
            color: #CBD5E1;
            border: 1px solid rgba(148, 163, 184, 0.35);
        }
        .badge-tech {
            background-color: rgba(59, 130, 246, 0.14);
            color: #93C5FD;
            border: 1px solid rgba(59, 130, 246, 0.28);
        }
        .badge-missing {
            background-color: rgba(244, 63, 94, 0.12);
            color: #FDA4AF;
            border: 1px dashed rgba(244, 63, 94, 0.4);
        }

        /* Match Score Gauge */
        .score-pill {
            font-size: 1.1rem;
            font-weight: 800;
            padding: 6px 14px;
            border-radius: 12px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .score-high {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.2));
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }
        .score-med {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.2));
            color: #F59E0B;
            border: 1px solid rgba(245, 158, 11, 0.4);
        }
        .score-low {
            background: linear-gradient(135deg, rgba(148, 163, 184, 0.15), rgba(100, 116, 139, 0.15));
            color: #94A3B8;
            border: 1px solid rgba(148, 163, 184, 0.3);
        }

        /* Issue Card */
        .issue-card {
            background: rgba(30, 41, 59, 0.85);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 16px;
            padding: 22px 24px;
            margin-bottom: 20px;
            transition: all 0.25s ease;
        }
        .issue-card:hover {
            border-color: rgba(96, 165, 250, 0.5);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.2);
            transform: translateY(-2px);
        }
        .issue-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #F1F5F9;
            margin-bottom: 8px;
            line-height: 1.4;
        }
        .issue-title a {
            color: #F1F5F9;
            text-decoration: none;
        }
        .issue-title a:hover {
            color: #60A5FA;
            text-decoration: underline;
        }
        .issue-meta {
            font-size: 0.85rem;
            color: #94A3B8;
            margin-bottom: 14px;
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
        }
        .section-heading {
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94A3B8;
            margin-top: 12px;
            margin-bottom: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero_banner(title: str = "OpenSource Compass", tagline: str = "Find your first issue. Make your first contribution.") -> None:
    """Render the top hero banner."""
    st.markdown(
        f"""
        <div class="hero-container">
            <div class="hero-title">🧭 {title}</div>
            <div class="hero-tagline">{tagline}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_difficulty_badge(difficulty: str) -> str:
    """Return HTML string for difficulty badge."""
    d_clean = difficulty.strip().lower()
    if "beginner" in d_clean:
        cls = "badge-beginner"
    elif "intermediate" in d_clean:
        cls = "badge-intermediate"
    elif "advanced" in d_clean:
        cls = "badge-advanced"
    else:
        cls = "badge-uncertain"
    return f'<span class="badge {cls}">{difficulty}</span>'


def render_score_pill(score_percent: int) -> str:
    """Return HTML string for match score gauge pill."""
    if score_percent >= 75:
        cls = "score-high"
        emoji = "✨"
    elif score_percent >= 50:
        cls = "score-med"
        emoji = "⚡"
    else:
        cls = "score-low"
        emoji = "🎯"
    return f'<div class="score-pill {cls}">{emoji} {score_percent}% Match</div>'


def render_issue_card(
    issue: RankedIssue,
    is_saved: bool = False,
    on_save_clicked: Optional[Any] = None,
    explainer_func: Optional[Any] = None,
) -> None:
    """Render a comprehensive, responsive issue card."""
    diff_badge = render_difficulty_badge(issue.difficulty)
    score_pill = render_score_pill(issue.match_score_percent)

    tech_badges = "".join([f'<span class="badge badge-tech">{t}</span>' for t in issue.technologies_involved])
    if not tech_badges:
        tech_badges = '<span class="badge badge-uncertain">General</span>'

    missing_badges = "".join([f'<span class="badge badge-missing">+ Learn {m}</span>' for m in issue.missing_skills])

    card_html = f"""
    <div class="issue-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; gap: 12px; flex-wrap: wrap;">
            <div>
                {diff_badge}
                <span style="color: #64748B; font-size: 0.85rem; font-weight: 600;">Issue #{issue.number}</span>
                <span style="color: #64748B; font-size: 0.85rem; margin-left: 8px;">• {issue.repository_full_name}</span>
            </div>
            <div>
                {score_pill}
            </div>
        </div>
        <div class="issue-title">
            <a href="{issue.html_url}" target="_blank" rel="noopener noreferrer">#{issue.number}: {issue.title}</a>
        </div>
        <div class="issue-meta">
            <span>⏱️ <b>Estimated Effort:</b> {issue.estimated_effort}</span>
            <span>💬 <b>Comments:</b> {issue.comments_count}</span>
            <span>👤 <b>Author:</b> @{issue.author}</span>
        </div>
        <div>
            <div class="section-heading">Technologies Involved</div>
            <div>{tech_badges}</div>
        </div>
    """

    if issue.missing_skills:
        card_html += f"""
        <div>
            <div class="section-heading" style="color: #FDA4AF;">Potential Skill Gaps to Prepare</div>
            <div>{missing_badges}</div>
        </div>
        """

    card_html += "</div>"
    st.markdown(card_html, unsafe_allow_html=True)

    # Action buttons and expander
    col_link, col_save, col_spacer = st.columns([2, 2, 4])
    with col_link:
        st.link_button(f"🔗 Open Issue #{issue.number} on GitHub", issue.html_url, use_container_width=True)
    with col_save:
        save_label = "⭐ Saved to Shortlist" if is_saved else "⭐ Save to Shortlist"
        if st.button(save_label, key=f"btn_shortlist_{issue.number}", use_container_width=True):
            if on_save_clicked:
                on_save_clicked(issue)

    # Expandable Deep-Dive Section
    with st.expander(f"🔍 Why this matches & Preparation Checklist (Issue #{issue.number})"):
        st.markdown("#### 🎯 Why this issue was recommended:")
        for r in issue.match_reasons:
            st.markdown(f"- {r}")

        st.markdown("#### 📊 Score Breakdown:")
        sb = issue.score_breakdown
        st.write(
            f"- **Skill Overlap:** {int(sb.get('skill_overlap', 0)*100)}% | "
            f"**Experience Fit:** {int(sb.get('experience_fit', 0)*100)}% | "
            f"**Learning Goals:** {int(sb.get('learning_goals', 0)*100)}% | "
            f"**Beginner Labels:** {int(sb.get('beginner_friendly_label', 0)*100)}% | "
            f"**Semantic Similarity:** {int(sb.get('semantic_similarity', 0)*100)}%"
        )

        st.markdown("#### 🏷️ Classification Evidence:")
        for ev in issue.difficulty_evidence:
            st.markdown(f"- *{ev}*")

        if explainer_func:
            with st.spinner("Loading technical explanation..."):
                explanation = explainer_func(issue)
                st.markdown("---")
                st.markdown(f"**Issue Summary:** {explanation.get('summary', '')}")
                if explanation.get("likely_files_to_inspect"):
                    st.markdown("**Suggested Files to Inspect:**")
                    for f in explanation["likely_files_to_inspect"]:
                        st.markdown(f"- `{f}`")
                if explanation.get("implementation_steps"):
                    st.markdown("**Recommended Implementation Steps:**")
                    for s in explanation["implementation_steps"]:
                        st.markdown(f"- {s}")
        else:
            st.markdown("#### 📋 Recommended Preparation Steps:")
            for step in issue.preparation_steps:
                st.markdown(f"- {step}")
