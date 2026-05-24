import streamlit as st
from services import state_service, chat_service
from ui.styles import inject_custom_css
from ui.sidebar import render_sidebar
from ui.header import render_header
from ui.chat import render_chat_history, render_chat_input
from ui.hitl_panel import render_hitl_panel

# 1. Initialize session states
state_service.init_session_state()

# 2. Inject premium design CSS styling
inject_custom_css()

# 3. Render left panel menu
render_sidebar()

# 4. Handle pre-validation on agent presence
agent = state_service.get_agent()
if agent is None:
    st.error("🔑 API Keys Missing or Configuration Failed!")
    st.markdown("""
    Please configure your API keys in the `.env` file in the project root:
    ```env
    GROQ_API_KEY=your_groq_api_key
    TAVILY_API_KEY=your_tavily_api_key
    ```
    """)
    st.stop()

# 5. Retrieve current execution status
is_interrupted, pending_tool_call = chat_service.check_interrupted()
messages = chat_service.get_messages()

# 6. Render main page headers & status indicators
render_header(is_interrupted, messages)

# 7. Render conversation history bubbles
render_chat_history(messages)

# 8. Render interactive Human-in-the-Loop review board OR regular chat text inputs
if is_interrupted and pending_tool_call:
    render_hitl_panel()
else:
    render_chat_input()
