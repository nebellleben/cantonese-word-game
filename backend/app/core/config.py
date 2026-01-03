from typing import List
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    api_v1_prefix: str = "/api"
    project_name: str = "Cantonese Word Game API"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    
    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Database
    database_url: str = "sqlite:///./cantonese_game.db"
    # For PostgreSQL, use: postgresql://user:password@localhost/dbname
    # For SQLite (default), use: sqlite:///./cantonese_game.db
    
    model_config = ConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()

