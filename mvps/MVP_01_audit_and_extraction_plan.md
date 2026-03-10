# MVP 01 — Audit and Extraction Plan

## Goal
Audit both reference projects and classify reusable versus disposable parts for the new World of Shadows server foundation.

## Scope
- Inspect MasterBlogAPI
- Inspect MovieProject
- Identify reusable technical patterns
- Identify disposable domain-specific code
- Identify risks, leftovers, and migration constraints

## Planned Changes
- Create this audit document
- Produce a keep/remove/replace mapping

## Expected Files Touched
- /mvps/MVP_01_audit_and_extraction_plan.md

## Decisions
- Reuse from MasterBlogAPI: JWT, CORS, limiter, api/v1, User; discard posts/categories/tags/comments, frontend_app. Reuse from MovieProject: base template, session flow, static; discard Movie, OMDb, movie routes/templates.

## Risks / Follow-ups
- Hidden coupling between source-project modules
- Legacy runtime paths may still reference domain-specific files

## Acceptance Criteria
- Reusable parts are listed clearly
- Disposable parts are listed clearly
- Replace-vs-keep rationale exists
- No implementation is falsely marked as completed

## Changes Made
- Audited backend_app.py, frontend_app.py, init_db (MasterBlogAPI); app.py, data/*, templates (MovieProject). Documented keep/discard mapping.

## Files Touched
- mvps/MVP_01_audit_and_extraction_plan.md

## Status
Done
