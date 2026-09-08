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
- [ ] The crater tile set is exactly the propane lake's frozen footprint from
  `LIQUID_BIOMES_MAP_1` — this item is BLOCKED until that footprint is frozen (owner
  ruling by render, per that item's own open status). Do not guess a footprint to
  unblock early.
- [ ] The hook fires exactly once per ignition event (idempotent — re-entering an
  already-cratered lab must not re-trigger the mutation).
- [ ] Works whether the map is loaded or not at the moment of ignition (the mutation
  targets the WORLD tile, not just the local map state).

## Watch out
⛔ Blocked on `LIQUID_BIOMES_MAP_1` — do not start the C# hook until that item's
propane-lake tile footprint is owner-ruled and frozen. Building against a guessed
footprint risks the exact "patch a curated artifact via reallocation" trap this
project has hit before (`patch-a-curated-artifact-never-reallocate` memory) — re-doing
the tile set later would churn work that should have waited.
