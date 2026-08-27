# LIVE.md — facts that needed a running game

## Live findings 2026-08-26 — layout layers

- **Power has two joining rules.** A TRANSMITTER (`transmitsPower: true` — conduits, **and SolarGenerator and Battery**) joins only by CARDINAL cell adjacency. A CONNECTOR (Cooler, most machines) binds to the nearest transmitter within `PowerConnectionMaker.ConnectMaxDist = 6`, no line-of-sight, reaching through walls. Measured 2026-08-26.
- **A connector binds AT SPAWN**; a transmitter appearing later never claims it. `rimplace/compile_calls` now emits transmitters first via `rimplace/netinfo.py`, which reads `transmitsPower` from the def dump and returns None rather than guessing.
- **`Building_Cooler` cools the cell BEHIND it** — `Position + IntVec3.South.RotatedBy(Rotation)`. Rot 0 in a north wall puts cold inside. A backwards cooler still reads `Current power use: Low` and looks alive.
- **Destroying a building marks its roof for collapse and rebuilding under it does not cancel that**; the collapse fires on the next TICK, after `set_roof_batch` has already reported "already correct". Read `room_get.openRoofCount` after a tick, never the roof writer's count.
- **`jawa/power_net` and `jawa/room_heat` exist in companion source but are NOT in the deployed DLL.** The live power reading is `jawa/inspect_string` (takes `rect`, not x/z) — `Grid excess` and `Current power use` are decisive. Redeploy needs the game down.
- **`jawa/destroy_batch` defaults to `categories: "Plant"`**; an undeclared `defs` key is ignored and it reports success having destroyed nothing.
- **`jawa/build_batch` takes rotation per-op** as `Def:x,z,rot`; a top-level `rot` does nothing.
- **The def dump nests ThingDef fields under `fields`** — `comps` is not top-level; reading from the root returns None, which reads as a clean wrong answer.
- **Thermal tests need ~5,000 ticks (2 in-game hours) from steady state.** Longer runs throw quest modals that PAUSE the game while `curTimeSpeed` still reads Superfast — check `paused`, not the speed.
- **Full 582-mod list was active 2026-08-26**, not the minimal list.
