from typing import List
import os
import json
from pydantic import ConfigDict, field_validator
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
    
    # AWS Secrets Manager (optional)
    # If AWS_SECRETS_MANAGER_SECRET_NAME is set, secrets will be loaded from AWS
    aws_secrets_manager_secret_name: str | None = None
    aws_region: str = "us-east-1"
    
    model_config = ConfigDict(env_file=".env", case_sensitive=True)
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            try:
                # Try to parse as JSON array
                return json.loads(v)
            except (json.JSONDecodeError, ValueError):
                # If not JSON, split by comma
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load secrets from AWS Secrets Manager if configured
        if self.aws_secrets_manager_secret_name:
            try:
                self._load_aws_secrets()
            except Exception as e:
                # Log warning but don't fail if AWS secrets can't be loaded
                # This allows the app to work without AWS in development
                import warnings
                warnings.warn(f"Could not load AWS secrets: {e}")
    
    def _load_aws_secrets(self):
        """Load secrets from AWS Secrets Manager."""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            client = boto3.client('secretsmanager', region_name=self.aws_region)
            response = client.get_secret_value(SecretId=self.aws_secrets_manager_secret_name)
            secrets = json.loads(response['SecretString'])
            
            # Update settings from secrets
            if 'SECRET_KEY' in secrets:
                self.secret_key = secrets['SECRET_KEY']
            if 'DATABASE_URL' in secrets:
                self.database_url = secrets['DATABASE_URL']
            if 'CORS_ORIGINS' in secrets:
                self.cors_origins = self.parse_cors_origins(secrets['CORS_ORIGINS'])
        except ImportError:
            # boto3 not installed, skip AWS secrets loading
            pass
        except ClientError as e:
            # AWS client error, skip but don't fail
            import warnings
            warnings.warn(f"AWS Secrets Manager error: {e}")


settings = Settings()

