from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.nodes.intent import recognize_intent
from agents.nodes.sleep import analyze_sleep
from agents.nodes.chat import analyze_chat
from agents.edges import route_by_intent

def build_agent_graph():
    """构建 Agent 图"""
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
            "analyze_chat": "analyze_chat"
        }
    )

    # 专家节点执行完成后结束
    workflow.add_edge("analyze_sleep", END)
    workflow.add_edge("analyze_chat", END)

    # 编译图
    app = workflow.compile()
    return app

# 全局 Agent 应用实例
agent_app = build_agent_graph()