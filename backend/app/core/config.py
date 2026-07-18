"""应用配置模块"""​
from pydantic_settings import BaseSettings​
from typing import Optional​
import os​
​
​
class Settings(BaseSettings):​
    """应用配置类"""​
    # 应用配置​
    APP_NAME: str = "AI营养师Agent"​
    APP_VERSION: str = "1.0.0"​
    DEBUG: bool = True​
    ​
    # 数据库配置​
    DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/ai_nutritionist"​
    ​
    # JWT配置​
    SECRET_KEY: str = "your-secret-key-here-change-in-production"​
    ALGORITHM: str = "HS256"​
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30​
    ​
    # OpenAI配置​
    OPENAI_API_KEY: str = "sk-your-openai-api-key"​
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"​
    ​
    # ChromaDB配置​
    CHROMA_PERSIST_DIR: str = "./chroma_data"​
    ​
    class Config:​
        env_file = ".env"​
        case_sensitive = True​
​
​
settings = Settings()