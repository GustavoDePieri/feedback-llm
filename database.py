import pandas as pd
from supabase import create_client, Client
from config import _get_secret


def get_client() -> Client:
    url = _get_secret("SUPABASE_URL")
    key = _get_secret("SUPABASE_ANON_KEY")
    return create_client(url, key)


def save_analysis(
    start_date: str,
    end_date: str,
    filters: dict,
    feedback_df: pd.DataFrame,
    result_df: pd.DataFrame,
) -> int:
    """Save an analysis run and its features. Returns the run ID."""
    db = get_client()

    run = db.table("analysis_runs").insert({
        "start_date": start_date,
        "end_date": end_date,
        "filters": filters,
        "total_feedbacks": len(feedback_df),
        "unique_accounts": int(feedback_df["Account Name"].nunique()),
        "total_mrr": float(feedback_df["Real MRR Last Month"].sum()),
    }).execute()

    run_id = run.data[0]["id"]

    features = []
    for idx, row in result_df.iterrows():
        features.append({
            "run_id": run_id,
            "rank": int(idx) + 1,
            "feature": row.get("Feature", ""),
            "total_mrr": float(row.get("Total MRR", 0)),
            "account_count": int(row.get("Account Count", 0)),
            "accounts": row.get("Accounts", ""),
            "sample_feedbacks": row.get("Sample Feedbacks", ""),
            "ai_insight": row.get("AI Insight", ""),
        })

    if features:
        db.table("analysis_features").insert(features).execute()

    return run_id


def load_history() -> list[dict]:
    """Return all past analysis runs with their features."""
    db = get_client()
    runs = db.table("analysis_runs").select("*").order("created_at", desc=True).execute()
    return runs.data


def load_run_features(run_id: int) -> pd.DataFrame:
    """Return features for a specific run as a DataFrame."""
    db = get_client()
    rows = (
        db.table("analysis_features")
        .select("*")
        .eq("run_id", run_id)
        .order("rank")
        .execute()
    )
    return pd.DataFrame(rows.data)
