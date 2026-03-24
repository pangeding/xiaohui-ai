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