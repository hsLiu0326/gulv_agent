"""FastAPI主应用"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, users, health_reports, recipes, daily_menus, preferences, knowledge_base
from knowledge_base import init_knowledge_base


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI营养师Agent - 智能个性化营养饮食管理系统"
)

# CORS 从配置读取，支持生产环境自定义
cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === 统一异常处理 ===

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """统一 HTTP 异常响应格式"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """统一参数校验错误响应"""
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err["loc"] if loc != "body")
        errors.append(f"{field}: {err['msg']}")
    return JSONResponse(
        status_code=422,
        content={"detail": "参数校验失败", "errors": errors},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """兜底异常处理，避免暴露内部细节"""
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请稍后重试"},
    )


# === 初始化 ===

Base.metadata.create_all(bind=engine)

init_knowledge_base()

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(health_reports.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(daily_menus.router, prefix="/api")
app.include_router(preferences.router, prefix="/api")
app.include_router(knowledge_base.router, prefix="/api")


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
