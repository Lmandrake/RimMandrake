# Decision strings, written before this load — BENCH, 2026-09-05 (full-list Ninefold-proof load)

## Ninefold hook proof — NINEFOLD hooks on-screen firing (this load's purpose)
DevMode must be ON: every hook routes through `ApplyDelta`, which logs only under
`Prefs.DevMode`. Expected-present string per hook, all matching
`[Ninefold] <god> satiation ±N.N (<reason>) -> ...`:
- kill/battle: reason `melee, the close exposed war` (KillManner) — fires on REAL
  `Pawn.Kill`, which jawa/damage bypasses; prove via an actual fight.
- explosion: reason starting `an explosion` (three variants).
- trade: reason `trade completed`.
Absence after a real fight with DevMode on = hook genuinely not attached (last
session could not distinguish this from bridge-bypass; this load can).
Baseline: research hook already proven live last session.

## Full-list quicktest crash (attempt LAST — may kill the session)
`start_debug_game` on the full list crashed unexplained. Signature to capture:
whatever the log's final lines are at crash; compare against a clean load-to-menu
(known fine). Run only after the Ninefold proof is banked.

# Prior deploy's strings (four assemblies) — still valid, kept below — FOUNDRY, 2026-09-05

Full 595-mod list. Four assemblies changed this deploy: JawaBench.BridgeTools,
RustChrome, StructureInjections, Inhabited. Batched per doctrine's "distinguishable
failure signature per assembly" waiver.

## JawaBench.BridgeTools — TILEGEN_SILENT_REUSE_1 + DEV_LOG_AUTOOPEN_SUPPRESS_1
- Signature if broken: any Harmony patch exception naming `JawaBenchLogAutoOpenSuppress`
  or a `TypeLoadException`/`MissingMethodException` referencing `JawaBenchSocietyTools`.
- Live test (bridge, post-load): two `jawa/world_tile_map_generate` calls at two
  distinct, confirmed-empty tiles. Decide by:
  - Second call REFUSES with a message naming both tiles → guard works, underlying
    bug still open (expected, not a failure).
  - Second call SUCCEEDS and `jawa/map_info`/`rimworld/get_game_info` show a real,
    distinct second map (`mapCount` increments, `map.Tile` matches request) → bug
    narrower than the trap suggested; re-run once more before believing it.
  - Second call SUCCEEDS but the map is still tile 701's (silent reuse persists) →
    guard did not fire; regression in the guard itself.

## RustChrome / StructureInjections / Inhabited
- No live behavior change intended this pass (rebuild only, no source edits
  since last deploy — confirms deployed bytes match repo HEAD).
- Signature if broken: any `Def.ConfigErrors()`/`^Config error in` line naming
  `RimMandrakeRustChrome`, `RimMandrakeStructureInjections`, or `Inhabited`
  assemblies, or a Harmony patch failure naming any type in them.

## Baseline
`harvest_log.py` on the last known-good full load: 0 dead mods, standing
crossref/patch-no-op counts as recorded in its own baseline file — read those,
don't requote from memory.
