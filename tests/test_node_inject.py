from langchain_core.messages import HumanMessage, AIMessage , BaseMessage , SystemMessage 
from langgraph.graph import StateGraph, START, END , add_messages 
from langchain_core.runnables import RunnableConfig
from langchain_core.language_models import BaseChatModel

from typing import Annotated , TypedDict 
from llm import get_llm_model 
from settings import settings 
from agents.prompt import chatbot_prompt
import pytest
from functools import partial

class ChatbotState(TypedDict):
    """Chatbot state"""
    messages : Annotated[list[BaseMessage], add_messages] = []


async def chatbot(state:ChatbotState , config:RunnableConfig , a:int)->ChatbotState:
    print(a)
    return ChatbotState(messages=[str(a)])
    
graph = StateGraph(ChatbotState)
partial_chatbot = partial(chatbot, a=10)
graph.add_node("chatbot", partial_chatbot)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)
graph = graph.compile()
graph.name = "chatbot"


@pytest.mark.asyncio
async def test_graph():
    config = {
        "configurable": {"thread_id": "test_thread_id"},
        "input": {"messages": ["데이트"]},
    }
    result = await graph.ainvoke(**config)
    print(result)











