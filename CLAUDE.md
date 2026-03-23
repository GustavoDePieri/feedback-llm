# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

Streamlit dashboard that pulls client feedback from Salesforce (CS_Insight__c object), uses Google Gemini to identify and rank pending product features by MRR impact. Feedbacks are multilingual (Spanish/English).

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Inspect Salesforce field names (useful for debugging SOQL)
python -c "from salesforce_client import describe_cs_insight; print(describe_cs_insight())"
```

## Architecture

- **`config.py`** — Loads credentials from `st.secrets` (Streamlit Cloud) or `.env` (local), defines SOQL template and constants
- **`salesforce_client.py`** — Connects to SF via `simple-salesforce`, fetches data using SOQL with `query_all()` (auto-paginates past 2k row limit). Flattens nested relationship fields into a clean DataFrame.
- **`llm_analyzer.py`** — Two-pass Gemini analysis:
  - Pass 1: Chunks feedbacks (~100/chunk), extracts feature requests as structured JSON
  - Pass 2: Deduplicates/clusters features across chunks, ranks by total MRR
- **`app.py`** — Streamlit UI with sidebar filters (date, subcategory, account owner), two tabs (Feature Ranking + Raw Data), CSV export. Uses `@st.cache_data` for SF fetch and LLM results.

## Key Technical Details

- Salesforce field API names in `config.py` SOQL_TEMPLATE may need adjustment — use `describe_cs_insight()` to verify against the actual SF org
- The Reports API has a 2,000-row hard limit; that's why we use SOQL `query_all()` instead
- LLM prompts are in `llm_analyzer.py` (EXTRACTION_PROMPT and CLUSTERING_PROMPT) — tune these to improve output quality
- Credentials go in `.env` locally (see `.env.example`) or `st.secrets` on Streamlit Cloud, never committed
- Deployed on Streamlit Community Cloud: connect the GitHub repo and configure secrets in Settings
