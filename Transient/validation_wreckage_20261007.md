# Wreckage validation, 2026-10-07 - LINT ONLY (under the ~800-line non-engine bar), nothing committed

Sizing: 1069 lines in 6 files. Non-engine logic is about 150 lines: RM_WreckWeathering.ShiftTier (15), the weathering fold in ResolveReferences (45), RareChanceFor / ApplyHazard / loot stack scaling (25), the disabledFields comma set (15), ConfigErrors rules (30), the wreck-fall drop loop and the field placement miss counter (30). The rest is GenStep_Scatterer plumbing (TryFindScatterCell, GenSpawn.CanSpawnAt, Jacket ring), ThingSetMaker generation, Skyfaller spawn, a Harmony prefix/finalizer pair and the settings UI. No kernel extracted: each pure rule is a few lines wrapped in engine calls.

## Lint
`python3 src/RimMandrake/Utils/lint_wreckage_defs.py [--quiet]`: 8 defs, 16 classes, 9 refs, 7 field checks, 8 settings: 0 ERROR, 0 WARN.
Shared-tool fixes found here (lint_mod_defs.py): (1) `GetNamedSilentFail("RM_SalvageLoot_" + tier)` was read as a lookup of the literal prefix (2 false WARNs) - a name built with `+` is now skipped; (2) a settings field read only inside a method of the settings class (`FieldDisabled` reading `disabledFields`) was reported as a dead toggle - such reads now count. A planted dead toggle still WARNs (checked on a copy).
