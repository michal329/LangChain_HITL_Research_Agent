import pytest
from unittest.mock import MagicMock, patch
from services import approval_service
from langgraph.types import Command

def test_format_approved_sources():
    sources = [
        {"title": "Title 1", "url": "https://url1.com", "content": "Content 1"},
        {"title": "Title 2", "url": "https://url2.com", "content": "Content 2"}
    ]
    formatted = approval_service.format_approved_sources(sources)
    expected = (
        "Source 1:\nTitle: Title 1\nURL: https://url1.com\nDetailed Content: Content 1\n\n"
        "Source 2:\nTitle: Title 2\nURL: https://url2.com\nDetailed Content: Content 2\n\n"
    )
    assert formatted == expected

def test_build_approval_command():
    sources = [{"title": "Title 1", "url": "https://url1.com", "content": "Content 1"}]
    cmd = approval_service.build_approval_command(sources)
    assert isinstance(cmd, Command)
    assert "decisions" in cmd.resume
    decision = cmd.resume["decisions"][0]
    assert decision["type"] == "edit"
    assert decision["edited_action"]["name"] == "approve"
    assert "Source 1:\nTitle: Title 1" in decision["edited_action"]["args"]["sources"]

def test_build_rejection_command():
    feedback = "Search for more technical docs."
    cmd = approval_service.build_rejection_command(feedback)
    assert isinstance(cmd, Command)
    assert "decisions" in cmd.resume
    decision = cmd.resume["decisions"][0]
    assert decision["type"] == "reject"
    assert decision["message"] == feedback

@patch("services.state_service.get_pending_sources")
@patch("services.source_service.get_gathered_sources")
@patch("services.state_service.set_pending_sources")
def test_get_pending_sources_for_review(mock_set_pending, mock_get_gathered, mock_get_pending):
    # Case 1: pending sources already exist
    mock_get_pending.return_value = [{"title": "Pending A"}]
    res = approval_service.get_pending_sources_for_review()
    assert res == [{"title": "Pending A"}]
    mock_set_pending.assert_not_called()
    
    # Case 2: pending sources empty, but gathered sources exist (lazy init)
    mock_get_pending.return_value = []
    mock_get_gathered.return_value = [{"title": "Gathered B"}]
    
    # We want state_service.get_pending_sources to return the list on the second call (inside get_pending_sources_for_review)
    mock_get_pending.side_effect = [[], [{"title": "Gathered B"}]]
    
    res2 = approval_service.get_pending_sources_for_review()
    assert res2 == [{"title": "Gathered B"}]
    mock_set_pending.assert_called_once_with([{"title": "Gathered B"}])

@patch("services.state_service.clear_checkbox_states")
@patch("services.state_service.set_pending_sources")
@patch("services.source_service.clear_sources")
@patch("services.chat_service.resume_agent")
def test_approve_sources(mock_resume, mock_clear_sources, mock_set_pending, mock_clear_checkboxes):
    pending = [
        {"title": "Source 0", "url": "https://0.com", "content": "C0"},
        {"title": "Source 1", "url": "https://1.com", "content": "C1"}
    ]
    
    # Test empty selected selection raises error
    with pytest.raises(ValueError, match="Please select at least one source"):
        approval_service.approve_sources(pending, [])
        
    # Test approval of selected indices
    approval_service.approve_sources(pending, [0])
    
    mock_clear_checkboxes.assert_called_once_with(2)
    mock_set_pending.assert_called_once_with([])
    mock_clear_sources.assert_called_once()
    
    # Verify resume was called with Command for Source 0
    mock_resume.assert_called_once()
    called_cmd = mock_resume.call_args[0][0]
    assert isinstance(called_cmd, Command)
    assert "Title: Source 0" in called_cmd.resume["decisions"][0]["edited_action"]["args"]["sources"]
    assert "Title: Source 1" not in called_cmd.resume["decisions"][0]["edited_action"]["args"]["sources"]

@patch("services.state_service.clear_checkbox_states")
@patch("services.state_service.set_pending_sources")
@patch("services.source_service.clear_sources")
@patch("services.chat_service.resume_agent")
def test_reject_sources(mock_resume, mock_clear_sources, mock_set_pending, mock_clear_checkboxes):
    pending = [{"title": "Source 0"}]
    
    # Reject with custom feedback
    approval_service.reject_sources(pending, "Try again!")
    mock_clear_checkboxes.assert_called_once_with(1)
    mock_set_pending.assert_called_once_with([])
    mock_clear_sources.assert_called_once()
    
    called_cmd = mock_resume.call_args[0][0]
    assert called_cmd.resume["decisions"][0]["type"] == "reject"
    assert called_cmd.resume["decisions"][0]["message"] == "Try again!"

def test_filter_sources():
    sources = [
        {"title": "Machine Learning in Medicine", "content": "We discuss neural networks"},
        {"title": "Deep Learning Techniques", "content": "An overview of convolutional models"},
        {"title": "Healthy Recipes", "content": "Making a salad with vegetables"}
    ]
    
    # Empty query should return all
    assert len(approval_service.filter_sources(sources, "")) == 3
    assert len(approval_service.filter_sources(sources, "   ")) == 3
    
    # Query matching title
    res1 = approval_service.filter_sources(sources, "Medicine")
    assert len(res1) == 1
    assert res1[0] == (0, sources[0])
    
    # Query matching content
    res2 = approval_service.filter_sources(sources, "convolutional")
    assert len(res2) == 1
    assert res2[0] == (1, sources[1])
    
    # Query matching both or multiple
    res3 = approval_service.filter_sources(sources, "learning")
    assert len(res3) == 2
    assert res3[0] == (0, sources[0])
    assert res3[1] == (1, sources[1])
    
    # Case insensitivity test
    res4 = approval_service.filter_sources(sources, "DeEp")
    assert len(res4) == 1
    assert res4[0] == (1, sources[1])
