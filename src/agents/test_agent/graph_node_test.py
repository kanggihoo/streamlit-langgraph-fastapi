from langchain_core.messages import HumanMessage, AIMessage , BaseMessage , SystemMessage 
from langgraph.graph import StateGraph, START, END , add_messages 
from langchain_core.runnables import RunnableConfig
from langchain_core.language_models import BaseChatModel

from typing import Annotated , TypedDict 
import asyncio
from langgraph.config import get_stream_writer




class ChatbotState(TypedDict):
    """Chatbot state"""
    messages : Annotated[list[BaseMessage], add_messages] = []
    metadata : str = ""


async def node1(state:ChatbotState , config:RunnableConfig)->ChatbotState:
    
    return ChatbotState(messages=["node1"] , metadata="test_metadata1")

async def node2(state:ChatbotState , config:RunnableConfig)->ChatbotState:
    return ChatbotState(messages=["node2"] , metadata="test_metadata2")

async def node3(state:ChatbotState , config:RunnableConfig)->ChatbotState:
    return ChatbotState(messages=[AIMessage(content="test_aimessage")] , metadata="test_aimessage")

async def node4(state:ChatbotState , config:RunnableConfig)->ChatbotState:
    writer = get_stream_writer()
    writer({"task": "node4 시작(시간 오 걸리는 작업)"})
    print("node4 시작(시간 오 걸리는 작ㅓ)")
    await asyncio.sleep(2)
    writer({"task": "node4 완료(시간 오 걸리는 작업)"})
    return ChatbotState(messages=[AIMessage(content="test_stream_event")] , metadata="test_time")

def build_graph():
    graph_builder = StateGraph(ChatbotState)
    graph_builder.add_node("node1", node1)
    graph_builder.add_node("node2", node2)
    graph_builder.add_node("node3", node3)
    graph_builder.add_node("node4", node4)

    graph_builder.add_edge(START, "node1")
    graph_builder.add_edge("node1", "node2")
    graph_builder.add_edge("node2", "node3")
    graph_builder.add_edge("node3", "node4")
    graph_builder.add_edge("node4", END)
    return graph_builder.compile()








