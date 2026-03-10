# MVP 03 — Project Bootstrap

## Goal
Create the new clean bootstrap structure for the World of Shadows server.

## Scope
- app/__init__.py
- app/config.py
- app/extensions.py
- run.py
- .env.example
- requirements cleanup

## Planned Changes
- Create the foundation files
- Make the application bootable

## Expected Files Touched
- /mvps/MVP_03_project_bootstrap.md
- app/__init__.py
- app/config.py
- app/extensions.py
- run.py
- .env.example
- requirements.txt

## Decisions
- Template/static paths via absolute paths from app package; single run.py entrypoint.

## Risks / Follow-ups
- Legacy entrypoints may conflict with the new app factory
- Requirements may include obsolete packages from source projects

## Acceptance Criteria
- App starts with the new structure
- App factory exists
- Extensions are separated cleanly
- No monolithic legacy entrypoint remains the main architecture

## Changes Made
- Added app/__init__.py (create_app), app/config.py, app/extensions.py, run.py, requirements.txt, .env.example; init_extensions(app); 404/500/429 and JWT error handlers; flask init-db CLI.

## Files Touched
- app/__init__.py, app/config.py, app/extensions.py, run.py, requirements.txt, .env.example, .gitignore, mvps/MVP_03_project_bootstrap.md

## Status
Done
