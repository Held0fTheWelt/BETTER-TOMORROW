# MVP 06 — API v1 and JWT Auth

## Goal
Add a versioned API layer with JWT authentication.

## Scope
- /api/v1 blueprint
- API login route
- Protected route
- Basic JSON responses

## Planned Changes
- Add API structure
- Add JWT auth wiring
- Add protected example route

## Expected Files Touched
- /mvps/MVP_06_api_v1_and_jwt_auth.md
- app/api/v1/auth_routes.py
- app/api/v1/system_routes.py
- related API/auth files

## Decisions
- api_v1_bp registered at /api/v1; auth_routes (register, login, me); system_routes (health, test/protected); JWT loaders in create_app; rate limits per route.

## Risks / Follow-ups
- Legacy auth concepts may conflict with new API auth boundaries
- Token configuration must remain environment-driven where practical

## Acceptance Criteria
- /api/v1 exists
- Login returns JWT
- Protected route requires valid token
- Responses are generic and not tied to movie/blog features

## Changes Made
- app/api/v1/__init__.py (api_v1_bp), auth_routes.py (register, login, me), system_routes.py (health, test/protected); JWT create_access_token on login; @jwt_required() on me and protected; register_api(app) in app/__init__.py.

## Files Touched
- app/api/__init__.py, app/api/v1/__init__.py, app/api/v1/auth_routes.py, app/api/v1/system_routes.py, app/__init__.py, mvps/MVP_06_api_v1_and_jwt_auth.md

## Status
Done
