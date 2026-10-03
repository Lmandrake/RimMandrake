# SALVAGE_WRECKAGE_EVERYWHERE_1: design (placement, repair and salvage ruled 2026-10-03)

BENCH design helper, 2026-10-02; placement rewritten 2026-10-03 to the owner's rulings (§8). Design
only: no defs or code came out of this pass. Item filed by the owner 2026-09-25: *"I like the
wreckage you made, game should be filled with lots of this all over the place given it's salvage
focus."* The richer scavenging system the owner asked for on 2026-10-03 is pitched separately in
`design/RimMandrake/jawa_scavenge_system_pitch_2026-10-03.md`.

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
  ⇒ Ruled 2026-10-03 (§8): the named set-pieces (Weeping Stones condensers, the Ship in the Wall)
  **and a rare few field wrecks** are repairable through the Wrecked Machines tiers. Every other
  scattered wreck is strip-only. §3d says how a field list carries the repairable few.
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
| **Grey Deep** (sea) | "the jacketed salvage": wrecks chiselled free from crystal (`the_grey_deep.md:366,463`, ruled) | none | crystal-jacketed wreck family on the floor map (inside the floor map generator, not a tag; see §1a's Grey precedent) |
| **Twilight Deep** (sea) | "the wrecks of the impatient"; `RM_PickedWreck`, 1-2 per floor, hull-rib with a salvage-mark and **nothing inside** (`the_twilight_deep_content_2026-09-26.md:816-823`, proposed) | none | the picked-clean family (low yield by design) |
| **Propane Lake** (sea) | sealed ancient cartridges, an unfinished pipeline junction (floor agenda `:219-221,389`, proposed) | none | pending its sitting |
| **Nightside Ice** | failed Junker crystal expeditions; "a seam of wreckage" (`nightside_ice.md:135`, ruled; review option proposed) | none | an ice-locked expedition-wreck family |
| **Weeping Stones** | ancient condenser arrays to salvage **or restore** (`weeping_stones.md:165,284`, ruled) | none | a restore-or-strip choice, which is WreckedMachines' grammar, not a strip family (ruled repairable, §8) |
| **Cauldron** | corroded ruins and small finds (a spent filter cartridge, a hauled-in tank); it **contrasts itself** with the dayside wrecks (`cauldron.md:227-230`) | none | small-finds scatter only, no hulls |
| **Sump** | Junker stations (derricks, barrel yards) (`the_sump.md:151,161`) | dig-stratum table | none: the Junker stations are structures, not wrecks |
| **Greentide, Pyrelands, Gelatinous Slime, Contagion, Lantern Deeps, Webwork, Terminator Sea, Leaning Scrub** | **nothing promised** (grep-only for Pyrelands and the Propane Lakes sheet). Lantern Deeps declined the Inherited Wreck **rite** (`lanterndeeps_bedazzle_review_2026-10-01.md:261`), which is a rite, not a scatter | none | density comes from the placement law (§3d), not from the sheet's silence |

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
stripping properly gives the costList **plus** a roll. It reads the family's loot tier, shifts it by
the weathering, and generates from a `ThingSetMakerDef` named `RM_SalvageLoot_<Tier>`.

**Ruled 2026-10-03: the rare-part chance scales with the salvager's skill.** `PostDestroy` is not told
who did the work, and vanilla deconstruction has no skill term at all: `GenLeaving`'s Deconstruct
branch is `count × resourcesFractionWhenDeconstructed`, and `JobDriver_Deconstruct` only trains
Construction (RimSage, read 2026-10-03). So a Harmony **prefix** on `JobDriver_Deconstruct.FinishedRemoving`
stashes the pawn before `Destroy` runs and the comp reads it. The Ninefold mod already patches that
method (`src/RimMandrake/Ninefold/Source/Patch_BuildingDeconstructed.cs`, a postfix), so the hook point is
proven. How far skill reaches beyond the rare roll is the scavenging pitch's question, not this one.

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
named in their floor map generator's `<genSteps>` (the Grey precedent: the floor terrain tag is shared by
all four seas, so a tag would leak). ⚠️ Element-name-as-key lists (the `<RM_ScaldWreckHull>1</…>`
form) need a custom loader, like `BiomeAnimalRecord`. Use the same `LoadDataFromXmlCustom` pattern
and **never** a `<li>` form, so that a roster counter does not read zero (see CLAUDE.md, `<wildAnimals>`).

### 3d-i. The placement law (owner, 2026-10-03)

The owner's ruling, by question card with typed answers: crashed ships are **rare**, and anything that
falls where people live or travel is **cleaned off the surface within a few decades**. So a wreck
**persists only where a biome is hostile or inaccessible and far from normal travel**, which is
*"perfect for the Utinni to visit"*. Every **sea floor** is high density, because *"almost no one can or
would bother to go there"*. The **Contagion** has wrecks, but it erodes them and little remains. The
**deep nightside** is *riddled* with them.

Density therefore follows **one axis, how long a wreck survives there**, and that is set by two things:
how hard the place is to reach, and whether the place itself eats metal. It never follows how many
ships fell, since falls are rare everywhere. One consequence follows directly: **the remoter the
wreck, the less it has been picked over**, so persistence and yield rise together (the nightside cold
also stops corrosion, the premise of the superseded `wreck_fields.md` sheet).

| class | why wrecks last there | count per 10k cells (INVENTED, tuned live) | yield / loot shift | repairable few (§8 ruling 2) |
|---|---|---|---|---|
| **Riddled** | deep nightside: nobody goes, the cold stops corrosion | 6-10, cluster chance 0.5 | ×1.0, loot +1 tier | yes, highest weight |
| **High** | sea floors: only a gravship gets down | 4-6, cluster chance 0.3 | ×1.0, +1 tier (except where a sheet rules otherwise) | yes |
| **Moderate** | hostile land: lethal terrain, heat, radiation, rot; few visitors | 1.5-3 | per weathering row (§3b) | rare |
| **Low** | hostile but crossed, or the land buries and reveals | 0.3-0.8 | per weathering row | no |
| **Eroded** | the Contagion: present, but the biome eats them | 1-2 fragments | ×0.2, Scrap tier only, no rare roll | no |
| **Cleaned** | inhabited or travelled: cleared within decades | **0 scatter**. A fresh crash arrives as an event (§3e), never as map-gen | n/a | no |
| **Fresh** | the Fall Line: the falling outruns the cleaning | delivered by §3e, renewable | +1 tier | 1 in 10 live/powered |

**Per-biome assignment.** This is BENCH's reading of each biome's sheet against the law; a biome's own
sitting may move its row (the owner's "biome by biome" rule), and the table is the paint-list's source
until then.

| biome | class | reason in one line |
|---|---|---|
| **Nightside Ice** | Riddled | deep nightside; the sheet already has failed Junker expeditions |
| **Lantern Deeps** | Riddled | deep nightside; its sheet declined a wreck *rite*, which is not a scatter |
| **Cauldron** | Riddled at its nightward edge, else Moderate | its sheet contrasts its finds with the dayside; the sitting fixes where the line falls |
| **Grey Deep, Twilight Deep, Propane Lake, Terminator Sea, Scald** (floor maps) | High | every sea floor, by ruling. Twilight Deep's `RM_PickedWreck` stays low-yield: that is its own sheet's law, not a density |
| **The Scald** (shallows) | Moderate | the shallows burn every trip |
| **Warscar** | Moderate | a live war zone few cross; but "plundered to skeletons", so yield stays ×0.35 |
| **Wasteland** | Moderate | radiation keeps people out |
| **Blue Desert** | Moderate | ice-locked and remote; the ablation incidents stay the main route |
| **Abyss** | Moderate | a chasm; the Ship in the Wall is its own item |
| **Rot** | Moderate | the gut eats people too; it digests wrecks slowly (weathering ×0.6) |
| **Webwork, Pyrelands, Gelatinous Slime, Fever Wood, Miasma, Weeping Stones** | Moderate | each is lethal or hostile to cross; Weeping Stones' condensers are repair set-pieces on top |
| **Dune Sea / Stillsand** | Low | remote, but the sand buries and reveals; finds are sealed and intact |
| **Deep Desert** | Low | its sheet already rules wrecks rare |
| **Cracked Lands / Flooded Canyon** | Low | floods expose and the mud reclaims (built) |
| **The Contagion** | Eroded | by ruling |
| **Desert, Arid Shrubland, Greentide, Leaning Scrub, Long Shade** | Cleaned | travelled land. The Jawa scrapfields' slag is consistent: slag is what cleaning leaves. Long Shade's crawler-road wrecks are fresh casualties of the road, not a field |
| **Rust Cathedral, The Forge, Sump** | Cleaned | inhabited; the Cathedral's walls are sacred salvage (a flag, not a scatter), the Forge cache is one placed thing |
| **Fall Line** | Fresh | delivered and renewed (§3e) |

⚠️ **One existing build disagrees with the law**: the Jawa ground hulk is stamped once on **every**
desert map (`JawaGroundHulk.xml`, count 1), which is travelled land. It is a card question in the
scavenging pitch, not a change made here.

**Implementation.** Each class is a row of a small `RM_WreckDensityClassDef` (count range, cluster
chance, loot shift, repairable weight) and a biome's GenStepDef names its class instead of restating
numbers, so re-tuning "High" re-tunes every sea. The Mod Settings density multiplier (§6) scales all
classes. **The repairable few:** a list may name a Wrecked Machines Wrecked-tier def (for example
`RM_WM_AutomatedSmelter` Wrecked) at the class's repairable weight. It is placed like any wreck and then
climbs the existing Kludged and Repaired tiers, so no new repair code exists in this framework. That
depends on the resurrection design's ruling that sacred scrap is a clan policy, not an undeconstructible
def (`design/Jawa/wrecked_machines_resurrection.md`, change 4).

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
| **Deep Desert** (Low; Desert is Cleaned, §3d-i) | Speeder, Hull, rare | **Sand-scoured**: ×0.6, sand leavings | Scrap/Hull | wreck shade pocket | Desert keeps only the scrapfields slag; the hulk is a card question |
| **Dune Sea / Stillsand** | Hull, Tank, Tread | **Sealed**: ×1.0, +1 tier | Sealed (intact parts, chemfuel) | half-buried; a storm-reveal variant later | "uncorroded" is the sheet's own law |
| **Long Shade** (Cleaned, §3d-i) | road casualties only: Skiff (`RSW_`), Cart (`RM_`, built), Tread (built) | **Sun-baked**: ×0.8 | Hull/Speeder | none | the crawler road is the placement (`RM_GenStep_CrawlerRoad`); no field scatter beside it |
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
| **Grey Deep** (floor) | Hull, Spine | **Crystal-jacketed**: mine the jacket first | Hull + crystal shards | none | in the floor map generator |
| **Twilight Deep** (floor) | Picked hull-rib (`RM_PickedWreck`, 1-2) | **Picked**: ×0.2, no loot roll | none ("nothing inside") | a Compact salvage-mark | yield is low on purpose |
| **Scald floor** | Hull (the surface S6 set, deeper) | **Cooked** | Hull | heat | per its floor sitting |
| **Propane Lake** (floor, High), **Weeping Stones** (Moderate), **Cauldron** (Riddled/Moderate) | families pending their sittings | | | | Weeping Stones' condensers are repair set-pieces (§8 ruling 2); Cauldron is small finds only |
| **Nightside Ice, Lantern Deeps** (Riddled) | Expedition rig, Tank, Hull | **Frozen**: ×1.0, +1 tier, no corrosion | Hull/Tank, Junker tools | none | the densest fields on the planet |
| **Contagion** (Eroded) | fragments of any family | **Eroded**: ×0.2, Scrap only | Scrap | none | little remains, by ruling |
| **Pyrelands, Slime, Webwork, Terminator Sea floor** (Moderate / High) | pending their sittings | | | | **Greentide, Leaning Scrub** are Cleaned: no scatter |

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
| 0 | **Owner sitting**: the scavenging-system cards (`Transient/jawa_scavenge_cards_2026-10-03.json`), plus `FASCINATING_WORLD_JUNK_1` Phase 3 cards for the family list. Blocks the names, not the engine | sitting | ruled roster as data (`junk_roster.json`, the target Phase 3 already names) |
| 1 | **Engine**: `Wreckage` compose entry; `RM_WreckWeatheringDef` + extension + resolve pass; `RM_CompSalvageLoot` (Deconstruct-only); `RM_GenStep_WreckField` with the custom-loader list; settings page; `RM_MechanicGates` keys; 6 family parents; 8 weathering rows; 5 loot tiers | M (about 400 lines of C#, 4 XML files) | selftest under `--mock`; quicktest: spawn one family wreck, deconstruct → costList×factor + a loot roll; smash → slag only |
| 2 | **Migrate the Scald** onto the framework: 3 defs reparented and renamed `RM_`; 3 GenStepDefs → 1; the S6 bool → per-biome key with alias. Art untouched | S | quicktest Scald map: wrecks only on `RUT_ScaldShallow`; toggle off → new map has none |
| 3 | **Riddled and High first** (the law's densest places): Nightside Ice, Lantern Deeps, the Cauldron's nightward edge, and the sea floors (Grey, Twilight, Propane Lake, Terminator, Scald floor) named in their floor map generators; plus `RM_WreckDensityClassDef` and the repairable-few list entry | M | one quicktest per biome; a floor map holds wrecks at the High count; `SALVAGE_PALETTE` regen shows every new def in USABLE-YIELDS |
| 4 | **Warscar + Wasteland** (unblocks the Warscar lichen web) | S | lichen spawns adjacent to a wreck (state read) |
| 5 | **§3e wreck fall**: the incident + Fall Line list; refactor the Cracked Lands recede to read a list; Miasma flotsam trigger | M | debug-fire the incident → 1-4 wrecks land in the area; recede drops from the list |
| 6 | **Moderate, Low and Eroded land** (Blue Desert, Miasma, Cracked Lands, Fever Wood, Rot, Abyss, Webwork, Pyrelands, Slime, Weeping Stones, Dune Sea/Stillsand, Deep Desert, Contagion; Forge cache loot) | M, 1 sitting each | per-biome quicktest |
| 7 | **Cleaned biomes**: confirm zero scatter; Long Shade's crawler road reads the family list | S | quicktest Desert map: no field wrecks, slag only |
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

## 8. Owner rulings (2026-10-03, question card, answers typed)

1. **Placement.** Wrecks are rare and cleaned off within decades, so they persist only where a biome is
   hostile or inaccessible and far from normal travel. All sea floors high; the Contagion eroded; the
   deep nightside riddled. Realised as the law and table in §3d-i.
2. **Repair.** The named set-pieces (Weeping Stones condensers, the Ship in the Wall) **and** a rare few
   field wrecks are repairable through the Wrecked Machines tiers: *"it's a scavenger game, so this
   really should be honored"*. Realised as the repairable-few list entry in §3d-i.
3. **Vanilla junk.** Reskin the vanilla tanks, trucks and cars as Star-Wars-adjacent junk, with lots of
   variety, right away. Handled by a separate art pass, not by this design.
4. **Smash versus care.** Careful salvage gives loot, and the rare-part chance scales with the
   colonist's skill (§3c). The owner also asked whether this can grow into a richer system: *"Jawa
   SCAVENGE. It's what they do, and they're good at it."* That is pitched with options in
   `design/RimMandrake/jawa_scavenge_system_pitch_2026-10-03.md`, and its questions are cards in
   `Transient/jawa_scavenge_cards_2026-10-03.json`.
