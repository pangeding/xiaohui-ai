#!/usr/bin/env python3
"""
DeepSeek AI Client

提供与 DeepSeek AI 服务的交互接口
"""
import httpx
import json
from typing import List, Dict, Any, Optional
from agents.config import get_deepseek_config, DeepSeekConfig


class DeepSeekClient:
    """DeepSeek Chat API 客户端"""
    
    def __init__(self, config: Optional[DeepSeekConfig] = None):
        """
        初始化 DeepSeek 客户端
        
        Args:
            config: DeepSeek 配置对象，如果为 None 则使用默认配置
            
        Raises:
            ValueError: 当 API Key 未配置时
        """
        self.config = config or get_deepseek_config()
        
        # 验证配置
        if not self.config.is_configured():
            raise ValueError(
                "DeepSeek API 未配置！\n\n"
                "请按以下任一方式配置:\n"
                "1. 设置环境变量：export DEEPSEEK_API_KEY='sk-your-key'\n"
                "2. 在项目根目录创建 .env 文件，添加：DEEPSEEK_API_KEY=sk-your-key\n"
                "\n获取 API Key: https://platform.deepseek.com/"
            )
        
        self.api_key = self.config.api_key
        self.base_url = self.config.base_url
        self.timeout = self.config.timeout
        self.client = httpx.Client(timeout=self.timeout)
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: Optional[float] = None, 
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        调用 DeepSeek Chat API
        
        Args:
            messages: 对话消息列表，格式：[{"role": "user|assistant|system", "content": "..."}]
            model: 模型名称，默认使用配置的模型
            temperature: 生成温度 (0.0-2.0)，默认使用配置值
            max_tokens: 最大生成 token 数，默认使用配置值
            
        Returns:
            API 响应数据，包含：
            - choices: 生成的回复
            - usage: token 使用统计
            
        Raises:
            httpx.HTTPStatusError: HTTP 请求错误
            httpx.RequestError: 网络请求失败
            json.JSONDecodeError: 响应解析失败
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model or self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens
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
            error_msg = f"DeepSeek API 错误 ({e.response.status_code}):\n{e.response.text}"
            raise Exception(error_msg)
            
        except httpx.RequestError as e:
            error_msg = f"请求失败：{str(e)}\n请检查网络连接或 API 配置"
            raise Exception(error_msg)
    
    def close(self):
        """关闭客户端连接"""
        self.client.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
