import pytest
import pytest_asyncio
import httpx
from src.agents.external_llm import build_graph
from langchain_core.runnables import RunnableConfig
from src.model.type import SSETypes


@pytest.mark.asyncio
async def test_external_llm_streaming():
    """Test external LLM streaming functionality"""
    client = httpx.AsyncClient()
    
    try:
        graph = build_graph(client)
        
        config = {
            "config": RunnableConfig(configurable={"thread_id": "test_thread_id"}),
            "input": {"messages": ["데이트"]},
        }
        
        # ===============================================================================================================
        # custom 스트리밍 모드 테스트(updates, custom, messages 모드 테스트)
        # 이때 updates , custom , messages 모드에 전부 걸리지만 custom 모드에서만 토큰 단위로 되고, 나머지 messages , updates 모드는 메세지 단위로 됨
        # 여기서는 custom 모드에서 token으로 처리, 해당 노드에서 BaseMessage 형태로 반환하면 messages 모드에서도 트리거 됨.
        # 1. 굳이 맨 마지막 노드에서 BaseMessage 형태로 반환하지 않아도 될거 같고 (messages 모드에서도 트리거 되지 않음)
        # 2. custom 모드에서 dict 형태로 반환해서 이거를 SSE 방식으로 type = token 으로 처리  , content = ChatMessage 객체(type='ai' , content = "토큰 문자열" , "어떤 전문자에서 나온건지 메타정보??")
        # 3. updates 모드에서 최종 전체 문자열을 SSE 방식으로 type = "message" 으로 처리  , content = ChatMessage 객체(type='ai' , content = "최종 전체 문자열" , "어떤 전문자에서 나온건지 메타정보??")
        # ===============================================================================================================
        async for chunk in graph.astream(**config, stream_mode=["updates", "custom", "messages"], subgraphs=True):
            _, stream_mode_type, data = chunk

            if stream_mode_type == "updates":
                for node_name, updates in data.items():
                    updated_messages = updates.get("messages", [])
                    print("[updates_mode] : data =>  ", f"data: {{'type' : 'message' , 'content' : {updated_messages[-1]} }}")

            # elif stream_mode_type == "messages":
            #     msg , metadata = data
            #     if not isinstance(msg, AIMessageChunk):
            #         continue
            #     print("[messages_mode] : data =>  " , data , type(data))
            elif stream_mode_type == "custom":
                msg_type, content = data["type"], data["content"]
                print("[custom_mode] : data =>  ", f"data: {{'type' : {msg_type} , 'content' : {content} }}")
            else:
                print("[other_mode] : data =>  ", data, type(data))
                
    finally:
        await client.aclose()
