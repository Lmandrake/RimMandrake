# PITS_STALE_DEPLOY_COLLISION_1

MEASURED 2026-09-30 (read-only): the live `ModsConfig.xml` (612 active) contains BOTH
`mandrake.rm.flowworks` and `mandrake.rm.pits`. The game folder `Mods/Pits/` (About.xml dated
2026-08-30, `Assemblies/RimMandrakePits.dll`) is the pre-merge Pits mod. **All 22 of its defNames collide
with FlowWorks' defs** (`RM_OpenPit_Bare`, `RM_OpenPit_Spiked`, `RM_PinnedInPit`, `RM_DigPitDeeper`, …).
Pits merged into FlowWorks at `cade628c1`; the source folder holds only `__pycache__`.

Effect: duplicate defs (later load wins or errors) and a second, stale assembly defining the old pit
classes — any pit behaviour seen on the full list may be the OLD mod's. Blocks
`FLOWWORKS_NORTHSTAR_GREEN_FULL_1`.

## acceptance
- `mandrake.rm.pits` removed from the live list and from `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (parse with ET, never grep).
- `Mods/Pits/` retired (moved aside, not deleted on inference) — check no savegame references a Pits-only def first (rimworld-savegame skill; placed Things are a third reference).
- Next load's Player.log: no duplicate-def warning for any `RM_` pit def, no `RimMandrakePits` assembly load line.
- Touches his live list: do it while holding the bridge, game down.
