import httpx
from typing import Annotated, Literal, Dict, Any, List, Union

#TODO : FAST API로 부터 API 호출 => 뭔가 잘못된 경우 404 오류 code 반환됨.
class ErrorType:
    NO_DATA = "NO_RECOMMENDATION_DATA"
    HTTP_ERROR = "HTTP_ERROR"
    UNKNOWN = "UNKNOWN_EXCEPTION"
    NO_OPTIONS = "NO_SELECTION_OPTIONS"
    API_ERROR = "API_REQUEST_FAILED"
    REGEX_MATCH_FAILED = "REGEX_MATCH_FAILED"
    JSON_PARSING_FAILED = "JSON_PARSING_FAILED"
    INVALID_REQUEST = "INVALID_REQUEST"

import functools 

def handle_error(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 422:
                return {
                    "message": ErrorType.INVALID_REQUEST,
                    "code": e.response.status_code
                    
                }
            return {
                "message": f"API 서버에 문제가 발생했습니다. {ErrorType.API_ERROR}",
                "code": e.response.status_code
            }
        except Exception as e:
            # 네트워크 오류, JSON 파싱 오류 등 기타 예외 처리
            return {
                "message": f"데이터를 처리하는 중 알 수 없는 오류가 발생했습니다: {str(e)}",
                "error_details": {
                    "error_type": ErrorType.UNKNOWN,
                    "error_message": str(e)
                }
            }
    return wrapper


class MusinsaAPIWrapper:
    """
    FAST API에 등록된 API를 호출하여 llm에게 전달할 데이터를 가공하는 래퍼 클래스입니다.
    httpx.AsyncClient를 사용하여 HTTP 요청을 관리합니다.
    """

    def __init__(self):
        """
        클래스 초기화 시, 재사용 가능한 httpx.AsyncClient와 공통 헤더를 설정합니다.
        """
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        self.client = httpx.AsyncClient(
            headers={"User-Agent": self.user_agent, "accept": "application/json"},
            timeout=10.0
        )
        self.protocol = "http"
        self.fastapi_ip = "3.36.171.231"
        self.fastapi_port = "8000"
        self.base_url = f"{self.protocol}://{self.fastapi_ip}:{self.fastapi_port}/api/v1/musinsa"

    async def close(self):
        """
        애플리케이션 종료 시, httpx.AsyncClient 리소스를 안전하게 닫습니다.
        """
        await self.client.aclose()

    async def _make_request(self, url: str, method: str = "GET", params: dict = None, json: dict = None) -> tuple[bool, Any, str, Dict[str, Any]]:
        """
        API 요청을 보내고 공통 응답을 처리하는 헬퍼 메서드입니다.
        """
        if method.upper() == "GET":
            response = await self.client.get(url, params=params)
        elif method.upper() == "POST":
            response = await self.client.post(url, json=json)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        raw_data = response.json()
        
        is_success = raw_data.get("success", False)
        data = raw_data.get("data")
        message = raw_data.get("message")
        
        return is_success, data, message, raw_data

    @handle_error
    async def get_size_recommend(self, product_id: str | int, height: str | int, weight: str | int) -> dict:
        product_id_str = str(product_id)
        height_str = str(height)
        weight_str = str(weight)
        params = {"height": height_str, "weight": weight_str}
        
        is_success, data, message, raw_data = await self._make_request(
            url=f"{self.base_url}/products/{product_id_str}/size-recommend",
            params=params
        )

        # 2-1. API 응답이 실패했거나 데이터가 없는 경우
        if not is_success or not data:
            return {
                "message": message,
                "error_details": raw_data.get("error_details")
            }
    
        return {
            "message": message,
            "data": data
        }
    

    @handle_error
    async def get_product_selection_info(self, product_id: str | int) -> Dict[str, Any]:
        product_id_str = str(product_id)
        
        is_success, data, message, raw_data = await self._make_request(
            url=f"{self.base_url}/products/{product_id_str}/selection-info"
        )

        # 2. 응답 성공 여부 및 데이터 유무 확인
        if not is_success or not data:
            return {"message": message, "error_details": raw_data.get("error_details")}
        
        # 3. 성공 데이터 가공
        option_info = data[0]
        if option_info.get("option_count") > 1:
            return {
                "message": message,
                "data": {
                    "option_count": option_info.get("option_count"),
                    "first_option_name": option_info.get("first_option_name"),
                    "secondary_option_name": option_info.get("secondary_option_name"),
                    "first_options": [opt.get("name") for opt in option_info.get("first_options", [])],
                    "secondary_options": [opt.get("name") for opt in option_info.get("secondary_options", [])]
                }
            }
        else:
            return {
                "message": message,
                "data": {
                    "option_count": option_info.get("option_count"),
                    "first_option_name": option_info.get("first_option_name"),
                    "first_options": [opt.get("name") for opt in option_info.get("first_options", [])],
                }
            }
        
    @handle_error
    async def get_product_option_stock(self, product_id: str | int) -> Dict[str, Any]:
        product_id_str = str(product_id)
        
        is_success, data, message, raw_data = await self._make_request(
            url=f"{self.base_url}/products/{product_id_str}/option-stock"
        )

        if not is_success or not data:
            return {"message": message, "error_details": raw_data.get("error_details")}
        
        stock_info = data[0]
        stock_list = stock_info.get("stock_by_options", [])

        # 옵션의 종류(예: ["컬러", "사이즈"])를 추출하여 LLM에게 추가 정보 제공
        option_types = []
        for option in stock_info.get("option_filters", []):
            option_types.append({
                "name": option.get("name"),
                "values": [opt.get("name") for opt in option.get("values", [])]
            })
            

        # 최종 결과를 담을 딕셔너리
        # {"블랙(쭈리), S": "구매 가능", "블랙(기모), S": "품절"} 형태가 될 것입니다.
        processed_stock_status = {}
        for stock_item in stock_list:
            # ["블랙(기모)", "S"] -> "블랙(기모), S" 와 같은 문자열 키로 변환
            option_key = ", ".join(stock_item.get("option_combination", []))
            
            # is_sold_out 값에 따라 재고 상태를 텍스트로 변환
            status = "품절" if stock_item.get("is_sold_out") else "구매 가능"
            processed_stock_status[option_key] = status

        return {
            "message": message,
            "data": {
                "option_types": option_types,
                "stock_status": processed_stock_status
            }
        }
        
            
    @handle_error
    async def get_product_size(self, product_id : str | int) -> Dict[str, Any]:
        product_id_str = str(product_id)
        
        is_success, data, message, raw_data = await self._make_request(
            url=f"{self.base_url}/products/{product_id_str}/size-details"
        )

        if not is_success or not data:
            message = raw_data.get("message")
            return {"message": message, "error_details": raw_data.get("error_details")}
        
        # 3. 성공 데이터 가공
        product_info = data[0]
        size_details_list = product_info.get("size_details", [])
        
        # 가공된 실측 정보를 담을 딕셔너리
        # {"S": {"총장": 69, "어깨너비": 46.5, ...}, "M": ...} 형태가 될 것입니다.
        processed_measurements = []

        for size_detail in size_details_list:
            size_name = size_detail.get("size_name")
            
            # 각 사이즈별 측정 항목(items)을 {항목이름: 값} 형태의 딕셔너리로 변환
            measurements = {
                item.get("name"): item.get("value")
                for item in size_detail.get("items", [])
            }
            processed_measurements.append({
                "size_name": size_name,
                "values": measurements
            })

        return {
            "message": message,
            "data": processed_measurements
        }
    
    #CHECK : 스타일 리뷰를 사용하지 않을거면 한달 사용리뷰량 , 일반 리뷰만 반환해도 되지 않을지?
    @handle_error
    async def get_review_summary(self, product_id: str | int) -> str:
        product_id_str = str(product_id)
        
        is_success, data, message, raw_data = await self._make_request(
            url=f"{self.base_url}/products/{product_id_str}/reviews/summary"
        )

        if not is_success or not data:
            return {"message": message, "error_details": raw_data.get("error_details")}
        
        # 3. 성공 데이터 가공
        summary_info = data[0]
        total_count = summary_info.get("total_review_count", 0)
        style_count = summary_info.get("style_review_count", 0)
        monthly_count = summary_info.get("monthly_review_count", 0)
        general_count = summary_info.get("general_review_count", 0)
        avg_rating = summary_info.get("average_rating", 0)

        # LLM이 바로 사용할 수 있는 요약 문장 생성
        return (
            f"리뷰 요약: 총 {total_count}개의 리뷰가 있으며, 평균 평점은 {avg_rating}점입니다. "
            f"(스타일 리뷰: {style_count}개, 한달 사용 리뷰: {monthly_count}개, 일반 리뷰: {general_count}개)"
        )

    @handle_error
    async def get_filtered_review_count(self,
                                    product_id : str | int,
                                    has_photo:bool=False, option_list:List[str] | None = None,
                                    sex:Literal["M", "F"] | None = None)->str:
        product_id_str = str(product_id)
        params = {"has_photo": has_photo, "option_list": option_list, "sex": sex }
        params = {k: v for k, v in params.items() if v}
       
        is_success, data, message, raw_data = await self._make_request(
            url=f"{self.base_url}/products/{product_id_str}/reviews/count", 
            params=params
        )

        if not is_success or not data or "count" not in data[0]:
            message = raw_data.get("message", "리뷰 개수를 조회하지 못했습니다.")
            return f"리뷰 개수를 찾을 수 없습니다. (이유: {message})"
        
        # 4. 성공 데이터 및 필터 조건 가공
        count = data[0]["count"]

        # 4-1. 필터 조건에 대한 설명을 동적으로 생성
        filter_descriptions = []
        if has_photo:
            filter_descriptions.append("사진 포함")
        if option_list:
            filter_descriptions.append(f"옵션: {', '.join(option_list)}")
        if sex == "M":
            filter_descriptions.append("성별: 남성")
        elif sex == "F":
            filter_descriptions.append("성별: 여성")

        # 4-2. 필터 유무에 따라 다른 문장 생성
        if not filter_descriptions:
            return f"해당 상품의 총 리뷰 개수는 {count:,}개입니다."
        else:
            context_str = ", ".join(filter_descriptions)
            return f"요청하신 조건({context_str})에 맞는 리뷰는 총 {count:,}개입니다."

           
    @handle_error
    async def get_review_list(self,
                               product_id: str | int,
                               page_size: int = 10,
                               page: int = 0,
                               option_list: List[str] | None = None,
                               sex: Literal["M", "F"] | None = None,
                               sort: Literal["up_cnt_desc", "new", "comment_cnt_desc", "goods_est_desc", "goods_est_asc"] = "up_cnt_desc",
                               is_experience: bool = False,
                               has_photo: bool = False
                            ) -> Dict[str, Any]:
        product_id_str = str(product_id)
        params = {
            "product_id": product_id_str, 
            "page_size": page_size, 
            "page": page, 
            "sort": sort, 
            "is_experience": is_experience, 
            "has_photo": False,
            "option_list": option_list,
            "sex": sex,
            "sort": sort,
            "is_experience": is_experience
        }
        params = {k: v for k, v in params.items() if v}
        
        is_success, data, message, raw_data = await self._make_request(
            url=f"{self.base_url}/products/{product_id_str}/reviews", 
            params=params
        )

        if not is_success or not data:
            return {"message": message, "error_details": raw_data.get("error_details")}

        # 4. 성공 데이터(리뷰 리스트) 가공
        processed_reviews = []
        for review in data:
            # 4-1. 작성자 정보(user_info)를 하나의 문자열로 가공
            user_info = review.get("user_info", {})
            spec_parts = []
            if user_info.get("sex"):
                spec_parts.append(user_info["sex"])
            if user_info.get("height_cm"):
                spec_parts.append(f"{user_info['height_cm']}cm")
            if user_info.get("weight_kg"):
                spec_parts.append(f"{user_info['weight_kg']}kg")
            
            author_spec = ", ".join(spec_parts) if spec_parts else "정보 없음"

            # 4-2. 날짜 형식을 'YYYY-MM-DD'로 간소화
            created_at = review.get("created_at", "")
            date = created_at.split("T")[0] if "T" in created_at else created_at
            
            # 4-3. LLM에게 필요한 핵심 정보만 담은 간결한 딕셔너리 생성
            processed_reviews.append({
                "rating": review.get("rating"),
                "likes": review.get("like_count"),
                "option": review.get("goods_option"),
                "date": date,
                "author_spec": author_spec,
                "content": review.get("content")
            })

        return {
            "message": message,
            "data": processed_reviews
        }
            
    @handle_error
    async def get_product_like_count(self, product_id: Union[str, int, List[Union[str, int]]]) -> Dict[str, Any]:
        product_ids = product_id if isinstance(product_id, list) else [product_id]
        product_ids_str = [str(pid) for pid in product_ids]
        payload = {"relationIds": product_ids_str}
        
        is_success, data, message, raw_data = await self._make_request(
            url=f"{self.base_url}/products/likes", 
            method="POST", 
            json=payload
        )

        if not is_success or not data:
            return f"제품의 좋아요 수 조회 중 오류가 발생했습니다. (이유: {message}) , 상세 오류: {raw_data.get('error_details')}"
        
        # 4-1. 조회한 상품이 1개인 경우
        if len(data) == 1:
            count = data[0].get("count", 0)
            return f"해당 상품의 좋아요 수는 {count:,}개입니다."
        
        # 4-2. 조회한 상품이 여러 개인 경우
        else:
            # ["상품 4637965 (12,345개)", "상품 1234567 (5,432개)"] 형태의 리스트 생성
            like_strings = [
                f"상품 {item.get('product_id')} ({item.get('count', 0):,}개)"
                for item in data
            ]
            return f"상품별 좋아요 수: {', '.join(like_strings)}."
       
    @handle_error
    async def get_product_stats(self, product_id: str | int) -> Dict[str, Any]:
        product_id_str = str(product_id)
        
        is_success, data, message, raw_data = await self._make_request(
            url=f"{self.base_url}/products/{product_id_str}/stats"
        )

        # 2. 응답 성공 여부 및 데이터 유무 확인
        if not is_success or not data:
            return f"통계 정보를 찾을 수 없습니다. (이유: {message}) , 상세 오류: {raw_data.get('error_details')}"
        
        # 3. 성공 데이터 가공
        stats_info = data[0]
        views = stats_info.get("product_view_total", 0)
        purchases = stats_info.get("purchase_total", 0)

        # LLM이 바로 사용할 수 있는 요약 문장 생성 (숫자에 콤마 추가)
        return f"제품 통계: 최근 1개월 조회수는 {views:,}회이며, 누적 판매량은 {purchases:,}개입니다."

        

    @handle_error
    async def get_product_other_color(self, product_id: str | int) -> Dict[str, Any]:
        product_id_str = str(product_id)
        
        is_success, data, message, raw_data = await self._make_request(
            url=f"{self.base_url}/products/{product_id_str}/other-colors"
        )

        if not is_success or not data:
            return f"다른 색상 제품 정보를 찾을 수 없습니다. (이유: {message}) , 상세 오류: {raw_data.get('error_details')}"
        
        color_status_list = []
        for product in data:
            
            # # "스웨트셔츠 [헤더 베이지]" -> "헤더 베이지" 와 같이 색상만 추출
            # try:
            #     color_name = name[name.rfind('[')+1:name.rfind(']')]
            #     if not color_name: color_name = name # 추출 실패 시 전체 이름 사용
            # except:
            #     color_name = name
            
            color_status_list.append(
                {
                    "product_name": product.get("goods_name"),
                    "status": "품절" if product.get("is_sold_out") else "구매 가능",
                    "image_url": product.get("image_url")
                }
            )
        return {
            "message": message,
            "data": color_status_list
        }
    
    @handle_error
    async def get_product_price(self, product_id: str | int) -> Dict[str, Any]:
        product_id_str = str(product_id)
        
        is_success, data, message, raw_data = await self._make_request(
            url=f"{self.base_url}/products/{product_id_str}/brand-price"
        )

        if not is_success or not data:
            return f"브랜드 및 가격 정보를 찾을 수 없습니다. (이유: {message}) , 상세 오류: {raw_data.get('error_details')}"
        
        # 3. 성공 데이터 가공
        info = data[0]
        price_info = info.get("price_info", {})

        sale_price = price_info.get("sale_price", 0)
        original_price = price_info.get("original_price", 0)
        discount_rate = price_info.get("discount_rate", 0)
        is_on_sale = price_info.get("is_on_sale", False)
        
        # 4. 할인 여부에 따라 다른 문장 생성
        if is_on_sale and discount_rate > 0:
            return (
                f"현재 {discount_rate}% 할인하여 {sale_price:,}원에 판매 중입니다. "
                f"(정상가: {original_price:,}원)"
            )
        elif is_on_sale:
            return f"현재 판매중인 정상가는 {original_price:,}원입니다."
        else:
            return f"현재 판매중인 상품은 아니며 정상가는 {original_price:,}원입니다."
        
        
    @handle_error
    async def get_brand_name(self, product_id: str | int) -> Dict[str, Any]:
        product_id_str = str(product_id)
        
        is_success, data, message, raw_data = await self._make_request(
            url=f"{self.base_url}/products/{product_id_str}/brand-price"
        )

        if not is_success or not data:
            return f"브랜드 이름을 찾을 수 없습니다. (이유: {message}) , 상세 오류: {raw_data.get('error_details')}"
        info = data[0]
        brand_info = info.get("brand_info", {})
        brand_name = brand_info.get("brand_english_name", "알 수 없음")
        return f"해당 제품의 브랜드 이름은 `{brand_name}` 입니다."
    
    @handle_error
    async def get_brand_likes_count(self, brand_name: Union[str, List[str]]) -> Dict[str, Any]:
        brand_names = [brand_name.lower()] if isinstance(brand_name, str) else [name.lower() for name in brand_name]
        payload = {"relationIds": brand_names}
       
        is_success, data, message, raw_data = await self._make_request(
            url=f"{self.base_url}/brands/likes", 
            method="POST", 
            json=payload
        )

        if not is_success or not data:
            return f"브랜드의 '좋아요' 수를 찾을 수 없습니다. (이유: {message}) , 상세 오류: {raw_data.get('error_details')}"
        
        # 4-1. 조회한 브랜드가 1개인 경우
        if len(data) == 1:
            result = data[0]
            name = result.get("brand_name", "알 수 없는 브랜드")
            count = result.get("count", 0)
            return f"'{name}' 브랜드의 좋아요 수는 {count:,}개입니다."
        
        # # 4-2. 조회한 브랜드가 여러 개인 경우
        # else:
        #     # ["markm (34,533개)", "covernat (392,414개)"] 형태의 리스트 생성
        #     like_strings = [
        #         f"{item.get('brand_name')} ({item.get('count', 0):,}개)"
        #         for item in data
        #     ]
        #     return f"브랜드별 좋아요 수: {', '.join(like_strings)}."
    # async def get_color_code(self) -> Dict[str, Any]:
    #     error_context = {"error_type": ErrorType.API_ERROR}
    #     try:
    #         response = await self.client.get(f"{self.base_url}/meta/colors")
    #         response.raise_for_status()
    #         raw_data = response.json()
    #         # if raw_data.get("meta", {}).get("result") == "SUCCESS":
    #         #     color_list = sorted([{"color_id": color.get("colorId"), "color_name": color.get("colorName")} for color in raw_data.get("data", {}).get("colorImages", [])], key=lambda x: int(x["color_id"]))
    #         #     return {"success": True, "data": color_list, "message": "색상 코드 정보를 성공적으로 조회했습니다."}
    #         # else:
    #         #     return {"success": False, "data": [], "message": "API에서 색상 코드 데이터를 반환하지 않았습니다.", "error_details": {"error_type": ErrorType.NO_DATA}}
    #     except Exception as e:
    #         return {"success": False, "data": [], "message": f"색상 코드 조회 중 오류가 발생했습니다: {str(e)}", "error_details": error_context}

async def main():
    musinsa_api_wrapper = MusinsaAPIWrapper()
    product_id = 3522389
    import pprint
    height = "170"
    weight = 70
    # print(await musinsa_api_wrapper.get_size_recommend(product_id, height, weight))
    pprint.pprint(await musinsa_api_wrapper.get_product_price(product_id))
    # print(await musinsa_api_wrapper.get_review_summary(product_id))
    # pprint.pprint(await musinsa_api_wrapper.get_size_recommend("markm" ))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())