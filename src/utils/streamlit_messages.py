import streamlit as st
from model.schema import ChatMessage
from typing import AsyncGenerator


async def draw_messages(
    messages_agen: AsyncGenerator[ChatMessage|str , None],
    is_new: bool = False,
) -> None:
    """
    1. 기존 세션에 있는 메시지를 다시 출력(단순 출력)
    2. API 요청으로 새롭게 받은 메시지를 스트리밍으로 출력
    이 함수에는 스트리밍 토큰 및 도구 호출을 처리하는 추가 논리가 포함되어 있습니다.
    스트리밍 토큰이 도착하면 렌더링하기 위해 플레이스홀더 컨테이너를 사용합니다.
    도구 호출을 렌더링하기 위해 상태 컨테이너를 사용합니다. 도구 입력과 출력을 추적하고 그에 따라 상태 컨테이너를 업데이트합니다.

    이 함수는 이후 메시지가 동일한 컨테이너에 그려질 수 있으므로, 세션 상태에서 마지막 메시지 컨테이너를 추적해야 합니다. 이는 또한 최신 채팅 메시지에 피드백 위젯을 그리는 데에도 사용됩니다.
    Args:
        messages_aiter (AsyncGenerator[ChatMessage | None]): 비동기 제너레이터로 , 해당 제너레이러부터 메시지를 출력 
        is_new (bool): 메시지가 기존 세션에 있는 메시지인지, 아니면 새롭게 받은 메시지인지 여부. (default: False)
    """


    #===============================================================================================================
    # 마지막 메세지 타입 추적 (같은 메세지 타입이 연속으로 오는 경우에 같은 컨테이너에 출력되도록 하기 위해 추적)
    # human => ai 인 경우에는 서로 다른 컨테이너에 출력 , ai => ai 인 경우 같은 컨테이너에 출력
    #===============================================================================================================
    last_message_type = None
    st.session_state.last_message = None

    # Placeholder for intermediate streaming tokens
    streaming_content = ""
    streaming_placeholder = None

    #===============================================================================================================
    # 비동기 제너레이터로 부터 반복하여 하나씩 데이터를 가져온뒤 streamlit ui에 출력
    #===============================================================================================================
    # async for msg in messages_agen:
    while msg := await anext(messages_agen, None):

        #===============================================================================================================
        # "token" 타입인 경우 스트리밍 토큰 처리, streaming_placeholder가 비어있으면 첫번째 토큰인 경우 처리
        # => 첫번째 토큰을 받은경우 스트리밍 출력을 위한 빈 공간 생성(st.empty())=> 토큰 메세지를 누적한뒤 빈 공간에 계속 출력 
        # 참고 : st.empty()는 빈 공간을 생성하는 함수로, 그 안에 다른 Streamlit 요소를 써서 내용을 덮어쓸 수 있습니다.
        #===============================================================================================================
        if isinstance(msg, str):
            if not streaming_placeholder:
                if last_message_type != "ai":
                    last_message_type = "ai"
                    st.session_state.last_message = st.chat_message("ai")
                with st.session_state.last_message:
                    streaming_placeholder = st.empty()

            streaming_content += msg
            streaming_placeholder.write(streaming_content)
            continue
        
        # 오류 처리 
        if not isinstance(msg, ChatMessage):
            st.error(f"Unexpected message type: {type(msg)}")
            st.write(msg)
            st.stop()


        #===============================================================================================================
        # "message" 타입인 경우 ChatMessage 형식의 데이터 처리(src/model/schema.py 참고)
        #===============================================================================================================
        match msg.type:
            
            # 사용자가 입력한 메세지 처리
            case "human":
                last_message_type = "human"
                st.chat_message("human").write(msg.content)

            #===============================================================================================================
            # 에이전트가 반환한 메세지 처리, 가장 복잡한 케이스, 스트리밍 토큰과 도구 호출을 처리해야 함
            #===============================================================================================================
            case "ai":

                # API 요청으로 부터 새롭게 받은 메세지인 경우 세션에 추가 
                if is_new:
                    st.session_state.messages.append(msg)

                # 마지막 메세지 타입이 AI가 아닌 경우, 새로운 채팅 메세지 생성
                if last_message_type != "ai":
                    last_message_type = "ai"
                    st.session_state.last_message = st.chat_message("ai")

                with st.session_state.last_message:
                    #===============================================================================================================
                    # 메세지 콘텐츠 처리(먼저 token을 st.empty()에 출력하고 , 그 뒤에 완전한 메세지가 도착하면 다시한번 출력하고 다음 토큰 처리를 위한 초기화 과정
                    # 그리고 다음 토큰 출력을 처리하기 위한 streaming_content , streaming_placeholder 초기화 
                    # token 없이 바로 message가 도착하는 경우 (llm 출력이 아닌 특정 노드의 결과를 보고 싶은 겨우)는 st.write()로 출력 해서 새로운 채팅 메세지 컨테이너를 생성 ?
                    #===============================================================================================================
                    #TODO : 여기서 msg.additional_kwargs를 처리해서 이미지 타입인지, 텍스트 타입인지 처리해서 이미지인경우 이미지 url를 바탕으로 출력 
                    if msg.content:
                        if streaming_placeholder:
                            print("ai 메세지 이면서 streaming_placeholder가 있고, stream_mode= update인 경우 \n" , msg)
                            # streaming_placeholder.write(msg.content)
                            streaming_content = ""
                            streaming_placeholder = None
                        else:
                            st.write(msg.content)


                    #===============================================================================================================
                    # 도구 호출 처리(전달받은 ChatMessage 객체의 tool_calls 필드의 list[ToolCall] 스키마 이용)
                    # st.status() 함수를 이용하여 도구 호출처리(데이터 진행 상태 시각화)
                    #===============================================================================================================
                    if msg.tool_calls:
                        
                        # type = "ai" 이면서 tool_calls 필드가 있는 경우 st.status() 함수에 tool name , id , args를 파싱한 후 상태 컨테이너 생성
                        call_results = {}
                        for tool_call in msg.tool_calls:
                            status = st.status(
                                f"""Tool Call: {tool_call["name"]}""",
                                state="running" if is_new else "complete",
                                expanded=False,
                            )
                            call_results[tool_call["id"]] = status
                            status.write("Input:")
                            status.write(tool_call["args"])

                        #===============================================================================================================
                        # 가정 : tool_calls 가 포함된 ai 메세지를 받은 후 tool_calls 안에 있는 개수 만큼 다음 메세지는 도구 호출 결과가 담기 tool 메세지를 받음.
                        # 따라서 해당 도구 호출의 결과를 처리하기 위해서 await anext(messages_agen) 함수를 통해 도구 호출 결과 처리 
                        #===============================================================================================================
                        for tool_call in msg.tool_calls:
                            # if "transfer_to" in tool_call["name"]:
                            #     await _handle_agent_msgs(messages_agen, call_results, is_new)
                            #     break
                            tool_result: ChatMessage = await anext(messages_agen)

                            # 우리는 해당 이전의 tool_calls에서 파싱한 실제 도구 호출결과를 기대 했지만 type = tool 인 경우가 아닌 경우 오류 처리
                            if tool_result.type != "tool":
                                st.error(f"Unexpected ChatMessage type: {tool_result.type}")
                                st.write(tool_result)
                                st.stop()

                            
                            # 새로운 메세지인 경우 세션에 추가(실제 도구 호출 결과)
                            if is_new:
                                st.session_state.messages.append(tool_result)
                            
                            # tool_call_id에 맞는 도구 호출 결과에 대한 상태 컨테이너에 도구 호출 결과 출력 
                            if tool_result.tool_call_id:
                                status = call_results[tool_result.tool_call_id]
                            status.write("Output:")
                            status.write(tool_result.content)
                            status.update(state="complete")

            # case "custom":
            #     # CustomData example used by the bg-task-agent
            #     # See:
            #     # - src/agents/utils.py CustomData
            #     # - src/agents/bg_task_agent/task.py
            #     try:
            #         task_data: TaskData = TaskData.model_validate(msg.custom_data)
            #     except ValidationError:
            #         st.error("Unexpected CustomData message received from agent")
            #         st.write(msg.custom_data)
            #         st.stop()

            #     if is_new:
            #         st.session_state.messages.append(msg)

            #     if last_message_type != "task":
            #         last_message_type = "task"
            #         st.session_state.last_message = st.chat_message(
            #             name="task", avatar=":material/manufacturing:"
            #         )
            #         with st.session_state.last_message:
            #             status = TaskDataStatus()

            #     status.add_and_draw_task_data(task_data)

            # In case of an unexpected message type, log an error and stop
            case _:
                st.error(f"Unexpected ChatMessage type: {msg.type}")
                st.write(msg)
                st.stop()


#TODO : 이 메서드에 대해서도 살펴보기 
async def _handle_agent_msgs(
    messages_agen: AsyncGenerator[ChatMessage|str , None], 
    call_results : dict[str, st.status], 
    is_new: bool,
    ) -> None:
    """
    This function segregates agent output into a status container.
    It handles all messages after the initial tool call message
    until it reaches the final AI message.

    Args:
        messages_agen (AsyncGenerator[ChatMessage|str , None]): 비동기 제너레이터로 , 해당 제너레이러부터 메시지를 출력
        call_results (dict[str, st.status]): 도구 호출 결과를 저장하는 딕셔너리로 tool_id에 대한 st.status.container를 담고 있음.
        is_new (bool): 메시지가 기존 세션에 있는 메시지인지, 아니면 새롭게 받은 메시지인지 여부. (default: False)
    """
    nested_popovers = {}
    # looking for the Success tool call message
    first_msg = await anext(messages_agen)
    if is_new:
        st.session_state.messages.append(first_msg)
    status = call_results.get(getattr(first_msg, "tool_call_id", None))
    # Process first message
    if status and first_msg.content:
        status.write(first_msg.content)
        # Continue reading until finish_reason='stop'
    while True:
        # Check for completion on current message
        finish_reason = getattr(first_msg, "response_metadata", {}).get("finish_reason")
        # Break out of status container if finish_reason is anything other than "tool_calls"
        if finish_reason is not None and finish_reason != "tool_calls":
            if status:
                status.update(state="complete")
            break
        # Read next message
        sub_msg = await anext(messages_agen)
        # this should only happen is skip_stream flag is removed
        # if isinstance(sub_msg, str):
        #     continue
        if is_new:
            st.session_state.messages.append(sub_msg)

        if sub_msg.type == "tool" and sub_msg.tool_call_id in nested_popovers:
            popover = nested_popovers[sub_msg.tool_call_id]
            popover.write("**Output:**")
            popover.write(sub_msg.content)
            first_msg = sub_msg
            continue
        # Display content and tool calls using the same status
        if status:
            if sub_msg.content:
                status.write(sub_msg.content)
            if hasattr(sub_msg, "tool_calls") and sub_msg.tool_calls:
                for tc in sub_msg.tool_calls:
                    popover = status.popover(f"{tc['name']}", icon="🛠️")
                    popover.write(f"**Tool:** {tc['name']}")
                    popover.write("**Input:**")
                    popover.write(tc["args"])
                    # Store the popover reference using the tool call ID
                    nested_popovers[tc["id"]] = popover
        # Update first_msg for next iteration
        first_msg = sub_msg