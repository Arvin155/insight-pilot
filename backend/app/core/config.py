import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # 应用配置
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", 8000))

    # MYSQL配置
    mysql_user: str = os.getenv("MYSQL_USER")
    mysql_password: str = os.getenv("MYSQL_PASSWORD")
    mysql_host: str = os.getenv("MYSQL_HOST")
    mysql_port: int = os.getenv("MYSQL_PORT")
    mysql_db: str = os.getenv("MYSQL_DB")

    # JWT 配置
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM")
    access_token_expire_minutes: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")

    # 文件存储配置
    log_file_path: str = os.getenv("LOG_FILE_PATH")
    knowledge_file_path: str = os.getenv("KNOWLEDGE_FILE_PATH")

    # llama_index 元数据配置
    metadata_exclude_fields: str = os.getenv("METADATA_EXCLUDE_FIELDS")

    # LLM 配置
    dashscope_api_key: str = os.getenv("DASHSCOPE_API_KEY")
    llm_base_url: str = os.getenv("LLM_BASE_URL")
    chat_model: str = os.getenv("CHAT_MODEL", "qwen-plus")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-v2")
    rerank_model: str = os.getenv("RERANK_MODEL", "get-rerank-v2")

    # 向量数据库配置
    vector_file_path: str = os.getenv("VECTOR_FILE_PATH")
    # chroma
    chroma_file_path: str = os.getenv("CHROMA_FILE_PATH")
    # milvus
    milvus_client: str = os.getenv("MILVUS_CLIENT")
    milvus_user: str = os.getenv("MILVUS_USER")
    milvus_password: str = os.getenv("MILVUS_PASSWORD")

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
            "?charset=utf8mb4"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


# 创建全局配置实例
settings = get_settings()
