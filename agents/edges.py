from agents.state import AgentState

def route_by_intent(state: AgentState) -> str:
    """根据意图路由到不同节点"""
    intent = state.get("intent")

    if intent == "sleep_analysis":
        return "analyze_sleep"
    elif intent == "chat_analysis":
        return "analyze_chat"
    else:
        # 默认路由到聊天分析（或可以添加一个错误处理节点）
        return "analyze_chat"