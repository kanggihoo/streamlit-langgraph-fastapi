## **1. 전체 시스템 구성**

이 시스템은 사용자에게 보여지는 **프론트엔드**와 실제 로직을 처리하는 **서버(백엔드)**로 구성됩니다.

- **💻 프론트엔드 (Client):** **Streamlit**을 사용하여 사용자 인터페이스(UI)를 구축합니다. 사용자가 메시지를 입력하고 실시간으로 응답을 확인하는 화면입니다.
- **⚙️ 서버 (Backend):** **FastAPI**를 기반으로 만들어졌으며, 사용자의 요청을 받아 처리하는 핵심 로직을 담당합니다. 내부적으로는 **LangGraph**를 사용하여 메시지에 대한 응답을 생성합니다.
- **🤝 통신 방식:** 클라이언트와 서버는 **SSE(Server-Sent Events)** 방식을 사용하여 서버가 클라이언트에게 지속적으로 데이터를 스트리밍합니다.

## **2. 동작 흐름 (Work Flow)**

사용자가 메시지를 입력하고 화면에 응답이 표시되기까지의 과정은 총 6단계로 이루어집니다.

### **① 사용자 메시지 입력 (in Streamlit)**

사용자가 Streamlit으로 만들어진 채팅 화면에 메시지를 입력하고 '전송' 버튼을 누릅니다.

### **② API 요청 준비 및 전송 (in client.py)**

1. `client.py`는 사용자가 입력한 메시지를 서버(FastAPI)가 이해할 수 있는 형식(**Pydantic의 `StreamInput` 모델**)으로 변환합니다.
2. 변환된 데이터를 담아 서버로 API 요청을 보냅니다.

### **③ 서버 로직 처리 (in FastAPI & LangGraph)**

1. FastAPI 서버는 `client.py`로부터 받은 요청을 수신합니다.
2. 수신한 데이터를 바탕으로 **LangGraph**를 호출하여 사용자의 메시지에 대한 응답 생성을 시작합니다.

### **④ SSE 응답 생성 및 전송 (in FastAPI)**

1. LangGraph가 생성하는 결과(응답)를 **실시간 스트리밍(SSE)** 형식에 맞게 파싱합니다.
2. FastAPI는 처리된 결과를 `client.py`로 즉시 전송하기 시작합니다. 이 과정은 응답이 완전히 끝날 때까지 계속됩니다.

### **⑤ SSE 응답 수신 및 가공 (in client.py)**

1. `client.py`는 FastAPI 서버로부터 SSE 스트림을 실시간으로 수신합니다.
2. 수신한 데이터의 `type`을 확인하고, 이를 **비동기 제너레이터(asynchronous generator)** 방식으로 Streamlit에 전달할 준비를 합니다. 이를 통해 데이터를 한 번에 다 받는 것이 아니라, 들어오는 족족 순차적으로 처리할 수 있습니다.

### **⑥ 최종 화면 표시 (in Streamlit)**

1. Streamlit은 `client.py`로부터 전달받은 비동기 제너레이터를 계속해서 확인합니다 (`while` 루프).
2. 제너레이터에서 새로운 데이터가 나올 때마다 데이터의 `type`에 맞춰 UI를 업데이트하여 사용자에게 최종 응답 메시지를 실시간으로 보여줍니다.

## **3. SSE 데이터 구조**

서버(FastAPI)가 클라이언트(`client.py`)로 전송하는 SSE 메시지는 다음과 같은 `JSON` 문자열 구조를 가짐.

`data: {"type" : "타입" , "content" : "내용"}\n\n`

- `type`: 메시지의 종류를 나타내며, 총 5가지가 있습니다.
    - **`token`**: 응답이 생성되는 과정의 각 단어(토큰) 조각입니다.
    - **`error`**: 처리 과정에서 오류가 발생했을 때 사용됩니다.
    - **`end`**: 모든 응답 스트림이 정상적으로 종료되었음을 알립니다.
    - **`status`**: 현재 서버의 처리 상태(예: '모델 호출 중...')를 전달할 때 사용됩니다.
    - **`message` :** ai의 최종 응답 및, 추가 메타 정보가 포함된 구조화된 데이터 처리
- `content`: `type`에 따라 담기는 내용이 달라집니다.
    - `token`, `error`, `end`타입일 경우: `content`에는 일반 **문자열(string)**이 담깁니다.
        - `end` 일 경우에는 빈 문자열
    - `status` 타입일 경우: `content`에는 특정 작업의 진행 상태(시작, 중간 과정, 종료)를 담은 **`StatusUpdate` 모델**이 `JSON` 형식으로 변환되어 담깁니다.
        
        ```python
        from pydantic import BaseModel, Field
        from typing import Literal, Optional, Annotated
        from uuid import uuid4
        
        class StatusUpdate(BaseModel):
            """특정 작업의 진행 상태를 클라이언트에 전달하기 위한 모델"""
        
            task_id: Annotated[str, Field(default_factory=lambda: str(uuid4()) , description="작업의 고유 ID. 동일한 작업의 시작과 종료를 매칭하는 데 사용됩니다.") ]
        
            state: Literal["start", "end", "progress","error"] = Field(
                description="작업의 현재 상태 (시작, 종료, 진행중, 에러)",
                examples=["start", "end", "progress", "error"],
            )
        
            content: str = Field(
                description="사용자에게 보여줄 메시지 (예: '벡터 DB 검색 중...')",
                examples=["벡터 DB 검색 중..."],
            )
        
            # 에러 발생 시 추가적인 에러 정보를 담을 수 있는 필드
            error_details: Optional[str] = None
        ```
        
    - **`message`** 타입일 경우: `content`에는 채팅 메시지 전체 정보(작성자, 내용, 이미지 url정보 등)를 담은 **`ChatMessage` 모델**이 `JSON` 형식으로 변환되어 담깁니다.
        
        ```python
        class ChatMessage(BaseModel):
            """Langchain의 BaseMessage를 pydantic 모델로 정의한 ChatMessage 으로 변환 후 API 요청에 대한 응답 데이터 타입"""
        
            type: Literal["human", "ai", "tool", "custom"] = Field(
                description="Role of the message.",
                examples=["human", "ai", "tool", "custom"],
            )
            content: str = Field(
                description="Content of the message.",
                examples=["Hello, world!"],
            )
            tool_calls: list[ToolCall] = Field(
                description="Tool calls in the message.",
                default_factory=list,
            )
            tool_call_id: str | None = Field(
                description="type = tool 혹은 ai이면서 tool_calls 필드가 있는 경우 메세지의 tool_call_id 전달",
                default=None,
                examples=["call_Jja7J89XsjrOLA5r!MEOW!SL"],
            )
            run_id: str | None = Field(
                description="Run ID of the message.",
                default=None,
                examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
            )
            response_metadata: dict[str, Any] = Field(
                description="type = ai 인경우 ai 메세지의 response_metadata 필드 전달 For example: response headers, logprobs, token counts.",
                default_factory=dict,
            )
            additional_kwargs: dict[str, Any] = Field(
                description="additional_kwargs 필드 전달",
                default_factory=dict,
            )
        ```
        

## 세부 동작 과정 (langgraph 동작 시킨 후 fastapi에서 SSE 데이터 반환)

클라이언트로부터 API 요청을 받아 LangGraph를 호출하고, 그 결과를 SSE(Server-Sent Events) 스트림으로 변환하여 클라이언트로 전송하는 서버 내부의 상세 동작 과정

### **1. API 요청 수신 및 LangGraph 호출**

1. **요청 수신**: 클라이언트(`client.py`)는 사용자 정보가 담긴 **`StreamInput`** Pydantic 모델을 FastAPI 서버로 전송합니다.
2. **LangGraph 비동기 호출**: FastAPI는 수신한 `StreamInput` 정보를 바탕으로 LangGraph 에이전트를 비동기 스트리밍 방식(**`graph.astream()`**)으로 호출합니다. 이때, 다양한 종류의 이벤트(최종 결과, 중간 토큰, 커스텀 상태)를 모두 수신하기 위해 `stream_mode`를 다음과 같이 설정합니다.
    
    ```python
    async for stream_event in agent.astream(
        ...,
        stream_mode=["updates", "custom", "messages"],
        subgraphs=True
    ):
        # 스트림 이벤트 처리 로직
    ```
    

### **2. LangGraph 스트림 이벤트 처리 및 SSE 변환**

`astream()`으로부터 반환되는 이벤트는 `stream_mode`의 종류에 따라 구분되어 처리됩니다. 서버는 **각 이벤트의 성격에 맞게 데이터를 파싱하여 표준 SSE 형식으로 변환한 후 클라이언트로** `yield` 합니다.

### **▶️ `updates` 모드 처리: 최종 메시지 생성**

`updates` 모드는 그래프의 각 노드(단계)가 작업을 마친 후 상태(State)를 업데이트할 때 발생하는 이벤트를 처리합니다. 주로 **완성된 최종 메시지를 생성**하는 데 사용됩니다.

- **최종 SSE 응답**: `type="message"`, `content=ChatMessage`
- **처리 과정**:
    1. 단순 상태 업데이트와 같이 불필요한 노드의 결과는 **필터링**하여 무시합니다.
    2. LangGraph가 반환한 `dict` 형태의 결과를 LangChain의 **`AIMessage`** 형식으로 변환합니다. (`create_ai_message` 함수 사용)
    3. `AIMessage`를 클라이언트 전송용 Pydantic 모델인 `ChatMessage`로 한 번 더 변환합니다. (`langchain_to_chat_message` 함수 사용)
    4. 변환 과정에서 오류 발생 시, `type="error"` SSE 이벤트를 전송합니다.
        
        ```python
        yield f"data: {json.dumps({'type': 'error', 'content': 'Unexpected error'})}\n\n"
        ```
        
    5. 사용자가 **처음에 입력했던 메시지가 응답에 포함되어 반환되는 경우, 이를 필터링하여 중복 전송을 방지**합니다.
    6. 최종적으로 `ChatMessage` 모델을 `JSON`으로 변환하여 `type="message"` SSE 응답을 전송
        
        ```python
        yield f"data: {json.dumps({'type': 'message', 'content': chat_message.model_dump()})}\n\n"
        ```
        

### **▶️ `messages` 모드 처리: 실시간 토큰 스트리밍**

`messages` 모드는 LLM이 **실시간으로 생성하는 텍스트 토큰**을 처리하는 데 특화되어 있습니다.

- **최종 SSE 응답**: `type="token"`, `content="문자열"`
- **처리 과정**:
    1. 이벤트의 `metadata` 내 `tags` 값을 확인하여 스트리밍을 원치 않는 정보(`skip_stream` 태그 등)는 `continue`로 건너뜁니다.
    2. 이벤트의 데이터 형식이 `AIMessageChunk`가 아니면 `continue`로 건너뜁니다.
        - *이유: 특정 노드의 상태 반환 값은 `updates`와 `messages` 모드 양쪽에서 모두 트리거될 수 있습니다. `messages` 모드에서는 순수한 LLM 토큰 스트림(`AIMessageChunk`)만 처리하기 위해 이 필터링 과정이 필수적입니다.*
    3. `msg.content`의 내용이 리스트(list) 형식인 경우 문자열로 변환하는 등 필요한 전처리를 수행합니다.
    4. 최종적으로 `type="token"`과 함께 텍스트 조각(토큰)을 `content`에 담아 SSE 응답을 전송합니다.Python
        
        ```python
        yield f"data: {json.dumps({'type': 'token', 'content': string_content})}\n\n"
        ```
        

### **▶️ `custom` 모드 처리: 커스텀 이벤트 및 상태**

`custom` 모드는 LangGraph의 기본 스트림 외에 **개발자가 의도적으로 주입한 커스텀 데이터**를 처리하기 위해 사용됩니다. 주로 **외부 LLM 스트리밍** 결과를 통합하거나, `get_stream_writer`를 이용해 **그래프의 현재 상태**(예: '검색 시작', '데이터 분석 중...')를 클라이언트에 전달할 때 유용합니다.

- **처리 과정**:
    1. `custom` 이벤트로 들어온 데이터는 `{"type": ..., "content": ...}` 구조의 딕셔너리 형태
    2. `type` 값에 따라 분기하여 처리합니다.
        - **외부 LLM 토큰 스트림 (`type="token"`)**: `content`에 담긴 토큰 문자열을 그대로 SSE로 전송합니다.
        - **그래프 상태 알림 (`type="status"`)**: `content`에 담긴 상태 메시지(예: 'Agent Start')를 그대로 SSE로 전송합니다.
    
    ```python
    # custom 모드 데이터 처리 예시
    type, content = data["type"], data["content"]
    match type:
        case "token":
            yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
        case "status":
            yield f"data: {json.dumps({'type': 'status', 'content': content})}\n\n"
    ```
    

### **3. 스트림 종료 및 예외 처리**

1. **전체 예외 처리**: 위에서 설명한 개별 처리 과정 외에 예측하지 못한 서버 내부 오류가 발생할 경우, `type="error"` SSE 이벤트를 전송하여 클라이언트가 오류 상황을 인지하게 합니다.
    
    ```python
    yield f"data: {json.dumps({'type': 'error', 'content': 'Internal server error'})}\n\n"
    ```
    
2. **최종 종료 신호**: 모든 LangGraph **스트림 처리가 정상적으로 완료되면, 마지막으로 `type="end"` SSE 이벤트를 전송하여 클라이언트에게 스트림이 완전히 끝났음을 알립**니다
    
    ```python
    yield f"data: {json.dumps({'type': 'end', 'content': ''})}\n\n"
    ```
    

### **▶️ `custom` 모드 처리: 커스텀 이벤트 및 상태**

`custom` 모드는 LangGraph의 기본 스트림 외에 **개발자가 의도적으로 주입한 커스텀 데이터**를 처리하기 위해 사용됩니다. 이 시스템에서는 두 가지 주요 목적으로 활용됩니다.

1. **그래프 상태 알림 (`type="status"`)**: `get_stream_writer`를 이용해 그래프 내부 작업(예: '의류 조합 분석 시작', 'DB 검색 중...')의 현재 상태를 클라이언트에 실시간으로 전달합니다.
2. **외부 LLM 스트리밍 결과 통합 (`type="token"`)**: 그래프의 주된 LLM이 아닌, 외부에서 호출된 다른 LLM의 응답 스트림을 메인 SSE 스트림에 통합하여 클라이언트가 일관된 방식으로 토큰을 처리할 수 있게 합니다.

### **처리 과정**

`custom` 이벤트로 들어온 데이터는 `{"type": ..., "content": ...}` 구조의 딕셔너리 형태이며, `type` 값에 따라 다음과 같이 분기하여 처리됩니다.

- **그래프 상태 알림 (`type="status"`)**
    - **LangGraph 노드**: `writer`는 `type`을 `"status"`로, `content`에는 `StatusUpdate` Pydantic 모델이 담긴 딕셔너리를 주입합니다. 이 `StatusUpdate` 모델은 `task_id`, `state("start", "progress", "end")`, `content`(메시지) 등의 필드를 가집니다.
    - **FastAPI 서버**: 이 데이터를 수신하여, 클라이언트에는 `type`이 `"status"`이고 `content`가 `StatusUpdate` 객체의 JSON인 SSE 메시지를 그대로 전달합니다.
- **외부 LLM 토큰 스트림 통합 (`type="token"`)**
    - **LangGraph 노드**: 외부 LLM에서 받은 토큰(문자열 조각)을 `writer`를 통해 주입합니다. 이때 `type`은 `"token"`으로, `content`에는 해당 토큰 문자열을 담습니다.
    - **FastAPI 서버**: 이 데이터를 수신하면, `messages` 모드에서 처리되는 일반 토큰 스트림과 동일한 형식, 즉 `type`이 `"token"`이고 `content`가 문자열인 SSE 메시지를 클라이언트로 전달합니다. 이를 통해 클라이언트는 **토큰의 출처(내부 LangGraph, 외부 LLM)에 관계없이 동일한 로직으로 스트리밍 UI를 업데이트**할 수 있습니다.

```python
# FastAPI의 custom 모드 데이터 처리 예시
# data = {"type": "status" | "token", "content": StatusUpdate | str}

type, content = data["type"], data["content"]

match type:
    # 외부 LLM 스트림을 통합하기 위한 경우
    case "token":
        # content는 단순 문자열 토큰
        yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"

    # 그래프 내부 작업의 진행 상태를 알리기 위한 경우
    case "status":
        # content는 StatusUpdate 모델의 dict 형태
        yield f"data: {json.dumps({'type': 'status', 'content': content})}\n\n"
```

## 클라이언트 측 SSE 응답 처리 (client.py) 

`client.py`는 서버로부터 SSE(Server-Sent Events) 스트림을 수신하여 가공한 뒤, 최종적으로 프론트엔드(Streamlit)에 전달하는 역할을 수행합니다.

### **1. SSE 스트림 수신 및 반복 처리**

클라이언트는 **`httpx.AsyncClient`**를 사용하여 서버 API에 스트리밍 요청을 보냅니다. 연결이 성공하면, `response.aiter_lines()`를 통해 서버가 보내는 SSE 데이터 라인을 비동기적으로 하나씩 수신하여 처리합니다.

- **요청/응답 흐름**:
    1. `httpx`를 이용해 서버로 POST 스트리밍 요청을 시작합니다.
    2. 응답이 오기 시작하면 `async for` 루프를 통해 데이터 라인을 순회합니다.
    3. 각 라인은 `_parse_stream_line` 함수로 전달되어 파싱됩니다.
    4. 파싱된 결과(`ChatMessage` | `StatusUpdate` | `str` | `None`)는 **비동기 제너레이터(`yield`)**를 통해 Streamlit 로직으로 즉시 전달됩니다.
    5. 파싱 결과가 `None`이면 스트림이 종료된 것으로 간주하고 루프를 중단합니다.

```python
# client.py의 메인 스트리밍 로직
async with client.stream(...) as response:
    response.raise_for_status()
    async for line in response.aiter_lines():
        if line.strip(): # 빈 줄은 무시
            parsed = self._parse_stream_line(line)
            if parsed is None: # 종료 신호
                break
            yield parsed # 파싱된 데이터를 Streamlit으로 전달
```

### **2. SSE 메시지 파싱 및 전처리 (`_parse_stream_line`)**

서버로부터 받은 각 SSE 라인(`data: {...}\n\n`)은 이 함수를 통해 Streamlit이 사용하기 쉬운 객체로 변환됩니다.

### **① 원시 데이터 추출**

- 수신한 라인이 `"data: "`로 시작하는지 확인합니다.
- `"data: "` 부분을 잘라내어 순수한 `JSON` 문자열만 추출합니다.
- `json.loads()`를 사용해 `JSON` 문자열을 Python 딕셔너리로 변환합니다.

### **② 메시지 `type`에 따른 분기 처리**

파싱된 딕셔너리의 `"type"` 키 값을 기준으로 `match` 문을 사용하여 각기 다른 처리를 수행합니다.

- **`type="message"`** (완성된 메시지 객체)
    - **처리 내용**: `"content"` 키에 담긴 딕셔너리를 **`ChatMessage` Pydantic 모델**로 유효성 검사를 거쳐 객체 인스턴스로 변환 후 반환합니다.
    - **최종 반환**: `ChatMessage`
- **`type="token"`** (실시간 타이핑 효과)
    - **처리 내용**: `"content"` 키에 담긴 **문자열**을 그대로 반환합니다.
    - **최종 반환**: `str`
- **`type="status"`** (서버 내부 처리 상태)
    - **처리 내용**: `"content"` 키에 담긴 딕셔너리를 **`StatusUpdate` Pydantic 모델**로 유효성 검사를 거쳐 객체 인스턴스로 변환 후 반환합니다.
    - **최종 반환**: `StatusUpdate`
- **`type="error"`** (처리 중 오류 발생)
    - **처리 내용**: `"content"`에 담긴 오류 문자열 앞에 `"Error: "`를 붙여 새로운 `ChatMessage` 객체를 생성합니다. 이때 `type`은 `"ai"`로 설정하여 AI가 보낸 메시지처럼 보이게 합니다.
    - **최종 반환**: `ChatMessage(type="ai", content="Error: ...")`
- **`type="end"`** (스트림 종료 신호)
    - **처리 내용**: 스트림의 끝을 의미하므로, `None`을 반환하여 상위의 `async for` 루프를 중단시킵니다.
    - **최종 반환**: `None`

---

이 과정을 통해 `client.py`는 서버로부터 오는 복잡한 SSE 스트림을 Streamlit이 손쉽게 UI에 표시할 수 있는 **`ChatMessage`**, **`StatusUpdate`**, 단순 **`문자열`**, 또는 종료 신호(**`None`**)로 변환하여 전달하는 역할을 완수합니다.

## Streamlit 메시지 표시 및 상태 관리 명세서 (`draw_messages`)

 `client.py`로부터 전달받은 **비동기 제너레이터를 처리하여 사용자 화면에 메시지를 동적으로 표시하고, `st.session_state`를 통해 채팅 기록을 관리**하는 `draw_messages` 함수의 전체 동작 과정을 설명합니다.

### **1. 통합 메시지 처리 구조**

`draw_messages` 함수는 두 가지 종류의 메시지 소스를 동일한 방식으로 처리하는 통합 구조를 가집니다.

- **① 기존 메시지 불러오기**: `st.session_state.messages`에 저장된 과거 채팅 기록(`List[ChatMessage]`)을 **비동기 제너레이터로 변환하여 함수에 전달**합니다.
- **② 새로운 메시지 스트리밍**: **사용자가 새 입력을 하면 API로부터 실시간 SSE 응답을 받아 `client.py`가 생성한 비동기 제너레이터를 함수에 전달**합니다.
- `st.session_state.messages` 리스트 에는 항상 `ChatMessage` 만이 담겨있음.

이러한 통합 처리 덕분에, 과거 메시지를 다시 그리거나 새로운 메시지를 실시간으로 표시하는 로직이 일관되게 관리됩니다.

### **2. 메인 처리 흐름**

함수는 `while msg := await anext(messages_agen, None):` 루프를 통해 **비동기 제너레이터로부터 데이터가 소진될 때까지 하나씩 가져와 처리**합니다. 제너레이터에서 넘어오는 `msg` 객체의 타입에 따라 처리 로직이 분기됩니다.

1. **`str`**: LLM이 생성하는 실시간 텍스트 토큰
2. **`StatusUpdate`**: 도구 사용 등 백그라운드 작업의 진행 상태
3. **`ChatMessage`**: 대화의 완성된 단위 (사용자 입력, AI 응답, 도구 호출 등)

### **3. 메시지 타입별 상세 처리 과정**

### **▶️ `str` 타입 처리 (실시간 토큰 스트리밍)**

LLM의 답변이 **실시간으로 타이핑되는 것처럼 보이게 하는 기능**입니다.

- **동작 방식**:
    1. 첫 번째 토큰(`str`)을 받으면, `st.empty()`를 사용해 비어있는 UI 플레이스홀더를 생성합니다.
    2. 이후 들어오는 모든 토큰을 `streaming_content` **변수에 계속 누적**합니다.
    3. 누적된 전체 내용을 플레이스홀더에 덮어쓰는 방식으로 실시간 업데이트를 구현합니다.
- **세션 관리**: 개별 토큰(`str`)은 일시적인 표시 용도이므로 **`st.session_state.messages`에 저장되지 않습니다.**

### **▶️ `StatusUpdate` 타입 처리 (작업 상태 시각화)**

에이전트가 특정 도구를 사용하거나 작업을 수행할 때, 그 진행 상황을 사용자에게 시각적으로 보여주는 기능

- **동작 방식**:
    1. `st.status()` 위젯을 사용하여 각 작업(`task_id` 기준)에 대한 **상태 표시 컨테이너를 생성**합니다.
    2. `msg.state` 값("start", "progress", "end", "error")에 따라 컨테이너의 아이콘(⏳, 🔄, ✅, ❌)과 라벨, 상태가 동적으로 변경됩니다.
    3. 예를 들어, "start" 상태에서 "running" 상태의 컨테이너를 생성하고, "end" 상태를 받으면 "complete"로 업데이트 후 화면에 유지합니다.
    4. 이 컨테이너들은 `st.session_state.status_containers` 딕셔너리에서 관리됩니다.

### **▶️ `ChatMessage` 타입 처리 (구조화된 메시지)**

대화의 핵심 단위를 처리하며, 메시지의 `type` 속성(`human`, `ai` 등)에 따라 다르게 동작합니다.

- **`type="human"`**: 사용자의 입력입니다. `st.chat_message("human")` 컨테이너에 `msg.content`를 그대로 출력합니다.
- **`type="ai"`**: AI의 응답이며, 가장 복잡한 로직을 가집니다.
    1. **세션 저장**: 새로운 응답(`is_new=True`)인 경우, 해당 `ChatMessage` 객체를 `st.session_state.messages` 리스트에 추가하여 대화 기록을 보존합니다.
    2. **UI 그룹핑**: 직전 메시지 타입이 "ai"가 아니었던 경우에만 새로운 `st.chat_message("ai")` 컨테이너를 생성합니다. 이를 통해 연속된 AI 응답(예: 텍스트 출력 후 도구 사용)이 같은 말풍선 안에 표시됩니다.
    3. **콘텐츠 표시**:
        - 만약 이전에 `str` 타입의 토큰 스트리밍이 있었다면, `streaming_placeholder`를 최종 `msg.content`로 업데이트하고 플레이스홀더를 초기화합니다.
        - 스트리밍 없이 바로 `ChatMessage`가 온 경우(예: LLM 호출 없는 노드 결과), `st.write()`로 `msg.content`를 출력합니다.
        - `additional_kwargs`에 이미지 정보가 포함된 경우, `st.image`를 통해 이미지를 출력합니다.
    4. **도구 호출(Tool Calls) 처리**:
        - `msg.tool_calls` 필드에 데이터가 있으면, 각 도구 호출에 대해 `st.status()` 컨테이너를 생성하여 **어떤 도구를 어떤 인자로 호출하는지** 먼저 표시합니다.
        - 그 후, **`await anext(messages_agen)`를 호출하여 제너레이터에서 다음 메시지를 미리 가져옵니다.** 이는 **도구 호출 선언 바로 다음에 도구 실행 결과가 온다는 약속에 기반**합니다.
        - 가져온 결과 메시지(`type="tool"`)를 해당 `st.status` 컨테이너 내부에 "Output"으로 표시하고, 상태를 "complete"로 변경합니다.
    
    그외의 타입에 대해서는 에러처리