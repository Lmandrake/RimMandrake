# 10 — MineralsFramework retirement (`MINERALS_FW_RETIRE_ITS_MAPGEN_IN_HOUSE`)

Owner, by card 2026-10-19: *"Pass it, retire that mod, and ensure we create whatever it did within our own holdings."*

**Verdict: none of our mods uses anything MineralsFramework does. Nothing is rebuilt in-house; the item
is a retirement of four mods together.** All findings measured 2026-10-19 (offline; game up, untouched).

## What the mod adds

`zacharyfoster.mineralsframework`, workshop 3562390384 (`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3562390384`).
Its own About.xml: *"This mod does not add any content to the game, but provides a framework for other mods."*

| piece | what it does |
|---|---|
| `MF_GenStep_Rocks` (order 300), `MF_GenStep_Ice` (750) | patched into **every** BiomeDef's `extraGenSteps` (`Patches/AddRockGeneration.xml`); each loops over `ThingDef_StaticMineral` defs **from other mods** and spawns them |
| `MF_GenStep_RemoveChunks` (980) | deletes vanilla starting rock chunks; added to biomes only by Minerals Rock's `RemoveChunks.xml` |
| defs | abstract parents only (`MF_StaticMineralBase`, `MF_DynamicMineralBase`, `BigMineralBase`, `MF_*ChunksBase`, `MF_StoneBlocksBase`), research tag `TribalOnlyStart` + two abstract research bases. No concrete ThingDef. |
| Harmony | one transpiler on `World.NaturalRockTypesIn`: rock types per tile `Rand.RangeInclusive(2,3)` → setting `terrainCountRangeSetting`, default **1..4** |
| C# | `StaticMineral`/`DynamicMineral`/`BigMineral` classes (growth, snowy texture, drop tables) used by the three content mods |

**The NRE** (02_world_pipeline.md line 198): `StaticMineral.settlementDistProbFactor` reads
`s.Faction.IsPlayer` for every world Settlement; a settlement with a null faction throws. It fires
inside the GenStep, i.e. on every map, for any spawning mineral def.

The concrete content all lives in its three hard dependants (each `modDependencies` → mineralsframework,
so they must go with it), all four active in the live ModsConfig (parsed, 498 active):

| mod | content | registry status before this item |
|---|---|---|
| Minerals Rock `zacharyfoster.mineralsrock` (3562391080) | replaces mountain rock with Solid/Weathered/Hewn/Boulder/Passable forms, ore veins, `MR_` basalt | PHASE-OUT (01_mod_inventory) |
| Minerals Frozen `zacharyfoster.mineralsfrozen` (3562390973) | snow drifts, ice walls, ice/snow blocks | PHASE-OUT (01_mod_inventory) |
| Minerals Sparkle `zacharyfoster.mineralssparkle` (3562390730) | gem crystals, rough/cut gems, fossils, trophy research facilities | MOVE-TO-SHIP / droppable with the framework (09_second_look) |

No other workshop mod's About.xml names `zacharyfoster.*`.

## What of ours uses it — nothing (grep evidence)

- `src/` (`*.xml *.cs *.py *.json *.md`, excluding `northstar/` run records): **0 hits** for
  `zacharyfoster`, `MineralsFramework`, `ThingDef_StaticMineral`, `MF_GenStep_*`, every MF abstract
  parent, and **every defName of Rock/Frozen/Sparkle** (65+ names incl. `RoughGem`, `CutGem`,
  `*Crystal`, `*Fossil*`, `Solid*`, `Weathered*`, `Hewn*`, `MR_*`, `MF_IceBlocks`, `ZF_SnowDrift`).
  The only `MF_` hits are `MF_BasicFurniture`/`MF_ModernFurniture`/`MF_RoyalFurniture`/`MF_WasteDisposal`
  in `src/RimUtinni/ResearchRetag/Patches/RUT_ResearchTabAssign.xml` — another mod's research, not this one.
- Remaining `zacharyfoster` hits are records, not dependencies: northstar result JSONs (mod lists at run
  time), `src/Jawa/ideoligion/MandrakeJawa.xtp` (export mod-list metadata), historic
  `infrastructure/state/modlists/*.xml`, and design/audit docs.
- No About.xml of ours lists it in `modDependencies`/`loadAfter`; no live item in `infrastructure/state/items/` names it.
- Our C# reads `World.NaturalRockTypesIn` (`RM_DigDiscovery.cs`, `GenStep_LanternstoneRock.cs`,
  `RM_PreciousCaves.cs`) as a consumer only; all three take any count, none patches it.
- Canonical start save `Saves\CANONICAL_ASHKARR_START_2026-09-12.rws`: 0 Minerals things
  (sanity probe: the same grep sees 5896 `AncientConcrete`, 7767 things); its 4 `zacharyfoster` hits are the mod list.

## What we reproduce in-house — nothing, with one note

- Rock/ice/crystal spawning: comes from the dependants, two already PHASE-OUT; the in-house home for
  crystal clusters is the already-written per-biome design (`design/RimMandrake/minerals_where_they_belong_design_2026-10-02.md`
  F4/W4, PROPOSED per biome sitting) — it never depended on this mod.
- **Note, rock types per tile:** with the framework active every tile draws 1..4 rock types; after
  retirement it is vanilla 2..3, so the per-tile rock list changes. Nothing of ours depends on it and no
  ruling chose 1..4. Not reproduced. If the owner wants 1..4 back, it is a small Harmony patch plus a
  Mod Settings range in an owned mod — ask by card; the world is painted once at the end, so it should be
  settled before that.

## For the Wave 2 removed list (owner of modlists: 08_wave2_prep)

Add all four together (the three depend on the framework):

```
zacharyfoster.mineralsframework
zacharyfoster.mineralsrock
zacharyfoster.mineralsfrozen
zacharyfoster.mineralssparkle
```

Expected effect: the per-map `settlementDistProbFactor` GenStep NRE disappears.
