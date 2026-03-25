# 配置管理使用指南

## 📋 概述

本项目采用专业的配置管理系统，具有以下特性：

- ✅ **环境变量自动加载**: 支持 `.env` 文件和环境变量
- ✅ **类型安全**: 基于 Pydantic 的严格类型验证
- ✅ **默认值**: 所有配置项都有合理的默认值
- ✅ **错误提示**: 友好的错误信息和配置指引
- ✅ **单例模式**: 配置实例带缓存，避免重复加载
- ✅ **可测试性**: 易于 Mock 和测试

## 🎯 快速开始

### 1. 创建配置文件

```bash
# 在项目根目录复制示例配置
cp .env.example .env
```

### 2. 编辑配置

```bash
# 编辑 .env 文件
vi .env
```

**最小化配置（仅需 API Key）：**
```env
DEEPSEEK_API_KEY=sk-your-api-key-here
```

**完整配置：**
```env
# DeepSeek API 配置
DEEPSEEK_API_KEY=sk-your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TEMPERATURE=0.7
DEEPSEEK_MAX_TOKENS=1000
DEEPSEEK_TIMEOUT=30

# Agent 全局配置
AGENT_DEBUG=false
AGENT_LOG_LEVEL=INFO
```

## 💻 代码使用

### 方式一：获取 DeepSeek 配置（推荐）

```python
from agents.config import get_deepseek_config

# 获取配置实例
config = get_deepseek_config()

# 检查是否已配置
if config.is_configured():
    print(f"API Key: {config.api_key}")
    print(f"Base URL: {config.base_url}")
    print(f"Model: {config.model}")
else:
    print("❌ DeepSeek 未配置")
```

### 方式二：获取全局 Agent 配置

```python
from agents.config import get_config

config = get_config()
print(f"调试模式：{config.debug}")
print(f"日志级别：{config.log_level}")
print(f"DeepSeek API Key: {config.deepseek.api_key}")
```

### 方式三：在 Client 中使用（自动验证）

```python
from agents.clients.deepseek import DeepSeekClient

# 客户端会自动加载和验证配置
client = DeepSeekClient()  # 如果未配置会抛出友好提示

# 使用客户端
response = client.chat([
    {"role": "user", "content": "你好"}
])
```

### 方式四：自定义配置（用于测试）

```python
from agents.config import DeepSeekConfig
from agents.clients.deepseek import DeepSeekClient

# 创建自定义配置
custom_config = DeepSeekConfig(
    api_key="sk-test-key",
    base_url="https://test.api.com",
    temperature=0.5
)

# 使用自定义配置创建客户端
client = DeepSeekClient(config=custom_config)
```

## 🔍 配置验证

### 检查配置状态

```python
from agents.config import get_deepseek_config

config = get_deepseek_config()

# 方法 1: 检查是否已配置
is_ready = config.is_configured()  # True/False

# 方法 2: 验证并抛出异常（推荐）
try:
    config.validate_or_raise()
    print("✅ 配置正确")
except ValueError as e:
    print(f"❌ 配置错误：{e}")
```

### 运行配置测试

```bash
cd agents
uv run python config.py
```

输出示例：
```
=== 配置信息 ===
DeepSeek 已配置：True
API Key: ✓
Base URL: https://api.deepseek.com
Model: deepseek-chat
Temperature: 0.7
```

## ⚠️ 错误处理

### 常见错误及解决方案

#### 1. API Key 未配置

```python
ValueError: DeepSeek API 未配置！

请按以下任一方式配置:
1. 设置环境变量：export DEEPSEEK_API_KEY='sk-your-key'
2. 在项目根目录创建 .env 文件，添加：DEEPSEEK_API_KEY=sk-your-key

获取 API Key: https://platform.deepseek.com/
```

**解决方案：**
```bash
# 方式 1: 设置环境变量
export DEEPSEEK_API_KEY='sk-xxxxxxxx'

# 方式 2: 创建 .env 文件
echo "DEEPSEEK_API_KEY=sk-xxxxxxxx" >> .env
```

#### 2. API Key 格式错误

```python
ValueError: DeepSeek API Key 应该以 'sk-' 开头
```

**解决方案：** 确保 API Key 以 `sk-` 开头

#### 3. .env 文件未找到

配置系统会自动查找项目根目录的 `.env` 文件，如果不存在则使用环境变量。

**解决方案：**
```bash
# 确保 .env 文件在项目根目录
ls -la .env

# 如果不存在，复制示例配置
cp .env.example .env
```

## 🧪 测试场景

### 单元测试中的配置

```python
import pytest
from agents.config import DeepSeekConfig
from agents.clients.deepseek import DeepSeekClient

def test_deepseek_client_with_mock_config():
    """测试时使用 Mock 配置"""
    # 创建测试配置
    test_config = DeepSeekConfig(
        api_key="sk-test-key",
        base_url="https://test.api.com"
    )
    
    # 使用测试配置创建客户端
    client = DeepSeekClient(config=test_config)
    
    # 执行测试...
```

### 不同环境的配置

```python
# development.py
DEBUG = True
LOG_LEVEL = "DEBUG"

# production.py  
DEBUG = False
LOG_LEVEL = "INFO"
```

## 📊 配置优先级

配置加载的优先级（从高到低）：

1. **直接传入的参数** > 
2. **环境变量** > 
3. **.env 文件** > 
4. **默认值**

示例：
```python
# 直接传入的参数优先级最高
config = DeepSeekConfig(api_key="direct-key")  # 使用 "direct-key"

# 环境变量
export DEEPSEEK_API_KEY="env-key"
config = DeepSeekConfig()  # 使用 "env-key"

# .env 文件
# DEEPSEEK_API_KEY=file-key
config = DeepSeekConfig()  # 使用 "file-key"

# 默认值
config = DeepSeekConfig()  # 使用 "" (空字符串)
```

## 🎓 最佳实践

### ✅ 推荐做法

1. **使用 `.env` 文件管理配置**（不要提交到 Git）
2. **在代码中使用 `get_deepseek_config()`** 获取配置
3. **在入口处验证配置**（如程序启动时）
4. **为测试创建独立的配置**
5. **敏感信息使用环境变量**

### ❌ 不推荐做法

1. ~~直接在代码中硬编码 API Key~~
2. ~~将 `.env` 文件提交到 Git~~
3. ~~在全局作用域直接使用 `config` 变量~~
4. ~~不使用配置验证就调用 API~~

## 🔐 安全提示

- ⚠️ **永远不要**将 `.env` 文件提交到版本控制
- ⚠️ **永远不要**在代码中硬编码 API Key
- ⚠️ 定期轮换 API Key
- ⚠️ 使用不同的 API Key 区分开发和生产环境

## 📚 参考资料

- [Pydantic Settings 文档](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [python-dotenv 文档](https://pypi.org/project/python-dotenv/)
- [DeepSeek API 文档](https://platform.deepseek.com/docs)
