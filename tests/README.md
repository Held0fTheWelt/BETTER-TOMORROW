# Test Suite

Pytest-based tests for the World of Shadows server (web and API v1).

## Run

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=term-missing

# Only web or API
pytest tests/test_web.py -v
pytest tests/test_api.py -v
```

## Layout

- **conftest.py** – Fixtures: `app` (create_app with TestingConfig), `client`, `test_user`, `auth_headers` (JWT for API).
- **test_web.py** – Web routes: home, health, login (GET/POST), logout, 404.
- **test_api.py** – API v1: health, register, login, me, test/protected; status codes and JSON responses.

## Config

Tests use `TestingConfig`: in-memory SQLite, high rate limit, fixed JWT secret. See `app/config.py`.
