import os
import logging
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver

# Import tools and shared source store
from tools import search, approve, GATHERED_SOURCES

# Import middleware config
from middleware import hitl_middleware

# Configure logger for this module
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


def create_info_gathering_agent():
    """
    Creates and returns the Stage B/C Information Gathering Agent.
    It integrates Groq (LLM), custom tools, memory, and Human-in-the-loop.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    if not groq_api_key or not tavily_api_key:
        logger.error("[SETUP REQUIRED] Missing environment variables!")
        if not groq_api_key:
            logger.error(" - GROQ_API_KEY is not set.")
        if not tavily_api_key:
            logger.error(" - TAVILY_API_KEY is not set.")
        logger.error("\nPlease create a '.env' file in this folder with your keys:")
        logger.error("GROQ_API_KEY=your_key")
        logger.error("TAVILY_API_KEY=your_key")
        return None
        
    # Initialize Groq LLM
    model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    llm = ChatGroq(
        model=model_name,
        temperature=0.2,
        groq_api_key=groq_api_key
    )
    
    # Clean and natural System Prompt to prevent tool use conflicts on Groq
    system_prompt = (
        "You are an expert research and information gathering assistant.\n"
        "Your task is to gather high-quality sources on a user's topic and present them for approval before writing a summary.\n\n"
        "Please follow these guidelines:\n"
        "- First, search for potential sources on the user's topic.\n"
        "- Group the sources logically by category, perspective, or theme.\n"
        "- Submit the grouped list of sources to the user for approval using the 'approve' tool. You must wait for the user to approve the sources before writing any summary.\n"
        "- Once the 'approve' tool returns the approved sources' details, write a comprehensive, well-structured summary of the approved sources."
    )
    
    # Create the agent with MemorySaver and the middleware
    agent = create_agent(
        model=llm,
        tools=[search, approve],
        middleware=[hitl_middleware],
        checkpointer=MemorySaver()
    )
    
    return agent


if __name__ == "__main__":
    print("\n==========================================================")
    print("🔍 Sage B/C Research Assistant Web Application")
    print("==========================================================")
    print("To launch the research assistant using the modern Streamlit UI,")
    print("please run the following command in your terminal:")
    print("\n    streamlit run app.py\n")
    print("==========================================================\n")
