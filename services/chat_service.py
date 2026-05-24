from typing import Dict, Any, List
from services import state_service, source_service

def get_agent_state() -> Dict[str, Any]:
    """
    Retrieves the current state value of the agent graph.
    """
    agent = state_service.get_agent()
    config = state_service.get_config()
    if agent is None:
        return {}
    return agent.get_state(config)

def get_messages() -> List[Any]:
    """
    Retrieves the chronological list of message history from the agent's current thread state.
    """
    state = get_agent_state()
    return state.values.get("messages", []) if hasattr(state, "values") else []

def check_interrupted() -> tuple[bool, Any]:
    """
    Checks if the agent is currently paused/interrupted at the approve tool step.
    Returns (is_interrupted, pending_tool_call).
    """
    state = get_agent_state()
    is_interrupted = False
    pending_tool_call = None
    
    if hasattr(state, "values") and "messages" in state.values and len(state.values["messages"]) > 0:
        last_msg = state.values["messages"][-1]
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            for tool_call in last_msg.tool_calls:
                if tool_call["name"] == "approve":
                    is_interrupted = True
                    pending_tool_call = tool_call
                    break
    return is_interrupted, pending_tool_call

def send_chat_message(user_input: str):
    """
    Sends a user query to start or resume agent flow.
    """
    agent = state_service.get_agent()
    config = state_service.get_config()
    if agent:
        agent.invoke({
            "messages": [{"role": "user", "content": user_input}]
        }, config=config)

def resume_agent(command_or_resume: Any):
    """
    Resumes the agent graph with a custom resume Command.
    """
    agent = state_service.get_agent()
    config = state_service.get_config()
    if agent:
        agent.invoke(command_or_resume, config=config)
