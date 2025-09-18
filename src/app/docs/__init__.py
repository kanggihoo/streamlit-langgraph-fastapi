from typing import Any
import json
from fastapi import status
from agents import get_all_agent_info
from model.schema import ErrorResponse


AGENTS = get_all_agent_info()
def get_agents_openapi_examples() -> dict[str, Any]:
    result = {}
    for agent in AGENTS:
        result[agent] = {
            "summary": f"{agent} 에이전트",
            "value": agent,
        }
    return result

def sse_response_example() -> dict[str, Any]:
    """
    FastAPI 문서에 포함될 상세한 SSE 응답 예시를 생성합니다.
    
    이 함수는 프로젝트 워크플로우 문서에 기술된 모든 가능한 이벤트 타입(`status`, `token`, `message`, `error`, `[DONE]`)에 대한
    포괄적인 예시를 제공합니다.
    """
    # Example data for different SSE event types
    status_example = {
        "type": "status",
        "content": {
            "task_id": "some_task_id",
            "state": "progress",
            "content": "처리 중...",
            "error_details": None,
        },
    }
    token_example = {"type": "token", "content": "안녕하세요"}
    message_example = {
        "type": "message",
        "content": {
            "type": "ai",
            "content": "최종 AI 메시지입니다.",
            "tool_calls": [],
            "tool_call_id": None,
            "run_id": "some_run_id",
            "response_metadata": {},
            "additional_kwargs": {},
            "custom_data": {}
        },
    }
    error_example = {"type": "error", "content": "오류가 발생했습니다."}
    end_example = {"type": "[DONE]", "content": ""}

    # Combining examples into a single stream string
    sse_stream_example = (
        f"data: {json.dumps(status_example)}\n\n"
        f"data: {json.dumps(token_example)}\n\n"
        f"data: {json.dumps(message_example)}\n\n"
        f'data: {json.dumps(end_example)}\n\n'
    )

    return {
        status.HTTP_200_OK: {
            "description": "성공적인 SSE 스트림 응답입니다. 스트림은 여러 이벤트 타입으로 구성되며, 각 이벤트는 'data: ' 접두사가 붙은 JSON 문자열 형식입니다. 스트림은 `[DONE]` 이벤트로 종료됩니다.",
            "content": {
                "text/event-stream": {
                    "schema": {"type": "string"},
                    "examples": {
                        "전체 스트림": {
                            "summary": "전체 SSE 스트림에 대한 예시입니다.",
                            "value": sse_stream_example,
                        },
                        "토큰 이벤트": {
                            "summary": "LLM 응답을 토큰 단위로 스트리밍하기 위한 'token' 이벤트입니다. 'content'는 문자열입니다.",
                            "value": f"data: {json.dumps(token_example)}\n\n",
                        },
                        "상태 이벤트": {
                            "summary": "백그라운드 작업의 진행 상태를 보고하기 위한 'status' 이벤트입니다. 'content'는 StatusUpdate 객체입니다.",
                            "value": f"data: {json.dumps(status_example)}\n\n",
                        },
                        "메시지 이벤트": {
                            "summary": "최종 구조화된 메시지를 보내기 위한 'message' 이벤트입니다. 'content'는 ChatMessage 객체입니다.",
                            "value": f"data: {json.dumps(message_example)}\n\n",
                        },
                        "종료 이벤트": {
                            "summary": "스트림의 끝을 알리는 '[DONE]' 이벤트입니다.",
                            "value": f"data: {json.dumps(end_example)}\n\n",
                        },
                    },
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR:
            {
                "description": "스트림 중 문제가 발생했을 때 전송되는 에러 이벤트입니다.",
                "content": {
                    "text/event-stream": {
                        "schema": {"type": "string"},
                        "example": f"data: {json.dumps(error_example)}\n\n",
                    }
                },
            },
    }

ERROR_RESPONSES = {
    500: {
        "description": "서버 내부 오류가 발생했습니다",
        "model": ErrorResponse
    }
}


def get_mock_sse_response() -> str:
    return '''data: {"type": "status", "content": {"task_id": "style_analyst", "state": "start", "content": "style_analyst 의류 조합 분석 시작", "error_details": null}}

data: {"type": "status", "content": {"task_id": "style_analyst", "state": "progress", "content": "착장 매칭 시작...", "error_details": null}}

data: {"type": "status", "content": {"task_id": "style_analyst", "state": "progress", "content": "S3에서 착장 검색 중...", "error_details": null}}

data: {"type": "status", "content": {"task_id": "style_analyst", "state": "progress", "content": "S3 매칭 성공: 7개 착장 발견", "error_details": null}}

data: {"type": "status", "content": {"task_id": "style_analyst", "state": "progress", "content": "최종 착장 선택: c96192fc7e225468fbd88137717364ea", "error_details": null}}

data: {"type": "status", "content": {"task_id": "style_analyst", "state": "progress", "content": "전문가 분석 시작...", "error_details": null}}

data: {"type": "status", "content": {"task_id": "style_analyst", "state": "progress", "content": "Claude API 호출 중...", "error_details": null}}

data: {"type": "token", "content": "베이"}

data: {"type": "token", "content": "지 오버"}

data: {"type": "token", "content": "핏 반"}

data: {"type": "token", "content": "팔 셔"}

data: {"type": "token", "content": "츠에 블랙 "}

data: {"type": "token", "content": "와이드 "}

data: {"type": "token", "content": "슬랙스가"}

data: {"type": "token", "content": " 잘 어"}

data: {"type": "token", "content": "울려"}

data: {"type": "token", "content": "."}

data: {"type": "token", "content": " 셔츠 "}

data: {"type": "token", "content": "앞부분만"}

data: {"type": "token", "content": " 살짝 "}

data: {"type": "token", "content": "넣어서"}

data: {"type": "token", "content": " 내"}

data: {"type": "token", "content": "추럴한 분"}

data: {"type": "token", "content": "위기를 연"}

data: {"type": "token", "content": "출할"}

data: {"type": "token", "content": " 수 있어"}

data: {"type": "token", "content": "."}

data: {"type": "token", "content": " 여"}

data: {"type": "token", "content": "유있는"}

data: {"type": "token", "content": " 실"}

data: {"type": "token", "content": "루엣이"}

data: {"type": "token", "content": " 세"}

data: {"type": "token", "content": "련된 "}

data: {"type": "token", "content": "캐주얼 "}

data: {"type": "token", "content": "무드를 만"}

data: {"type": "token", "content": "들어내"}

data: {"type": "token", "content": "고,"}

data: {"type": "token", "content": " 블랙 "}

data: {"type": "token", "content": "옥스포드 "}

data: {"type": "token", "content": "슈즈로"}

data: {"type": "token", "content": " 포멀함"}

data: {"type": "token", "content": "을 더"}

data: {"type": "token", "content": "했어"}

data: {"type": "token", "content": ". "}

data: {"type": "token", "content": "셔츠 "}

data: {"type": "token", "content": "상단 "}

data: {"type": "token", "content": "버튼 "}

data: {"type": "token", "content": "1-2개 "}

data: {"type": "token", "content": "정도는 풀어두"}

data: {"type": "token", "content": "면 더 자연스러"}

data: {"type": "token", "content": "워. 브"}

data: {"type": "token", "content": "라운 가"}

data: {"type": "token", "content": "죽 서류가"}

data: {"type": "token", "content": "방으로 포"}

data: {"type": "token", "content": "인트를 주"}

data: {"type": "token", "content": "면서도"}

data: {"type": "token", "content": " 세련된 데"}

data: {"type": "token", "content": "이트 룩"}

data: {"type": "token", "content": "이 완성돼"}

data: {"type": "token", "content": ". 발"}

data: {"type": "token", "content": "목 길이 "}

data: {"type": "token", "content": "슬랙스에"}

data: {"type": "token", "content": "깔끔한 "}

data: {"type": "token", "content": "옥스포드 "}

data: {"type": "token", "content": "슈즈 "}

data: {"type": "token", "content": "매치로"}

data: {"type": "token", "content": " 다리"}

data: {"type": "token", "content": "라인도"}

data: {"type": "token", "content": " 길"}

data: {"type": "token", "content": "어 "}

data: {"type": "token", "content": "보여"}

data: {"type": "token", "content": "."}

data: {"type": "status", "content": {"task_id": "style_analyst", "state": "progress", "content": "전문가 분석 완료", "error_details": null}}

data: {"type": "status", "content": {"task_id": "style_analyst", "state": "end", "content": "style_analyst 분석 완료", "error_details": null}}

data: {"type": "message", "content": {"type": "ai", "content": "베이지 오버핏 반팔 셔츠에 블랙 와이드 슬랙스가 잘 어울려. 셔츠 앞부분만 살짝 넣어서 내추럴한 분위기를 연출할 수 있어. 여유있는 실루엣이 세련된 캐주얼 무드를 만들어내고, 블랙 옥스포드 슈즈로 포멀함을 더했어. 셔츠 상단 버튼 1-2개 정도는 풀어두면 더 자연스러워. 브라운 가죽 서류가방으로 포인트를 주면서도 세련된 데이트 룩이 완성돼. 발목 길이 슬랙스에깔끔한 옥스포드 슈즈 매치로 다리라인도 길어 보여.", "tool_calls": [], "tool_call_id": null, "run_id": "d54a8943-e754-4168-89d1-fb8a13eef8c8", "response_metadata": {}, "additional_kwargs": {"type": "text"}, "custom_data": {}}}

data: {"type": "status", "content": {"task_id": "search", "state": "start", "content": "이미지 검색 시작", "error_details": null}}

data: {"type": "status", "content": {"task_id": "search", "state": "end", "content": "이미지 검색 완료!", "error_details": null}}

data: {"type": "message", "content": {"type": "ai", "content": "이미지 검색을 진행했습니다. 관련 이미지 반환!", "tool_calls": [], "tool_call_id": null, "run_id": "d54a8943-e754-4168-89d1-fb8a13eef8c8", "response_metadata": {}, "additional_kwargs": {"type": "image", "image_urls": ["https://sw-fashion-image-data.s3.amazonaws.com/TOP/1002/4045199/segment/2_4.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAQKZOLTDISRDSPFYJ%2F20250916%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20250916T114630Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEBAaDmFwLW5vcnRoZWFzdC0yIkgwRgIhAPzvky3krALthdi0oxqCsZdmBVenn3hjY3%2BcuK6DLzOqAiEApdc2k%2BsE1hBYR0Kb8qAE9WxBWq6Z7oSuvVcSYBzlpocq1QUIif%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgwwMjMxODI2NzgyMjUiDBhqFpDWz7p24Z11qiqpBexveimPexSVHYFdIU8CpXVVue4oVk5as7SDeZqMvRuYdf97qMmTpUInfDJ%2FTOU2oxJRXBRV%2Fmqs%2FPC9II6XTIH2soSZzknG8VgBSvPZOJs3bK3VdFGNr2WdOw%2BiMsR08yZhjvUOZ01XBws%2FkprDAbHytywwtj94R2A5MIgqM%2B6ztpAgdGyZ7ceBYE3AjJIHMzMd0l1gr%2BS%2FDoVRp7IanoWOfuslhpxh%2BXaTYFLidT1oudOOPrvAApt98UbMymXMNSZ3DG1LRZw%2BB9oeGIAZcl5mtTzmHV%2B%2BESbE%2FLE6gxReGulgLEO9K0GlDbIfAPhoee%2BzufQe9LjgiWw6vTJvNlh%2FWFw%2FXbNuuhsVxCI4o4GAEWOTcPzaV9ONoPEjfaYZLOrpsl7YJgHUkT%2FCSw4qzsBGzgbDiEnmAX%2FbQnARfsp1fZ1Wk%2FOMWRwREOQL9CcO8XwEXoSJu82SPEz%2BNGtSuBy7Zt4sIV%2BB7MGsqDwoXn7RXmS5vmSo63t5hKkB%2B95%2BuZ2Uj0pz1mCk0IbOSfaYgBLvQBgoA5hlJrLnvGuTDLsLBdwyb5IaUTeSc4a6UhWjb4KQxhOl6BWO4v00QVTHrxkkWHcUHX2Vt4jfDN5mtG%2FBxsJp988Di5YBv%2BU2r74%2BsTZiMsKe%2FD9TmXWnFXy0ubekNMAY%2F9pWR24ydIo3baQKCF8a2KtqiRHseaZPZMI0FeQYtVvbB%2F9EwIdv%2FIj0j3fbnO4AsA7ybnX8jxApB8a042LqCYXYDUx8hrqtIx6cQjh68WxVSmNu%2BeAa0mkuTOzE7uLLnbqpHo71mNHXTaMHaR6nowEpP9CO7gaucTCSx0OBxcR5XLCk6Xr%2BKALB5BQ5eb3ntyxlup8m8BFgFyRi5uyg4DunNs8LvX9lccFqOvWxOdJ2e9FSTCHrKTGBjqwASJe%2B7l%2BhMW4qoVBpw1bWDCFlnQuE0r0Vv1rLrS%2BZ1D1IjkBF8VOe79j5WBLOPZBi5PBndZESimTiFdTJcpuZG9QH0Vb5iKpwPRi3NFHVcsGyi1DcR5aQkN99gTu5yRNAfJIfm%2B"]}}}

data: {"type": "[DONE]", "content": ""}
'''

__all__ = [
    "sse_response_example",
    "get_agents_openapi_examples",
    "get_mock_sse_response"
]