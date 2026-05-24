import pytest
from unittest.mock import MagicMock, patch
from services import source_service

@pytest.fixture(autouse=True)
def clean_fallback_sources():
    # Clear the fallback cache before each test
    source_service.clear_sources()
    yield
    source_service.clear_sources()

def test_fallback_storage():
    # When streamlit runtime doesn't exist (default test environment)
    assert source_service.get_gathered_sources() == []
    
    test_sources = [{"title": "Source A", "url": "https://a.com"}]
    source_service.set_gathered_sources(test_sources)
    
    assert source_service.get_gathered_sources() == test_sources
    
    source_service.clear_sources()
    assert source_service.get_gathered_sources() == []

class MockSessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
            
    def __setattr__(self, name, value):
        self[name] = value
        
    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)

@patch("streamlit.runtime.exists")
def test_streamlit_storage(mock_exists):
    mock_exists.return_value = True
    mock_session_state = MockSessionState()
    
    with patch("streamlit.session_state", mock_session_state):
        # Verify starting clean
        assert source_service.get_gathered_sources() == []
        
        # We should have "gathered_sources" initialized in session state
        assert "gathered_sources" in mock_session_state
        
        test_sources = [{"title": "Source B", "url": "https://b.com"}]
        source_service.set_gathered_sources(test_sources)
        
        # Verify it updated session state
        assert mock_session_state["gathered_sources"] == test_sources
        
        # Verify getter retrieves it
        assert source_service.get_gathered_sources() == test_sources
        
        # Verify clear operates on session state
        source_service.clear_sources()
        assert mock_session_state["gathered_sources"] == []
        assert source_service.get_gathered_sources() == []
