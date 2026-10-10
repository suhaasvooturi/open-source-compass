"""About and Methodology: Scoring models, architecture, limitations, and responsible use."""

from __future__ import annotations

import streamlit as st

from finder.ui_components import inject_custom_styles, render_hero_banner

st.set_page_config(
    page_title="About & Methodology | OpenSource Compass",
    page_icon="ℹ️",
    layout="wide",
)

inject_custom_styles()

render_hero_banner(
    title="About & Methodology",
    tagline="Transparent scoring formulas, classification heuristics, and design ethics.",
)

with st.sidebar:
    st.page_link("app.py", label="← Back to Main Dashboard", icon="🏠")
    st.page_link("pages/1_Issue_Explorer.py", label="Issue Explorer", icon="🔎")
    st.page_link("pages/2_Repository_Analysis.py", label="Repository Analysis", icon="🏛️")
    st.page_link("pages/3_Skill_Gap_Analysis.py", label="Skill Gap Analysis", icon="📈")
    st.page_link("pages/4_Saved_Shortlist.py", label="Saved Shortlist", icon="⭐")

tab_method, tab_arch, tab_ethics, tab_credits = st.tabs([
    "📐 Scoring & Heuristics",
    "🏛️ System Architecture",
    "🛡️ Limitations & Responsible Use",
    "👤 Project & License",
])

# -------------------------------------------------------------
# TAB 1: Scoring & Heuristics
# -------------------------------------------------------------
with tab_method:
    st.subheader("1. Explainable Ranking Formula")
    st.write(
        "OpenSource Compass uses a multi-factor weighted scoring model to match developers with issues. "
        "Scores are normalized to the range `[0.0, 1.0]` (or 0% - 100%)."
    )

    st.latex(
        r"""
        \text{Match Score} = w_{\text{skill}} \cdot S_{\text{skill}} + w_{\text{exp}} \cdot S_{\text{exp}} + w_{\text{goals}} \cdot S_{\text{goals}} + w_{\text{label}} \cdot S_{\text{label}} + w_{\text{semantic}} \cdot S_{\text{semantic}}
        """
    )

    st.markdown("""
    | Weight | Factor | Description |
    | :--- | :--- | :--- |
    | **30%** | **$S_{\text{skill}}$: Skill Overlap** | Jaccard overlap between developer's skills and technologies detected in the issue and repository. |
    | **25%** | **$S_{\text{exp}}$: Experience Fit** | Match between user experience level (Beginner, Intermediate, Advanced) and estimated issue difficulty. |
    | **20%** | **$S_{\text{goals}}$: Learning Goals** | Degree to which the issue provides an opportunity to practice user-defined learning goals. |
    | **15%** | **$S_{\text{label}}$: Friendly Labels** | Bonus for newcomer-friendly labels (`good first issue`, `help wanted`, `beginner`). |
    | **10%** | **$S_{\text{semantic}}$: Semantic Text Similarity** | TF-IDF Cosine Similarity (or optional Sentence-Transformers embedding similarity) comparing user profile vector to issue text. |
    """)

    st.markdown("---")
    st.subheader("2. Difficulty Classification Heuristics")
    st.write("Issues are classified into **Beginner**, **Intermediate**, **Advanced**, or **Difficulty uncertain** using multiple triangulated signals:")
    st.markdown("""
    1. **Maintainer Labels:** Community labels like `good first issue`, `documentation`, `bug`, `refactor`, `complex`. Labels are treated as hints, not absolute ground truth.
    2. **Text Patterns & Keywords:** Introductory indicators (e.g. typos, documentation, minor test cases) vs. architectural indicators (e.g. race conditions, memory leaks, distributed consensus).
    3. **Structural Complexity:** Presence of extensive checklists, multiple stack traces, or complex code snippets.
    4. **Uncertainty Fallback:** If an issue has less than 5 words and no labels, it is marked **Difficulty uncertain** to avoid fabricating false confidence.
    """)

# -------------------------------------------------------------
# TAB 2: System Architecture
# -------------------------------------------------------------
with tab_arch:
    st.subheader("Modular Architecture")
    st.markdown("""
    ```
    ┌────────────────────────────────────────────────────────┐
    │              Streamlit UI Dashboard & Pages            │
    └───────────┬────────────────────────────────┬───────────┘
                │                                │
    ┌───────────▼───────────┐        ┌───────────▼───────────┐
    │  GitHub REST API v3   │        │   Synthetic Demo Data │
    │  (Rate-limited/Cache) │        │   (100% Offline Mode) │
    └───────────┬───────────┘        └───────────┬───────────┘
                │                                │
    ┌───────────▼────────────────────────────────▼───────────┐
    │            Repository & Architecture Analyzer          │
    │         (Tech detection, Build files, Health)          │
    └───────────────────────────┬────────────────────────────┘
                                │
    ┌───────────────────────────▼────────────────────────────┐
    │                 Issue Classification                  │
    │             (Multi-signal heuristics & effort)         │
    └───────────────────────────┬────────────────────────────┘
                                │
    ┌───────────────────────────▼────────────────────────────┐
    │            Explainable Recommendation Engine           │
    │       (Weighted ranking + TF-IDF Semantic Matching)    │
    └───────────────────────────┬────────────────────────────┘
                                │
    ┌───────────────────────────▼────────────────────────────┐
    │            Provider-Independent Explainer              │
    │       (Grounded Template Engine / Optional LLM)        │
    └────────────────────────────────────────────────────────┘
    ```
    """)

# -------------------------------------------------------------
# TAB 3: Limitations & Responsible Use
# -------------------------------------------------------------
with tab_ethics:
    st.subheader("Important Disclaimers & Responsible Use")
    st.markdown("""
    - **Not a Probability of Success:** The match score reflects profile compatibility and relevance, *not* a statistical guarantee that a pull request will be merged. Review policies and project priorities remain at the maintainers' discretion.
    - **Public Read-Only Data:** OpenSource Compass accesses only publicly available GitHub data through standard read-only REST endpoints. No private data is accessed or scraped.
    - **Zero Password Collection:** The application never requests or stores GitHub passwords.
    - **Untrusted Input Safety:** Issue titles, descriptions, and README files are treated as untrusted input. The application never executes shell commands or instructions found in issue bodies.
    - **Transparent Limitations:** If README files, test suites, or contribution guides are missing, the tool explicitly reports them rather than assuming their contents.
    """)

# -------------------------------------------------------------
# TAB 4: Project & Credits
# -------------------------------------------------------------
with tab_credits:
    st.subheader("OpenSource Compass")
    st.markdown("""
    - **Tagline:** Find your first issue. Make your first contribution.
    - **GitHub Repository:** [suhaasvooturi/ai-open-source-contribution-finder](https://github.com/suhaasvooturi/ai-open-source-contribution-finder)
    - **Author / Copyright Holder:** Suhaas Vooturi
    - **License:** MIT License
    - **Stack:** Python 3.12 + Streamlit + scikit-learn + pandas + requests
    """)
