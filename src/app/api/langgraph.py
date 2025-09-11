from langchain_core.messages import AIMessage , AnyMessage
from langchain_core.runnables import RunnableConfig

from fastapi import APIRouter , HTTPException , status , Path
from fastapi.responses import StreamingResponse

import logging 
from typing import Any , cast ,Annotated

from app.config.dependencies import AgentDep
from agents import get_all_agent_info , DEFAULT_AGENT_NAME , get_agent
from utils import langchain_to_chat_message , handle_user_input , message_generator
from settings import settings
from model.schema import ServiceMetadata , UserInput , ChatMessage , StreamInput, ChatHistory , ChatHistoryInput

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/langgraph" , tags=["langgraph"])

@router.get("/info")
async def get_info()->ServiceMetadata:
    try:
        models = settings.AVAILABLE_LLM_MODELS
        return ServiceMetadata(
            agents=get_all_agent_info(),
            models=list(models),
            default_model=settings.DEFAULT_LLM_MODEL,
            default_agent=DEFAULT_AGENT_NAME,
        )
    except Exception as e:
        logger.error(f"Error getting info: {e}")
        raise e


@router.post("/{agent_name}/invoke")
async def invoke(user_input:UserInput , agent:AgentDep)->ChatMessage:

    # agent:CompiledStateGraph = get_agent(agent_name)
    kwargs , run_id = await handle_user_input(user_input , agent)

    try:
        response_events: list[tuple[str, Any]] = await agent.ainvoke(**kwargs, stream_mode=["updates", "values"])  # type: ignore # fmt: skip
        response_type, response = response_events[-1]
        if response_type == "values":
            # Normal response, the agent completed successfully
            output = langchain_to_chat_message(response["messages"][-1]) # 맨 마지막 message에 대해서 변환
        elif response_type == "updates" and "__interrupt__" in response:
            # The last thing to occur was an interrupt
            # Return the value of the first interrupt as an AIMessage
            output = langchain_to_chat_message(
                AIMessage(content=response["__interrupt__"][0].value)
            )
        else:
            raise ValueError(f"Unexpected response type: {response_type}")

        output.run_id = str(run_id)
        return output
    except Exception as e:
        logger.error(f"An exception occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")



def _sse_response_example()->dict[str, Any]:
    return {
        status.HTTP_200_OK : {
            "description" : "Successful response",
            "content" : {
                "text/event-stream" : {
                    "example" : "data: {'type': 'token' , 'content': 'Hello, world!'}\n\n",
                    "schema" : {"type" : "string"}
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR : {
            "description" : "Internal server error",
            "content" : {
                "text/event-stream" : {
                    "example" : "data: {'type': 'error' , 'content': 'Internal server error'}\n\n",
                    "schema" : {"type" : "string"}
                }
            }
        }
    }

@router.post(
        "/{agent_name}/stream",
        response_class = StreamingResponse,
        responses= _sse_response_example(),
        response_model=ChatMessage
)
async def stream(
    user_input:StreamInput , 
    agent:AgentDep,
    )->ChatMessage:
    return StreamingResponse(
        message_generator(user_input , agent),
        media_type="text/event-stream",
    )



@router.get("/{agent_name}/{thread_id}/history" , response_model=ChatHistory)
async def get_history(
    thread_id:Annotated[str, Path],
    agent:AgentDep,
    agent_name:Annotated[str, Path],
)->ChatHistory:
    print(f"agent_name: {agent_name}")
    try:
        state_snapshot = await agent.aget_state(
            config=RunnableConfig(configurable={"thread_id": thread_id})
        )
        messages: list[AnyMessage] = state_snapshot.values["messages"]
        chat_messages: list[ChatMessage] = [langchain_to_chat_message(m) for m in messages]
        return ChatHistory(messages=chat_messages)
    except Exception as e:
        logger.error(f"An exception occurred: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error")

@router.delete("/{thread_id}/history")
async def delete_history(
    thread_id:Annotated[str, Path],
)->None:
    try:
        for agent in get_all_agent_info():
            await get_agent(agent).checkpointer.adelete_thread(thread_id)
    except Exception as e:
        logger.error(f"An exception occurred: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error")

