from enum import StrEnum
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
    OPENROUTER_GPT_4O_MINI = "gpt-4o-mini"
    OPENROUTER_GPT_4O = "gpt-4o"
    OPENROUTER_GEMINI_20_FLASH_LITE = "gemini-2.0-flash-lite"
tmp = set()
tmp.update(set(GoogleModelName))
tmp.update(set(OpenAIModelName))
tmp.update(set(OpenRouterModelName))
print(tmp , len(tmp))
