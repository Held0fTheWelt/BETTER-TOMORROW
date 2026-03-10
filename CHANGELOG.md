# Changelog

All notable changes to the World of Shadows project are documented in this file.

---

## [Unreleased]

_Nothing yet._

---

## [0.0.3] - 2025-03-10

### Security

- **Secrets:** Removed hardcoded fallback secrets from production config. `SECRET_KEY` and `JWT_SECRET_KEY` must be set in the environment. App raises at startup if `SECRET_KEY` is missing (unless testing or `DEV_SECRETS_OK=1`).
- **Dev-only fallback:** Added `DevelopmentConfig` and `DEV_SECRETS_OK` env var. When set, dev fallback secrets are used and `flask seed-dev-user` is allowed. Not for production.
- **Default user seeding removed:** `flask init-db` only creates tables; it no longer creates an admin/admin user. Use `flask seed-dev-user` with `DEV_SECRETS_OK=1` for local dev only.
- **Logout:** Web logout is POST only. Logout link replaced with a form and CSRF token to reduce abuse.
- **CSRF:** Web forms (login, logout) protected with CSRF. API blueprint exempt; API remains JWT-based.
- **CORS:** Origins are configurable via `CORS_ORIGINS` (comma-separated). No CORS when unset (same-origin only).
- **Session cookies:** `SESSION_COOKIE_HTTPONLY` and `SESSION_COOKIE_SAMESITE` set explicitly; `SESSION_COOKIE_SECURE` when `PREFER_HTTPS=1`.

### Added

- **Web auth:** Protected route `/dashboard`; central `require_web_login` decorator in `app/web/auth.py`. Anonymous access to `/dashboard` redirects to `/login`.
- **Login flow:** If already logged in, GET `/login` redirects to dashboard. Optional `next` query param for redirect-after-login.
- **Dashboard template:** `app/web/templates/dashboard.html`.
- **CLI:** `flask seed-dev-user` to create a default admin user when `DEV_SECRETS_OK=1`.
- **Documentation:** `README.md` (purpose, structure, setup, env, web/API usage). `docs/runbook.md` (local workflow, example API flow). `docs/security.md` (auth model, CSRF, CORS, cookies, dev-only behavior).

### Changed

- **Config:** `SECRET_KEY`, `JWT_SECRET_KEY` from env only in base config. Added `CORS_ORIGINS`, explicit session cookie settings. `DevelopmentConfig` and `TestingConfig` separated.
- **Startup:** Debug mode driven by `FLASK_DEBUG` instead of `FLASK_ENV`.
- **API:** User lookup uses `db.session.get(User, id)` (SQLAlchemy 2.x) instead of `User.query.get(id)`.
- **Web health:** Docstring aligned: returns JSON status.
- **.env.example:** Updated with required vars, `CORS_ORIGINS`, `FLASK_DEBUG`, `DEV_SECRETS_OK`.

### Removed

- **Default admin from init-db:** No automatic admin/admin creation.
- **Empty layer:** Removed unused `app/repositories/` package.

### Documentation

- README.md: project purpose, scope, structure, setup, environment table, web/API usage, limitations, links to runbook and security.
- docs/runbook.md: one-time setup, start server, web flow, API curl examples, health checks, troubleshooting.
- docs/security.md: session vs JWT auth, CSRF scope, secrets and dev fallback, default users, CORS, session cookies, rate limiting.

---

## [0.0.2] - 2025-03-10

### Added

- Test suite: Pytest tests for web and API, in-memory DB config, pytest.ini, pytest and pytest-cov in requirements.
- Planning docs: Milestone list and execution prompts for staged rebuild (no code changes).

---

## [0.0.1] - 2025-03-10

### Added

- Server foundation: Flask app factory, config, extensions (db, jwt, limiter, CORS), single entrypoint run.py.
- Database: SQLite default, User model, flask init-db.
- Web: Blueprint with home, health, login, logout; session auth; templates and static.
- API: /api/v1 health, auth (register, login, me), protected test route; JWT and rate limiting.
- Tooling and docs: requirements.txt, .env.example, Postman collection for API testing.
