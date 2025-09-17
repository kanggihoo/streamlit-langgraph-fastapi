# from agents.tools.musinsa import MusinsaAPIWrapperTool
import httpx
import pytest
from pydantic import BaseModel , Field
from langchain_core.tools import StructuredTool
from wrapper.musinsa_wrapper import MusinsaAPIWrapper

client = httpx.AsyncClient()
logic_instance = MusinsaAPIWrapper(client)

class ProductPriceInput(BaseModel):
    product_id: int = Field(description="가격을 조회할 상품의 고유 ID.")


langchain_tool = StructuredTool.from_function(
            # logic_instance의 '바인딩된' 메서드를 func으로 지정
            func=None,
            name="get_product_selection_info",
            description="""상품 ID를 기반으로 가격 및 할인 정보를 조회합니다.
사용자가 상품의 '가격', '얼마', '세일', '할인' 정보를 물어볼 때 사용합니다.
예: "이 옷 가격이 얼마인가요?", "지금 할인하고 있어?"
성공 시, 정상가, 할인가, 할인율 등 가격 정보를 종합하여 설명하는 문자열을 반환합니다.
실패 시, 에러 메시지를 담은 문자열을 반환합니다.""",
            args_schema=ProductPriceInput,
            coroutine=getattr(logic_instance, MusinsaAPIWrapper.get_product_selection_info.__name__)
        )
langchain_tool.args

@pytest.mark.asyncio
async def test_get_product_selection_info():


    name = "get_product_selection_info"
    func = getattr(logic_instance, name)

    print(id(func))
    func2 = logic_instance.get_product_selection_info
    print(id(func2))
    
    func3 = getattr(logic_instance, "get_product_selection_info")
    print(id(func3))
    fun4 = getattr(logic_instance, "get_product_selection_info")
    print(id(fun4))
    print(func == func2 == func3 == fun4 )
    # print(getattr(logic_instance, MusinsaAPIWrapper.get_product_selection_info.__name__).__doc__)
    # tool_result = await langchain_tool.ainvoke({"product_id" : 3522389})
    # print(tool_result)
    # await client.aclose()
    


    