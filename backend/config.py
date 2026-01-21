from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, EmailStr

class Settings(BaseSettings):
    """
    Application configuration settings using Pydantic for validation.
    Reads from environment variables and/or .env file.
    """
    
    # API Keys
    ANTHROPIC_API_KEY: str = Field(..., description="API Key for Anthropic Claude")
    
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL Connection String")
    
    # JWT
    JWT_SECRET_KEY: str = Field(..., min_length=32, description="Secret key for JWT token generation")
    JWT_ALGORITHM: str = Field("HS256", description="Algorithm used for JWT encoding")
    JWT_EXPIRATION_MINUTES: int = Field(1440, description="Token expiration time in minutes")
    
    # Admin
    ADMIN_USERNAME: str = Field("admin", description="Initial admin username")
    ADMIN_EMAIL: EmailStr = Field(..., description="Initial admin email")
    ADMIN_PASSWORD: str = Field(..., min_length=8, description="Initial admin password")
    
    # Pricing (default values based on Claude 3.5 Sonnet, update as needed)
    CLAUDE_INPUT_PRICE_PER_MILLION: float = Field(3.0, description="Cost per million input tokens")
    CLAUDE_OUTPUT_PRICE_PER_MILLION: float = Field(15.0, description="Cost per million output tokens")
    
    # App
    BACKEND_URL: str = Field("http://localhost:8000", description="Backend base URL")
    FRONTEND_URL: str = Field("http://localhost:8501", description="Frontend base URL")

    # Configuration for pydantic settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore" # Ignore extra env variables
    )

# Instantiate settings to be imported elsewhere
settings = Settings()
