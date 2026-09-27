# CHILL_WORLD_CRATER_1 — the live world-tile crater

## what

Card ruling (2026-09-27): when the sarlacc-guts route fires
(CHILL_WARLAB_ROUTES_1's apocalyptic tier), **the lake's world tiles swap to a
new crater biome in-save** — the planet is visibly wounded from orbit,
forever.

Deliverables:
1. A crater BiomeDef (dead glass, no life, its own world-map color).
2. A live tile-swap mechanism: on the detonation event, the Chill's world
   tiles change biome in the running save (plus whatever regeneration/cleanup
   the affected maps need).

## doctrine guards, so this never gets mis-filed

- **A crater BiomeDef with 0 tiles is the EXPECTED state** — it only ever
  gains tiles by the in-game event. Never a finding.
- **This is not worldgen and produces no alternative planets** — it is a
  scripted in-save consequence on THE map, same planet, one wound. The
  no-worldgen law is untouched.
- First bar is **feasibility**: prove a live biome swap on world tiles is
  save-safe (the bridge's world tools do live biome writes + world_commit at
  authoring time; the open question is doing it from game code mid-save,
  and what happens to generated maps, roads and settlements on the swapped
  tiles). Report before building the full event.

## provenance

Decision taken by question card 2026-09-27 (live tile change chosen over
maps-only and defer options). Filed by BENCH out of the Chill concept sitting.
