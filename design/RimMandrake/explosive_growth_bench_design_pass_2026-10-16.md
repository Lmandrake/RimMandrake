# Explosive growth: BENCH design pass on the consensus model (2026-10-16)

Item: `EXPLOSIVE_GROWTH_RETHINK_SERIOUS_CONCERNS`. Input:
`design/RimMandrake/explosive_growth_consensus_2026-10-16.md` (cited as "consensus §n"), whose §1 holds the owner's
verbatim words; those words are the authority here. Earlier context:
`design/RimMandrake/explosive_growth_deep_dive_2026-10-16.md` ("deep dive §n"). Code read:
`src/RimMandrake/ExplosiveGrowth/Source/` (the engine, a member of Baroque Biomes, `mandrake.rm.biomes`).

Status: **PROPOSAL**. Nothing here is ruled. The consensus doc and the code were not edited.

**Tags.** **MEASURED** = read from a file, a def, the decompiled assembly or the 1.6 source (cited). **UNMEASURED** =
not checked; say so before relying on it. **INFERRED** = arithmetic on measured values, reasoning shown.
**PROPOSED** = a number or rule this document invents.

**Instruments used.**
- Vanilla 1.6 source and defs: RimSage (`Source/RimWorld/...`, `Defs/...` paths below).
- Live def dump: `DefDump/captures/2026-10-16T09-47-54Z` (game 1.6.4871). **Fingerprint check, MEASURED:** the
  dump lists 549 mods; the live `ModsConfig.xml` lists 548 active; 0 active mods are missing from the dump, and 1 dump
  mod is no longer active. The dump therefore describes today's full list, plus one extra mod.
- VFE Farming's `1.6/Assemblies/VFEF.dll` (workshop 1957158779), decompiled with ilspycmd. Only the two sprinkler
  types were read.

---

## 0. The five corrections that matter most

1. **At ×0.25, most of our plants die of old age before they mature (MEASURED inputs, INFERRED result).** Vanilla
   plants age on every long tick whatever their growth (`Plant.cs:840` `ageInt += 2000`). They start dying once age
   passes `growDays × lifespanDaysPerGrowDays` (`PlantProperties.cs:219`, `Plant.cs:210`). The default multiplier is
   8, and 218 of our 358 plant defs use it. A regrown sprout starts at growth 0.15 (`Plant.cs:22`;
   `WildPlantSpawner.cs:459` passes `setRandomGrowth=false`).
   - At ×0.25 on fertility-1 ground, a sprout needs 6.2 × growDays calendar days to mature. Only 8 of our plants die
     first.
   - On poor ground (fertility factor 0.55, which is sand 0.1 at the default sensitivity 0.5), it needs 11.2 ×
     growDays. Then **267 of 358** die first.
   - At the C6 option ×0.1 the figure is 281 of 358 even on good soil.
   - A sown vanilla crop on fertility-0.7 soil has the same problem: rice needs 8.8 × growDays against a lifespan of
     8 × growDays.
   - The consensus's "barely grow" therefore becomes "never grows up" unless **the age clock slows with the rate**
     (§4, card WP2).
2. **Hydroponics would fall to ×0.25** (MEASURED: nothing in the engine reads the grower building). The consensus
   never names a grower. Vanilla's own moisture rule exists and already exempts them. The Odyssey drought, a ×0.3
   growth factor (`GameCondition_Drought.cs:7`), is skipped for any plant cultivated in a building with a `sowTag`
   (`Plant.cs:393-397`; `BuildingProperties.SupportsPlants => sowTag != null`, `BuildingProperties.cs:430`). Basins
   need a rule (§1, card H1).
3. **Pulsed water beats steady water** (INFERRED from the consensus's own timers). With "3 days to settle, 2 days dry
   to re-arm", a field watered 3 days on and 2 days off averages (3×10 + 2×0.25)/5 = **×6.1**, and it fruits every 5
   days. A field watered without a break averages ×4 and fruits once. The best play is to *stop* watering, which
   saves labour and water and grows faster. That contradicts S4's intent, under which permanent wet is the
   *reduced* case. It only stops paying when re-arm ≥ 6 days, or when settled-wet is computed from a moving average
   (§7, card EC2).
4. **Natural rain falls on biomes whose flora the consensus classes as dry-adapted, so those biomes get recurring
   map-wide waves** (MEASURED weather weights, live dump). In water-rain share of `baseWeatherCommonalities`:
   - Webwork 19%, Twilight Sea 17%, Contagion 12.5%;
   - Contagion's `RM_ContagionBloom` takes another 87.5%, so A4 decides whether that map is ever dry.

   None of the three is wet-adapted under consensus §3.2. Each rain on a map dry for 2 days fires the whole map:
   ×10, then fruit, then a 15% burst chance per plant, with pawn stun. The consensus treats map-wide rain as a rare
   perf case only (§5, card WP3).
5. **Wood plants on a fast clock, and the missing tree numbers** (MEASURED, dump). Some issues are gaps in the
   consensus; others are faults in our defs that ×10 magnifies.
   - The engine's tree test is `def.plant.IsTree`, which is `harvestTag == "Wood"` or `forceIsTree`
     (`RM_ExplosiveGrowthRegistry.cs:207`; `PlantProperties.cs:207-214`).
   - **6 of our 47 wood-yielding plants** are not trees by that test, so they would get the full ×10. They are
     `RM_Varnoth` (60 logs in 30 days), `RM_TreeMushroom`, `RM_Kollavane`, `RM_IlbareenDead`, `RM_Ammeth` and
     `RM_Sodderel`.
   - Among the "trees", `RM_SicklyGlowMushroom` gives 25 logs in **2** growDays. Watered at ×6.25 that is about **43
     logs per cell per calendar day**. The dump's `Plant_TreeOak` (46 logs, 30 days) gives 0.84 a day at vanilla
     speed.
   - The consensus also gives no **dry** or **wet-adapted-home** rate for trees (§7, card EC1).

Second-tier corrections, each in its section:
- The Soak Zone and the timer switch are **dev-mode map-maker markers**, not player buildings (MEASURED,
  `FloodedCanyon/Defs/ThingDefs_Buildings/RM_BiomeMapControls.xml:21`; `FlowWorks_MapControls.xml:88-95`). The
  consensus lists the Soak Zone as a player source.
- The VFE sprinkler makes water from power alone (§2).
- Vanilla `Drought` would multiply with our dry rate, giving ×0.075 (§1).
- The live biome numbers are not the XML numbers, because Map Designer rewrites them (§8).
- Wasteland, the Sump and Flooded Canyon have no precipitation at all (owner 2026-10-16, OQ-3); snow falls only in RUT_FuelSnows and RUT_Umbra, and it melts like rain (§5).

---

## 1. Hydroponics: vanilla basins and modded growers

**What the consensus says.** Nothing. §4.2 lists water sources by cell. A plant in a basin stands on a cell with no
source, so under §4.3 it is "dry", ×0.25.

**What is true (MEASURED).**
- `Plant.GrowthRate` = fertility × temperature × light × noxious haze × drought (`Plant.cs:301`). It has no moisture
  term.
- A basin raises growth only through **fertility**: `HydroponicsBasin` `<fertility>2.8</fertility>` (RimSage def).
  The fertility grid reads the building.
- **Vanilla already has a "watered" exemption.** `GrowthRateFactor_Drought` (`Plant.cs:385-409`) returns 1 when the
  plant is `CurrentlyCultivated()` and its edifice has `SupportsPlants` (that is, a `sowTag`), and for cave plants.
  Otherwise it returns 0.3 while the Odyssey `Drought` condition runs. Ludeon's model is that a grower is
  self-watered and open ground is not.
- `SupportsPlants` is true for **every** `sowTag`, `SupportPlantsOnly` included. That covers sleeping spots, party
  spots and ritual spots (MEASURED: 57 defs with a `sowTag` in the dump). It is too loose to copy as it stands.
- Today's build: basins get the ×4 band like any plant and never soak (MEASURED: no `sowTag`, `PlantGrower` or
  edifice test in `RM_ExplosiveGrowthPatches.cs` or the kernel).

**The growers in today's list (MEASURED, dump; class `Building_PlantGrower` unless noted):**

| def | mod | sowTag | fert | power | proposed moisture |
|---|---|---|---|---|---|
| `HydroponicsBasin` | Core | Hydroponic | 2.8 | 70 W | **sealed-wet** |
| `VFE_Hydroponics_Tilable` | VFE Farming | Hydroponic | 2.8 | yes | sealed-wet |
| `VGE_Agrocell` | VGE Gravship (`Building_Agrocell`) | Hydroponic | 3.2 | yes | sealed-wet |
| `VQEA_AncientGreenbed` | VQE Ancients | Hydroponic | 3.6 | yes | sealed-wet |
| `VFE_Ecosystem`, `_Tilable` | VFE Farming | Ground | 3.5 | yes, glower | sealed-wet |
| `RM_FungiponicsBasin` | Baroque Biomes | RM_Fungiponics | 2.8 | yes | sealed-wet (its fungi are exempt as cave plants anyway) |
| `RM_ChillCryoponicsVat` | Baroque Biomes (`RM_Building_CryoGrower`) | RM_ChillBed | 1 | yes | sealed-wet |
| `RM_GlowTank` | LuminousPigment | RM_GlowTank | 1 | yes | sealed-wet |
| `RM_ConstellationCageSphere/Cube` | Baroque Biomes | RM_ConstellationCage | 1 | none | UNMEASURED fiction; default sealed-wet |
| `RM_ChillFloorBed` | Baroque Biomes | RM_ChillBed | 1 | none | **inherits the cell** (a floor bed on the ice) |
| `VFE_PlanterBox`, `_Tilable` | VFE Farming (`Building_PlantGrower_NoEmptyLines`) | Hydroponic | 0.95 | none | **inherits the cell**. VFE's own sprinkler deliberately reaches through planter boxes (§2), so VFE treats them as outdoor soil |
| `PlantPot`, `PlantPot_Bonsai`, `VFE_LongPlantPot`, `VFE_DecorativePlantPot` | Core / Ideology / VFE | Decorative(Tree) | 0.95–1 | none | sealed-wet (somebody waters a pot; vanilla's drought agrees) |
| `VFEFactory_Autofarmer` | VFE Factory | Ground | −1 | yes | inherits the cell (it farms the ground under it; whether its class derives from `Building_PlantGrower` is UNMEASURED) |

**Recommendation.**
1. Add a **fourth cell state, "sealed-wet"**: a plant whose edifice is a `Building_PlantGrower` (not merely
   `SupportsPlants`) counts as permanently watered. It never makes a fresh event, never arms and never fruits, the
   same as settled-wet ground. It needs no per-cell storage: one `GetEdifice` read per plant per long tick. That is
   the same read vanilla's drought factor already makes (INFERRED cost: one grid read).
2. Data, not code: a `DefModExtension` (`RM_GrowerMoisture { inheritCell = true }`) on the few growers that should
   read the ground instead (`RM_ChillFloorBed`, the VFE planter boxes, the autofarmer). The extension is patched onto
   the VFE defs with `PatchOperationFindMod`.
3. **The rate in a basin**: sealed-wet uses the settled rate (×4) under card H1 option 1. Economy (INFERRED, §6
   method): vanilla rice in a basin makes 2.8 × 0.055 = 0.154 nutrition per cell per day, so about 10.4 basin cells
   feed one colonist. At ×4 it makes 0.62, so 2.6 cells. Today's build already gives basins ×4, so option 1 changes
   nothing for hydroponics players.
4. **Vanilla Drought stacking.** In scope, our rate should **replace** `GrowthRateFactor_Drought` rather than
   multiply it. Otherwise a dry plant runs 0.25 × 0.3 = ×0.075. Today this is reachable only with the campaign's
   `scopeAllBiomes` on vanilla Grasslands, because `DroughtInitial` and `Drought` list only `Grasslands`
   (`Defs/Odyssey/IncidentDefs/Incidents_Map_Misc.xml:133-172`). It costs a few lines (divide out the drought factor
   when ours applies). PROPOSED.

**H1. Do plants in hydroponics basins and pots count as watered?**
1. *(Recommended)* **Yes, always wet at the settled rate (×4), and they never fruit or burst.** Basins work as they do
   today. *Trade: basins become the easy way around the water rule indoors, but they cost power and steel, and
   vanilla's drought already treats them this way.*
2. Yes, at the full watered rate (×10). *Trade: about one basin cell feeds a colonist; indoor farming outclasses
   every irrigated field.*
3. No, they follow the ground (dry ×0.25 unless watered). *Trade: a basin, "an artificial nutrient bath", is dry;
   hydroponic rice falls to 0.7× vanilla.*
4. *(write your own)*

---

## 2. Sprinklers

**What the consensus says.** Nothing. No sprinkler appears in §4.2.

**What exists (MEASURED).**
- **Our mods: no sprinkler.** No def in `src/` or the dump whose name or label matches sprinkler, irrigation,
  watering or mister, apart from `RM_Webwork_Gutter`. The gutter is a "silk irrigation gutter" by its label, but its
  comps are web-sense and specimen comps only. It has no watering behaviour (`src/RimMandrake/Webwork/Defs/ThingDefs_Buildings/RM_WebworkStructures.xml`).
- **The active list has one: `VFE_Sprinkler`** (Vanilla Furniture Expanded – Farming, `vanillaexpanded.vfefarming`,
  load order 333). Def: radius 5.8, 250 W, 40 steel and 1 component, research `VFE_Res_Sprinkler`. What it does
  (decompiled `VFEF.VFEF_SprinklersManager.MapComponentTick` and `BoostPlantAt`):
  - it acts only during local hour 7, at most once per 57,500 ticks, and only while powered;
  - for each cell in its radius (cells already claimed by an earlier sprinkler are skipped), it adds **`plant.Growth
    += 0.04`** to the plant there, unless the plant is a tree, or another building stands on the cell (the
    `VFE_PlanterBox` and `VFE_PlanterBox_Tilable` exceptions are let through);
  - it writes no moisture state and reads no water. It is a flat growth gift, about 105 cells (πr², INFERRED).
- Today's interaction: the +0.04 bypasses `GrowthRate`, so neither our bands nor our soak see it. On rice (3
  growDays) at vanilla speed, +0.04 a day is +22% (INFERRED: 0.55/3 = 0.183 a day). In our proposed dry ×0.25 world
  it is **+87%**, the largest single growth source on a dry field.

**What is wrong.** A sprinkler conjures water from electricity. On this world *"the limit on agriculture is WATER"*
(`design/Jawa/worldbuilding/PLANT_GROWTH_SPEC.md:60`), and the owner's 12:18 sentence (*"won't be growing almost at
all unless water is present"*) makes water the switch. A power-only sprinkler bypasses the whole water economy.

**Recommendation.**
1. **The VFE sprinkler does not water our cells by default.** Its own +0.04 a day stays (it is VFE's mechanic, and
   patching it out is rude to a mod we do not own). In our dry world that is a modest, honest boost.
2. If watering by sprinkler is wanted, it should **cost water**. Hook `VFEF.CompSprinkler.StartSprinklingMotes`
   (reflection-soft, guarded by `PatchOperationFindMod`-style presence, never a dependency). Each sprinkle waters the
   affect cells for 1 day **only if** it draws N litres from a FlowWorks tank or pipe in range. A daily sprinkle never
   leaves a cell dry for 2 days, so the field settles after 3 days to ×4. This is a "steady-wet field" device, never
   a fruiting engine.
3. Our own equivalent belongs in **FlowWorks** (another agent's mod): a drip line on a FlowWorks pipe that waters its
   strip for as long as litres flow. It is the same "sustaining" source as an irrigation channel (consensus §4.2),
   without digging. It is not needed for the sprint.

**SP1. Should a sprinkler water plants under the water rule?**
1. *(Recommended)* **Not by itself: VFE's sprinkler keeps its small daily boost; watering comes only from real water**
   (channels, floods, rain, hand watering). *Trade: an installed VFE sprinkler looks like it "doesn't work" for our
   rule; a tooltip line is needed.*
2. Yes, a VFE sprinkler waters its circle while it has water from a FlowWorks tank in range. *Trade: a cross-mod hook
   into two mods (VFE and FlowWorks).*
3. Yes, on power alone. *Trade: 250 W turns any desert into a ×4 field; water stops mattering.*
4. Build our own FlowWorks drip line instead (later). *Trade: new building, art and another agent's mod.*
5. *(write your own)*

---

## 3. Hand watering

**What the consensus says.** W4 asks whether players may pour water. Option 1 is the hose Outflow spill; option 2
is "a water plants job with bottles". It states no cost.

**What exists (MEASURED).**
- No "water a plant" job exists. FlowWorks' bottle work-givers are fill, wash, empty-into-tank and fill-from-tank
  (`src/RimMandrake/FlowWorks/Defs/LiquidTypes/WorkGiverDefs/RM_LiquidBottleWorkGivers.xml:19-70`).
- A FlowWorks bottle holds **1.5 L** (`RM_LiquidBottles_Base.xml:107`).
- Water is scarce by design. The Leaning Scrub `RM_WindVaporator` spawns **4 `RM_FogWater` per ~1 day**
  (`CompProperties_Spawner`, 54,000–66,000 ticks;
  `src/RimMandrake/LeaningScrub/Defs/ThingDefs_Buildings/RM_WindVaporator.xml`). Its own text says *"a thin,
  reliable margin, never a living"*. How many litres one `RM_FogWater` holds is UNMEASURED.
- Vanilla work costs (dump): rice, corn and potato `sowWork` 170 and `harvestWork` 200 ticks per plant.

**Labour arithmetic (INFERRED).**
- **Labour per unit of food does not depend on the growth rate.** Sow plus harvest is 370 ticks per plant. Rice
  gives 6 × 0.05 = 0.3 nutrition, so farming costs about **1,233 work-ticks per nutrition** at any multiplier.
  Growth speed changes **land and calendar time**, not labour per meal.
- A colonist eats 1.6 nutrition a day (`Need_Food.cs:11,218`: 2.667e-5 a tick × 60,000 × `baseHungerRate` 1).
  Farming that costs about 2,000 work-ticks a day per colonist, whatever the rate.
- Hand watering adds labour **per cell per day**, not per meal. Take PROPOSED costs of 40 ticks a cell plus a 450-tick
  round trip per 9-cell refill: about 90 ticks per cell per day.
  - At ×10, rice makes 0.55 nutrition per cell per day, so watering costs 164 ticks per nutrition: **+13%** on
    farming labour.
  - At ×4 (settled), it is 0.22 per cell per day, so 410 ticks per nutrition: +33%.
- Against those costs, dry ground needs 116 cells per colonist at ×0.25 and still risks the lifespan death of §0.1.
  **Hand watering pays by a wide margin wherever water exists.** The real limit is litres, not pawn time. Litres per
  cell is a tuning number: PROPOSED 0.5 L per cell per day, so a bottle waters 3 cells.

**Shape (PROPOSED).**
- **Not a bill.** Bills belong to workbenches.
- **Not a per-cell designation.** Re-designating dozens of cells every day is tedious.
- **A toggle on the growing zone** ("Water this zone", next to vanilla's allow-sow and allow-cut gizmos) plus a
  `WorkGiver` under **Growing**. It picks a dry, sown cell of a flagged zone, fetches a water container through the
  FlowWorks liquid API, and waters up to 3 cells per bottle. Each pour is a source with a 1-day duration (consensus
  §4.2 row "players pouring water"). The first pour on a field dry ≥ the re-arm time is a **fresh** event.
- **Cross-mod:** the job lives in the engine; the water draw reads FlowWorks containers reflection-soft, the same way
  `FlowWorksIrrigationRead` does today. Without FlowWorks the toggle is hidden.
- The hose Outflow hook (W4 option 1) is **complementary**. It is cheaper to build and automatic, but it waters one
  spill cell, not a field.

**HW1. Should pawns water crops by hand?**
1. *(Recommended)* **Yes: a "water this zone" switch on growing zones; pawns carry bottled water from FlowWorks
   (about 3 cells a bottle, 1 day each).** Water, not time, is the cost. *Trade: a new job and a cross-mod read of
   FlowWorks; about +13% farm labour at ×10.*
2. Hose only (W4 option 1): water leaving an Outflow end waters that spot. *Trade: no job, but fields are watered one
   spill cell at a time.*
3. No hand watering; channels and floods only. *Trade: a colony with no channel site cannot farm outdoors in a
   desert.*
4. *(write your own)*

---

## 4. Wild plants: do dry-adapted wild plants ever see ×10?

**What the consensus implies.** ×10 comes from a fresh event. The natural fresh sources are rain, snowmelt, canyon
floods, Odyssey floods, the Miasma surge and the Bloom event. Natural permanent water (W2) only ever settles ground
(×4) and never fruits.

**Per biome, natural fresh water (MEASURED weather weights, live dump; INFERRED consequence):**

| biome (RM_ and RUT_ twin) | natural fresh water for wild plants | wild dry-adapted plants see ×10? |
|---|---|---|
| Stillsand, Long Shade, Leaning Scrub, Weeping Stones, Cauldron, Blue Desert, The Forge, Abyss, Warscar, The Scald, The Chill, Grey Sea | **none** (0 weight on every water-rain weather; no flood system) | **never**, unless the player waters them |
| Flooded Canyon | canyon flood (fresh; deep dive §1.3). Rain weight **0** in the live dump (consensus §4.2 says Rain 0.5; the live dump disagrees) | yes, in the flood footprint, on the flood clock |
| Wasteland, The Sump | **no precipitation** (weathers zeroed, commit `607aecf946`, owner 2026-10-16) | no |
| Webwork, Twilight Sea, Contagion | water rain: 19%, 17%, 12.5% of weight | **yes, map-wide, recurring** (§5) |
| Greentide, Miasma, Fever Wood | rain 18%, 58%, 0% | natives are wet-adapted, ×10 always; only foreign dry plants fire |
| Pyrelands | `RM_FE_BlackRain` (3 of 88) is not water | card C5 (fire as the trigger) |
| Gelatinous Slime | `RM_Weather_SlimeRain` 30 of 72 | if slime counts (A13, T2), a fresh slime event about every rain |

**What is wrong or missing.**
1. **The owner's image is a wild one.** *"The dry-adapted alien plants of this world generally barely grow at all
   until they get access to water"* describes the world, not the farm. Under the consensus, twelve dry biomes never
   show it on their own. The deserts would be static scenery, and ×10 would be a farming mechanic only. Either that
   is accepted (the Flooded Canyon is the showcase), or the dry biomes need **a rare natural water event**: a desert
   rain weather at low commonality, a dew morning, or a flash flood down a dry wash.
2. **Lifespan (§0.1).** Wild sprouts on sand die of age before they mature at ×0.25. Map generation hides this,
   because it places plants at random growth 0.15–1.5 with a random age (`WildPlantSpawner.cs:452-461`). Regrowth
   does not hide it: sprouts arrive at 0.15. A burnt or grazed desert would refill with sprouts that wither before
   adulthood. That is a dead-looking map, not a waiting one. Fix (PROPOSED): **while a plant's rate multiplier is
   below 1, its age advances at that multiplier**. This is dormancy, which is also the fiction: a desert plant
   waiting for water does not age. Implementation: a `Plant.TickLong` prefix/postfix pair that subtracts
   `2000 × (1 − m)` from `ageInt` when m < 1. It is one field write per plant per long tick, in scope only.
3. **Grazing suppression and rain.** Suppression wipes and blocks soak (deep dive §1.3). On a rained-on map the herds
   keep their grazed cells dry. That is fine and worth keeping: it is a visible pattern.
4. **Wild plants in a fresh event arm and fruit as well**, and 183 of our 358 plant defs have no `harvestedThingDef`
   (MEASURED). Those drop nothing on Fruit, so for most wild plants Fruit is invisible apart from the swelling. The
   spectacle in the wild comes from the tell ladder and from Burst, not from Fruit.

**WP1. Should the dry biomes ever get water on their own?**
1. *(Recommended)* **Yes: a rare desert rain (about 1–2% of weather) in the dry biomes, so the "waiting desert wakes
   up" moment happens a few times a year.** *Trade: rare map-wide perf spikes (X2 must test them); it changes ten
   BiomeDefs' weather lists.*
2. Only the Flooded Canyon shows it naturally; other deserts wake only when the player brings water. *Trade: the
   deserts are static scenery, and ×10 is a farming mechanic.*
3. A local event instead of rain: a flash flood down a dry wash (Flooded-Canyon-style, smaller). *Trade: new incident
   code, but local, cheaper and more dramatic.*
4. *(write your own)*

**WP2. Should a plant that barely grows also barely age?**
1. *(Recommended)* **Yes: below normal speed, a plant ages at the same slowed rate (dormancy).** Waiting plants
   never wither of old age. *Trade: one more patch on every plant; old plants live much longer in deserts.*
2. No; instead raise "barely grow" to ×0.5. *Trade: dry ground is slower but not still; sprouts on sand still die
   young.*
3. No change. *Trade: about three-quarters of our plants cannot mature from a sprout on poor dry ground; crops on
   0.7-fertility soil die before harvest.*
4. *(write your own)*

---

## 5. Rain, snow and the biomes that will fire map-wide

**What the consensus says.** Card W1 recommends that water rain is a fresh event for every unroofed dry cell. §4.2
claims "rain hardly matters in our dry biomes".

**What is wrong or missing.**
1. **The rainy biomes are not wet-adapted.** Wet-adapted = the natives of Greentide, Miasma and Fever Wood only
   (consensus §3.2). Webwork, Twilight Sea and Contagion keep dry-adapted flora by default, and they rain (MEASURED,
   §4). Whether a rain is fresh depends on the cell having been dry for 2 days, and vanilla weather durations
   (UNMEASURED here) decide how often that holds. With water rain at 12–19% of weight, a fresh map-wide event every
   few days is plausible (INFERRED). Each one means ×10 for 3 days, then a synchronised fruiting with a 15% burst
   roll per grown plant and pawn stun. On a dense map (Webwork `plantDensity` 0.9, live dump) that is **hundreds of
   bursts per rain**. That is the opposite of ruling 7's *"VERY hard to weaponize and trigger"*, and it makes a perf
   worst case routine, not rare.
2. **Snow is precipitation.** `SnowGentle`, `SnowHard`, `Blizzard`, `RG_FoggySnow` and the Grimterra snows all have
   `rainRate` 1 (MEASURED, dump). Vanilla's `GameCondition_Drought.HandleEndDueToRain` ends a drought on **any**
   weather with `rainRate > 0`, snow and tox rain included (`GameCondition_Drought.cs:14-20`). The consensus
   allow-list omits snow, and its snowmelt route is "not built". PROPOSED: snow weather counts as water rain on cells
   above 0 °C. Snowmelt (a falling `snowGrid` depth above 0 °C) is a fresh event. Only RUT_FuelSnows and RUT_Umbra
   snow (RULED 2026-10-16: it melts like water and rain; Fuel Snows' snow is water, not fuel); Wasteland, the Sump and Flooded Canyon have no precipitation.
3. **The allow-list must name more weathers.** These have `rainRate` > 0 in today's list and are not in consensus
   §4.2: `RG_Drizzle` (0.5), `AB_ReddishRain`, `AB_ForsakenRainyNight` (+ `_Alternate`), `AB_AcidRainWeather`,
   `BloodRain`, `VEE_PsychicRain`, `VEE_FertileRains`, `ToxRain` (MEASURED, dump: 31 weathers with `rainRate` > 0).
   PROPOSED: water = `Rain`, `RainyThunderstorm`, `FoggyRain`, `TorrentialRain`, `RG_Drizzle`, `VEE_FertileRains`,
   `RSW_SW_RedFoggyRain`, plus snow when warm. Not water: acid, blood, psychic, tox, sheen, slime, boiling, black, and
   Contagion bloom (A4/T2).
4. **The rain stays a map scalar.** The consensus is right that rain must not write per cell (§9 here, perf).

**WP3. Webwork, Twilight Sea and Contagion rain often. Should their plants count as dry-adapted?**
1. *(Recommended)* **No: plants native to any biome with regular water rain count as wet-adapted (×10 at home, no
   bursting); the dry-adapted class is for the dry biomes' natives.** *Trade: the wet-adapted list grows from three
   biomes to six; the "rain wakes the desert" moment stays in the deserts.*
2. Yes, keep the consensus: every rain on those maps is a ×10, fruit and burst wave. *Trade: frequent map-wide bursts
   that stun pawns, and a routine perf worst case.*
3. Yes, but rain there only sustains (no fruiting, no bursting). *Trade: the rule depends on the biome after all.*
4. *(write your own)*

---

## 6. Economy: food and yield under ×10

**What the consensus says.** §3.3: "grass in about half a calendar day, corn in about two days". C4 notes that "a
non-campaign player's first desert colony starves without irrigation". No yield numbers.

**Vanilla baselines (MEASURED, dump; full list, so some values are mod-patched).** Nutrition per cell per calendar
day = `harvestYield × Nutrition ÷ (growDays ÷ 0.55)`. 0.55 is the growing share of a day (`Plant.cs:278-287`,
`Resting` outside 0.25–0.80). It assumes fertility 1, ideal temperature and the full year.

| crop | growDays | yield | nutrition / cell / day, vanilla | ×0.25 dry | ×4 settled | ×10 watered |
|---|---|---|---|---|---|---|
| `Plant_Rice` | 3 | 6 | 0.055 | 0.014 | 0.22 | 0.55 |
| `Plant_Potato` | 5.8 | 11 | 0.052 | 0.013 | 0.21 | 0.52 |
| `Plant_Corn` | 11.3 | 22 | 0.054 | 0.013 | 0.21 | 0.54 |
| `Plant_Haygrass` (animal) | 7 | 18 | 0.071 | 0.018 | 0.28 | 0.71 |
| `RM_Dewgourd` (ours) | 26 | 14 | 0.148 | 0.037 | 0.59 | 1.48 |
| `RM_GlowberryBush` (ours) | 3 | 10 | 0.092 | 0.023 | 0.37 | 0.92 |

**Cells to feed one colonist** (1.6 nutrition a day, INFERRED): rice needs **29** at vanilla, **116** dry, **7.3**
settled and **2.9** watered. Today's build gives 7.3 everywhere in scope and **0.7** on soaked ground (×40).

**What is wrong or missing.**
1. **Sowing needs fertility before water matters.** Vanilla crops have `fertilityMin` **0.7** in the full list
   (MEASURED, dump; mod-patched from vanilla's 0.9 default, `PlantProperties.cs:95`). Sand (0.1) and lakebeds (0) can
   never be sown, watered or not. In a sand-only desert, C4's starving colony is a **fertility** problem first. The
   ways out are basins (H1), a canyon flood's `SoilRich` (consensus §5.5), or our low-fertility crops (`RM_Nabbuq`
   `fertilityMin` 0.2, `RM_Dewgourd` 0.35; MEASURED). The first-colony letter should say which.
2. **Fruit is a free harvest.** Fruit drops `harvestedThingDef × yield` with no pawn labour and resets the plant to
   60% (consensus §3.5). If crops fruit (C4 option 1 implies so), each fresh event gives one labour-free harvest per
   grown crop. Combined with the pulsed-water pattern (§7), a field yields a free crop every 5 days. PROPOSED: Fruit
   drops **half** a harvest, and the plant resets to 60%, so the pawn's harvest still pays.
3. **Labour does not scale with growth** (§3). ×10 shrinks land and calendar time, not work per meal, so a ×10 colony
   is limited by **water and pawn hours**, as the water doctrine intends. No change is needed. The owner should hear
   that ×10 does not mean ×10 food per pawn.
4. **Wood (§0.5).** Per cell per calendar day, INFERRED:

   | plant | logs / growDays | vanilla | consensus watered (tree ×6.25, non-tree ×10) |
   |---|---|---|---|
   | `Plant_TreeOak` (dump) | 46 / 30 | 0.84 | 5.3 |
   | `RM_SicklyGlowMushroom` (IsTree) | 25 / 2 | 6.9 | **43** |
   | `RM_HeatsinkFungus` (IsTree) | 25 / 5.5 | 2.5 | 15.6 |
   | `RM_Varnoth` (**not** IsTree) | 60 / 30 | 1.1 | **11** |

   The tree factor (×0.625 of the plant rate) is keyed on `IsTree`, so it misses 6 wood plants. Some of our "trees"
   are 2–5-day fungi with tree-sized yields, which is a def balance fault that ×10 magnifies. PROPOSED:
   - apply the tree factor to **anything whose `harvestedThingDef` is `WoodLog`** (or any stuff with the `Woody`
     category), not only to `IsTree`;
   - file a separate yield review of the fast wood fungi (logs per growDay > 5: 6 defs, MEASURED list in §0.5) as
     its own item.
5. **Rates the consensus leaves out:**
   - dry trees: PROPOSED 0.25 × 0.625 = ×0.16;
   - wet-adapted trees at home: ×6.25 (today's wet-tree band; consensus §3.6 keeps it implicitly);
   - stunted trees: ×0.4 (ruled stalled band).

   Write all of these into the §4.3 table so the settings page has a row for each.

**EC1. How should wood plants follow the water rule?**
1. *(Recommended)* **Anything that yields wood logs grows at the slower tree rate (×6.25 watered, ×2.5 settled, ×0.16
   dry), and the six fast wood fungi get a yield review.** *Trade: a few odd plants change class; a def review item.*
2. Keep the consensus: only `IsTree` plants are slowed. *Trade: about 43 logs per cell per day from one fungus on
   watered ground.*
3. Wood plants ignore water entirely (vanilla speed always). *Trade: "wood stays a decision", but forests no longer
   respond to floods.*
4. *(write your own)*

**EC3. When a watered crop fruits, how much does it drop?**
1. *(Recommended)* **Half a harvest, and it shrinks back to 60%.** The pawn's harvest is still the main crop.
   *Trade: smaller spectacle.*
2. A full harvest (the consensus). *Trade: one free crop per watering, without labour.*
3. Crops never fruit; only wild plants do. *Trade: farmers never see the moment.*
4. *(write your own)*

---

## 7. The timers: settle, re-arm and the pulse exploit

**What the consensus says.** §4.3 and W3: settled-wet after 3 days of unbroken wet; fresh after 2 dry days; a
watering lasts 1 day.

**What is wrong.** Average multiplier for a cycle of S wet days and R dry days, INFERRED:
(10·min(S,3) + 4·max(S−3,0) + 0.25·R) / (S+R).

| pattern | average | fruiting events |
|---|---|---|
| steady (S = ∞) | ×4 | once |
| 3 on / 2 off | **×6.1** | every 5 days |
| 2 on / 2 off | ×5.1 | every 4 days |
| 3 on / 5 off | ×4.6 | every 8 days |
| 3 on / 6 off | ×3.5 | every 9 days |

Pulsing beats steady water and costs **less** water and labour. Every efficient player would pulse, and FlowWorks
sluices make it a routine, which inverts S4 (*"reduced growth factor in permanently wet areas"*). The consensus line
"cycling costs water and labour" (§4.4) is backwards. The dev-only timer switch (`RM_TimerSwitch`, *"switches … the
sluices and grates near it … on a repeating period"*, MEASURED def text) already automates it for map makers.

**Fix options (PROPOSED).**
- **(a) Longer re-arm:** re-arm ≥ 6 days makes steady water the better deal. It is simple, but the "fresh water after
  a long drought" moment becomes rare.
- **(b) A moisture average instead of two timers.** Each cell holds a moisture value m ∈ [0,1]. Watering pushes it
  toward 1, and it decays toward 0 when dry, with half-life H.
  - The rate is ×10 while the cell is being watered and m was below 0.3 when the water arrived (fresh). It eases to
    ×4 as m stays high.
  - Pulsing never lets m fall far enough to re-arm, unless the dry spell is long.
  - It is one byte per touched cell instead of three ticks, and it is the most physical model. It needs a re-read
    path (decay computed lazily from a last-touched tick), so it costs no ticking.
- **(c) Accept pulsing as skill.** Ruling 7: *"Support players who try."* The fruit wave is then a farming technique.

**EC2. Watering in bursts (3 days on, 2 off) grows faster than steady water. Is that OK?**
1. *(Recommended)* **No: use a moisture level that drains slowly, so only a real dry spell (about a week) makes the
   next water "fresh".** Steady water stays the reliable choice. *Trade: a slightly more complex model; the fruit
   moment needs a week of drought.*
2. Yes, it is a skill (your 09-21 "Support players who try"). *Trade: every good player runs sluices on a timer;
   steady irrigation is for beginners.*
3. Keep two timers but make re-arm 6 days. *Trade: simplest; same result as option 1 with a hard edge.*
4. *(write your own)*

---

## 8. Shared biome tuning classes (consensus §6.4)

**What the consensus says.** Five density classes (barren, sparse, normal, dense, choked), each with fixed
`plantDensity` and `wildPlantRegrowDays`, set on BiomeDefs. Growth comes from the plant class. Card C7.

**What is wrong or missing.**
1. **The live values are not the XML values.** Live dump (MEASURED) against XML and the consensus:
   - Pyrelands is **1 / 0.5625**, against XML `16` / `9` (`src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml:124,134`);
   - Lantern Deeps is **1 / 2.5**, against the consensus's "2 / 5";
   - Gelatinous Slime is **1 / 5.45**, against "1.1 / 6".

   Map Designer folds any density above 1 into regrow days (density ÷ k, regrow ÷ k). The consensus already notes the
   caveat for Pyrelands; in fact it applies to every biome above 1. The "choked" class (16 / 9) **cannot exist as
   authored numbers**. It must be declared as the live pair (1 / 0.56) or kept as the named exception, with
   `RM_PyrelandsDensityEnforcer.cs` re-asserting it. Any class table must be validated against the **dump**, not the
   XML.
2. **The count is 62 BiomeDefs of ours, not ~30** (MEASURED, dump: `mandrake.*` BiomeDefs, the RUT_ twins and 6
   seabed floors included). Each RUT_ twin must take its RM_ twin's class, or the twins drift. They already differ
   in places: `RUT_Sump` 0.15 against `RM_TheSump` 0.25; `RUT_Webwork` has 7 wild plants against 17.
3. **Outliers the consensus missed:** `RUT_FuelSnows` and `RUT_Umbra` have density 0.75 with regrow **1** day
   (MEASURED). Each is either a class of its own or a named exception.
4. **A second biome axis is needed, the water regime**, because §4–5 show that growth now depends on how often a
   biome's ground gets water. That is a biome fact, not a plant fact. It is not a growth rate: it decides which
   plants count as wet-adapted (WP3) and whether rain and snow fire. PROPOSED regimes, from the MEASURED weather
   weights in §4:

   | regime | meaning | biomes |
   |---|---|---|
   | **arid** | no natural water; ×10 only from player water, floods, events | Stillsand, Long Shade, Leaning Scrub, Weeping Stones, Cauldron, Blue Desert, The Forge, Abyss, Warscar, The Scald, The Chill, Grey Sea |
   | **flood** | arid, plus a scheduled flood | Flooded Canyon |
   | **snow** | arid, plus warm snow and melt | RUT_FuelSnows, RUT_Umbra |
   | **rainy** | regular water rain; natives wet-adapted (if WP3 = 1) | Webwork, Twilight Sea, Contagion (by A4) |
   | **wet** | the three jungles (ruled 09-21) | Greentide, Miasma, Fever Wood |
   | **other liquid** | precipitation that is not water | The Rot (sheen), Gelatinous Slime (slime, by T2), Pyrelands (fire, by C5) |
   | **none** | no plants | Rust Cathedral, Nightside Ice, Chill Crater, the seabeds, Lantern Deeps (fungal; cave plants are exempt) |

5. **How classes are declared (PROPOSED).**
   - One `RM_GrowthClassDef` file holds the class table (density, regrow, regime defaults), so numbers are tuned in
     one place.
   - Each BiomeDef carries `<modExtensions><li Class="RM_BiomeGrowthClass"><density>sparse</density><water>arid</water></li>`,
     plus an optional `<exceptionQuote>`.
   - **No runtime write of `plantDensity`.** A startup writer would fight Map Designer and the Pyrelands enforcer,
     the trap of 2026-09-18 and 10-06. Instead, a validation check (selftest) compares each BiomeDef's authored
     numbers with its class and fails on drift, and the XML numbers are edited to match on the owner's review rows
     (A10).
   - The regime **is** read at runtime: it drives the rain allow-list scope, the plant class default and the
     startup counts line (X1).

**BC1. Besides plant density, should each biome be labelled with how it gets water?**
1. *(Recommended)* **Yes: seven water labels (arid, flood, snow, rainy, wet, other liquid, none) set once per biome;
   they decide rain, snow and which plants count as wet-living.** *Trade: one more label per biome, about 60 biomes
   with their twins.*
2. No; decide plant by plant only (the consensus). *Trade: WP3's rainy biomes must be handled one plant list at a
   time.*
3. *(write your own)*

**BC2. Where do the class numbers live?**
1. *(Recommended)* **In each biome's file, checked by a test against one shared table; nothing rewrites them while the
   game runs.** *Trade: changing a class means editing several files (a script can do it).*
2. Set at game start from the shared table. *Trade: one edit tunes all biomes, but it fights Map Designer, which
   already rewrites dense biomes.*
3. *(write your own)*

---

## 9. Performance: per-cell moisture cost

**What the consensus says.** Sparse per-cell `wetUntil`, `wetSince` and `dryAt`; a permanent-water bitset; rain as
a map scalar. The worst case moves to a map-wide rain (§4.4, X2).

**What the code does today (MEASURED).**
- **Cadence.** `Plant` grows only in `TickLong` (`Plant.cs:810-822`: `growthInt += GrowthPerTick * 2000`), and
  `GrowthPerTick` reads `GrowthRate` (`Plant.cs:346`). Our rate postfixes therefore run **once per plant per 2,000
  ticks**, spread over the interval, plus inspect-pane reads (`Plant.cs:1077,1236`). Nothing else in vanilla reads
  `Plant.GrowthRate` (RimSage search: only `HarbingerTree` overrides it).
- **Storage.** `RM_EgLedger` keeps `soakUntil` and `suppressedUntil` as `Dictionary<IntVec3,int>`, plus `charges`
  (`Kernel/RM_ExplosiveGrowthKernel.cs:146-148`). They are saved with `Scribe_Collections.Look(..., LookMode.Value,
  LookMode.Value)` (`RM_MapComponent_ExplosiveGrowth.cs:360-361`), which writes one XML `<li>` per entry.
- **The pass** runs every 250 ticks over every soaked cell and charging plant, sweeps 1/8 of the map for irrigation,
  and requests mesh rebuilds for soaked immature and charging plants (deep dive §1.8; `RM_ExplosiveGrowthKernel.cs:40,49`).
- Vanilla dirties a plant's mesh on growth only for **cultivated** plants, once per tenth of growth (`Plant.cs:827`).
  Wild plants never re-mesh on growth in vanilla. Our engine adds that for soaked plants, which is why soaked wild
  plants visibly jump.

**Recommendations.**
1. **Grid, not a per-plant comp.** Moisture belongs to the ground: it must outlive the plant (a new sprout inherits
   wet ground) and must exist on empty cells. A comp on about 900 plant defs adds an instance and save data to every
   plant on the map (tens of thousands on a dense map) and still cannot represent empty wet ground. The only per-plant
   memory needed is "already fruited this event". Keep it in the cell record (below), not on the plant.
2. **One record per touched cell, not three dictionaries.** A struct `{ wetUntil, wetSince, dryAt, lastTopEvent }`,
   or under EC2 option 1 `{ moisture byte, lastTouchedTick, lastTopEvent }`. Decay is computed **on read** from
   absolute ticks, so moisture needs **no ticking at all**. Only sources write.
   - Sparse while small. Past about 10% of the map, switch to dense `int[]` arrays (250×250 = 62,500 cells × 12–16
     bytes ≈ 0.75–1 MB per map).
   - Save dense grids with vanilla's `MapExposeUtility.ExposeInt` / `ExposeUshort` (`Source/Verse/MapExposeUtility.cs:7,21`),
     which compresses into one base64 block. A 62,500-entry dictionary saved as XML `<li>`s would be several MB per
     map (INFERRED, about 50 bytes a row).
3. **Per-plant read cost** under the consensus: an array read for the plant class (the registry already indexes by
   def), a sparse or dense cell read, one roof read for rain, and one bitset read for permanent water (a `BitArray`
   of 62,500 bits ≈ 7.8 KB). INFERRED: cheaper than today's three hash lookups plus a dictionary lookup.
4. **The real cost is arming and re-meshing.** A fresh map-wide rain arms every grown plant on every unroofed cell.
   The 250-tick pass then updates every charge and dirties every section that holds one. On a dense map that means
   rebuilding most sections every 250 ticks until the wave ends (about 6 h charge = 15,000 ticks = 60 passes).
   PROPOSED brakes:
   - Re-mesh a charging plant only when its tell stage or size step changes, not every pass.
   - For a **rain** event, arm only a capped sample: PROPOSED at most 300 plants per map per event, chosen nearest the
     player's buildings so the show is where the player looks. Floods and player water arm everything in their
     footprint (≤ 400 cells, as today).
   - X2's TPS bar (≥ 90% of soak-off, S0-6) must run the rain case on Webwork-density ground, not only the canyon
     flood.
5. **The permanent-water bitset** is rebuilt per cell on terrain change. FlowWorks channel fills are temp overlays
   that change often. Hook `SetTempTerrain`/`RemoveTempTerrain` as well as `SetTerrain`, and recompute only the
   radius-2 neighbourhood (25 cells) per change.

**PF1. When rain wakes a whole map, how many plants swell and fruit?**
1. *(Recommended)* **A few hundred, nearest your colony; the rest just grow ×10.** *Trade: the far map grows but does
   not put on the show.*
2. Every grown plant on the map. *Trade: the full spectacle; likely fails the 90%-speed bar on dense maps.*
3. *(write your own)*

---

## 10. Ground moisture classes: wet, mud, damp (consensus §5)

**What the consensus says.** A hand-made class per TerrainDef (open water, shallow, waterlogged, damp, dry soil, arid,
never-waters, slime), read once into a per-def array. Wetness is a state, never a terrain swap (T1). Damp ground by
water comes from a radius-2 bitset.

**What is right.** State, not terrain, is correct. A soil→mud swap would drop fertility to 0 (`Mud` fertility 0) and
kill the plants it watered. Vanilla never re-wets ground, and `driesTo` is one-way (consensus §5.1, MEASURED there).

**What is wrong or missing.**
1. **Seed the class table from vanilla's own wet marker.** 99 TerrainDefs in today's list carry `driesTo` (MEASURED,
   dump). By Ludeon's definition they are "wet terrain that a moisture pump dries": `Mud`, `Marsh`, `MarshyTerrain`,
   `WaterShallow`, the AB muds, `RM_Churnmud`, the ManyWaters `RM_Water_*`, `RM_Slime_*`, `RUT_ScaldWaterShallow` and
   more. It is a seed, not authority: it also catches `SoftSand`→`Sand`, `HotSpring`, `AB_Strawberry` and the
   junkyard terrains. A generator can propose the class from `driesTo`, tags and fertility, and the owner rules on
   the diff. That replaces hand-typing about 150 rows (consensus Δ16), which is how drift starts.
2. **`Riverbank` has no `driesTo`** (MEASURED), so it must be listed by hand as damp. The same holds for
   `RM_BankSilt(_Rich)`.
3. **The rim of never-water terrain.** The bitset must test the **neighbour's** class, so that a salt shore (brine
   pool, salt crust) wets nothing. The consensus states this in its table (§5.4) but not in the bitset definition
   (§4.2). Make the bitset builder read only fresh-water and waterlogged-fresh classes.
4. **Snow and ice.** A cell with snow above 0 °C is melting, so it is fresh (§5). Ice terrains (`RM_WaterFrigid*`,
   `IceTerrain`-tagged) are frozen water: not wet until thawed. UNMEASURED: whether any of our arid biomes place ice.
5. **Visibility.** Wet is invisible state (T1 option 1). The player needs to see it, or the water rule reads as random
   growth. Vanilla already has the pattern: the fertility overlay toggle (`PlaySettings.showFertilityOverlay`,
   `PlaySettings.cs:22,167`, drawn by `FertilityGrid`'s cell drawer, `FertilityGrid.cs:61`). PROPOSED: a "ground
   moisture" overlay on the same pattern, with four colours: dry, fresh-watered, settled-wet and sealed (basins).
   This is cheap, needs no new terrain art, and answers T1's trade ("the ground does not look wet").
6. **Transitions.** Keep consensus §5.5. Add one: **a moisture pump** (`CompTerrainPumpDry`) that dries marsh to soil
   must also clear any timed wetness on those cells, not only the bitset. Otherwise a pumped field stays watered for
   its remaining timer.

**GM1. Should players be able to see which ground is wet?**
1. *(Recommended)* **Yes: a "ground moisture" overlay button beside the fertility one (dry / fresh / settled /
   basin).** *Trade: one new overlay; no terrain art.*
2. Only the dark ground stain we have today. *Trade: players must guess why one patch grows.*
3. A visible wet-soil terrain (T1 option 3). *Trade: new terrain and art per soil type.*
4. *(write your own)*

**GM2. Does snow count as water?**
1. *(Recommended)* **Yes: snow falling above freezing, and melting snow, water the ground like rain.** It touches only
   RUT_FuelSnows and RUT_Umbra (the Wasteland, the Sump and Flooded Canyon have no precipitation, owner 2026-10-16). RULED yes. *Trade: one more source; snowmelt needs a slice read of the snow grid.*
2. No; only liquid rain. *Trade: the snowy biomes never water themselves.*
3. *(write your own)*

---

## 11. New card lines (summary)

| id | question (one line) |
|---|---|
| H1 | Do plants in hydroponics basins and pots count as watered? |
| SP1 | Should a sprinkler water plants under the water rule? |
| HW1 | Should pawns water crops by hand? |
| WP1 | Should the dry biomes ever get water on their own? |
| WP2 | Should a plant that barely grows also barely age? |
| WP3 | Webwork, Twilight Sea and Contagion rain often: are their plants dry-adapted? |
| EC1 | How should wood plants follow the water rule? |
| EC2 | Watering in bursts grows faster than steady water: is that OK? |
| EC3 | When a watered crop fruits, how much does it drop? |
| BC1 | Should each biome be labelled with how it gets water? |
| BC2 | Where do the class numbers live? |
| PF1 | When rain wakes a whole map, how many plants swell and fruit? |
| GM1 | Should players be able to see which ground is wet? |
| GM2 | Does snow count as water? |

Interactions with the consensus cards:
- WP2 = 1 makes C6's ×0.1 viable; without it, only ×0.5 is safe.
- WP3 = 1 changes C1/C3's scope.
- EC2 = 1 replaces W3.
- H1 and HW1 settle most of C4's "first colony starves".

## 12. Additions to the consensus delta list (sizes INFERRED)

| # | change | size |
|---|---|---|
| Δ18 | Sealed-wet state for `Building_PlantGrower` edifices + `RM_GrowerMoisture` extension on 3–4 defs; replace vanilla Drought factor in scope | S |
| Δ19 | Dormancy: age advances × rate when rate < 1 (WP2) | S |
| Δ20 | Tree factor by `WoodLog` yield; dry/home/stunted tree rates; yield-review item for the six fast wood fungi | S + item |
| Δ21 | Rain allow-list extended (drizzle, fertile rains, warm snow); snowmelt slice | S |
| Δ22 | Moisture record struct or moisture byte (EC2); dense-grid switch and `MapExposeUtility` save | M |
| Δ23 | Rain arming cap and stage-change-only re-mesh (PF1) | S |
| Δ24 | Ground-moisture overlay (GM1) | M |
| Δ25 | Zone "water this zone" toggle + Growing work-giver + FlowWorks container read (HW1) | M (cross-mod) |
| Δ26 | Water-regime extension on 62 BiomeDefs + class selftest (BC1/BC2) | M (data + his review) |
| Δ27 | Terrain-class generator seeded from `driesTo`/tags/fertility, producing a review diff (replaces Δ16's hand list) | S |
