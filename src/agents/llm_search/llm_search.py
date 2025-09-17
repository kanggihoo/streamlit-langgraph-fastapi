# Combined External LLM and Search Agent
from langgraph.config import get_stream_writer 
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import BaseMessage
from typing import Annotated, TypedDict
from functools import partial

import json
import httpx
import logging

from model.type import SSETypes
from model.schema import StatusUpdate
from utils.messages import create_message
from agents.external_llm.utils import external_streaming_llm
from wrapper.search_wrapper import VectorSearchAPIWrapper

logger = logging.getLogger(__name__)

class LLMSearchState(TypedDict):
    """Combined LLM Search state that includes both external LLM and search functionality"""
    messages: Annotated[list[BaseMessage], add_messages] = []
    metadata: str = ""
    search_image_context: str = ""

async def external_llm_node(state: LLMSearchState, http_session: httpx.AsyncClient, api_endpoint: str) -> LLMSearchState:
    """외부 LLM 스트리밍 결과를 반환하는 노드 - 사용자 입력을 분석하여 검색 쿼리 생성"""
    text = state["messages"][-1].content
    writer = get_stream_writer()
    response_text = ""
    external_agent_name = "style_analyst"
    
    content = StatusUpdate(
        state="start", 
        content=f"{external_agent_name} 의류 조합 분석 시작", 
        task_id=external_agent_name
    ).model_dump()
    writer({"type": SSETypes.STATUS.value, "content": content})
    
    try:
        async for chunk in external_streaming_llm(text, api_endpoint, http_session):
            chunk = chunk.strip()
            if chunk.startswith("data: "):
                data = chunk[6:]
                parsed = json.loads(data)
                match parsed["type"]:
                    case SSETypes.TOKEN.value:
                        response_text += parsed["content"]
                        writer({"type": SSETypes.TOKEN.value, "content": parsed["content"]})
                    case SSETypes.STATUS.value:
                        writer({"type": SSETypes.STATUS.value, "content": parsed["content"]})
                    case SSETypes.END.value:
                        content = StatusUpdate(
                            state="end", 
                            content=f"{external_agent_name} 분석 완료", 
                            task_id=external_agent_name
                        ).model_dump()
                        writer({"type": SSETypes.STATUS.value, "content": content})
                        break
    except Exception as e:
        logger.error(f"Error in external LLM node: {e}")
        response_text = "의류 분석 중 오류가 발생했습니다."
        content = StatusUpdate(
            state="error", 
            content=f"{external_agent_name} 분석 오류", 
            task_id=external_agent_name,
            error_details=str(e)
        ).model_dump()
        writer({"type": SSETypes.STATUS.value, "content": content})

    return LLMSearchState(
        messages=[create_message(message_type="ai", content=response_text)], 
        metadata="external_llm_response"
    )

async def search_node(state: LLMSearchState, search_api_wrapper: VectorSearchAPIWrapper) -> LLMSearchState:
    """외부 LLM 결과를 기반으로 벡터 검색을 수행하는 노드"""
    writer = get_stream_writer()
    writer({"type": SSETypes.STATUS.value, "content": StatusUpdate(state="start", content="이미지 검색 시작", task_id="search").model_dump()})
    
    # 마지막 메시지(외부 LLM 결과)를 검색 쿼리로 사용
    search_query = state["messages"][-1].content
    
    try:
        response = await search_api_wrapper.search(search_query)
        
        writer({"type": SSETypes.STATUS.value, "content": StatusUpdate(state="end", content="이미지 검색 완료!", task_id="search").model_dump()})
        
        metadata = {"search_response": response}
        image_urls = [data["image_url"] for data in response.get("data", [])]
        
        # 검색 결과와 함께 메시지 생성
        search_result_message = create_message(
            message_type="ai", 
            content="이미지 검색을 진행했습니다. 관련 이미지 반환!", 
            metadata_type="image", 
            image_urls=image_urls, 
            metadata=metadata
        )
        
        return LLMSearchState(messages=[search_result_message])
        
    except Exception as e:
        logger.error(f"Error in search node: {e}")
        writer({"type": SSETypes.STATUS.value, "content": StatusUpdate(state="error", content="이미지 검색 오류", task_id="search", error_details=str(e)).model_dump()})
        
        error_message = create_message(
            message_type="ai", 
            content="이미지 검색 중 오류가 발생했습니다."
        )
        
        return LLMSearchState(messages=[error_message])

def build_graph(http_session: httpx.AsyncClient, api_endpoint: str = None) -> StateGraph:
    """Combined external LLM and search graph builder
    
    Flow: 사용자 입력 -> external_llm_node -> search_node
    - external_llm_node: 사용자 입력을 분석하여 의류 조합 추천
    - search_node: 외부 LLM 결과를 기반으로 이미지 검색 수행
    """
    if api_endpoint is None:
        host = "http://3.35.85.182"
        port = "6020"
        path = "/llm/api/expert/single/stream"
        api_endpoint = f"{host}:{port}{path}"
    
    # Create node functions with bound parameters
    external_llm_partial = partial(
        external_llm_node, 
        http_session=http_session, 
        api_endpoint=api_endpoint
    )
    
    search_partial = partial(
        search_node, 
        search_api_wrapper=VectorSearchAPIWrapper(http_session)
    )
    
    # Build the graph
    graph_builder = StateGraph(LLMSearchState)
    
    # Add nodes
    graph_builder.add_node("external_llm", external_llm_partial)
    graph_builder.add_node("search", search_partial)
    
    # Define edges: START -> external_llm -> search -> END
    graph_builder.add_edge(START, "external_llm")
    graph_builder.add_edge("external_llm", "search")
    graph_builder.add_edge("search", END)
    
    compiled_graph = graph_builder.compile()
    compiled_graph.name = "llm_search"
    
    return compiled_graph
