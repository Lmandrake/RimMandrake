# Natural water and our water: one kind or two? Engine and vanilla feasibility (RULED 2026-10-17)

Helper A of a double review (lens: **engine and vanilla interaction feasibility**). **Written as a proposal; RULED 2026-10-17 (section below).** Nothing in
code, defs, the bridge or the game was touched to write this, and no existing doc was changed. FlowWorks claims are
file:line from a read-only census of `src/RimMandrake/FlowWorks/Source` at `06c09c0f7`. Vanilla claims were read from the
1.6 source and defs through RimSage (Core + Odyssey). Every behaviour claim below is **READ FROM CODE**, not seen live,
unless it says MEASURED. One independent outside read (GPT via `gpt_consult.py`) sits beside this file as
`flowworks_natural_water_engine_2026-10-17.gpt_read.md`. It is evidence, not authority (§7).

**Every agent-day figure is an ESTIMATE**, same unit as `flowworks_one_rebuild_plan_2026-10-17.md`: one focused coding
agent day including selftests, no live game time unless stated.

The owner, 2026-10-17: *"Worth thinking back on natural bodies of water now too... should we just replace them on maps
with our own pits right away, and enable swimming, fishing, and other water interactions within our own scope? It is a
bit odd that there will be 'two kinds of surface water' one that is flattened depth and one that is articulated depth.
Please look into this deeply. I certainly wouldn't want to turn off aquatic farming, swimming, fishing, or other water
interactions."*


## RULED 2026-10-17 (owner; ledger notes on `WATER_NATURAL_DECIDE_ONE_SURFACE`)

The analysis below is kept as written; where it recommends or asks something these rulings settle, the rulings win.
Build packages and estimates: `design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md` (P11-P14).

| # | ruling | authority |
|---|---|---|
| R10 | **One kind of water (engine doc Option B2).** Every pond, lake, canal and pit is one kind; wet squares write the main (base) terrain layer from one ladder of vanilla water terrains chosen by water depth; natural lakes get their floors recorded when the map is made and nothing on a natural lake changes on screen; rivers and oceans stay vanilla, limitless and never run dry (not converted). | card |
| R11 | **Lake depth varies by lake and by biome:** *"Vary it. Some lakes will be shallow and silted up. Others will be deep and chasm-like. Depends on the biome. The more mountainous, the deeper in general. The more plains-like, the smoother/shallower. They should also have some variation down there, not just a radial crater."* Replaces the 0.5 m-per-4-squares slope and the 20 m default / 50 m large-lake numbers as fixed rules. The settable ceiling (to 125 m) stays; 50 m is an upper bound reachable only by mountainous/deep biomes. | owner said |
| R12 | **Pawns may swim in water 2 m or deeper** (vanilla: impassable). Needs swim rules, speed, drowning/exhaustion, apparel/weight, animals. Non-water fluids keep the no-swim refusal. Deep water stops being a barrier for trenches and prisoner pits: flagged as a risk on the pit items. | card |
| R13 | **Limitless bodies are marked:** *"Any natural body of water that is supposed to be 'clearly limitless' should be so marked, so players aren't shocked."* Narrows ruling 35 (card 2026-09-17, *"Stock replaced it — cut the idea."*): limited bodies still show no indicator. | owner said |

**Defaulted, veto-able (not asked; the docs' recommendations):** fish in dug water by the game's size rule (engine Q2a,
follows R10); the same fish return when a dried pond refills (engine Q5a); reeds survive short pump cycles (engine Q6a);
fish live in lakes as well as seas, caught not seen (play Q7a); a 0.5 m beach ring so a drained lake stays reachable
for small animals (play Q4a); a river below a dam keeps flowing from the edge (play Q6b, R10 keeps rivers vanilla).
The steeper-lake question (play Q2) is superseded by R11; play Q1 and engine Q4 by R10 (floors at map creation);
engine Q1 by R10; engine Q3 and play Q2 by R12; play Q1b by R13.

---

## Summary (one page)

**1. After the rebuild, depth is already one kind.** The ruled level-surface solver (P3 of the rebuild plan) gives a
natural pond the same model as a canal: one exact volume per connected body, one surface, and a floor per square
(`bedRecord` for a lake, `depthGrid` for a dig). Water depth = surface − floor in both. A pond is "flattened" today only
because (a) its floors are written down lazily, on first contact with a canal (`RM_LiquidStock.cs:100-125`), and
(b) oceans and edge rivers are limitless (ruled; their depth is a readout, not a quantity). Neither is a second physics.

**2. The real "two kinds" is a terrain LAYER, and vanilla can see it.** This is the finding that matters most.

| | natural pond square (wet) | dug canal or pit square (wet) |
|---|---|---|
| where the water terrain is written | the **base** terrain layer (`StageNaturalCell`, `RM_MapComponent_Excavation.cs:1659-1676`) | the **temporary** layer, over a dry channel floor (`SetTempTerrain`, `:2292`) |
| defs used | vanilla `WaterDeep` / `WaterShallow` + `RM_WaterChestDeepStill`, `RM_WaterThin` | `RM_Fill_Water_{Trace,Half,Brim,Superdeep}` (`Defs/Canals/TerrainDefs/FlowWorks_Terrain.xml:272-343`) |
| vanilla water body (fishing) | **yes** (base def is Freshwater) | **no.** `GridsUtility.GetWaterBodyType` reads **under** temp terrain (`Verse/GridsUtility.cs:135-146`), finds the channel floor (`NaturalTerrainBase`, type None), so no body forms, whatever the fill def says |
| ice | yes (vanilla `canFreeze` on shallow) | no (`canFreeze=false` on every fill). It cannot simply be turned on: vanilla ice is **also** temp terrain (`FreezeManager.DoWaterFreezing` → `SetTempTerrain(ThinIce)`), and a cell has **one** temp slot. Freezing would overwrite our water picture, and melting (`RemoveTempTerrain`) would leave a dry-looking floor under water |
| swimming, water plants, fire, wet thoughts, path cost | yes | **yes** already: these read `GetTerrain` (top, including temp) and the `Water` tag, which the fills carry |

So canals already swim, put out fires, grow reeds and count as water for other mods. What they lack is **fishing and
ice**, and the reason is the layer, not the flags. **Making our fill terrains inherit vanilla flags (the brief's
Option B as worded) does not give fishing.** The fill defs already inherit Freshwater from `WaterShallow`; vanilla
ignores it because it reads under the temp layer.

**3. Recommendation: one water, written one way (Option B2 below).** Every limited body of water (pond, lake, canal,
pit, reservoir) is the same thing: volume plus floors, one surface. Every wet square writes its **base** terrain from
**one ladder** of vanilla-water-family defs chosen by water depth, the same ladder for a lake and a canal. Every dry
square shows its floor (dug channel or lakebed) from the grids. Natural lakes are not visibly "replaced with pits":
their floors are recorded at map start instead of on first contact, and nothing on screen changes. Oceans and edge
rivers stay vanilla terrain with limitless volume (ruled). **Nothing is turned off**; fishing and ice are turned **on**
for dug water. **Cost (ESTIMATE): 5 to 8 agent-days on top of the rebuild, best folded in right after P3.**

**4. Vanilla has three traps that bite whatever is chosen**, including today's design (§2.3): a water body that starts
small never gets fish (fish are rolled once, at size 1); a pond that dries out completely and refills loses its fish for
good; and vanilla never splits a water body that dries in the middle. Each needs a small adapter (about 1 to 1.5 days
together, inside every option's figure).

**Converting rivers and oceans into our cells (Option C) buys nothing the player can see and costs the most** (15 to 30
days, and it fights the limitless ruling). Not recommended.

---

## 1. How natural water is represented today

### 1.1 Vanilla 1.6 (RimSage, Core + Odyssey)

**Classification is by TAG, not a bool.** `TerrainDef.IsWater => HasTag("Water")`, `IsRiver => HasTag("River")`,
`IsOcean => HasTag("Ocean")` (`Verse/TerrainDef.cs:~318-324`). There is no `isWater` field.

| def | parent | key fields |
|---|---|---|
| `WaterBase` (abstract) | | tag `Water`; `waterBodyType` Freshwater; `extinguishesFire`; `takeSplashes`; `avoidWander`; `traversedThought` SoakingWet; perceived path cost +180 (+18 drafted); `canFreeze` true; `fertility` 0; `floodTerrain` ShallowFloodwater; `waterDepthShader` |
| `WaterDeep` | `WaterDeepBase` | **Impassable**, path 300, `canFreeze` false, no affordances (not bridgeable), `gravshipReplacementTerrain` WaterShallow, `forcePassableByFlyingPawns` |
| `WaterShallow` | `WaterShallowBase` | path 30; affordances ShallowWater, WaterproofConduitable, Bridgeable, Walkable; tags + `WaterFreshShallow`, `WaterFreshShallowStill`; `driesTo` Gravel |
| `WaterMovingShallow` / `WaterMovingChestDeep` | shallow / chest-deep base | tag `River`; affordance `MovingFluid`; chest-deep path 42 |
| `WaterOceanDeep` / `WaterOceanShallow` | | tag `Ocean`; `waterBodyType` **Saltwater**; `canFreeze` false |
| `Marsh` | `WaterShallowBase` | tag `WaterMarshy`; `driesTo` Soil |
| `ShallowFloodwater` (Odyssey) | `WaterShallow` | `temporary`, tag `Flood`, `canFreeze` false (our fill defs are clones of this, `FlowWorks_Terrain.xml:~262-270`) |
| Toxic waters, `HotSpring` | | `waterBodyType` **Other** (water, but no body and no fish) |
| `ThinIce` | | temporary terrain; placed over water by freezing |

**Still water has only two depths in vanilla** (shallow, walkable; deep, impassable). Chest-deep exists only as
moving water.

**Water bodies and fishing (Odyssey).** `Map.waterBodyTracker` flood-fills 4-way every cell whose
`GetWaterBodyType != None` into `WaterBody` objects at map init (`WaterBodyTracker.ConstructBodies`, no-op without
Odyssey). Live changes: `TerrainGrid.DoTerrainChangedEffects` → `WaterBodyTracker.Notify_TerrainChanged`
(`RimWorld/WaterBodyTracker.cs:173-188`), which acts **only when `waterBodyType` changes** (so swapping between two
Freshwater defs costs nothing). A new body is `Initialize`d (`Verse/WaterBody.cs`): population = max, fish types rolled
from `BiomeDef.fishTypes` by size (`FishingUtility`: common fish chance 0 below 75 cells, 0.5 at 100, 1.0 at 200;
uncommon from 400; population factor 0 below 75 cells). Consumers: `Designator_ZoneAdd_Fishing.CanDesignateCell`
(needs a body type, not impassable, fish present), `Zone_Fishing`, `WorkGiver_Fish`/`JobDriver_Fish`, animal fishing
in `JobGiver_GetFood` (:142, :167; body not frozen, population > 10), `FishShadowComponent` (bodies of 12+ cells),
pollution toxfish (`WaterBody.PollutionPct`), `TorrentialRainFlood` (salt check), the "no fish" precept, mouseover.

**Swimming and wading.** No swim-speed stat. `Pawn.WaterCellCost` (race, gene, or the job's `swimming` flag) applies
in `Pawn_PathFollower` when `terrain.IsWater`. Move speed by terrain tag (`PawnKindDef.moveSpeedFactorByTerrainTag`).
Swimming joy (`JoyGiver_GoSwimming.TryGiveJob`): `GetTerrain(...).IsWater`, `toxicBuildupFactor == 0`, standable, not
fogged, outdoors ≥ 10 °C. So vanilla never swims in deep water (impassable). Water-seeking animals
(`RaceProperties.waterSeeker`) spawn on `terrainGrid.WaterAt` cells; sea animals enter on `== WaterOceanShallow`
(`WildAnimalSpawner.cs:135`).

**Drowning: none in vanilla** (no "drown" anywhere in the 1.6 source). FlowWorks' pit drowning is our own rule.

**Aquatic plants.** Vanilla 1.6 has **wild** water plants only (Odyssey `Plant_Reeds`, `Plant_LilyPad`,
`Plant_Bulrush`, `Plant_Lotus`; `Defs/Odyssey/ThingDefs_Plants/Plants_Water.xml`), keyed on `wildTerrainTags`
(`WaterFreshShallow`, `WaterFreshShallowStill`, `WaterMarshy`, `Mud`). None has `sowTags`: **there is no sowable
aquatic crop in vanilla 1.6**. If "aquatic farming" means a mod's crop (or a future one of ours), it will key on the same
tags or on terrain affordances. Enforcement: `TerrainGrid.DoTerrainChangedEffects` (:~522) **destroys** a plant whose
tags no longer overlap the new terrain's tags; `Plant.cs:267-269` does the same check over time.

**Ice.** `FreezeManager` (Odyssey): at ≤ −7 °C a cell whose top terrain has `canFreeze` (and is not surrounded by
water) freezes a radius-2.9 patch to `ThinIce` with `SetTempTerrain`; melting at ≥ 2 °C calls `RemoveTempTerrain` on
cells `== ThinIce`. Deep and ocean water never freeze. `WaterBody.numCellsCanFreeze` reads `BaseTerrainAt(...).canFreeze`.

**Fire.** `Fire.DoComplexCalcs` reads `GetTerrain().extinguishesFire`; `JobGiver_JumpInWater` looks for it.

**Mapgen.** Water is placed by tile mutators (`Lake`, `Pond`, `LakeWithIsland(s)`, `Oasis`, `Wetland`, `Coast` and
its variants, `River*`, `CaveLakes`, `Marshy`, `Harbor`) through `MapGenUtility.*WaterTerrainAt`, which return
`biome.waterDeepTerrain ?? TerrainDefOf.WaterDeep` and so on (`MapGenUtility.cs:182-207`), plus biome
`terrainPatchMakers` (Core biomes name `WaterShallow`/`Marsh` directly).

**World and caravans.** Coastal and lake tiles are **BiomeDefs** (`BiomeDefOf.Ocean`, `BiomeDefOf.Lake`), not
terrain. `Tile.IsCoastal` and caravan travel never read map terrain. **No vanilla boats exist.** Gravships landing on
water use `gravshipReplacementTerrain`.

**Places that compare to vanilla water defs by identity** (a modded def fails these): `RoadDefGenStep_Place.cs:54-60`
(roads shallow `WaterDeep`), `WildAnimalSpawner.cs:135` (sea animals enter on `WaterOceanShallow`),
`TileMutatorWorker_River.cs:273, 293` (`!= Marsh`). Everything else is by tag or field.

### 1.2 How FlowWorks hooks it today (`src/RimMandrake/FlowWorks/`, S = `Source/`)

| mechanism | what it does | where |
|---|---|---|
| natural liquid | base terrain `IsWater`; no defName list | `S/RM_MapComponent_Excavation.cs:841-845` |
| source cell | undug (`depthGrid == 0`) natural liquid; reads as Superdeep/full (`DepthAt` :866-884, `FillAt` :926-938) | `:849-856`; kernel `S/RM_FlowKernel.cs:194` |
| body formation | **lazy**, on first contact (a canal, pump or bottle draws); 8-way walk of same-fluid sources | `S/RM_LiquidStock.cs:100-250`, `S/RM_FlowKernel.cs:1470` |
| limitless | sticky: truncated (> 4,000 cells, `RM_BedMath.cs:41`) or edge contact + ≥ 50 cells; never debited | `S/RM_StockMath.cs:91-98, 336-359`; `S/RimMandrakeFlowWorksMod.cs:112, 161` |
| floor per square | shallow 2 notches (1 m), deep (impassable or path ≥ 40) 4 (2 m); lake middle +1 notch per 4 squares past 3 from shore, recorded once in `bedRecord` | `S/RM_Volume.cs:97-116`, `S/RM_BedMath.cs:28-54`, `S/RM_LiquidStock.cs:231-264`, `S/RM_MapComponent_Excavation.cs:889-928` |
| pond stages (natural water shallows out) | writes **base** terrain by water depth: original → `WaterDeep` → `RM_WaterChestDeepStill` → `WaterShallow` → `RM_WaterThin` → Mud → `RM_Lakebed_*`; restore writes the recorded original back | `S/RM_MapComponent_Excavation.cs:1590-1715`, `S/RM_PondDepthMath.cs`; defs `Defs/Canals/TerrainDefs/FlowWorks_PondStageTerrain.xml:16-43` |
| canal and pit water | **temp** terrain `RM_Fill_<fluid>_{Trace,Half,Brim,Superdeep}` (parent `WaterShallow`, `temporary`, `canFreeze=false`, Superdeep Standable) over a dry `RM_Channel_*` floor (`NaturalTerrainBase`, no water type) | `S/RM_MapComponent_Excavation.cs:2292`; `Defs/Canals/TerrainDefs/FlowWorks_Terrain.xml:3-343`, `FlowWorks_PitFluidTerrain.xml`, `FlowWorks_SlimeTerrain.xml` |
| digging and filling natural water | refused ("Already water.", `S/Designator_DigCanal.cs:73-76`; `S/WorkGiver_DigCanal.cs:53`); a dry bed can be dug and leaves the pond (`DetachIfDryBed`, `S/RM_MapComponent_Excavation.cs:1377-1440`); filling in natural water is **not built** (`S/Designator_FillInCanal.cs:82-92`) | |
| vanilla water-body patch | `RM_Patch_WaterBodyTypeFlip`: prefix on `WaterBodyTracker.Notify_TerrainChanged`, fixes a vanilla miscount when a cell flips between two water types | `S/RM_WaterBodyTypeFlipFix.cs:21` |
| fishing | only the weir: `RM_Weir.TryCatchFish` reads the vanilla body (`HasFish`, population) | `S/Rivers/RM_Weir.cs:334-345` |
| swimming | only a refusal on our no-swim fluids (`JoyGiver_GoSwimming.TryGiveJob` postfix) | `S/ManyWaters/RM_Patch_NoRecreationalSandSwim.cs:47`; `Patches/Canals/FlowWorks_NoRecreationalSwim.xml` |
| drinking (our thirst need) | `IsRiver || (IsWater && !IsOcean)` → fresh water, debited from the body | `S/Thirst/RM_ThirstUtility.cs:52-69`, `S/Thirst/RM_ThirstJobs.cs:80-91, 172` |
| fire | liquid fire on burnable fluids; burnable fills set `extinguishesFire=false` | `S/RM_LiquidFire.cs:212-214, 1156, 1172` |
| typed shores (mapgen) | repaints a tagged tile's lakes and seas into a typed liquid; rivers, marsh, ice untouched | `S/LiquidTypes/RM_GenStep_LiquidShores.cs:79-80` |
| rivers | river cells by `IsRiver` or `MovingFluid`; mutates every `IsRiver` def's perceived path cost; ferry/levee patches on `Flood.CanFloodSpreadInto`; current painter paints `IsWater` cells | `S/Rivers/RM_RiverWorks.cs:95-188`, `S/Rivers/RM_FerryAndLevee.cs:139-211`, `S/MapControls/RM_CurrentPainter.cs:69` |
| mouseover | natural bed depth scaled by fill; "limitless" | `S/RM_MouseoverDepth.cs:19, 85, 95` |
| ice, freezing, vanilla pollution | **no FlowWorks hook** | |

---

## 2. What keys on natural water, and what replacement would need

### 2.1 System by system

"Keys on" says what a replacement terrain must carry. "Canal today" is what dug water does now.

| system | keys on | canal today | if natural water became our cells, it needs |
|---|---|---|---|
| fishing zone, fishing job, catch | `GetWaterBodyType` (base under temp), `IsWater`, not impassable, body has fish; biome `fishTypes` | **no** (temp layer) | wet cells on the **base** layer with Freshwater/Saltwater; body-growth fish roll (§2.3) |
| animal fishing (Odyssey) | body not frozen, common fish, population > 10; stand cell `IsWater` | no | same as fishing |
| fish shadows | body with fish, ≥ 12 cells, all 8 neighbours in body | no | same |
| swimming (joy) | top terrain `IsWater`, `toxicBuildupFactor` 0, standable, outdoors ≥ 10 °C | **yes** | `Water` tag, standable band defs |
| wading cost, swimmers' path cost | `IsWater` + `pathCost` + tag speed factors; `Pawn.WaterCellCost` | yes | same tags; path cost per band |
| wild water plants | `wildTerrainTags` vs terrain tags; plants destroyed when tags stop overlapping | yes (fill tags include `WaterFreshShallow`/`Still`) | the same tag set on every band where they should live; **hysteresis** so a pumped body does not kill reeds every pulse (§2.3) |
| sowable aquatic crops | none in vanilla 1.6 | n/a | n/a (if a mod adds one, it will key on these tags or affordances) |
| drinking | vanilla: none. Ours: `IsWater && !IsOcean` | yes | nothing new |
| ice | top `canFreeze`; ice is **temp** `ThinIce`; body `numCellsCanFreeze` from base | **no** | base-layer water (one temp slot, §2.2) |
| fire put out / jump in water | `extinguishesFire` on top terrain | yes (except burnable fluids) | nothing new |
| wet thought, splashes | `traversedThought`, `takeSplashes` | yes | nothing new |
| drowning | vanilla: none. Ours: pit drowning, going relative (rebuild V2) | ours | **owner card**: if deep natural water becomes enterable, drowning reaches lakes (§6 Q3) |
| deep water blocks walking | `passability` Impassable on `WaterDeepBase` | `RM_Fill_*_Superdeep` is **Standable** (pit rules need it) | one rule for both (§6 Q3) |
| bridges, conduits | affordances `Bridgeable`, `WaterproofConduitable` (shallow and chest-deep; **not** deep) | inherited from `WaterShallow` | per band, as vanilla |
| gravship landing | `gravshipReplacementTerrain` | inherited | keep on every band |
| pollution, toxfish | `canBePolluted`, polluted textures; body `PollutionPct` | partial (no body) | base layer |
| roads over deep water | `== TerrainDefOf.WaterDeep` (identity) | n/a | keep vanilla `WaterDeep` as the deep band, or accept roads not shallowing ours |
| sea animals arriving | `== WaterOceanShallow` (identity) | n/a | oceans stay vanilla (all options keep this) |
| river mutator over marsh | `!= Marsh` (identity) | n/a | mapgen only; untouched if mapgen stays vanilla |
| mapgen placement | mutators via `MapGenUtility.*WaterTerrainAt` + biome water fields | n/a | **untouched**: no option needs to change mapgen; we record floors after it |
| seasonal floods, torrential rain, emerge-from-water raids | `IsRiver`, `IsOcean`, body salt type | n/a | rivers and oceans stay vanilla |
| world map, coasts, caravans | BiomeDefs, never map terrain | n/a | **nothing**, whatever we do on the map |
| boats | **none in vanilla** | n/a | n/a |
| quests needing water | fish-requiring conditions use `AnyBodyContainsFish`; nothing else found by terrain | n/a | base-layer bodies keep it true |
| other mods (VE, Dubs, ice mods) | mostly `IsWater` on top terrain; some by identity | they see canals as water | base layer is closer to vanilla than today |

### 2.2 The one-temp-slot problem (why "inherit the flags" is not enough)

A RimWorld cell has one base terrain, one optional foundation/floor, and **one temporary terrain**. FlowWorks puts canal
water in the temporary slot. Vanilla puts **ice** (`ThinIce`), **floods** (`ShallowFloodwater`, `MarshFlood`) and
reads water bodies **under** that slot. Three consequences:

1. **No fish in dug water, ever, under any flag change**, because `GetWaterBodyType` skips temp terrain.
2. **Ice and canal water fight over the slot.** Turning `canFreeze` on for fills lets `FreezeManager` overwrite the fill
   with `ThinIce`; melt removes the temp terrain and the cell shows a dry channel with water still in the books.
   (`FreezeManager.DoWaterFreezing` also dereferences `c.GetWaterBody(map)` without a null check: a freezable cell with no
   body would throw. Read from code; not seen live.)
3. **Odyssey floods** write `ShallowFloodwater` into the same slot. Today a seasonal or torrential flood reaching a wet
   canal would replace our fill picture. UNMEASURED live; worth one row in the next live walk.

The fix is to put dug water where natural water already lives: the **base** layer. The dry floor of a dug square is
then a picture chosen from `depthGrid` whenever the square is dry, exactly as a drained lake already shows
`RM_Lakebed_*` from `bedRecord`.

### 2.3 Vanilla traps that bite every option (read from `Verse/WaterBody.cs`, `RimWorld/WaterBodyTracker.cs`)

1. **A body that starts small never gets fish.** `SetFishTypes` rolls once, in `Initialize`, at the body's size then.
   A body born at 1 cell rolls `shouldHaveFish = false` (chance 0 below 75 cells). `RecacheState` re-rolls only if
   `shouldHaveFish` is already true. Growth by `FloodFillBody` never re-rolls. So a reservoir that fills square by square
   would stay fishless forever even after the base-layer change. **Adapter:** when a body crosses 75, 100 or 200 cells
   with no fish and no prior roll at that size, re-roll (postfix on the tracker's add/flood path). About 0.5 day.
2. **A pond that dries out completely loses its fish for good, today.** At 0 cells the body is removed
   (`RemoveCellFromExistingBody`); the refilled pond is a new 1-cell body and trap 1 applies. This is a bug in the
   current ruled design (ponds shallow out to Mud), not only in a new one. The same adapter fixes it; optionally the
   adapter remembers the old body's fish list by footprint and restores it (the owner's "a refilled pond returns to its
   exact shape", ruling 7 of 2026-10-12, suggests he would expect the fish back too: §6 Q5). Drying also deletes the
   square from any **fishing zone** (`WaterBodyTracker.cs:229-234`), and refilling never adds it back; the adapter
   restores zone squares by footprint too.
3. **Vanilla never splits a body.** A lake that dries in the middle into two puddles stays one `WaterBody` until the
   next load (`ConstructBodies`). Harmless for fishing; it skews the frozen fraction. Optional adapter: rebuild a body's
   membership when FlowWorks' solver reports a split (it must know anyway; rebuild plan risk 3). About 0.5 day.
4. **Water plants die on every band change that drops their tag.** `WaterDeep` carries no `WaterFreshShallow*` tags,
   so a square going shallow → deep → shallow loses its reeds and lilies. That is natural for a real lake rising. For a
   pump cycling every few hours it is churn. **Adapter:** a band change for a square only after its depth has stayed past
   the threshold for a while (hysteresis), or keep the plant tags on the chest-deep band. About 0.25 day.
5. Notifications are cheap: the tracker acts only when `waterBodyType` changes, so band-to-band swaps inside
   Freshwater cost nothing; only wet ↔ dry does a flood fill.

---

## 3. Options

All three keep: the ruled level-surface solver (P3), exact litres, the 0.5 m dig step, lake floors to 20/50/125 m,
limitless oceans and edge rivers (ruling 16), and vanilla mapgen. They differ in what natural water **is** in the engine
and which layer the water picture lives on.

### Option A — Keep vanilla natural water; adapt (today's direction)

- **What:** as planned. Natural lakes stay vanilla terrain, formed into our bodies on first contact. Canal water stays
  on the temp layer. Add the §2.3 adapters.
- **Two kinds remain:** canals are not fishable and do not freeze; lake water is and does. Lake art and canal art come
  from two ladders (pond stages vs `RM_Fill_*`).
- **Cost (ESTIMATE):** 1 to 2 agent-days on top of the rebuild (the adapters, plus a selftest).
- **Risk:** low. **Save impact:** none beyond the rebuild's own migration.

### Option B — Every limited body is ours from map start, one picture ladder, vanilla water defs kept

The brief's Option B, in two strengths. **B1 is what the brief describes; B2 is what it takes to work.**

- **B1 (flags only):** record every limited lake's floors at map start; give the fill defs vanilla flags. **Does not
  deliver fishing or ice for dug water** (§2.2). Listed so the card does not offer it as if it worked. About 2 days.
- **B2 (recommended): one water, base layer.**
  1. **Formation at map start** (or at first load of an old save): every limited natural body is walked once, its
     `bedRecord` written, and it joins the solver as a body (pond-as-node design, `pond_depth_design_2026-10-16.md` §3).
     Oceans and edge rivers are classified limitless at the same moment. Nothing on screen changes. 0.5 to 1 day.
  2. **One ladder of wet-square defs by water depth**, used by lakes and digs alike: under 25 cm (new art, R2) → 0.5 m
     thin (`RM_WaterThin`) → 1 m (`WaterShallow`) → 1.5 m (`RM_WaterChestDeepStill`) → 2 m and deeper (vanilla
     `WaterDeep`, or a passable sibling: §6 Q3) → darker tints past 5 m (art, his look). All Freshwater (or the fluid's
     own type: Saltwater for brackish, Other for slimes and fuels, as the LiquidTypes defs already set). Each fluid keeps
     its own ladder; the water ladder is the vanilla family.
  3. **Wet squares write the base layer**; dry dug squares show `RM_Channel_*` from `depthGrid`, dry lake squares
     `RM_Lakebed_*` from `bedRecord`. The temp layer is left to vanilla (ice, floods). Every `SetTempTerrain` site in
     `RM_MapComponent_Excavation.cs` (fill staging, `:2264-2292`) becomes a base write plus an original-terrain record;
     the recorded original for a dug square is its channel picture, recomputed from depth, never stored as a second
     truth. 2 to 3 days, including the save migration and the selftests.
  4. **Adapters** (§2.3): fish re-roll on growth and refill, split refresh, plant hysteresis. 1 to 1.5 days.
  5. **Things on squares that turn to water** (bridges, conduits, items, pawns) follow vanilla terrain-change rules, as
     ponds already do. A building whose affordance the new band lacks needs one rule (vanilla's handling on a base change
     was not read for this pass: UNVERIFIED). 0.5 day.
  6. **Live rows** (minimal list, no flyers): freeze and melt a canal; fishing zone on a 100-square reservoir; reeds on a
     pumped canal; a seasonal flood over a canal. 0.5 to 1 day, needs the bridge.
- **Cost (ESTIMATE): 5 to 8 agent-days**, of which about 1 is live (the outside read put B at 10 to 20 counting work
  P3 already holds; budget the upper end, §7 #1). Folded into the rebuild right after P3, about 1 to 2
  days of it overlap P3/P4 work on the same staging code.
- **Risk:** medium. The base-layer switch touches every place that stages canal water and every reader that assumes the
  fill is temp (`RM_LiquidLooks`, mouseover, `WorkGiver_DigCanal.cs:53` "is water, so stale"). The dig workgiver and
  designator must ask the grids, not the terrain, whether a square is natural water (the rebuild's P5 already moves them
  to the grid). Other mods that skip temp terrain will now see canals as real water (wanted).
- **Save impact:** one migration on load: every wet dug square's temp fill becomes a base write; every limited lake gets
  its floors. Vanilla rebuilds water bodies on load, so a big existing reservoir gets its fish roll then. Back up the
  Saves folder first. Downgrade unsupported (already true of the rebuild).

### Option C — Everything is our cells, rivers and oceans included

- **What:** rivers and oceans become bodies of cells in the solver.
- **Why not:** an ocean is limitless by ruling; making it cells adds a 40,000-square body to the kernel for a number that
  never changes (`OceanWalkCells = 4000` exists because of this, `RM_BedMath.cs:41`). Rivers are moving water: vanilla
  `WaterInfo` flow vectors read `BaseTerrainAt(...).IsRiver`, seasonal floods, emerge-from-water raids, sea-animal
  entry by identity, road building over deep water by identity, our own river works (current, weir, ferry, swept away).
  All of it would need re-wiring to gain a depth number the player already gets from the readout.
- **Cost (ESTIMATE): 15 to 30 agent-days** on top of B2. **Risk:** high (perf, every river system). **Save impact:**
  large and irreversible.

### Coverage, by option

"✔" works as vanilla does; "✘" does not; "~" partly.

| interaction | A: lake water | A: dug water | B1: dug water | **B2: all limited water** | C |
|---|---|---|---|---|---|
| swim (joy) | ✔ (not in deep) | ✔ | ✔ | ✔ | ✔ |
| fish (zones, jobs, animals, shadows) | ✔ (traps §2.3) | ✘ | ✘ | ✔ (with the re-roll adapter) | ✔ (adapter) |
| wild water plants | ✔ | ✔ | ✔ | ✔ (hysteresis) | ✔ |
| aquatic farming (no vanilla crop exists) | n/a | n/a | n/a | tags in place for any mod's | same |
| drink (our thirst) | ✔ | ✔ | ✔ | ✔ | ✔ (rivers rewired) |
| ice | ✔ | ✘ | ✘ (or broken pictures if turned on) | ✔ | ✔ |
| fire | ✔ | ✔ | ✔ | ✔ | ✔ |
| drown (ours) | none in lakes today | ✔ | ✔ | one rule everywhere (Q3) | same |
| boats | none in vanilla | | | none | none |
| caravans, world coasts | untouched | | | untouched | untouched |
| cost (ESTIMATE) | 1-2 days | | ~2 days | **5-8 days** | 20-38 days total |

---

## 4. The single-representation argument

**Can our water be the ONE surface water, flat or articulated being only depth data? Yes, for every limited body.**
What it takes is already mostly ruled or planned:

| requirement | status |
|---|---|
| one physics: volume + floors → one surface per connected body | **ruled** (R1); P3 builds it; ponds join as nodes (`pond_depth_design` §3) |
| one floor record per square: `depthGrid` (dug) and `bedRecord` (natural) | built; natural floors written lazily today; B2 writes them at map start |
| one picture rule: wet square's terrain chosen by water depth from one ladder | **not yet**: lakes and digs use two ladders on two layers. B2 unifies |
| vanilla sees every wet square as water of the right type | lakes yes; digs no (temp layer). B2 fixes |
| limitless water is the same representation with an infinite volume | ruled (16); its floors are a rule, its depth a readout |
| moving water stays vanilla | rivers keep `River` tag, flow and floods; our river works stay as they are |

**The biggest trap:** thinking flags fix it. The water-body tracker and the freeze manager decide by **layer**; the
fill defs already carry Freshwater and still get no fish. The second trap is §2.3.1: even on the base layer, water that
**grows** into a lake never rolls fish without an adapter. The third is identity checks on `WaterDeep`: keep vanilla
`WaterDeep` (or vanilla-identical) as the deep band so roads and mods that compare by identity still work, which in turn
forces the deep-walkability question (§6 Q3).

**Where the line stays:** oceans and edge rivers. They are "our water with infinite volume", and the player cannot tell
the difference, because their surface never moves. That is one kind of water with one exception the rules already name.

---

## 5. Recommendation

1. **Option B2, folded into the rebuild as a work package right after P3** (P3 writes the surface; B2 decides how it is
   drawn and what vanilla sees). Proposed item name: `WATER_LAYER_UNIFY_ONE_LADDER_FOR_ALL` (not filed; the owner's
   card first).
2. **Ship the §2.3 adapters whatever he picks**, because trap 2 (fish lost on a full drain and refill) is a bug in
   today's ruled pond design.
3. **Do not convert rivers or oceans** (C).
4. **Live proof is owed before it ships:** a canal that freezes and thaws with its water picture intact; a fishing zone
   on a 100+ square dug reservoir; reeds surviving a pump cycle; a seasonal flood over a wet canal. Minimal list, no
   flyers.
5. **What would change this:** if the owner does not want fish in dug water (Q2 b), B2 still earns its keep through ice,
   floods and one art ladder, but A plus a "canals never freeze" note becomes defensible at a fifth of the cost.

---

## 6. Decisions for the owner (question-card wording)

**Q1. One kind of water, or two?**
- (a) **One: a pond you dig and a natural pond are the same water. Same pictures by depth, and the game treats both as
  real water: fishing, ice, reeds, swimming.** *Recommended; about 5 to 8 days, fitted into the rebuild.*
- (b) Two, as planned: dug water swims and puts out fires but never has fish and never freezes. About 1 to 2 days.
- (c) Also turn rivers and oceans into our water. About 20 to 38 days; you would see no difference in play.

**Q2. Can a pond you dig get fish?**
- (a) **Yes, by the game's own rule: a body of water of about 75 squares or more can hold fish, and it is likelier the
  bigger it is.** *Recommended: same rule as a natural pond.*
- (b) No, only natural water ever has fish.
- (c) Yes, any size (our own rule; small ponds would have fish the game never gives them).

**Q3. Water 2 m and deeper: can people go in it?** (It decides whether lakes and pits follow one rule.)
- (a) **The game's rule everywhere: deep water blocks walking, in lakes and in dug pits alike. Someone who falls in or
  is caught by rising water swims to the nearest edge they can climb out at.** *Recommended: one rule, closest to the game.*
- (b) Everyone can go into deep water anywhere; swimmers cross it, others risk drowning (your relative drowning rule).
  Lakes become places people can drown.
- (c) Keep today: deep water in a dug pit can be entered, deep lake water cannot.

**Q4. When does a natural lake become "ours"?**
- (a) **When the map is made: every lake and pond gets its floor and its water recorded at once. Nothing looks
  different.** *Recommended: lakes and digs then behave the same from the first hour.*
- (b) The first time a canal, pump or bottle touches it (today).

**Q5. A pond that dries out completely and fills again: what about its fish?**
- (a) **The same fish come back when it refills.** *Recommended: matches your rule that a refilled pond returns to
  its exact shape.*
- (b) It rolls new fish by size, as a new pond would.
- (c) The game's own behaviour: it never gets fish again. (Today's code does this, by accident.)

**Q6. Reeds, lilies and lotus in water that a pump keeps raising and lowering:**
- (a) **They live through short changes; only water that stays too deep (or dry) for a while kills them.**
  *Recommended.*
- (b) The game's own rule: they die the moment the water goes too deep.

---

## 7. The outside read (GPT) and its disposition

Model gpt-6.1-sol (default), via `src/RimMandrake/Utils/gpt_consult.py`, kept verbatim as
`flowworks_natural_water_engine_2026-10-17.gpt_read.md`. It got the question, the context in prose, the pond-stage defs
and the flip-fix patch. It was not shown this doc. It read its own decompile, so its line numbers may differ from
RimSage's.

**Agrees (independently):** one physical model for natural and dug water, with natural vs dug as provenance and finite
vs limitless as a boundary condition; rivers and oceans stay limitless with vanilla metadata; band swaps within one
water type do not rebuild bodies; vanilla never splits a body; the freeze-manager null dereference on freezable water
with no body; no vanilla drinking, drowning or boats; no vanilla aquatic crop.

| # | point | disposition |
|---|---|---|
| 1 | **Estimates higher: A 6-12, B 10-20, C 20-40 agent-days** | **NOTED, not adopted.** Its A includes adapting the solver to natural bodies, which P3 and the pond-as-node design already count. Its B includes integer decilitres for ponds (ruled R1, inside P3). On top of the rebuild, this doc keeps 1-2 (A) and 5-8 (B2). **The honest range for B2 is 5 to 10**: GPT's figure is a reason to budget the upper end. |
| 2 | `RM_WaterChestDeepStill` inherits the `ShallowWater` affordance (it is parented to `WaterShallowBase`), unlike vanilla chest-deep; shallow-water building stays allowed at 1.5 m | **ACCEPT, new finding.** In B2's ladder the 1.5 m band takes vanilla `WaterChestDeepBase`'s affordances. Fix is one def; belongs to the rebuild whatever is chosen |
| 3 | Drying removes fishing-zone cells (`RemoveCellFromExistingBody` → `Zone_Fishing.RemoveCell`); refilling does not put them back | **ACCEPT.** Confirmed in RimSage (`WaterBodyTracker.cs:229-234`). Added to trap 2's adapter: remember zone cells by footprint and restore them on refill |
| 4 | Band swaps can cancel blueprints and frames whose affordance the new band lacks | **ACCEPT** into B2 step 5 (things on squares that change band) |
| 5 | Vanilla terrain writers (moisture pump `CompTerrainPumpDry` via `driesTo`, seasonal and torrential floods) must reconcile with FlowWorks' volume, or vanilla and FlowWorks fight over a square | **ACCEPT.** The moisture pump was already open (2026-10-11 review #14). B2 adds: a `driesTo` write on a body's square removes that square from the body (as digging a dry bed does); floods get a live row (§2.2 point 3) |
| 6 | Watermills need `MovingFluid` and `WaterInfo` flow data; flags do not make flow | **ACCEPT**; rivers are untouched in A and B2, and this is one more reason against C |
| 7 | "Prefer B for new maps; migrate existing maps through A" | **PARTLY.** B2's migration already converts an old save once on load; running two models side by side for old saves is the "two kinds" the owner objects to. Offered only if a migration test fails |
| 8 | It did not raise the temp-layer cause of "no fish in canals" | Not a disagreement: it was not told canals are temp terrain. It confirms the mechanism (`GetWaterBodyType` ignores temp terrain) |
