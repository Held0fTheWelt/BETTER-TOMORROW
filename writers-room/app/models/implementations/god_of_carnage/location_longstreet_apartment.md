---
id: implementation.god_of_carnage.location.longstreet_apartment
kind: prompt_implementation
implementation_type: location
variant: current
parent:
  scenario: implementation.god_of_carnage
references:
  rooms:
  - implementation.god_of_carnage.room.living_room
inject_with:
- template.scenes.setting_micro.standard
- template.scenes.room_or_place.standard
tags:
- location
- apartment
- domestic
---

# Location — Longstreet Apartment

## Identity
- **Type:** well-kept apartment used as a social proving ground
- **Function in play:** a polite domestic environment that traps escalating hostility
- **Emotional effect:** comfort becomes claustrophobic pressure

## Adjacencies
- living room as main arena
- kitchen as retreat and reset space
- hallway as failed escape route
- bathroom as emergency spillover space
