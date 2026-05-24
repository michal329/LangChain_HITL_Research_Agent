import streamlit as st
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)

# Fallback module-level storage for non-Streamlit contexts and cross-thread persistence
_FALLBACK_SOURCES: List[Dict[str, Any]] = []

def get_gathered_sources() -> List[Dict[str, Any]]:
    """
    Retrieves the current cached list of gathered sources. Prefers Streamlit session state
    if populated, otherwise falls back to the cross-thread module-level store.
    """
    try:
        if st.runtime.exists():
            if "gathered_sources" not in st.session_state:
                st.session_state.gathered_sources = []
            if st.session_state.gathered_sources:
                return st.session_state.gathered_sources
    except Exception:
        pass
    return _FALLBACK_SOURCES

def set_gathered_sources(sources: List[Dict[str, Any]]) -> None:
    """
    Saves the fetched search results, writing to both the thread-safe fallback list
    and the Streamlit session state proxy (if active in the current thread).
    """
    # 1. Always update the module-level fallback store (cross-thread sharing)
    global _FALLBACK_SOURCES
    _FALLBACK_SOURCES.clear()
    _FALLBACK_SOURCES.extend(sources)
    logger.info(f"Updated cross-thread fallback source store with {len(sources)} sources.")

    # 2. Also try updating Streamlit session state if available in this thread context
    try:
        if st.runtime.exists():
            if "gathered_sources" not in st.session_state:
                st.session_state.gathered_sources = []
            st.session_state.gathered_sources.clear()
            st.session_state.gathered_sources.extend(sources)
            logger.info(f"Updated Streamlit session state store with {len(sources)} sources.")
    except Exception:
        pass

def clear_sources() -> None:
    """
    Clears both the fallback list and the Streamlit session state cache.
    """
    # 1. Clear fallback store
    global _FALLBACK_SOURCES
    _FALLBACK_SOURCES.clear()
    logger.info("Cleared cross-thread fallback source store cache.")

    # 2. Clear Streamlit session state
    try:
        if st.runtime.exists() and "gathered_sources" in st.session_state:
            st.session_state.gathered_sources.clear()
            logger.info("Cleared Streamlit session state source store cache.")
    except Exception:
        pass
