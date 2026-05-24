from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver

from config import settings
from tools.search_tool import search
from tools.approve_tool import approve
from middleware.hitl import hitl_middleware
from utils.logger import get_logger

logger = get_logger(__name__)

def create_info_gathering_agent():
    """
    Creates and returns the Stage B/C Information Gathering Agent.
    It integrates Groq (LLM), custom tools, memory, and Human-in-the-loop.
    """
    groq_api_key = settings.GROQ_API_KEY
    tavily_api_key = settings.TAVILY_API_KEY
    
    if not groq_api_key or not tavily_api_key:
        logger.error("[SETUP REQUIRED] Missing environment variables!")
        if not groq_api_key:
            logger.error(" - GROQ_API_KEY is not set.")
        if not tavily_api_key:
            logger.error(" - TAVILY_API_KEY is not set.")
        return None
        
    # Initialize Groq LLM
    llm = ChatGroq(
        model=settings.GROQ_MODEL,
        temperature=0.2,
        groq_api_key=groq_api_key,
        model_kwargs={"parallel_tool_calls": False}
    )
    
    # Clean and natural System Prompt to prevent tool use conflicts on Groq
    system_prompt = (
        "You are an expert research and information gathering assistant.\n"
        "Your task is to gather high-quality sources on a user's topic and present them for approval before writing a summary.\n\n"
        "Please follow these guidelines:\n"
        "- First, search for potential sources on the user's topic.\n"
        "- Group the sources logically by category, perspective, or theme.\n"
        "- Submit the grouped list of sources to the user for approval using the 'approve' tool. You must wait for the user to approve the sources before writing any summary.\n"
        "- CRITICAL: You must NEVER call the 'search' tool and the 'approve' tool in parallel or in the same turn. You must first call the 'search' tool, wait for the actual search results, and then call the 'approve' tool using ONLY those fetched sources.\n"
        "- Once the 'approve' tool returns the approved sources' details, write a comprehensive, well-structured summary of the approved sources."
    )
    
    logger.info("Initializing Agent with Groq LLM, custom search/approve tools, and HITL middleware.")
    
    # Create the agent with MemorySaver and the middleware
    agent = create_agent(
        model=llm,
        tools=[search, approve],
        system_prompt=system_prompt,
        middleware=[hitl_middleware],
        checkpointer=MemorySaver()    
        )

    

    return agent
