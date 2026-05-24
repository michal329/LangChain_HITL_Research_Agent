import os
import re
import logging
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

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

def log_agent_messages(response):
    """Utility to log the entire message history and tool calls."""
    if isinstance(response, dict) and "messages" in response:
        for i, msg in enumerate(response["messages"]):
            role = "User"
            if hasattr(msg, "type"):
                role = msg.type.capitalize()
            elif isinstance(msg, dict) and "role" in msg:
                role = msg["role"].capitalize()
                
            content = msg.content if hasattr(msg, "content") else (msg.get("content", "") if isinstance(msg, dict) else str(msg))
            
            logger.info(f"\n--- [{role} Message {i+1}] ---")
            logger.info(content)
            
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                logger.info(f"Proposing Tool Calls: {msg.tool_calls}")
    else:
        logger.info(response)

if __name__ == "__main__":
    # Configure logging to write cleanly to standard output when running this script directly
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    logger.info("Initializing Stage B/C Agent with Memory & Human-in-the-loop...")
    agent = create_info_gathering_agent()
    
    if agent is not None:
        logger.info("Agent created successfully!")
        
        # Check if environment is ready
        if os.getenv("GROQ_API_KEY") and os.getenv("TAVILY_API_KEY"):
            topic = input("\nEnter a topic to search for (e.g., 'Recent advances in fusion energy'): ")
            if topic.strip():
                logger.info(f"\n[1/3] Starting research on topic: '{topic}'...")
                
                # Config with a thread_id for persistence/checkpointing
                config = {"configurable": {"thread_id": "info_gathering_thread"}}
                
                # First invocation
                result = agent.invoke({
                    "messages": [
                        {"role": "user", "content": topic}
                    ]
                }, config=config)
                
                # Get current state to verify if interrupted
                state = agent.get_state(config)
                
                # Check for interrupts
                is_interrupted = False
                pending_tool_call = None
                
                # Inspect messages to find pending tool call
                if "messages" in state.values and len(state.values["messages"]) > 0:
                    last_msg = state.values["messages"][-1]
                    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                        for tool_call in last_msg.tool_calls:
                            if tool_call["name"] == "approve":
                                is_interrupted = True
                                pending_tool_call = tool_call
                                break
                
                if is_interrupted and pending_tool_call:
                    logger.info("⚠️  [HUMAN IN THE LOOP INTERRUPT]")
                    logger.info("The agent has gathered the following sources for your approval:")
                    
                    args = pending_tool_call.get("args", {}) if isinstance(pending_tool_call, dict) else getattr(pending_tool_call, "args", {})
                    sources_str = args.get("sources", "")
                    
                    # Print the sources proposed by the agent
                    logger.info(sources_str)
                    logger.info("-" * 50)
                    
                    # Present the actual items from GATHERED_SOURCES to let the user select by ID
                    if GATHERED_SOURCES:
                        logger.info("\nFetched search results available for selection:")
                        for i, src in enumerate(GATHERED_SOURCES, 1):
                            logger.info(f"{i}. [{src.get('title')}]")
                            logger.info(f"   URL: {src.get('url')}")
                            logger.info(f"   Snippet: {src.get('content')[:100]}...")
                            logger.info("-" * 30)
                            
                    logger.info("\nOptions:")
                    logger.info(" - [Press Enter] to approve ALL sources.")
                    logger.info(" - Enter comma-separated indices to KEEP (e.g., '1,3' to keep only those).")
                    logger.info(" - Type 'r' to reject and ask the agent to search again with feedback.")
                    
                    user_input = input("\nYour decision: ").strip()
                    
                    if user_input.lower() == 'r':
                        feedback = input("Provide feedback/guidance for the search: ")
                        decision = {
                            "type": "reject",
                            "message": feedback if feedback.strip() else "Please search for better sources."
                        }
                        logger.info("\n[2/3] Resubmitting search with feedback...")
                        resume_command = Command(resume={"decisions": [decision]})
                        result = agent.invoke(resume_command, config=config)
                        
                        # Print the final result after rejection feedback
                        logger.info("\n=== Agent Output ===")
                        log_agent_messages(result)
                        
                    else:
                        # Process approved/filtered list
                        filtered_str = ""
                        if user_input and GATHERED_SOURCES:
                            try:
                                indices = [int(x.strip()) - 1 for x in user_input.split(",") if x.strip().isdigit()]
                                selected_items = [GATHERED_SOURCES[idx] for idx in indices if 0 <= idx < len(GATHERED_SOURCES)]
                                for i, src in enumerate(selected_items, 1):
                                    filtered_str += (
                                        f"Source {i}:\n"
                                        f"Title: {src.get('title')}\n"
                                        f"URL: {src.get('url')}\n"
                                        f"Detailed Content: {src.get('content')}\n\n"
                                    )
                            except Exception as e:
                                logger.error(f"Invalid input selection. Defaulting to all sources. Error: {e}")
                                filtered_str = ""
                                
                        # Default to passing all gathered sources with their full content if no filtering is applied
                        if not filtered_str and GATHERED_SOURCES:
                            for i, src in enumerate(GATHERED_SOURCES, 1):
                                filtered_str += (
                                    f"Source {i}:\n"
                                    f"Title: {src.get('title')}\n"
                                    f"URL: {src.get('url')}\n"
                                    f"Detailed Content: {src.get('content')}\n\n"
                                )
                                
                        if not filtered_str:
                            logger.warning("No sources selected. Cancelling.")
                        else:
                            logger.info(f"\n[2/3] Approving sources...")
                            
                            # Resume by editing the string argument to contain the detailed source content
                            decision = {
                                "type": "edit",
                                "edited_action": {
                                    "name": "approve",
                                    "args": {"sources": filtered_str}
                                }
                            }
                            resume_command = Command(resume={"decisions": [decision]})
                            
                            logger.info("\n[3/3] Generating final summary of approved sources...")
                            result = agent.invoke(resume_command, config=config)
                            
                            logger.info("\n=== Agent Output ===")
                            log_agent_messages(result)
                else:
                    logger.info("\nAgent finished without interruption.")
                    logger.info("\n=== Agent Output ===")
                    log_agent_messages(result)
        else:
            logger.error("\nPlease configure GROQ_API_KEY and TAVILY_API_KEY in a .env file to run the agent.")
    else:
        logger.error("Initialization failed due to missing configuration.")
