import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not needed on Streamlit Cloud

def _get_secret(key: str, default: str = "") -> str:
    """Read from st.secrets (Streamlit Cloud) or env vars (local)."""
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)

# Salesforce
SF_USERNAME = _get_secret("SF_USERNAME")
SF_PASSWORD = _get_secret("SF_PASSWORD")
SF_SECURITY_TOKEN = _get_secret("SF_SECURITY_TOKEN")
SF_INSTANCE = _get_secret("SF_INSTANCE")
SF_DOMAIN = _get_secret("SF_DOMAIN", "login")

# Google Gemini
GEMINI_API_KEY = _get_secret("GEMINI_API_KEY")

# LLM settings
GEMINI_MODEL = "gemini-3.0-flash"
CHUNK_SIZE = 100

# Salesforce report ID (fallback if SOQL doesn't work)
REPORT_ID = "00OVP0000071fwL2AQ"

SOQL_TEMPLATE = """
SELECT
    Account__r.Owner.Name,
    Account__r.Name,
    Account__r.MRR_Last_Month__c,
    Account__r.Last_Invoiced_TPV__c,
    Account__r.Platform_Client_ID__c,
    Name,
    CreatedDate,
    Subcategory__c,
    Additional_feedback__c,
    CreatedBy.Name
FROM CS_Insights__c
{where_clause}
ORDER BY CreatedDate DESC
"""
