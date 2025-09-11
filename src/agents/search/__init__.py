from .search import search_graph
from langgraph.graph.state import CompiledStateGraph

agents = {
    'search': search_graph
}

def get_agent(agent_name:str)->CompiledStateGraph:
    if agent_name not in agents:
        raise ValueError(f"Agent {agent_name} not found")
    return agents[agent_name]