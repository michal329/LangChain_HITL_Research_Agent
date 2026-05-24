import streamlit as st
import uuid
import os
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.types import Command

from config import settings
from agents.info_agent import create_info_gathering_agent
from services import source_service, approval_service
from utils.logger import get_logger

logger = get_logger(__name__)

# Set page configuration for a premium responsive experience
st.set_page_config(
    page_title="Sage B/C Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom design and CSS styles for a premium modern aesthetic
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.main-title {
    font-weight: 700;
    background: linear-gradient(90deg, #6C63FF, #FF6584);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}

.subtitle {
    font-size: 1.1rem;
    opacity: 0.85;
    margin-bottom: 2rem;
}

.source-card {
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    background-color: rgba(128, 128, 128, 0.03);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.source-card:hover {
    box-shadow: 0 8px 24px rgba(108, 99, 255, 0.12);
    border-color: #6C63FF;
    transform: translateY(-2px);
}

.source-title {
    font-size: 1.1rem;
    font-weight: 600;
    text-decoration: none;
    color: #6C63FF !important;
    margin-bottom: 0.4rem;
    display: inline-block;
}

.source-url {
    color: #888888;
    font-size: 0.8rem;
    margin-bottom: 0.8rem;
    word-break: break-all;
}

.source-snippet {
    font-size: 0.95rem;
    line-height: 1.5;
    opacity: 0.9;
}

.chat-bubble-user {
    background-color: rgba(108, 99, 255, 0.1);
    border-radius: 15px;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 5px solid #6C63FF;
}

.chat-bubble-assistant {
    background-color: rgba(128, 128, 128, 0.05);
    border-radius: 15px;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 5px solid #FF6584;
}

.status-pill {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
}

.status-thinking {
    background-color: rgba(108, 99, 255, 0.15);
    color: #6C63FF;
}

.status-hitl {
    background-color: rgba(255, 101, 132, 0.15);
    color: #FF6584;
}
</style>
""", unsafe_allow_html=True)

# Initialize Session States
if "agent" not in st.session_state:
    st.session_state.agent = create_info_gathering_agent()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "config" not in st.session_state:
    st.session_state.config = {"configurable": {"thread_id": st.session_state.thread_id}}

if "pending_sources" not in st.session_state:
    st.session_state.pending_sources = []

# Sidebar Navigation and Control Panel
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2 style="font-weight: 700; color: #6C63FF; margin-bottom: 0;">Sage B/C</h2>
        <p style="font-size: 0.9rem; opacity: 0.8;">Research Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    st.markdown("### ⚙️ Session Settings")
    st.markdown(f"**Thread ID:** `{st.session_state.thread_id[:8]}...`")
    
    # Check environment variable configurations
    groq_configured = "Configured ✅" if settings.GROQ_API_KEY else "Missing ❌"
    tavily_configured = "Configured ✅" if settings.TAVILY_API_KEY else "Missing ❌"
    
    st.write(f"**Groq API Key:** {groq_configured}")
    st.write(f"**Tavily API Key:** {tavily_configured}")
    
    st.write("---")
    
    # New Thread Button to clear checkpointer state
    if st.button("🔄 New Research Thread", use_container_width=True, type="secondary"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.config = {"configurable": {"thread_id": st.session_state.thread_id}}
        st.session_state.pending_sources = []
        source_service.clear_sources()
        # Clear any old checkbox states from session state
        keys_to_del = [k for k in st.session_state.keys() if k.startswith("src_cb_")]
        for k in keys_to_del:
            del st.session_state[k]
        st.success("New thread initialized!")
        st.rerun()
        
    st.write("---")
    
    # Educational section about the multi-turn agent flow
    st.markdown("### 📖 How It Works")
    st.markdown("""
    1. **Initial Search:** Enter a topic in the chat. The assistant will search the web using Tavily.
    2. **Human-in-the-Loop:** Before compiling the final report, the assistant will present the gathered sources. You can select which ones to approve, or reject and ask for a new search with custom feedback.
    3. **Final Summary:** Once approved, the assistant will generate a comprehensive, category-grouped summary of the selected sources.
    """)

# Validate environment variables before running
if st.session_state.agent is None:
    st.error("🔑 API Keys Missing or Configuration Failed!")
    st.markdown("""
    Please configure your API keys in the `.env` file in the project root:
    ```env
    GROQ_API_KEY=your_groq_api_key
    TAVILY_API_KEY=your_tavily_api_key
    ```
    """)
    st.stop()

# Retrieve current agent message state
state = st.session_state.agent.get_state(st.session_state.config)
messages = state.values.get("messages", [])

# Header section
col_title, col_status = st.columns([0.8, 0.2])
with col_title:
    st.markdown("<h1 class='main-title'>Sage B/C Research Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>A premium Human-in-the-Loop web research tool</p>", unsafe_allow_html=True)

# Detect if the agent is interrupted on approve tool call
is_interrupted = False
pending_tool_call = None

if "messages" in state.values and len(state.values["messages"]) > 0:
    last_msg = state.values["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        for tool_call in last_msg.tool_calls:
            if tool_call["name"] == "approve":
                is_interrupted = True
                pending_tool_call = tool_call
                break

with col_status:
    # Render interactive status indicator
    st.write("")
    if is_interrupted:
        st.markdown("<div class='status-pill status-hitl'>🚦 Awaiting Approval</div>", unsafe_allow_html=True)
    elif len(messages) > 0:
        st.markdown("<div class='status-pill status-thinking'>🤖 Ready for Instruction</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='status-pill status-thinking'>🟢 Idle</div>", unsafe_allow_html=True)

# Render Chat History
if not messages:
    st.markdown("""
    <div style="text-align: center; padding: 3rem 1rem;">
        <h2 style="font-weight: 600; opacity: 0.8;">Welcome! Ready to conduct extensive web research?</h2>
        <p style="font-size: 1.1rem; opacity: 0.7; max-width: 600px; margin: 1rem auto;">
            Enter a topic below to initiate web search, retrieve metadata, curate list of sources, and compile detailed reports.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("### 💬 Conversation History")
    for msg in messages:
        # Render User message
        if isinstance(msg, HumanMessage):
            with st.chat_message("user", avatar="👤"):
                st.write(msg.content)
                
        # Render Assistant message
        elif isinstance(msg, AIMessage):
            if msg.content:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(msg.content)
            
            # Display proposed actions / tool calls
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    if tc["name"] == "search":
                        st.info(f"🔍 **Agent Proposed Search:** `{tc['args'].get('query', '')}`")
                    elif tc["name"] == "approve":
                        st.warning("⚠️ **Agent Proposed Sources for Human Verification**")
                        
        # Render Tool execution messages
        elif isinstance(msg, ToolMessage):
            if msg.name == "search":
                with st.expander("📋 View Search Tool Results", expanded=False):
                    st.markdown(msg.content)
            elif msg.name == "approve":
                with st.expander("✅ Approved Sources & Summary Context", expanded=False):
                    st.markdown(msg.content)

# Render Human-in-the-Loop (HITL) Interface
if is_interrupted and pending_tool_call:
    # Populates pending sources from module-level store if not already set in session state
    if not st.session_state.pending_sources and source_service.get_gathered_sources():
        st.session_state.pending_sources = list(source_service.get_gathered_sources())
        
    if st.session_state.pending_sources:
        st.write("---")
        st.markdown("## 🔍 Gathered Sources Verification")
        st.info("Please choose which sources to keep for the final summary. You can select/deselect individual sources, search or filter through them, and approve them, or reject and prompt the agent to search again.")
        
        # Initialize checkbox states in session state if not set
        for idx in range(len(st.session_state.pending_sources)):
            cb_key = f"src_cb_{idx}"
            if cb_key not in st.session_state:
                st.session_state[cb_key] = True  # True by default
                
        # Search & Filter box for sources
        filter_query = st.text_input("🔍 Filter sources by title or brief...", "")
        
        # Select All / Deselect All quick buttons
        col_s1, col_s2 = st.columns([0.15, 0.85])
        with col_s1:
            if st.button("Select All", use_container_width=True):
                for idx in range(len(st.session_state.pending_sources)):
                    st.session_state[f"src_cb_{idx}"] = True
                st.rerun()
        with col_s2:
            if st.button("Deselect All", use_container_width=True):
                for idx in range(len(st.session_state.pending_sources)):
                    st.session_state[f"src_cb_{idx}"] = False
                st.rerun()
                
        # Render list of source cards with checkboxes
        selected_indices = []
        for idx, src in enumerate(st.session_state.pending_sources):
            # Apply user filter query
            if filter_query:
                q = filter_query.lower()
                if q not in src.get('title', '').lower() and q not in src.get('content', '').lower():
                    continue
                    
            cb_key = f"src_cb_{idx}"
            
            col_cb, col_card = st.columns([0.05, 0.95])
            with col_cb:
                st.write("")
                is_selected = st.checkbox("", value=st.session_state.get(cb_key, True), key=cb_key)
                if is_selected:
                    selected_indices.append(idx)
            with col_card:
                st.markdown(f"""
                <div class="source-card">
                    <a class="source-title" href="{src.get('url')}" target="_blank">🔗 {src.get('title')}</a>
                    <div class="source-url">{src.get('url')}</div>
                    <div class="source-snippet">{src.get('content')}</div>
                </div>
                """, unsafe_allow_html=True)
                
        # Action Panel: Approve or Reject
        st.write("---")
        st.markdown("### Choose an Action")
        col_act1, col_act2 = st.columns(2)
        
        # Approve flow
        with col_act1:
            st.markdown("#### Option 1: Approve Selection")
            st.write("Construct a comprehensive, high-quality report based on the selected sources.")
            if st.button("✅ Approve & Summarize Selected Sources", type="primary", use_container_width=True):
                if not selected_indices:
                    st.error("⚠️ Please select at least one source to approve.")
                else:
                    selected_items = [st.session_state.pending_sources[idx] for idx in selected_indices]
                    resume_command = approval_service.build_approval_command(selected_items)
                    
                    with st.spinner("Generating final summary of approved sources..."):
                        try:
                            st.session_state.agent.invoke(resume_command, config=st.session_state.config)
                            # Clear checkbox keys for next time
                            for idx in range(len(st.session_state.pending_sources)):
                                if f"src_cb_{idx}" in st.session_state:
                                    del st.session_state[f"src_cb_{idx}"]
                            st.session_state.pending_sources = []
                            source_service.clear_sources()
                            st.success("Resumed successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error resuming agent: {e}")
                            
        # Reject flow
        with col_act2:
            st.markdown("#### Option 2: Reject & Search Again")
            st.write("Provide custom feedback to guide the research agent to re-run Tavily search.")
            feedback_text = st.text_area(
                "Search feedback / guidance for the agent:",
                placeholder="e.g., Search for recent academic papers, include news articles from 2026, or focus on fusion power cost projections...",
                key="feedback_val"
            )
            if st.button("❌ Reject & Re-Search", type="secondary", use_container_width=True):
                feedback_val = feedback_text.strip() if feedback_text.strip() else "Please search for better sources."
                resume_command = approval_service.build_rejection_command(feedback_val)
                
                with st.spinner("Submitting feedback and restarting search..."):
                    try:
                        st.session_state.agent.invoke(resume_command, config=st.session_state.config)
                        # Clear checkbox keys for next time
                        for idx in range(len(st.session_state.pending_sources)):
                            if f"src_cb_{idx}" in st.session_state:
                                del st.session_state[f"src_cb_{idx}"]
                        st.session_state.pending_sources = []
                        source_service.clear_sources()
                        st.success("Feedback submitted!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error resuming agent: {e}")
                        
# Render Chat Input when not interrupted
else:
    st.write("---")
    user_input = st.chat_input("Enter a research topic or ask follow-up questions...")
    if user_input:
        with st.spinner("Initiating research and searching..."):
            try:
                st.session_state.agent.invoke({
                    "messages": [{"role": "user", "content": user_input}]
                }, config=st.session_state.config)
                st.rerun()
            except Exception as e:
                st.error(f"Error starting research: {e}")
