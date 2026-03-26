"""
FastAPI 主应用入口
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db import connect_db, close_db, init_tables
from api.routes import router as device_health_report_router
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

# 定义生命周期事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("正在连接数据库...")
    connect_db()
    print("正在初始化数据表...")
    init_tables()
    print("应用启动成功！")
    
    yield
    
    # 关闭时执行
    print("正在关闭数据库连接...")
    close_db()


# 创建 FastAPI 应用
app = FastAPI(
    title="小汇 AI 后端 API",
    description="基于 FastAPI + Peewee + MySQL 的后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS（跨域资源共享）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该配置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(device_health_report_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用小辉 AI 后端 API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        connect_db()
        close_db()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
