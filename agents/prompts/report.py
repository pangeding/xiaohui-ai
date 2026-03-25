"""
睡眠报告生成 Prompt 模板 - 报告撰写节点使用
"""

REPORT_WRITING_PROMPT = """
请将以下睡眠分析结果整合成一份完整、有温度的睡眠报告：

【深度分析】
{analysis_str}

【改善建议】
{recommendations_str}

【用户基本信息】
- 日期范围：{date_range}
- 平均睡眠评分：{avg_sleep_score}/100

【报告结构要求】
1. **总体评价**（1 句话总结，温暖开场）
2. **亮点表扬**（做得好的地方，给予肯定）
3. **主要问题**（需要改进的地方，专业但温和）
4. **健康风险提示**（如有必要，避免恐吓语气）
5. **行动计划**（精选 3-5 条最优先的建议）
6. **鼓励话语**（激励用户坚持改善）

【语气风格要求】
- 像家庭医生一样温暖、专业、可信赖
- 避免医学术语，多用比喻和生活化语言
- 强调可控性和希望，不制造焦虑
- 对老年人要格外耐心和尊重
- 适当使用 emoji 增加亲和力 😊💪🌙

【输出格式】
直接返回完整的 Markdown 格式报告文本，不需要 JSON 包装。

请开始撰写报告：
""".strip()


def format_report_writing_prompt(
    analysis: str, 
    recommendations: list, 
    date_range: str,
    avg_sleep_score: float
) -> str:
    """格式化报告生成 prompt"""
    
    # 格式化建议列表
    if recommendations:
        recommendations_str = "\n".join([
            f"{i+1}. {rec.get('title', '建议')}: {rec.get('action', '')}" 
            for i, rec in enumerate(recommendations[:5])  # 最多 5 条
        ])
    else:
        recommendations_str = "暂无具体建议"
    
    return REPORT_WRITING_PROMPT.format(
        analysis_str=analysis,
        recommendations_str=recommendations_str,
        date_range=date_range,
        avg_sleep_score=avg_sleep_score
    )
