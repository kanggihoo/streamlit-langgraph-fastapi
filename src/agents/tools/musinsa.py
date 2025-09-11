from app.services import MusinsaAPIWrapper , VectorSearchAPIWrapper
from langchain_core.tools import tool
from typing import List, Literal, Dict, Any, Union

# MusinsaAPIWrapper 인스턴스 생성
musinsa_api_wrapper = MusinsaAPIWrapper()


@tool(parse_docstring=True)
async def get_size_recommend(product_id: int, height: int, weight: int) -> dict:
    """상품 ID와 사용자의 키, 몸무게를 기반으로 사이즈를 추천합니다.

    사용자가 특정 상품에 대해 자신의 신체 정보(키, 몸무게)를 제공하며 사이즈 추천을 요청할 때 이 함수를 사용해야 합니다.
    예: "이 옷 175cm, 70kg인데 어떤 사이즈가 맞을까요?"

    성공 시, 추천 사이즈 정보를 담은 딕셔너리를 반환합니다.
    실패 시, 'error' 키를 포함하는 딕셔너리를 반환합니다.

    Args:
        product_id (int): 사이즈 추천을 원하는 상품의 고유 ID.
        height (int): 사용자의 키 (cm).
        weight (int): 사용자의 몸무게 (kg).

    Returns:
        dict: 사이즈 추천 결과. 성공 시 추천 내용, 실패 시 에러 정보를 포함합니다.
    """
    return await musinsa_api_wrapper.get_size_recommend(product_id, height, weight)


@tool(parse_docstring=True)
async def get_product_selection_info(product_id: int) -> dict:
    """상품 ID를 기반으로 해당 상품의 구매 옵션 정보를 조회합니다.

    사용자가 상품의 '색상', '사이즈' 등 어떤 종류의 구매 옵션이 있는지 궁금해할 때 사용합니다.
    예: "이 상품은 어떤 색상들이 있나요?", "사이즈 옵션 좀 알려줘"

    성공 시, 상품의 옵션(색상, 사이즈 등) 정보를 담은 딕셔너리를 반환합니다.
    이 딕셔너리에는 'option_count', 'first_option_name', 'first_options' 등의 키가 포함됩니다.
    실패 시, 'error' 키를 포함하는 딕셔너리를 반환합니다.

    Args:
        product_id (int): 조회할 상품의 고유 ID.

    Returns:
        dict: 상품의 구매 옵션 정보. 실패 시 에러 정보를 포함합니다.
    """
    return await musinsa_api_wrapper.get_product_selection_info(product_id)


@tool(parse_docstring=True)
async def get_product_option_stock(product_id: int) -> dict:
    """상품 ID를 기반으로 각 옵션별 재고 상태를 조회합니다.

    사용자가 특정 상품의 '품절' 여부나, 특정 색상/사이즈의 재고가 있는지 질문할 때 사용합니다.
    예: "이 신발 270 사이즈 재고 있나요?", "검정색은 품절인가요?"

    성공 시, 각 옵션 조합별 재고 상태('구매 가능' 또는 '품절')를 담은 딕셔너리를 반환합니다.
    'option_types' 키는 선택 가능한 옵션의 종류와 값들을, 'stock_status' 키는 각 조합별 재고 상태를 나타냅니다.
    실패 시, 'error' 키를 포함하는 딕셔너리를 반환합니다.

    Args:
        product_id (int): 재고를 조회할 상품의 고유 ID.

    Returns:
        dict: 옵션별 재고 상태 정보. 실패 시 에러 정보를 포함합니다.
    """
    return await musinsa_api_wrapper.get_product_option_stock(product_id)


@tool(parse_docstring=True)
async def get_product_size_details(product_id: int) -> dict:
    """상품 ID를 기반으로 사이즈별 상세 실측 정보를 조회합니다.

    사용자가 '실측 사이즈', '사이즈 표', '어깨너비', '총장' 등 구체적인 치수를 물어볼 때 사용합니다.
    예: "M 사이즈 총장 길이가 어떻게 되나요?", "사이즈별 상세 치수 알려줘"

    성공 시, 각 사이즈별('S', 'M', 'L' 등) 상세 측정 항목과 값을 담은 딕셔너리 리스트를 반환합니다.
    실패 시, 'error' 키를 포함하는 딕셔너리를 반환합니다.

    Args:
        product_id (int): 상세 실측 사이즈를 조회할 상품의 고유 ID.

    Returns:
        dict: 사이즈별 상세 실측 정보. 실패 시 에러 정보를 포함합니다.
    """
    return await musinsa_api_wrapper.get_product_size(product_id)


@tool(parse_docstring=True)
async def get_review_summary(product_id: int) -> str:
    """상품 ID를 기반으로 전체 리뷰 요약 정보를 조회합니다.

    사용자가 상품의 '평점', '리뷰 개수' 등 전반적인 리뷰 정보를 궁금해할 때 사용합니다.
    예: "이 상품 리뷰 어때?", "평점 몇 점이야?"

    성공 시, 총 리뷰 수, 평균 평점 등을 요약한 문자열을 반환합니다.
    실패 시, 에러 메시지를 담은 문자열을 반환합니다.

    Args:
        product_id (int): 리뷰 요약을 조회할 상품의 고유 ID.

    Returns:
        str: 리뷰 요약 정보 또는 에러 메시지.
    """
    return await musinsa_api_wrapper.get_review_summary(product_id)


@tool(parse_docstring=True)
async def get_filtered_review_count(product_id: int, has_photo: bool = False, option_list: List[str] = None, sex: Literal["M", "F"] = None) -> str:
    """다양한 조건(사진 유무, 옵션, 성별)에 따라 필터링된 리뷰의 개수를 조회합니다.

    사용자가 "사진 있는 리뷰만 몇 개야?", "170cm 남자가 쓴 리뷰 찾아줘" 와 같이
    특정 조건에 맞는 리뷰의 개수를 물어볼 때 사용합니다.

    성공 시, 조건에 맞는 리뷰 개수를 설명하는 문자열을 반환합니다.
    실패 시, 에러 메시지를 담은 문자열을 반환합니다.

    Args:
        product_id (int): 리뷰 개수를 조회할 상품의 고유 ID.
        has_photo (bool, optional): 사진이 포함된 리뷰만 필터링할지 여부. Defaults to False.
        option_list (List[str], optional): 특정 옵션(예: '블랙', 'L')을 선택한 리뷰만 필터링. Defaults to None.
        sex (Literal["M", "F"], optional): 작성자의 성별을 기준으로 필터링. Defaults to None.

    Returns:
        str: 필터링된 리뷰 개수 또는 에러 메시지.
    """
    return await musinsa_api_wrapper.get_filtered_review_count(product_id, has_photo, option_list, sex)


@tool(parse_docstring=True)
async def get_review_list(product_id: int, page_size: int = 5, page: int = 0, option_list: List[str] = None, sex: Literal["M", "F"] = None, sort: Literal["up_cnt_desc", "new", "comment_cnt_desc", "goods_est_desc", "goods_est_asc"] = "up_cnt_desc", is_experience: bool = False, has_photo: bool = False) -> dict:
    """조건에 따라 필터링 및 정렬된 리뷰 목록을 상세하게 조회합니다.

    사용자가 "도움이 되는 순으로 리뷰 5개 보여줘", "최신 리뷰 알려줘" 와 같이
    리뷰의 실제 내용을 확인하고 싶을 때 사용합니다.

    성공 시, 리뷰 목록과 관련 정보를 담은 딕셔너리를 반환합니다.
    'data' 키에는 각 리뷰의 평점, 좋아요 수, 내용, 작성자 정보 등이 포함된 리스트가 들어있습니다.
    실패 시, 'error' 키를 포함하는 딕셔너리를 반환합니다.

    Args:
        product_id (int): 리뷰를 조회할 상품의 고유 ID.
        page_size (int, optional): 한 페이지에 가져올 리뷰 수. Defaults to 5.
        page (int, optional): 조회할 페이지 번호 (0부터 시작). Defaults to 0.
        option_list (List[str], optional): 특정 옵션을 선택한 리뷰만 필터링. Defaults to None.
        sex (Literal["M", "F"], optional): 작성자 성별로 필터링. Defaults to None.
        sort (Literal[...], optional): 정렬 기준 ('up_cnt_desc': 도움순, 'new': 최신순 등). Defaults to "up_cnt_desc".
        is_experience (bool, optional): 한달 사용 리뷰만 필터링할지 여부. Defaults to False.
        has_photo (bool, optional): 사진 리뷰만 필터링할지 여부. Defaults to False.

    Returns:
        dict: 상세 리뷰 목록 또는 에러 정보.
    """
    return await musinsa_api_wrapper.get_review_list(product_id, page_size, page, option_list, sex, sort, is_experience, has_photo)


@tool(parse_docstring=True)
async def get_product_like_count(product_id: Union[int, List[int]]) -> str:
    """상품 ID 또는 ID 리스트를 기반으로 '좋아요' 수를 조회합니다.

    사용자가 특정 상품의 인기도를 나타내는 '좋아요' 수나 '관심' 수를 물어볼 때 사용합니다.
    예: "이 상품 좋아요 몇 개야?", "1번이랑 2번 상품 중에 뭐가 더 인기 많아?"

    성공 시, 하나 또는 여러 상품의 좋아요 수를 설명하는 문자열을 반환합니다.
    실패 시, 에러 메시지를 담은 문자열을 반환합니다.

    Args:
        product_id (Union[int, List[int]]): 좋아요 수를 조회할 단일 상품 ID 또는 상품 ID의 리스트.

    Returns:
        str: 상품의 좋아요 수 정보 또는 에러 메시지.
    """
    return await musinsa_api_wrapper.get_product_like_count(product_id)


@tool(parse_docstring=True)
async def get_product_stats(product_id: int) -> str:
    """상품 ID를 기반으로 조회수 및 누적 판매량 통계를 조회합니다.

    사용자가 상품의 '조회수', '판매량', '인기도' 등 정량적인 데이터를 궁금해할 때 사용합니다.
    예: "이거 사람들 많이 봐?", "지금까지 몇 개나 팔렸어?"

    성공 시, 최근 1개월 조회수와 누적 판매량을 요약한 문자열을 반환합니다.
    실패 시, 에러 메시지를 담은 문자열을 반환합니다.

    Args:
        product_id (int): 통계를 조회할 상품의 고유 ID.

    Returns:
        str: 상품 통계 정보 또는 에러 메시지.
    """
    return await musinsa_api_wrapper.get_product_stats(product_id)


@tool(parse_docstring=True)
async def get_product_other_color(product_id: int) -> dict:
    """현재 상품과 동일한 디자인의 다른 색상 제품 목록을 조회합니다.

    사용자가 "이거 다른 색상도 있어?" 와 같이 현재 보고 있는 상품의 다른 색상 옵션을 찾을 때 사용합니다.

    성공 시, 다른 색상 제품의 이름, 재고 상태, 이미지 URL을 담은 딕셔너리 리스트를 반환합니다.
    'data' 키에 해당 리스트가 포함됩니다.
    실패 시, 'error' 키를 포함하는 딕셔너리를 반환합니다.

    Args:
        product_id (int): 다른 색상을 조회할 기준 상품의 고유 ID.

    Returns:
        dict: 다른 색상 제품 목록 또는 에러 정보.
    """
    return await musinsa_api_wrapper.get_product_other_color(product_id)


@tool(parse_docstring=True)
async def get_product_price(product_id: int) -> str:
    """상품 ID를 기반으로 가격 및 할인 정보를 조회합니다.

    사용자가 상품의 '가격', '얼마', '세일', '할인' 정보를 물어볼 때 사용합니다.
    예: "이 옷 가격이 얼마인가요?", "지금 할인하고 있어?"

    성공 시, 정상가, 할인가, 할인율 등 가격 정보를 종합하여 설명하는 문자열을 반환합니다.
    실패 시, 에러 메시지를 담은 문자열을 반환합니다.

    Args:
        product_id (int): 가격을 조회할 상품의 고유 ID.

    Returns:
        str: 상품 가격 정보 또는 에러 메시지.
    """
    return await musinsa_api_wrapper.get_product_price(product_id)


@tool(parse_docstring=True)
async def get_brand_name(product_id: int) -> str:
    """상품 ID를 기반으로 해당 상품의 브랜드 이름을 조회합니다.

    사용자가 "이 상품 어느 브랜드 거야?", "브랜드 이름 알려줘" 와 같이
    상품의 소속 브랜드를 궁금해할 때 사용합니다.

    성공 시, 브랜드 이름을 설명하는 문자열을 반환합니다.
    실패 시, 에러 메시지를 담은 문자열을 반환합니다.

    Args:
        product_id (int): 브랜드 이름을 조회할 상품의 고유 ID.

    Returns:
        str: 브랜드 이름 또는 에러 메시지.
    """
    return await musinsa_api_wrapper.get_brand_name(product_id)


@tool(parse_docstring=True)
async def get_brand_likes_count(brand_name: str) -> str:
    """브랜드 이름을 기반으로 해당 브랜드의 '좋아요(팬)' 수를 조회합니다.

    사용자가 특정 브랜드의 '인기도', '팬 수', '좋아요 수' 등을 물어볼 때 사용합니다.
    예: "A 브랜드 팬 수 얼마나 돼?"

    성공 시, 해당 브랜드의 좋아요 수를 설명하는 문자열을 반환합니다.
    실패 시, 에러 메시지를 담은 문자열을 반환합니다.

    Args:
        brand_name (str): 좋아요 수를 조회할 브랜드의 이름.

    Returns:
        str: 브랜드의 좋아요 수 또는 에러 메시지.
    """
    return await musinsa_api_wrapper.get_brand_likes_count(brand_name)