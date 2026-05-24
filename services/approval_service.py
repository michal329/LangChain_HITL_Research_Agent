from typing import List, Dict, Any
from langgraph.types import Command
from utils.logger import get_logger

logger = get_logger(__name__)

def format_approved_sources(selected_sources: List[Dict[str, Any]]) -> str:
    """
    Formats the list of selected sources into a structured text block for the agent.
    """
    filtered_str = ""
    for i, src in enumerate(selected_sources, 1):
        filtered_str += (
            f"Source {i}:\n"
            f"Title: {src.get('title')}\n"
            f"URL: {src.get('url')}\n"
            f"Detailed Content: {src.get('content')}\n\n"
        )
    return filtered_str

def build_approval_command(selected_sources: List[Dict[str, Any]]) -> Command:
    """
    Constructs a LangGraph resume Command for approving a selection of sources.
    """
    formatted_sources = format_approved_sources(selected_sources)
    decision = {
        "type": "edit",
        "edited_action": {
            "name": "approve",
            "args": {"sources": formatted_sources}
        }
    }
    logger.info(f"Built approval Command with {len(selected_sources)} approved sources.")
    return Command(resume={"decisions": [decision]})

def build_rejection_command(feedback: str) -> Command:
    """
    Constructs a LangGraph resume Command for rejecting proposed sources with feedback.
    """
    decision = {
        "type": "reject",
        "message": feedback
    }
    logger.info("Built rejection Command with feedback.")
    return Command(resume={"decisions": [decision]})

def get_pending_sources_for_review() -> List[Dict[str, Any]]:
    """
    Retrieves the pending sources from state_service. If empty and gathered
    sources exist, lazy-initializes the pending sources state.
    """
    from services import state_service, source_service
    pending = state_service.get_pending_sources()
    gathered = source_service.get_gathered_sources()
    if not pending and gathered:
        state_service.set_pending_sources(list(gathered))
        pending = state_service.get_pending_sources()
    return pending

def approve_sources(pending: List[Dict[str, Any]], selected_indices: List[int]) -> None:
    """
    Handles approving selected sources: compiles them, builds the resume Command,
    clears checkbox/source caches, and resumes the agent.
    """
    if not selected_indices:
        raise ValueError("Please select at least one source to approve.")

    from services import state_service, source_service, chat_service
    selected_items = [pending[idx] for idx in selected_indices]
    resume_command = build_approval_command(selected_items)
    
    state_service.clear_checkbox_states(len(pending))
    state_service.set_pending_sources([])
    source_service.clear_sources()
    
    chat_service.resume_agent(resume_command)

def reject_sources(pending: List[Dict[str, Any]], feedback_text: str) -> None:
    """
    Handles rejecting sources: builds the resume Command with feedback,
    clears checkbox/source caches, and resumes the agent.
    """
    from services import state_service, source_service, chat_service
    feedback_val = feedback_text.strip() if feedback_text.strip() else "Please search for better sources."
    resume_command = build_rejection_command(feedback_val)
    
    state_service.clear_checkbox_states(len(pending))
    state_service.set_pending_sources([])
    source_service.clear_sources()
    
    chat_service.resume_agent(resume_command)

def filter_sources(sources: List[Dict[str, Any]], query: str) -> List[tuple[int, Dict[str, Any]]]:
    """
    Filters sources by checking if the query string matches the title or content.
    Returns a list of tuples containing (original_index, source_dict).
    """
    if not query:
        return list(enumerate(sources))
        
    q = query.strip().lower()
    filtered = []
    for idx, src in enumerate(sources):
        title = src.get('title', '').lower()
        content = src.get('content', '').lower()
        if q in title or q in content:
            filtered.append((idx, src))
    return filtered


