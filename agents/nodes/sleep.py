from agents.state import AgentState
from agents.clients.deepseek import DeepSeekClient
from agents.prompts.sleep import SLEEP_ANALYSIS_PROMPT_TEMPLATE
import json

def analyze_sleep(state: AgentState) -> AgentState:
    """睡眠分析节点"""
    client = DeepSeekClient()

    sleep_data = state["input_data"]["record"]
    prompt = SLEEP_ANALYSIS_PROMPT_TEMPLATE.format(**sleep_data)

    messages = [
        {"role": "system", "content": "你是专业的睡眠健康分析师。"},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat(messages)
        analysis = json.loads(response["choices"][0]["message"]["content"])

        return {
            "analysis_result": analysis,
            "analysis_type": "sleep",
            "tokens_used": response["usage"]["total_tokens"]
        }
    except Exception as e:
        return {
            "analysis_result": {
                "quality": "分析失败",
                "issues": ["数据解析错误"],
                "recommendations": ["请检查输入数据格式"],
                "summary": str(e)
            },
            "analysis_type": "sleep",
            "tokens_used": 0
        }