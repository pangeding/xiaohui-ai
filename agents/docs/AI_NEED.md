### 1. 需求设计

常规（日常陪伴）

趋势分析（风险检测）

### 2. 所有原始数据

{
    "day": "2026-03-25",
    "devID": "9451DC57BFD0",
    "avgBRWholeDay": 19, 平均呼吸
    "avgHRWholeDay": 66, 平均心跳
    "maxBRWholeDay": 28, 最大呼吸
    "maxHRWholeDay": 108, 最大心跳
    "minBRWholeDay": 14, 最小呼吸
    "minHRWholeDay": 41, 最小心跳
    "arrayBRWholeDay": [
        60 * 24 个数据 20左右 也有 null
    ],
    "arrayHRWholeDay": [
        60 * 24 个数据 60左右 也有 null
    ],
    "movCountsWholeDay": 187, 移动次数
    "alarmTimesWholeDay": 0, 警告数
    "physiologicalLevel": "A", 生理等级
    "physiologicalScore": 99, 生理得分
    "standardBRWholeDay": 19, 标准呼吸
    "standardHRWholeDay": 60, 标准心跳
    "arrayBRAlarmWholeDay": [],
    "arrayHRAlarmWholeDay": [],
    "brAlarmCountWholeDay": 0, 呼吸警告
    "hrAlarmCountWholeDay": 0, 心跳警告
    "movFrequencyWholeDay": 13, 移动频率
    "snoreDurationWholeDay": 2460, 午睡时间
    "arrayBodyStateWholeDay": [ 身体状态
        60 * 24 个数据 个位数 也有 null
    ],
    "arrayMovCountsWholeDay": [ 移动次数
        60 * 24 个数据 个位数 也有 null
    ],
    "outBedDurationWholeDay": 37260, 不在床上时间
    "sensingDurationWholeDay": 0, 清醒时间
    "movementDurationWholeDay": 14400, 移动时长
    "bodyQuietDurationWholeDay": 32220, 身体安静时间
    "vitalSignTimeAxisWholeDay": [ 时间点（每分钟）
        60 * 24 个 关键时间点
    ]
}

### 3. 中间数据

- **睡眠时长(h)**：`(86400 - outBedDurationWholeDay) / 3600`
- **睡眠效率(%)**：`(bodyQuietDurationWholeDay / (86400 - outBedDurationWholeDay)) * 100`
- **清醒时间占比(%)**：`(sensingDurationWholeDay / (86400 - outBedDurationWholeDay)) * 100`
- **平均心率**：arrayHRWholeDay过滤null后的均值 直接用average就可以了
- **平均呼吸率**：arrayBRWholeDay过滤null后的均值
- **移动频率**：movCountsWholeDay / 24 (次/小时)
- **生理健康评分**：physiologicalScore(0-100)转换为A/B/C/D等级
- **异常事件计数**：alarmTimesWholeDay + brAlarmCountWholeDay + hrAlarmCountWholeDay

### 4. 最终输出结构

```json
{
  "daily_summary": {
    "date": "YYYY-MM-DD",
    "sleep_duration": "X.Xh",
    "sleep_efficiency": "XX%",
    "quality_score": "XX/100"
  },
  "vital_stats": {
    "avg_heart_rate": XX,
    "avg_breath_rate": XX,
    "hr_variability": "low/medium/high"
  },
  "recommendations": [
    "睡眠效率低于理想值(85%+)。建议...",
    "心率变异性表明恢复状态良好。"
  ]
}
```

### 5. 处理流程

1. 原始数据清洗（过滤null值，时间单位转换）
2. 中间数据指标计算
3. 生成结构化健康报告
4. 趋势分析（需多日数据积累）

