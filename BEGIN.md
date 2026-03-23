# 1. 项目介绍

xiaohui 是一个 AI 养老监护平台，致力于通过智能化技术提升老年人的生活质量和安全保障。系统主要包含后端服务、AI Agent 智能体集群和前端监控平台三部分，整体部署在阿里云平台上。

## 1.1 核心功能

### 安全监测
- **烟雾报警**：实时接收烟雾传感器数据，发现异常立即告警
- **燃气监测**：监控燃气泄漏风险，及时推送预警信息
- **摔倒检测**：通过视觉或雷达传感器识别老人摔倒事件，触发紧急救援流程

### 健康管理
- **睡眠分析**：采集睡眠质量数据，进行长期趋势分析和健康评估
- **智能聊天**：记录和分析老人日常对话，评估心理状态和认知能力

### 智能处理
- **分级告警**：根据事件紧急程度（烟雾/燃气/摔倒 > 睡眠/聊天）进行差异化处理
- **意图识别**：由意图分析 Agent 统一调度各子 Agent 进行多维度数据分析
- **推送通知**：紧急事件实时推送给前端监控人员和家属

---

# 2. 项目架构

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                 │
│                  监控 dashboard + 管理后台               │
└────────────────────┬────────────────────────────────────┘
                     │ REST API / WebSocket
┌────────────────────┴────────────────────────────────────┐
│                   Backend (FastAPI)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │  API Gateway│  │ 业务逻辑层  │  │   消息队列      │ │
│  │             │  │             │  │  (Redis Queue)  │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
│  ┌──────────────────────────────────────────────────┐   │
│  │           Data Access Layer                      │   │
│  │  MySQL ←→ Peewee | Redis ←→ redis-py | Milvus   │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │ RPC / Message Queue
┌────────────────────┴────────────────────────────────────┐
│                AI Agent Cluster (LangGraph)             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │意图分析Agent│  │睡眠分析Agent│  │  聊天分析 Agent  │ │
│  │  (Router)   │  │  (Analyzer) │  │   (Analyzer)    │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
│  ┌──────────────────────────────────────────────────┐   │
│  │        Model: 阿里百炼 + Vector DB: Milvus       │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 2.1 架构分层说明

### 表现层 (Frontend)
- 实时监控大屏：展示传感器状态、告警信息、老人位置等
- 管理后台：用户管理、设备管理、数据分析报表
- 移动端 H5：家属端小程序/H5，接收推送和查看报告

### 业务层 (Backend)
- API 网关：统一入口，鉴权、限流、日志
- 业务逻辑：设备接入、数据处理、告警规则引擎
- 消息队列：异步任务处理、削峰填谷、解耦服务

### 数据层 (Data Layer)
- MySQL：结构化数据存储（用户、设备、告警记录）
- Redis：缓存、会话、实时数据、消息队列
- Milvus：向量存储，用于语义搜索和 RAG

### 智能层 (AI Agent)
- 意图识别：多模态输入分类和路由
- 专业 Agent：睡眠分析、聊天分析、行为分析
- 知识库：基于向量检索的领域知识增强

---

# 3. 技术栈选型

## 3.1 后端技术栈

### API 框架：FastAPI

**选型理由：**
1. **高性能**：基于 Starlette 和 Pydantic，性能媲美 Node.js 和 Go
2. **自动文档**：自动生成 OpenAPI Schema 和 Swagger UI，降低前后端沟通成本
3. **异步支持**：原生 async/await，适合 I/O 密集型场景（如数据库查询、API 调用）
4. **数据验证**：基于 Pydantic 的类型系统，自动请求验证和序列化
5. **依赖注入**：内置依赖注入系统，便于模块化和测试

**备选方案对比：**
- Flask：轻量但缺少现代特性，性能一般
- Django：功能全面但过于重量级，学习曲线陡峭
- Tornado：异步但 API 设计老旧

**版本建议：** `fastapi>=0.100.0`（Poetry: `poetry add fastapi`）

---

### ORM 框架：Peewee

**选型理由：**
1. **轻量简洁**：代码量少，学习成本低，适合中小型项目
2. **Pythonic**：API 设计符合 Python 习惯，开发效率高
3. **多数据库支持**：MySQL、PostgreSQL、SQLite 无缝切换
4. **迁移工具**：配合 peewee_migrate 可实现数据库版本管理

**备选方案对比：**
- SQLAlchemy：功能强大但过于复杂，学习曲线陡峭
- Tortoise ORM：异步 ORM 但生态不成熟
- Django ORM：耦合度高，不适合独立使用

**版本建议：** `peewee>=3.16.0`（Poetry: `poetry add peewee pymysql`）

---

### 关系型数据库：MySQL 8.0

**选型理由：**
1. **成熟稳定**：经过数十年验证，社区活跃，文档丰富
2. **阿里云支持**：RDS MySQL 提供高可用、备份、监控等企业级功能
3. **JSON 支持**：8.0 版本增强 JSON 字段支持，可存储半结构化数据
4. **成本可控**：相比 PostgreSQL，运维成本更低

**表设计规范：**
- 字符集：`utf8mb4`（支持 emoji 和多语言）
- 存储引擎：InnoDB（支持事务和外键）
- 时间字段：统一使用 `DATETIME` 或 `TIMESTAMP`
- 软删除：所有业务表添加 `is_deleted` 和 `deleted_at` 字段

---

### 缓存与消息队列：Redis 7.0

**双角色应用：**

**1. 缓存层**
- 用户会话：JWT Token 黑名单、登录状态
- 热点数据：设备最新状态、配置信息
- 计数器：告警次数、访问统计

**2. 消息队列（Redis Queue）**
- 异步任务：邮件发送、报表生成
- 事件驱动：传感器数据入库、告警推送
- 削峰填谷：高并发数据写入缓冲

**数据结构选型：**
- String：缓存、计数器
- Hash：对象存储（如设备信息）
- List：简单队列
- Pub/Sub：实时消息推送
- Stream：复杂消息队列（可选，用于事件溯源）

**备选方案对比：**
- RabbitMQ：功能强大但运维复杂
- Kafka：适合大数据场景，过度设计
- Celery：重量级，依赖 Broker

**版本建议：** `redis-py>=5.0.0`（Poetry: `poetry add redis`）

---

### 向量数据库：Milvus 2.3 

**选型理由：**
1. **专为 AI 设计**：支持稠密向量、稀疏向量、多模态向量
2. **高性能检索**：亿级向量库毫秒级返回，支持多种索引（IVF、HNSW）
3. **云原生**：支持 Kubernetes 部署，弹性扩缩容
4. **生态完善**：LangChain、LlamaIndex 原生集成
5. **阿里云支持**：阿里云托管版 Milvus，降低运维成本

**应用场景：**
- 语义搜索：聊天记录的语义检索
- RAG 增强：知识库检索增强生成
- 相似度推荐：相似睡眠模式匹配

**备选方案对比：**
- Pinecone：SaaS 服务，国内访问慢
- Weaviate：功能类似但社区较小
- FAISS：Facebook 开源库，需自行封装

**版本建议：** `pymilvus>=2.3.0`（Poetry: `poetry add pymilvus`）

---

## 3.2 AI Agent 技术栈

### AI 编排框架：LangGraph 

**选型理由：**
1. **图结构编排**：基于状态机的图结构，适合复杂的多 Agent 协作场景
2. **循环与分支**：支持条件分支、循环、并行执行，超越 LangChain 的线性链式调用
3. **持久化**：内置 Checkpoint 机制，支持长对话记忆和断点续传
4. **可观测性**：完整的 Trace 日志，便于调试和监控
5. **LangChain 生态**：兼容 LangChain 的 Tool、Memory、Retriever 组件

**核心概念：**
- State：全局状态对象，贯穿整个 Graph
- Node：处理节点，执行具体任务（如意图识别、工具调用）
- Edge：条件边，决定下一个节点
- Checkpointer：状态持久化，支持对话历史存储

**典型工作流：**
```
用户输入 → 意图识别 → [路由] → 睡眠分析 Agent / 聊天分析 Agent / 紧急告警
                              ↓
                         结果汇总 → 响应生成 → 数据库存储
```

**备选方案对比：**
- LangChain：线性链条，不支持复杂循环和状态管理
- AutoGen：微软出品，侧重多 Agent 对话，控制粒度粗
- Haystack：专注问答系统，灵活性不足

**版本建议：** `langgraph>=0.1.0`（Poetry: `poetry add langgraph langchain-core`）

---

### 大语言模型：阿里百炼

**推荐模型矩阵：**

| 场景 | 模型 | 理由 |
|------|------|------|
| 意图识别 | Qwen-Max | 高精度分类，低延迟 |
| 文本分析 | Qwen-Plus | 平衡性能和成本 |
| 复杂推理 | Qwen-Max | 强逻辑推理能力 |
| 长文本 | Qwen-Long | 支持 10M+ 上下文 |

**选型理由：**
1. **国产优势**：数据不出境，符合隐私保护法规
2. **阿里云集成**：与 ECS、RDS、VPC 无缝集成，网络延迟低
3. **性价比高**：相比 GPT-4，价格低 50% 以上
4. **中文优化**：对中文语境、养老领域术语理解更好
5. **企业级 SLA**：99.9% 可用性保证

**接入方式：**
- DashScope SDK：官方 Python SDK
- OpenAI 兼容接口：通过适配层复用 LangChain 组件

**备选方案对比：**
- 百度文心一言：生态封闭
- 腾讯混元：开放度不足
- GPT-4：数据出境风险，网络不稳定

---

### 向量嵌入模型：Text Embedding v2

**选型理由：**
1. **阿里云官方**：与百炼平台深度集成
2. **中文优化**：针对中文语义优化的 embedding 模型
3. **维度灵活**：支持 768/1024/1536 维，适配 Milvus
4. **成本低廉**：按量付费，远低于自建模型

---

## 3.3 前端技术栈

### Web 框架：Next.js 14

**选型理由：**
1. **服务端渲染（SSR）**：首屏加载快，SEO 友好（适用于公开页面）
2. **静态站点生成（SSG）**：管理后台等动态要求低的页面可预渲染
3. **API Routes**：后端 For Frontend（BFF）模式，聚合后端 API
4. **路由系统**：基于文件系统的路由，约定优于配置
5. **React Server Components**：减少客户端 bundle 体积
6. **TypeScript 支持**：一流的类型系统支持

**项目结构建议：**
```
app/
├── (dashboard)/          # 监控后台
│   ├── devices/         # 设备管理
│   ├── alerts/          # 告警中心
│   └── reports/         # 数据报表
├── (mobile)/            # 移动端 H5
│   └── family/          # 家属端
├── api/                 # BFF 层 API
└── components/          # 公共组件
```

**备选方案对比：**
- Create React App：纯客户端渲染，SEO 差，首屏慢
- Nuxt.js：Vue 生态，团队技术栈偏好 React
- Vite + React：需自行配置 SSR

**版本建议：** `nextjs>=14.0.0`（npm: `npm install next@14`）

---

### UI 框架：React 18 + Ant Design 5

**React 18 特性利用：**
- Concurrent Rendering：提升复杂 dashboard 的交互流畅度
- Suspense：组件级懒加载
- Automatic Batching：性能优化

**Ant Design 5 优势：**
1. **企业级组件**：Table、Form、Modal 等组件成熟稳定
2. **主题定制**：CSS-in-JS方案，支持动态主题
3. **国际化**：内置多语言支持
4. **无障碍**：符合 WCAG 标准

**图表库：Ant Charts / ECharts**
- 睡眠趋势图：折线图 + 热力图
- 告警统计：柱状图 + 饼图
- 设备分布：地图可视化

---

### 状态管理：Zustand

**选型理由：**
1. **轻量简洁**：相比 Redux 减少 80% 样板代码
2. **无 Provider**：直接 import useStore，避免组件树嵌套
3. **中间件支持**：persist（本地存储）、immer（不可变更新）
4. **TypeScript 友好**：完整的类型推导

**使用场景：**
- 用户登录状态
- 全局主题配置
- 实时告警通知

---

### 实时通信：WebSocket / Socket.IO

**选型理由：**
1. **实时推送**：紧急告警秒级推送到前端
2. **双向通信**：支持前端指令下发（如设备控制）
3. **自动重连**：网络异常自动恢复

**实现方案：**
- 后端：FastAPI WebSocket / Socket.IO
- 前端：Socket.IO Client / React Query + WebSocket

---

## 3.4 基础设施

### 部署平台：阿里云

**推荐产品组合：**
- ECS：应用服务器（Backend + Agent）
- RDS MySQL：托管数据库
- Redis 版：托管缓存
- 容器服务 ACK：Kubernetes 部署（可选）
- OSS：文件存储（日志、备份）
- SLB：负载均衡
- VPC：网络隔离

### 容器化：Docker + Docker Compose

**优势：**
- 环境一致性：开发、测试、生产环境统一
- 快速部署：一键启动所有服务
- 服务编排：依赖关系管理

### CI/CD：GitHub Actions / 阿里云云效

**流水线设计：**
1. 代码检查（Lint + Type Check）
2. 单元测试
3. 构建镜像
4. 部署到测试环境
5. 人工审核后部署生产

---

# 4. 数据库设计

## 4.1 用户数据表

### users（用户基础信息表）
```sql
CREATE TABLE `users` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户 ID',
  `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
  `phone` VARCHAR(20) COMMENT '手机号',
  `email` VARCHAR(100) COMMENT '邮箱',
  `role` ENUM('admin', 'monitor', 'family') NOT NULL DEFAULT 'family' COMMENT '角色',
  `avatar_url` VARCHAR(255) COMMENT '头像 URL',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` TINYINT NOT NULL DEFAULT 0,
  INDEX idx_phone (`phone`),
  INDEX idx_role (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户基础信息表';
```

### elderly_users（老人信息表）
```sql
CREATE TABLE `elderly_users` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `user_id` BIGINT NOT NULL COMMENT '关联 users.id',
  `name` VARCHAR(50) NOT NULL COMMENT '姓名',
  `gender` ENUM('male', 'female') COMMENT '性别',
  `age` INT COMMENT '年龄',
  `id_card` VARCHAR(18) COMMENT '身份证号（加密存储）',
  `health_conditions` TEXT COMMENT '健康状况（JSON 格式）',
  `emergency_contact` VARCHAR(50) COMMENT '紧急联系人',
  `emergency_phone` VARCHAR(20) COMMENT '紧急联系电话',
  `address` VARCHAR(255) COMMENT '居住地址',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` TINYINT NOT NULL DEFAULT 0,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`),
  INDEX idx_user_id (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='老人信息表';
```

### devices（设备信息表）
```sql
CREATE TABLE `devices` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `device_sn` VARCHAR(50) NOT NULL UNIQUE COMMENT '设备序列号',
  `device_type` ENUM('smoke', 'gas', 'fall', 'sleep', 'chat') NOT NULL COMMENT '设备类型',
  `device_name` VARCHAR(100) COMMENT '设备名称',
  `elderly_user_id` BIGINT COMMENT '关联老人 ID',
  `install_location` VARCHAR(255) COMMENT '安装位置',
  `status` ENUM('online', 'offline', 'fault') NOT NULL DEFAULT 'offline',
  `last_heartbeat` DATETIME COMMENT '最后心跳时间',
  `firmware_version` VARCHAR(20) COMMENT '固件版本',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` TINYINT NOT NULL DEFAULT 0,
  FOREIGN KEY (`elderly_user_id`) REFERENCES `elderly_users`(`id`),
  INDEX idx_device_type (`device_type`),
  INDEX idx_status (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备信息表';
```

---

## 4.2 睡眠数据

### sleep_records（睡眠记录表）
```sql
CREATE TABLE `sleep_records` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `elderly_user_id` BIGINT NOT NULL,
  `device_id` BIGINT NOT NULL,
  `start_time` DATETIME NOT NULL COMMENT '入睡时间',
  `end_time` DATETIME NOT NULL COMMENT '醒来时间',
  `total_duration` INT COMMENT '总睡眠时长（分钟）',
  `deep_sleep_duration` INT COMMENT '深睡时长（分钟）',
  `light_sleep_duration` INT COMMENT '浅睡时长（分钟）',
  `wake_up_count` INT COMMENT '醒来次数',
  `sleep_score` INT COMMENT '睡眠评分（0-100）',
  `raw_data` JSON COMMENT '原始数据（JSON 格式）',
  `analysis_result` TEXT COMMENT 'AI 分析结果',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_time (`elderly_user_id`, `start_time`),
  INDEX idx_date (`start_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='睡眠记录表';
```

### sleep_analysis_logs（睡眠分析日志表）
```sql
CREATE TABLE `sleep_analysis_logs` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `sleep_record_id` BIGINT NOT NULL,
  `agent_type` VARCHAR(50) NOT NULL COMMENT 'Agent 类型',
  `input_data` TEXT COMMENT '输入数据',
  `output_data` TEXT COMMENT '输出数据',
  `tokens_used` INT COMMENT '消耗 Token 数',
  `latency_ms` INT COMMENT '耗时（毫秒）',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_record_id (`sleep_record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='睡眠分析日志表';
```

---

## 4.3 聊天数据

### chat_sessions（聊天会话表）
```sql
CREATE TABLE `chat_sessions` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `elderly_user_id` BIGINT NOT NULL,
  `session_id` VARCHAR(64) NOT NULL UNIQUE COMMENT '会话 ID（UUID）',
  `title` VARCHAR(255) COMMENT '会话标题',
  `start_time` DATETIME NOT NULL,
  `end_time` DATETIME,
  `message_count` INT DEFAULT 0,
  `mood_score` INT COMMENT '情绪评分（0-100）',
  `topic_tags` JSON COMMENT '话题标签',
  `risk_level` ENUM('normal', 'warning', 'high') DEFAULT 'normal',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_session (`elderly_user_id`, `session_id`),
  INDEX idx_start_time (`start_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='聊天会话表';
```

### chat_messages（聊天消息表）
```sql
CREATE TABLE `chat_messages` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `session_id` BIGINT NOT NULL,
  `message_id` VARCHAR(64) NOT NULL UNIQUE,
  `role` ENUM('user', 'assistant') NOT NULL,
  `content` TEXT NOT NULL,
  `emotion` VARCHAR(50) COMMENT '情绪识别结果',
  `intent` VARCHAR(100) COMMENT '意图识别结果',
  `vector_id` VARCHAR(64) COMMENT 'Milvus 中的向量 ID',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_session (`session_id`),
  INDEX idx_created (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='聊天消息表';
```

### chat_analysis_results（聊天分析结果表）
```sql
CREATE TABLE `chat_analysis_results` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `session_id` BIGINT NOT NULL,
  `analysis_type` ENUM('emotion', 'cognitive', 'topic', 'risk') NOT NULL,
  `analysis_data` JSON NOT NULL,
  `summary` TEXT,
  `recommendations` TEXT COMMENT '建议措施',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_session_type (`session_id`, `analysis_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='聊天分析结果表';
```

---

## 4.4 告警数据

### alerts（告警记录表）
```sql
CREATE TABLE `alerts` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `alert_type` ENUM('smoke', 'gas', 'fall', 'health', 'behavior') NOT NULL,
  `level` ENUM('critical', 'warning', 'info') NOT NULL,
  `elderly_user_id` BIGINT NOT NULL,
  `device_id` BIGINT,
  `title` VARCHAR(255) NOT NULL,
  `content` TEXT NOT NULL,
  `raw_data` JSON COMMENT '触发告警的原始数据',
  `status` ENUM('pending', 'processing', 'resolved', 'ignored') NOT NULL DEFAULT 'pending',
  `assigned_to` BIGINT COMMENT '分配给的处理人 ID',
  `handled_at` DATETIME COMMENT '处理时间',
  `handled_result` TEXT COMMENT '处理结果',
  `pushed` TINYINT DEFAULT 0 COMMENT '是否已推送',
  `pushed_at` DATETIME COMMENT '推送时间',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_status (`elderly_user_id`, `status`),
  INDEX idx_level_created (`level`, `created_at`),
  INDEX idx_pushed (`pushed`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警记录表';
```

### alert_push_logs（告警推送日志表）
```sql
CREATE TABLE `alert_push_logs` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `alert_id` BIGINT NOT NULL,
  `user_id` BIGINT NOT NULL,
  `push_channel` ENUM('websocket', 'sms', 'wechat', 'app') NOT NULL,
  `push_status` ENUM('success', 'failed', 'retrying') NOT NULL,
  `error_message` TEXT,
  `retry_count` INT DEFAULT 0,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_alert (`alert_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警推送日志表';
```

---

## 4.5 Agent 相关表

### agent_tasks（Agent 任务表）
```sql
CREATE TABLE `agent_tasks` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `task_id` VARCHAR(64) NOT NULL UNIQUE,
  `task_type` VARCHAR(50) NOT NULL COMMENT '任务类型',
  `input_data` JSON NOT NULL,
  `output_data` JSON,
  `status` ENUM('pending', 'running', 'completed', 'failed') NOT NULL DEFAULT 'pending',
  `error_message` TEXT,
  `tokens_used` INT,
  `latency_ms` INT,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `started_at` DATETIME,
  `completed_at` DATETIME,
  INDEX idx_task_type (`task_type`),
  INDEX idx_status (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent 任务表';
```

### agent_knowledge_base（Agent 知识库表）
```sql
CREATE TABLE `agent_knowledge_base` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `category` VARCHAR(50) NOT NULL COMMENT '知识分类',
  `title` VARCHAR(255) NOT NULL,
  `content` TEXT NOT NULL,
  `vector_id` VARCHAR(64) COMMENT 'Milvus 向量 ID',
  `embedding_model` VARCHAR(50),
  `metadata` JSON,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_category (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent 知识库表';
```

---

# 5. 系统非功能性需求

## 5.1 性能指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| API 响应时间 | < 200ms | P95 延迟 |
| 告警推送延迟 | < 5s | 从事件发生到前端收到推送 |
| AI 分析延迟 | < 10s | 单次 Agent 调用 |
| 系统可用性 | > 99.9% | 月度 SLA |
| 并发用户数 | > 1000 | 同时在线监控人员 |

## 5.2 安全要求

1. **数据传输加密**：全站 HTTPS，TLS 1.3
2. **敏感数据加密**：身份证号、手机号 AES-256 加密存储
3. **访问控制**：RBAC 权限模型，最小权限原则
4. **审计日志**：所有敏感操作记录审计日志
5. **防 SQL 注入**：ORM 参数化查询，禁止拼接 SQL

## 5.3 可扩展性

1. **微服务拆分**：按业务域拆分为独立服务（设备服务、告警服务、AI 服务）
2. **水平扩展**：无状态服务支持快速扩容
3. **读写分离**：MySQL 主从架构，读多写少场景优化

---

# 6. 开发规范

## 6.1 Poetry 依赖管理

### 安装 Poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 初始化项目
```bash
cd backend
poetry init  # 交互式创建 pyproject.toml
```

### 添加依赖
```bash
# 生产依赖
poetry add fastapi uvicorn peewee pymysql redis pymilvus langgraph

# 开发依赖
poetry add --group dev pytest black mypy ruff
```

### 激活虚拟环境
```bash
poetry shell  # 进入虚拟环境
# 或者
poetry run python app/main.py  # 直接运行命令
```

### 导出 requirements.txt（可选，用于部署）
```bash
poetry export -f requirements.txt --output requirements.txt
```

---

## 6.3 代码规范

- Python: PEP 8 + Black 格式化
- TypeScript: ESLint + Prettier
- Git Commit: Conventional Commits 规范

---

## 6.4 pyproject.toml 配置示例

```
[tool.poetry]
name = "xiaohui-backend"
version = "0.1.0"
description = "AI 养老监护平台 - 后端服务"
authors = ["Your Team"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.10"
# API 框架
fastapi = ">=0.100.0"
uvicorn = {extras = ["standard"], version = ">=0.23.0"}

# 数据库
peewee = ">=3.16.0"
pymysql = ">=1.1.0"
redis = ">=5.0.0"

# 向量数据库
pymilvus = ">=2.3.0"

# AI 框架（遵循非必要不引入依赖原则）
langgraph = ">=0.1.0"
langchain-core = ">=0.1.0"  # 仅提供基础类型定义

# 数据验证
pydantic = ">=2.0.0"
pydantic-settings = ">=2.0.0"

# HTTP 客户端
httpx = ">=0.25.0"

# 工具库
python-dotenv = ">=1.0.0"
structlog = ">=23.0.0"  # 结构化日志

[tool.poetry.group.dev.dependencies]
pytest = ">=7.4.0"
pytest-cov = ">=4.1.0"
black = ">=23.0.0"
mypy = ">=1.5.0"
ruff = ">=0.0.290"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 88
target-version = ['py310']

[tool.ruff]
line-length = 88
select = ["E", "F", "I"]

[tool.mypy]
python_version = "3.10"
strict = true