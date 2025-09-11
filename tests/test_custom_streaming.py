from typing import TypedDict
from langgraph.config import get_stream_writer 
from langgraph.graph import StateGraph, START , add_messages
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage , ToolMessage , AIMessage
from typing import Annotated , AsyncGenerator

import json
import httpx
from functools import partial
import pytest
import pytest_asyncio
from contextlib import asynccontextmanager
from src.model.type import SSETypes , ExternalLLMNames


class State(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages] 


client = httpx.AsyncClient() 
host = "http://3.35.85.182"
port = "6020"
path = "/llm/api/expert/single/stream"
end_point = f"{host}:{port}{path}"

async def external_streaming_llm(text:str , api_end_point:str, httpx_client)->AsyncGenerator[str, None]:
    """Call external streaming LLM API and return SSE response"""
    headers = {
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
    }
    
    payload = {
        "user_input": text,
        "room_id": 0,
        "expert_type": "style_analyst",
        "user_profile": {
            "additionalProp1": {}
        },
        "context_info": {
            "additionalProp1": {}
        },
        "json_data": {
            "additionalProp1": {}
        }
    }
    
    try:
        async with httpx_client.stream(
            "POST", 
            api_end_point, 
            headers=headers, 
            json=payload
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    data = line[6:]
                    parsed = json.loads(data)
                    if parsed["type"] =="status":
                        continue
                    match parsed["type"]:
                        case "content":
                            yield f"data: {json.dumps({'type': SSETypes.TOKEN.value, 'content': parsed['chunk'] })}\n\n"
                        case "complete":
                            yield f"data: {json.dumps({'type': SSETypes.END.value, 'content': parsed['data'] , 'agent_name': ExternalLLMNames.STYLE_ANALYST.value})}\n\n"
    except Exception as e:
        print(e)
        yield f"data: {json.dumps({'type': SSETypes.ERROR.value, 'content': 'Unexpected error' , 'agent_name': ExternalLLMNames.STYLE_ANALYST.value})}\n\n"




async def call_exteranl_streaming_llm(state:State):
    text = state["messages"][-1].content
    writer = get_stream_writer()
    str = ""
    exteral_agent_name = None
    async for chunk in external_streaming_llm(text):
        chunk = chunk.strip()
        if chunk.startswith("data: "):
            data = chunk[6:]
            parsed = json.loads(data)
            if parsed["type"] == SSETypes.TOKEN.value:
                str += parsed["content"]
                #TODO: langgraph의 custom 스트리밍시 전송할 데이터 형식을 정해주면될듯 
                writer({"type": SSETypes.TOKEN.value, "content": parsed["content"]})
            elif parsed["type"] == SSETypes.END.value:
                exteral_agent_name = parsed["agent_name"]

    print("외부 LLM 스트리밍 완료")
    return State(messages=[AIMessage(content = str , additional_kwargs={"agent_name": exteral_agent_name})])


external_streaming_llm = partial(external_streaming_llm, httpx_client=client , api_end_point=end_point)

graph_builder = StateGraph(State)
graph_builder.add_node("test_streaming_llm", call_exteranl_streaming_llm) # 노드 추가
graph_builder.add_edge(START, "test_streaming_llm") # 시작점에서 노드로 엣지 추가
graph = graph_builder.compile() # 그래프 컴파일
graph




@pytest.mark.asyncio
async def test_custom_streaming():
    config = {
        "configurable": {"thread_id": "test_thread_id"},
        "input": {"messages": ["데이트"]},

    }
    #===============================================================================================================
    # custom 스트리밍 모드 테스트(updates, custom, messages 모드 테스트)
    # 이때 updates , custom , messages 모드 다 걸리네? 
    #===============================================================================================================
    async for chunk in graph.astream(**config, stream_mode=["updates", "custom", "messages"] , subgraphs=True):
        _ , stream_mode_type , data = chunk
        if stream_mode_type == "custom":
            print("stream_mode_type: custom" , data)
        else:
            print("stream_mode_type: " , stream_mode_type , data)
    
    await client.aclose()
        

