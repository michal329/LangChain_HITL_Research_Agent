import streamlit as st
import uuid
from typing import List, Dict, Any
from agents.info_agent import create_info_gathering_agent
from services import source_service

def init_session_state():
    """
    Initializes all required session state variables if not already present.
    """
    if "agent" not in st.session_state:
        st.session_state.agent = create_info_gathering_agent()

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    if "config" not in st.session_state:
        st.session_state.config = {"configurable": {"thread_id": st.session_state.thread_id}}

    if "pending_sources" not in st.session_state:
        st.session_state.pending_sources = []

def get_agent():
    """
    Retrieves the agent instance stored in the session state.
    """
    return st.session_state.agent

def get_thread_id() -> str:
    """
    Retrieves the unique thread ID.
    """
    return st.session_state.thread_id

def get_config() -> Dict[str, Any]:
    """
    Retrieves the thread run configuration.
    """
    return st.session_state.config

def get_pending_sources() -> List[Dict[str, Any]]:
    """
    Retrieves the current cached list of verification candidate sources.
    """
    return st.session_state.pending_sources

def set_pending_sources(sources: List[Dict[str, Any]]):
    """
    Updates the list of verification candidate sources.
    """
    st.session_state.pending_sources = sources

def reset_thread():
    """
    Resets the thread, creating a new session configuration and clearing cached elements.
    """
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.config = {"configurable": {"thread_id": st.session_state.thread_id}}
    st.session_state.pending_sources = []
    source_service.clear_sources()
    # Clear any old checkbox states from session state
    keys_to_del = [k for k in st.session_state.keys() if k.startswith("src_cb_")]
    for k in keys_to_del:
        del st.session_state[k]

def get_source_checkbox(idx: int) -> bool:
    """
    Checks the checkbox value for a source index, initializing it to True if not present.
    """
    cb_key = f"src_cb_{idx}"
    if cb_key not in st.session_state:
        st.session_state[cb_key] = True
    return st.session_state[cb_key]

def set_source_checkbox(idx: int, value: bool):
    """
    Sets the checkbox value for a source index.
    """
    st.session_state[f"src_cb_{idx}"] = value

def select_all_checkboxes(count: int):
    """
    Selects all source checkboxes.
    """
    for idx in range(count):
        st.session_state[f"src_cb_{idx}"] = True

def deselect_all_checkboxes(count: int):
    """
    Deselects all source checkboxes.
    """
    for idx in range(count):
        st.session_state[f"src_cb_{idx}"] = False

def clear_checkbox_states(count: int):
    """
    Cleans up old checkbox session keys.
    """
    for idx in range(count):
        cb_key = f"src_cb_{idx}"
        if cb_key in st.session_state:
            del st.session_state[cb_key]
