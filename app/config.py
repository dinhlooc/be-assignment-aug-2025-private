from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field, validator

class Settings(BaseSettings):
    # Database
    database_url: str = Field(..., env="database_url")
    
    # Redis Configuration
    redis_host: str = Field(default="redis", env="redis_host")
    redis_port: int = Field(default=6379, env="redis_port")
    redis_db: int = Field(default=0, env="redis_db")
    redis_password: Optional[str] = Field(default=None, env="redis_password")
    notification_ttl: int = Field(default=2592002, env="notification_ttl")
    task_cache_expiration: int = Field(default=300, env="task_cache_expiration")  # 5 minutes
    report_cache_ttl: int = Field(default=3600, env="report_cache_ttl")  # 1 hour

    # JWT
    secret_key: str = Field(..., env="secret_key")
    algorithm: str = Field(default="HS256", env="algorithm")
    access_token_expire_days: int = Field(default=7, env="access_token_expire_days")
    refresh_token_expire_days: int = Field(default=30, env="refresh_token_expire_days")

    # Application
    debug: bool = Field(default=True, env="debug")
    log_level: str = Field(default="INFO", env="log_level")
    
    # File Upload
    allowed_extensions: str = Field(default="pdf,docx,xlsx,png,jpg,jpeg,zip", env="allowed_extensions")
    max_file_size: int = Field(default=5242880, env="max_file_size")  # 5MB
    max_files_per_task: int = Field(default=3, env="max_files_per_task")
    upload_dir: str = Field(default="uploads", env="upload_dir")
    
    # Thêm validation
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long and not empty')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'log_level must be one of {valid_levels}')
        return v.upper()
    
    @validator('max_file_size')
    def validate_file_size(cls, v):
        if v <= 0:
            raise ValueError('max_file_size must be positive')
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings()



