"""Configuration loaded from environment."""
import os
from pathlib import Path

# Load .env when present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    """Base config from environment."""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-change-in-production"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database: default SQLite in instance folder
    _instance_path = Path(__file__).resolve().parent.parent / "instance"
    _default_db = _instance_path / "wos.db"
    _uri = os.environ.get("DATABASE_URI")
    if not _uri:
        _instance_path.mkdir(parents=True, exist_ok=True)
        _uri = "sqlite:///" + str(_default_db).replace("\\", "/")
    SQLALCHEMY_DATABASE_URI = _uri

    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or os.environ.get("SECRET_KEY") or "jwt-secret-change-me"
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 86400))
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # Session cookie (HTTPS)
    _prefer_https = os.environ.get("PREFER_HTTPS", "").strip().lower() in ("1", "true", "yes")
    if _prefer_https:
        SESSION_COOKIE_SECURE = True
        SESSION_COOKIE_SAMESITE = "Lax"

    # Rate limiting
    RATELIMIT_DEFAULT = os.environ.get("RATELIMIT_DEFAULT", "100 per minute")
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")


class TestingConfig(Config):
    """Config for tests: in-memory DB, high rate limit, fixed JWT key."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-jwt-secret-key-at-least-32-bytes-long"
    RATELIMIT_DEFAULT = "1000 per minute"
    WTF_CSRF_ENABLED = False
