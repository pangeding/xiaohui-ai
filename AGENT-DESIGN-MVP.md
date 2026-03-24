# AI Agent MVP 实现方案

## 概述

基于 LangGraph 实现一个简化的多 Agent 协作系统，包含 3 个核心 ChatModel：
- **意图识别专家**：判断用户输入类型（睡眠分析/聊天分析）
- **聊天分析专家**：分析用户聊天内容和情绪
- **睡眠分析专家**：分析睡眠质量并提供建议

---

## 项目结构

```
xiaohui-ai/
├── agents/
│   ├── __init__.py
│   ├── config.py              # 配置管理（API Key、环境变量）
│   ├── state.py               # AgentState 定义
│   ├── clients/
│   │   ├── __init__.py
│   │   └── deepseek.py        # DeepSeek API 客户端封装
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── intent.py          # 意图识别节点
│   │   ├── sleep.py           # 睡眠分析节点
│   │   └── chat.py            # 聊天分析节点
│   ├── edges.py               # 条件路由函数
│   ├── graph.py               # Graph 构建主逻辑
│   └── prompts/
│       ├── __init__.py
│       ├── intent.py
│       ├── sleep.py
│       └── chat.py
├── .env                       # 环境变量配置
├── .env.example               # 环境变量示例
├── AGENT-DESIGN-MVP.md        # 本文档
└── backend/
    └── pyproject.toml         # 依赖配置
```

---

## 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      User Input                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   意图识别专家 (Intent  │
        │        ChatModel)       │
        └──────────┬─────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
    ┌────▼────┐        ┌────▼────┐
    │聊天分析 │        │睡眠分析 │
    │专家节点 │        │专家节点 │
    └─────────┘        └─────────┘
```

---

## 核心组件

### 0. DeepSeek API 客户端封装

**文件：`agents/clients/deepseek.py`**

```python
import httpx
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class DeepSeekClient:
    """DeepSeek API 客户端封装"""
    
    def __init__(
        self, 
        api_key: str = None,
        base_url: str = None,
        timeout: float = 30.0
    ):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.timeout = timeout
        
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
        
        self.client = httpx.Client(timeout=self.timeout)
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """调用 DeepSeek Chat API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = self.client.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
```

---

### 1. State 定义

**文件：`agents/state.py`**

```python
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

class AgentState(TypedDict):
    input_data: Dict[str, Any]          # 用户输入数据
    input_type: str                      # "chat" | "sleep"
    intent: Optional[str]                # "sleep_analysis" | "chat_analysis"
    intent_confidence: float             # 意图置信度
    intent_reasoning: str                # 意图判断理由
    analysis_result: Optional[Dict]      # 分析结果
    analysis_type: Optional[str]         # "sleep" | "chat"
    messages: List[Dict[str, str]]       # 对话历史
    created_at: datetime                 # 创建时间
    updated_at: datetime                 # 更新时间
    tokens_used: int                     # Token 消耗统计
```

---

### 2. 图结构流程

#### Step 1: 入口点 → 意图识别专家

```
Entry Point → recognize_intent (ChatModel)
                           ↓
                    解析用户输入
                    判断意图类别
                    ↓
              输出：intent, confidence, reasoning
```

**文件：`agents/nodes/intent.py`**

```python
from agents.state import AgentState
from agents.clients.deepseek import DeepSeekClient
from agents.prompts.intent import INTENT_PROMPT_TEMPLATE
import json
import logging

logger = logging.getLogger(__name__)

def recognize_intent(state: AgentState) -> AgentState:
    """意图识别 ChatModel 节点"""
    try:
        client = DeepSeekClient()
        
        content = state["input_data"].get("content", str(state["input_data"]))
        history = "\n".join([f"{m['role']}: {m['content']}" 
                            for m in state["messages"][-5:]]) if state["messages"] else "无"
        
        prompt = INTENT_PROMPT_TEMPLATE.format(
            input_content=content,
            conversation_history=history
        )
        
        messages = [
            {"role": "system", "content": "你是养老监护平台的意图识别助手。"},
            {"role": "user", "content": prompt}
        ]
        
        response = client.chat(messages)
        result = json.loads(response["choices"][0]["message"]["content"])
        
        return {
            "intent": result.get("intent"),
            "intent_confidence": result.get("confidence", 0.0),
            "intent_reasoning": result.get("reasoning", ""),
            "tokens_used": response.get("usage", {}).get("total_tokens", 0)
        }
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return {
            "intent": "chat_analysis",  # 默认 fallback
            "intent_confidence": 0.5,
            "intent_reasoning": f"JSON 解析失败：{str(e)}",
            "tokens_used": 0
        }
    except Exception as e:
        logger.error(f"Intent recognition failed: {e}")
        raise
```

---

#### Step 2: 条件路由 → 选择专家节点

```
recognize_intent
        ↓
   route_by_intent (条件函数)
        ↓
    ┌───┴───┐
    ↓       ↓
analyze_chat  analyze_sleep
```

**文件：`agents/edges.py`**

```python
from agents.state import AgentState

def route_by_intent(state: AgentState) -> str:
    """根据意图路由到对应专家节点"""
    intent = state.get("intent")
    
    if intent == "sleep_analysis":
        return "analyze_sleep"
    elif intent == "chat_analysis":
        return "analyze_chat"
    else:
        # 未知意图默认走聊天分析
        logger.warning(f"Unknown intent: {intent}, defaulting to chat_analysis")
        return "analyze_chat"
```

---

#### Step 3a: 聊天分析专家 ChatModel

```
analyze_chat (ChatModel)
        ↓
  分析聊天内容
  评估情绪状态
  认知能力评估
        ↓
  输出：emotion, cognitive_level, risk_level, topics
```

**文件：`agents/nodes/chat.py`**

```python
from agents.state import AgentState
from agents.clients.deepseek import DeepSeekClient
from agents.prompts.chat import CHAT_ANALYSIS_PROMPT_TEMPLATE
import json
import logging

logger = logging.getLogger(__name__)

def analyze_chat(state: AgentState) -> AgentState:
    """聊天分析 ChatModel 节点"""
    try:
        client = DeepSeekClient()
        
        chat_content = state["input_data"]["content"]
        history = "\n".join([f"{m['role']}: {m['content']}" 
                            for m in state["messages"][-5:]]) if state["messages"] else "无"
        
        prompt = CHAT_ANALYSIS_PROMPT_TEMPLATE.format(
            chat_content=chat_content,
            conversation_history=history
        )
        
        messages = [
            {"role": "system", "content": "你是老年心理健康专家。"},
            {"role": "user", "content": prompt}
        ]
        
        response = client.chat(messages)
        analysis = json.loads(response["choices"][0]["message"]["content"])
        
        return {
            "analysis_result": analysis,
            "analysis_type": "chat",
            "tokens_used": response.get("usage", {}).get("total_tokens", 0)
        }
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in chat analysis: {e}")
        return {
            "analysis_result": {
                "emotion": "unknown",
                "emotion_score": 50,
                "cognitive_level": "unknown",
                "risk_level": "normal",
                "topics": [],
                "warnings": ["解析失败"],
                "suggestions": ["请重新输入"]
            },
            "analysis_type": "chat",
            "tokens_used": 0
        }
    except Exception as e:
        logger.error(f"Chat analysis failed: {e}")
        raise
```

---

#### Step 3b: 睡眠分析专家 ChatModel

```
analyze_sleep (ChatModel)
        ↓
  分析睡眠数据
  评估睡眠质量
  生成改善建议
        ↓
  输出：quality, issues, recommendations, summary
```

**文件：`agents/nodes/sleep.py`**

```python
from agents.state import AgentState
from agents.clients.deepseek import DeepSeekClient
from agents.prompts.sleep import SLEEP_ANALYSIS_PROMPT_TEMPLATE
import json
import logging

logger = logging.getLogger(__name__)

def analyze_sleep(state: AgentState) -> AgentState:
    """睡眠分析 ChatModel 节点"""
    try:
        client = DeepSeekClient()
        
        sleep_data = state["input_data"]["record"]
        prompt = SLEEP_ANALYSIS_PROMPT_TEMPLATE.format(**sleep_data)
        
        messages = [
            {"role": "system", "content": "你是专业睡眠健康分析师。"},
            {"role": "user", "content": prompt}
        ]
        
        response = client.chat(messages)
        analysis = json.loads(response["choices"][0]["message"]["content"])
        
        return {
            "analysis_result": analysis,
            "analysis_type": "sleep",
            "tokens_used": response.get("usage", {}).get("total_tokens", 0)
        }
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in sleep analysis: {e}")
        return {
            "analysis_result": {
                "quality": "unknown",
                "issues": ["解析失败"],
                "recommendations": ["请重新提供睡眠数据"],
                "summary": "分析失败"
            },
            "analysis_type": "sleep",
            "tokens_used": 0
        }
    except Exception as e:
        logger.error(f"Sleep analysis failed: {e}")
        raise
```

---

### 3. 完整 Graph 构建

**文件：`agents/graph.py`**

```python
from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.nodes.intent import recognize_intent
from agents.nodes.sleep import analyze_sleep
from agents.nodes.chat import analyze_chat
from agents.edges import route_by_intent
import logging

logger = logging.getLogger(__name__)

def build_agent_graph():
    """构建 Agent 协作图"""
    workflow = StateGraph(AgentState)
    
    # 添加 3 个核心 ChatModel 节点
    workflow.add_node("recognize_intent", recognize_intent)  # 意图识别专家
    workflow.add_node("analyze_sleep", analyze_sleep)        # 睡眠分析专家
    workflow.add_node("analyze_chat", analyze_chat)          # 聊天分析专家
    
    # 设置入口点
    workflow.set_entry_point("recognize_intent")
    
    # 添加条件边（路由）
    workflow.add_conditional_edges(
        source="recognize_intent",
        condition=route_by_intent,
        mapping={
            "analyze_sleep": "analyze_sleep",
            "analyze_chat": "analyze_chat"
        }
    )
    
    # 专家节点执行完成后结束
    workflow.add_edge("analyze_sleep", END)
    workflow.add_edge("analyze_chat", END)
    
    # 编译图
    app = workflow.compile()
    logger.info("Agent graph compiled successfully")
    return app

# 实例化 Agent 图
agent_app = build_agent_graph()
```

---

## 可视化图结构

```
                    ┌──────────────┐
                    │ ENTRY POINT  │
                    └──────┬───────┘
                           │
                           ▼
                ┌──────────────────┐
                │ recognize_intent │◄─── ChatModel 1
                │  (意图识别专家)   │
                └────────┬─────────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
              ▼          ▼          ▼
     ┌───────────┐               ┌─────────────┐
     │analyze_   │               │ analyze_    │
     │sleep      │               │ chat        │
     │(睡眠专家) │               │ (聊天专家)  │
     └─────┬─────┘               └──────┬──────┘
           │                            │
           └──────────────┬─────────────┘
                          │
                          ▼
                    ┌─────────────┐
                    │    END      │
                    └─────────────┘
```

---

## Prompt 模板

### 1. 意图识别专家 Prompt

```python
INTENT_PROMPT_TEMPLATE = """
你是养老监护平台的意图识别助手。请分析用户输入，判断其意图类别。

可用类别：
1. sleep_analysis - 与睡眠相关的问题（睡眠质量、失眠、作息等）
2. chat_analysis - 日常聊天、情感交流、认知训练等
3. emergency - 紧急情况（摔倒、身体不适、危险等）

用户输入：{input_content}
历史对话：{conversation_history}

请以 JSON 格式返回：
{{
    "intent": "类别名称",
    "confidence": 0.95,
    "reasoning": "判断理由"
}}
""".strip()
```

### 2. 聊天分析专家 Prompt

```python
CHAT_ANALYSIS_PROMPT_TEMPLATE = """
你是老年心理健康专家。请分析以下聊天内容：

聊天内容：{chat_content}
对话历史：{conversation_history}

请分析：
1. 情绪状态（积极/中性/消极）及情绪评分（0-100）
2. 认知能力评估（正常/轻度下降/中度下降）
3. 风险等级（normal/warning/high）
4. 主要话题标签
5. 需要关注的预警信号

以 JSON 格式返回：
{{
    "emotion": "情绪类型",
    "emotion_score": 65,
    "cognitive_level": "认知等级",
    "risk_level": "risk_level",
    "topics": ["话题 1", "话题 2"],
    "warnings": ["预警信号"],
    "suggestions": ["建议"]
}}
""".strip()
```

### 3. 睡眠分析专家 Prompt

```python
SLEEP_ANALYSIS_PROMPT_TEMPLATE = """
你是专业睡眠健康分析师。请根据以下睡眠数据进行分析：

睡眠数据：
- 总睡眠时长：{duration} 分钟
- 深睡时长：{deep_sleep} 分钟
- 浅睡时长：{light_sleep} 分钟
- 醒来次数：{wake_up_count} 次
- 睡眠评分：{sleep_score}/100

请提供：
1. 睡眠质量评估（优秀/良好/一般/较差）
2. 主要问题分析
3. 改善建议（3-5 条具体措施）

以 JSON 格式返回：
{{
    "quality": "评估等级",
    "issues": ["问题 1", "问题 2"],
    "recommendations": ["建议 1", "建议 2"],
    "summary": "总结性评价"
}}
""".strip()
```

---

## 测试示例

### 测试 1: 睡眠分析流程

**文件：`agents/demo.py`**

```python
from datetime import datetime
from agents.graph import agent_app
import logging

logging.basicConfig(level=logging.INFO)

# 测试睡眠分析
initial_state = {
    "input_data": {
        "type": "sleep",
        "record": {
            "duration": 380,
            "deep_sleep": 60,
            "light_sleep": 290,
            "wake_up_count": 5,
            "sleep_score": 65
        }
    },
    "input_type": "sleep",
    "intent": None,
    "intent_confidence": 0.0,
    "intent_reasoning": "",
    "analysis_result": None,
    "analysis_type": None,
    "messages": [],
    "created_at": datetime.now(),
    "updated_at": datetime.now(),
    "tokens_used": 0
}

try:
    result = agent_app.invoke(initial_state)
    print("\n=== 睡眠分析结果 ===")
    print(f"意图：{result['intent']}")
    print(f"置信度：{result['intent_confidence']}")
    print(f"分析类型：{result['analysis_type']}")
    print(f"分析结果：{result['analysis_result']}")
    print(f"Token 消耗：{result['tokens_used']}")
except Exception as e:
    print(f"测试失败：{e}")
```

### 测试 2: 聊天分析流程

```python
from datetime import datetime
from agents.graph import agent_app
import logging

logging.basicConfig(level=logging.INFO)

initial_state = {
    "input_data": {
        "type": "chat",
        "content": "最近总是感觉心情不好，没什么兴趣出门活动"
    },
    "input_type": "chat",
    "intent": None,
    "intent_confidence": 0.0,
    "intent_reasoning": "",
    "analysis_result": None,
    "analysis_type": None,
    "messages": [],
    "created_at": datetime.now(),
    "updated_at": datetime.now(),
    "tokens_used": 0
}

try:
    result = agent_app.invoke(initial_state)
    print("\n=== 聊天分析结果 ===")
    print(f"意图：{result['intent']}")
    print(f"置信度：{result['intent_confidence']}")
    print(f"分析类型：{result['analysis_type']}")
    print(f"情绪状态：{result['analysis_result']['emotion']}")
    print(f"情绪评分：{result['analysis_result']['emotion_score']}")
    print(f"风险等级：{result['analysis_result']['risk_level']}")
    print(f"Token 消耗：{result['tokens_used']}")
except Exception as e:
    print(f"测试失败：{e}")
```

---

## 关键特性

1. **三专家架构**：
   - ✅ 意图识别专家：快速分类用户请求
   - ✅ 聊天分析专家：深度分析情绪和认知
   - ✅ 睡眠分析专家：专业睡眠健康建议

2. **条件路由**：根据意图自动分配到对应专家节点

3. **Token 统计**：每个节点累加 token 消耗，便于成本核算

4. **JSON 输出**：所有 LLM 输出结构化，易于程序解析

5. **对话历史**：支持传递最近 5 轮对话上下文

6. **错误处理**：每个节点独立的 try-catch，避免单点失败影响全局

7. **环境变量管理**：从 `.env` 文件读取配置，安全且易于部署

---

## 下一步扩展

- [ ] 添加紧急告警处理节点（emergency）
- [ ] 集成向量数据库（RAG）增强知识检索
- [ ] 添加记忆机制（Checkpoint）支持长短期记忆
- [ ] 接入真实传感器数据流
- [ ] 添加人机协作接口
- [ ] 支持多轮对话状态管理

---

## 附录：完整代码清单

### 文件列表

- [x] `agents/__init__.py` - 包初始化
- [x] `agents/config.py` - 配置管理
- [x] `agents/state.py` - State 定义
- [x] `agents/clients/deepseek.py` - API 客户端
- [x] `agents/nodes/intent.py` - 意图识别节点
- [x] `agents/nodes/chat.py` - 聊天分析节点
- [x] `agents/nodes/sleep.py` - 睡眠分析节点
- [x] `agents/edges.py` - 路由函数
- [x] `agents/graph.py` - Graph 构建
- [x] `agents/prompts/intent.py` - 意图识别 Prompt
- [x] `agents/prompts/chat.py` - 聊天分析 Prompt
- [x] `agents/prompts/sleep.py` - 睡眠分析 Prompt
- [x] `agents/demo.py` - 测试入口
- [x] `.env` - 环境变量配置
- [x] `.env.example` - 环境变量示例

---

## 快速开始指南

### 1. 安装依赖

```bash
cd backend
poetry install
# 或者使用 pip
pip install langgraph langchain-core httpx pydantic pydantic-settings python-dotenv
```

### 2. 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，填入你的 DeepSeek API Key
# DEEPSEEK_API_KEY=sk-your-actual-api-key-here
```

### 3. 获取 DeepSeek API Key

1. 访问 [DeepSeek 平台](https://platform.deepseek.com/)
2. 注册/登录账号
3. 进入个人中心 → API Keys
4. 创建新的 API Key 并复制保存

### 4. 运行测试

```bash
# 确保在 agents 目录下
cd agents

# 运行睡眠分析测试
python demo.py

# 或者单独运行某个节点测试
python -c "from graph import agent_app; print(agent_app)"
```

---

## 常见问题排查

### 问题 1: `DEEPSEEK_API_KEY not found`

**解决方案：**
- 检查 `.env` 文件是否存在
- 确认 `DEEPSEEK_API_KEY` 已正确配置
- 确保代码中调用了 `load_dotenv()`

### 问题 2: JSON 解析失败

**可能原因：**
- LLM 返回的内容不是有效的 JSON 格式
- 网络问题导致响应不完整

**解决方案：**
- 增加日志记录查看原始响应
- 在 Prompt 中强调必须返回 JSON 格式
- 添加重试机制

### 问题 3: 路由到错误的专家节点

**可能原因：**
- 意图识别不准确
- Prompt 描述不够清晰

**解决方案：**
- 优化意图识别的 Prompt 模板
- 在历史对话中添加更多上下文
- 调整意图类别的描述

---

## 依赖配置

```
[tool.poetry.dependencies]
python = "^3.10"
langgraph = "^0.1.0"
langchain-core = "^0.1.0"
httpx = "^0.25.0"
pydantic = "^2.0.0"
pydantic-settings = "^2.0.0"
python-dotenv = "^1.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

---

## 环境变量

```bash
# DeepSeek API 配置
DEEPSEEK_API_KEY=sk-your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# 日志配置
LOG_LEVEL=INFO

# 可选配置
DEEPSEEK_TIMEOUT=30
```

---

