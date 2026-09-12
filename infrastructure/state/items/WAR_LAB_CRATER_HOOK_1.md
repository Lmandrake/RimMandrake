# WAR_LAB_CRATER_HOOK_1 — ignition-to-crater world-tile mutation C# hook

Split from `ANCIENT_WAR_LAB_1` (2026-09-08, FOUNDRY): the war lab's dungeon build
(shielding, `AA_Slurrypede` lab fauna, mechanoid/ancient guardians, the containment
core) is offline KCSG authoring with a proven pipeline. This item is the other half —
the "plentiful ways to permanently change the map" ending (`the_propane_lakes.md` §8)
— which is genuinely new engineering, not a config task.

## spec
- **What it does**: an in-game ignition event (thruster contact, a dropped reactor
  core per `wasteland.md` §10 option 4, or a deliberate charge) at the war lab's map
  flips the propane lake's worldmap tile(s) from `RUT_PropaneLake` to a crater biome/
  terrain state, permanently, surviving save/load.
- **Proven sequence to call in-process** (already validated externally via the bridge,
  `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchWorldTools.cs`):
  `jawa/world_tile_set` writes `Tile.PrimaryBiome` (public setter, confirmed via
  decompiled `Source/RimWorld/Planet/Tile.cs`); `jawa/world_commit` runs
  `WorldDrawLayer_{Terrain,Hills,Landmarks,Roads,Rivers}.RegenerateNow`,
  `FastTileFinder.DirtyCache`, `WorldPathGrid.RecalculateLayerPerceivedPathCosts`,
  `WorldReachability.ClearCache`. `Tile.ExposeData()` Scribes plain values — no
  special-casing blocks a runtime write from surviving a save.
- **New work**: a `QuestPart`/`CompDestroyed`/`GameComponent` hook, fired by the
  ignition event on the war lab's local map, that calls that SAME sequence
  in-process (not over the bridge RPC — the bridge cannot fire itself from an
  in-game trigger). No runtime precedent for an in-process per-tile biome rewrite
  exists yet in this codebase or in vanilla (the only vanilla precedent is
  `WorldPollutionUtility.PolluteWorldAtTile`, a plain float, not a biome swap).
- **Scope boundary**: local-map spectacle (fire, terrain swap, roof breach at the lab
  itself) is the war lab dungeon's own build, not this item's — this item is the
  worldmap-tile side only, and must not be faked independently of it (a permanent
  discrepancy between what the map shows and what the save holds is worse than
  neither).

## verify
- [ ] Ignition trigger on a quicktest map flips the correct worldmap tile(s) to the
  crater state.
- [ ] Crater state persists across a save/load cycle.
- [ ] `world_commit`'s cache regeneration confirmed correct after an in-process write
  (not just the externally-driven bridge sequence) — screenshot of the world map
  before/after.
- [ ] No other tiles affected; the tile set matches the propane lake's real footprint,
  not a guessed rectangle.

## criteria
- [x] The crater tile set is exactly the propane lake's frozen footprint — resolved:
  `LIQUID_BIOMES_MAP_1` closed 2026-09-07 leaving this footprint deliberately
  unpainted, but it WAS owner-ruled and painted the next day (commit a5020486e,
  2026-09-08, "RUT_PropaneLake paint recorded DONE"; live/frozen CSV confirms 57
  tiles, water=1, Umbra 29/Ammonia Flats 28). The item text below was stale — this
  block was cleared 2026-09-11 (`rimflow unblock`). The mutation derives the tile
  set live from the current `RUT_PropaneLake` footprint rather than a hardcoded
  snapshot, so it tracks whatever that def covers at ignition time.
- [ ] The hook fires exactly once per ignition event (idempotent — re-entering an
  already-cratered lab must not re-trigger the mutation).
- [ ] Works whether the map is loaded or not at the moment of ignition (the mutation
  targets the WORLD tile, not just the local map state).

## Watch out
✅ Was blocked on `LIQUID_BIOMES_MAP_1`'s propane-lake tile footprint — resolved,
see `## criteria` above. Building against a guessed footprint risked the exact
"patch a curated artifact via reallocation" trap this
project has hit before (`patch-a-curated-artifact-never-reallocate` memory) — re-doing
the tile set later would churn work that should have waited.

## XML wiring (FOUNDRY, 2026-09-12 — reclaimed from stale-queue audit)

The C# (`CompIgniteCraterOnDestroy`/`GameComponent_WarLabCrater`/
`WarLabCraterMutation`, commit `5e2f5084e`, marked CLEAN `f4c56cd19`) was built and
reviewed 2026-09-11 but never attached to any def — the 2026-09-11 note is explicit:
"not wired to any def yet, no such reactor-core thing exists." No candidate def
existed anywhere in the war lab's authored XML (`RUT_WarLabArchive`,
`RUT_WarLabContainmentCell` are inert narrative props, not ignition sources), so
this pass authored the missing def rather than guess an existing one:

- **New**: `src/RimUtinni/StructureInjectionsRUT/Defs/WarLab/ThingDefs_Buildings/RUT_WarLabReactorCore.xml`
  — `RUT_WarLabReactorCore`, the "dropped reactor core" ignition source
  `wasteland.md` §10 option 4 names by name. Modeled on vanilla `AncientGravReactor`
  (art reuse, `CompProperties_Explosive` so damage/heat can detonate it), at the
  narrative-anchor (1,1) footprint convention `RUT_WarLabArchive`/
  `RUT_WarLabContainmentCell` already use. Carries
  `RimMandrake.Utinni.StructureInjectionsRUT.CompProperties_IgniteCraterOnDestroy`,
  so any destruction path (its own explosion included) fires
  `WarLabCraterMutation.Ignite()` via `PostDestroy`.
- **Validated**: `validate_patch.py --live` against the 2026-09-12T07:12:37Z live
  dump (592 mods, 69709 defNames) plus a fuller pass with `--defs` over
  RimWorld/Data + Workshop + Mods and `--mods-config`: 0 errors. Two expected,
  non-actionable warnings: the vanilla `texPath` can't be confirmed loose-file-side
  (Unity asset bundle, matches `AncientGravReactor`'s own def verbatim) and the
  custom `Class=` can't be resolved by a static XML scan (it's this mod's own
  compiled DLL — confirmed public via reading the C# source directly).
- **Deployed**: `deploy_custom_mods.py --apply` — `+ Defs/WarLab/ThingDefs_Buildings/RUT_WarLabReactorCore.xml`,
  verified in sync. Mod is currently not enabled in the live `ModsConfig.xml`
  (minimal-list regime); deployment does not depend on that.

**NOT DONE — honestly owed, needs a live bridge quicktest this pass did not have**:
- The def is not yet placed via any GenStep/SymbolDef into the war lab's KCSG
  layout, nor given a way to reach the player's hands (no recipe, no loot
  placement, no quest reward) — that staging belongs to whoever finishes the war
  lab's own local-map ending (`ANCIENT_WAR_LAB_1`), not this item's scope.
- Every `## verify` box below is still unchecked: ignition-fires-mutation on a
  quicktest map, save/load persistence, `world_commit`'s in-process cache-regen
  confirmed by screenshot, and confirming no tile outside the propane lake's
  footprint is touched. None of this can be honestly claimed from an offline pass —
  filing `rimflow block` rather than `close` for exactly this reason.
