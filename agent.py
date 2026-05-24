import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch

# Load environment variables from .env file
load_dotenv()

def create_info_gathering_agent():
    """
    Creates and returns the Stage A MVP Information Gathering Agent.
    It uses Groq (LLM) and Tavily (search engine) as a tool.
    """
    # 1. Ensure required API keys are configured
    groq_api_key = os.getenv("GROQ_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    if not groq_api_key or not tavily_api_key:
        print("\n========================================================")
        print("[SETUP REQUIRED] Missing environment variables!")
        if not groq_api_key:
            print(" - GROQ_API_KEY is not set.")
        if not tavily_api_key:
            print(" - TAVILY_API_KEY is not set.")
        print("\nPlease create a '.env' file in this folder with your keys:")
        print("GROQ_API_KEY=your_key")
        print("TAVILY_API_KEY=your_key")
        print("========================================================\n")
        return None
        
    # 2. Initialize LLM (Groq)
    model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    llm = ChatGroq(
        model=model_name,
        temperature=0.3,
        groq_api_key=groq_api_key
    )
    
    # 3. Initialize Tavily Search Tool
    tavily_tool = TavilySearch()

    
    # 4. Define the System Prompt
    system_prompt = (
        "You are an expert information gathering and research assistant.\n"
        "Your primary objective is to search the internet to collect and group high-quality sources on a user-provided topic.\n\n"
        "Instructions:\n"
        "1. Identify the core concepts of the user's topic and formulate precise search queries.\n"
        "2. Use the TavilySearch tool to search the internet and gather relevant articles, papers, or documentation.\n"
        "3. Once you gather sources, group them logically into themes, categories, or perspectives.\n"
        "4. For each source, list the Title, URL, and a brief 1-sentence description of what it covers.\n"
        "5. Stop and present the grouped sources to the user for approval. Do not attempt to summarize or write a detailed analysis of the topic yet. Your only job in this phase is to collect and group the sources."
    )
    
    # 5. Create the Agent using create_agent
    agent = create_agent(
        model=llm,
        tools=[tavily_tool],
        system_prompt=system_prompt
    )
    
    return agent

if __name__ == "__main__":
    print("Initializing Stage A MVP Agent...")
    agent = create_info_gathering_agent()
    
    if agent is not None:
        print("Agent created successfully!")
        
        # Check if we can run a test execution (only if keys are set)
        if os.getenv("GROQ_API_KEY") and os.getenv("TAVILY_API_KEY"):
            topic = input("\nEnter a topic to search for (e.g., 'Latest breakthroughs in quantum computing'): ")
            if topic.strip():
                print(f"\nRunning search for topic: '{topic}'...")
                
                # Since create_agent returns a compiled graph, we invoke it with a messages state
                try:
                    response = agent.invoke({
                        "messages": [
                            {"role": "user", "content": topic}
                        ]
                    })
                    
                    # Print output
                    print("\n=== Agent Output ===")
                    if isinstance(response, dict) and "messages" in response:
                        last_message = response["messages"][-1]
                        if hasattr(last_message, "content"):
                            print(last_message.content)
                        elif isinstance(last_message, dict) and "content" in last_message:
                            print(last_message["content"])
                        else:
                            print(last_message)
                    else:
                        print(response)
                except Exception as e:
                    print(f"\nError running agent: {e}")
    else:
        print("Initialization failed due to missing configuration.")

