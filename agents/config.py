#!/usr/bin/env python3
"""
Agent Configuration Management

提供统一的配置管理，支持：
- 环境变量自动加载
- 配置验证和默认值
- 开发/生产环境分离
- 配置热重载
- 友好的错误提示
"""
from functools import lru_cache
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DeepSeekConfig(BaseSettings):
    """DeepSeek AI 服务配置"""
    
    api_key: str = Field(
        default="",
        description="DeepSeek API 密钥",
        examples=["sk-xxxxxxxxxxxxxxxx"]
    )
    base_url: str = Field(
        default="https://api.deepseek.com",
        description="DeepSeek API 基础 URL"
    )
    model: str = Field(
        default="deepseek-chat",
        description="使用的模型名称"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="生成温度，控制随机性"
    )
    max_tokens: int = Field(
        default=1000,
        ge=1,
        le=32000,
        description="最大生成 token 数"
    )
    timeout: float = Field(
        default=30.0,
        gt=0.0,
        description="请求超时时间（秒）"
    )
    
    model_config = SettingsConfigDict(
        env_prefix='DEEPSEEK_',
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=False,
        json_schema_extra={
            "example": {
                "api_key": "sk-***",
                "base_url": "https://api.deepseek.com",
                "model": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 1000,
                "timeout": 30.0
            }
        }
    )
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """验证 API Key 格式"""
        if v and not v.startswith('sk-'):
            raise ValueError("DeepSeek API Key 应该以 'sk-' 开头")
        return v
    
    def is_configured(self) -> bool:
        """检查是否已正确配置"""
        return bool(self.api_key and self.api_key.startswith('sk-'))
    
    def validate_or_raise(self) -> None:
        """验证配置，如果未配置则抛出友好提示"""
        if not self.is_configured():
            raise ValueError(
                "DeepSeek API 未配置！请设置环境变量:\n"
                "  export DEEPSEEK_API_KEY='sk-your-api-key'\n"
                "\n或在项目根目录创建 .env 文件:\n"
                "  DEEPSEEK_API_KEY=sk-your-api-key\n"
                "\n获取 API Key: https://platform.deepseek.com/"
            )
    


class AgentConfig(BaseSettings):
    """Agent 全局配置"""
    
    # 调试模式
    debug: bool = Field(
        default=False,
        description="是否启用调试模式"
    )
    
    # 日志级别
    log_level: str = Field(
        default="INFO",
        description="日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    
    # DeepSeek 配置（嵌套配置）
    deepseek: DeepSeekConfig = Field(
        default_factory=DeepSeekConfig,
        description="DeepSeek AI 服务配置"
    )
    
    model_config = SettingsConfigDict(
        env_prefix='AGENT_',
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=False,
        json_schema_extra={
            "example": {
                "debug": False,
                "log_level": "INFO",
                "deepseek": {
                    "api_key": "sk-***",
                    "base_url": "https://api.deepseek.com",
                    "model": "deepseek-chat"
                }
            }
        }
    )
    


@lru_cache()
def get_config() -> AgentConfig:
    """
    获取单例配置实例（带缓存）
    
    Returns:
        AgentConfig: 全局配置对象
        
    Example:
        >>> config = get_config()
        >>> print(config.debug)
        >>> config.deepseek.validate_or_raise()
    """
    return AgentConfig()


@lru_cache()
def get_deepseek_config() -> DeepSeekConfig:
    """
    获取 DeepSeek 配置实例（带缓存）
    
    Returns:
        DeepSeekConfig: DeepSeek 配置对象
        
    Example:
        >>> ds_config = get_deepseek_config()
        >>> if ds_config.is_configured():
        ...     # 使用配置
        ...     pass
    """
    return DeepSeekConfig()


# 向后兼容：保留全局 config 变量（不推荐直接使用）
config = get_deepseek_config()


if __name__ == "__main__":
    # 测试配置加载
    print("=== 配置信息 ===")
    try:
        ds_config = get_deepseek_config()
        print(f"DeepSeek 已配置：{ds_config.is_configured()}")
        print(f"API Key: {'✓' if ds_config.is_configured() else '✗'}")
        print(f"Base URL: {ds_config.base_url}")
        print(f"Model: {ds_config.model}")
        print(f"Temperature: {ds_config.temperature}")
        
        if not ds_config.is_configured():
            print("\n⚠️  警告：DeepSeek API 未配置")
            print("\n请按以下步骤配置:")
            print("1. 在项目根目录创建 .env 文件")
            print("2. 添加内容：DEEPSEEK_API_KEY=sk-your-key")
            print("3. 或设置环境变量：export DEEPSEEK_API_KEY=sk-your-key")
    except Exception as e:
        print(f"❌ 配置错误：{e}")
