from agents.state import AgentState
from agents.clients.deepseek import DeepSeekClient
from agents.prompts.intent import INTENT_PROMPT_TEMPLATE
import json

def recognize_intent(state: AgentState) -> AgentState:
    """意图识别节点"""
    client = DeepSeekClient()

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

    try:
        response = client.chat(messages)
        result = json.loads(response["choices"][0]["message"]["content"])

        # 更新状态
        return {
            "intent": result["intent"],
            "intent_confidence": result["confidence"],
            "intent_reasoning": result["reasoning"],
            "tokens_used": response["usage"]["total_tokens"]
        }
    except Exception as e:
        # 错误处理：返回默认意图
        return {
            "intent": "chat_analysis",
            "intent_confidence": 0.0,
            "intent_reasoning": f"意图识别失败: {str(e)}",
            "tokens_used": 0
        }