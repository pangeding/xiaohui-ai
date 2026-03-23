# AI Agent 图结构设计方案

## 1. 方案概述

本方案设计一个基于 LangGraph 的多 Agent 协作系统，通过图结构实现意图识别、任务路由和专业处理的完整流程。系统采用"1+2"模式：**1 个意图识别 Agent** + **2 个专业分析 Agent**（睡眠分析、聊天分析）。

### 1.1 核心目标

- 实现基于状态机的图结构编排
- 支持条件分支和动态路由
- 提供可扩展的 Agent 架构
- 快速验证 DeepSeek API 集成

---

## 2. 架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                    User Input                           │
│              (用户输入/传感器数据)                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│              State: AgentState                          │
│  - input_data: 输入数据                                 │
│  - intent: 意图分类结果                                 │
│  - analysis_result: 分析结果                            │
│  - messages: 对话历史                                   │
└─────────────────────────────────────────────────────────┘
                     │
                     ↓
        ┌────────────────────────┐
        │   意图识别 Agent        │
        │  (Intent Recognition)   │
        │   Node: recognize_intent│
        └───────────┬────────────┘
                    │
                    ↓
        ┌────────────────────────┐
        │   条件路由判断          │
        │   Edge: route_by_intent│
        └───────────┬────────────┘
                    │
        ┌───────────┴────────────┐
        │                        │
        ↓                        ↓
┌──────────────┐        ┌──────────────┐
│ 睡眠分析 Agent│        │ 聊天分析 Agent│
│SleepAnalyzer │        │ChatAnalyzer  │
│Node: analyze_│        │Node: analyze_│
│   sleep      │        │   chat       │
└──────┬───────┘        └──────┬───────┘
       │                       │
       └───────────┬───────────┘
                   │
                   ↓
        ┌────────────────────────┐
        │    结果汇总节点         │
        │  Node: aggregate_result│
        └───────────┬────────────┘
                    │
                    ↓
        ┌────────────────────────┐
        │    END: 输出结果        │
        └────────────────────────┘
```

---

## 3. 详细设计

### 3.1 State 设计

State 是贯穿整个 Graph 的核心数据结构，承载所有节点的输入输出。

```python
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

class AgentState(TypedDict):
    """Agent 全局状态"""
    
    # 输入数据
    input_data: Dict[str, Any]  # 原始输入（用户消息或传感器数据）
    input_type: str  # 输入类型："chat" | "sleep" | "sensor"
    
    # 意图识别结果
    intent: Optional[str]  # 意图分类："sleep_analysis" | "chat_analysis" | "emergency"
    intent_confidence: float  # 置信度 (0-1)
    intent_reasoning: str  # 推理过程
    
    # 分析结果
    analysis_result: Optional[Dict[str, Any]]  # 专业 Agent 的分析结果
    analysis_type: Optional[str]  # 分析类型："sleep" | "chat"
    
    # 对话历史（用于多轮对话）
    messages: List[Dict[str, str]]  # 对话历史列表
    
    # 元数据
    created_at: datetime  # 会话创建时间
    updated_at: datetime  # 最后更新时间
    tokens_used: int  # 消耗的 Token 数
```

---

### 3.2 Node 设计

#### 3.2.1 意图识别节点 (recognize_intent)

**职责：**
- 接收用户输入
- 调用 DeepSeek API 进行意图分类
- 更新 State 中的 intent 字段

**输入：**
```python
{
    "input_data": {
        "type": "chat",
        "content": "我昨晚睡得不好",
        "timestamp": "2024-01-01 08:00:00"
    },
    "messages": [...]  # 历史对话（可选）
}
```

**处理逻辑：**
```python
def recognize_intent(state: AgentState) -> AgentState:
    """
    意图识别节点
    使用 DeepSeek 对输入进行分类
    """
    prompt = build_intent_prompt(state["input_data"], state["messages"])
    response = call_deepseek_api(prompt, model="deepseek-chat")
    
    # 解析返回结果
    intent = parse_intent(response)  # "sleep_analysis" | "chat_analysis" | "emergency"
    confidence = extract_confidence(response)
    reasoning = extract_reasoning(response)
    
    return {
        "intent": intent,
        "intent_confidence": confidence,
        "intent_reasoning": reasoning,
        "tokens_used": response.usage.total_tokens
    }
```

**Prompt 模板：**
```
你是一个养老监护平台的意图识别助手。请分析用户输入，判断其意图类别。

可用类别：
1. sleep_analysis - 与睡眠相关的问题（睡眠质量、失眠、作息等）
2. chat_analysis - 日常聊天、情感交流、认知训练等
3. emergency - 紧急情况（摔倒、身体不适、危险等）

用户输入：{input_content}
历史对话：{conversation_history}

请以 JSON 格式返回：
{
    "intent": "类别名称",
    "confidence": 0.95,
    "reasoning": "判断理由"
}
```

---

#### 3.2.2 睡眠分析节点 (analyze_sleep)

**职责：**
- 接收睡眠相关数据
- 调用 DeepSeek API 进行睡眠质量分析
- 生成健康建议

**输入：**
```python
{
    "input_data": {
        "type": "sleep",
        "record": {
            "duration": 420,  # 总睡眠时长（分钟）
            "deep_sleep": 90,  # 深睡时长
            "light_sleep": 280,  # 浅睡时长
            "wake_up_count": 3,  # 醒来次数
            "sleep_score": 75  # 睡眠评分
        }
    },
    "intent": "sleep_analysis"
}
```

**处理逻辑：**
```python
def analyze_sleep(state: AgentState) -> AgentState:
    """
    睡眠分析节点
    分析睡眠数据并生成报告
    """
    sleep_data = state["input_data"]["record"]
    prompt = build_sleep_analysis_prompt(sleep_data)
    response = call_deepseek_api(prompt, model="deepseek-chat")
    
    analysis = parse_sleep_analysis(response)
    
    return {
        "analysis_result": analysis,
        "analysis_type": "sleep",
        "tokens_used": response.usage.total_tokens
    }
```

**Prompt 模板：**
```
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
{
    "quality": "评估等级",
    "issues": ["问题 1", "问题 2"],
    "recommendations": ["建议 1", "建议 2"],
    "summary": "总结性评价"
}
```

---

#### 3.2.3 聊天分析节点 (analyze_chat)

**职责：**
- 接收聊天内容
- 进行情绪识别和认知能力评估
- 发现潜在风险（如抑郁倾向）

**输入：**
```python
{
    "input_data": {
        "type": "chat",
        "content": "最近总觉得没意思，不想说话",
        "session_id": "xxx"
    },
    "messages": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]
}
```

**处理逻辑：**
```python
def analyze_chat(state: AgentState) -> AgentState:
    """
    聊天分析节点
    分析情绪、认知状态和风险
    """
    chat_content = state["input_data"]["content"]
    conversation = state["messages"]
    
    prompt = build_chat_analysis_prompt(chat_content, conversation)
    response = call_deepseek_api(prompt, model="deepseek-chat")
    
    analysis = parse_chat_analysis(response)
    
    return {
        "analysis_result": analysis,
        "analysis_type": "chat",
        "tokens_used": response.usage.total_tokens
    }
```

**Prompt 模板：**
```
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
{
    "emotion": "情绪类型",
    "emotion_score": 65,
    "cognitive_level": "认知等级",
    "risk_level": "risk_level",
    "topics": ["话题 1", "话题 2"],
    "warnings": ["预警信号"],
    "suggestions": ["建议"]
}
```

---

#### 3.2.4 结果汇总节点 (aggregate_result)

**职责：**
- 整合各 Agent 的分析结果
- 格式化输出
- 记录日志和统计信息

**处理逻辑：**
```python
def aggregate_result(state: AgentState) -> AgentState:
    """
    结果汇总节点
    整合分析结果并准备最终输出
    """
    final_output = {
        "intent": state["intent"],
        "intent_reasoning": state["intent_reasoning"],
        "analysis_type": state["analysis_type"],
        "analysis_result": state["analysis_result"],
        "metadata": {
            "tokens_used": state["tokens_used"],
            "processed_at": datetime.now().isoformat()
        }
    }
    
    return {
        "output": final_output,
        "updated_at": datetime.now()
    }
```

---

### 3.3 Edge 设计

#### 3.3.1 条件路由边 (route_by_intent)

**职责：**
- 根据 intent 字段决定下一个节点
- 实现动态分支逻辑

**实现：**
```python
def route_by_intent(state: AgentState) -> str:
    """
    条件路由函数
    根据意图分类结果路由到不同的专业 Agent
    """
    intent = state.get("intent")
    
    if intent == "sleep_analysis":
        return "analyze_sleep"
    elif intent == "chat_analysis":
        return "analyze_chat"
    elif intent == "emergency":
        return "handle_emergency"  # 可扩展紧急处理节点
    else:
        return "handle_unknown"  # 未知意图处理
```

---

### 3.4 Graph 构建

**完整 Graph 组装：**

```python
from langgraph.graph import StateGraph, END

def build_agent_graph():
    """
    构建完整的 Agent Graph
    """
    # 1. 创建 StateGraph
    workflow = StateGraph(AgentState)
    
    # 2. 添加节点
    workflow.add_node("recognize_intent", recognize_intent)
    workflow.add_node("analyze_sleep", analyze_sleep)
    workflow.add_node("analyze_chat", analyze_chat)
    workflow.add_node("aggregate_result", aggregate_result)
    
    # 3. 设置入口点
    workflow.set_entry_point("recognize_intent")
    
    # 4. 添加条件边（路由）
    workflow.add_conditional_edges(
        source="recognize_intent",
        condition=route_by_intent,
        mapping={
            "analyze_sleep": "analyze_sleep",
            "analyze_chat": "analyze_chat",
            "handle_emergency": "aggregate_result",  # 紧急情况直接汇总
            "handle_unknown": "aggregate_result"  # 未知意图也汇总
        }
    )
    
    # 5. 添加普通边（专业 Agent → 汇总节点）
    workflow.add_edge("analyze_sleep", "aggregate_result")
    workflow.add_edge("analyze_chat", "aggregate_result")
    
    # 6. 设置结束点
    workflow.add_edge("aggregate_result", END)
    
    # 7. 编译 Graph
    app = workflow.compile()
    
    return app


# 创建应用实例
agent_app = build_agent_graph()
```

---

## 4. 使用示例

### 4.1 睡眠分析场景

```python
# 模拟睡眠数据输入
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

# 运行 Graph
result = agent_app.invoke(initial_state)

# 输出结果
print(result["analysis_result"])
# {
#     "quality": "一般",
#     "issues": ["深睡时间不足", "夜间醒来频繁"],
#     "recommendations": [
#         "保持规律作息，每天固定时间上床",
#         "睡前避免使用电子设备",
#         "适当增加日间运动量"
#     ],
#     "summary": "总体睡眠质量一般，需关注深睡时间偏短问题"
# }
```

---

### 4.2 聊天分析场景

```python
# 模拟聊天输入
initial_state = {
    "input_data": {
        "type": "chat",
        "content": "今天天气不错，出去散了散步，心情好多了"
    },
    "input_type": "chat",
    "intent": None,
    "intent_confidence": 0.0,
    "intent_reasoning": "",
    "analysis_result": None,
    "analysis_type": None,
    "messages": [
        {"role": "user", "content": "最近总觉得闷闷的"},
        {"role": "assistant", "content": "理解您的感受，可以多和家人朋友聊聊天，或者培养一些兴趣爱好"}
    ],
    "created_at": datetime.now(),
    "updated_at": datetime.now(),
    "tokens_used": 0
}

# 运行 Graph
result = agent_app.invoke(initial_state)

# 输出结果
print(result["analysis_result"])
# {
#     "emotion": "积极",
#     "emotion_score": 78,
#     "cognitive_level": "正常",
#     "risk_level": "normal",
#     "topics": ["天气", "户外活动", "心情"],
#     "warnings": [],
#     "suggestions": ["继续保持户外活动", "鼓励参与社交互动"]
# }
```

---

## 5. DeepSeek API 集成

### 5.1 API 封装

```python
import httpx
from typing import List, Dict, Any

class DeepSeekClient:
    """DeepSeek API 客户端封装"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)
    
    def chat(self, messages: List[Dict[str, str]], model: str = "deepseek-chat") -> Dict[str, Any]:
        """
        调用 DeepSeek 聊天接口
        
        Args:
            messages: 对话历史 [{"role": "user|assistant", "content": "..."}]
            model: 模型名称
        
        Returns:
            API 响应（包含 choice 和 usage）
        """
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


# 全局客户端实例
deepseek_client = DeepSeekClient(api_key="your-api-key-here")
```

---

### 5.2 调用工具函数

```python
def call_deepseek_api(prompt: str, model: str = "deepseek-chat") -> Dict[str, Any]:
    """
    调用 DeepSeek API 的便捷函数
    
    Args:
        prompt: 提示词
        model: 模型名称
    
    Returns:
        API 响应
    """
    messages = [
        {"role": "system", "content": "你是一个专业的养老监护助手。"},
        {"role": "user", "content": prompt}
    ]
    
    response = deepseek_client.chat(messages, model=model)
    return response


def build_intent_prompt(input_data: Dict[str, Any], messages: List[Dict[str, str]]) -> str:
    """构建意图识别 Prompt"""
    content = input_data.get("content", str(input_data))
    history = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-5:]]) if messages else "无"
    
    return f"""
你是一个养老监护平台的意图识别助手。请分析用户输入，判断其意图类别。

可用类别：
1. sleep_analysis - 与睡眠相关的问题（睡眠质量、失眠、作息等）
2. chat_analysis - 日常聊天、情感交流、认知训练等
3. emergency - 紧急情况（摔倒、身体不适、危险等）

用户输入：{content}
历史对话：{history}

请以 JSON 格式返回：
{{
    "intent": "类别名称",
    "confidence": 0.95,
    "reasoning": "判断理由"
}}
""".strip()


# ... 其他 prompt 构建函数类似
```

---

## 6. 项目结构

```
xiaohui/
├── backend/
│   ├── pyproject.toml
│   └── ...
└── agents/                    # Agent 代码目录
    ├── __init__.py
    ├── config.py             # 配置管理
    ├── state.py              # State 定义
    ├── nodes/                # 节点实现
    │   ├── __init__.py
    │   ├── intent.py         # 意图识别节点
    │   ├── sleep.py          # 睡眠分析节点
    │   └── chat.py           # 聊天分析节点
    ├── edges.py              # 边（路由）定义
    ├── graph.py              # Graph 构建
    ├── clients/              # API 客户端
    │   ├── __init__.py
    │   └── deepseek.py       # DeepSeek 客户端
    ├── prompts/              # Prompt 模板
    │   ├── __init__.py
    │   ├── intent.py
    │   ├── sleep.py
    │   └── chat.py
    ├── tests/                # 测试用例
    │   ├── test_intent.py
    │   ├── test_sleep.py
    │   └── test_chat.py
    └── demo.py               # Demo 入口
```

---

## 7. 依赖配置

### 7.1 Poetry 依赖

在 `backend/pyproject.toml` 中添加：

```toml
[tool.poetry.dependencies]
python = "^3.10"

# AI 框架
langgraph = ">=0.1.0"
langchain-core = ">=0.1.0"

# HTTP 客户端（用于调用 DeepSeek API）
httpx = ">=0.25.0"

# 配置管理
pydantic = ">=2.0.0"
pydantic-settings = ">=2.0.0"
python-dotenv = ">=1.0.0"

# 日志
structlog = ">=23.0.0"

# 开发依赖
pytest = ">=7.4.0"
pytest-asyncio = ">=0.21.0"
```

---

### 7.2 环境变量配置

创建 `.env` 文件：

```bash
# DeepSeek API 配置
DEEPSEEK_API_KEY=sk-your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 日志配置
LOG_LEVEL=INFO
```

---

## 8. 实施计划

### Phase 1: 基础框架搭建（1-2 天）

- [ ] 创建项目结构和配置文件
- [ ] 实现 DeepSeek API 客户端封装
- [ ] 定义 AgentState 数据结构
- [ ] 搭建 LangGraph 基础框架

### Phase 2: 核心节点开发（2-3 天）

- [ ] 实现意图识别节点（含 Prompt 工程）
- [ ] 实现睡眠分析节点（含 Prompt 工程）
- [ ] 实现聊天分析节点（含 Prompt 工程）
- [ ] 实现条件路由逻辑

### Phase 3: 测试与优化（1-2 天）

- [ ] 编写单元测试
- [ ] 端到端测试（模拟真实场景）
- [ ] Prompt 调优和迭代
- [ ] 性能测试和 Token 消耗分析

### Phase 4: 扩展功能（后续迭代）

- [ ] 添加紧急告警处理节点
- [ ] 集成 Milvus 向量数据库（RAG）
- [ ] 添加记忆机制（Checkpoint）
- [ ] 接入真实传感器数据

---

## 9. 技术要点总结

### 9.1 LangGraph 核心概念应用

| 概念 | 本项目应用 |
|------|----------|
| **State** | AgentState 承载全流程数据 |
| **Node** | 4 个处理节点（意图识别、睡眠分析、聊天分析、结果汇总） |
| **Edge** | 条件边实现动态路由 |
| **Checkpoint** | 后续扩展，支持长对话记忆 |

---

### 9.2 图结构优势

相比线性链条，本设计的优势：

1. **动态路由**：根据意图自动选择处理路径
2. **并行扩展**：可同时运行多个专业 Agent（未来可改为并行执行）
3. **灵活分支**：易于添加新的专业 Agent（如行为分析、健康评估）
4. **可观测性**：每个节点独立，便于调试和监控

---

### 9.3 关键设计决策

1. **统一 State 设计**：所有节点共享同一 State，避免数据传递混乱
2. **JSON 格式输出**：所有 LLM 调用要求返回 JSON，便于程序解析
3. **Token 统计**：在每个节点中累加 tokens_used，便于成本核算
4. **错误处理**：每个节点独立 try-catch，单个节点失败不影响全局

---

## 10. 风险与挑战

### 10.1 技术风险

- **DeepSeek API 稳定性**：需评估服务可用性和延迟
- **Prompt 工程质量**：直接影响意图识别准确率
- **JSON 解析失败**：LLM 返回格式不符合预期

**应对方案：**
- 添加重试机制和降级策略
- 建立 Prompt 测试集，持续优化
- 添加 JSON Schema 验证和容错处理

---

### 10.2 性能挑战

- **多次 LLM 调用**：单次请求可能调用 2-3 次（意图识别 + 专业分析）
- **Token 消耗**：复杂分析场景 Token 用量大

**优化方向：**
- 缓存高频问题的答案
- 对小流量问题使用更轻量的模型
- 合并某些步骤（如意图识别和分析合并）

---

## 11. 下一步行动

1. **确认方案**：Review 本设计方案
2. **环境准备**：安装 Poetry 依赖，配置 DeepSeek API Key
3. **代码实现**：按照项目结构逐步实现各模块
4. **快速验证**：运行 Demo，测试基本流程
5. **迭代优化**：根据测试结果调整 Prompt 和图结构

---

## 附录 A: 完整代码示例

详见后续实现的代码文件。

---

## 附录 B: 参考资料

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [DeepSeek API 文档](https://platform.deepseek.com/api-docs/)
- [LangChain Core 概念](https://python.langchain.com/docs/concepts/)
