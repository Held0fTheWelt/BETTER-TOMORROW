# World of Shadows Prompt Models — Refactored Pack

This pack separates **templates** from **implementations**.

## Structure
- `markdown/` contains reusable prompt templates.
- `markdown/_registry/` contains IDs, presets, and indexing metadata.
- `implementations/` contains concrete scenario files.

## Reference Model
- Directories are for humans.
- `id` is the canonical machine-stable reference.
- `base` links fast or deep variants back to their conceptual root.
- `inject_with` lists useful companion prompts for runtime stacking.
- `depends_on` marks prompts that usually need to be loaded first.
