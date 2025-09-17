from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
import httpx
import pytest
from langchain_core.runnables import RunnableConfig
from utils.messages import create_message
from typing import Annotated , TypedDict
from langchain_core.messages import BaseMessage 
from langgraph.graph import add_messages
from langchain_core.language_models import BaseChatModel
from agents.prompt import chatbot_prompt
from langgraph.graph import StateGraph , START , END

@pytest.fixture
def user_input():
    return {
        "config": RunnableConfig(configurable={"thread_id": "test_thread_id"}),
        "input": {"messages": [create_message(message_type="human", content="test")]},
    }

class ChatbotState(TypedDict):
    """Chatbot state"""
    messages : Annotated[list[BaseMessage], add_messages] = []


async def chatbot(state:ChatbotState , config:RunnableConfig)->ChatbotState:
    
    model : BaseChatModel = ChatGoogleGenerativeAI(model = "gemini-2.0-flash-lite")
    chain = chatbot_prompt | model 
    response = await chain.ainvoke({"messages":state["messages"]})
    response = create_message(message_type="ai", content=response.content)
    return ChatbotState(messages=[response])


graph_builder = StateGraph(ChatbotState)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
chatbot_graph = graph_builder.compile()
chatbot_graph.name = "chatbot"




@pytest.mark.asyncio
async def test_chatbot_graph(user_input):

    async for stream_event in chatbot_graph.astream(**user_input, stream_mode=["updates", "messages", "custom"], subgraphs=True):
        _ , stream_mode_type , data = stream_event
        print("stream_mode_type: " , stream_mode_type)
        print("data: " , data)
    


def test_langchain():
    model = ChatGoogleGenerativeAI(model = "gemini-2.0-flash-lite")
    print(model.invoke("test"))