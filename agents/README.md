### 0. 问题？
1. 睡眠质量总分是如何计算的？
2. 如何利用已有的评分和评级提供更有价值的洞察？
3. **核心问题：哪些必须用 AI？哪些用代码就够了？**

### 0.1 技术选型原则

**✅ 用传统代码 (规则/统计/ML):**
- 数据清洗、验证
- 指标计算 (平均值、占比、趋势)
- 异常检测 (基于阈值)
- 模式识别 (聚类、统计规律)
- 标签生成 (基于规则)

**✅ 必须用 AI (LLM):**
- 生成自然语言报告 (可读性强、有温度)
- 个性化建议 (综合考虑多因素、像专家一样思考)
- 复杂因果推理 (为什么睡不好？多因素关联)
- 情感支持和激励 (共情用户、行为改变引导)

**❌ 不需要 AI:**
- 简单的 if-else 判断
- 数学计算
- 数据转换

我看了一下睡眠的数据模型和具体数据，我现在想的是先起一个python的ai服务，有基本 REST Api接口，然后原始数据和分析数据落库，ai生成的建议和报告每天推送给用户。
公司内部和别的后端比如java和前端，通过REST api进行交互。


### 1. 主要功能

**核心价值**: 
- **代码做计算** - 高效、准确地处理数据
- **AI 做解读** - 像睡眠专家一样分析和建议
- **人机协作** - 代码 + AI 各自发挥优势
功能：
1. 每日对每个用户分析原始数据，将中间数据落库，ai报告落库吧，每日推送ai睡眠报告给用户
2. 趋势分析，
3. 警告推送，
### 2. 全流程

```
[代码节点] 数据获取 → 数据清洗 → 指标计算 → 异常检测 → 标签生成
                                              ↓
                                    [AI 节点] 深度分析
                                              ↓
                                    [AI 节点] 报告生成
                                              ↓
                                    [AI 节点] 建议生成

趋势分析

警告推送
```

### 3. 具体节点

#### 3.1 【代码节点】数据获取与验证
**实现方式**: Python 函数
```python
def validate_sleep_data(data: Dict) -> bool:
    required_fields = ['devID', 'day', 'sleepQualityScore']
    return all(field in data for field in required_fields) and data['isEffective']
```

#### 3.2 【代码节点】数据清洗
**实现方式**: Pandas/NumPy
```python
def clean_data(data: List[Dict]) -> List[Dict]:
    # 处理缺失值、异常值
    df = pd.DataFrame(data)
    df.fillna(method='ffill', inplace=True)
    # 移除心率>200 或<30 的异常记录
    df = df[(df['avgHR'] >= 30) & (df['avgHR'] <= 200)]
    return df.to_dict('records')
```

#### 3.3 【代码节点】指标计算
**实现方式**: 统计计算
```python
def calculate_metrics(data: List[Dict]) -> Dict:
    metrics = {
        'avg_sleep_duration': np.mean([d['sleepDuration'] for d in data]),
        'sleep_efficiency_avg': np.mean([d['sleepEfficiency'] for d in data]),
        'bedtime_regularity': np.std([d['inbedTime'] for d in data]),
        'deep_sleep_ratio': np.mean([d['deepSleepPercent'] for d in data]),
        'awakening_frequency': np.sum([d['awake_in_sleep_counts'] for d in data]) / len(data)
    }
    return metrics
```

#### 3.4 【代码节点】异常检测
**实现方式**: 规则引擎 + 统计方法
```python
def detect_anomalies(record: Dict) -> List[Dict]:
    anomalies = []
    
    # 规则 1: 入睡困难
    if record['sleepOnsetLatency'] > 1800:  # 30 分钟
        anomalies.append({
            'type': 'INSOMNIA_RISK',
            'severity': 'HIGH' if record['sleepOnsetLatency'] > 3600 else 'MEDIUM',
            'evidence': f"入睡时长{record['sleepOnsetLatency']//60}分钟，超过正常范围"
        })
    
    # 规则 2: 深睡不足
    if record['deepSleepPercent'] < 10:
        anomalies.append({
            'type': 'DEEP_SLEEP_DEFICIENCY',
            'severity': 'MEDIUM',
            'evidence': f"深睡占比仅{record['deepSleepPercent']}%，低于正常值 (13-23%)"
        })
    
    # 规则 3: 心率变异性低 (压力大)
    if record['SDNN'] < 50:
        anomalies.append({
            'type': 'HIGH_STRESS',
            'severity': 'HIGH',
            'evidence': f"SDNN 仅{record['SDNN']}ms，提示自主神经功能紊乱"
        })
    
    return anomalies
```

#### 3.5 【代码节点】标签生成
**实现方式**: 规则匹配
```python
def generate_labels(metrics: Dict, anomalies: List) -> List[str]:
    labels = []
    
    if any(a['type'] == 'INSOMNIA_RISK' for a in anomalies):
        labels.append('#入睡困难')
    
    if metrics['deep_sleep_ratio'] < 10:
        labels.append('#深睡不足')
    
    if metrics['bedtime_regularity'] > 7200:  # 标准差>2 小时
        labels.append('#作息不规律')
    
    if metrics['awakening_frequency'] > 5:
        labels.append('#频繁觉醒')
    
    return labels
```

---

#### 3.6 【AI 节点】深度分析 ⭐ **必须用 AI**

**为什么必须用 AI:**
- 需要综合多个指标进行**因果推理**
- 需要**医学知识**来判断严重性
- 需要**类比推理**(类似案例的经验)

**输入:**
```python
{
    'metrics': {...},  # 计算好的指标
    'anomalies': [...],  # 异常列表
    'labels': ['#入睡困难', '#深睡不足'],
    'raw_data': [...]  # 原始数据 (可选)
}
```

**Prompt 示例:**
```
你是一位睡眠医学专家。请根据以下数据分析用户的睡眠问题:

【基本信息】
- 平均睡眠时长：6.2 小时
- 睡眠效率：78%
- 深睡占比：8%
- 入睡潜伏期：45 分钟
- 夜间觉醒次数：7 次

【已识别问题】
- #入睡困难
- #深睡不足
- #频繁觉醒

【任务】
1. 分析这些问题的可能原因 (考虑相互关联性)
2. 评估严重程度 (轻度/中度/重度)
3. 推测对健康的影响 (短期 + 长期)
4. 给出初步判断

请用专业但易懂的语言回答。
```

**AI 输出示例:**
```
根据数据分析，该用户存在中度睡眠障碍，主要表现为:

1. **核心问题**: 睡眠维持困难伴深睡不足
   - 入睡需要 45 分钟 (正常<30 分钟)
   - 夜间觉醒 7 次 (正常<3 次),导致睡眠碎片化
   - 深睡仅 8% (正常 13-23%),身体修复不足

2. **可能原因分析**:
   - 生理因素：压力激素 (皮质醇) 水平偏高，抑制深睡
   - 行为因素：睡前使用电子设备、咖啡因摄入过晚
   - 环境因素：卧室温度/噪音干扰 (需进一步询问)

3. **健康影响**:
   - 短期：白天疲劳、注意力下降、情绪波动
   - 长期：免疫力下降、心血管风险增加、认知功能衰退

4. **严重程度**: 中度 (建议干预)
```

---

#### 3.7 【AI 节点】个性化建议生成 ⭐ **必须用 AI**

**为什么必须用 AI:**
- 需要**权衡优先级**(先解决哪个问题)
- 需要**个性化**(考虑用户生活方式)
- 需要**行为心理学**(让建议可执行、可持续)

**Prompt 示例:**
```
基于以上分析，请为该用户制定改善计划:

【要求】
1. 分优先级 (紧急/重要/一般)
2. 具体可执行 (不要说"早睡早起",要说"22:30 上床")
3. 解释原理 (让用户理解为什么要这样做)
4. 给出预期效果和时间线
5. 语气温暖、鼓励而非说教

【用户画像】(可选)
- 年龄：65 岁
- 职业：退休
- 习惯：午睡 2 小时、晚上喝茶
```

**AI 输出示例:**
```
🌙 您的专属睡眠改善计划

【优先级 A - 本周开始】
1. **调整午睡时间** 
   - 当前：午睡 2 小时 (14:00-16:00)
   - 建议：缩短至 30 分钟 (13:00-13:30)
   - 原因：过长午睡会消耗夜间睡眠驱动力
   - 预期：3-5 天内入睡时间缩短

2. **建立睡前仪式**
   - 21:30 后避免饮茶/咖啡
   - 22:00 关闭电视/手机
   - 22:30 上床，进行腹式呼吸放松
   - 原因：蓝光抑制褪黑素，咖啡因半衰期 6 小时

【优先级 B - 下周开始】
3. **增加日间光照**
   - 早上 7:00-8:00 户外散步 30 分钟
   - 原因：晨光重置生物钟，提升夜间深睡

【预期进展】
- 第 1 周：入睡时间缩短至 20 分钟内
- 第 2 周：夜间觉醒减少到 3-4 次
- 第 4 周：深睡占比提升至 12-15%

💪 加油！坚持 2 周就能看到明显改善!
```

---

#### 3.8 【AI 节点】报告生成 ⭐ **必须用 AI**

**为什么必须用 AI:**
- 需要**叙事能力**(把数据变成故事)
- 需要**共情**(理解用户感受)
- 需要**风格调整**(对老人要用温和语气)

**Prompt 示例:**
```
请将以下分析结果整合成一份完整的睡眠报告:

【分析报告结构】
1. 总体评价 (一句话总结)
2. 亮点表扬 (做得好的地方)
3. 主要问题 (需要改进的地方)
4. 健康风险提示
5. 行动计划
6. 鼓励话语

【语气要求】
- 温暖、专业、像家庭医生
- 避免恐吓，强调可控性
- 多用比喻，少用术语
```
#### 3.6 趋势追踪与报告
- 7 天/30 天/90 天趋势分析
- 改善进度追踪
- 预警阈值设置与通知


---

### 4. 技术架构

#### 4.1 系统架构图

```
┌─────────────────────────────────────────────┐
│          传统代码层 (Python)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 数据获取 │→│ 数据清洗 │→│ 指标计算 │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                          ↓                  │
│                    ┌──────────┐             │
│                    │ 异常检测 │             │
│                    │ (规则引擎)│             │
│                    └──────────┘             │
│                          ↓                  │
│                    ┌──────────┐             │
│                    │ 标签生成 │             │
│                    │ (规则匹配)│             │
└─────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────┐
│           AI 层 (LangGraph + LLM)            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 深度分析 │→│ 建议生成 │→│ 报告生成 │  │
│  │ (推理)   │  │ (规划)   │  │ (写作)   │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────┘
```

#### 4.2 Agent 状态定义 (简化)

```python
class SleepAnalysisState(TypedDict):
    raw_data: List[Dict]           # 原始数据
    metrics: Dict                  # [代码计算] 指标
    anomalies: List[Dict]          # [代码检测] 异常
    labels: List[str]              # [代码生成] 标签
    analysis: str                  # [AI 生成] 深度分析
    recommendations: List[Dict]    # [AI 生成] 建议
    report: str                    # [AI 生成] 完整报告
```

#### 4.3 工作流

```python
# 伪代码
def analyze_sleep(state: SleepAnalysisState):
    # === 代码部分 (90% 的工作) ===
    validated = validate_data(state['raw_data'])
    cleaned = clean_data(validated)
    metrics = calculate_metrics(cleaned)
    anomalies = detect_anomalies(cleaned)
    labels = generate_labels(metrics, anomalies)
    
    # === AI 部分 (10%,但最关键) ===
    analysis = llm.analyze(metrics, anomalies, labels)
    recommendations = llm.generate_recommendations(analysis)
    report = llm.write_report(analysis, recommendations)
    
    return {
        'metrics': metrics,
        'anomalies': anomalies,
        'labels': labels,
        'analysis': analysis,
        'recommendations': recommendations,
        'report': report
    }
```

### 5. 附录

#### 5.1 睡眠数据

| 数据名称 | 数据类型 | 说明 | 分析用途 |
|---------|---------|------|---------|
| devID | String | 设备唯一识别 ID | 用户标识 |
| day | String | 日期 | 时间序列索引 |
| algorithmVersion | String | 算法版本 | 数据质量控制 |
| everFellAsleep | Boolean | 是否入睡过 | 筛选有效记录 |
| sleepQualityScore | Integer | 睡眠质量总分，0~100 分 | 总体评估指标 |
| sleepLevel | String | 睡眠评级，A/B/C/D/E 五个等级 | 快速分类 |
| arrayScoreAssigned | Array<Integer> | 睡眠得分分配，各项总分 | 评分解构分析 |
| arrayScore | Array<Integer> | 睡眠单项得分 | 短板识别 |
| inbedTime | Timestamp | 上床时刻 | 作息规律性 |
| asleepTime | Timestamp | 入睡时刻 | 入睡难度 |
| awakeTime | Timestamp | 醒来时刻 | 觉醒模式 |
| outbedTime | Timestamp | 起床时刻 | 作息规律性 |
| sleepOnsetLatency | Integer | 入睡时长，单位 s | 失眠判断 (>30min) |
| sleepDuration | Integer | 睡眠时长，单位 s | 充足度评估 |
| inbedDuration | Integer | 在床时长，单位 s | 卧床时间 |
| sleepEfficiency | Integer | 睡眠效率% | 睡眠质量核心指标 |
| soberDuration | Integer | 觉醒时长，单位 s | 睡眠连续性 |
| dreamDuration | Integer | 做梦时长，单位 s | REM 睡眠 |
| lightSleepDuration | Integer | 浅睡时长，单位 s | 睡眠深度 |
| moderateSleepDuration | Integer | 中睡时长，单位 s | 睡眠结构 |
| deepSleepDuration | Integer | 深睡时长，单位 s | 恢复质量 |
| outbedDuration | Integer | 离床时长，单位 s | 夜间干扰 |
| soberPercent | Integer | 觉醒占比% | 碎片化程度 |
| dreamPercent | Integer | 做梦占比% | REM 占比 |
| lightSleepPercent | Integer | 浅睡占比% | 结构分析 |
| moderateSleepPercent | Integer | 中睡占比% | 结构分析 |
| deepSleepPercent | Integer | 深睡占比% | 深度评估 |
| outbedPercent | Integer | 离床占比% | 连续性 |
| dreamLatency | Integer | 梦境潜伏期，单位 s | REM 延迟 |
| awake_in_sleep_counts | Integer | 睡中觉醒次数 | 碎片化指标 |
| awake_in_sleep_duration | Integer | 睡中觉醒时长，单位 s | 觉醒严重度 |
| sleepStage | Array<Integer> | 睡眠分期 | 周期分析 |
| sleepTimeAxis | Array<Timestamp> | 睡眠时间轴 | 可视化 |
| outbedCounts | Integer | 离床次数 | 夜间活动 |
| outbedEvents | Array<Object> | 离床事件 | 异常检测 |
| arrayHR | Array<Integer> | 心率曲线 | 心脏健康 |
| standardHR | Integer | 基准心率 | 基线对比 |
| avgHR | Integer | 平均心率 | 心血管负荷 |
| maxHR | Integer | 最快心率 | 极端情况 |
| minHR | Integer | 最慢心率 | 基础代谢 |
| SDNN | Integer | 心率变异性，单位 ms | 自主神经功能 |
| PNN50 | Integer | 心率变异性，单位% | 迷走神经张力 |
| fatigue | Integer | 压力指数，单位% | 精神压力 |
| arrayBR | Array<Integer> | 呼吸率曲线 | 呼吸健康 |
| standardBR | Integer | 基准呼吸率 | 基线对比 |
| avgBR | Integer | 平均呼吸率 | 呼吸功能 |
| maxBR | Integer | 最快呼吸率 | 异常检测 |
| minBR | Integer | 最慢呼吸率 | 异常检测 |
| arrayMov | Array<Integer> | 体动幅度曲线 | 活动分析 |
| movCounts | Integer | 体动次数 | 不安腿综合征 |
| movFrequency | Integer | 体动频率，次/小时 | 睡眠稳定性 |
| arrayBodyState | Array<Integer> | 身体状态图谱 | 姿势分析 |
| vitalSignTimeAxis | Array<Timestamp> | 生命体征时间轴 | 同步分析 |
| isEffective | Boolean | 是否有效 | 数据筛选 |

#### 5.2 关键阈值参考

**医学指南参考值:**
- 睡眠效率：<85% 为差，85-90% 为中，>90% 为优
- 入睡潜伏期：>30 分钟为入睡困难
- 深睡占比：正常 13-23%，<10% 为不足
- REM 占比：正常 20-25%
- 觉醒次数：>5 次为频繁
- SDNN：<50ms 为高压力，50-100ms 为中等，>100ms 为良好

#### 5.3 睡眠标签体系

**问题标签:**
- #入睡困难 (sleepOnsetLatency > 30min)
- #早醒 (awakeTime 比平时早>2h)
- #睡眠浅 (lightSleepPercent > 60%)
- #深睡不足 (deepSleepPercent < 10%)
- #频繁觉醒 (awake_in_sleep_counts > 5)
- #作息不规律 (上床时间标准差>2h)
- #睡眠呼吸暂停风险 (avgBR 异常 + 血氧数据)
- #压力过大 (fatigue > 70%)

**改善标签:**
- #睡眠高效 (sleepEfficiency > 90%)
- #作息规律 (标准差<30min)
- #深度睡眠好 (deepSleepPercent > 15%)
- #快速入睡 (sleepOnsetLatency < 15min)