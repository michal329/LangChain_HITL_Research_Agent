from langchain_core.tools import tool
from pydantic import BaseModel, Field
from tavily import TavilyClient
from config import settings
from services import source_service
from utils.logger import get_logger

logger = get_logger(__name__)

class SearchInput(BaseModel):
    query: str = Field(description="The search query to run on Tavily.")

@tool(args_schema=SearchInput)
def search(query: str) -> str:
    """
    Search the internet using Tavily to find potential sources on a topic.
    This tool returns a list of potential sources (Title, URL, and a brief snippet).
    """
    tavily_key = settings.TAVILY_API_KEY
    if not tavily_key:
        logger.error("TAVILY_API_KEY is not set in the configuration.")
        return "Error: TAVILY_API_KEY is not set in the environment."
        
    try:
        logger.info(f"Running Tavily search for query: {query}")
        client = TavilyClient(api_key=tavily_key)
        response = client.search(query=query, search_depth="advanced")
        results = response.get("results", [])
        
        # Store full results in source_service
        source_service.set_gathered_sources(results)
        
        # Format metadata-only response for the agent
        output = []
        for i, res in enumerate(results, 1):
            snippet = res.get("content", "")
            if len(snippet) > 150:
                snippet = snippet[:150] + "..."
            output.append(
                f"Source ID: {i}\n"
                f"Title: {res.get('title')}\n"
                f"URL: {res.get('url')}\n"
                f"Brief: {snippet}"
            )
            
        metadata_str = "\n\n".join(output)
        return (
            f"Found potential sources:\n\n{metadata_str}\n\n"
            "REMINDER: You must submit your grouped sources as a formatted text block "
            "to the 'approve' tool before writing any summaries."
        )
    except Exception as e:
        logger.error(f"Error running search: {e}", exc_info=True)
        return f"Error running search: {e}"
