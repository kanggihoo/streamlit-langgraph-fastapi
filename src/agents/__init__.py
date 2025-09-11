from langgraph.graph.state import CompiledStateGraph
from .chatbot import chatbot_graph
from .product import product_agent


DEFAULT_AGENT_NAME = "product"

agents = {
    'chatbot' : chatbot_graph,
    'product' : product_agent,
}


def get_agent(agent_name:str)->CompiledStateGraph:
    """Get an agent by name"""
    if agent_name not in agents:
        raise ValueError(f"Agent {agent_name} not found")
    return agents[agent_name]


def get_all_agent_info()->list[str]:
    return [k for k,v in agents.items() ]


__all__ = [
    "get_agent",
    "get_all_agent_info",
    "DEFAULT_AGENT_NAME",
]