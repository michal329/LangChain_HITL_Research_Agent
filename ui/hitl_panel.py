import streamlit as st
from services import state_service, source_service, approval_service, chat_service

def render_hitl_panel():
    """
    Renders the verification list cards with checkboxes, text filters,
    and Option 1 (Approve) / Option 2 (Reject) command controls.
    """
    pending = state_service.get_pending_sources()
    gathered = source_service.get_gathered_sources()
    
    # Lazy initialize pending list in session state from store service
    if not pending and gathered:
        state_service.set_pending_sources(list(gathered))
        pending = state_service.get_pending_sources()
        
    if pending:
        st.write("---")
        st.markdown("## 🔍 Gathered Sources Verification")
        st.info("Please choose which sources to keep for the final summary. You can select/deselect individual sources, search or filter through them, and approve them, or reject and prompt the agent to search again.")
        
        # Initialize checkbox states
        for idx in range(len(pending)):
            state_service.get_source_checkbox(idx)
            
        # Search & Filter box for sources
        filter_query = st.text_input("🔍 Filter sources by title or brief...", "")
        
        # Select All / Deselect All quick buttons
        col_s1, col_s2 = st.columns([0.15, 0.85])
        with col_s1:
            if st.button("Select All", use_container_width=True):
                state_service.select_all_checkboxes(len(pending))
                st.rerun()
        with col_s2:
            if st.button("Deselect All", use_container_width=True):
                state_service.deselect_all_checkboxes(len(pending))
                st.rerun()
                
        # Render list of source cards with checkboxes
        selected_indices = []
        for idx, src in enumerate(pending):
            # Apply user filter query
            if filter_query:
                q = filter_query.lower()
                if q not in src.get('title', '').lower() and q not in src.get('content', '').lower():
                    continue
            
            is_checked = state_service.get_source_checkbox(idx)
            col_cb, col_card = st.columns([0.05, 0.95])
            with col_cb:
                st.write("")
                is_selected = st.checkbox("", value=is_checked, key=f"src_cb_{idx}")
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
                    selected_items = [pending[idx] for idx in selected_indices]
                    resume_command = approval_service.build_approval_command(selected_items)
                    
                    with st.spinner("Generating final summary of approved sources..."):
                        try:
                            state_service.clear_checkbox_states(len(pending))
                            state_service.set_pending_sources([])
                            source_service.clear_sources()
                            
                            chat_service.resume_agent(resume_command)
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
                        state_service.clear_checkbox_states(len(pending))
                        state_service.set_pending_sources([])
                        source_service.clear_sources()

                        chat_service.resume_agent(resume_command)
                        st.success("Feedback submitted!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error resuming agent: {e}")
