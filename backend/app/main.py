"""FastAPI主应用"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, users, health_reports, recipes


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI营养师Agent - 智能个性化营养饮食管理系统"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(health_reports.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")


@app.get("/")
def root():
    """根路径"""
    return {
        "message": "欢迎使用AI营养师Agent",
        "version": settings.APP_VERSION
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}