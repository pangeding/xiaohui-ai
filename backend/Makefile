.PHONY: install run dev test clean lint type-check help venv activate

# 默认目标
.DEFAULT_GOAL := help

# 使用 uv 安装依赖（自动创建虚拟环境）
install:
	@echo "正在使用 uv 安装依赖..."
	uv venv || true
	uv pip install -e .
	@echo "✅ 依赖安装完成"
	@echo ""
	@echo "💡 提示：运行以下命令激活虚拟环境："
	@echo "   source .venv/bin/activate  (Linux/Mac)"
	@echo "   .venv\\Scripts\\activate    (Windows)"

# 安装开发依赖
install-dev:
	@echo "正在使用 uv 安装开发依赖..."
	uv venv || true
	uv pip install -e ".[dev]"
	@echo "✅ 开发依赖安装完成"
	@echo ""
	@echo "💡 提示：运行以下命令激活虚拟环境："
	@echo "   source .venv/bin/activate  (Linux/Mac)"
	@echo "   .venv\\Scripts\\activate    (Windows)"

# 创建虚拟环境
venv:
	@echo "正在创建虚拟环境..."
	uv venv
	@echo "✅ 虚拟环境创建成功"
	@echo ""
	@echo "💡 运行以下命令激活虚拟环境："
	@echo "   source .venv/bin/activate  (Linux/Mac)"
	@echo "   .venv\\Scripts\\activate    (Windows)"

# 激活虚拟环境（仅适用于 bash/zsh）
activate:
	@echo "正在激活虚拟环境..."
	source .venv/bin/activate
	@echo "✅ 虚拟环境已激活"

# 启动服务（生产模式）
run:
	@echo "正在启动服务..."
	python main.py

# 启动服务（开发模式，自动重载）
dev:
	@echo "正在启动开发服务器..."
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 运行测试
test:
	@echo "正在运行 CRUD 测试..."
	python test_crud.py

# 运行 pytest 测试
pytest:
	@echo "正在运行 pytest 测试..."
	pytest

# 代码检查 (Ruff)
lint:
	@echo "正在运行代码检查..."
	ruff check .

# 自动修复代码问题
lint-fix:
	@echo "正在自动修复代码问题..."
	ruff check --fix .

# 类型检查 (Mypy)
type-check:
	@echo "正在运行类型检查..."
	mypy .

# 检查代码语法
check:
	@echo "正在检查代码..."
	python -m py_compile main.py
	python -m py_compile db/models.py
	python -m py_compile service/device_health_report.py
	python -m py_compile api/routes.py
	python -m py_compile api/schemas.py
	@echo "✅ 代码检查通过"

# 清理 Python 缓存文件
clean:
	@echo "正在清理缓存文件..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@echo "✅ 清理完成"

# 显示帮助信息
help:
	@echo "小辉 AI 后端服务 - Makefile 命令 (uv 版本)"
	@echo ""
	@echo "可用命令:"
	@echo "  make venv         - 创建虚拟环境"
	@echo "  make install      - 使用 uv 安装依赖（自动创建虚拟环境）"
	@echo "  make install-dev  - 使用 uv 安装开发依赖"
	@echo "  make run          - 启动服务（生产模式）"
	@echo "  make dev          - 启动开发服务器（自动重载）"
	@echo "  make test         - 运行 CRUD 测试"
	@echo "  make pytest       - 运行 pytest 测试"
	@echo "  make lint         - 运行代码检查 (Ruff)"
	@echo "  make lint-fix     - 自动修复代码问题"
	@echo "  make type-check   - 运行类型检查 (Mypy)"
	@echo "  make check        - 检查代码语法"
	@echo "  make clean        - 清理缓存文件"
	@echo "  make help         - 显示帮助信息"
	@echo ""
	@echo "快速开始:"
	@echo "  make venv && make install && source .venv/bin/activate && make dev"
	@echo ""
	@echo "开发流程:"
	@echo "  make venv && make install-dev && source .venv/bin/activate && make lint && make test && make dev"
