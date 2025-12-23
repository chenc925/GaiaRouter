"""
GaiaRouter 应用入口

FastAPI应用主文件
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from .config import get_settings
from .utils.logger import setup_logger, get_logger
from .api.middleware.logging import LoggingMiddleware
from .api.middleware.error import error_handler
from .api.controllers import chat, models, stats, api_keys, organizations, auth, admin_models

# 初始化日志
setup_logger()
logger = get_logger(__name__)

# 获取配置
settings = get_settings()

# 创建FastAPI应用
app = FastAPI(
    title="GaiaRouter API",
    description="AI模型路由服务，提供统一的API接口访问多个AI模型",
    version="0.1.0",
    debug=settings.server.debug,
)

# 配置CORS
# 注意：allow_origins=["*"] 和 allow_credentials=True 不能同时使用
# 开发环境：允许前端来源
cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite 默认端口
    "http://127.0.0.1:5173",
]

logger.info(f"CORS configured with origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 添加日志中间件
app.add_middleware(LoggingMiddleware)

# 注册全局异常处理器
app.add_exception_handler(Exception, error_handler)
app.add_exception_handler(RequestValidationError, error_handler)
app.add_exception_handler(HTTPException, error_handler)

# 注册路由
app.include_router(chat.router)
app.include_router(models.router)
app.include_router(stats.router)
app.include_router(api_keys.router)
app.include_router(organizations.router)
app.include_router(auth.router)  # 管理后台认证路由
app.include_router(admin_models.router)  # 模型管理路由


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("Starting GaiaRouter application")

    # 初始化数据库
    from .database import init_db

    init_db()

    logger.info("GaiaRouter application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("Shutting down GaiaRouter application")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """根路径"""
    return {"name": "GaiaRouter API", "version": "0.1.0", "status": "running"}
