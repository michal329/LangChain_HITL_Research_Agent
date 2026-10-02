import os
from dotenv import load_dotenv

# Load environment variables from .env file (local development)
load_dotenv()


def _get_setting(name: str, default=None):
    """
    Reads a setting from the environment first, then from Streamlit secrets.
    Locally the value comes from .env; on Streamlit Community Cloud it comes
    from the app's Secrets (root-level secrets are also exported as env vars,
    st.secrets is the fallback).
    """
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st
        return st.secrets.get(name, default)
    except Exception:
        return default


GROQ_API_KEY = _get_setting("GROQ_API_KEY")
TAVILY_API_KEY = _get_setting("TAVILY_API_KEY")
GROQ_MODEL = _get_setting("GROQ_MODEL", "llama-3.1-8b-instant")

# Optional cap on research runs per browser session, to protect API quotas
# on a public deployment. 0 (the default) means unlimited.
MAX_RESEARCH_RUNS_PER_SESSION = int(_get_setting("MAX_RESEARCH_RUNS_PER_SESSION", 0) or 0)

def validate_config() -> bool:
    """
    Checks if critical keys are configured.
    """
    return bool(GROQ_API_KEY and TAVILY_API_KEY)
