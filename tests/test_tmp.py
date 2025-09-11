from enum import StrEnum , Enum
from pydantic_settings import BaseSettings

from dotenv import load_dotenv
import os 
from src.settings import settings
load_dotenv()

def test_settings():
    print(settings.POSTGRES_PASSWORD.get_secret_value())



