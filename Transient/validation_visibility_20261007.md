# Visibility validation, 2026-10-07 - NO LINT POSSIBLE, NO KERNEL (under the ~800-line bar), nothing committed

Sizing: 1031 lines, ~150 of them non-engine: the band ladder, Adjust clamp, launch reset clamp, tile-memory decay (0.5^seasons) and the threat curve, already extracted and covered by `Source/SelfTest/Program.cs` + `Utils/selftest_colony_visibility.py` (passes in run_selftests). The remainder is Harmony patches on IncidentWorker.TryExecute / GravshipUtility and a settings screen.

## Lint
Not applicable: the mod ships no Defs/Patches XML, so `lint_mod_defs.py` returns UNMEASURED (found xml 0). No wrapper written; a wrapper that can only say UNMEASURED would be noise.
