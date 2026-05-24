from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)

# Module-level storage encapsulating GATHERED_SOURCES
_GATHERED_SOURCES: List[Dict[str, Any]] = []

def get_gathered_sources() -> List[Dict[str, Any]]:
    """
    Retrieves the current cached list of gathered sources.
    """
    return _GATHERED_SOURCES

def set_gathered_sources(sources: List[Dict[str, Any]]) -> None:
    """
    Clears the existing sources and updates the cache in-place with new search results.
    """
    global _GATHERED_SOURCES
    _GATHERED_SOURCES.clear()
    _GATHERED_SOURCES.extend(sources)
    logger.info(f"Updated source store with {len(sources)} sources.")

def clear_sources() -> None:
    """
    Clears the source store cache.
    """
    global _GATHERED_SOURCES
    _GATHERED_SOURCES.clear()
    logger.info("Cleared source store cache.")
