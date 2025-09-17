import pytest
import httpx
from src.agents.test_agent.graph_test import build_graph
from src.agents.chatbot import build_graph as build_chatbot_graph
from langchain_core.messages import AIMessageChunk

client = httpx.AsyncClient()
graph = build_graph(client)
chatbot_graph = build_chatbot_graph(client)

@pytest.fixture
def user_input():
    return {
        "configurable": {"thread_id": "test_thread_id"},
        "input": {"messages": ["test"]},
    }

@pytest.mark.asyncio
async def test_graph_output(user_input):
    async for stream_event in graph.astream(**user_input , stream_mode=["updates", "messages" , "custom"] , subgraphs=True):
        _ , stream_mode_type , data = stream_event
        
        print(stream_mode_type)
        print(data)

@pytest.mark.asyncio
async def test_stream_event(user_input):
    print("\n")
    graph.astream_events
    async for stream_event in chatbot_graph.astream_events(**user_input):
        event , data , tags , metadata , parent_ids = stream_event["event"] , stream_event["data"] , stream_event["tags"] , stream_event["metadata"] , stream_event["parent_ids"]
        print("event: " , event)
        print("data: " , data)
        # print(tags)
        
        # _ , stream_mode_type , data = stream_event

         
        # if stream_mode_type == "updates":
        #     print("stream_mode_type: " , stream_mode_type)
        #     print("updates: " , data)
        # elif stream_mode_type == "messages":
        #     msg , metadata = data
        #     if not isinstance(msg, AIMessageChunk):
        #         continue
        #     print("stream_mode_type: " , stream_mode_type)
        #     print("messages: " , data)
        
        