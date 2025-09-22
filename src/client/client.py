from typing import Any
import json
from model.schema import (
    ChatHistory,
    ChatHistoryInput,
    ChatMessage,
    StreamInput,
    AgentInfo,
    ServiceMetadata,
    UserInput,
    StatusUpdate,
)

import httpx 
from model.type import SSETypes


class AgentClientError(Exception):
    """Base exception for all agent client errors."""
    pass

class AgentClient:
    """Client for interacting with the agent service."""
    def __init__(
        self,
        base_url: str = "http://0.0.0.0/langgraph",
        agent: str | None = None,
        timeout: float | None = None,
        get_info : bool = True,
    )->None:
        """
        Initialize the agent client.

        Args:
            base_url (str): Base URL for the agent service.
            agent (str | None, optional): Agent key. Defaults to None.
            timeout (float | None, optional): Timeout for the agent service. Defaults to None.
            get_info (bool, optional): Whether to get agent info. Defaults to True.
        """

        self.base_url = base_url
        self.timeout = timeout
        self.agent: str | None = None
        self.info : ServiceMetadata | None = None
        if get_info:
            self.get_info()
        if agent:
            self.update_agent(agent)
    
    def get_info(self)->None:
        try:
            response = httpx.get(
                f"{self.base_url}/info",
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.RequestError as e:
            raise AgentClientError(f"Failed to get agent info: {e}")

        
        self.info = ServiceMetadata.model_validate(response.json())
        if not self.agent and self.agent not in self.info.agents:
            self.agent = self.info.default_agent
    
    def update_agent(self , agent:str , verify:bool = True)->None:
        if verify:
            if not self.info:
                self.get_info()
            
            if agent not in self.info.agents:
                raise AgentClientError(f"Invalid agent: {agent}")
        self.agent = agent

    # def invoke(
    #         self,
    #         message:str, 
    #         model:str | None = None,
    #         thread_id:str | None = None,
    #         user_id:str | None = None,
    #         agent_config:dict[str, Any] | None = None,
    # ):
    #     request = UserInput(
    #         message=message,
    #     )
    #     if model:
    #         request.model = model
    #     if thread_id:
    #         request.thread_id = thread_id
    #     if user_id:
    #         request.user_id = user_id
    #     if agent_config:
    #         request.agent_config = agent_config
        
    #     try:
    #         response = httpx.post(
    #             f"{self.base_url}/{self.agent}/invoke",
    #             json=request.model_dump(),
    #             timeout=self.timeout,
    #         )
    #         response.raise_for_status()
    #     except httpx.RequestError as e:
    #         raise AgentClientError(f"Failed to invoke agent: {e}")
        
    #     return ChatMessage.model_validate(response.json())


    async def ainvoke(
            self,
            message:str, 
            model:str | None = None,
            thread_id:str | None = None,
            user_id:str | None = None,
            agent_config:dict[str, Any] | None = None,
    )->ChatMessage:
        """
        Asynchronous invoke agent.

        Args:
            message (str): message to send to agetn
            model (str | None, optional): LLM model to use for agent
            thread_id (str | None, optional): Thread ID for conversation
            user_id (str | None, optional): _description_. Defaults to None.
            agent_config (dict[str, Any] | None, optional): Additional configuration to pass through to the agent
        """
        if not self.agent:
            raise AgentClientError("Agent not selected")
        request = UserInput(message=message)
        if model:
            request.model = model
        if thread_id:
            request.thread_id = thread_id
        if user_id:
            request.user_id = user_id
        if agent_config:
            request.agent_config = agent_config
        
        try:
            async with httpx.AsyncClient() as client:

                response = await client.post(
                    f"{self.base_url}/{self.agent}/invoke",
                    json = request.model_dump(),
                    timeout=self.timeout,
                )
                response.raise_for_status()
        except httpx.RequestError as e:
            raise AgentClientError(f"Failed to invoke agent: {e}")
        return ChatMessage.model_validate(response.json())
    
    
    # def stream(
    #         self,
    #         message:str, 
    #         model:str | None = None,
    #         thread_id:str | None = None,
    #         user_id:str | None = None,
    #         agent_config:dict[str, Any] | None = None,
    #         stream_tokens:bool = True,
    # ):
    #     request = StreamInput(
    #         message = message,
    #         stream_tokens = stream_tokens,
    #     )
    #     if model:
    #         request.model = model
    #     if thread_id:
    #         request.thread_id = thread_id
    #     if user_id:
    #         request.user_id = user_id
    #     if agent_config:
    #         request.agent_config = agent_config
        
    #     try:
    #         with httpx.stream(
    #             "POST",
    #             f"{self.base_url}/{self.agent}/stream",
    #             json=request.model_dump(),
    #             timeout=self.timeout,
    #         ) as response:
    #             response.raise_for_status()
    #             for line in response.iter_lines():
    #                 if line.strip():
    #                     parsed = self._parse_stream_line(line)
    #                     if parsed is None:
    #                         break
    #                     yield parsed
    #     except httpx.RequestError as e:
    #         raise AgentClientError(f"Failed to stream agent: {e}")
    
    async def astream(
            self,
            message:str, 
            model:str | None = None,
            thread_id:str | None = None,
            user_id:str | None = None,
            agent_config:dict[str, Any] | None = None,
            stream_tokens:bool = True,
    ):
        """stream_tokens가 True일 때는 토큰 단위로 스트리밍

        Args:
            message (str): agent에게 전달할 입력 메세지
            model (str | None, optional): 사용할 LLM 모델. Defaults to None.
            thread_id (str | None, optional): 대화 유지를 위한 스레드 ID. Defaults to None.
            user_id (str | None, optional): _description_. Defaults to None.
            agent_config (dict[str, Any] | None, optional): agent에게 전달할 설정. Defaults to None.
            stream_tokens (bool, optional): 토큰 단위로 스트리밍 여부. Defaults to True.
        """
        if not self.agent:
            raise AgentClientError("Agent not selected")
        request = StreamInput(
            message = message,
            stream_tokens = stream_tokens,
        )
        if model:
            request.model = model
        if thread_id:
            request.thread_id = thread_id
        if user_id:
            request.user_id = user_id
        if agent_config:
            request.agent_config = agent_config


        #=====================================================================================================================================
        # 스트리밍 모드로 요청을 받았을 때, Fastapi에게 전달할 요청 데이터 생성 및 stream 요청 및 응답 수신 후 stremalit에게 전달할 형식으로 데이터 전달(비동기 제너레이터)
        #=====================================================================================================================================
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/{self.agent}/stream",
                    json = request.model_dump(),
                    timeout=self.timeout,
                ) as response:
                    # print(f"stream response(client.py): {response}")
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.strip(): # 데이터가 있는 경우 파싱
                            parsed = self._parse_stream_line(line)
                            if parsed is None:
                                break
                            yield parsed
            except httpx.RequestError as e:
                raise AgentClientError(f"Failed to stream agent: {e}")
    
    #===============================================================================================================
    # SSE 응답에 대한 결과 문자열을 parsing 함수 (data: 키워드 제외 후 json 파싱 후 데이터 처리) 
    # 0 : 다음과 같은 구조로 데이터 수신 {"type": "message", "content": ChatMessage | StatusUpdate | str}
    #     1. type : message 인 경우 contnet = ChatMessage 
    #     2. type : status 인 경우 content = StatusUpdate 객체
    #     2. type : token | error | end 인 경우 content = 문자열
    # 
    # 수신한 데이터 paring 한 후 최종 반환 형식
    # 1. type : meesage 인 경우(langgraph stream_mode : updates인 경우) => ChatMessage 객체 반환
    # 2. type : token 인 경우(langgraph stream_mode : messages인 경우) => 문자열 반환(ChatMessage.content 내용만 반환)
    # 3. type : status 인 경우(langgraph stream_mode : updates인 경우) => StatusUpdate 객체 반환
    # 3. type : error 인 경우 (langgraph stream_mode 과정에서 오류 발생한 경우) => ChatMessage 객체 반환
    #===============================================================================================================
    def _parse_stream_line(self , line:str)->ChatMessage | StatusUpdate |str| None:
        line = line.strip()
        if line.startswith("data: "):
            data = line[6:]
            try:
                parsed:dict[str, Any] = json.loads(data)
            except Exception as e:
                raise AgentClientError(f"Failed to parse stream line: {e}")
            # print("client.py : _parse_stream_line : parsed => " , parsed)
            match parsed["type"]:
                case SSETypes.END.value:
                    return None
                case SSETypes.MESSAGE.value:
                    try:
                        return ChatMessage.model_validate(parsed["content"])
                    except Exception as e:
                        raise Exception(f"Failed to parse stream line: {e}")

                case SSETypes.TOKEN.value:
                    return parsed["content"]
                case SSETypes.STATUS.value:
                    try:
                        return StatusUpdate.model_validate(parsed["content"])
                    except Exception as e:
                        raise Exception(f"Failed to parse stream line: {e}")
                
                case SSETypes.ERROR.value:
                    error_msg = "Error: " + parsed["content"]
                    return ChatMessage(
                        type="ai",
                        content=error_msg,
                    )
        return None
    

    def get_history(self, thread_id: str) -> ChatHistory:
        """
        thread_id에 대한 채팅 내역 가져오기
    
        Args:
            thread_id (str, optional): Thread ID for identifying a conversation
        """
        
        print(f"{self.base_url}/{self.agent}/history")
        try:
            response = httpx.get(
                f"{self.base_url}/{self.agent}/{thread_id}/history",
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise AgentClientError(f"Error: {e}")

        return ChatHistory.model_validate(response.json())

    def delete_history(self, thread_id: str) -> None:
        """
        thread_id에 대한 채팅 내역 삭제
        
        Args:
            thread_id (str): Thread ID for identifying a conversation to delete
        """
        try: 
            response = httpx.delete(
                    f"{self.base_url}/{thread_id}/history",
                    timeout=self.timeout,
                )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise AgentClientError(f"Error deleting chat history: {e}")

    # async def acreate_feedback(
    #     self, run_id: str, key: str, score: float, kwargs: dict[str, Any] = {}
    # ) -> None:
    #     """
    #     Create a feedback record for a run.

    #     This is a simple wrapper for the LangSmith create_feedback API, so the
    #     credentials can be stored and managed in the service rather than the client.
    #     See: https://api.smith.langchain.com/redoc#tag/feedback/operation/create_feedback_api_v1_feedback_post
    #     """
    #     request = Feedback(run_id=run_id, key=key, score=score, kwargs=kwargs)
    #     async with httpx.AsyncClient() as client:
    #         try:
    #             response = await client.post(
    #                 f"{self.base_url}/feedback",
    #                 json=request.model_dump(),
    #                 headers=self._headers,
    #                 timeout=self.timeout,
    #             )
    #             response.raise_for_status()
    #             response.json()
    #         except httpx.HTTPError as e:
    #             raise AgentClientError(f"Error: {e}")
