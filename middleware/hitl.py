from langchain.agents.middleware import HumanInTheLoopMiddleware

# Configure HumanInTheLoopMiddleware to pause on `approve` tool
hitl_middleware = HumanInTheLoopMiddleware(
    interrupt_on={"approve": True}
)
