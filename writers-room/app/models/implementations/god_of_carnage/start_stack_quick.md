---
id: implementation.god_of_carnage.start_stack.quick
kind: runtime_stack
stack_type: scenario_start
variant: quick
parent:
  scenario: implementation.god_of_carnage
references:
  required:
    - template.characters.gm.quick_start
    - template.scenes.scene.quick
    - implementation.god_of_carnage.scenario.core
    - implementation.god_of_carnage.player_role.penelope_longstreet
    - implementation.god_of_carnage.player_role.michael_longstreet
    - implementation.god_of_carnage.scene.s01_arrival_and_statement
  optional:
    - implementation.god_of_carnage.npc.annette_reille
    - implementation.god_of_carnage.npc.alain_reille
tags:
  - quick_start
  - scenario_stack
---

# Start Stack — Quick

Load this when you want to begin play fast with minimal context.

## Load Order
1. `template.characters.gm.quick_start`
2. `implementation.god_of_carnage.scenario.core`
3. one player role:
   - `implementation.god_of_carnage.player_role.penelope_longstreet`
   - or `implementation.god_of_carnage.player_role.michael_longstreet`
4. `template.scenes.scene.quick`
5. `implementation.god_of_carnage.scene.s01_arrival_and_statement`

## Quick Runtime Rule
Start in the apartment, with the meeting already underway or just beginning.
Do not frontload backstory.
Make the first exchange polite, tense, and immediately unstable.
