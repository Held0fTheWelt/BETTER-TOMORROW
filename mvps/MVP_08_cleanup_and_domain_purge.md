# MVP 08 — Cleanup and Domain Purge

## Goal
Remove legacy movie/blog/domain clutter from the runtime codebase.

## Scope
- Remove movie-specific behavior
- Remove OMDb behavior
- Remove blog-specific behavior
- Remove dead imports, dead templates, and obsolete helpers
- Clean runtime paths

## Planned Changes
- Delete or isolate domain leftovers
- Fix imports and startup references

## Expected Files Touched
- /mvps/MVP_08_cleanup_and_domain_purge.md
- multiple legacy files depending on findings

## Decisions
- No movie or blog code in codebase; World of Shadows built as new foundation; .gitignore excludes instance/, *.db, .env.

## Risks / Follow-ups
- Legacy files may still be referenced indirectly
- Cleanup may expose hidden dependencies from earlier steps

## Acceptance Criteria
- Active runtime path is free from movie/blog logic
- Imports are clean
- Dead files are removed or clearly archived
- The codebase looks like a reusable server base, not a patched demo app

## Changes Made
- Foundation created clean; no Movie/Post/OMDb imports or routes; generic User and auth only; .gitignore updated.

## Files Touched
- .gitignore, codebase (no legacy domain files retained), mvps/MVP_08_cleanup_and_domain_purge.md

## Status
Done
