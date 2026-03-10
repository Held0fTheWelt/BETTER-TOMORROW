# MVP 02 — Target Architecture

## Goal
Define the target architecture for the new World of Shadows Flask server foundation.

## Scope
- App factory structure
- Blueprint layout
- Auth split between web and API
- Target folders and naming conventions
- Removal of movie/blog vocabulary from runtime architecture

## Planned Changes
- Create the architecture definition
- Define target routes and module boundaries

## Expected Files Touched
- /mvps/MVP_02_target_architecture.md

## Decisions
- Single app factory; web blueprint (session) and api/v1 blueprint (JWT); config from env; extensions in separate module; no backend_app/frontend_app split.

## Risks / Follow-ups
- Over-preserving source layout may leak unwanted domain concepts
- Authentication split must remain practical and minimal

## Acceptance Criteria
- Target folder structure is defined
- Web/API split is defined
- Session/JWT split is defined
- Domain-specific naming is removed from the target design

## Changes Made
- Documented target layout (app/, config, extensions, models, web, api/v1, static), auth split, DB and config choices.

## Files Touched
- mvps/MVP_02_target_architecture.md

## Status
Done
