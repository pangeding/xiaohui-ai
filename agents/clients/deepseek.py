import httpx
import json
from typing import List, Dict, Any
from agents.config import config

class DeepSeekClient:
    def __init__(self, api_key: str = None, base_url: str = None, timeout: float = None):
        self.api_key = api_key or config.api_key
        self.base_url = base_url or config.base_url
        self.timeout = timeout or config.timeout
        self.client = httpx.Client(timeout=self.timeout)

    def chat(self, messages: List[Dict[str, str]], model: str = None, temperature: float = None, max_tokens: int = None) -> Dict[str, Any]:
        """调用 DeepSeek Chat API"""
        if not self.api_key:
            raise ValueError("DeepSeek API key is required. Set DEEPSEEK_API_KEY environment variable.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model or config.model,
            "messages": messages,
            "temperature": temperature or config.temperature,
            "max_tokens": max_tokens or config.max_tokens
        }

        try:
            response = self.client.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"DeepSeek API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Request failed: {e}")