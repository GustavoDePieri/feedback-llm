import json
import google.generativeai as genai
import pandas as pd
from config import GEMINI_API_KEY, GEMINI_MODEL, CHUNK_SIZE

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

EXTRACTION_PROMPT = """You are analyzing client feedback for a fintech/payroll platform called Ontop.
Your task: extract actionable product feature requests from the feedback below.

Rules:
- Only extract concrete, actionable feature requests explicitly mentioned in the feedback.
- Ignore general praise, complaints without specific requests, or support issues.
- Feedback may be in Spanish or English. Normalize all output to English.
- For each feature, include which accounts requested it and their MRR.
- Return ONLY valid JSON, no commentary.

Return a JSON array where each element has:
{
  "feature": "Short description of the requested feature",
  "accounts": [{"name": "Account Name", "mrr": 1234.56}],
  "sample_feedbacks": ["Original feedback text (truncated to 200 chars)"]
}

If no actionable feature requests exist in the data, return an empty array: []

Here is the feedback data (CSV format):
Account Name | Real MRR Last Month | Feedback
"""

CLUSTERING_PROMPT = """You are a senior product analyst at Ontop, a fintech/payroll platform. Below is a list of extracted feature requests from client feedback, with associated accounts and MRR values.

Your task:
1. Merge and deduplicate similar feature requests into unified features.
2. For each unified feature, aggregate all unique accounts and sum their MRR.
3. Rank features by total MRR impact (highest first).
4. Keep feature descriptions concise but specific.
5. For EACH feature, write an "insight" — a brief strategic recommendation (2-3 sentences) explaining why this feature matters, the business impact of building it, and a suggested priority or approach.

Rules:
- Combine features that are clearly the same request phrased differently.
- Do NOT merge features that are only loosely related.
- An account should only be counted once per feature even if they mentioned it multiple times.
- The insight should be actionable and reference the MRR at risk or growth opportunity.
- Return ONLY valid JSON, no commentary.

Return a JSON array:
{
  "features": [
    {
      "feature": "Feature description",
      "total_mrr": 12345.67,
      "account_count": 5,
      "accounts": [{"name": "Account Name", "mrr": 1234.56}],
      "sample_feedbacks": ["Example feedback 1", "Example feedback 2"],
      "insight": "Strategic recommendation about this feature request."
    }
  ]
}

Extracted feature requests:
"""


def _call_llm(prompt: str, data: str) -> str:
    import time
    for attempt in range(3):
        try:
            response = model.generate_content(prompt + data)
            return response.text
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                wait = 30 * (attempt + 1)
                import streamlit as st
                st.info(f"Rate limited, waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                raise


def _parse_json(text: str) -> dict | list:
    """Extract JSON from Claude's response, handling markdown code blocks."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]  # remove opening ```json
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return json.loads(text)


def extract_features(df: pd.DataFrame, progress_callback=None) -> list[dict]:
    """Pass 1: Extract feature requests from feedback in chunks."""
    if df.empty:
        return []

    # Filter rows that actually have feedback text
    df_with_feedback = df[df["Feedback"].notna() & (df["Feedback"].str.strip() != "")]
    if df_with_feedback.empty:
        return []

    all_features = []
    total_chunks = (len(df_with_feedback) + CHUNK_SIZE - 1) // CHUNK_SIZE

    for i in range(0, len(df_with_feedback), CHUNK_SIZE):
        chunk = df_with_feedback.iloc[i:i + CHUNK_SIZE]
        chunk_num = i // CHUNK_SIZE + 1

        # Format chunk as text table
        rows = []
        for _, row in chunk.iterrows():
            feedback = str(row["Feedback"])[:500]  # truncate very long feedbacks
            rows.append(f"{row['Account Name']} | ${row['Real MRR Last Month']:,.2f} | {feedback}")
        data = "\n".join(rows)

        try:
            result = _call_llm(EXTRACTION_PROMPT, data)
            features = _parse_json(result)
            if isinstance(features, list):
                all_features.extend(features)
        except Exception as e:
            import streamlit as st
            st.warning(f"Chunk {chunk_num}/{total_chunks} failed: {e}")

        if progress_callback:
            progress_callback(chunk_num / total_chunks)

    return all_features


def cluster_and_rank(features: list[dict]) -> pd.DataFrame:
    """Pass 2: Deduplicate, cluster, and rank features by MRR impact."""
    if not features:
        return pd.DataFrame(columns=["Feature", "Total MRR", "Account Count", "Accounts", "Sample Feedbacks", "AI Insight"])

    data = json.dumps(features, indent=2)
    result = _call_llm(CLUSTERING_PROMPT, data)
    parsed = _parse_json(result)

    if isinstance(parsed, dict):
        features_list = parsed.get("features", [])
    elif isinstance(parsed, list):
        features_list = parsed
    else:
        features_list = []

    rows = []
    for f in features_list:
        accounts = f.get("accounts", [])
        account_names = [a["name"] for a in accounts]
        rows.append({
            "Feature": f.get("feature", "Unknown"),
            "Total MRR": f.get("total_mrr", 0),
            "Account Count": f.get("account_count", len(accounts)),
            "Accounts": ", ".join(account_names),
            "Sample Feedbacks": " | ".join(f.get("sample_feedbacks", [])[:3]),
            "AI Insight": f.get("insight", ""),
        })

    result_df = pd.DataFrame(rows)
    if not result_df.empty:
        result_df = result_df.sort_values("Total MRR", ascending=False).reset_index(drop=True)
    return result_df


def analyze_feedbacks(df: pd.DataFrame, progress_callback=None) -> pd.DataFrame:
    """Full pipeline: extract features then cluster and rank them."""
    features = extract_features(df, progress_callback=progress_callback)
    return cluster_and_rank(features)
