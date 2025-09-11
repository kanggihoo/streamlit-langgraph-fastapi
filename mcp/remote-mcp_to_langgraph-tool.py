from langchain_mcp_adapters.client import MultiServerMCPClient


#===============================================================================================================
# 예제 관련
'''
client = MultiServerMCPClient(
    {
        "server-sequential-thinking": {
            "command": "npx",
            "args": [
                "-y",
                "@smithery/cli@latest",
                "run",
                "@smithery-ai/server-sequential-thinking",
                "--key",
                "89a4780a-53b7-4b7b-92e9-a29815f2669b",
            ],
            "transport": "stdio",  # stdio 방식으로 통신을 추가합니다.
        },
        "desktop-commander": {
            "command": "npx",
            "args": [
                "-y",
                "@smithery/cli@latest",
                "run",  
                "@wonderwhy-er/desktop-commander",
                "--key",
                "89a4780a-53b7-4b7b-92e9-a29815f2669b",
            ],
            "transport": "stdio",  # stdio 방식으로 통신을 추가합니다.
        },
        # 나만의 MCP 서버를 이용하는 경우에 (FastMCP 서버를 구동시키는 명령어로 )
        "document-retriever": {  
            "command": "./.venv/bin/python",
            # mcp_server_rag.py 파일의 절대 경로로 업데이트해야 합니다
            "args": ["./mcp_server_rag.py"],
            # stdio 방식으로 통신 (표준 입출력 사용)
            "transport": "stdio",
        },
    }
)
'''
#===============================================================================================================



#===============================================================================================================
# remote 환경으로 제공하는 Exa MCP 서버 정보 가져오기 
#===============================================================================================================
from dotenv import load_dotenv
load_dotenv()
import os
async def main():
    client = MultiServerMCPClient({
            "weather": {
                "url": f"https://mcp.exa.ai/mcp?exaApiKey={os.getenv('EXA_API_KEY')}",
                "transport": "streamable_http",
            }
        }
    )
    tools = await client.get_tools()
    print(tools)
    


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())