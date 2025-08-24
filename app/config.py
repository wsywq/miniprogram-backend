from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "mysql+pymysql://root:password@localhost:3306/habit_tracker"
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT Configuration
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # WeChat Configuration
    wechat_app_id: str = ""
    wechat_app_secret: str = ""
    
    # File Upload Configuration
    upload_dir: str = "uploads"
    max_file_size: int = 5242880  # 5MB
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings()
