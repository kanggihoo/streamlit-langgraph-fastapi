from langgraph.graph.state import CompiledStateGraph
import httpx
from typing import Callable

from .chatbot import build_graph as build_chatbot_graph
from .product import build_graph as build_product_graph
from .search import build_graph as build_search_graph
from .external_llm import build_graph as build_external_llm_graph
from .llm_search import build_graph as build_llm_search_graph

DEFAULT_AGENT_NAME = "search"

agents = {
    'chatbot' : build_chatbot_graph,
    'product' : build_product_graph,
    'search' : build_search_graph,
    "external_llm" : build_external_llm_graph,
    "llm_search" : build_llm_search_graph,
}

def get_graph_builder(agent_name:str)->Callable[[httpx.AsyncClient | None],CompiledStateGraph]:
    "에이전트 이름으로 그래프 빌더 factory function 반환"
    if agent_name not in agents:
        raise ValueError(f"Agent {agent_name} not found")
    return agents[agent_name]

# def get_agent(agent_name:str)->CompiledStateGraph:
#     """Get an agent by name"""
#     if agent_name not in agents:
#         raise ValueError(f"Agent {agent_name} not found")
#     return agents[agent_name]


def get_all_agent_info()->list[str]:
    "이용 가능한 에이전트 이름 목록 반환"
    return [k for k,v in agents.items() ]


__all__ = [
    "get_graph_builder",
    "get_all_agent_info",
    "DEFAULT_AGENT_NAME",
]