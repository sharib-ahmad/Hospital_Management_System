import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class BaseConfig:
    # --- Base JWT Configuration ---
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-me")
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_COOKIE_CSRF_PROTECT = True

    # --- Base SQLAlchemy Configuration ---
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESTX_MASK_SWAGGER = False
    
    # --- Email Server Configuration ---
    SMTP_SERVER_HOST = os.getenv("SMTP_SERVER_HOST", "localhost")
    SMTP_SERVER_PORT = int(os.getenv("SMTP_SERVER_PORT", 1025))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
    SENDER_ADDRESS = os.getenv("SENDER_ADDRESS")

    # --- Caching Configuration ---
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/0")
    CACHE_DEFAULT_TIMEOUT = 300 # Default cache timeout in seconds (5 minutes)

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    # Default to PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    JWT_COOKIE_SECURE = False

class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    JWT_COOKIE_SECURE = True

config_dict = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}