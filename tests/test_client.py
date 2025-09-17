
from settings import settings
from client.client import AgentClient
import pytest

host = settings.HOST
port = settings.PORT
agent_endpoint = settings.AGENT_ENDPOINT
agent_url = f"http://{host}:{port}{agent_endpoint}"
client = AgentClient(base_url=agent_url , agent="search")

@pytest.mark.asyncio
async def test_client():
    async for chunk in client.astream(
        message="test", 
        model="",
        thread_id= "1",
        stream_tokens = True,
    ):
        print(chunk , type(chunk))
