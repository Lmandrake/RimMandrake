# LIQUID_INDUSTRY_SETPIECES_1 — found industrial liquid works: desal, detox, tar refinery, pumping station

Filed by BENCH, 2026-09-13 (owner law: industrial scale is FOUND, not built —
`design/RimMandrake/liquids_framework_design.md` §4 "Found industry").

## spec

Set-pieces scattered via `RM_GENSTEP_PLACED_SETPIECES_1`'s shared scatterer:
desal plant on brine coasts, detox works near toxic bodies, tar-cracking
refinery (tar → vanilla chemfuel), pumping station. Each in WreckedMachines
tier grammar (Wrecked→Kludged→Repaired): found broken, repaired into the
industrial conversion tier, NEVER buildable from the menu in the campaign
(public wave adds a settings switch to allow building). Each stocks stealable
pumps/tanks (defs from LIQUID_LOGISTICS_MOD_1) feeding the tanker pillar.

## verify

Quicktest map with a forced set-piece: it spawns intact per the grid key,
repairs through tiers, converts at the industrial rate; the build menu never
offers it. Placement verified per-slot by listing things, not by the
placement log's net count.

## Watch out

- Depends on RM_GENSTEP_PLACED_SETPIECES_1 (the scatterer), and on
  LIQUID_REGISTRY_CORE_1 + LIQUID_LOGISTICS_MOD_1 for what the pieces do and
  stock.
- Siting rules read worldTags/terrain — coordinate with WORLDMAP_LIQUID_TAGS_1
  so a desal plant does not spawn beside a tar lake.
- Art-heavy: budget sprite work per the generating-rimworld-sprites skill and
  the 256² downscale lesson.
