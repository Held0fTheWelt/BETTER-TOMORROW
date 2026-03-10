# MVP 04 — Database and User Model

## Goal
Add the minimal generic database layer and a reusable User model.

## Scope
- SQLAlchemy integration
- Minimal User model
- SQLite default database setup
- Generic persistence only

## Planned Changes
- Add base DB wiring
- Add generic User model

## Expected Files Touched
- /mvps/MVP_04_database_and_user_model.md
- app/models/user.py
- related database wiring files

## Decisions
- User model: id, username, password_hash; SQLite default; db in extensions; seed via flask init-db.

## Risks / Follow-ups
- Old models may still influence imports
- Password handling must remain generic and secure enough for baseline usage

## Acceptance Criteria
- User model exists
- DB wiring works
- SQLite default works
- No movie/blog model remains required for app startup

## Changes Made
- app/models/user.py (User); app/extensions.py (db); config SQLALCHEMY_DATABASE_URI; run.py init-db command creates tables and optional admin user.

## Files Touched
- app/models/__init__.py, app/models/user.py, app/config.py, app/extensions.py, run.py, mvps/MVP_04_database_and_user_model.md

## Status
Done
