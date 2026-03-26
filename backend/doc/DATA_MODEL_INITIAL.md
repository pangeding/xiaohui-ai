# 数据模型选型

## 📋 概述

本文档定义 Agent 系统使用的数据模型，包括原始数据、中间数据和结果数据的结构设计。

## 🎯 设计原则

1. **类型安全**: 使用 Python 类型注解和 Pydantic 进行数据验证
2. **可扩展性**: 支持未来数据字段的扩展
3. **性能优化**: 使用轻量级 ORM 框架 peewee
4. **数据完整性**: 通过数据库约束保证数据质量
5. **时间序列友好**: 针对睡眠监测数据的时间序列特性优化

---

## 📊 Raw Data 数据模型

### SleepRecord - 睡眠记录主表

存储每晚的原始睡眠监测数据。

```python
from peewee import Model, CharField, IntegerField, BooleanField, TextField, DateTimeField, DateField
from datetime import datetime

class SleepRecord(Model):
    """
    睡眠记录原始数据表
    
    存储设备采集的每晚睡眠监测原始数据
    """
    # 主键和标识字段
    id = AutoField(primary_key=True)                    # 自增主键
    dev_id = CharField(max_length=64, index=True)       # 设备唯一识别 ID
    day = DateField(index=True)                          # 日期（YYYY-MM-DD）
    algorithm_version = CharField(max_length=32)         # 算法版本号
    
    # 基础状态字段
    ever_fell_asleep = BooleanField(default=False)      # 是否入睡过
    is_effective = BooleanField(default=True)           # 是否有效记录
    
    # 总体评分字段
    sleep_quality_score = IntegerField(default=0)        # 睡眠质量总分 (0-100)
    sleep_level = CharField(max_length=1)                # 睡眠评级 (A/B/C/D/E)
    
    # 得分分配字段（JSON 格式存储数组）
    array_score_assigned = TextField(null=True)          # 睡眠得分分配 [各项总分]
    array_score = TextField(null=True)                   # 睡眠单项得分 [各项得分]
    
    # 时间节点字段（Timestamp）
    inbed_time = DateTimeField(null=True)               # 上床时刻
    asleep_time = DateTimeField(null=True)              # 入睡时刻
    awake_time = DateTimeField(null=True)               # 醒来时刻
    outbed_time = DateTimeField(null=True)              # 起床时刻
    
    # 时长指标字段（单位：秒）
    sleep_onset_latency = IntegerField(default=0)        # 入睡时长
    sleep_duration = IntegerField(default=0)             # 睡眠时长
    inbed_duration = IntegerField(default=0)             # 在床时长
    sober_duration = IntegerField(default=0)             # 觉醒时长
    dream_duration = IntegerField(default=0)             # 做梦时长
    light_sleep_duration = IntegerField(default=0)       # 浅睡时长
    moderate_sleep_duration = IntegerField(default=0)    # 中睡时长
    deep_sleep_duration = IntegerField(default=0)        # 深睡时长
    outbed_duration = IntegerField(default=0)            # 离床时长
    awake_in_sleep_duration = IntegerField(default=0)    # 睡中觉醒时长
    
    # 百分比指标字段（单位：%）
    sleep_efficiency = IntegerField(default=0)           # 睡眠效率
    sober_percent = IntegerField(default=0)              # 觉醒占比
    dream_percent = IntegerField(default=0)              # 做梦占比
    light_sleep_percent = IntegerField(default=0)        # 浅睡占比
    moderate_sleep_percent = IntegerField(default=0)     # 中睡占比
    deep_sleep_percent = IntegerField(default=0)         # 深睡占比
    outbed_percent = IntegerField(default=0)             # 离床占比
    
    # 潜伏期字段（单位：秒）
    dream_latency = IntegerField(default=0)              # 梦境潜伏期
    
    # 事件计数字段
    awake_in_sleep_counts = IntegerField(default=0)      # 睡中觉醒次数
    outbed_counts = IntegerField(default=0)              # 离床次数
    
    # 生命体征字段 - 心率
    standard_hr = IntegerField(default=0)                # 基准心率
    avg_hr = IntegerField(default=0)                     # 平均心率
    max_hr = IntegerField(default=0)                     # 最快心率
    min_hr = IntegerField(default=0)                     # 最慢心率
    sdnn = IntegerField(default=0)                       # 心率变异性 (ms)
    pnn50 = IntegerField(default=0)                      # 心率变异性 (%)
    
    # 生命体征字段 - 呼吸率
    standard_br = IntegerField(default=0)                # 基准呼吸率
    avg_br = IntegerField(default=0)                     # 平均呼吸率
    max_br = IntegerField(default=0)                     # 最快呼吸率
    min_br = IntegerField(default=0)                     # 最慢呼吸率
    
    # 体动字段
    mov_counts = IntegerField(default=0)                 # 体动次数
    mov_frequency = IntegerField(default=0)              # 体动频率 (次/小时)
    
    # 压力指数
    fatigue = IntegerField(default=0)                    # 压力指数 (%)
    
    # 时间序列数据（JSON 格式存储数组）
    sleep_stage = TextField(null=True)                   # 睡眠分期 [整数值]
    sleep_time_axis = TextField(null=True)               # 睡眠时间轴 [时间戳]
    vital_sign_time_axis = TextField(null=True)          # 生命体征时间轴 [时间戳]
    array_hr = TextField(null=True)                      # 心率曲线 [整数值]
    array_br = TextField(null=True)                      # 呼吸率曲线 [整数值]
    array_mov = TextField(null=True)                     # 体动幅度曲线 [整数值]
    array_body_state = TextField(null=True)              # 身体状态图谱 [整数值]
    
    # 离床事件（JSON 格式存储对象数组）
    outbed_events = TextField(null=True)                 # 离床事件 [{time, duration}]
    
    # 审计字段
    created_at = DateTimeField(default=datetime.now)     # 创建时间
    updated_at = DateTimeField(default=datetime.now)     # 更新时间
    
    class Meta:
        table_name = 'sleep_records'
        indexes = (
            (('dev_id', 'day'), True),  # 复合唯一索引
        )
```

### 字段说明

#### 1. 基础标识字段
- `dev_id`: 设备唯一识别码，用于区分不同用户
- `day`: 记录对应的日期，按自然日划分
- `algorithm_version`: 算法版本，用于数据质量控制和回溯

#### 2. 评分相关字段
- `sleep_quality_score`: 0-100 分的总体睡眠质量评分
- `sleep_level`: A/B/C/D/E 五个等级的快速分类
- `array_score_assigned`: 各评分项的总分列表
- `array_score`: 各评分项的原始得分列表

#### 3. 时间节点字段
所有时间戳字段均使用 `DateTimeField`，存储具体时刻：
- `inbed_time`: 上床准备睡觉的时刻
- `asleep_time`: 实际入睡的时刻
- `awake_time`: 早晨醒来的时刻
- `outbed_time`: 起床离开床的时刻

#### 4. 时长指标字段
所有时长字段均以**秒**为单位存储整数：
- 入睡时长、睡眠时长、在床时长等
- 各阶段睡眠时长（浅睡、中睡、深睡、REM）
- 觉醒时长、离床时长等

#### 5. 百分比字段
所有百分比字段均以**整数百分比**存储（0-100）：
- 睡眠效率、各阶段占比等

#### 6. 时间序列数据
以下字段使用 JSON 格式存储数组数据：
- `sleep_stage`: 睡眠分期序列，如 `[1,2,3,2,1,4,...]`
- `sleep_time_axis`: 对应的时间轴，ISO 8601 格式字符串数组
- `array_hr`: 心率曲线数据点数组
- `array_br`: 呼吸率曲线数据点数组
- `array_mov`: 体动幅度曲线数据点数组
- `array_body_state`: 身体状态图谱数组

#### 7. 事件数据
- `outbed_events`: JSON 格式存储离床事件数组，每个事件包含时间和持续时间

---

## 🔄 中间数据模型

### （待补充）

用于存储分析过程中的中间结果，例如：
- 数据质量评估结果
- 特征工程提取的特征向量
- 模式识别的中间状态
- ...

---

## 📈 结果数据模型

### （待补充）

用于存储最终的分析结果，例如：
- 睡眠质量评估报告
- 健康建议生成结果
- 趋势分析和预测结果
- ...

---

## 💡 使用示例

### 初始化数据库

```python
from peewee import SqliteDatabase

# 创建数据库连接
db = SqliteDatabase('sleep_data.db')

# 绑定到模型
SleepRecord.bind(db)

# 创建表
db.create_tables([SleepRecord])
```

### 插入睡眠记录

```python
import json
from datetime import datetime, date

# 准备数据
record_data = {
    'dev_id': 'DEVICE_001',
    'day': date(2024, 3, 20),
    'algorithm_version': 'v2.1.0',
    'ever_fell_asleep': True,
    'is_effective': True,
    'sleep_quality_score': 85,
    'sleep_level': 'B',
    'sleep_duration': 28800,  # 8 小时
    'sleep_efficiency': 92,
    'avg_hr': 65,
    'avg_br': 16,
    'sleep_stage': json.dumps([1, 2, 3, 2, 1, 4, 2, 3]),
    'array_hr': json.dumps([62, 63, 65, 64, 66, 68, 65, 63]),
}

# 创建记录
SleepRecord.create(**record_data)
```

### 查询睡眠记录

```python
# 查询指定设备的记录
records = (SleepRecord
           .select()
           .where(SleepRecord.dev_id == 'DEVICE_001')
           .order_by(SleepRecord.day.desc())
           .limit(30))

for record in records:
    print(f"日期：{record.day}, 睡眠质量：{record.sleep_quality_score}, 时长：{record.sleep_duration/3600:.1f}小时")
```

### 数据分析查询

```python
from peewee import fn

# 计算平均睡眠质量
avg_quality = (SleepRecord
               .select(fn.AVG(SleepRecord.sleep_quality_score))
               .where(SleepRecord.dev_id == 'DEVICE_001')
               .scalar())

# 统计各睡眠等级分布
level_distribution = (SleepRecord
                      .select(SleepRecord.sleep_level, fn.COUNT(SleepRecord.id))
                      .where(SleepRecord.dev_id == 'DEVICE_001')
                      .group_by(SleepRecord.sleep_level))
```

---

## 🔧 数据库优化建议

### 索引策略

1. **复合索引**: `(dev_id, day)` 用于快速查询指定设备的睡眠记录
2. **时间索引**: `day` 字段单独索引，支持时间范围查询
3. **质量索引**: `is_effective` 和 `sleep_level` 可考虑索引，用于筛选和分组

### 分区策略

对于大规模数据，可以考虑：
- 按 `day` 字段进行月度或年度分区
- 按 `dev_id` 哈希分区，实现多用户数据物理隔离

### 数据归档

- 热数据：最近 6 个月的记录，存储在高性能存储
- 温数据：6 个月 -2 年的记录，可压缩存储
- 冷数据：2 年以上的记录，归档到低成本存储

---

## 📚 参考资料

- [Peewee ORM 官方文档](https://docs.peewee-orm.com/)
- [Python 数据模型最佳实践](https://docs.python.org/3/reference/datamodel.html)
- [时间序列数据库设计模式](https://martinfowler.com/articles/time-series-patterns.html)
