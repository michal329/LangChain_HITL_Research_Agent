import streamlit as st

def render_header(is_interrupted: bool, messages: list):
    """
    Renders the page titles, main headings, and current execution state pill.
    """
    col_title, col_status = st.columns([0.8, 0.2])
    
    with col_title:
        st.markdown("<h1 class='main-title'>Sage B/C Research Assistant</h1>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle'>A premium Human-in-the-Loop web research tool</p>", unsafe_allow_html=True)
        
    with col_status:
        st.write("")
        if is_interrupted:
            st.markdown("<div class='status-pill status-hitl'>🚦 Awaiting Approval</div>", unsafe_allow_html=True)
        elif len(messages) > 0:
            st.markdown("<div class='status-pill status-thinking'>🤖 Ready for Instruction</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='status-pill status-thinking'>🟢 Idle</div>", unsafe_allow_html=True)
