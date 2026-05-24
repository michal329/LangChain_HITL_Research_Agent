import streamlit as st

def inject_custom_css():
    """
    Injects custom CSS to style the Sage B/C Research Assistant with a premium visual design.
    """
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
