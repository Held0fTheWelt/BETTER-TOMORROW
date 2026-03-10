"""Configuration loaded from environment. No hardcoded secrets in production."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _parse_cors_origins():
    """Parse CORS_ORIGINS env: comma-separated list, or None for same-origin only."""
    raw = os.environ.get("CORS_ORIGINS", "").strip()
    if not raw:
        return None
    return [o.strip() for o in raw.split(",") if o.strip()]


class Config:
    """Base config. SECRET_KEY and JWT_SECRET_KEY must be set via environment."""

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Required from environment; no insecure defaults
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or os.environ.get("SECRET_KEY")

    # Database
    _instance_path = Path(__file__).resolve().parent.parent / "instance"
    _default_db = _instance_path / "wos.db"
    _uri = os.environ.get("DATABASE_URI")
    if not _uri:
        _instance_path.mkdir(parents=True, exist_ok=True)
        _uri = "sqlite:///" + str(_default_db).replace("\\", "/")
    SQLALCHEMY_DATABASE_URI = _uri

    # JWT
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 86400))
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # CORS: configurable origins; None means same-origin only
    CORS_ORIGINS = _parse_cors_origins()

    # Session cookies: explicit and secure by default
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    _prefer_https = os.environ.get("PREFER_HTTPS", "").strip().lower() in ("1", "true", "yes")
    SESSION_COOKIE_SECURE = _prefer_https

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
    # CSRF: enabled for web forms; API is exempted in create_app
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None


class DevelopmentConfig(Config):
    """Dev-only: fallback secrets when DEV_SECRETS_OK=1. Do not use in production."""

    _dev_ok = os.environ.get("DEV_SECRETS_OK", "").strip() in ("1", "true", "yes")
    if _dev_ok:
        SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-do-not-use-in-production"
        JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or os.environ.get("SECRET_KEY") or "dev-jwt-secret-do-not-use-in-production"


class TestingConfig(Config):
    """Config for tests: in-memory DB, fixed secrets, CSRF disabled."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret-key-at-least-32-bytes-long"
    RATELIMIT_DEFAULT = "1000 per minute"
    WTF_CSRF_ENABLED = False
    CORS_ORIGINS = None
