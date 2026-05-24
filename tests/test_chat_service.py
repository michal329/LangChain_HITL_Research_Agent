import pytest
from unittest.mock import MagicMock, patch
from services import chat_service

@patch("services.state_service.get_agent")
@patch("services.state_service.get_config")
def test_get_agent_state_empty(mock_get_config, mock_get_agent):
    mock_get_agent.return_value = None
    assert chat_service.get_agent_state() == {}

@patch("services.state_service.get_agent")
@patch("services.state_service.get_config")
def test_get_agent_state_success(mock_get_config, mock_get_agent):
    mock_agent = MagicMock()
    mock_get_agent.return_value = mock_agent
    mock_get_config.return_value = {"configurable": {"thread_id": "test-thread"}}
    
    mock_state = MagicMock()
    mock_agent.get_state.return_value = mock_state
    
    res = chat_service.get_agent_state()
    assert res == mock_state
    mock_agent.get_state.assert_called_once_with({"configurable": {"thread_id": "test-thread"}})

@patch("services.chat_service.get_agent_state")
def test_get_messages(mock_get_agent_state):
    # Case 1: no values attribute
    mock_get_agent_state.return_value = object()
    assert chat_service.get_messages() == []
    
    # Case 2: valid messages in values
    mock_state = MagicMock()
    mock_state.values = {"messages": ["msg1", "msg2"]}
    mock_get_agent_state.return_value = mock_state
    assert chat_service.get_messages() == ["msg1", "msg2"]

@patch("services.chat_service.get_agent_state")
def test_check_interrupted(mock_get_agent_state):
    # Case 1: state doesn't have values or is empty
    mock_get_agent_state.return_value = MagicMock(spec=[])
    is_int, tool_call = chat_service.check_interrupted()
    assert is_int is False
    assert tool_call is None
    
    # Case 2: state has messages but last message does not have tool calls
    mock_state1 = MagicMock()
    mock_msg1 = MagicMock(spec=[]) # No tool_calls attribute
    mock_state1.values = {"messages": [mock_msg1]}
    mock_get_agent_state.return_value = mock_state1
    is_int, tool_call = chat_service.check_interrupted()
    assert is_int is False
    assert tool_call is None
    
    # Case 3: state has messages, last message has tool calls but not for 'approve'
    mock_state2 = MagicMock()
    mock_msg2 = MagicMock()
    mock_msg2.tool_calls = [{"name": "search", "args": {"query": "AI"}}]
    mock_state2.values = {"messages": [mock_msg2]}
    mock_get_agent_state.return_value = mock_state2
    is_int, tool_call = chat_service.check_interrupted()
    assert is_int is False
    assert tool_call is None
    
    # Case 4: state has messages, last message has 'approve' tool call
    mock_state3 = MagicMock()
    mock_msg3 = MagicMock()
    mock_msg3.tool_calls = [
        {"name": "search", "args": {"query": "AI"}},
        {"name": "approve", "args": {"sources": "some sources"}}
    ]
    mock_state3.values = {"messages": [mock_msg3]}
    mock_get_agent_state.return_value = mock_state3
    is_int, tool_call = chat_service.check_interrupted()
    assert is_int is True
    assert tool_call == {"name": "approve", "args": {"sources": "some sources"}}

@patch("services.state_service.get_agent")
@patch("services.state_service.get_config")
def test_send_chat_message(mock_get_config, mock_get_agent):
    mock_agent = MagicMock()
    mock_get_agent.return_value = mock_agent
    mock_get_config.return_value = {"configurable": {"thread_id": "123"}}
    
    chat_service.send_chat_message("Hello AI")
    
    mock_agent.invoke.assert_called_once_with(
        {"messages": [{"role": "user", "content": "Hello AI"}]},
        config={"configurable": {"thread_id": "123"}}
    )

@patch("services.state_service.get_agent")
@patch("services.state_service.get_config")
def test_resume_agent(mock_get_config, mock_get_agent):
    mock_agent = MagicMock()
    mock_get_agent.return_value = mock_agent
    mock_get_config.return_value = {"configurable": {"thread_id": "123"}}
    
    mock_command = MagicMock()
    chat_service.resume_agent(mock_command)
    
    mock_agent.invoke.assert_called_once_with(
        mock_command,
        config={"configurable": {"thread_id": "123"}}
    )
