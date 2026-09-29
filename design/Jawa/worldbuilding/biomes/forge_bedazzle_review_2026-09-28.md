# The Forge — bedazzle review (movements 1–2), 2026-09-28

Program: `BAROQUE_BEDAZZLE_PROGRAM_1`, row 6. Reviewer: DESIGN subagent (Fable).
Both spellings swept: "TheForge"/"The Forge", prefixes `RM_Forge`/`RUT_Forge`.

## What's there

**Item:** FORGE_BEDAZZLE_SITTING_1 · **Program:** BAROQUE_BEDAZZLE_PROGRAM_1 (row 6)
**Author:** DESIGN subagent (Fable), movement 1–2 pass. Sources read this pass:
`src/RimMandrake/TheForge/` (all defs + C#), the frozen twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheForge.xml`, all seven Forge Utinni
patches + the FoundryFloor/Tower/Vent/Tibanna def files,
`src/RimMandrake/EnvironmentalHazards/Source/` (the whole Forge kit lives there),
`rosters/the_forge.json`, the frozen sheet `the_forge.md`
(🧊 *"FROZEN — BIOME_FREEZE_FABLE_REVIEW_1, 2026-09-07. The rulings in this sheet are
frozen: amendments add detail; they never change a ruling."*),
`FORGE_MECHANICS_1` (all four build passes), `forge_kit_spec.md`, the accent doc Batch 5c,
artpipe `registry.jsonl`/`done/`/`_artsrc/`/`pending/` + `Transient/*.decisions.json`.
No rename is ruled for this biome.

### BiomeDef(s)

Two, deliberately (twin architecture, `biome_mod_architecture.md` §5) — the sheet's
"three defs as one place" (Volcano · LavaField · AB_PyroclasticConflagration, one
massif zoned by elevation) is long since merged into the single owned def pair:

- **`RM_TheForge`** — `src/RimMandrake/TheForge/Defs/BiomeDefs/RM_TheForge_Biome.xml`,
  ships in `mandrake.rm.theforge` ("RimMandrake: The Forge"), built 2026-09-25
  (`THEFORGE_RM_MOD_BUILD_1`). animalDensity 1.2, plantDensity 0.4, own worker
  `RM_BiomeWorker_TheForge` (temp 38–65 °C, elev 1100–2400 m bands, replaces the donor
  AlphaBiomes worker), own `RM_RedFog` weather (owner ruling 2026-09-24 de-SW-ing
  RSW_SW_RedFog), `RM_ForgePulse` biomeMapCondition wired natively. Hard modDependency:
  `mandrake.rm.environmentalhazards` (the shared kit assembly).
- **`RUT_TheForge`** — the frozen campaign twin, still carrying the donor's bare
  `Beldon`/`LavaFlea` rows and `RSW_SW_RedFog`; served the live world to date.

Donor exposure in the RM def, disclosed in its own headers: 3 AB_ terrainsByFertility
bands inline unguarded, `AB_VolcanicAsh`/`AshRain` weathers (MayRequire-guarded),
donor flora rows (below), vanilla `ExtremeDesert` worldmap texture stand-in.

### Flora roster (def + patch-added, merged)

No Utinni flora patch for this biome — flora is inline on the RM def (shorthand
`<DefName>commonality</DefName>` form, parsed as such). 10 rows:

| def | comm | provenance |
|---|---|---|
| `Plant_Fireweed` | 0.9 | vanilla/Odyssey — THE signature per the frozen sheet (heat-gear fiber economy) |
| `Plant_MagmaCactus` | 0.7 | vanilla/Odyssey |
| `RM_FireLavender` | 0.6 | OURS — renamed from RUT_, glower, 50–352 °C band; art done+deployed (`FireLavender_a.png`) |
| `RM_CinderCrust` | 0.4 | OURS — Q13 divergence of shared RUT_Sagecrust (TheRot took RM_Sagecrust); **no art yet** (texPath points at nothing) |
| `IronScruff_PrimordialGrass` | 0.35 | donor |
| `AB_TinkleGrass` | 0.3 | Alpha Biomes donor |
| `IronScruff_PrimordialTallGrass` | 0.3 | donor |
| `IronScruff_Bindweed` | 0.25 | donor |
| `AB_FirevineTree` | 0.2 | Alpha Biomes donor tree |
| `RM_HeatsinkFungus` | 0.2 | OURS — renamed from RUT_, heat-drinking tree; art done+deployed |

### Fauna roster (def + patch-added, merged)

RM def inline (5 rows): `AA_Aerofleet` 0.4 (sky jelly-fleet — sheet renames it
"fumerider", still donor label) · `LavaSnail` 0.35 (Odyssey) · `AA_Metallovore` 0.15 ·
`AA_CrescendoAnole` 0.5 (pyramid-law small) · **`RM_FleetFlier` 0.45** (OURS,
from-scratch small sky darter; real core-1.6 flight stats `MaxFlightTime 15` +
`CompProperties_VaporDrifter`; **no textures in the mod yet** but art EXISTS in artpipe).

Patch-added (`UtinniPatches/Patches/WildAnimals_TheForge.xml`, one
PatchOperationConditional targeting `Defs/BiomeDef[defName="RM_TheForge"]/wildAnimals`,
species read from the op's own value): `RSW_LavaFlea` 0.25 · **`RSW_Beldon` 0.08** (the
tibanna herd — fixing the frozen twin's latent mismatch where the tap targeted RSW_Beldon
but only bare donor `Beldon` ever spawned) · `RSW_Maguana` 0.5 (magma-camouflage lizard,
ours ex-BMT).

**Campaign cast: 8 wired species. RM-standalone cast with no donors installed: 1
creature (the fleet flier) + 3 owned plants + 2 vanilla plants.** See roster gaps.

Roster-vs-wiring gap (adjudicate at the sitting, no action taken):
`rosters/the_forge.json` fauna carries `AA_ColossalAerofleet` (0.5) and `Tibidee` (0.5)
wired NOWHERE (twin comment says both were left out on purpose as LARGE during the
pyramid-law small-share fix; the roster still lists them). `Beldon` roster confidence
block: "placid" ruling vs register predator special — resolved in RSW_Beldon's port per
the roster's stat_adjustments row, worth re-confirming at the sitting.

### Terrain / weather / conditions

- Terrain: the 3 donor AB_ bands (`AB_BlackPebbles`/`AB_HardenedGrass`/`+Fertile`)
  inline — **no owned TerrainDef anywhere in the biome**; the sheet's §7 obsidian/
  volcanic-glass material family has no def expression.
- Weather: `RM_RedFog` (owned), `RM_ForgeStill` + `RM_BoilingRain` (owned, only ever
  forced by the pulse), AB_VolcanicAsh/AshRain donors, Clear 40. Rain/snow all 0 (ban 6).
- **`RM_ForgePulse`** GameConditionDef (canBePermanent, on the biome's
  biomeMapConditions): `RM_GameCondition_WeatherPulse` forces ForgeStill, rolls MTB-10h
  bursts of BoilingRain 20–40 min, deals `RUT_Scald` damage (4/60 ticks, unroofed only),
  starts a 2 h flash-growth window per burst. This is a REAL, shipped, biome-scale
  unique mechanic.

### Mechanics / C# (the Forge kit — FORGE_MECHANICS_1, all six built, item still `doing`)

The kit lives in `src/RimMandrake/EnvironmentalHazards/` (shared assembly, hard dep),
Forge-specific content in `UtinniPatches/`. Build passes 2026-09-13/14, offline-proven,
live quicktest still owed:

| F# | mechanic | state |
|---|---|---|
| F1 | Boiling-rain pulse + scald + flash flora | SHIPPED: `RM_GameCondition_WeatherPulse`, `RM_MapComponent_FlashCycle`, `RUT_Plant_FlashFlora` (×8 growth in window / ×0.05 outside), `RUT_Scald` DamageDef + `RM_ScaldArmor`/`RM_ArmorRating_Scald` |
| F2 | Beldon tibanna tap | SHIPPED: `RM_CompGatherableGas` (CompMilkable-shape), `RUT_TibannaTap_BeldonWiring.xml` (FindMod-gated onto RSW_Beldon, 12 gas / 2 days), `RUT_TibannaGas` item (placeholder price; **DEPLOY_HOLD, no art**). Ban-5 linter: only consumer is the tap — monopoly holds by construction |
| F3 | Vapor-column flight layer | SHIPPED (classes): `RM_MapComponent_VaporColumns` (columns from steam geysers / CompActiveGasEmitter / dangerous+avoidWander terrain), `RM_CompVaporDrifter`, `RUT_VaporDrifter_AerofleetWiring.xml`; ThinkTree wander-root wiring proven but thin |
| F4 | Foundry tower dungeon | SHIPPED (shell): `RUT_FoundryTowerEntrance` (MapPortal → `RUT_FoundryFloor` 80×80 pocket map, temp 70 °C, LavaDeep melt channels via `RM_GenStep_TerrainChannels`, salvage cache + tender spawn gensteps, `RUT_FoundryTowerScatter` on player maps). One floor per owner card 1 (RULED 2026-09-12); interiors are vanilla ScatterRuinsSimple stand-ins; tender pawnkind NOT cast; **both buildings DEPLOY_HOLD, no art** |
| F5 | Contagion die-off ring | SHIPPED: `RM_CompScriptedDieOff`, `RUT_DyingCreep`→`RUT_DeadCreep` (spread 6–10 over 4 h, dead by 8 h); in no wildPlants by design |
| F6 | Geothermal vent industry | SHIPPED (XML): `RUT_VentSmelter`/`RUT_VentForge`/`RUT_VentKiln` + recipe wirings |

Mod Settings: `RM_TheForgeMod.cs` — master toggle + 6 per-mechanic knobs (weather pulse,
tibanna rate, vapor immunity, tower scatter, die-off density, vent work-speed) —
**declared but NOT wired** except F1's shared `weatherPulseEnabled`; consolidation owed
to FORGE_MECHANICS_1 per the file's own header.

⚠️ **`RM_HediffComp_ForgeOnSurvival.cs` is NOT a Forge-biome mechanic.** It is the
MIASMA's fever-"forged" survival-boon comp (`onlyInBiomes: RUT_Miasma`, wired by
`Miasma/Patches/RUT_Miasma_ForgeOnSurvival.xml`). Named "forge" for the verb. Recorded
here so no census counts it either way.

Campaign plot on top (not this sitting's to build): `TIBANNA_EMBARGO_PLOT_1` (Empire gas
monopoly clock, both cards RULED 2026-09-12, source cut executed, build surfaces owed);
`TibannaEmbargo_CutMineableRoute.xml` live.

### Art status per cast member

From artpipe `registry.jsonl` + `done/` + `_artsrc/` + `Transient/*.decisions.json`
(checked before anything is called "owed", per the standing rule). Blanket owner ruling
2026-09-20: **replace** on every ported donor row's art.

| subject | status |
|---|---|
| `RM_FleetFlier` | **art DONE in artpipe** (`rutfleetflier_v1` east/north/south in `done/` + `_artsrc/`) — but the mod ships 0 PNGs and the def's texPath expects `Things/Pawn/Animal/RM_FleetFlier/`. **Wiring ticket, not an art ask** |
| `RSW_Beldon` | canon art DONE (`canon_beldon_v1` 3 facings) — replace ruling satisfied |
| `RM_FireLavender` | done + deployed (`FireLavender_a.png` in mod) |
| `RM_HeatsinkFungus` | done + deployed (`HeatsinkFungus_a.png`) |
| `RM_CinderCrust` | **no art anywhere** (searched cinder/cindercrust — only Cinderfelt/Cinderwing/Cindermite, different subjects). Q13 "regenerate the second copy's identity" still owed |
| fireweed / firevine | `firevine_fireweed_v1` done |
| sagecrust lineage | `sagecrust_v1` + `rot_sagecrust_v2` done (Rot's copy — not this biome's) |
| `AA_Aerofleet`/`AA_Metallovore`/`AA_CrescendoAnole`/`LavaSnail`/`RSW_LavaFlea`/`RSW_Maguana` | donor/port art live; all under the 2026-09-20 blanket "replace" ruling, none replaced yet, none queued |
| `RUT_TibannaGas`, `RUT_FoundryTowerEntrance`, `RUT_FoundrySalvageCache` | **DEPLOY_HOLD "no art yet"** (held 2026-09-13/14) — three real art debts on shipped mechanics |

⛔ Nothing in this table may be re-queued at movement 4; the fleet flier especially —
its art exists and sits unwired.

## Nine-mark scorecard

PENDING

## Roster gaps + Proposed fills

PENDING

## Candidate mechanics slate

PENDING
