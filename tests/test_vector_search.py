from wrapper.search_wrapper import VectorSearchAPIWrapper
import pytest
from urllib.parse import urlparse
from dotenv import load_dotenv
load_dotenv()

from agents.search.search import build_graph
import httpx
from langchain_core.runnables import RunnableConfig
from utils.messages import langchain_to_chat_message
from langchain_core.messages import AIMessageChunk
# from aws import S3Manager
# vector_search_api_wrapper = VectorSearchAPIWrapper()
# s3_manager = S3Manager(region_name="ap-northeast-2", bucket_name="sw-fashion-image-data")
client = httpx.AsyncClient()
graph = build_graph(client)

@pytest.fixture
def user_input():
    return {
        "config": RunnableConfig(configurable={"thread_id": "test_thread_id"}),
        "input": {"messages": ["test"]},
    }

@pytest.mark.asyncio
async def test_vector_search(user_input):
    async for stream_event in graph.astream(**user_input , stream_mode=["updates", "messages" , "custom"] , subgraphs=True):
        _ , stream_mode_type , data = stream_event

        filtered_messages = []
        if stream_mode_type == "updates":
            for node_name , updates in data.items():
                updated_messages = updates.get("messages" , [])
                filtered_messages.extend(updated_messages)
    
            for message in filtered_messages:
                try :
                    chat_message = langchain_to_chat_message(message)
                except Exception as e:
                    print(e)
                print("[updates_mode] : data =>  " , f"data: {{'type' : 'message' , 'content' : {chat_message.model_dump()}}}")

        elif stream_mode_type == "messages":
            msg , metadata = data
            if not isinstance(msg, AIMessageChunk):
                continue
            print("[messages_mode] : data =>  " , f"data: {{'type' : 'token' , 'content' : {msg.content}}}")
        elif stream_mode_type == "custom":
            type , content = data["type"] , data["content"]
            print("[custom_mode] : data =>  " ,  f"data: {{'type' : {type} , 'content' : {content} }}")
        

        

@pytest.mark.asyncio
async def test_vector_search_invoke(user_input):
    result = await graph.ainvoke(**user_input)
    print(result)

def parse_s3_key(url_string: str) -> str:
    """
    Parses an S3 URL to extract the key.
    
    Args:
        url_string: The full S3 URL string, including bucket and query parameters.
    
    Returns:
        The S3 key as a string.
    """
    # Parse the URL into components
    parsed_url = urlparse(url_string)
    
    # The S3 key is the path, which starts with a '/'
    s3_key_with_leading_slash = parsed_url.path
    
    
    # Remove the leading '/'
    s3_key = s3_key_with_leading_slash.lstrip('/')

    return s3_key

# def test_parse_s3_key(get_url):
#     s3_key = parse_s3_key(get_url)
#     print(s3_key)
    # print(s3_manager.generate_presigned_url(s3_key))

