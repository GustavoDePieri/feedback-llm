import re
import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config(
    page_title="Ontop — Feedback Intelligence",
    page_icon="https://www.ontop.ai/favicon.ico",
    layout="wide",
)

# --- Ontop-inspired theme via custom CSS ---
st.markdown("""
<style>
    /* Dark background matching Ontop's palette */
    .stApp {
        background: linear-gradient(180deg, #0a0a1a 0%, #111128 50%, #0a0a1a 100%);
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: #0d0d24 !important;
        border-right: 1px solid rgba(139, 92, 246, 0.15);
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #c4b5fd !important;
    }

    /* Header area */
    .ontop-header {
        padding: 1.5rem 0 1rem 0;
        border-bottom: 1px solid rgba(139, 92, 246, 0.2);
        margin-bottom: 1.5rem;
    }
    .ontop-logo {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .ontop-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a3e 0%, #16163a 100%);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid rgba(139, 92, 246, 0.2);
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
        border-radius: 8px 8px 0 0;
        padding: 0.6rem 1.5rem;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(139, 92, 246, 0.1);
        color: #c4b5fd !important;
        border-bottom: 2px solid #8b5cf6;
    }

    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #1a1a3e 0%, #16163a 100%);
        border: 1px solid rgba(139, 92, 246, 0.15);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s;
    }
    .feature-card:hover {
        border-color: rgba(139, 92, 246, 0.4);
    }
    .feature-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.75rem;
    }
    .feature-metrics {
        display: flex;
        gap: 2rem;
        margin-bottom: 0.75rem;
    }
    .feature-metric {
        display: flex;
        flex-direction: column;
    }
    .feature-metric-label {
        font-size: 0.7rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .feature-metric-value {
        font-size: 1.3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .feature-accounts {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-bottom: 0.5rem;
    }
    .feature-insight {
        background: rgba(139, 92, 246, 0.08);
        border-left: 3px solid #8b5cf6;
        border-radius: 0 8px 8px 0;
        padding: 0.75rem 1rem;
        margin-top: 0.75rem;
        font-size: 0.9rem;
        color: #c4b5fd;
        line-height: 1.5;
    }
    .feature-feedback {
        font-size: 0.82rem;
        color: #64748b;
        font-style: italic;
        margin-top: 0.5rem;
    }
    .rank-badge {
        display: inline-block;
        background: linear-gradient(135deg, #8b5cf6, #ec4899);
        color: white;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        margin-right: 0.5rem;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #8b5cf6, #ec4899) !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button[kind="primary"]:hover {
        opacity: 0.85 !important;
    }

    /* Download buttons */
    .stDownloadButton > button {
        background: transparent !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 12px !important;
        color: #c4b5fd !important;
    }
    .stDownloadButton > button:hover {
        border-color: #8b5cf6 !important;
        background: rgba(139, 92, 246, 0.1) !important;
    }

    /* Dataframe */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Welcome state */
    .welcome-box {
        text-align: center;
        padding: 4rem 2rem;
    }
    .welcome-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .welcome-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
    }
    .welcome-text {
        color: #64748b;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="ontop-header">
    <div class="ontop-logo">ontop</div>
    <div class="ontop-subtitle">Feedback Intelligence — Product Feature Impact Analysis</div>
</div>
""", unsafe_allow_html=True)

# --- Sidebar filters ---
st.sidebar.markdown("### Filters")

start_date = st.sidebar.date_input("Start date", value=date.today() - timedelta(days=90))
end_date = st.sidebar.date_input("End date", value=date.today())

@st.cache_data(ttl=3600, show_spinner="Loading filters from Salesforce...")
def load_filter_options():
    from salesforce_client import get_filter_options
    return get_filter_options()

try:
    filter_opts = load_filter_options()
    subcategory_options = filter_opts["subcategories"]
    owner_options = filter_opts["account_owners"]
except Exception as e:
    st.sidebar.error(f"Could not load filters: {e}")
    subcategory_options = []
    owner_options = []

selected_subcategories = st.sidebar.multiselect("Subcategory", subcategory_options)
selected_owners = st.sidebar.multiselect("Account Owner", owner_options)

st.sidebar.markdown("---")
st.sidebar.markdown("### MRR Filter")
mrr_filter_type = st.sidebar.radio(
    "Filter accounts by MRR",
    ["No filter", "Minimum MRR", "Top N accounts"],
    horizontal=True,
)
min_mrr = 0.0
top_n = 0
if mrr_filter_type == "Minimum MRR":
    min_mrr = st.sidebar.number_input("Minimum MRR ($)", min_value=0.0, value=1000.0, step=100.0)
elif mrr_filter_type == "Top N accounts":
    top_n = st.sidebar.number_input("Top N accounts by MRR", min_value=1, value=10, step=1)

st.sidebar.markdown("---")
st.sidebar.markdown("### Keyword Search")
keyword_search = st.sidebar.text_input("Search in feedbacks", placeholder="e.g. ACH, invoice, payroll...")

st.sidebar.markdown("---")
fetch_clicked = st.sidebar.button("Fetch & Analyze", type="primary", use_container_width=True)

# --- Data fetching (cached) ---
@st.cache_data(ttl=3600, show_spinner="Fetching data from Salesforce...")
def load_data(start: str, end: str, subcats: tuple, owners: tuple) -> pd.DataFrame:
    from salesforce_client import fetch_feedback_data
    return fetch_feedback_data(
        start_date=start,
        end_date=end,
        subcategories=list(subcats) if subcats else None,
        account_owners=list(owners) if owners else None,
    )

# --- Main logic ---
if fetch_clicked:
    start_str = start_date.isoformat()
    end_str = end_date.isoformat()
    subcats_tuple = tuple(selected_subcategories)
    owners_tuple = tuple(selected_owners)

    df = load_data(start_str, end_str, subcats_tuple, owners_tuple)

    if df.empty:
        st.warning("No feedback records found for the selected filters.")
    else:
        if mrr_filter_type == "Minimum MRR" and min_mrr > 0:
            df = df[df["Real MRR Last Month"] >= min_mrr]
        elif mrr_filter_type == "Top N accounts" and top_n > 0:
            top_accounts = (
                df.groupby("Account Name")["Real MRR Last Month"]
                .max()
                .nlargest(top_n)
                .index
            )
            df = df[df["Account Name"].isin(top_accounts)]

        # Keyword filter (word-boundary match to avoid partial matches like "reach" for "ACH")
        if keyword_search.strip():
            keyword = keyword_search.strip()
            pattern = r'\b' + re.escape(keyword) + r'\b'
            df = df[df["Feedback"].fillna("").str.contains(pattern, case=False, na=False, regex=True)]

        if df.empty:
            st.warning("No feedback records match the selected filters.")
        else:
            st.session_state["feedback_data"] = df

    # Clear previous analysis on re-fetch
    if "analysis_result" in st.session_state:
        del st.session_state["analysis_result"]

# Display if data exists in session
if "feedback_data" in st.session_state:
    df = st.session_state["feedback_data"]

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Feedbacks", f"{len(df):,}")
    col2.metric("Unique Accounts", f"{df['Account Name'].nunique():,}")
    col3.metric("Total MRR in Scope", f"${df['Real MRR Last Month'].sum():,.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Feature Ranking", "Raw Feedback Data"])

    with tab2:
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode("utf-8")
        raw_filename = f"feedback_raw_{start_date.isoformat()}_{end_date.isoformat()}.csv"
        st.download_button("Download Raw Data (CSV)", csv, raw_filename, "text/csv")

    with tab1:
        if "analysis_result" not in st.session_state:
            analyze_clicked = st.button("Run Feature Analysis", type="primary")
            if analyze_clicked:
                progress_bar = st.progress(0, text="Analyzing feedbacks with Gemini...")

                def update_progress(pct):
                    progress_bar.progress(pct, text=f"Analyzing feedbacks... {int(pct * 100)}%")

                from llm_analyzer import analyze_feedbacks
                from database import save_analysis
                result_df = analyze_feedbacks(df, progress_callback=update_progress)
                progress_bar.empty()
                st.session_state["analysis_result"] = result_df

                # Persist to Supabase
                try:
                    filters_meta = {
                        "subcategories": selected_subcategories,
                        "account_owners": selected_owners,
                        "mrr_filter": mrr_filter_type,
                        "min_mrr": min_mrr,
                        "top_n": int(top_n),
                    }
                    save_analysis(start_date.isoformat(), end_date.isoformat(), filters_meta, df, result_df)
                except Exception as e:
                    st.warning(f"Analysis complete, but could not save to database: {e}")

        if "analysis_result" in st.session_state:
            result_df = st.session_state["analysis_result"]
            if result_df.empty:
                st.info("No actionable feature requests found in the feedback data.")
            else:
                st.markdown(f"### Top {len(result_df)} Product Features by MRR Impact")
                st.markdown("<br>", unsafe_allow_html=True)

                for idx, row in result_df.iterrows():
                    rank = idx + 1
                    feedbacks_text = row.get("Sample Feedbacks", "")
                    # Split sample feedbacks by pipe
                    feedback_items = [f.strip() for f in feedbacks_text.split("|") if f.strip()] if feedbacks_text else []
                    feedback_html = "".join(
                        f'<div class="feature-feedback">"{fb}"</div>' for fb in feedback_items[:3]
                    )

                    insight_html = ""
                    insight = row.get("AI Insight", "")
                    if insight:
                        insight_html = f'<div class="feature-insight">{insight}</div>'

                    st.markdown(f"""
                    <div class="feature-card">
                        <div class="feature-title">
                            <span class="rank-badge">#{rank}</span>
                            {row['Feature']}
                        </div>
                        <div class="feature-metrics">
                            <div class="feature-metric">
                                <span class="feature-metric-label">Total MRR Impact</span>
                                <span class="feature-metric-value">${row['Total MRR']:,.2f}</span>
                            </div>
                            <div class="feature-metric">
                                <span class="feature-metric-label">Accounts</span>
                                <span class="feature-metric-value">{row['Account Count']}</span>
                            </div>
                        </div>
                        <div class="feature-accounts">Accounts: {row['Accounts']}</div>
                        {feedback_html}
                        {insight_html}
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                csv = result_df.to_csv(index=False).encode("utf-8")
                analysis_filename = f"feature_analysis_{start_date.isoformat()}_{end_date.isoformat()}.csv"
                st.download_button(
                    "Download Feature Analysis (CSV)",
                    csv,
                    analysis_filename,
                    "text/csv",
                )

else:
    st.markdown("""
    <div class="welcome-box">
        <div class="welcome-title">Welcome to Feedback Intelligence</div>
        <div class="welcome-text">Set your filters in the sidebar and click <strong>Fetch & Analyze</strong> to discover<br>which product features have the highest MRR impact.</div>
    </div>
    """, unsafe_allow_html=True)

# --- History section (always visible) ---
st.markdown("---")
st.markdown("### Past Analyses")
try:
    from database import load_history, load_run_features
    history = load_history()
    if not history:
        st.info("No analyses saved yet. Run your first analysis to see it here.")
    else:
        for run in history:
            run_date = run["created_at"][:10]
            label = f"**{run_date}** — {run['start_date']} to {run['end_date']} | {run['total_feedbacks']} feedbacks | ${run['total_mrr']:,.2f} MRR"
            with st.expander(label):
                features_df = load_run_features(run["id"])
                if features_df.empty:
                    st.write("No features saved for this run.")
                else:
                    for _, row in features_df.iterrows():
                        insight_html = f'<div class="feature-insight">{row["ai_insight"]}</div>' if row.get("ai_insight") else ""
                        st.markdown(f"""
                        <div class="feature-card">
                            <div class="feature-title">
                                <span class="rank-badge">#{int(row['rank'])}</span>
                                {row['feature']}
                            </div>
                            <div class="feature-metrics">
                                <div class="feature-metric">
                                    <span class="feature-metric-label">Total MRR Impact</span>
                                    <span class="feature-metric-value">${row['total_mrr']:,.2f}</span>
                                </div>
                                <div class="feature-metric">
                                    <span class="feature-metric-label">Accounts</span>
                                    <span class="feature-metric-value">{int(row['account_count'])}</span>
                                </div>
                            </div>
                            <div class="feature-accounts">Accounts: {row['accounts']}</div>
                            {insight_html}
                        </div>
                        """, unsafe_allow_html=True)
except Exception as e:
    st.error(f"Could not load history: {e}")
