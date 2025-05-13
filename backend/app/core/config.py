import os
from typing import List, Optional, Union
from pydantic import BaseSettings, AnyHttpUrl, validator


class Settings(BaseSettings):
    API_VERSION: str = "1.0.0"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

    # Database settings
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "gtinging")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "dsp_ad_system")
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"mysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"
    
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ECHO: bool = DEBUG

    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev_jwt_key")
    JWT_ACCESS_TOKEN_EXPIRES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 86400))
    JWT_TOKEN_LOCATION: List[str] = ["headers"]
    JWT_HEADER_NAME: str = "Authorization"
    JWT_HEADER_TYPE: str = "Bearer"
    JWT_ERROR_MESSAGE_KEY: str = "error"
    JWT_ACCESS_CSRF_HEADER_NAME: str = "X-CSRF-Token"
    JWT_CSRF_CHECK_FORM: bool = True
    JWT_CSRF_IN_COOKIES: bool = True
    JWT_CSRF_METHODS: List[str] = ["POST", "PUT", "PATCH", "DELETE"]
    JWT_JSON_KEY: str = "access_token"
    JWT_IDENTITY_CLAIM: str = "sub"

    # Security
    AES_SECRET_KEY: str = os.getenv("AES_SECRET_KEY", "dev_aes_key_16_bytes!")
    CSRF_SECRET_KEY: str = os.getenv("CSRF_SECRET_KEY", "dev_csrf_key")

    # CORS Settings
    CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Redis Settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_CACHE_URL: str = os.getenv("REDIS_CACHE_URL", "redis://localhost:6379/1")

    # Celery Settings
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/2")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

    # API Rate Limiting
    RATE_LIMIT_DEFAULT: str = "100/hour"

    # File Upload Settings
    UPLOAD_FOLDER: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "png", "jpg", "jpeg"]

    # Neo4j Settings
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "neo4j")

    # Email Settings
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS: bool = os.getenv("MAIL_USE_TLS", "True").lower() in ("true", "1", "t")
    MAIL_USE_SSL: bool = os.getenv("MAIL_USE_SSL", "False").lower() in ("true", "1", "t")
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER: str = os.getenv("MAIL_DEFAULT_SENDER", "noreply@yourdsp.com")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:8080")

    # Aliyun Content Security API
    ALIYUN_CONTENT_SECURITY_KEY: Optional[str] = os.getenv("ALIYUN_CONTENT_SECURITY_KEY")
    ALIYUN_CONTENT_SECURITY_SECRET: Optional[str] = os.getenv("ALIYUN_CONTENT_SECURITY_SECRET")

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
