## spec

`FLUID_CANAL_FLOOD_TUNING_GAPS_1` findings 1/2/3 were fixed in code and
compile clean, but the mod is NOT deployed and nobody has watched a flood
recede or a floor come back. This is that watch — a quicktest, not the
campaign, and not a cold load: the 13-mod minimal list is enough. Requires
Odyssey active and `mandrake.rm.fluidcanals` deployed.

Setup: place `RM_FluidSpring_Test`, build a concrete floor on a cell next to
it, then `Actions\RMFluidCanals\Instant-dig canal at cell` adjacent to the
spring. Read cells with `Actions\RMFluidCanals\Report cell (RAW)`.

## verify

1. **Recoverable (the owner's ruling, finding 1).** A flooded cell reports
   `terrain=ShallowFloodwater tempTerrain=ShallowFloodwater underneath=<the
   cell's real terrain>`. On the concrete cell `underneath=Concrete` is the
   whole proof. FAIL if `tempTerrain=none` (the fluid went to the permanent
   layer) or `underneath` reads the floodwater. Then let it drain
   (`floodedTicks` 300000 — dev-mode tick advance) and confirm the concrete
   is back and the cell is re-diggable.
2. **Rate (finding 3).** The flood advances ~1 tile per 60 ticks: a 60-volume
   spring covers ~60 tiles in ~1.5 in-game hours. FAIL if it is one tile per
   in-game hour (the old rate-divisor behaviour).
3. **Boxed-in expiry (finding 2).** Wall a spring in so the flood is boxed
   after a few tiles. The `Flood_FluidCanal` must be GONE by the
   `expiresAtTick` its own report prints (the report also prints `nowTick`),
   and the tiles it did place must still drain on schedule afterwards — the
   removals live on the map's `TempTerrainManager`, not on the flood.

## note 2026-09-03 (BENCH)

Deploy state measured: `FluidCanals` repo↔game **in sync (9 files)** but
`mandrake.rm.fluidcanals` is **not in the active ModsConfig** — the live session
(full 578 list, gravship_scratch_b) cannot run this. Rides the next game-DOWN:
swap to the minimal list WITH Odyssey + fluidcanals enabled (`modset_builder.py`),
22 s load, then the three verify steps. Do not spend a full-list session on it.

## criteria

All three read as expected on a live map, or the reading that failed is
written back into `FLUID_CANAL_FLOOD_TUNING_GAPS_1`'s own record with what it
actually did.

## RESULT 2026-09-04 (BENCH) — all three readings PASS, live

Run on the 21-mod MINIMAL list, dev quicktest (tile 82716, map 0), via the new
companion tools `canal_dig` / `canal_cell_report` (criteria-(b) route —
`prove_fluid_canal.py` in `src/RimMandrake/bridgetools/` is the harness):

1. **Recoverable — PASS.** Flooded concrete cell read
   `terrain=ShallowFloodwater tempTerrain=ShallowFloodwater underneath=Concrete`
   (flooded sand read `underneath=Sand`). After a clock jump past
   `spawnedTick + FloodingTicks + floodedTicks(300000)`, every flooded cell
   drained: concrete back to `Concrete`, sand to `Sand`, `tempTerrain=none`,
   and the dug channel still `RM_Channel_Empty`.
2. **Rate — PASS.** 9 tiles at tick 536, 33 at tick 1988 from a tick-1 dig —
   ~1 tile per 60 ticks, matching `ticksPerTile=60`. The old rate-divisor
   behaviour (1 tile per 2500 ticks) is gone.
3. **Boxed-in expiry — PASS.** Spring dug inside a 5×5-interior walled room:
   flood stalled at 21 tiles with 39.0 volume stranded, and the
   `Flood_FluidCanal` was GONE by tick 954576 against its own
   `expiresAtTick=954533` (≤ one poll interval). Its placed tiles remained
   flooded after the flood's death and drained on schedule afterwards — the
   removals live on the map's TempTerrainManager, as designed.

Traps hit and worked around, for whoever re-runs this:
`Dialog_NamePlayerFactionAndSettlement` (forcePause) froze the sim while every
bridge call kept succeeding — close it by clicking its OK via
`rimworld/click_ui_target` (plain window-close re-queues it). And
`jawa/set_game_speed` takes 'Normal'/'Superfast' strings, not integers.

## note 2026-09-04 (BENCH, relaying FOUNDRY's live-check attempt — CORRECT_FLUID_CANAL_1)

1. **The 2026-09-03 deploy/enable blocker is resolved.** Swapped to the 21-mod
   MINIMAL list (`modlist_swap.py --minimal --apply`) — it already includes
   Odyssey + `mandrake.rm.fluidcanals`, confirmed by reading
   `infrastructure/state/modlists/ModsConfig.MINIMAL.xml` directly. Loaded clean
   via Steam launch, bridge up, real playable quicktest colony (3 colonists).
   Spawned `RM_FluidSpring_Test` (`rimworld/spawn_thing`) and painted `Concrete`
   on the adjacent cell (`jawa/set_terrain`) — both succeeded. `jawa/get_defs`
   confirmed `RM_FluidSpring_Test` resolves with `CompProperties_FluidReservoir`
   attached: the mod's defs and comp declaration are genuinely live.
2. **Narrower blocker: `RMFluidCanals`'s debug actions never appear in the live
   debug-action tree.** `rimworld/list_debug_action_children` on `Actions`
   returned 350 children across 20 categories — no `RMFluidCanals` at all, in
   the same load where `RimMandrake.Inhabited`'s debug actions appeared and
   were successfully driven (confirmed via Player.log). Both debug classes are
   plain `public static class` with `[DebugAction]` static methods, same shape.
3. **The `allowedGameStates = PlayingOnMap` lead is now RULED OUT** (BENCH,
   2026-09-04, source read): `IsAllowedInCurrentGameState` only gates
   `DebugActionNode.VisibleNow`, and `DebugTabMenu_Actions.InitActions` adds
   every `[DebugAction]` to the tree unconditionally — and the round-2 control
   showed Inhabited's own `PlayingOnMap` actions registering fine in the same
   load. Also refuted offline today: the `ReflectionTypeLoadException`
   partial-recovery path in `GenTypes.AllTypes` (would drop a static class with
   no static initializer) — an unfiltered grep for "Exception getting types in
   assembly" across all three saved session logs returns 0 hits.
4. **`Player.log` has zero lines mentioning FluidCanals, CompFluidReservoir, or
   Flood_FluidCanal** (literal grep, `MEASURE_ALLOW_SCAN=1`) — consistent with
   "loaded fine, never touched"; def/comp resolution is evidence for that.
5. **None of this item's three verify steps has run** — blocked before the
   first (`Actions\T: Instant-dig canal at cell` could not be invoked at all).

Root cause remains unnamed (that hunt is `FLUID_CANAL_DEBUG_SURFACE_1`, which
now needs a live reflection probe, not more reading). This item unblocks by the
criteria-(b) route instead: a companion `[Tool]` that drives the dig's two
effects (`terrainGrid.SetTerrain` + `CompFluidReservoir.Notify_CanalCellOpened`)
and the RAW cell report directly, bypassing the debug-action surface.

## note 2026-09-03 (BENCH, after the blocked run)

Spec correction for whoever runs this once FLUID_CANAL_DEBUG_SURFACE_1 lands:
the debug-action paths in `## spec` use the wrong grammar. Category is metadata,
not a path segment, and ToolMap actions get a `T: ` label prefix
(Source/LudeonTK/DebugTabMenu_Actions.cs:52-55). Correct paths:
`Actions\T: Instant-dig canal at cell` · `Actions\T: Report cell (RAW)`.
Everything else about the run is proven ready — deploy in sync, assembly loads,
minimal-list swap and restore clean. Session log:
`Transient/Player_log_20260903_fluidcanal_livecheck.log`.
