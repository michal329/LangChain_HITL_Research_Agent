import streamlit as st
from config import settings
from services import state_service

def render_sidebar():
    """
    Renders the sidebar navigation, settings controller, and info guide.
    """
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="font-weight: 700; color: #6C63FF; margin-bottom: 0;">Sage B/C</h2>
            <p style="font-size: 0.9rem; opacity: 0.8;">Research Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        
        st.markdown("### ⚙️ Session Settings")
        thread_id = state_service.get_thread_id()
        st.markdown(f"**Thread ID:** `{thread_id[:8]}...`")
        
        # Check environment variable configurations
        groq_configured = "Configured ✅" if settings.GROQ_API_KEY else "Missing ❌"
        tavily_configured = "Configured ✅" if settings.TAVILY_API_KEY else "Missing ❌"
        
        st.write(f"**Groq API Key:** {groq_configured}")
        st.write(f"**Tavily API Key:** {tavily_configured}")
        
        st.write("---")
        
        # New Thread Button to clear checkpointer state
        if st.button("🔄 New Research Thread", use_container_width=True, type="secondary"):
            state_service.reset_thread()
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
