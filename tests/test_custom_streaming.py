from typing import TypedDict
from langgraph.config import get_stream_writer 
from langgraph.graph import StateGraph, START , add_messages
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage , ToolMessage , AIMessage , AIMessageChunk
from typing import Annotated , AsyncGenerator

import json
import httpx
from functools import partial
import pytest
import pytest_asyncio
from contextlib import asynccontextmanager
from src.model.type import SSETypes , ExternalLLMNames
from src.model.schema import StatusUpdate

class State(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages] 
    metadata : str = ""


client = httpx.AsyncClient() 
host = "http://3.35.85.182"
port = "6020"
path = "/llm/api/expert/single/stream"
end_point = f"{host}:{port}{path}"

async def external_streaming_llm(text:str , api_end_point:str, httpx_client)->AsyncGenerator[str, None]:
    """특정 노드에서 외부 LLM 스트리밍 결과를 반환하는 비동기 제너레이터"""
    headers = {
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
    }
    external_agent_name = "style_analyst"
    payload = {
        "user_input": text,
        "room_id": 0,
        "expert_type": external_agent_name,
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
                    match parsed["type"]:
                        case "status":
                            content = StatusUpdate(state="progress", content=parsed["message"] , task_id=external_agent_name).model_dump()
                            yield f"data: {json.dumps({'type': SSETypes.STATUS.value, 'content': content})}\n\n"
                        case "content":
                            yield f"data: {json.dumps({'type': SSETypes.TOKEN.value, 'content': parsed['chunk'] })}\n\n"
                        case "complete":
                            yield f"data: {json.dumps({'type': SSETypes.END.value, 'content': ""})}\n\n"
    except Exception as e:
        print(e)
        yield f"data: {json.dumps({'type': SSETypes.ERROR.value, 'content': 'Unexpected error' , 'agent_name': ExternalLLMNames.STYLE_ANALYST.value})}\n\n"




async def call_exteranl_streaming_llm(state:State):
    """외부 LLM 스트리밍 결과를 반환하는 노드"""
    text = state["messages"][-1].content
    writer = get_stream_writer()
    str = ""
    exteral_agent_name = "style_analyst"
    content = StatusUpdate(state="start", content=f"{exteral_agent_name} 의류 조합 분석 시작" , task_id=exteral_agent_name).model_dump()
    writer({"type": SSETypes.STATUS.value, "content": content})
    async for chunk in external_streaming_llm(text):
        chunk = chunk.strip()
        if chunk.startswith("data: "):
            data = chunk[6:]
            parsed = json.loads(data)
            match parsed["type"]:
                case SSETypes.TOKEN.value:
                    str += parsed["content"]
                    writer({"type": SSETypes.TOKEN.value, "content": parsed["content"]})

                case SSETypes.STATUS.value:
                    writer({"type": SSETypes.STATUS.value, "content": parsed["content"]})
                
                case SSETypes.END.value:
                    content = StatusUpdate(state="end", content=f"{exteral_agent_name} 분석 완료" , task_id=exteral_agent_name).model_dump()
                    writer({"type": SSETypes.STATUS.value, "content": content})
                

    return State(messages=[str] , metadata="test_metadata")


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
    # 이때 updates , custom , messages 모드에 전부 걸리지만 custom 모드에서만 토큰 단위로 되고, 나머지 messages , updates 모드는 메세지 단위로 됨
    # 여기서는 custom 모드에서 token으로 처리, 해당 노드에서 BaseMessage 형태로 반환하면 messages 모드에서도 트리거 됨.
    # 1. 굳이 맨 마지막 노드에서 BaseMessage 형태로 반환하지 않아도 될거 같고 (messages 모드에서도 트리거 되지 않음)
    # 2. custom 모드에서 dict 형태로 반환해서 이거를 SSE 방식으로 type = token 으로 처리  , content = ChatMessage 객체(type='ai' , content = "토큰 문자열" , "어떤 전문자에서 나온건지 메타정보??")
    # 3. updates 모드에서 최종 전체 문자열을 SSE 방식으로 type = "message" 으로 처리  , content = ChatMessage 객체(type='ai' , content = "최종 전체 문자열" , "어떤 전문자에서 나온건지 메타정보??")
    #===============================================================================================================
    async for chunk in graph.astream(**config, stream_mode=["updates", "custom", "messages"] , subgraphs=True):
        _ , stream_mode_type , data = chunk

        if stream_mode_type == "updates":
            for node_name , updates in data.items():
                updated_messages = updates.get("messages" , [])
                print("[updates_mode] : data =>  " , f"data: {{'type' : 'message' , 'content' : {updated_messages[-1]} }}")

        # elif stream_mode_type == "messages":
        #     msg , metadata = data
        #     if not isinstance(msg, AIMessageChunk):
        #         continue
        #     print("[messages_mode] : data =>  " , data , type(data))
        elif stream_mode_type == "custom":
            type , content = data["type"] , data["content"]
            print("[custom_mode] : data =>  " ,  f"data: {{'type' : {type} , 'content' : {content} }}")
        else:
            print("[other_mode] : data =>  " , data , type(data))
        
    
    await client.aclose()
        

