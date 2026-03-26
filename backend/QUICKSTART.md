# 快速开始指南

本指南将帮助你在 5 分钟内启动项目。

## 📋 前置要求

- Python 3.10+
- MySQL 5.7+ 或 MariaDB 10.3+
- uv (推荐) 或 pip

## 🚀 安装步骤

### 1. 安装 uv（如果尚未安装）

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 克隆项目并进入目录

```bash
cd backend
```

### 3. 安装依赖

```bash
# 使用 Makefile（推荐）
make install

# 或者手动安装
uv pip install -e .
```

### 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=xiaohui_ai
```

### 5. 创建数据库

```bash
mysql -u root -p -e "CREATE DATABASE xiaohui_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 6. 启动服务

```bash
# 开发模式（自动重载）
make dev

# 或生产模式
make run
```

服务将在 http://localhost:8000 启动

### 7. 验证安装

访问 API 文档：http://localhost:8000/docs

或运行健康检查：

```bash
curl http://localhost:8000/health
```

## 🧪 运行测试

```bash
# 安装开发依赖（首次运行需要）
make install-dev

# 运行 CRUD 功能测试
make test

# 或使用 pytest
make pytest
```

## 🛠️ 常用命令

```bash
# 代码检查
make lint          # Ruff 代码检查
make lint-fix      # 自动修复问题
make type-check    # Mypy 类型检查

# 清理缓存
make clean

# 查看所有可用命令
make help
```

## ❓ 常见问题

### Q: 无法连接到数据库？
A: 确保 MySQL 服务已启动，并检查 `.env` 文件中的数据库配置是否正确。

### Q: 端口 8000 已被占用？
A: 修改启动命令的端口号：`uvicorn main:app --port 8001`

### Q: 如何查看详细的日志？
A: 在 `.env` 中添加 `DEBUG=True`，或查看应用启动时的日志输出。

## 📚 下一步

- 阅读 [README.md](README.md) 了解完整的项目说明
- 访问 http://localhost:8000/docs 查看 API 文档
- 查看 [test_crud.py](test_crud.py) 了解如何使用 API

祝你使用愉快！🎉
