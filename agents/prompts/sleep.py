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