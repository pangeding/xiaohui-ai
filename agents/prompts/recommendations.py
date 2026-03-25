"""
个性化建议生成 Prompt 模板 - 建议引擎节点使用
"""

RECOMMENDATIONS_PROMPT = """
基于以上睡眠分析结果，请为该用户制定个性化的睡眠改善计划：

【分析结果摘要】
{analysis_summary}

【已识别的主要问题】
{issues_str}

【用户画像】（可选）
{user_profile_str}

【制定要求】
1. **分优先级**：按 A(紧急)/B(重要)/C(一般) 三级分类
2. **具体可执行**：
   - 不要说"早睡早起"，要说"22:30 上床，7:00 起床"
   - 包含具体的时间点、时长、频率
3. **解释原理**：每条建议都要说明"为什么要这样做"
4. **预期效果和时间线**：给出可量化的预期改善进度
5. **语气风格**：温暖、鼓励、像健康教练，避免说教

【输出格式】
请按以下 JSON 格式返回：
{{
    "recommendations": [
        {{
            "priority": "A",
            "title": "建议标题",
            "current_status": "当前状况描述",
            "action": "具体行动指令",
            "reason": "科学原理/原因",
            "expected_effect": "预期效果",
            "timeline": "预期见效时间"
        }},
        ...
    ],
    "encouragement": "一句鼓励的话语"
}}

请开始制定改善计划：
""".strip()


def format_recommendations_prompt(analysis: str, issues: list, user_profile: dict = None) -> str:
    """格式化建议生成 prompt"""
    
    # 格式化问题列表
    issues_str = "\n".join([f"- {issue}" for issue in issues]) if issues else "暂无明确问题"
    
    # 格式化用户画像
    if user_profile:
        user_profile_str = "\n".join([
            f"- {k}: {v}" for k, v in user_profile.items()
        ])
    else:
        user_profile_str = "未提供用户画像信息"
    
    return RECOMMENDATIONS_PROMPT.format(
        analysis_summary=analysis[:500] + "..." if len(analysis) > 500 else analysis,
        issues_str=issues_str,
        user_profile_str=user_profile_str
    )
