# Changelog

All notable changes to the World of Shadows project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

_Nothing yet._

---

## [0.0.2] - 2025-03-10

### Added

- **Test suite:** Pytest tests for web and API (19 tests), in-memory DB config, pytest.ini, pytest and pytest-cov in requirements.
- **Planning docs:** Milestone list and execution prompts for staged rebuild (no code changes).

---

## [0.0.1] - 2025-03-10

### Added

- **Server foundation**
  - Flask application factory (`app/__init__.py`) with config loading from environment.
  - Central config (`app/config.py`) for `SECRET_KEY`, database URI, JWT, session cookies, and rate limiting.
  - Extensions module (`app/extensions.py`): SQLAlchemy, Flask-JWT-Extended, Flask-Limiter, Flask-CORS.
  - Single entrypoint `run.py`; no separate backend/frontend apps.

- **Database**
  - SQLite as default database (configurable via `DATABASE_URI`).
  - User model (`app/models/user.py`): `id`, `username`, `password_hash`.
  - CLI command `flask init-db` to create tables and optionally seed a default admin user.

- **Web (server-rendered)**
  - Blueprint `web`: routes for `/`, `/health`, `/login`, `/logout`.
  - Session-based authentication for browser users.
  - Templates: `base.html`, `home.html`, `login.html`, `404.html`, `500.html`.
  - Static assets: `app/static/style.css` (World of Shadows theme).

- **API (REST v1)**
  - Versioned API under `/api/v1`.
  - **Auth:** `POST /api/v1/auth/register`, `POST /api/v1/auth/login` (returns JWT), `GET /api/v1/auth/me` (protected).
  - **System:** `GET /api/v1/health`, `GET /api/v1/test/protected` (protected).
  - JWT authentication for API; CORS and rate limiting enabled.
  - Consistent JSON error responses for 401 and 429.

- **Tooling and docs:** requirements.txt, .env.example, Postman collection for API testing.

### Technical notes

- No movie or blog domain logic; foundation only.
- Code and identifiers in English.
- `.gitignore` updated (instance/, *.db, .env, __pycache__, etc.).
