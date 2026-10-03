# SALVAGE_WRECKAGE_EVERYWHERE_1: design (DRAFT, for owner ruling)

BENCH design helper, 2026-10-02. Design only: no defs, code, items or ledger verbs came out of
this pass. Item filed by the owner 2026-09-25: *"I like the wreckage you made, game should be
filled with lots of this all over the place given it's salvage focus."*

**The short version.** The Scald's three wrecks work, and they are built the expensive way:
one ThingDef per silhouette, one GenStepDef per silhouette (the class takes a single
`thingDef`), and one hand-written settings bool, all for one biome. Doing that again for about 25
biomes would mean about 75 GenStepDefs and 25 one-off toggles. The design below keeps the
Scald's mechanism (`ShipChunkBase` salvage buildings, a terrain-tag-validated scatter, a Mod
Settings gate), and adds three pieces of shared machinery so that each biome becomes **data**:
one weighted-list scatter GenStep, one deconstruct-loot comp, and abstract family parents that
a biome inherits from and weathers. The roster ruling (which junk kinds exist, and what is cut) is
**already owned by `FASCINATING_WORLD_JUNK_1` Phase 3**, which has not started. This design gives
that sitting a machine to fill, and does not pre-empt its roster.

## 1. Inventory (measured 2026-10-02, read from source, with paths)

All paths are relative to `/home/mandrake/rm/bench` (Windows mirror: `D:\Luke\dev\RimMandrake\`).

### 1a. Scatter wrecks (salvage buildings that map generation places)

| what | defs | mechanism | tier / mod | state |
|---|---|---|---|---|
| **Scald wrecks** (the worked example) | `RUT_ScaldWreckHull` (30 Steel + 1 ComponentIndustrial), `RUT_ScaldWreckTank` (20 Steel + 5 GravlitePanel), `RUT_ScaldWreckFrame` (15 Steel); all 2x2, `ParentName="ShipChunkBase"`, `resourcesFractionWhenDeconstructed 0.75`, `killedLeavings` slag, `terrainAffordanceNeeded Walkable`, 3 `Graphic_Random` 512px variants each | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Buildings/RUT_ScaldWrecks.xml`; scatter `.../Defs/MapGeneration/RUT_ScaldWreckScatter.xml`: **3 GenStepDefs** (orders 965-967), class `RM_GenStep_ScaldWreckScatter : GenStep_ScatterThings` (`Source/RM_TerminalBiomesScaldKit.cs:62`, which only adds `ShouldSkipMap` on the setting), validated on terrain tag `RUT_ScaldShallow`, 0.4~0.6 per 10k cells each, minSpacing 6; registered on `RM_TheScald`/`RUT_TheScald` `extraGenSteps` by `Patches/RUT_ScaldWreckScatter_Register.xml` | defs are `RUT_` but live in an **RM** mod (`mandrake.rm.biomes` via TerminalBiomes). See the tier note in §5 | built, art wired (`506c4ca63`), toggle "S6 — wreck salvage" (`RM_TerminalBiomesMod.cs:279`), gate `RM_MechanicGates.Register("Scald.S6", …)` |
| Scald yield economy note | the defs' own header says that loot on deconstruct (`RUT_ScaldSalvage` ThingSetMaker) was **deferred** because it needs a comp. v1 is costList only | same file, header | | open idea, never built |
| **Jawa scrapfields** | `ChunkSlagSteel` scatter, 7~9 per 10k (44-56 chunks per 250x250) | `src/RimUtinni/UtinniPatches/Defs/MapGeneration/JawaScrapfields.xml` (`RUT_Jawa_ScatterScrapfields`) | RUT, desert maps | built (V1 row 4, `73ca76c`) |
| **Ground hulk** | one PrefabDef stamp per map: deck, breach, 4x `ShipChunk_Mech`, `AncientCryptosleepCasket` | `src/RimUtinni/UtinniPatches/Defs/PrefabDefs/JawaGroundHulk.xml` + `Defs/MapGeneration/JawaGroundHulk.xml` (`GenStep_ScatterGroupPrefabs`, count 1, order 940) + `Patches/JawaGroundHulk_Register.xml` | RUT | built |
| **Wreck vermin nests** | `RM_CompProperties_VerminNest` patched onto Odyssey `ShipChunk_Mech` | engine `src/RimMandrake/ShipVermin/`; wiring `src/RimUtinni/UtinniPatches/Patches/WreckVerminNest_ShipChunk.xml` | RM engine, RUT wiring | built. **This is a reusable wreck hazard: any family can carry it** |
| **Crawler road wrecks** | `RSW_WreckedSkiff` (60 Steel, 2 Comp), `RSW_CrawlerTreadWreck` (110 Steel), terminus GenStep | `src/RimStarWars/StructureInjectionsSW/Defs/ThingDefs_CrawlerRoad.xml` | RSW | built |
| Long Shade crawler road (RM half) | `RM_WreckedCart` (10 Steel), `RM_CrawlerRoadTerminus`, `RM_GenStep_CrawlerRoad` | `src/RimMandrake/LongShade/Defs/ThingDefs_Buildings/RM_CrawlerRoad_Wrecks.xml`, `.../MapGeneration/RM_LongShade_GenSteps.xml` | RM (Long Shade) | built |
| **Crashed ship / podracer wreck** | `RSW_CrashedShip` TileMutator → `RSW_GenStep_CrashedShip` (rimplace plan `Templates/crashed_ship.txt`, 30x20); `RSW_PodracerWreck` | `src/RimStarWars/StructureInjectionsSW/Defs/{TileMutatorDefs,GenStepDefs}_CrashedShip.xml` | RSW, engine `mandrake.rm.injections` | built; the junk census records "NOT YET PLACED on any Ash'karr tile" (a placement question for the paint pass, not a defect) |
| **KOTOR junk piles** | `KOTOR_JunkPileClusters` (`GenStep_ScatterGroup`, 0.2~0.5), `KOTOR_MineableJunk` | `src/RimStarWars/Armoury/Defs/Absorbed_KotorCore/ThingDefs_Resources/` | RSW (absorbed) | built |
| Forge salvage cache | `RUT_FoundrySalvageCache`: an inert marker and **placeholder** (no loot table, no art, DEPLOY_HOLD) | `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_FoundrySalvageCache.xml` | RUT | shell only. Loot owed |

### 1b. Salvage that arrives (not map-gen scatter)

| what | path | state |
|---|---|---|
| Blue Desert ablation salvage: 3 incidents (`RM_AblationSalvage_Wreckage/_Metal/_Fallen`), the ice gives up wreckage, meteoritic metal, a freeze-dried body | `src/RimMandrake/BlueDesert/Defs/IncidentDefs/RM_AblationSalvage.xml`, `Source/RM_AblationSalvage.cs` | built |
| Cracked Lands recede salvage: `RM_MapComponent_RecedeAftermath` drops 1-3 ComponentIndustrial + 1-3 slag on wetted cells; the mud takes it back after 3 days | `infrastructure/state/items/CRACKEDLANDS_SALVAGE_CLAIM_CREW_1.md` (built in parent); **owed:** claim stakes, rival crew, half-buried wreck silhouettes | partly built |
| Jawa_TheClaim quest: "Something came down past the ridge", walk to the wreck | `src/RimUtinni/UtinniPatches/Defs/QuestScriptDefs/Jawa_TheClaim.xml` | built |
| Fall Line arrivals: 15 species that should arrive **with** wreckage, not live in the sand | `infrastructure/state/items/FALL_LINE_ARRIVAL_MECHANISM_1.md` | **nothing built**. Needs a fall-wreck delivery |
| Fall-zone lost cargo quests: a manifest on injected wreckage points to cargo still out there; *"The player did not fall from space"* | `infrastructure/state/items/FALLZONE_LOST_CARGO_QUESTS_1.md` | lead only, unruled |
| Abyss Lightfall: a wrecked rescue gravship in the chasm wall, stripped to repair yours; *"You can't have two ships"* | `infrastructure/state/items/ABYSS_LIGHTFALL_BROOD_WRECK_1.md` | ruled 2026-10-01, unbuilt |

### 1c. Wreck-adjacent systems this design must not duplicate

- **WreckedMachines** (`src/RimMandrake/WreckedMachines/`, `mandrake.rm.wreckedmachines`): the start
  ship's machines with three tiers, Wrecked → Kludged → Repaired. *"cannot be removed"*. These are **repair**
  wrecks, not **strip** wrecks, and are a separate grammar. `WRECKED_DISTILLATION_MODULE_1` adds a sibling.
  ⇒ The scatter families here are **strip-only**. A scattered wreck never becomes a repairable machine
  (§8 Q3 asks about the one exception).
- **AssailantSalvage** (`src/RimMandrake/AssailantSalvage/`, `mandrake.rut.assailantsalvage`): 22 owned
  `RUT_` frozen-ancient-ship props (airlocks, busted turrets, terminals, cryptopod), *"not yet wired into
  any map generation"*. This is a ready-made **interior** family for a hulk prefab.
- **SALVAGE_PALETTE** (`design/Jawa/art/SALVAGE_PALETTE.md`, generated by `salvage_filter.py` from the
  live def dump): 315 USABLE-YIELDS, 26 destroy-only, 635 empty, 73 EXCLUDED props. This is the existing
  instrument for "can the clan actually strip this". Every new family def must land in USABLE-YIELDS.
- **FASCINATING_WORLD_JUNK_1** (`infrastructure/state/items/FASCINATING_WORLD_JUNK_1.md`, census
  `design/Jawa/worldbuilding/junk/junk_census_2026-09-13.md`): Phases 1-2 done; **Phase 3 (the roster,
  by cards with the owner) and Phase 4 (re-graphic) not started**. It found that vanilla/Ideology
  **`AncientJunkClusters`** (`GenStep_ScatterGroup`, 9 junk groups, tanks/trucks/cars) runs on **every**
  common map, which is the "crashed motorway" the owner dislikes. It also found that Odyssey
  `ScarlandsJunkPrefabs` (`GenStep_ScatterGroupPrefabs`) is the precedent for whole multi-cell junk prefabs,
  and named 6 borrowable silhouettes from `xmb.ancienturbanruins.mo`.
  ⇒ **This item and that one are the same program from two ends.** That item rules *what kinds*
  exist; this one builds the *per-biome machine* that places and weathers them.

### 1d. Engine facts this design rests on

- `GenStep_ScatterThings` takes **one** `thingDef` (the Scald header, read against decompiled source),
  which is why the Scald needed three GenStepDefs. Terrain validation is **tag-based**
  (`terrainValidationAllowed`). Both facts are recorded in `RUT_ScaldWreckScatter.xml`.
- `ThingComp.PostDestroy(DestroyMode mode, Map previousMap)` and `PostDeSpawn(Map, DestroyMode)` exist
  (RimSage, `Verse/ThingComp.cs:39,43`), so a comp can tell **Deconstruct** from **KillFinalize** and
  drop a ThingSetMaker's output only on a deconstruct. That is the comp the Scald deferred.
- `ShipChunkBase` is static, non-claimable, always deconstructible, with no rot, corpse or spawner. It is
  the right parent for every strip-wreck.
- A water biome's scatter needs `allowInWaterBiome true`, and a shallow-water wreck needs
  `terrainAffordanceNeeded Walkable`, because the inherited `Light` fails on water terrain
  (`RUT_ScaldWrecks.xml` header).

## 2. Biome table: promised / built / missing

"Promised" is what the biome's frozen sheet or bedazzle review says, under
`design/Jawa/worldbuilding/biomes/`. It comes from a grep-led read of every doc there, with context
read only around the hits. "Ruled" means the frozen-sheet freeze (2026-09-07) or an owner pick that
the doc records. Per CLAUDE.md, **no tile counts**: whether a biome is painted yet has no bearing here.

| biome | wrecks promised (source) | built | missing |
|---|---|---|---|
| **The Scald** | wrecks in the shallows, "cooked clean", burn-priced (`the_scald.md:162,208`, ruled); `RUT_ScaldSalvage` loot (`kits/scald_kit_spec.md:283-310`) | 3 silhouettes + scatter + toggle (§1a) | deconstruct loot (the deferred comp); `RUT_` names in an RM mod (§5) |
| **Fall Line** (injection layer, not a BiomeDef) | "a slow rain of other people's ruined machinery", **fresh and renewable** ("Salvage taken is replaced"), live powered wrecks, salvager camps, debris strikes (`fall_line.md:51-53,96-98,143-146`, ruled) | ground hulk (one per map), scrapfields slag, vermin nests on `ShipChunk_Mech` | the **renewal** (an incident that drops fresh wrecks), the live/powered wreck, the arrival delivery for 15 species (`FALL_LINE_ARRIVAL_MECHANISM_1`), the manifest leads (`FALLZONE_LOST_CARGO_QUESTS_1`) |
| **Warscar / Scarlands** | crashed ships "plundered to skeletons", "No intact treasure in the open" (`the_scarlands.md:54,138,190,234`, ruled); `RM_WreckLichen` grows only on wrecks; `RM_FailedChassis`; live shield generators (`warscar_bedazzle_review_2026-09-30.md:156-199`, web ruled turn 3); wreck-state PrefabDefs + slag-only loot table (`kits/scarlands_kit_spec.md:349-372`) | vermin nest wiring (shared) | the whole stripped-fleet family; lichen needs a wreck to grow on, so **the Warscar food web is blocked on this item** |
| **Wasteland** | crashed hulls, warcasket sarcophagi as salvage-within-salvage (`wasteland.md:199,217,247-253`, ruled) | none found | the hull family + sarcophagus interior |
| **Blue Desert** | ablation line surfaces wreckage, metal and freeze-dried bodies; fall debris fields (`the_blue_desert.md:176,221,251-252`, ruled) | `RM_AblationSalvage_*` incidents | static ice-locked wreck family on the map (optional: the incident already delivers) |
| **Deep Desert** | "fallen wreckage" landmark, **rare** here; wreck-shelter shade pocket (`deep_desert.md:158,212-215`, ruled) | scrapfields + hulk where the patch registers | the rare sand-scoured landmark wreck + shade pocket |
| **Desert** | shadows collect "bones, debris and wreckage" (`desert.md:304`, ruled) | scrapfields | small wreck scatter, sand-blasted register |
| **Dune Sea / Stillsand** | buried finds, **sealed and uncorroded**; a storm exposes a wreck (`dune_sea.md:217,234,253`, ruled; `stillsand_bedazzle_2026-09-27.md:190,241-247`, proposed) | `RSW_CrawlerTreadWreck` cast (`stillsand_bedazzle_cast_2026-09-30.md:83`) | buried-wreck family + storm reveal |
| **Long Shade** | N2 wreck road: "the richest salvage on the map and... the only road across the gap" (`longshade_shade_ideation_2026-09-29.md:253-258`, ideation) | `RM_WreckedCart`, `RSW_WreckedSkiff`, `RSW_CrawlerTreadWreck`, crawler road GenStep; landspeeder art exists | the road as the ideation describes it; deconstruct loot |
| **Arid Shrubland** | scrap nests lined with wire, lens-glass, hull chips (`arid_shrubland.md:211-218`, ruled) | `RSW_ScrapNest` / `RSW_ScrapNestBird` / `RSW_HoardScrap` | nothing for this item: nests are creature content |
| **Rust Cathedral** | the whole map is salvage, "every wall is money, every sacred" (`the_rust_cathedral.md:179,333,356`, ruled); Mending Weld rite (owner typed approval, `rustcathedral_bedazzle_review_2026-10-02.md:466`); borehulk (owner picked) | biome walls | a **sacred-wreck** register (stripping costs the faction's goodwill), not a scatter |
| **Abyss** | wind-farms, working and wrecked (`abyss.md:227`, ruled); the Ship in the Wall (ruled 2026-10-01) | none | handled by `ABYSS_LIGHTFALL_BROOD_WRECK_1`; the wrecked wind-farm is a small family here |
| **Miasma** | the planet's "driftwood-and-salvage beach"; a flotsam yard after surges (`the_miasma.md:197`, ruled); the review notes "no flotsam table, genstep or post-surge salvage exists" (`miasma_bedazzle_review_2026-10-02.md:183`) | none | the flotsam family + post-surge delivery |
| **Cracked Lands / Flooded Canyon** | "a flood is a salvage strike": floods expose buried wreckage (`the_cracked_lands.md:318`, ruled) | recede salvage (components + slag), mud reclaims after 3 days | half-buried silhouettes, claim stakes, rival crew (`CRACKEDLANDS_SALVAGE_CLAIM_CREW_1`) |
| **Fever Wood** | "chitin and salvage", the two-front war's leavings (`the_fever_wood.md:168`, ruled) | none | an overgrown-war-wreck family |
| **Rot** | the gut that eats wrecks and passes "Sheen-glazed salvage castings"; the old ship pinging inside (owner typed "AWESOME", `rot_bedazzle_review_2026-10-02.md:541`) | none | a digested-wreck family, plus the pinging ship (a set-piece, its own item) |
| **The Forge** | forge-tech salvage in the towers (`the_forge.md:142`) | `RUT_FoundrySalvageCache` marker only (no loot, no art) | the cache's loot table (the same comp as §3) |
| **Grey Deep** (sea) | "the jacketed salvage": wrecks chiselled free from crystal (`the_grey_deep.md:366,463`, ruled) | none | crystal-jacketed wreck family on the floor map (inside the dive generator, not a tag; see §1a's Grey precedent) |
| **Twilight Deep** (sea) | "the wrecks of the impatient"; `RM_PickedWreck`, 1-2 per floor, hull-rib with a salvage-mark and **nothing inside** (`the_twilight_deep_content_2026-09-26.md:816-823`, proposed) | none | the picked-clean family (low yield by design) |
| **Propane Lake** (sea) | sealed ancient cartridges, an unfinished pipeline junction (floor agenda `:219-221,389`, proposed) | none | pending its sitting |
| **Nightside Ice** | failed Junker crystal expeditions; "a seam of wreckage" (`nightside_ice.md:135`, ruled; review option proposed) | none | an ice-locked expedition-wreck family |
| **Weeping Stones** | ancient condenser arrays to salvage **or restore** (`weeping_stones.md:165,284`, ruled) | none | a restore-or-strip choice, which is WreckedMachines' grammar, not a strip family (§8 Q3) |
| **Cauldron** | corroded ruins and small finds (a spent filter cartridge, a hauled-in tank); it **contrasts itself** with the dayside wrecks (`cauldron.md:227-230`) | none | small-finds scatter only, no hulls |
| **Sump** | Junker stations (derricks, barrel yards) (`the_sump.md:151,161`) | dig-stratum table | none: the Junker stations are structures, not wrecks |
| **Greentide, Pyrelands, Gelatinous Slime, Contagion, Lantern Deeps, Webwork, Terminator Sea, Leaning Scrub** | **nothing promised** (grep-only for Pyrelands and the Propane Lakes sheet). Lantern Deeps declined the Inherited Wreck rite (`lanterndeeps_bedazzle_review_2026-10-01.md:261`) | none | §8 Q1: does "everywhere" override a sheet that is silent, or one that said no? |

**Reading the table.** About 20 biomes promise wreckage and 3 have any scatter built: the Scald,
plus the desert band via the scrapfields and the hulk. Most of the promises share one shape: a
small scatter of 2-4 silhouettes with a biome-flavoured skin and yield. That shape is what the
framework below makes cheap. A handful are set-pieces or delivery mechanisms (Ship in the Wall,
the Rot's pinging ship, Fall Line renewal, Miasma post-surge flotsam, the flood strike) and stay
their own items. The framework only gives them a family to drop.

## 3. Shared wreck-family framework

**The principle: define a family once, then let each biome weather it with data.** A *family* is
what the wreck **was**: a hull section, a tank, a frame, a speeder, a droid carapace, a tread. A
*weathering* is what the **biome did to it**: cooked, sand-scoured, ice-locked, overgrown,
digested, crystal-jacketed, flood-buried. A placed wreck is family × weathering. Three new
pieces of engine do this, and none of them is new XML grammar.

### 3a. Family = an abstract ThingDef parent (XML only)

```
RM_WreckFamilyBase            (Abstract, ParentName="ShipChunkBase")
  └ RM_WreckFamily_Hull       (Abstract) size, drawSize, shadow box, base costList, loot tier "Hull"
  └ RM_WreckFamily_Tank       (Abstract) ... loot tier "Tank"
  └ RM_WreckFamily_Frame      (Abstract) ...
  └ RM_WreckFamily_Speeder    (Abstract) ...   (Long Shade, Desert, Fall Line)
  └ RM_WreckFamily_Carapace   (Abstract) ...   (droid shell: components, a live-bolt risk)
  └ RM_WreckFamily_Tread      (Abstract) ...   (crawler; big, steel-heavy)
```

The family carries everything that does not change with the biome: footprint, a shadow volume
calibrated once per silhouette on the Scald's ratio (0.70x width and 0.63x height of the mean alpha
bbox), base `costList`, `killedLeavings`, and a **loot tier** read by the comp in §3c. The base sets
`terrainAffordanceNeeded Walkable`, so every family can sit on shallows (the Scald trap, solved once).

### 3b. Weathering = a biome's concrete child def + one ModExtension

```xml
<ThingDef ParentName="RM_WreckFamily_Hull">
  <defName>RM_ScaldWreckHull</defName>
  <label>scalded hull section</label>               <!-- the biome's voice -->
  <description>…cooked in the shallows…</description>
  <graphicData><texPath>Things/Building/Wrecks/Scald/Hull</texPath></graphicData>
  <modExtensions>
    <li Class="RimMandrake.Wreckage.RM_WreckWeathering">
      <weathering>Cooked</weathering>                <!-- a WreckWeatheringDef -->
    </li>
  </modExtensions>
</ThingDef>
```

`RM_WreckWeatheringDef` is a small new Def type, about 8 rows planet-wide, and one row is shared by
every biome with that weathering:

| field | meaning | example: Cooked (Scald) | example: Sealed (Dune Sea) |
|---|---|---|---|
| `yieldFactor` | multiplies the family's base `costList` once, at def-resolve time | 0.75 (corrosion) | 1.0 (uncorroded) |
| `lootTierShift` | moves the loot table up or down | 0 | +1 (sealed, so intact parts) |
| `labelPrefix` | default adjective if the child sets no label | "scalded" | "sand-sealed" |
| `hazards` | optional comps added by the patch, reused, not new | none (the terrain burns) | none |
| `extraLeavings` | biome by-product on destroy | slag | sand |

**Why a child def per biome, and not a C# generator that multiplies families by weatherings at load.**
A generated def is invisible to the def dump, to `SALVAGE_PALETTE`'s filter and to grep, and the
texture still has to be a real per-biome path. A child def is about 12 lines and is readable,
patchable and art-addressable. The weathering def keeps the numbers single-source, so changing
"Cooked" re-tunes every cooked wreck. (`yieldFactor` is applied in a `ResolveReferences`-time pass
over defs carrying the extension. That is about 30 lines of C#, and it lets a biome def never restate
a cost.)

Hazards reuse what exists: `RM_CompProperties_VerminNest` (ShipVermin) for nests under hulls;
`RM_WreckLichen` growth (Warscar) keyed on a `RM_WreckSurface` thing-category that every family base
carries; Odyssey/vanilla `CompProperties_Explosive` for a live tank. No new hazard engine.

### 3c. Loot = one comp, one ThingSetMaker per tier

`RM_CompSalvageLoot` overrides `PostDestroy(DestroyMode mode, Map previousMap)` (verified to exist,
§1d). It fires **only on `DestroyMode.Deconstruct`**, so smashing gives `killedLeavings`, and
stripping properly gives the costList **plus** a roll. That makes deconstructing the skilled path,
which a Jawa campaign wants. It reads the family's loot tier, shifts it by the weathering, and
generates from a `ThingSetMakerDef` named `RM_SalvageLoot_<Tier>`:

| tier | typical roll (INVENTED, for tuning) | rare roll |
|---|---|---|
| Scrap | 0-1 ComponentIndustrial, steel offcuts | none |
| Hull | 1 component, plasteel 0-5 | a usable ship part, 1 in 20 |
| Tank | chemfuel 0-15 if sealed, gravlite | a working valve or pump part |
| Carapace | 1-2 components | an intact droid part or a restraining bolt (the "risk" flavour from `FASCINATING_WORLD_JUNK_1` Phase 3) |
| Sealed | the above at +1 tier | ComponentSpacer |

Biomes may name an **extra** ThingSetMaker in the weathering for regional goods (Rust Cathedral
relic-scrap, Grey Deep crystal shards). The `RUT_` layer patches the tiers to add Star Wars parts
(repulsorlift coil, hyperdrive motivator shard) without touching RM defs. This is the Q11a tier line.

The same comp closes the Forge's `RUT_FoundrySalvageCache` "loot owed" gap and the Scald's deferred
`RUT_ScaldSalvage`.

### 3d. Placement = one weighted-list scatter GenStep per biome

`RM_GenStep_WreckField : GenStep_Scatterer`, a list-taking sibling of `GenStep_ScatterThings`:

```xml
<GenStepDef>
  <defName>RM_WreckField_Scald</defName>
  <order>965</order>
  <genStep Class="RimMandrake.Wreckage.RM_GenStep_WreckField">
    <settingsKey>Scald</settingsKey>                  <!-- §6 gate -->
    <wrecks>                                           <!-- weight per family -->
      <RM_ScaldWreckHull>1</RM_ScaldWreckHull>
      <RM_ScaldWreckTank>1</RM_ScaldWreckTank>
      <RM_ScaldWreckFrame>1</RM_ScaldWreckFrame>
    </wrecks>
    <countPer10kCellsRange>1.2~1.8</countPer10kCellsRange>
    <minSpacing>6</minSpacing>
    <terrainValidationAllowed><li>RUT_ScaldShallow</li></terrainValidationAllowed>
    <terrainValidationRadius>2</terrainValidationRadius>
    <allowInWaterBiome>true</allowInWaterBiome>
    <clusterChance>0.3</clusterChance>               <!-- field of 2-4, "fell together" -->
  </genStep>
</GenStepDef>
```

There is one GenStepDef per biome, not per silhouette, so the Scald's three collapse to one.
Registration stays the proven way: a patch adds it to the biome's `extraGenSteps`. Sea floors are
named in their dive generator's `<genSteps>` (the Grey precedent: the floor terrain tag is shared by
all four seas, so a tag would leak). ⚠️ Element-name-as-key lists (the `<RM_ScaldWreckHull>1</…>`
form) need a custom loader, like `BiomeAnimalRecord`. Use the same `LoadDataFromXmlCustom` pattern
and **never** a `<li>` form, so that a roster counter does not read zero (see CLAUDE.md, `<wildAnimals>`).

**Density note.** The owner said *"lots of this all over the place"*. The per-biome `countPer10k`
is the single knob for that, and the Mod Settings expose a global multiplier (§6). The Scald's
~1.5 total per 10k cells is "a few in the shallows". A land biome might sit at 2-4 per 10k
before clusters. These numbers are INVENTED and tuned live.

### 3e. Fresh wrecks (the Fall Line's law, and any arrival)

The Fall Line's wrecks are fresh and renewable, so they are **delivered, not generated**.
`RM_IncidentWorker_WreckFall` is one IncidentDef shape that drops 1-4 wrecks from a named
`RM_WreckField_*` list, using the vanilla `SkyfallerMaker` with a `ShipChunkIncoming`-style skyfaller,
and can attach an arrivals payload: a `PawnKindDef` list (the 15 species in
`FALL_LINE_ARRIVAL_MECHANISM_1`) or a manifest note (`FALLZONE_LOST_CARGO_QUESTS_1`). It also serves
Miasma post-surge flotsam (a different worker trigger, the same list) and the Cracked Lands flood
strike (the existing `RM_MapComponent_RecedeAftermath` would read a list instead of hard-coding
ComponentIndustrial and slag). That gives three of the "missing" rows in §2 one mechanism.

## 4. Per-biome families with weathering and loot

Every name below is a **proposal for the `FASCINATING_WORLD_JUNK_1` Phase 3 sitting to rule**.
Where a biome's sheet already names the content, the row follows it. "Weathering" refers to the
`RM_WreckWeatheringDef` rows. Tier: invented names go in `RM_` (Q11a); canon hulls (TIE panel,
landspeeder, skiff, crawler) go in `RSW_`; campaign-specific registers go in `RUT_`.

| biome | families (count) | weathering | loot lean | hazard / special | note |
|---|---|---|---|---|---|
| **The Scald** (worked example) | Hull, Tank, Frame (3, built) | **Cooked**: ×0.75, slag | Hull/Tank tiers, no sealed | the shallows burn per trip (terrain, unchanged) | migrate `RUT_ScaldWreck*` → `RM_ScaldWreck*` onto the family parents; art and texPaths unchanged |
| **Fall Line** | Hull, Speeder, Carapace, TIE-panel (`RSW_`) | **Fresh**: ×1.0, +1 tier, live power on 1 in 10 | Hull/Carapace; Imperial parts | vermin nests; Imperial attention if hauled in bulk (Phase 3 idea) | delivered by §3e, **not** scattered; "Nothing here is old" |
| **Desert / Deep Desert** | Speeder, Hull (rare in the Deep Desert) | **Sand-scoured**: ×0.6, sand leavings | Scrap/Hull | wreck shade pocket (Deep Desert) | the hulk stays as the one landmark |
| **Dune Sea / Stillsand** | Hull, Tank, Tread | **Sealed**: ×1.0, +1 tier | Sealed (intact parts, chemfuel) | half-buried; a storm-reveal variant later | "uncorroded" is the sheet's own law |
| **Long Shade** | Speeder, Skiff (`RSW_`), Cart (`RM_`, built), Tread (built) | **Sun-baked**: ×0.8 | Hull/Speeder; richest on the map | none | the road is the placement; feed the existing `RM_GenStep_CrawlerRoad` the family list |
| **Warscar** | Hull, Frame, FailedChassis, Shield-gen | **Stripped**: ×0.35, −1 tier ("plundered to skeletons") | Scrap; the live shield generator is the one prize | carries `RM_WreckSurface` so `RM_WreckLichen` grows; chatrak food web | unblocks the ruled web |
| **Wasteland** | Hull, Warcasket sarcophagus (salvage-within-salvage) | **Irradiated**: ×0.9, a rad hazard via existing Wasteland hediffs | Hull; sarcophagus = Carapace +1 | radiation on deconstruct | |
| **Blue Desert** | Hull, Frame | **Ice-locked**: ×0.9, must mine free first (a `RockBase` jacket) | Hull, freeze-dried finds | none new | ablation incidents stay the main route |
| **Nightside Ice** | Expedition rig, Tank | **Ice-locked** (shared) | Tank; Junker tools | none | failed Junker expeditions |
| **Miasma** | Flotsam: Frame, Tank, small crates | **Brined**: ×0.7, salt crust | Scrap | none | post-surge delivery via §3e |
| **Cracked Lands** | Hull, Speeder, half-buried | **Flood-buried**: ×0.8, mud leavings | Hull | the mud reclaims (built) | recede drops from a list (§3e) |
| **Fever Wood** | Hull, Carapace (two-front war) | **Overgrown**: ×0.8, vines must be cut (a plant on the cell) | Carapace | none | |
| **Rot** | Hull, Frame | **Digested**: ×0.6, drops "Sheen-glazed salvage casting" as an extra | Scrap + casting | none | the pinging ship is a set-piece, not this family |
| **Abyss** | Wind-farm vane, Pylon | **Storm-torn**: ×0.8 | Scrap/Tank (gravlite) | none | Ship in the Wall is `ABYSS_LIGHTFALL_BROOD_WRECK_1` |
| **Rust Cathedral** | none scattered; the walls are the salvage | **Sacred** (a flag, no scatter) | none | stripping costs faction goodwill | the Mending Weld rite reads this flag |
| **The Forge** | Salvage cache (built shell) | **Forge-warm**: ×1.0 | `RUT_FoundrySalvage` extra table | none | gets the §3c comp and art |
| **Grey Deep** (floor) | Hull, Spine | **Crystal-jacketed**: mine the jacket first | Hull + crystal shards | none | in the dive generator |
| **Twilight Deep** (floor) | Picked hull-rib (`RM_PickedWreck`, 1-2) | **Picked**: ×0.2, no loot roll | none ("nothing inside") | a Compact salvage-mark | yield is low on purpose |
| **Scald floor** | Hull (the surface S6 set, deeper) | **Cooked** | Hull | heat | per its floor sitting |
| **Propane Lake**, **Weeping Stones**, **Cauldron** | pending their sittings | | | | Weeping Stones is restore-or-strip (Q3); Cauldron is small finds only |
| **Greentide, Pyrelands, Slime, Contagion, Lantern Deeps, Webwork, Leaning Scrub, Terminator Sea** | none until Q1 is answered | | | | |

So about 8 weathering rows, about 7 families, and 15-18 biome scatter lists cover every promise.
Art: about 2 variants per biome × family pair, through the artpipe. **Search artpipe state first**
(`artpipe_state.py find wreck`), because the Scald renders and a landspeeder render already exist.

## 5. Mod ownership

| piece | owner mod | tier | why |
|---|---|---|---|
| Engine: `RM_WreckWeatheringDef`, `RM_WreckWeathering` extension, `RM_CompSalvageLoot`, `RM_GenStep_WreckField`, `RM_IncidentWorker_WreckFall`, family parents, weathering rows, loot tiers | **a new engine entry `Wreckage` composed into `mandrake.rm.biomes`** (group `engine`, beside EnvironmentalHazards and CreatureBehaviors in `src/RimMandrake/Biomes.compose.json`) | RM | every biome needs it, and biomes already ship as one composed mod (Q17). A standalone mod would add a load dependency for no gain. |
| Per-biome child defs + scatter list + registration patch | each biome's own folder (`src/RimMandrake/<Biome>/`) | RM | stays with the biome sitting that rules it |
| Canon hulls (TIE panel, skiff, landspeeder), Star Wars loot rows | `src/RimStarWars/StructureInjectionsSW` (already holds the crawler-road wrecks) | RSW | Q11a: canon is IP |
| Fall Line renewal list, Zeddo's Yard register, hulk, scrapfields | `src/RimUtinni/UtinniPatches` | RUT | campaign-only |
| AncientJunkClusters suppression / reskin | `FASCINATING_WORLD_JUNK_1` Phase 4 | per that item | not this item |

🔴 **Tier defect found.** `RUT_ScaldWreckHull/Tank/Frame` and their GenStepDefs carry the `RUT_`
(campaign) prefix but ship in **TerminalBiomes**, an `RM_` mod composed into `mandrake.rm.biomes`.
They are invented, not canon, so per Q11a they belong in `RM_`. The migration onto the family parents
(build step 2) is the moment to rename them. ⚠️ Renaming a placed building orphans every wreck already
in a save (CLAUDE.md, donor-retirement memory). The world is remade at the end, so this costs only
throwaway test saves, but say so in the commit.

**WreckedMachines is not the owner.** Its three-tier repair grammar is a different mechanism (§1c).

## 6. Mod Settings

The settings page is "Wreckage", inside the Baroque Biomes settings, built like the composed mods'
per-biome toggles.

| setting | default | effect |
|---|---|---|
| **Wreck fields** (master) | on | off: no `RM_GenStep_WreckField` runs on new maps. Existing wrecks stay; a GenStep cannot unplace them (the Scald's own reasoning, `RM_TerminalBiomesScaldKit.cs:58-60`) |
| **Per biome: wreck field** | on | one checkbox per biome that has a list, keyed by `settingsKey`, generated from the GenStepDefs, so no hand-written bool per biome. The Scald's existing "S6 — wreck salvage" folds into this and keeps `RM_MechanicGates` key `Scald.S6` as an alias |
| **Wreck density** | 1.0× (slider 0-3×, labelled "affects new maps only") | multiplies every `countPer10k`. This is the owner's "lots" knob |
| **Salvage loot on deconstruct** | on | off: the costList only, as in vanilla ShipChunk |
| **Loot generosity** | 1.0× (0.25-3×) | scales the ThingSetMaker value range |
| **Fresh wreck falls** (Fall Line, flotsam, flood strike) | on | off: the §3e incidents never fire |
| **Wreck hazards** (nests, radiation, lichen host) | on | off: the hazard comps are inert; the wrecks remain |

All-off leaves vanilla behaviour: the defs still load and are inert. Every toggle is registered in
`RM_MechanicGates` so that `modcheck` `suite.toggles` can flip it (debug_process §2.3).

## 7. Build plan for FOUNDRY

Each step is one item and one commit series, offline-first. A live check is needed only where a
step says so. Effort is rough.

| # | step | effort | proof |
|---|---|---|---|
| 0 | **Owner sitting**: §8 questions, plus `FASCINATING_WORLD_JUNK_1` Phase 3 cards for the family list. Blocks the names, not the engine | sitting | ruled roster as data (`junk_roster.json`, the target Phase 3 already names) |
| 1 | **Engine**: `Wreckage` compose entry; `RM_WreckWeatheringDef` + extension + resolve pass; `RM_CompSalvageLoot` (Deconstruct-only); `RM_GenStep_WreckField` with the custom-loader list; settings page; `RM_MechanicGates` keys; 6 family parents; 8 weathering rows; 5 loot tiers | M (about 400 lines of C#, 4 XML files) | selftest under `--mock`; quicktest: spawn one family wreck, deconstruct → costList×factor + a loot roll; smash → slag only |
| 2 | **Migrate the Scald** onto the framework: 3 defs reparented and renamed `RM_`; 3 GenStepDefs → 1; the S6 bool → per-biome key with alias. Art untouched | S | quicktest Scald map: wrecks only on `RUT_ScaldShallow`; toggle off → new map has none |
| 3 | **Desert band** (Desert, Deep Desert, Dune Sea/Stillsand, Long Shade): 4 lists; Long Shade's road GenStep reads the family list | S-M | one quicktest per biome; `SALVAGE_PALETTE` regen shows every new def in USABLE-YIELDS |
| 4 | **Warscar + Wasteland** (unblocks the Warscar lichen web) | S | lichen spawns adjacent to a wreck (state read) |
| 5 | **§3e wreck fall**: the incident + Fall Line list; refactor the Cracked Lands recede to read a list; Miasma flotsam trigger | M | debug-fire the incident → 1-4 wrecks land in the area; recede drops from the list |
| 6 | **Remaining land biomes** (Blue Desert, Nightside, Miasma, Cracked Lands, Fever Wood, Rot, Abyss, Forge cache loot) | M, 1 sitting each | per-biome quicktest |
| 7 | **Sea floors** (Grey, Twilight, Scald floor) via the dive generators | S | dive-map quicktest |
| 8 | **Art waves** through the artpipe: about 2 variants per new biome × family pair. Search first | daemon | no magenta (`prove-art-missing-first`) |
| 9 | **RSW/RUT layers**: canon hulls, Star Wars loot rows, Fall Line Imperial register | S | full-list load, zero new Config errors |

The steps are sequential up to 2, and 3-7 can be done in any order after that. There are no worldgen
or painting dependencies: the scatter is registered on the BiomeDef and runs wherever that biome is
painted, whenever that happens.

### First-script sketch (`design/RimMandrake/debug_process.md` §2)

The walk `design/validation_walks/RimMandrake/Wreckage.md`, `## must be true`:

```
1. Every RM_WreckFamily_* child resolves with a costList = family base × weathering.yieldFactor
   → defs.family_yield (t.get_defs "ThingDef/RM_ScaldWreckHull", read costList; compare to table)
2. A wreck field GenStep places wrecks only on its allowed terrain tag
   → mapgen.scald_tag (quicktest Scald map; list_things RM_ScaldWreck*; every cell's terrain carries RUT_ScaldShallow)
3. Deconstruct yields costList AND a loot roll; smash yields killedLeavings only
   → salvage.deconstruct / salvage.smash (spawn hull, designate deconstruct, step ticks, count things in radius)
4. Wreck fields toggle off → a new map of that biome has zero family wrecks
   → toggles.wreckfield_off   (in suite.toggles)
5. Loot toggle off → deconstruct yields costList only
   → toggles.loot_off
6. Density 0× → zero wrecks; 2× → count rises (ratio, not exact)
   → toggles.density
7. Wreck fall incident drops 1-4 wrecks from its list
   → incident.wreckfall (debug-fire; list_things before/after)
8. Every family def is deconstructible (never in SALVAGE_PALETTE's EXCLUDED bucket)
   → defs.deconstructible (offline: salvage_filter.py on the dump)
```

`## anti-guessing notes` seeded from what is already known:
- `RULED OUT: GenStep_ScatterThings takes a list — RUT_ScaldWreckScatter.xml header; singular <thingDef>.`
- `RULED OUT: inherited Light affordance works on shallows — RUT_ScaldWrecks.xml header; Walkable needed.`
- `RULED OUT: a <li> count measures a wreck list — custom element-name loader, same trap as <wildAnimals>.`
- Guard: a component goes red if any family def ends up in `SALVAGE_PALETTE` EXCLUDED.

Each check must be shown able to fail: run check 2 against a deliberately mis-tagged GenStep, and
check 3 with the loot toggle off.

## 8. Questions for the owner

**Q1. "Everywhere": does every biome get wrecks, even ones whose sheet is silent or said no?**
Eight biomes promise none (Greentide, Pyrelands, Slime, Contagion, Lantern Deeps, Webwork, Leaning
Scrub, Terminator Sea), and Lantern Deeps turned down the wreck rite.
- **A. Only where a sheet promises it.** About 20 biomes. This respects the sittings, and some
  places stay clean, so wrecks keep meaning "this region had a fall".
- **B. Everywhere, with a light default in silent biomes.** One or two small wrecks. This matches
  "all over the place", but blurs the Fall Line's identity as the wreck land.
- **C. Decide at each biome's own sitting.** This is slowest, but it is consistent with "biome by
  biome, not sweeping changes".

**Q2. What happens to the vanilla tanks, trucks and cars that spawn on every map today?**
- **A. Switch them off and let these wreck fields replace them.** This gives one coherent look, but
  it removes vanilla junk from non-Ash'karr maps too, unless that is behind a setting.
- **B. Reskin them as Star Wars junk** (`FASCINATING_WORLD_JUNK_1` Phase 4). They stay everywhere,
  and the wreck fields are added on top. This means more junk overall and more art.
- **C. Leave them for now.** The wreck fields come first, and the vanilla junk is decided at the
  Phase 3 roster sitting.

**Q3. Can a scattered wreck ever be repaired instead of stripped?**
Today they are separate: field wrecks are stripped for parts, and the Wrecked Machines are repaired
in tiers. Weeping Stones' condensers ("salvage or restore") and the Fall Line's live, powered wrecks
blur that line.
- **A. Never.** Field wrecks are always strip-only, which is simple and clear.
- **B. A rare few ("live" wrecks)** can be repaired through the Wrecked Machines tiers. This is a
  great find, but it adds a second mechanism to the field.
- **C. Only named set-pieces** (Weeping Stones condensers, the Ship in the Wall). The field stays
  strip-only.

**Q4. Should breaking a wreck apart give the same as taking it apart carefully?**
- **A. No: careful deconstruction adds a loot roll, and smashing gives slag.** (This is the design
  above.) It rewards the skilled path, which is the Jawa fantasy.
- **B. Both give the same.** This is simpler, and close to vanilla ship chunks.
- **C. Careful work gives loot, and the chance of rare parts scales with the colonist's skill.** This
  goes deepest, but it is one more number to balance.
