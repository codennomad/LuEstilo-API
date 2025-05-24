import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "WhatsApp API"
    PROJECT_VERSION: str = "1.0.0"
    
    DB_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/db")
    
    JWT_SECRET: str = os.getenv("JWT_SECRET", "s3cr3t")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES: int = 30
    JWT_REFRESH_EXPIRES: int = 7
    
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")

settings = Settings()
