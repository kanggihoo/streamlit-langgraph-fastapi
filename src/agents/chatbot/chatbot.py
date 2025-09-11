from langchain_core.messages import HumanMessage, AIMessage , BaseMessage , SystemMessage 
from langchain_core.prompts import ChatPromptTemplate , MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END , add_messages 
from langchain_core.runnables import RunnableConfig
from langchain_core.language_models import BaseChatModel

from typing import Annotated , TypedDict 
from utils import create_message
from llm import get_llm_model 
from settings import settings 
import logging


logger = logging.getLogger(__name__)

class ChatbotState(TypedDict):
    """Chatbot state"""
    messages : Annotated[list[BaseMessage], add_messages] = []


async def chatbot(state:ChatbotState , config:RunnableConfig)->ChatbotState:
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are a helpful assistant."),
        MessagesPlaceholder(variable_name="messages"),
    ])
    model : BaseChatModel = get_llm_model(config["configurable"].get("model" , settings.DEFAULT_LLM_MODEL))
    chain = prompt | model 
    response = await chain.ainvoke({"messages":state["messages"]})
    response.additional_kwargs["type"] = "text"
    return ChatbotState(messages=[response])


graph_builder = StateGraph(ChatbotState)


graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

chatbot_graph = graph_builder.compile()
chatbot_graph.name = "chatbot"






