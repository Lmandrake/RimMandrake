# CORRECT_FLUID_CANAL_1

Correction/addendum to `FLUID_CANAL_FLOOD_LIVE_CHECK_1`, filed by FOUNDRY after a
live-check attempt on 2026-09-04. Not a replacement — the parent item's three
verify steps are still unattempted; this only updates what's blocking them.

## Spec

Write the following into `FLUID_CANAL_FLOOD_LIVE_CHECK_1`'s own file as a dated
note (FOUNDRY can't write it directly — cross-seat ownership):

1. **The 2026-09-03 deploy/enable blocker is resolved.** Swapped to the 21-mod
   MINIMAL list (`modlist_swap.py --minimal --apply`) — it already includes
   Odyssey + `mandrake.rm.fluidcanals`, confirmed by reading
   `infrastructure/state/modlists/ModsConfig.MINIMAL.xml` directly. Loaded
   clean via Steam launch, bridge up, real playable quicktest colony (3
   colonists). Spawned `RM_FluidSpring_Test` (`rimworld/spawn_thing`) and
   painted a `Concrete` floor on the adjacent cell (`jawa/set_terrain`) — both
   succeeded. `jawa/get_defs` on `RM_FluidSpring_Test` confirmed it resolves
   with `CompProperties_FluidReservoir` attached, so the mod's defs and comp
   declaration are genuinely live in this session.

2. **New, narrower blocker: `RMFluidCanals`'s debug actions never appear in the
   live debug-action tree.** `rimworld/list_debug_action_children` on path
   `Actions` returned 350 children across categories `AlienRace, Anomaly,
   Autotests, General, Generation, Ideoligion, Incidents, KCSG, Lighting, Map,
   Mechanoid, More debug actions, Music, Pathing, Pawns, Pipe System, Quests,
   RimMandrake.Inhabited, Sound, Spawning` — no `RMFluidCanals` category at all,
   in the same load where `RimMandrake.Inhabited`'s own debug actions DID
   appear and were successfully driven (`Create place at current tile`, `Stuff
   roster (3 pawns)`, confirmed via Player.log). Both
   `FluidCanalsDebugActions`/`DebugActions_Inhabited` are plain `public static
   class` with `[DebugAction]`-attributed static methods — same shape.

3. **One structural difference spotted, not confirmed as the cause:**
   `FluidCanalsDebugActions`'s two actions both declare `allowedGameStates =
   AllowedGameStates.PlayingOnMap`; Inhabited's use the looser `Playing`. The
   bridge's own diagnostic (`rimworld/list_debug_action_children`'s `state`
   block) read `programState: "Playing"`, `hasCurrentGame: true,
   currentMapReady: true` at the time — which reads as satisfying
   "PlayingOnMap" too, so this is not a confirmed explanation, just the one
   lead not yet chased down.

4. **`Player.log` has zero lines anywhere mentioning FluidCanals,
   CompFluidReservoir, or Flood_FluidCanal** (checked with a literal grep,
   `MEASURE_ALLOW_SCAN=1`) — consistent with either "the assembly never
   loaded" or "loaded fine, never touched" (the def/comp resolving is evidence
   for the latter, not proof).

5. **None of the item's three verify steps ran** — blocked before the first
   one (`Actions\T: Instant-dig canal at cell` could not be invoked at all).

## Verify

The note lands in `FLUID_CANAL_FLOOD_LIVE_CHECK_1.md` (a dated section, not a
rewrite of the existing content) and its `blocked:` reason in the queue reflects
the narrower blocker (debug-action visibility, not deploy/enable) rather than the
stale 2026-09-03 one.

## Criteria

Whoever picks this up next (BENCH, or FOUNDRY once reassigned) either: (a)
figures out why `RMFluidCanals`'s debug actions aren't listed — check
`allowedGameStates` first since it's the one lead — and fixes it, or (b) finds a
non-debug-action route to drive `Instant-dig canal at cell`'s two effects
(`map.terrainGrid.SetTerrain` + `CompFluidReservoir.Notify_CanalCellOpened`)
directly, e.g. via a new companion `[Tool]` method
(`rimbridge-companion` skill) if this keeps coming up.

## Watch out

- The quicktest map used for this attempt is on world tile 701 (Temperate
  Forest, Mountainous) via `jawa/world_tile_map_generate` — NOT the crashlanded
  colony's own tile (45577). Both maps coexisted in the same session; if
  resuming this test, check `jawa/map_info` for which map is actually
  "current" before spawning anything — the bridge's notion of "current map"
  did not always match expectations this session (see the
  `jawa/world_tile_map_generate` trap filed in
  `skills/rimbridge/references/traps.md` 2026-09-04, from a DIFFERENT test
  in the same load round — read it before trusting a second
  `world_tile_map_generate` call).
- Odyssey + fluidcanals were both freshly enabled together with several other
  mods on the same MINIMAL swap; if debug-action absence turns out to be a
  load-order or mod-interaction issue rather than the `allowedGameStates`
  lead, it hasn't been isolated against a smaller list yet.
