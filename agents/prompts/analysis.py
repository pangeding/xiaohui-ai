"""
AI 分析 Prompt 模板 - 深度分析节点使用
"""

DEEP_ANALYSIS_PROMPT = """
你是一位睡眠医学专家，拥有丰富的临床经验。请根据以下数据分析用户的睡眠问题：

【基本信息】
- 平均睡眠时长：{avg_sleep_duration} 小时
- 睡眠效率：{sleep_efficiency_avg}%
- 深睡占比：{deep_sleep_ratio}%
- 入睡潜伏期：{sleep_onset_latency} 分钟
- 夜间觉醒次数：{awakening_frequency} 次

【已识别问题】
{labels_str}

【异常检测详情】
{anomalies_str}

【任务要求】
1. **因果分析**：分析这些问题的可能原因，考虑各指标间的相互关联性
2. **严重程度评估**：判断是轻度/中度/重度，并说明依据
3. **健康影响推测**：分别说明短期和长期可能的健康影响
4. **初步判断**：给出你的专业判断

【输出要求】
- 用专业但易懂的语言回答
- 分点论述，逻辑清晰
- 避免过度恐吓，强调可控性
- 如有必要，指出需要进一步排查的因素

请开始你的分析：
""".strip()


def format_deep_analysis_prompt(metrics: dict, anomalies: list, labels: list) -> str:
    """格式化深度分析 prompt"""
    
    # 格式化标签字符串
    labels_str = "\n".join([f"- {label}" for label in labels]) if labels else "暂无明显问题标签"
    
    # 格式化异常详情
    if anomalies:
        anomalies_str = "\n".join([
            f"- {a['type']}: {a['evidence']} (严重程度：{a['severity']})" 
            for a in anomalies
        ])
    else:
        anomalies_str = "未检测到明显异常"
    
    return DEEP_ANALYSIS_PROMPT.format(
        avg_sleep_duration=metrics.get('avg_sleep_duration', 0) / 3600,  # 秒转小时
        sleep_efficiency_avg=metrics.get('sleep_efficiency_avg', 0),
        deep_sleep_ratio=metrics.get('deep_sleep_ratio', 0),
        sleep_onset_latency=metrics.get('sleep_onset_latency', 0) / 60,  # 秒转分钟
        awakening_frequency=metrics.get('awakening_frequency', 0),
        labels_str=labels_str,
        anomalies_str=anomalies_str
    )
