import pytest
from unittest.mock import MagicMock, patch
from services import state_service

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

@pytest.fixture
def mock_streamlit_session():
    state = MockSessionState()
    with patch("streamlit.session_state", state):
        yield state

@patch("services.state_service.create_info_gathering_agent")
def test_init_session_state(mock_create_agent, mock_streamlit_session):
    mock_agent = MagicMock()
    mock_create_agent.return_value = mock_agent
    
    assert "agent" not in mock_streamlit_session
    assert "thread_id" not in mock_streamlit_session
    assert "config" not in mock_streamlit_session
    assert "pending_sources" not in mock_streamlit_session
    
    state_service.init_session_state()
    
    assert mock_streamlit_session["agent"] == mock_agent
    assert "thread_id" in mock_streamlit_session
    assert "config" in mock_streamlit_session
    assert mock_streamlit_session["pending_sources"] == []
    
    # Verify getters
    assert state_service.get_agent() == mock_agent
    assert state_service.get_thread_id() == mock_streamlit_session["thread_id"]
    assert state_service.get_config() == mock_streamlit_session["config"]
    assert state_service.get_pending_sources() == []

def test_reset_thread(mock_streamlit_session):
    # Setup initial state
    mock_streamlit_session.thread_id = "old-thread"
    mock_streamlit_session.config = {"configurable": {"thread_id": "old-thread"}}
    mock_streamlit_session.pending_sources = [{"title": "Old source"}]
    mock_streamlit_session["src_cb_0"] = True
    mock_streamlit_session["src_cb_1"] = False
    
    with patch("services.source_service.clear_sources") as mock_clear_sources:
        state_service.reset_thread()
        
        assert mock_streamlit_session.thread_id != "old-thread"
        assert mock_streamlit_session.config == {"configurable": {"thread_id": mock_streamlit_session.thread_id}}
        assert mock_streamlit_session.pending_sources == []
        mock_clear_sources.assert_called_once()
        
        # Checkbox states should be deleted
        assert "src_cb_0" not in mock_streamlit_session
        assert "src_cb_1" not in mock_streamlit_session

def test_checkbox_states(mock_streamlit_session):
    # Test lazy initialization of checkbox
    assert state_service.get_source_checkbox(0) is True
    assert mock_streamlit_session["src_cb_0"] is True
    
    # Test setting checkbox
    state_service.set_source_checkbox(0, False)
    assert state_service.get_source_checkbox(0) is False
    assert mock_streamlit_session["src_cb_0"] is False
    
    # Test batch operations
    state_service.select_all_checkboxes(3)
    assert mock_streamlit_session["src_cb_0"] is True
    assert mock_streamlit_session["src_cb_1"] is True
    assert mock_streamlit_session["src_cb_2"] is True
    
    state_service.deselect_all_checkboxes(3)
    assert mock_streamlit_session["src_cb_0"] is False
    assert mock_streamlit_session["src_cb_1"] is False
    assert mock_streamlit_session["src_cb_2"] is False
    
    # Test initialization
    state_service.initialize_checkbox_states(3)
    # They should remain False if already in session state
    assert mock_streamlit_session["src_cb_0"] is False
    
    # Test clear
    state_service.clear_checkbox_states(3)
    assert "src_cb_0" not in mock_streamlit_session
    assert "src_cb_1" not in mock_streamlit_session
    assert "src_cb_2" not in mock_streamlit_session
