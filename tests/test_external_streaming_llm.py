from typing import TypedDict
from langgraph.config import get_stream_writer 
from langgraph.graph import StateGraph, START , add_messages
from langchain_core.messages import BaseMessage , ToolMessage , AIMessage
from typing import Annotated 
import httpx 
import pytest
import pytest_asyncio
import json
# import asyncio
# import random 
# import time


@pytest_asyncio.fixture
async def httpx_client():
    """pytest fixture for httpx async client"""
    async with httpx.AsyncClient() as client:
        yield client

@pytest.fixture
def api_end_point():
    #  post http://3.35.85.182:6020/llm/api/expert/single/stream
    host = "http://3.35.85.182"
    port = "6020"
    path = "/llm/api/expert/single/stream"
    return f"{host}:{port}{path}"

'''
{'type': 'status', 'message': 'S3에서 착장 검색 중...', 'step': 2}
{'type': 'status', 'message': 'S3 매칭 성공: 7개 착장 발견', 'step': 7}
{'type': 'status', 'message': '최종 착장 선택: 49bb3d7ef7dfbe3f087842dfc1b81e43', 'step': 9}
{'type': 'status', 'message': '전문가 분석 시작...', 'step': 11}
{'type': 'status', 'message': 'Claude API 호출 중...', 'step': 12}
{'type': 'content', 'chunk': '블'}
{'type': 'content', 'chunk': '랙 '}
{'type': 'content', 'chunk': '폴로 셔'}
{'type': 'content', 'chunk': '츠에 베'}
{'type': 'content', 'chunk': '이지 와이'}
{'type': 'content', 'chunk': '드 슬'}
{'type': 'content', 'chunk': '랙스가'}
{'type': 'content', 'chunk': ' 잘 어'}
{'type': 'content', 'chunk': '울려. '}
{'type': 'content', 'chunk': '슬림한'}
{'type': 'content', 'chunk': '폴로 셔'}
{'type': 'content', 'chunk': '츠를'}
{'type': 'content', 'chunk': '앞'}
{'type': 'content', 'chunk': '쪽만'}
{'type': 'content', 'chunk': ' 살짝 '}
{'type': 'content', 'chunk': '넣어서'}
{'type': 'content', 'chunk': ' 세'}
{'type': 'content', 'chunk': '련된 실'}
{'type': 'content', 'chunk': '루엣을 '}
{'type': 'content', 'chunk': '만'}
{'type': 'content', 'chunk': '들 '}
{'type': 'content', 'chunk': '수 있어'}
{'type': 'content', 'chunk': '.'}
{'type': 'content', 'chunk': ' 시'}
{'type': 'content', 'chunk': '원'}
{'type': 'content', 'chunk': '한 린'}
{'type': 'content', 'chunk': '넨 혼'}
{'type': 'content', 'chunk': '방 '}
{'type': 'content', 'chunk': '슬랙스는'}
{'type': 'content', 'chunk': ' 여름'}
{'type': 'content', 'chunk': '데이트에 '}
{'type': 'content', 'chunk': '딱이'}
{'type': 'content', 'chunk': '고, 브라'}
{'type': 'content', 'chunk': '운 로'}
{'type': 'content', 'chunk': '퍼로'}
{'type': 'content', 'chunk': ' 포인'}
{'type': 'content', 'chunk': '트를 줘'}
{'type': 'content', 'chunk': '도'}
{'type': 'content', 'chunk': ' 좋아.'}
{'type': 'content', 'chunk': ' 블'}
{'type': 'content', 'chunk': '랙 벨'}
{'type': 'content', 'chunk': '트로'}
{'type': 'content', 'chunk': ' 허리라'}
{'type': 'content', 'chunk': '인을 강조'}
{'type': 'content', 'chunk': '하면 '}
{'type': 'content', 'chunk': '더 세련되'}
{'type': 'content', 'chunk': '어'}
{'type': 'content', 'chunk': ' 보일 수'}
{'type': 'content', 'chunk': ' 있어. '}
{'type': 'content', 'chunk': '발'}
{'type': 'content', 'chunk': '목이'}
{'type': 'content', 'chunk': ' 살'}
{'type': 'content', 'chunk': '짝 보'}
{'type': 'content', 'chunk': '이는 길이'}
{'type': 'content', 'chunk': '감'}
{'type': 'content', 'chunk': '이'}
{'type': 'content', 'chunk': '라'}
{'type': 'content', 'chunk': '키'}
{'type': 'content', 'chunk': '가 더 커'}
{'type': 'content', 'chunk': ' 보이는 '}
{'type': 'content', 'chunk': '효과도 있'}
{'type': 'content', 'chunk': '지'}
{'type': 'content', 'chunk': '. 블'}
{'type': 'content', 'chunk': '랙 토트'}
{'type': 'content', 'chunk': '백으로 마'}
{'type': 'content', 'chunk': '무리하면 '}
{'type': 'content', 'chunk': '격'}
{'type': 'content', 'chunk': '식과'}
{'type': 'content', 'chunk': ' 트'}
{'type': 'content', 'chunk': '렌디함'}
{'type': 'content', 'chunk': '을 동시에'}
{'type': 'content', 'chunk': ' 살'}
{'type': 'content', 'chunk': '릴 수 '}
{'type': 'content', 'chunk': '있어.'}
{'type': 'status', 'message': '전문가 분석 완료', 'step': 13}
{'type': 'complete', 'data': {'matched_outfit': {'filename': '49bb3d7ef7dfbe3f087842dfc1b81e43', 'score': 0.7100000000000001, 's3_url': 'https://thefirsttake-combination.s3.ap-northeast-2.amazonaws.com/json/49bb3d7ef7dfbe3f087842dfc1b81e43.json', 'situations': ['소개팅', '비즈니스', '데이트', '면접', '직장/오피스', '첫 만남/소개팅']}, 'total_matches': 7, 'search_method': 'index', 'source': 's3_json_stream'}}

=> 완료일때 type이 status랑 complete 두개 있는거 같은데 
=> type "complete" 인 경우 data 필드에 있는게 front쪽에 전달할 내용들인건지? 
'''


@pytest.mark.asyncio
async def test_call_exteranl_streaming_llm(api_end_point, httpx_client):
    """Call external streaming LLM API and return SSE response"""
    print(httpx_client)
    headers = {
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
    }
    
    payload = {
        "user_input": "데이트",
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
            
            # Process SSE stream
            async for line in response.aiter_lines():
                if line.strip():
                    data = line[6:]
                    parsed = json.loads(data)
                    if parsed["type"] =="status":
                        continue

                    match parsed["type"]:
                        case "content":
                            print(parsed["chunk"] , end =" " , flush=True)
                        case "complete":
                            print("\n")
                            print(parsed["data"])
    except Exception as e:
        print(e)





