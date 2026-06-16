"""
应用配置管理
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pydantic import field_validator


class Settings(BaseSettings):
    """应用配置类"""

    # 应用配置
    APP_NAME: str = "社团统一管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_mode(cls, v):
        if isinstance(v, str):
            normalized = v.strip().lower()
            if normalized in {"release", "prod", "production"}:
                return False
            if normalized in {"debug", "dev", "development"}:
                return True
        return v

    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "club_management"
    DB_ECHO: bool = False

    @field_validator("DB_PASSWORD")
    @classmethod
    def db_password_must_not_be_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("DB_PASSWORD 不能为空，请在 .env 文件中配置数据库密码")
        return v

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    # JWT 配置
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_set(cls, v: str) -> str:
        if not v or v == "your-secret-key-change-in-production":
            raise ValueError(
                "SECRET_KEY 不能为空或使用默认值，请在 .env 中设置一个随机密钥。"
                "可运行: python -c \"import secrets; print(secrets.token_hex(32))\" 生成"
            )
        return v

    # CORS 配置 (从环境变量读取时是逗号分隔的字符串)
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    @property
    def cors_origins_list(self) -> List[str]:
        """将 CORS 配置转为列表"""
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]
        return self.BACKEND_CORS_ORIGINS

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
