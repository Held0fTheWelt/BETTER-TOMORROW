# World of Shadows — Milestone List

Master plan for the server foundation. Each task is documented in its own MVP file.

| # | Milestone | File | Goal | Status |
|---|-----------|------|------|--------|
| 01 | Audit and Extraction Plan | [MVP_01_audit_and_extraction_plan.md](MVP_01_audit_and_extraction_plan.md) | Audit MasterBlogAPI and MovieProject; map reusable vs disposable parts | Done |
| 02 | Target Architecture | [MVP_02_target_architecture.md](MVP_02_target_architecture.md) | Define target structure, app factory, web/API split, session/JWT auth | Done |
| 03 | Project Bootstrap | [MVP_03_project_bootstrap.md](MVP_03_project_bootstrap.md) | Create app factory, config, extensions, run.py, requirements, .env.example | Done |
| 04 | Database and User Model | [MVP_04_database_and_user_model.md](MVP_04_database_and_user_model.md) | Add SQLAlchemy, User model, SQLite default, flask init-db | Done |
| 05 | Web Blueprint and Templates | [MVP_05_web_blueprint_and_templates.md](MVP_05_web_blueprint_and_templates.md) | Web routes, base template, home, login/logout, session auth | Done |
| 06 | API v1 and JWT Auth | [MVP_06_api_v1_and_jwt_auth.md](MVP_06_api_v1_and_jwt_auth.md) | /api/v1 blueprint, login/register/me, protected route, JWT | Done |
| 07 | Security Baseline | [MVP_07_security_baseline.md](MVP_07_security_baseline.md) | CORS, rate limiting, env-based secrets, session cookie options | Done |
| 08 | Cleanup and Domain Purge | [MVP_08_cleanup_and_domain_purge.md](MVP_08_cleanup_and_domain_purge.md) | No movie/blog logic; clean imports and runtime path | Done |
| 09 | Smoke Tests and Runbook | [MVP_09_smoke_tests_and_runbook.md](MVP_09_smoke_tests_and_runbook.md) | Verify web/API locally; document setup and run steps | Done |
| 10 | Handover Summary | [MVP_10_handover_summary.md](MVP_10_handover_summary.md) | Summary of foundation, removed vs retained, next steps | Done |

---

## Reference

- Planning prompt: [00_start_prompt_cursor.txt](00_start_prompt_cursor.txt)
- Implementation combined bootstrap (03), database/user (04), web (05), API (06), security (07), and cleanup (08) into a single staged build. Additional docs: [MVP_04_web_and_api_routes.md](MVP_04_web_and_api_routes.md), [MVP_05_definition_of_done.md](MVP_05_definition_of_done.md) (definition-of-done checklist).
