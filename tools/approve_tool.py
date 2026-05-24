from langchain_core.tools import tool
from pydantic import BaseModel, Field

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
