# LOAD_GAME_READY_MAPGEN_CRASH_1 — `rimworld/load_game_ready` also hits the map-gen crash

## why this exists

Discovered live 2026-09-27 while trying to run `GREENTIDE_PLANT_SIGHT_BLOCK_ENGINE_1`'s
own deterministic dev-action probe. `DEBUG_GAME_READY_WORLDUI_CRASH_1` (closed) already
proved `rimworld/start_debug_game_ready`/`start_debug_game` are broken on any mod list
because vanilla `Verse.Root_Play.SetupForQuickTestPlay()` throws during world-feature
path-cost generation. **This item is the same underlying crash, reached from a different,
previously-assumed-safe tool.**

## what was measured

On a fresh cold load of the full 629-active-mod list (launched via `steam.exe -applaunch
294100`, `runInBackground: True`, RimBridge answering), `rimworld/load_game_ready` was
called against two different existing saves:

- `CANONICAL_ASHKARR_START_2026-09-12` (`ignoreModCompatibility: true`) — compatibility
  reported `missing_mods` (2 missing: `mandrake.rut.rotsporekit`, `mandrake.rut.lanterndeeps`
  — both apparently retired/merged mods, not present anywhere in the current 629-mod list).
  Load queued, `longEventPending` went true then false, `hasCurrentGame` stayed false for
  the full 150s wait plus 4 more minutes of polling on fresh connections. RimWorld's own
  window showed a modal: **"Error while generating a map / An error occurred while
  generating a new map. See error log for more information."**
- `ASHKARR_LABELSIZES_DRAWCENTERFIX_2026-09-26` (also `ignoreModCompatibility: true`,
  also `missing_mods` — 3 missing, same two RimUtinni mods plus `biomesteam.biomescore`)
  — **the identical dialog fired again**, seconds after the load was queued.

`Player.log` for both attempts shows `Verse.GameDataSaveLoader+<>c__DisplayClass30_0.
<LoadGame>g__PreLoadAct|0()` queued via `Verse.LongEventHandler.RunEventFromAnotherThread`
(the real save load, correctly invoked) **alongside** `Verse.Root_Play.SetupForQuickTestPlay()`
also queued via `RunEventFromAnotherThread` around the same moment, both from the bridge
thread. The quicktest path throws (this run: a `NullReferenceException` inside
`RimWorld.DrugPolicy.InitializeIfNeeded`'s array sort comparer, triggered through a
Harmony prefix from `Mlie.YayosCombat3` — a *different* concrete exception than
`DEBUG_GAME_READY_WORLDUI_CRASH_1`'s `WorldPathGrid` one, but the same
`SetupForQuickTestPlay`-during-`RunEventFromAnotherThread` shape, and equally fatal to
reaching a playable map) as a repeating uncaught async exception, and the modal above is
RimWorld's own generic "map generation failed" handler catching it.

**Not caused by the sight-block patch under test**: `Player.log`'s own LoadTracer entry
for `RimMandrake.CreatureBehaviors.RM_SightBlockPatches`'s static constructor
(`ctor 1464/1557`) has no following "Error in static constructor" line — the new Harmony
patches applied cleanly. The 4 genuinely dead mods in this log
(`AlphaMemes.StaticCollections`, `BiomeCompatibilityProject.StartUp`, `GeneticRim.Core`,
`JumppackForMeleeAI.JumppackForMeleeAI`) are unrelated third-party mods, not ours.

## best-guess mechanism (unverified further — out of scope for this note)

`rimworld/load_game_ready`'s internal implementation appears to fall back to (or run
alongside) a `SetupForQuickTestPlay`-style bootstrap when the save's recorded mod list
doesn't exactly match the live one (`compatible: false`), even with
`ignoreModCompatibility: true` honoured for the *save load itself*. Both saves tried here
carry the same 2-3 persistently-missing RimUtinni mods, so **whether a save whose mod list
matches EXACTLY would skip this path entirely is UNMEASURED** — no such save was
available this pass (`rimworld/get_save_info` is not a registered tool, so compatibility
can't be cheaply pre-checked without a real load attempt).

## impact

Blocks `GREENTIDE_PLANT_SIGHT_BLOCK_ENGINE_1`'s live dev-action probe/stress verification,
and blocks any other FOUNDRY workflow that opens with `load_game_ready` against an
existing save on the full mod list while that save's recorded mods don't exactly match
live — which per the two saves tried here may be the common case, not the exception.

## NEXT

- Get (or make) a save whose `recordedModCount`/`missingModCount` is an exact match against
  the live 629-mod list, retry `load_game_ready` against it, and see whether the map-gen
  crash still fires. That isolates "mismatch triggers the quicktest fallback" from "the
  fallback fires unconditionally."
- If it still fires on an exact-match save, this is the same root cause as
  `DEBUG_GAME_READY_WORLDUI_CRASH_1` reached through a second, previously-trusted door —
  worth escalating the RimSage/decompile investigation to `load_game_ready`'s own C#
  implementation (RimBridge's own code this time, not vanilla) to find what triggers the
  `SetupForQuickTestPlay` call.
- Until resolved, no live-bridge verification of anything can safely assume
  `load_game_ready` reaches a playable map on the full list — budget for this dialog and
  have a dismiss-and-report plan (`system_click.py` on the modal's OK button, then
  `system_screenshot.py` to confirm recovery to the main menu) rather than treating a
  `load_game_ready` timeout as inconclusive-but-safe.
