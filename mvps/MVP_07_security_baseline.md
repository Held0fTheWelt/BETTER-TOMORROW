# MVP 07 — Security Baseline

## Goal
Establish a practical security baseline for the new server foundation.

## Scope
- CORS
- Rate limiting
- Environment-based secrets
- Safer defaults
- Session cookie settings review

## Planned Changes
- Clean security-related configuration
- Remove debug-first assumptions from the base runtime

## Expected Files Touched
- /mvps/MVP_07_security_baseline.md
- app/config.py
- app/extensions.py
- related security/config files

## Decisions
- CORS via flask-cors in init_app; rate limiting via Flask-Limiter on API routes; SECRET_KEY and JWT_SECRET_KEY from env; optional PREFER_HTTPS for session cookies; 429 JSON handler.

## Risks / Follow-ups
- Over-tightening may slow local development
- Under-tightening may preserve weak defaults from source projects

## Acceptance Criteria
- Secrets are environment-driven
- CORS is configured
- Rate limiting is active where intended
- Security defaults are cleaner than the source projects

## Changes Made
- app/extensions.py: CORS, limiter; app/config.py: SECRET_KEY, JWT_*, SESSION_COOKIE_*, RATELIMIT_DEFAULT; per-route @limiter.limit on API; 401/429 JSON responses in create_app.

## Files Touched
- app/config.py, app/extensions.py, app/__init__.py, app/api/v1/auth_routes.py, app/api/v1/system_routes.py, mvps/MVP_07_security_baseline.md

## Status
Done
