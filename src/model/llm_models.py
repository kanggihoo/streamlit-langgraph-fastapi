from enum import StrEnum , auto
from typing import TypeAlias

class LLMProvider(StrEnum):
    OPENAI = auto()
    ANTHROPIC = auto()
    GOOGLE = auto()
    OPENROUTER = auto()


class GoogleModelName(StrEnum):
    """https://ai.google.dev/gemini-api/docs/models/gemini"""

    GEMINI_15_PRO = "gemini-1.5-pro"
    GEMINI_20_FLASH = "gemini-2.0-flash"
    GEMINI_20_FLASH_LITE = "gemini-2.0-flash-lite"
    GEMINI_25_FLASH = "gemini-2.5-flash"
    GEMINI_25_PRO = "gemini-2.5-pro"

class OpenAIModelName(StrEnum):
    """https://platform.openai.com/docs/models/models"""

    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"

class OpenRouterModelName(StrEnum):
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"


AllModelEnum: TypeAlias = (
    GoogleModelName 
    | OpenAIModelName
    | OpenRouterModelName
)


# if __name__ == "__main__":
#     print(list(m for m in GoogleModelName))
#     print(dir(GoogleModelName))
