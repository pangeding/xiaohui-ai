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