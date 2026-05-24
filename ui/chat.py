import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from services import chat_service

def render_chat_history(messages: list):
    """
    Renders user speech bubbles, assistant answers, and expanding status tools.
    """
    if not messages:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem;">
            <h2 style="font-weight: 600; opacity: 0.8;">Welcome! Ready to conduct extensive web research?</h2>
            <p style="font-size: 1.1rem; opacity: 0.7; max-width: 600px; margin: 1rem auto;">
                Enter a topic below to initiate web search, retrieve metadata, curate list of sources, and compile detailed reports.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

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

def render_chat_input():
    """
    Renders the central text chat input and initiates graph execution on submit.
    """
    st.write("---")
    user_input = st.chat_input("Enter a research topic or ask follow-up questions...")
    if user_input:
        with st.spinner("Initiating research and searching..."):
            try:
                chat_service.send_chat_message(user_input)
                st.rerun()
            except Exception as e:
                st.error(f"Error starting research: {e}")
