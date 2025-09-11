from langchain_core.tools import tool
from app.services import VectorSearchAPIWrapper

search_api_wrapper = VectorSearchAPIWrapper()

@tool(parse_docstring=True , name_or_callable = "vector_search")
async def vector_search(query: str) -> dict:
    """
    입력 쿼리에 대한 실제 의류 이미지를 검색합니다. 
    쿼리에 대한 결과는 딕셔너리 형태로 다음과 같은 정보가 반영됩니다.
    {
        "message": "검색 결과",
        "data": [
            {
                "product_id": "제품 고유 식별자",
                "image_url": "제품 이미지 URL",
                "score": "유사도 점수(0~1)",
                "caption": "제품 캡션 내용",
            }
        ]
    }

    Args:
        query (str): 검색 쿼리

    Returns:
        dict: 검색 결과
    """
    return await search_api_wrapper.search(query)