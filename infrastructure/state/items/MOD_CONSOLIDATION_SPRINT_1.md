# MOD_CONSOLIDATION_SPRINT_1

## Spec
Execute `infrastructure/state/mod_consolidation_map.csv` (103 rows, the
single source of truth — patch it, never re-derive) per
`design/MOD_CONSOLIDATION_PLAN.md` §4 (v3, SIGNED OFF 2026-09-08 on
MOD_NAMING_CONSOLIDATION_AUDIT_1). 77 → 53 mods; RM 21 / RSW 12 / RUT 20.

🔴 The game-down window is MECHANICAL ONLY: git mv, About merges,
packageId consolidation, MayRequire rewrite from the map, tier-move
defName re-prefix (R4, Phase-2 machinery), ModsConfig swap, redeploy,
refresh.py, naming_lint zero, validate_patch --live/--defs, magenta
sweep, minimal-list load. NO authoring in-window.

GATES (must be closed before the Chronicle/Property/Pursuit/Graffiti/
Pyrelands rows execute; the rest of the map does not wait):
- CHRONICLE_EVENT_SPINE_1 (hook points named before those merges)
- GRAFFITI_GENERIC_MARKS_1 (RM Graffiti needs default content to ship)
- PYRELANDS_GENERIC_TEXT_1 (self-contained biome text + donor BiomeDef)

Write-freeze during the window: rimflow blocking item + the temporary
PreToolUse src/ hook (NAMING_SCHEME_PLAN §5 Phase 2 precedent).
Hard ordering: this sprint → regenerate .rid/.xtp → world re-import →
only then any world freeze.

## Verify
Per-destination def-count reconciliation vs sources (plan §4's
lost-nothing check); naming_lint 0 violations; MayRequire checker 0;
minimal-list load clean; every VERIFY row on the map resolved or
explicitly re-parked with reason.

## Criteria
All 103 map rows executed or re-parked; counts reconcile; owner told
scheduling was his call — do not start without his go.

## Game-down window runbook — prepared 2026-09-08 (BENCH)

15 dying ids are ACTIVE in live ModsConfig (MEASURED against the live file).
Swap old→new (dedupe after — several map to one destination):
```
mandrake.rut.factionslate -> mandrake.rut.patches
mandrake.rsw.beastnorm -> mandrake.rsw.swbestiary
mandrake.rsw.seabeasts -> mandrake.rsw.swbestiary
mandrake.rm.sauridfrillfix -> mandrake.rm.patches
mandrake.rm.gravshipastronautfix -> mandrake.rm.patches
mandrake.rm.toolbeltfix -> mandrake.rm.patches
mandrake.rsw.blastdoorframeasyncfix -> mandrake.rsw.patches
mandrake.rm.researchkiteastfix -> mandrake.rm.patches
mandrake.rm.desertvehiclereskin -> mandrake.rsw.desertvehiclereskin
mandrake.rsw.jawaikee -> mandrake.rsw.swbestiary
mandrake.rsw.fireecology -> mandrake.rm.pyrelands
mandrake.rut.fireecology -> mandrake.rut.fireecology
mandrake.rm.salvageclaim -> mandrake.rm.property
mandrake.rm.theft_hauler -> mandrake.rm.property
mandrake.rut.shell -> mandrake.rut.menushell
```
Then: deploy_custom_mods.py plan → --apply; refresh.py; minimal-list load proof.
Game must be DOWN for the swap+deploy (ModsConfig describes the NEXT load).
