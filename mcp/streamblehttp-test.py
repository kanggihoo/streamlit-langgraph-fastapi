# from mcp import ClientSession
# from mcp.client.streamable_http import streamablehttp_client

# # Construct server URL with authentication
# from urllib.parse import urlencode
# base_url = "https://server.smithery.ai/@smithery-ai/server-sequential-thinking/mcp"
# params = {"api_key": "f0bfa51f-ebd9-4fee-b10d-4f0a5327728e", "profile": "sore-vulture-Dea3mE"}
# url = f"{base_url}?{urlencode(params)}"

# async def main():
#     # Connect to the server using HTTP client
#     async with streamablehttp_client(url) as (read, write, _):
#         async with ClientSession(read, write) as session:
#             # Initialize the connection
#             await session.initialize()
            
#             # List available tools
#             tools_result = await session.list_tools()
#             print(f"Available tools: {', '.join([t.name for t in tools_result.tools])}")
#             print(tools_result)

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
'''
 description: str | None = None
"""A human-readable description of the tool."""
inputSchema: dict[str, Any]
"""A JSON Schema object defining the expected parameters for the tool."""
outputSchema: dict[str, Any] | None = None
"""
An optional JSON Schema object defining the structure of the tool's output
returned in the structuredContent field of a CallToolResult.
"""
annotations: ToolAnnotations | None = None
"""Optional additional tool information."""
meta: dict[str, Any] | None = Field(alias="_meta", default=None)
"""
See [MCP specification](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/47339c03c143bb4ec01a26e721a1b8fe66634ebe/docs/specification/draft/basic/index.mdx#general-fields)
for notes on _meta usage.
"""
model_config = ConfigDict(extra="allow")

'''

# Construct server URL with authentication
from urllib.parse import urlencode
base_url = "https://mcp.exa.ai/mcp"
params = {"exaApiKey": "2718cd01-27e5-44b2-a169-b75c6b0a3e08", "profile": "sore-vulture-Dea3mE"}
url = f"{base_url}?{urlencode(params)}"

async def main():
    # Connect to the server using HTTP client
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            tools_result = await session.list_tools()
            result = []
            for t in tools_result.tools:
                result.append({
                    "name": t.name,
                    "description": t.description,
                    "inputSchema": t.inputSchema,
                    "outputSchema": t.outputSchema,
                    "annotations": t.annotations,
                    "meta": t.meta,
                })
            import pprint
            
            # 도구 호출
            tool_result = await session.call_tool(
                "web_search_exa",
                {"query": "2025 한국 남성 의류 트렌드 www.youtube.com에서 검색" , "numResults": 1},
            )
            print(tool_result)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())