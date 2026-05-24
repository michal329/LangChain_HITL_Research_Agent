import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

def validate_config() -> bool:
    """
    Checks if critical keys are configured.
    """
    return bool(GROQ_API_KEY and TAVILY_API_KEY)
