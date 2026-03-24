#!/usr/bin/env python3
"""
Agent MVP Demo
"""
import json
from datetime import datetime
from agents.graph import agent_app

def test_sleep_analysis():
    """测试睡眠分析流程"""
    print("=== 测试睡眠分析 ===")
    initial_state = {
        "input_data": {
            "type": "sleep",
            "record": {
                "duration": 380,
                "deep_sleep": 60,
                "light_sleep": 290,
                "wake_up_count": 5,
                "sleep_score": 65
            }
        },
        "input_type": "sleep",
        "intent": None,
        "intent_confidence": 0.0,
        "intent_reasoning": "",
        "analysis_result": None,
        "analysis_type": None,
        "messages": [],
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "tokens_used": 0
    }

    result = agent_app.invoke(initial_state)
    print(f"意图：{result['intent']}")
    print(f"意图置信度：{result['intent_confidence']}")
    print(f"意图理由：{result['intent_reasoning']}")
    print(f"分析类型：{result['analysis_type']}")
    print(f"分析结果：{json.dumps(result['analysis_result'], ensure_ascii=False, indent=2)}")
    print(f"Token 消耗：{result['tokens_used']}")
    print()

def test_chat_analysis():
    """测试聊天分析流程"""
    print("=== 测试聊天分析 ===")
    initial_state = {
        "input_data": {
            "type": "chat",
            "content": "最近总是感觉心情不好，没什么兴趣出门活动"
        },
        "input_type": "chat",
        "intent": None,
        "intent_confidence": 0.0,
        "intent_reasoning": "",
        "analysis_result": None,
        "analysis_type": None,
        "messages": [],
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "tokens_used": 0
    }

    result = agent_app.invoke(initial_state)
    print(f"意图：{result['intent']}")
    print(f"意图置信度：{result['intent_confidence']}")
    print(f"意图理由：{result['intent_reasoning']}")
    print(f"分析类型：{result['analysis_type']}")
    print(f"情绪状态：{result['analysis_result']['emotion']}")
    print(f"情绪评分：{result['analysis_result']['emotion_score']}")
    print(f"风险等级：{result['analysis_result']['risk_level']}")
    print(f"Token 消耗：{result['tokens_used']}")
    print()

if __name__ == "__main__":
    test_sleep_analysis()
    test_chat_analysis()