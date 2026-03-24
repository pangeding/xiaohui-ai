# AI Agent 实现任务书

## 任务目标

基于 LangGraph 实现一个多 Agent 协作系统，包含：
- **1 个意图识别 Agent**：判断用户输入类型（睡眠分析/聊天分析）
- **2 个专业分析 Agent**：睡眠分析 Agent、聊天分析 Agent

---

## 核心要求

### 1. 项目结构

```
xiaohui/
├── backend/
│   ├── pyproject.toml
│   └── ...
└── agents/
    ├── __init__.py
    ├── config.py              # 配置管理（API Key、环境变量）
    ├── state.py               # AgentState 定义
    ├── nodes/                 # 节点实现
    │   ├── __init__.py
    │   ├── intent.py          # 意图识别节点
    │   ├── sleep.py           # 睡眠分析节点
    │   └── chat.py            # 聊天分析节点
    ├── edges.py               # 条件路由函数
    ├── graph.py               # Graph 构建主逻辑
    ├── clients/
    │   ├── __init__.py
    │   └── deepseek.py        # DeepSeek API 客户端封装
    ├── prompts/               # Prompt 模板
    │   ├── __init__.py
    │   ├── intent.py
    │   ├── sleep.py
    │   └── chat.py
    └── demo.py                # Demo 入口文件
```

---

### 2. State 设计

在 `agents/state.py` 中定义：

```python
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

class AgentState(TypedDict):
    input_data: Dict[str, Any]
    input_type: str  # "chat" | "sleep" | "sensor"
    intent: Optional[str]  # "sleep_analysis" | "chat_analysis" | "emergency"
    intent_confidence: float
    intent_reasoning: str
    analysis_result: Optional[Dict[str, Any]]
    analysis_type: Optional[str]  # "sleep" | "chat"
    messages: List[Dict[str, str]]
    created_at: datetime
    updated_at: datetime
    tokens_used: int
```

---

### 3. 实现步骤

#### Step 1: DeepSeek API 客户端封装

文件：`agents/clients/deepseek.py`

**要求：**
- 实现 `DeepSeekClient` 类
- 支持调用 `deepseek-chat` 模型
- 返回格式包含 `choices` 和 `usage`

**参考实现：**
```python
import httpx
from typing import List, Dict, Any

class DeepSeekClient:
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)
    
    def chat(self, messages: List[Dict[str, str]], model: str = "deepseek-chat") -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = self.client.post(
            f"{self.base_url}/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
```

---

#### Step 2: Prompt 模板定义

在 `agents/prompts/` 目录下创建对应文件：

**intent.py:**
```python
INTENT_PROMPT_TEMPLATE = """
你是一个养老监护平台的意图识别助手。请分析用户输入，判断其意图类别。

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

**sleep.py:**
```python
SLEEP_ANALYSIS_PROMPT_TEMPLATE = """
你是一位专业的睡眠健康分析师。请根据以下睡眠数据进行分析：

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

**chat.py:**
```python
CHAT_ANALYSIS_PROMPT_TEMPLATE = """
你是一位老年心理健康专家。请分析以下聊天内容：

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

---

#### Step 3: 实现 Node 节点

**文件：`agents/nodes/intent.py`**
```python
from agents.state import AgentState
from agents.clients.deepseek import DeepSeekClient
from agents.prompts.intent import INTENT_PROMPT_TEMPLATE
import json

def recognize_intent(state: AgentState) -> AgentState:
    """意图识别节点"""
    client = DeepSeekClient(api_key="your-api-key")
    
    content = state["input_data"].get("content", str(state["input_data"]))
    history = "\n".join([f"{m['role']}: {m['content']}" for m in state["messages"][-5:]]) if state["messages"] else "无"
    
    prompt = INTENT_PROMPT_TEMPLATE.format(
        input_content=content,
        conversation_history=history
    )
    
    messages = [
        {"role": "system", "content": "你是一个专业的养老监护助手。"},
        {"role": "user", "content": prompt}
    ]
    
    response = client.chat(messages)
    result = json.loads(response["choices"][0]["message"]["content"])
    
    return {
        "intent": result["intent"],
        "intent_confidence": result["confidence"],
        "intent_reasoning": result["reasoning"],
        "tokens_used": response["usage"]["total_tokens"]
    }
```

**文件：`agents/nodes/sleep.py`**
```python
from agents.state import AgentState
from agents.clients.deepseek import DeepSeekClient
from agents.prompts.sleep import SLEEP_ANALYSIS_PROMPT_TEMPLATE
import json

def analyze_sleep(state: AgentState) -> AgentState:
    """睡眠分析节点"""
    client = DeepSeekClient(api_key="your-api-key")
    
    sleep_data = state["input_data"]["record"]
    prompt = SLEEP_ANALYSIS_PROMPT_TEMPLATE.format(**sleep_data)
    
    messages = [
        {"role": "system", "content": "你是专业的睡眠健康分析师。"},
        {"role": "user", "content": prompt}
    ]
    
    response = client.chat(messages)
    analysis = json.loads(response["choices"][0]["message"]["content"])
    
    return {
        "analysis_result": analysis,
        "analysis_type": "sleep",
        "tokens_used": response["usage"]["total_tokens"]
    }
```

**文件：`agents/nodes/chat.py`**
```python
from agents.state import AgentState
from agents.clients.deepseek import DeepSeekClient
from agents.prompts.chat import CHAT_ANALYSIS_PROMPT_TEMPLATE
import json

def analyze_chat(state: AgentState) -> AgentState:
    """聊天分析节点"""
    client = DeepSeekClient(api_key="your-api-key")
    
    chat_content = state["input_data"]["content"]
    history = "\n".join([f"{m['role']}: {m['content']}" for m in state["messages"][-5:]]) if state["messages"] else "无"
    
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
        "tokens_used": response["usage"]["total_tokens"]
    }
```

---

#### Step 4: 实现条件路由

**文件：`agents/edges.py`**
```python
from agents.state import AgentState

def route_by_intent(state: AgentState) -> str:
    """根据意图路由到不同节点"""
    intent = state.get("intent")
    
    if intent == "sleep_analysis":
        return "analyze_sleep"
    elif intent == "chat_analysis":
        return "analyze_chat"
    else:
        return "aggregate_result"
```

---

#### Step 5: 构建 Graph

**文件：`agents/graph.py`**
```python
from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.nodes.intent import recognize_intent
from agents.nodes.sleep import analyze_sleep
from agents.nodes.chat import analyze_chat
from agents.edges import route_by_intent

def build_agent_graph():
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("recognize_intent", recognize_intent)
    workflow.add_node("analyze_sleep", analyze_sleep)
    workflow.add_node("analyze_chat", analyze_chat)
    
    # 设置入口点
    workflow.set_entry_point("recognize_intent")
    
    # 添加条件边
    workflow.add_conditional_edges(
        source="recognize_intent",
        condition=route_by_intent,
        mapping={
            "analyze_sleep": "analyze_sleep",
            "analyze_chat": "analyze_chat",
            "aggregate_result": "aggregate_result"
        }
    )
    
    # 添加普通边
    workflow.add_edge("analyze_sleep", END)
    workflow.add_edge("analyze_chat", END)
    
    # 编译
    app = workflow.compile()
    return app

agent_app = build_agent_graph()
```

---

### 4. 依赖配置

在 `backend/pyproject.toml` 中添加：

```toml
[tool.poetry.dependencies]
python = "^3.10"
langgraph = ">=0.1.0"
langchain-core = ">=0.1.0"
httpx = ">=0.25.0"
pydantic = ">=2.0.0"
pydantic-settings = ">=2.0.0"
python-dotenv = ">=1.0.0"
```

---

### 5. 环境变量

创建 `.env` 文件：

```bash
DEEPSEEK_API_KEY=sk-your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
LOG_LEVEL=INFO
```

---

### 6. 测试示例

**文件：`agents/demo.py`**
```python
from datetime import datetime
from agents.graph import agent_app

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

result = agent_app.invoke(initial_state)
print(result)
```

---

## 交付清单

- [ ] DeepSeek API 客户端封装完成
- [ ] 3 个 Prompt 模板定义完成
- [ ] 3 个 Node 节点实现完成
- [ ] 条件路由函数实现完成
- [ ] Graph 构建并成功运行
- [ ] Demo 可执行测试通过

---

## 注意事项

1. **所有 LLM 输出必须为 JSON 格式**，便于程序解析
2. **每个节点需累加 tokens_used**，用于成本核算
3. **错误处理**：每个节点独立 try-catch，避免单点失败影响全局
4. **API Key 配置**：从环境变量读取，不要硬编码

---

## 扩展方向（后续迭代）

- 添加紧急告警处理节点
- 集成向量数据库（RAG）
- 添加记忆机制（Checkpoint）
- 接入真实传感器数据
