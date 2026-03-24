import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class DeepSeekConfig(BaseSettings):
    api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: float = float(os.getenv("DEEPSEEK_TIMEOUT", "30.0"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

config = DeepSeekConfig()