# StructureInjections validation, 2026-10-07 - LINT ONLY (under the ~800-line non-engine bar), nothing committed

Sizing: 951 lines. Non-engine logic is about 150 lines: RimplacePlan.Parse (a tab-separated line parser, ~110, reads a file path so not yet a pure function), the plan-centre offset arithmetic (15) and the unknown-directive tally (10). GenStep_RimplacePlan.ApplyPlan (~330) is spawn / terrain / roof / pawn calls in a fixed order: engine. Rejected as a kernel; the cheap win (parse from lines, round-trip against rimplace/plan.py `compile_flat`) is noted for whoever next touches the file.

## Lint
`python3 src/RimMandrake/Utils/lint_structureinjections_defs.py [--quiet]`: 1 def + 1 patch file, 11 classes, 1 ref, 1 field check, 1 setting: 0 ERROR, 0 WARN.
Shared-tool fix found here (lint_mod_defs.py): `GenStep_Whisper_NoOp` was WARNed as referenced by nothing, but it is named by the sibling mod `StructureInjectionsRUT/Defs/GenStepDefs_Whisper_Batch1.xml` (a framework mod's class used by a content mod). A class named in any other mod's Defs/Patches now counts as wired.
