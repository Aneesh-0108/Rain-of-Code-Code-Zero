import os

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure")
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = ENV == "development"
    ENABLE_SESSIONS = os.getenv("ENABLE_SESSIONS", "false").lower() == "true"

settings = Settings()