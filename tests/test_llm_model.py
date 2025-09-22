from llm import get_llm_model
from model.llm_models import OpenAIModelName, GoogleModelName, OpenRouterModelName
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from settings import settings
from dotenv import load_dotenv
import os

load_dotenv()

def test_llm_model():
    llm = get_llm_model(GoogleModelName.GEMINI_20_FLASH_LITE)
    print(llm.invoke("Hello, how are you?"))


def test_openrouter_llm():
    llm = ChatOpenAI(
        api_key=settings.OPENROUTER_API_KEY.get_secret_value(),
        model="google/gemini-2.0-flash-lite-001",
        base_url="https://openrouter.ai/api/v1/",
        temperature=0.0,
        streaming=True,
    )
    print(llm.invoke("Hello, how are you?"))
