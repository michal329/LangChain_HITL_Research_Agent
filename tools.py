import os
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from tavily import TavilyClient

# Global store to maintain fetched source details across tool calls
GATHERED_SOURCES = []

class SearchInput(BaseModel):
    query: str = Field(description="The search query to run on Tavily.")

@tool(args_schema=SearchInput)
def search(query: str) -> str:
    """
    Search the internet using Tavily to find potential sources on a topic.
    This tool returns a list of potential sources (Title, URL, and a brief snippet).
    """
    global GATHERED_SOURCES
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        return "Error: TAVILY_API_KEY is not set in the environment."
        
    try:
        client = TavilyClient(api_key=tavily_key)
        response = client.search(query=query, search_depth="advanced")
        results = response.get("results", [])
        
        # Store full results globally in-place so references in other modules are preserved
        GATHERED_SOURCES.clear()
        GATHERED_SOURCES.extend(results)
        
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
        return f"Error running search: {e}"

class ApproveInput(BaseModel):
    sources: str = Field(description="A formatted text string listing all the gathered sources grouped by category, including their Titles and URLs.")

@tool(args_schema=ApproveInput)
def approve(sources: str) -> str:
    """
    Submit the gathered and grouped sources (as a formatted text string) for human approval.
    This tool MUST be called before writing any final summaries.
    It returns the approved sources' details.
    """
    return f"Sources approved for summary:\n\n{sources}"
