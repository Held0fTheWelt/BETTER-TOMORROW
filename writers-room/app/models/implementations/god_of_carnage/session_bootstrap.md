---
id: implementation.god_of_carnage.session.bootstrap
kind: prompt_implementation
implementation_type: session_bootstrap
variant: current
parent:
  scenario: implementation.god_of_carnage
depends_on:
- template.characters.gm.standard
- template.core.session_state.standard
- template.scenes.scene.starter
inject_with:
- implementation.god_of_carnage.location.longstreet_apartment
- implementation.god_of_carnage.room.living_room
- implementation.god_of_carnage.scene.opening.quick
tags:
- implementation
- bootstrap
- stage_play
---

# Session Bootstrap — Der Gott des Gemetzels

## Scenario Frame
- **Format:** social chamber play
- **Primary conflict:** a reconciliation meeting keeps collapsing into personal conflict
- **Player chooses one role:** Penelope Longstreet or Michael Longstreet
- **Guests present:** Annette Reille and Alain Reille
- **Primary play space:** the Longstreet apartment, centered on the living room

## Recommended Load Order
1. `template.characters.gm.standard`
2. `template.core.session_state.standard`
3. `template.scenes.scene.starter`
4. one player role implementation
5. `implementation.god_of_carnage.location.longstreet_apartment`
6. `implementation.god_of_carnage.room.living_room`
7. one opening scene implementation
