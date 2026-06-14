import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change this in production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./app.db")
REMINDER_CHECK_INTERVAL = int(os.getenv("REMINDER_CHECK_INTERVAL", "10"))
REMINDER_PROCESSING_TIMEOUT_MINUTES = int(os.getenv("REMINDER_PROCESSING_TIMEOUT_MINUTES", "5"))
REDIS_URL = REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0"
)
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

#redis://redis:6379/0 is correct when running through Docker Compose.
#    "redis://localhost:6379/0"