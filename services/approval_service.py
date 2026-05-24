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
