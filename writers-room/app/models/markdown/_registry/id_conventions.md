# ID Conventions

## Pattern
`<layer>.<domain>.<subject>.<variant>`

Examples:
- `template.characters.gm.standard`
- `template.scenes.scene.director`
- `template.core.session_state.standard`
- `implementation.god_of_carnage.scene.opening.quick`

## Rules
- use lowercase only
- separate parts with dots
- keep IDs stable even if files move
- use `template` for reusable prompt models
- use `implementation` for concrete scenario files
- use `variant` for quick, standard, director, starter, or current forms
