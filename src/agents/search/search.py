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
from aws import S3Manager
import logging

'''
단순히 그래프 호출시 => llm => stat에 llm 결과 넣고, => 해당 llm 쿼리문을 그래도 벡터 검색 => 
반환된 검색 결과를 state혹은 AIMessage 형태로 반환(이때 지금은 검색된 url을 s3key 형태로 parsing 해서 넣기)

#CHECK :  벡터 서치의 모든 결과를 그대로 다 AIMessage의 additional_kwargs에 넣어 주어야 하나? 

'''
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

async def search(state:ChatbotState , config:RunnableConfig)->ChatbotState:
    return ChatbotState(messages=[response])


graph_builder = StateGraph(ChatbotState)


graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

chatbot_graph = graph_builder.compile()
chatbot_graph.name = "chatbot"






