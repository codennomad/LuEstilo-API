import os
import sys
from dotenv import load_dotenv

# Load .env.test if running under pytest, else load .env
if "pytest" in sys.modules:
    load_dotenv(".env.test")
else:
    load_dotenv()

class Settings:
    PROJECT_NAME: str = "WhatsApp API"
    PROJECT_VERSION: str = "1.0.0"
    
    DB_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/fastapi_commercial_api")
    
    JWT_SECRET: str = os.getenv("JWT_SECRET", "kwOtC+G5U.9yAQ.r1ve-4qa$-f")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES: int = 30
    JWT_REFRESH_EXPIRES: int = 7
    
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")

settings = Settings()
