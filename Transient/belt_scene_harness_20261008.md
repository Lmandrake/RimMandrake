# Scene harness - 2026-10-08 (FOUNDRY helper)
Progress log, appended per step. Module: src/RimMandrake/Utils/scenes/
- start: bridge held by FOUNDRY; game up on live_20261008b.
## Scenes / criteria
- handoff ordered by owner before any scene was built. No module code written; no bridge calls made; no criteria verified. Game left up on live_20261008b.
## Still UNMEASURED, with NEXT
- Harness itself — NEXT: create src/RimMandrake/Utils/scenes/ (build/teardown by name, calls composed from Transient/belt_lc6_lib.py's call/spawn/list_things/AerialProbe helpers, tool names checked against the live tool list) + offline selftest.
- LIGHT_LEDGER A2-A5, DEEPFIRE_WORLD_LIGHT A1-A4 — NEXT: scene "dark_room_lamps" (walled roofed room, lamps on/off, time of day set), read the light values by state.
- GLOW_TANK A2/A3 — NEXT: scene "glow_tank_fed" (FlowWorks liquid tank piped to RM_GlowTank, seeded crowncarpet), read growth.
- FEVERWOOD A1-A3 — NEXT: read FEVER_WOOD_FIRST_SCRIPT_1 criteria, then scene on Fever Wood terrain with its cast.
- CHILL_AIR_PUMP A2-A4 — NEXT: scene "sealed_room_pump" (OxygenPump with ChillAirSupply in a sealed room), read temp/hediffs vs control.
- WETBULB A3/A4 — NEXT: scene "hot_humid_room" with protected vs unprotected pawn, read heat hediffs.
- BIOME_ARRIVAL A2 — NEXT: a map on an RM_ biome (quicktest with biome override), read the arrival letter.
- SURFACE_HOME_MAP_HELPER A1 — NEXT: scene needs a sea-floor home map (RM_SeabedLayer); check a bridge tool can make one, else rimbridge-companion build.
- HARMONY A2 — NEXT: throwaway deliberately-broken DLL deploy on a minimal tier; needs a kill/swap.
- PARENTAL_ENRAGE A1 — NEXT: test fixture def with calf/adult mode (no shipped species uses it), or report as unbuildable-live.
- Piinnok fire-AOE — NEXT: find a fire source that damages (flamethrower/incendiary DamageDef via jawa/damage Flame), apply to hidden piinnok.
- FALLEN_WIRE A5 canal-oil half — NEXT: FlowWorks canal with oil fluid under a live wire tip.
- ELDER A1 offer draw — NEXT: drive the offer draw by state (debug quest/incident trigger) and read the result.
