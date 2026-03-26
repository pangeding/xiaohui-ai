# 小辉 AI 后端服务

基于 FastAPI + Peewee + MySQL 构建的后端 API 服务。

## 技术栈

- **FastAPI**: 现代高性能 Web 框架
- **Peewee**: 轻量级 Python ORM
- **MySQL**: 关系型数据库
- **Pydantic**: 数据验证和序列化
- **uv**: 下一代 Python 包管理工具 🚀

## 项目结构

```
backend/
├── api/                    # API 层
│   ├── __init__.py
│   ├── routes.py          # API 路由定义
│   └── schemas.py         # Pydantic 模型（请求/响应）
├── db/                     # 数据库层
│   ├── __init__.py        # 数据库配置
│   └── models.py          # Peewee 模型定义
├── service/                # 服务层
│   ├── __init__.py
│   └── device_health_report.py  # 业务逻辑
├── doc/                    # 文档
│   └── DATA_MODEL.md      # 数据模型设计
├── pyproject.toml         # 项目配置 (uv)
├── .env.example           # 环境配置示例
├── main.py                # FastAPI 应用入口
└── README.md              # 项目说明
```

## 快速开始

### 前置要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (推荐使用 uv 进行包管理)

安装 uv：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 1. 安装依赖

使用 uv 安装项目依赖：

```bash
make install
# 或者手动安装：
uv pip install -e .
```

安装开发依赖（可选）：

```bash
make install-dev
# 或者：
uv pip install -e ".[dev]"
```

### 2. 配置环境变量

复制环境配置示例文件并修改：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的数据库配置：

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=xiaohui_ai
```

### 3. 创建数据库

在 MySQL 中创建数据库：

```sql
CREATE DATABASE xiaohui_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 启动服务

开发模式（自动重载）：

```bash
make dev
# 或手动启动：
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

生产模式：

```bash
make run
# 或手动启动：
python main.py
```

### 5. 访问 API 文档

启动后访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 设备健康报告 (`/api/v1/device-health-reports`)

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/` | 创建报告 |
| GET | `/{report_id}` | 根据 ID 获取报告 |
| GET | `/biz/{device_health_report_id}` | 根据业务 ID 获取报告 |
| GET | `/device/{device_id}` | 根据设备 ID 获取列表 |
| GET | `/customer/{customer_id}` | 根据客户 ID 获取列表 |
| GET | `/date-range` | 根据日期范围查询 |
| PUT | `/{report_id}` | 更新报告 |
| DELETE | `/{report_id}` | 删除报告（软删除） |
| DELETE | `/{report_id}/hard` | 物理删除报告 |
| GET | `` (空) | 分页获取报告列表 |

## 使用示例

### 创建设备健康报告

```bash
curl -X POST "http://localhost:8000/api/v1/device-health-reports" \
  -H "Content-Type: application/json" \
  -d '{
    "device_health_report_id": 12345,
    "device_id": 1001,
    "customer_id": 2001,
    "business_id": 3001,
    "report_id": "RPT20240101001",
    "health_report": {"sleep_score": 85, "duration": 7.5},
    "report_type": 1,
    "report_date": "2024-01-01",
    "report_status": "INIT"
  }'
```

### 获取报告详情

```bash
curl "http://localhost:8000/api/v1/device-health-reports/1"
```

### 分页查询报告列表

```bash
curl "http://localhost:8000/api/v1/device-health-reports?page=1&page_size=10&device_id=1001"
```

## 开发命令

使用 Makefile 提供的快捷命令：

```bash
# 安装依赖
make install

# 安装开发依赖
make install-dev

# 启动开发服务器
make dev

# 运行测试
make test

# 代码检查
make lint

# 自动修复代码问题
make lint-fix

# 类型检查
make type-check

# 清理缓存
make clean
```

## 开发说明

### 添加新的数据模型

1. 在 `db/models.py` 中定义 Peewee 模型
2. 在 `service/` 目录下创建对应的服务类
3. 在 `api/schemas.py` 中定义 Pydantic 模型
4. 在 `api/routes.py` 中添加 API 路由

### 代码质量

项目配置了以下工具保证代码质量：

- **Ruff**: 快速的 Python 代码检查工具
- **Mypy**: Python 类型检查工具
- **Pytest**: 测试框架

运行检查：

```bash
make lint        # 代码检查
make type-check  # 类型检查
make pytest      # 运行测试
```

### 数据库迁移

目前表结构会在应用启动时自动创建。生产环境建议使用迁移工具如 [Peewee Migrate](https://github.com/pawamoy/peewee-migrate)。

## 注意事项

- 默认启用 CORS（允许所有来源），生产环境请配置具体域名
- 软删除通过设置 `delete_flag=1` 实现
- 时间字段使用 `datetime` 类型，会自动转换为 ISO 格式字符串
- 使用 uv 管理依赖，更快的安装速度和更好的依赖锁定

## 许可证

MIT License
