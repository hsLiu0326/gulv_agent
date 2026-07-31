"""应用配置模块"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


def load_env_file(env_path=None):
    if env_path is None:
        # \u4f18\u5148\u4f7f\u7528 backend/.env\uff08\u76f8\u5bf9\u4e8e\u672c\u9879\u76ee\uff09
        env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        env_path = os.path.abspath(env_path)
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.replace("\u200b", "").strip()
                        os.environ[key] = value


load_env_file()


class Settings(BaseSettings):
    """应用配置类"""
    APP_NAME: str = "AI营养师Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/ai_nutritionist"

    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    OPENAI_API_KEY: str = "sk-your-openai-api-key"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

    CHROMA_PERSIST_DIR: str = "./chroma_data"

    # 知识库向量化提供方：ollama（本地语义向量，推荐）/ hash（纯本地兜底，无模型依赖）
    EMBEDDING_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_EMBED_MODEL: str = "qwen-emb:latest"

    # CORS 允许的域名，逗号分隔
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # 分页默认值
    PAGE_SIZE_DEFAULT: int = 20
    PAGE_SIZE_MAX: int = 100


settings = Settings()
