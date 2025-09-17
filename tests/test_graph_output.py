import pytest
import httpx
from src.agents.test_agent.graph_test import build_graph
from src.agents.chatbot import build_graph as build_chatbot_graph
from src.agents.test_agent.graph_node_test import build_graph as build_graph_node_test
from langchain_core.messages import AIMessageChunk
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

client = httpx.AsyncClient()
graph = build_graph(client)
chatbot_graph = build_chatbot_graph(client)
graph_node_test = build_graph_node_test()

@pytest.fixture
def user_input():
    return {
        "config": RunnableConfig(configurable={"thread_id": "1"}),
        "input": {"messages": ["test"]},
    }

@pytest.mark.asyncio
async def test_graph_output(user_input):
    async for stream_event in graph.astream(**user_input , stream_mode=["updates", "messages" , "custom"] , subgraphs=True):
        _ , stream_mode_type , data = stream_event
        
        print(stream_mode_type)
        print(data)

@pytest.mark.asyncio
async def test_chatbot_graph_output(user_input):
    print("\n")
    graph.astream_events
    async for stream_event in chatbot_graph.astream(**user_input , stream_mode=["updates", "messages" , "custom"] , subgraphs=True):
        _ , stream_mode_type , data = stream_event

        
        if stream_mode_type == "updates":
            print("stream_mode_type: " , stream_mode_type)
            print("updates: " , data)
        elif stream_mode_type == "messages":
            msg , metadata = data
            if not isinstance(msg, AIMessageChunk):
                continue
            print("stream_mode_type: " , stream_mode_type)
            print("messages: " , data)
        
@pytest.mark.asyncio
async def test_graph_node_test_output(user_input):
    memory_saver = MemorySaver()
    graph_node_test.checkpointer = memory_saver
    
    async for stream_event in graph_node_test.astream(**user_input , stream_mode=["updates", "messages" , "custom"] , subgraphs=True):
        # print(stream_event)
        _ , stream_mode_type , data = stream_event
        print("stream_mode_type: " , stream_mode_type)
        print("data: " , data)

    state = await graph_node_test.aget_state(RunnableConfig(configurable={"thread_id": "1"}))
    print("state: " , state)

         
        # if stream_mode_type == "updates":
        #     print("stream_mode_type: " , stream_mode_type)
        #     print("updates: " , data)