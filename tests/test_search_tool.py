import pytest
from unittest.mock import MagicMock, patch
from tools.search_tool import search
from config import settings
from services import source_service

def test_search_missing_api_key():
    # Save the original key to restore later
    orig_key = settings.TAVILY_API_KEY
    settings.TAVILY_API_KEY = None
    try:
        res = search.invoke({"query": "test query"})
        assert "Error: TAVILY_API_KEY is not set" in res
    finally:
        settings.TAVILY_API_KEY = orig_key

@patch("tools.search_tool.TavilyClient")
@patch("services.source_service.set_gathered_sources")
def test_search_success(mock_set_gathered, mock_tavily_client_class):
    # Setup mock TavilyClient response
    mock_client = MagicMock()
    mock_tavily_client_class.return_value = mock_client
    
    mock_results = [
        {
            "title": "Search Result 1",
            "url": "https://example.com/1",
            "content": "Short description of first search result."
        },
        {
            "title": "Search Result 2",
            "url": "https://example.com/2",
            "content": "A very long content that needs truncation. " * 10
        }
    ]
    mock_client.search.return_value = {"results": mock_results}
    
    # Save the original key to ensure it passes check
    orig_key = settings.TAVILY_API_KEY
    if not orig_key:
        settings.TAVILY_API_KEY = "dummy-tavily-key"
        
    try:
        res = search.invoke({"query": "AI Agents"})
        
        # Verify TavilyClient was instantiated with key
        mock_tavily_client_class.assert_called_once_with(api_key=settings.TAVILY_API_KEY)
        
        # Verify search was called with correct parameters
        mock_client.search.assert_called_once_with(query="AI Agents", search_depth="advanced")
        
        # Verify results were set in source_service
        mock_set_gathered.assert_called_once_with(mock_results)
        
        # Assert format of the output string
        assert "Found potential sources:" in res
        assert "Source ID: 1" in res
        assert "Title: Search Result 1" in res
        assert "URL: https://example.com/1" in res
        assert "Brief: Short description of first search result." in res
        
        assert "Source ID: 2" in res
        assert "Title: Search Result 2" in res
        assert "URL: https://example.com/2" in res
        # Check that second source was truncated (length of snippet in output is 150 + '...')
        assert len(mock_results[1]["content"]) > 150
        assert "..." in res
        
        assert "REMINDER: You must submit your grouped sources" in res
    finally:
        settings.TAVILY_API_KEY = orig_key

@patch("tools.search_tool.TavilyClient")
def test_search_exception(mock_tavily_client_class):
    # Setup mock to raise exception
    mock_client = MagicMock()
    mock_tavily_client_class.return_value = mock_client
    mock_client.search.side_effect = Exception("API connection error")
    
    orig_key = settings.TAVILY_API_KEY
    if not orig_key:
        settings.TAVILY_API_KEY = "dummy-tavily-key"
        
    try:
        res = search.invoke({"query": "error query"})
        assert "Error running search: API connection error" in res
    finally:
        settings.TAVILY_API_KEY = orig_key
