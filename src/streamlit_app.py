import asyncio
import os
import streamlit as st
import urllib.parse
import uuid
from typing import AsyncGenerator
from dotenv import load_dotenv
import logging


from model.schema import ChatMessage , ChatHistory
from client import AgentClient , AgentClientError
from utils.streamlit_messages import draw_messages
from settings import settings

logging.basicConfig(level=logging.INFO , format="%(asctime)s - %(levelname)s - %(message)s  [%(filename)s:%(lineno)d]" , datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)


# from client import AgentClient, AgentClientError
# from schema import ChatHistory, ChatMessage
# from schema.task_data import TaskData, TaskDataStatus

# A Streamlit app for interacting with the langgraph agent via a simple chat interface.
# The app has three main functions which are all run async:

# - main() - sets up the streamlit app and high level structure
# - draw_messages() - draws a set of chat messages - either replaying existing messages
#   or streaming new ones.
# - handle_feedback() - Draws a feedback widget and records feedback from the user.

# The app heavily uses AgentClient to interact with the agent's FastAPI endpoints.


APP_TITLE = "Agent Test with langgraph , fastapi , streamlit"
APP_ICON = "🧰"
USER_ID_COOKIE = "user_id"


def get_or_create_user_id() -> str:
    #===============================================================================================================
    # USER_ID 정보를 session_state 또는 URL 파라미터에서 가져오거나 새로 생성하여 반환
    #===============================================================================================================
    if USER_ID_COOKIE in st.session_state:
        return st.session_state[USER_ID_COOKIE]

    # 현재 URL 파라미터에서 USER_ID_COOKIE 파라미터가 있는 경우 해당 값을 session_state에 저장하고 반환
    if USER_ID_COOKIE in st.query_params:
        user_id = st.query_params[USER_ID_COOKIE]
        st.session_state[USER_ID_COOKIE] = user_id
        return user_id
    print("USER_ID_COOKIE 파라미터가 없는 경우 새로 생성")
    user_id = str(uuid.uuid4())
    
    #===============================================================================================================
    # session_state, URL 파라미터에 USER_ID_COOKIE 파라미터 저장
    # st.query_params를 새롭게 지정하면 URL의 쿼리 파라미터가 즉시 변경되고, 스트림릿 앱이 재실행
    #===============================================================================================================
    # Store in session state for this session
    st.session_state[USER_ID_COOKIE] = user_id

    # Also add to URL parameters so it can be bookmarked/shared
    st.query_params[USER_ID_COOKIE] = user_id

    return user_id

#===============================================================================================================
# 메인 함수
#===============================================================================================================
async def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        menu_items={},
    )

    # if st.get_option("client.toolbarMode") != "minimal":
    #     st.set_option("client.toolbarMode", "minimal")
    #     await asyncio.sleep(0.1)
    #     st.rerun()

    # Get or create user ID
    user_id = get_or_create_user_id()
    #===============================================================================================================
    # 에이전트 초기화 (AgentClient 초기화) 후 session_state.agent_client에 AgentClient 객체 저장
    #===============================================================================================================
    if "agent_client" not in st.session_state:
        host = settings.HOST
        port = settings.PORT
        agent_endpoint = settings.AGENT_ENDPOINT
        agent_url = f"http://{host}:{port}{agent_endpoint}"
        try:
            with st.spinner("Connecting to agent service..."):
                print("AgentClient 초기화 시작")
                st.session_state.agent_client = AgentClient(base_url=agent_url)
        except AgentClientError as e:
            st.error(f"Error connecting to agent service at {agent_url}: {e}")
            st.markdown("The service might be booting up. Try again in a few seconds.")
            st.stop()
    
    agent_client: AgentClient = st.session_state.agent_client


    #==================================================================================================================
    # thread_id 초기화 (session_state , URL 파라미터에 thread_id 가 없는 경우 새로운 thread_id 생성 , 있는 경우 기존 대화 내역 불러오기)
    # 새로운 창에서 접속하는 경우 st.session_state는 공유 하지 않으므로 thread_id 값을 얻기 위해서 URL 파라미터에서 가져옴
    #==================================================================================================================
    if "thread_id" not in st.session_state:
        thread_id = st.query_params.get("thread_id")
        agent_client.agent = st.query_params.get("agent")

        messages = []
        if not thread_id:
            logger.info("thread_id 가 없는 경우 새로운 thread_id 생성")
            thread_id = str(uuid.uuid4())
            messages = []
        else:
            try:
                logger.info(f"thread_id 가 session_state에 없지만 쿼리 파라미터에 있는 경우 기존 대화 내역 불러오기: {thread_id}")
                messages: ChatHistory = agent_client.get_history(thread_id=thread_id).messages
            except AgentClientError:
                st.error("No message history found for this Thread ID.")
                messages = []
        st.session_state.messages = messages
        st.session_state.thread_id = thread_id
    # else:
    #     print(f"thread_id: {st.session_state.thread_id}")
    #     print(f"messages: {st.session_state.messages}")

    #===============================================================================================================
    # Sidebar 설정  (사용자 입력 메세지 입력창 , 모델 선택 , agent 선택 , 스트리밍 모드 선택 , 사용자 ID , 대화 스레드 ID 출력)
    #===============================================================================================================
    with st.sidebar:
        st.header(f"{APP_ICON} {APP_TITLE}")

        ""
        "AI agent service built with LangGraph, FastAPI and Streamlit"
        ""

        if st.button(":material/chat: New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.rerun()
        
       
        
        #===============================================================
        # 사용 가능한 모델 , agent 선택 및 streaming 모드 설정 
        #===============================================================
        with st.popover(":material/settings: Settings", use_container_width=True):
            model_idx = agent_client.info.models.index(agent_client.info.default_model)
            model = st.selectbox("LLM to use", options=agent_client.info.models, index=model_idx)
            agent_list = [a for a in agent_client.info.agents]
            agent_idx = agent_list.index(agent_client.info.default_agent if agent_client.agent is None else agent_client.agent)
            agent_client.agent = st.selectbox(
                "Agent to use",
                options=agent_list,
                index=agent_idx,
            )
            use_streaming = st.toggle("Stream results", value=True)

            # Display user ID (for debugging or user information)
            st.text_input("User ID (read-only)", value=user_id, disabled=True)
            st.text_input("Thread ID (read-only)", value=st.session_state.thread_id, disabled=True)
            logger.info(f"Agent: {agent_client.agent} selected!")
            

        #===============================================================
        # 이전 채팅 공유 기능
        #===============================================================
        @st.dialog("Share/resume chat")
        def share_chat_dialog() -> None:
            session = st.runtime.get_instance()._session_mgr.list_active_sessions()[0]
            st_base_url = urllib.parse.urlunparse(
                [session.client.request.protocol, session.client.request.host, "", "", "", ""]
            )
            # if it's not localhost, switch to https by default
            # if not st_base_url.startswith("https") and "localhost" not in st_base_url:
            #     st_base_url = st_base_url.replace("http", "https")
            # Include both thread_id and user_id in the URL for sharing to maintain user identity
            chat_url = (
                f"{st_base_url}?thread_id={st.session_state.thread_id}&{USER_ID_COOKIE}={user_id}&agent={agent_client.agent}"
            )
            st.markdown(f"**Chat URL:**\n```text\n{chat_url}\n```")
            st.info("Copy the above URL to share or revisit this chat")

        if st.button(":material/upload: Share/resume chat", use_container_width=True):
            share_chat_dialog()

         # Delete chat history button
        if st.button(":material/delete: Delete Chat History", use_container_width=True):
            try:
                with st.spinner("Deleting chat history..."):
                    agent_client.delete_history(thread_id=st.session_state.thread_id)
                st.success("Chat history deleted successfully!")
                # Clear the current messages and create a new thread
                st.session_state.messages = []
                st.session_state.thread_id = str(uuid.uuid4())
                st.rerun()
            except AgentClientError as e:
                st.error(f"Error deleting chat history: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")


    # # Draw existing messages
    messages: list[ChatMessage] = st.session_state.messages

    #===============================================================
    # 이전 채팅 메세지가 없는 경우 agent 종류에 따른 소개 메세지 추가 
    #===============================================================
    if len(messages) == 0:
        match agent_client.agent:
            case "chatbot":
                WELCOME = "Hello! I'm a simple chatbot. Ask me anything!"
            case "interrupt-agent":
                WELCOME = "Hello! I'm an interrupt agent. Tell me your birthday and I will predict your personality!"
            case "research-assistant":
                WELCOME = "Hello! I'm an AI-powered research assistant with web search and a calculator. Ask me anything!"
            case "rag-assistant":
                WELCOME = """Hello! I'm an AI-powered Company Policy & HR assistant with access to AcmeTech's Employee Handbook.
                I can help you find information about benefits, remote work, time-off policies, company values, and more. Ask me anything!"""
            case _:
                WELCOME = "Hello! I'm an AI agent. Ask me anything!"

        with st.chat_message("ai"):
            st.write(WELCOME)
    
    #===============================================================================================================
    # st.session_state.messages에 저장된 기존의 메시지인 list[ChatMessage]를 출력(이때는 리스트에 담긴 ChatMessage 객체를 하나씩 출력)
    #===============================================================================================================
    # draw_messages() expects an async iterator over messages
    async def amessage_iter() -> AsyncGenerator[ChatMessage, None]:
        for m in messages:
            yield m

    await draw_messages(amessage_iter())

    #===============================================================================================================
    # 사용자가 채팅창에 입력을 한 경우 => AgentClient를 통해 fastapi 서버에 API 요청 => 스트리밍여부에 따라 API 응답결롸를 출력 
    #===============================================================================================================
    
    if user_input := st.chat_input():
        messages.append(ChatMessage(type="human", content=user_input))
        st.chat_message("human").write(user_input)
        try:
            #===============================================================
            # 스트리밍 모드시 AgentClient.astream() 호출 => fastapi의 /api/langgraph/{agent_name}/stream 엔드포인트 호출
            #  => API 응답결과(SSE 방식) 수신 => 계속 수신받은 문자열 파싱 후 => ChatMessage | str 형식의 비동기 Generator를 반환 ("token" 타입인 경우 str 반환 )
            #  => draw_messages() 함수를 통해 비동기 Generator 처리
            #===============================================================
            if use_streaming:
                stream:AsyncGenerator[ChatMessage|str, None] = agent_client.astream(
                    message=user_input,
                    model=model,
                    thread_id=st.session_state.thread_id,
                    user_id=user_id,
                )
                await draw_messages(stream, is_new=True)

            #===============================================================
            # 스트리밍 모드가 아닌 경우 AgentClient.ainvoke() 호출 => fastapi의 /api/langgraph/{agent_name}/invoke 엔드포인트 호출
            #  => API 응답결과 수신(ChatMessage) => st.session_state.messages에 ChatMessage 추가 , ChatMessage.content 출력
            #===============================================================
            else:
                response: ChatMessage = await agent_client.ainvoke(
                    message=user_input,
                    model=model,
                    thread_id=st.session_state.thread_id,
                    user_id=user_id,
                )
                messages.append(response)
                st.chat_message("ai").write(response.content)
            st.rerun()  # Clear stale containers
        except AgentClientError as e:
            st.error(f"Error generating response: {e}")
            st.stop()

    #===============================================================
    # 메세지가 생성된 경우 피드백 위젯 표시
    #===============================================================
    # If messages have been generated, show feedback widget
    # if len(messages) > 0 and st.session_state.last_message:
    #     with st.session_state.last_message:
    #         await handle_feedback()



if __name__ == "__main__":
    asyncio.run(main())
