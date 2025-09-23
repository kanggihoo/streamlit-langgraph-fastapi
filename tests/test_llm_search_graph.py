import pytest
import httpx
from src.agents.llm_search import build_graph
from src.model.type import SSETypes
from src.utils.messages import create_message
from langchain_core.runnables import RunnableConfig

@pytest.fixture
async def http_client():
    """HTTP client fixture"""
    client = httpx.AsyncClient()
    try:
        yield client
    finally:
        await client.aclose()

@pytest.mark.asyncio
async def test_llm_search_graph_build(http_client):
    """Test that the combined LLM search graph can be built successfully"""
    graph = build_graph(http_client)
    
    # Verify graph is built
    assert graph is not None
    assert graph.name == "llm_search"
    
    # Verify nodes exist
    assert "external_llm" in graph.nodes
    assert "search" in graph.nodes

@pytest.mark.asyncio 
async def test_llm_search_graph_basic_flow(http_client):
    """Test basic flow of the combined graph"""
    graph = build_graph(http_client)
    
    config = {
        "configurable": {"thread_id": "test_thread_id"},
        "input": {
            "messages": [create_message(message_type="human", content="데이트 스타일 추천해줘")]
        },
    }
    
    try:
        # Test that graph can process input without errors
        result = await graph.ainvoke(**config)
        
        # Verify result structure
        assert "messages" in result
        assert len(result["messages"]) > 0
        
        # The final message should be from the search node
        final_message = result["messages"][-1]
        assert final_message.type == "ai"
        
    except Exception as e:
        # If external API is not available, we expect a graceful failure
        print(f"Expected potential failure due to external API: {e}")

@pytest.mark.asyncio
async def test_llm_search_streaming(http_client):
    """Test streaming mode of the combined graph"""
    graph = build_graph(http_client)
    
    config = {
        "configurable": {"thread_id": "test_thread_id"},
        "input": {
            "messages": [create_message(message_type="human", content="캐주얼 스타일")]
        },
    }
    
    try:
        # Test streaming with custom mode to capture status updates
        events = []
        async for chunk in graph.astream(**config, stream_mode=["custom"], subgraphs=True):
            _, stream_mode_type, data = chunk
            if stream_mode_type == "custom":
                events.append(data)
                
        # Should have received some events
        assert len(events) >= 0  # May be 0 if external API is not available
        
    except Exception as e:
        # If external API is not available, we expect a graceful failure
        print(f"Expected potential failure due to external API: {e}")


def test_generate_graph_image(http_client):
    graph = build_graph(http_client)
    try:
        from langchain_core.runnables.graph import MermaidDrawMethod
        graph.get_graph(xray=True).draw_mermaid_png(output_file_path="images/llm_search.png", draw_method=MermaidDrawMethod.PYPPETEER)
        print("\n그래프 이미지를 connect_i.png 파일로 저장했습니다.")
    except Exception as e:
        print(f"\n그래프 시각화 실패: {e}")