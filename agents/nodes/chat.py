from agents.state import AgentState
from agents.clients.deepseek import DeepSeekClient
from agents.prompts.chat import CHAT_ANALYSIS_PROMPT_TEMPLATE
import json

def analyze_chat(state: AgentState) -> AgentState:
    """聊天分析节点"""
    client = DeepSeekClient()

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

    try:
        response = client.chat(messages)
        analysis = json.loads(response["choices"][0]["message"]["content"])

        return {
            "analysis_result": analysis,
            "analysis_type": "chat",
            "tokens_used": response["usage"]["total_tokens"]
        }
    except Exception as e:
        return {
            "analysis_result": {
                "emotion": "未知",
                "emotion_score": 0,
                "cognitive_level": "未知",
                "risk_level": "normal",
                "topics": [],
                "warnings": ["分析失败"],
                "suggestions": ["请检查输入数据"]
            },
            "analysis_type": "chat",
            "tokens_used": 0
        }