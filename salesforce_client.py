import pandas as pd
from simple_salesforce import Salesforce
from config import (
    SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN, SF_DOMAIN, SF_INSTANCE, SOQL_TEMPLATE
)


def get_connection() -> Salesforce:
    if SF_INSTANCE:
        return Salesforce(
            username=SF_USERNAME,
            password=SF_PASSWORD,
            security_token=SF_SECURITY_TOKEN,
            instance=SF_INSTANCE,
        )
    return Salesforce(
        username=SF_USERNAME,
        password=SF_PASSWORD,
        security_token=SF_SECURITY_TOKEN,
        domain=SF_DOMAIN,
    )


def _build_where_clause(
    start_date: str | None = None,
    end_date: str | None = None,
    subcategories: list[str] | None = None,
    account_owners: list[str] | None = None,
) -> str:
    conditions = []
    if start_date:
        conditions.append(f"CreatedDate >= {start_date}T00:00:00Z")
    if end_date:
        conditions.append(f"CreatedDate <= {end_date}T23:59:59Z")
    if subcategories:
        escaped = [s.replace("'", "\\'") for s in subcategories]
        values = ", ".join(f"'{v}'" for v in escaped)
        conditions.append(f"Subcategory__c IN ({values})")
    if account_owners:
        escaped = [s.replace("'", "\\'") for s in account_owners]
        values = ", ".join(f"'{v}'" for v in escaped)
        conditions.append(f"Account__r.Owner.Name IN ({values})")
    if conditions:
        return "WHERE " + " AND ".join(conditions)
    return ""


def _flatten_record(record: dict) -> dict:
    """Flatten nested Salesforce relationship fields into a flat dict."""
    flat = {}
    account = record.get("Account__r") or {}
    owner = account.get("Owner") or {}
    flat["Account Owner"] = owner.get("Name", "")
    flat["Platform Client ID"] = account.get("Platform_Client_ID__c", "")
    flat["Account Name"] = account.get("Name", "")
    flat["Real MRR Last Month"] = account.get("MRR_Last_Month__c", 0) or 0
    flat["Last Invoiced TPV"] = account.get("Last_Invoiced_TPV__c", 0) or 0
    flat["CS Insight ID"] = record.get("Name", "")
    flat["Date"] = record.get("CreatedDate", "")
    flat["Subcategory"] = record.get("Subcategory__c", "")
    flat["Feedback"] = record.get("Additional_feedback__c", "")
    created_by = record.get("CreatedBy") or {}
    flat["Created By"] = created_by.get("Name", "")
    return flat


def fetch_feedback_data(
    start_date: str | None = None,
    end_date: str | None = None,
    subcategories: list[str] | None = None,
    account_owners: list[str] | None = None,
) -> pd.DataFrame:
    """Fetch feedback data from Salesforce using SOQL. Returns a clean DataFrame."""
    sf = get_connection()
    where_clause = _build_where_clause(start_date, end_date, subcategories, account_owners)
    soql = SOQL_TEMPLATE.format(where_clause=where_clause)
    result = sf.query_all(soql)
    records = [_flatten_record(r) for r in result["records"]]
    df = pd.DataFrame(records)
    if not df.empty:
        df["Real MRR Last Month"] = pd.to_numeric(df["Real MRR Last Month"], errors="coerce").fillna(0)
        df["Last Invoiced TPV"] = pd.to_numeric(df["Last Invoiced TPV"], errors="coerce").fillna(0)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df


def get_filter_options() -> dict:
    """Fetch distinct values for filter dropdowns."""
    sf = get_connection()

    subcategories = sf.query_all(
        "SELECT Subcategory__c FROM CS_Insights__c WHERE Subcategory__c != null GROUP BY Subcategory__c"
    )
    owners = sf.query_all(
        "SELECT Account__r.Owner.Name FROM CS_Insights__c WHERE Account__r.Owner.Name != null GROUP BY Account__r.Owner.Name"
    )

    return {
        "subcategories": sorted(set(r["Subcategory__c"] for r in subcategories["records"])),
        "account_owners": sorted(set(r["Owner"]["Name"] for r in
                                      [r.get("Account__r", {}) or {} for r in owners["records"]]
                                      if r.get("Name"))),
    }


def describe_cs_insight(sf: Salesforce | None = None) -> dict:
    """Utility to inspect CS_Insight__c field names. Run this to confirm API names."""
    if sf is None:
        sf = get_connection()
    desc = sf.CS_Insights__c.describe()
    return {f["name"]: f["label"] for f in desc["fields"]}
