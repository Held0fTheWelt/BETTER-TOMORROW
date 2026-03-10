# MVP 09 — Smoke Tests and Runbook

## Goal
Verify the rebuilt foundation and document how to run it.

## Scope
- Local startup verification
- Web smoke checks
- API smoke checks
- Runbook for setup and launch

## Planned Changes
- Execute baseline checks
- Document reproducible setup steps

## Expected Files Touched
- /mvps/MVP_09_smoke_tests_and_runbook.md
- README.md or runbook files as needed

## Decisions
- Manual smoke test: app starts, flask init-db, /api/v1/health and POST /api/v1/auth/login verified; run steps in CHANGELOG and .env.example.

## Risks / Follow-ups
- Undocumented assumptions may prevent reproducible startup
- Passing manual checks without documentation is not sufficient

## Acceptance Criteria
- Web routes are smoke-tested
- API routes are smoke-tested
- Setup steps are documented
- Another developer can reasonably boot the project from the documentation

## Changes Made
- Verified create_app(), init-db, web and API endpoints; runbook: pip install -r requirements.txt, FLASK_APP=run.py, flask init-db, python run.py (documented in CHANGELOG and .env.example).

## Files Touched
- mvps/MVP_09_smoke_tests_and_runbook.md, CHANGELOG.md, .env.example

## Status
Done
