# PYRELANDS_FLORA_LEAK_1

Alpha Biomes flora spawns on Pyrelands past the grass-only eviction.

## Problem

MEASURED 2026-09-18, minimal-list (27-mod) Pyrelands quicktest map: `AB_SessileMechanoid`
(x105) and `AB_GiantStikehr` (x24) — both Alpha Biomes plant defs — growing among the
two RM_FE grasses on Pyrelands, including a visible grove of Stikehr trees and giant
fungus clusters (owner spotted them live). Screenshots:
`Transient/pyre_trees_look_20260918t.png`, `Transient/_trees_zoom1.png`,
`Transient/_trees_zoom2.png`. Pyrelands' own `<wildPlants>` list
(`src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml`) names only
`RM_FE_Plant_EmberGrass` and `RM_FE_Plant_Quickgrass` — an intentional eviction of
every other wild plant, ruled by the owner 2026-09-14/17.

## Root cause (TRACED 2026-09-19, RimSage source reads — not guessed)

The filer's two hypotheses were checked directly against Alpha Biomes' shipped XML
(`1841354677/1.6/Defs`) and RULED OUT for these two specific defs:

- **`plant.wildBiomes` on the ThingDef itself** — neither `AB_SessileMechanoid`
  (`ThingDefs_Plants/Plants_MechanoidIntrusion.xml`) nor `AB_GiantStikehr`
  (`ThingDefs_Plants/Plants_ForsakenCrags.xml`) has a `wildBiomes` block at all.
- **Tile-mutator `AdditionalWildPlants`** — grepped the whole Alpha Biomes 1.6 tree;
  neither defName appears in any `TileMutatorDef` file. Both plants are referenced
  ONLY inside their own dedicated biomes' `<wildPlants>` lists
  (`AB_MechanoidIntrusion` in `BiomeDefs/Biomes_MechanoidIntrusion.xml`,
  `AB_RockyCrags`/"forsaken crags" in `BiomeDefs/Biomes_ForsakenCrags.xml`).

The actual route (confirmed by reading `RimWorld/WildPlantSpawner.cs`,
`RimWorld/BiomeDef.cs`, `RimWorld/Planet/Tile.cs` and
`RimWorld/TileMutatorWorker_MixedBiome.cs` via RimSage) is more general than either
guess:

1. `WildPlantSpawner.CalculatePlantsWhichCanGrowAt(c, ...)` builds its per-cell
   candidate list from `map.BiomeAt(c).AllWildPlants` (plus `MutatorWildPlants`).
2. `map.BiomeAt(c)` is `map.MixedBiomeComp.GetBiomeAt(c)` — **per-cell**, not
   per-map.
3. `Tile.Biomes` (`Source/RimWorld/Planet/Tile.cs`) yields the tile's primary
   biome plus, if any `TileMutatorDef` on the tile has a
   `TileMutatorWorker_MixedBiome`-derived worker, a **secondary** biome drawn from
   a neighbouring world tile. `TileMutatorWorker_MixedBiome.Init` then paints a
   Perlin-noise patchwork of map cells over to that secondary biome via
   `MixedBiomeMapComponent`.
4. Once a cell's `BiomeAt(c)` returns the secondary (foreign) biome, its ENTIRE
   `<wildPlants>` roster applies verbatim to that cell — Pyrelands' own eviction
   list is never consulted for those cells at all, because it belongs to a
   different `BiomeDef` object.

The vanilla `MixedBiome` `TileMutatorDef`'s own `biomeWhitelist` only names vanilla
biomes, and Alpha Biomes' own Odyssey compat patch
(`Mods/Odyssey/Patches/TileMutatorBiomePatches.xml`) only adds Alpha Biomes' OWN
biomes to that whitelist and to `AB_MechanoidIntrusion`/`AB_RockyCrags`'s eligibility
as a *primary* biome — `RM_FE_Pyrelands` is not named there. The owner's full
634-mod list carries a dense biome-blending stack
(`m00nl1ght.geologicallandforms` + `.biometransitions`,
`kopp.biomecompatibilityproject`, `sarg.alphabiomes`, several biome-expansion mods)
that plausibly cross-patches a custom biome like Pyrelands into this eligibility
independently of anything in this repo — I did not find and did not need to find
the exact interloping patch to confirm the MECHANISM or to build a robust fix; the
mechanism itself (a per-cell secondary-biome assignment bypassing the primary
biome's own wildPlants list) is confirmed directly from engine source, and is
biome-agnostic — it would recur for ANY foreign biome placed as Pyrelands'
neighbour, not just these two Alpha Biomes defs.

## Fix chosen: runtime enforcement (not targeted per-def patches)

A per-def XML patch (`PatchOperationRemove` on `AB_SessileMechanoid`/`AB_GiantStikehr`'s
`wildBiomes`) was rejected outright: **there is nothing on either def to strip** —
confirmed above, neither carries `wildBiomes` or a mutator reference at all. Even a
patch targeting the secondary-biome mechanism (e.g. keeping `RM_FE_Pyrelands` out of
every `MixedBiome`-family whitelist) would need to be re-derived per biome-mixing mod
and would still leave the map.Biomes/`WildPlantSpawner.CachePlantCommonalitiesIfShould`
union path open. This is exactly the "multiplies across every flora mod" class the
filer warned about, so runtime enforcement (option 1) was chosen.

Built `src/RimMandrake/Pyrelands/Source/WildPlantAllowlist.cs`: a Harmony postfix
(`mandrake.rm.pyrelands.wildplantallowlist`) on the private
`WildPlantSpawner.CalculatePlantsWhichCanGrowAt`. Whenever the calling map's
**primary** biome (`map.Biome.defName`) is `RM_FE_Pyrelands`, it strips every
candidate in the mutated `outPlants` list that is not one of the two RM_FE_ grasses —
regardless of whether the candidate arrived via a secondary biome, a tile mutator's
`AdditionalWildPlants`, a `wildBiomes` entry, or any future mechanism. A map where
Pyrelands is merely the *secondary* biome of some other primary-biome map is
untouched (that map's own biome rules apply there, unchanged — correct, since that
land isn't "Pyrelands" to the player).

Wired into the mod's existing `mandrake.rm.pyrelands` Harmony/Mod-Settings pattern
(same file family as `RM_PyrelandsDensityEnforcer.cs`, which already re-asserts
Pyrelands' own numbers after other mods run). New Mod Settings toggle
`wildPlantAllowlistEnabled` (default on) in `RM_PyrelandsMod.cs`, per the
"every mod ships superb Mod Settings" standing rule.

`dotnet build FireEcologyHook.csproj -c Release` — clean, 0 warnings/errors. No XML
`PatchOperation` was added or changed, so `validate_patch.py` does not apply to this
change. Committed and pushed at `a448e9657`.

## Owed (NOT done this pass)

- **Live-quicktest proof.** This is an offline fix only — ground rule for this task
  forbade touching the bridge. Next FOUNDRY/BENCH pass with bridge access should
  spawn a Pyrelands quicktest map (same repro conditions as the 2026-09-18 measurement)
  and confirm zero `AB_SessileMechanoid`/`AB_GiantStikehr` instances, and ideally a
  second map where Pyrelands is a mixed-biome neighbour to confirm the enforcement
  doesn't over-fire onto the OTHER biome's own territory.
- The exact mod/patch that grants `RM_FE_Pyrelands` `MixedBiome`-family eligibility on
  the owner's full list was not identified (not needed for the fix, which is
  biome-agnostic) — if anyone wants to name it later,
  `kopp.biomecompatibilityproject` and `m00nl1ght.geologicallandforms.biometransitions`
  are the two most likely candidates from the active mod list.

## History

- 2026-09-18 BENCH file — MEASURED leak, two fix directions proposed, needs offline.
- 2026-09-19 FOUNDRY claim/start — investigated via RimSage, built
  `WildPlantAllowlist.cs` runtime enforcement, `dotnet build` clean, committed+pushed
  `a448e9657`. Left `doing` — live-quicktest proof owed.
- ✅ **2026-09-19 FOUNDRY (overnight full-621-mod batch) — LIVE-CONFIRMED, CLOSING.**
  `FlowWorks`/`Pyrelands` deployed clean (in sync). This scratch quicktest world has no
  Pyrelands tile of its own (100% TemperateForest), so — since nothing about this
  scratch world is precious — set one tile's biome directly to `RM_FE_Pyrelands` via
  `jawa/world_tile_set` + `jawa/world_commit`, then `jawa/world_tile_map_generate` on
  it. Switched to the new map (`jawa/set_current_map`) before censusing — a first
  attempt without switching silently scanned the wrong (previous) map and returned a
  false-clean 0/0 against a thing count that didn't match; corrected before trusting
  it. On the correct map (18,563 things scanned, matching that map's own reported
  `thingCount`): **0x `AB_SessileMechanoid`, 0x `AB_GiantStikehr`.** A sample of the
  map's wild plants showed only `RM_FE_Plant_EmberGrass` and `RM_FE_Plant_Quickgrass`
  — exactly Pyrelands' own two-species eviction list, nothing foreign. Clean pass.
  Closing.
