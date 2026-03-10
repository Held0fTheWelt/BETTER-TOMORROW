# MVP 05 — Web Blueprint and Templates

## Goal
Build a minimal server-rendered web layer using sessions.

## Scope
- Web blueprint
- Home page
- Base template
- Login page
- Logout flow
- Session-based access flow

## Planned Changes
- Add web routes
- Add templates and base layout
- Add session-based login/logout behavior

## Expected Files Touched
- /mvps/MVP_05_web_blueprint_and_templates.md
- app/web/routes.py
- app/web/templates/base.html
- related web files

## Decisions
- Web blueprint without url_prefix; session keys user_id, username; templates extend base.html; static in app/static.

## Risks / Follow-ups
- Template reuse from MovieProject may bring domain clutter
- Session logic must remain clearly separated from JWT API logic

## Acceptance Criteria
- Web home page renders
- Login page renders
- Session-based flow works at a baseline level
- No movie-specific templates remain in the active runtime path

## Changes Made
- app/web/routes.py (health, home, login, logout); app/web/templates/base.html, home.html, login.html, 404.html, 500.html; app/static/style.css; user_service for verify_user; session-based login flow.

## Files Touched
- app/web/__init__.py, app/web/routes.py, app/web/templates/*.html, app/static/style.css, app/services/user_service.py, mvps/MVP_05_web_blueprint_and_templates.md

## Status
Done
