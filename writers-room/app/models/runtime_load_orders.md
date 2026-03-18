# Runtime Load Orders

## Purpose
This document defines practical load orders for prompt runtime stacks across small, medium, and larger context windows.

Use it to decide:
- what to load first
- what to keep under pressure
- what to drop when context gets tight
- which stacks fit different play styles

The main rule is:

1. load output control first
2. load the current playable space second
3. load the active actors third
4. load runtime state fourth
5. only then add broader world context

---

## Priority Model

### Priority A — Critical
These files usually matter most for moment-to-moment play.

- `gm_quick_start_prompt.md` or `gm_prompt_stack.md`
- `scene_quick_prompt_stack.md` or `scene_director_prompt_stack.md`
- `session_state_prompt_stack.md`
- active `location` / `room` / `micro setting`
- active NPC files
- active scene file from the implementation

### Priority B — Strong Support
These enrich pressure, continuity, and consequences.

- `consequence_heat_prompt_stack.md`
- `clue_secret_prompt_stack.md`
- `quest_or_mission_prompt_stack.md`
- `world_state_prompt_stack.md`

### Priority C — Expansion
These are useful when there is room for more depth.

- `setting_macro_prompt_stack.md`
- `district_prompt_stack.md`
- `faction_prompt_stack.md`
- `event_prompt_stack.md`
- `encounter_prompt_stack.md`

---

## 4k Context Window

### Goal
Fast, stable, scene-focused runtime.

### Recommended Load Order
1. `gm_quick_start_prompt.md`
2. `scene_quick_prompt_stack.md`
3. `session_state_prompt_stack.md`
4. active `room_or_place_prompt_stack.md` or concrete implementation location
5. active NPC files
6. current scene file
7. optional compact escalation or consequence note

### Best Use Cases
- small local models
- quick tests
- one-room scenes
- tightly focused social conflict
- fast iteration

### Avoid in 4k
- full macro setting
- full district files
- broad faction context
- long world state summaries
- multiple previous scenes
- inactive clues or inactive NPCs

### 4k Rule
Only keep:
- control
- scene
- room
- actors
- current state
- immediate pressure

---

## 8k Context Window

### Goal
Balanced standard runtime with stronger continuity.

### Recommended Load Order
1. `gm_prompt_stack.md` or `gm_quick_start_prompt.md`
2. `scene_director_prompt_stack.md`
3. `session_state_prompt_stack.md`
4. active location / room
5. active NPC files
6. current scene file
7. `consequence_heat_prompt_stack.md`
8. `clue_secret_prompt_stack.md`
9. compact `world_state_prompt_stack.md`
10. optional `quest_or_mission_prompt_stack.md`

### Best Use Cases
- default play mode
- guided scene direction
- dialogue-heavy episodes
- mystery scenes
- stronger memory continuity

### 8k Rule
Use this as the default operating range when possible.

---

## 16k Context Window

### Goal
Deeper continuity and richer support without losing focus.

### Recommended Load Order
1. `gm_prompt_stack.md`
2. `scene_director_prompt_stack.md`
3. `session_state_prompt_stack.md`
4. `world_state_prompt_stack.md`
5. `setting_macro_prompt_stack.md`
6. `district_prompt_stack.md` or other relevant local-context layer
7. active location
8. active sub-rooms if needed
9. active NPC files
10. `faction_prompt_stack.md` if relevant
11. `quest_or_mission_prompt_stack.md`
12. `clue_secret_prompt_stack.md`
13. `consequence_heat_prompt_stack.md`
14. current scene file
15. 1–3 short scene recaps
16. active event or encounter files

### Best Use Cases
- larger context models
- campaign continuity
- multi-thread scenes
- sessions with meaningful state carryover
- richer investigation or faction interplay

### 16k Rule
Add depth, not ballast.

---

## Runtime Presets

### Minimal Runtime
Use for:
- small context
- quick local testing
- fast social scenes

Load:
1. GM quick
2. Scene quick
3. Session state
4. current room
5. active NPCs
6. current scene

### Scene Director Runtime
Use for:
- cleaner scene handling
- stronger pacing
- better consequence awareness

Load:
1. GM standard
2. Scene director
3. Session state
4. current location / room
5. active NPCs
6. current scene
7. consequence / heat
8. clue / secret

### One-Room Social Conflict Runtime
Use for:
- chamber play
- tense dialogue
- alliance shifts
- escalating social breakdown

Load:
1. GM standard or quick
2. Scene director
3. Session state
4. primary room
5. scenario core
6. active characters
7. relationship map
8. escalation / consequence layer
9. current beat scene

### Investigation Runtime
Use for:
- clue-driven play
- uncertain truth
- layered revelations

Load:
1. GM standard
2. Scene director
3. Session state
4. current location
5. active NPCs
6. clue / secret
7. quest / mission
8. consequence / heat
9. optional compact world state

---

## Drop Order Under Context Pressure

When the context window becomes tight, remove in this order:

1. old event files
2. faction files
3. district files
4. macro setting
5. broad world state
6. inactive quest files
7. inactive clue files
8. side rooms
9. inactive NPCs

Do not drop early:
- GM prompt
- active scene
- session state
- current room
- active NPCs
- escalation / consequence layer

---

## Compact Runtime Snapshot Pattern

A compact runtime snapshot is often better than many larger files.

Example:

```md
# Active Runtime Snapshot

- Mode: scene_director
- Current scene: {{current_scene_id}}
- Current room: {{current_room_id}}
- Player role: {{player_role_id}}
- Present NPCs: {{present_npc_ids}}
- Current tension: {{current_tension}}
- Active objects: {{active_objects}}
- Active secrets: {{active_secrets}}
- Escalation stage: {{escalation_stage}}
- Immediate pressure: {{immediate_pressure}}
```

Recommended use:
- prepend before active scene material
- update after each major turn or beat
- keep compact and factual

---

## God of Carnage — Suggested Runtime Loads

### 4k
1. GM quick
2. Scene quick
3. Session state
4. living room
5. player role
6. Annette
7. Alain
8. current scene

### 8k
1. GM standard
2. Scene director
3. Session state
4. scenario core
5. adaptation / alias layer
6. living room
7. player role
8. Annette
9. Alain
10. Michael or Penelope as counterpart
11. relationship map
12. escalation / consequence
13. current scene

### 16k
Use the 8k stack, then add:
- 1–2 short prior-scene recaps
- side rooms only if currently relevant
- clue / secret layer
- compact world-state support only if it materially affects play

### Special Rule for This Scenario
This scenario works best when the runtime stays centered on:
- the room
- the present participants
- active emotional fault lines
- recurring props
- escalation beats
- failed departure attempts

Do not overinflate the stack with world breadth that the chamber-play structure does not need.

---

## Recommended Defaults

### Default for small local models
- `gm_quick_start_prompt.md`
- `scene_quick_prompt_stack.md`
- `session_state_prompt_stack.md`
- one location
- active NPCs
- one current scene

### Default for balanced play
- `gm_prompt_stack.md`
- `scene_director_prompt_stack.md`
- `session_state_prompt_stack.md`
- active location
- active NPCs
- current scene
- `consequence_heat_prompt_stack.md`
- `clue_secret_prompt_stack.md`

### Default for rich continuity
Start with the balanced play stack, then add:
- `world_state_prompt_stack.md`
- `setting_macro_prompt_stack.md`
- `district_prompt_stack.md`
- `faction_prompt_stack.md`
- 1–3 short recap blocks

---

## Final Guideline
When in doubt, prefer:
- sharper current context
over
- broader but weaker world context

The model should always know:
- who is here
- where this is happening
- what is under pressure
- what just changed
- what kind of response it is expected to produce
