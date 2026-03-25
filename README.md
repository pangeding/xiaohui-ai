# 小辉 AI 养老监护平台

基于 LangGraph 构建的智能养老监护 Agent 系统

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- uv (依赖管理工具)

### 2. 安装依赖

```bash
# 安装所有依赖
make install

# 或手动安装
cd agents && uv sync --frozen
```

### 3. 配置 API Key

**方式一：使用 .env 文件（推荐）**

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，填入你的 DeepSeek API Key
vi .env
```

**.env 文件内容：**
```env
DEEPSEEK_API_KEY=sk-your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

**方式二：使用环境变量**

```bash
export DEEPSEEK_API_KEY='sk-your-api-key-here'
```

**获取 API Key:** [https://platform.deepseek.com/](https://platform.deepseek.com/)

### 4. 运行 Demo

```bash
# 方式一：使用 Makefile
make run-agent

# 方式二：直接进入 agents 目录
cd agents && make run-demo

# 方式三：直接运行
uv run python agents/demo.py
```

## 📁 项目结构

```
xiaohui-ai/
├── agents/              # Agent 服务
│   ├── clients/        # API 客户端
│   │   └── deepseek.py # DeepSeek 客户端
│   ├── nodes/          # 图节点
│   │   ├── intent.py   # 意图识别
│   │   ├── sleep.py    # 睡眠分析
│   │   └── chat.py     # 聊天分析
│   ├── prompts/        # Prompt 模板
│   ├── config.py       # 配置管理 ⭐
│   ├── graph.py        # Agent 图构建
│   ├── state.py        # 状态定义
│   └── demo.py         # Demo 示例
├── backend/            # 后端服务
├── .env.example        # 配置模板
├── .env                # 实际配置（需自行创建）
└── Makefile           # 构建脚本
```

## ⚙️ 配置说明

### 核心配置项

| 配置项 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | - | ✅ |
| `DEEPSEEK_BASE_URL` | API 基础 URL | `https://api.deepseek.com` | ❌ |
| `DEEPSEEK_MODEL` | 使用的模型 | `deepseek-chat` | ❌ |
| `DEEPSEEK_TEMPERATURE` | 生成温度 | `0.7` | ❌ |
| `DEEPSEEK_MAX_TOKENS` | 最大 token 数 | `1000` | ❌ |
| `DEEPSEEK_TIMEOUT` | 请求超时（秒） | `30.0` | ❌ |

### 配置验证

运行配置测试：

```bash
cd agents
uv run python config.py
```

输出示例：
```
=== 配置信息 ===
DeepSeek 已配置：True
API Key: ✓
Base URL: https://api.deepseek.com
Model: deepseek-chat
Temperature: 0.7
```

## 🔧 开发命令

```bash
make install          # 安装依赖
make install-dev      # 安装开发依赖
make run-agent        # 运行 Agent Demo
make format           # 格式化代码
make lint             # 代码检查
make clean            # 清理缓存
```

## 📝 功能特性

### ✅ 已实现

- **意图识别**: 自动识别用户输入类型（睡眠数据/聊天消息）
- **睡眠分析**: 专业睡眠质量评估和建议
- **聊天分析**: 情绪分析和心理健康评估
- **智能路由**: 根据意图自动选择分析模块
- **配置管理**: 统一的配置管理系统
- **错误处理**: 友好的错误提示和降级策略

### 🚧 计划中

- 多轮对话支持
- 记忆和历史记录
- 健康数据可视化
- 告警和通知系统
- RESTful API 接口

## 🛠️ 技术栈

- **Python 3.10+**: 核心语言
- **LangGraph**: Agent 编排框架
- **Pydantic**: 数据验证和配置管理
- **httpx**: HTTP 客户端
- **uv**: 依赖管理

## 📖 相关文档

- [AGENT-DESIGN.md](./AGENT-DESIGN.md) - Agent 设计文档
- [AGENT-DESIGN-MVP.md](./AGENT-DESIGN-MVP.md) - MVP 版本设计
- [BEGIN.md](./BEGIN.md) - 入门指南

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
