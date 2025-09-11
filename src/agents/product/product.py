# react 구조 이용한 musinsa 상품 조회 도구 연결 
from langgraph.graph import StateGraph , START , END
from langgraph.graph.message import add_messages 
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage , BaseMessage , SystemMessage 
from langchain_core.prompts import ChatPromptTemplate , MessagesPlaceholder


from typing import Annotated , TypedDict 
import logging

from settings import settings 
from llm import get_llm_model 
from agents.tools.musinsa import (
    get_size_recommend,
    get_product_selection_info,
    get_product_option_stock,
    get_product_size_details,
    get_review_summary,
    get_filtered_review_count,
    get_review_list,
    get_product_like_count,
    get_product_stats,
    get_product_other_color,
    get_product_price,
    get_brand_name,
    get_brand_likes_count
)

logger = logging.getLogger(__name__)
class ProductState(TypedDict):
    """Chatbot state"""
    messages : Annotated[list[BaseMessage], add_messages] = []


product_agent = create_react_agent(
    model = get_llm_model(settings.DEFAULT_LLM_MODEL),
    tools = [
        get_size_recommend,
        get_product_selection_info,
        get_product_option_stock,
        get_product_size_details,
        get_product_stats,
        get_product_price,
        get_product_other_color,
        get_product_like_count,
        get_review_summary,
        get_filtered_review_count,
        get_review_list,
        get_brand_name,
        get_brand_likes_count,
    ],
    prompt = "You are a helpful assistant."
)



    