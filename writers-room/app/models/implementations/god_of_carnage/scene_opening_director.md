---
id: implementation.god_of_carnage.scene.opening.director
kind: prompt_implementation
implementation_type: scene
variant: director
base: implementation.god_of_carnage.scene.opening.quick
parent:
  scenario: implementation.god_of_carnage
  location: implementation.god_of_carnage.location.longstreet_apartment
  room: implementation.god_of_carnage.room.living_room
inject_with:
- template.characters.gm.standard
- template.scenes.scene.director
- template.core.session_state.standard
- implementation.god_of_carnage.npc.annette_reille
- implementation.god_of_carnage.npc.alain_reille
tags:
- scene
- opening
- director
---

# Opening Scene — Director

## Situation
The meeting has been framed as a civil attempt to discuss a violent incident between two children.
Everyone is still performing reasonableness, but each participant already has a different hidden win condition.

## Hidden Tensions
- precise wording equals moral leverage
- hospitality can feel generous or controlling
- professional detachment reads as cruelty
- any interruption can expose the gap between public politeness and private contempt

## Director Guidance
- keep the first exchange deceptively polite
- let interruptions, corrections, and body language carry pressure
- offer easy exits that do not actually resolve the social trap
- allow alliances to shift as soon as one truth hits a nerve
