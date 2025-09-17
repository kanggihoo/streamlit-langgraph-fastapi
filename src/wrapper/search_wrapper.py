
import httpx
from typing import Any
class VectorSearchAPIWrapper:
    def __init__(self , client:httpx.AsyncClient):
        """
        클래스 초기화 시, 재사용 가능한 httpx.AsyncClient와 공통 헤더를 설정합니다.
        """
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        self.client = client
        self.headers={"User-Agent": self.user_agent, "accept": "application/json"}
        self.timeout=10.0
        self.protocol = "http"
        self.fastapi_ip = "3.36.171.231"
        self.fastapi_port = "8000"
        self.base_url = f"{self.protocol}://{self.fastapi_ip}:{self.fastapi_port}/api/v1"
    
    async def search(self, query: str , limit: int = 1) -> dict[str, Any]:
        payload = {
            "messages": query,
            "limit": limit
        }
        try:
            response = await self.client.post(f"{self.base_url}/search/", json=payload , headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            raw_data = response.json()
            message = raw_data.get("message")
            data = raw_data.get("data").get("data")
            is_success = raw_data.get("success", False)
            if not is_success:
                return {
                    "success": is_success,
                    "message": message,
                    "data": [],
                }
            result = []
            for item in data:
                result.append({
                    "product_id": item.get("_id"),
                    "image_url": item.get("image_url"),
                    "score": item.get("score"),
                    "caption": item.get("products",{}).get("captions",{}).get("comprehensive_description", ""),
                })
            return {
                "success": is_success,
                "message": message,
                "data": result,
            }
                
        except Exception as e:
            return {
                "success": is_success,
                "message": f"벡터 검색 결과를 찾을 수 없습니다. (이유: {str(e)})",
                "data": [],
            }
            

