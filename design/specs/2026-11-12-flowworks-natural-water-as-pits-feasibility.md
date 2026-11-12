# FlowWorks: can natural water become real pits? Feasibility study

Date 2026-11-12. Item `RIMMANDRAKE_DESIGN_NATURAL_WATER_AS_PITS_NOT_FLAT_PONDS`. Study only: no mod code changed, no game run.
This file: `D:\Luke\dev\RimMandrake\design\specs\2026-11-12-flowworks-natural-water-as-pits-feasibility.md`
Copy, census data and the offline probe: `D:\ClaudeWork\rimmandrake\conductor\natural_water_20261112\`

Every claim carries a tag: **[measured: where]**, **[guess ~N%]** (my confidence it is right), or **UNMEASURED**.
"Source" below means `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\Source`. "Engine doc" means
`D:\Luke\dev\RimMandrake\design\RimMandrake\flowworks_natural_water_engine_2026-10-17.md`, which read the game's own code with RimSage on
2026-10-17. RimSage was not available in this session, so every vanilla class or field named here comes from that document or from
the game's own XML on disk; anything else about the game's code is marked UNMEASURED.

## Summary (12 lines)

1. **Verdict: feasible, with one fixed condition.** Still bodies (ponds, lakes, marsh, typed-liquid lakes) can be real pits with a bed map
   made at map load. [guess ~80%] The condition: a wet square must keep a game-recognised water terrain on it. Fishing, wild water plants,
   ice, fire, swimming and the water shader all read the terrain, not our grids. [measured: engine doc section 2.1]
2. **This is not a new question.** You asked it on 2026-10-17 and ruled R10 to R13: one kind of water, floors recorded at map load, lake
   pictures unchanged, rivers and sea left alone. About two thirds of "natural water as pits" is already built on that ruling. [measured: section 1.3]
3. **What you saw as "flat pond shrinking to mud" is the part R10 chose not to change:** the lake's picture. The books already hold a
   bed and exact litres; the screen still shows a flat sheet at ground height. [measured: Source\RM_LiquidStock.cs:263-283]
4. **Five real gaps** remain: the water surface is never drawn below the bank; rivers, sea, map-edge lakes and big lakes on wet tiles
   have no bed and never go down; a lake is one bowl in the solver (no inner ridges); see-through and "stands on its bottom" skip
   vanilla water; ponds get no direct rain and no evaporation. [measured: section 1.4]
5. **Size is not the obstacle.** On 70 saved maps natural liquid covers a median 0.4% of the map, 12% at the 90th percentile, 23% at
   most (about 14,500 squares). [measured: `D:\ClaudeWork\rimmandrake\conductor\natural_water_20261112\water_census_70_saves.json`]
6. **Solver cost is the real risk for "every lake square is a pit square".** In the Python twin of our solver, a 3,000-square lake as
   one node solves in 0.0002 s; as 3,000 nodes it takes 0.016 to 0.053 s, 80 to 230 times more. [measured: `...\offline_probe_out.txt`]
7. **Four designs** (section 5): A finish the picture on today's model, about 7 agent-days; B true pits for still bodies with river and sea as
   held-level edges, about 18; C everything finite including rivers, about 35; D convert a body only when engineering first touches it, about 13.
8. **Recommended: A first, then B on top of it.** A is wholly reused by B, and A alone removes the "flat texture" complaint. [guess ~70%]
9. **Rivers and sea are your call.** Giving them a bed and the pit picture is cheap. Making a river truly run dry behind a dam is the
   expensive, risky part (design C) and reverses R10's "never run dry".
10. **Biggest unknown: how a lowered water surface looks** where a deep pit meets a lake or river. No scene has ever looked at it.
    [measured: `D:\ClaudeWork\rimmandrake\conductor\clear_water_feasibility_20261112\STUDY.md`] Cheapest test: an offline mock-up from a real save, half a day.
11. **Nothing here needs worldgen, save migration or another water mod.** All of it is map-level, at map load.
12. **Six questions are yours** (section 6.4), first: do rivers and the sea stay bottomless, or do they get a real budget?

---

## 1. What exists today

### 1.1 The natural bodies, kind by kind

The game makes water at map creation from tile features (lake, pond, lake with islands, oasis, wetland, coast, river, cave lakes,
marshy, harbour). [measured: engine doc section 1.1] Each wet square holds one terrain. These are all the liquid terrains in the game's
own files: [measured: `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\TerrainDefs\Terrain_Water.xml` and
`...\Data\Odyssey\Defs\TerrainDefs\Terrain_Water.xml`, `Terrain_Temporary.xml`, `Terrain_Natural.xml`]

| Kind | Terrain names | What the game does with it | What FlowWorks does with it today |
|---|---|---|---|
| Still fresh water | `WaterShallow`, `WaterDeep` | Shallow is walkable and bridgeable. Deep is impassable, no building. Fishable. | Limited body if small enough and off the map edge: bed recorded, exact litres, drains and refills. Otherwise limitless. |
| Marsh | `Marsh` | Walkable wet ground with its own plant tag. | Counts as natural liquid. The marsh map in the census was 10,404 squares in one map. Bed treatment of marsh: UNMEASURED. |
| River | `WaterMovingShallow`, `WaterMovingChestDeep` | Tagged River; flow arrows drawn from that tag. | Always limitless. No bed. Never goes down. [measured: Source\RM_StockMath.cs:126-133] |
| Sea | `WaterOceanShallow`, `WaterOceanDeep` | Tagged Ocean, salt water, never freezes. | Limitless (touches the map edge). No bed. |
| Toxic water (Odyssey) | `ToxicWaterShallow`, `ToxicWaterDeep`, moving and ocean twins | Water body type "Other" (no fish), toxic build-up. | Treated as natural liquid like any water. Separate handling: UNMEASURED. |
| Hot spring (Odyssey) | `HotSpring` | Shallow, never freezes, body type "Other", warms the air. | Treated as natural liquid. Separate handling: UNMEASURED. |
| Flood water (Odyssey) | `ShallowFloodwater`, `MarshFlood`, `ToxicFlood`, `SpringFlood` | Temporary layer laid over land by a storm. | Not a body. Left alone. |
| Thin ice (Odyssey) | `ThinIce` | Temporary layer laid over freezable water in the cold. | Left to the game. |
| Lava (Odyssey) | `LavaDeep` (base), `LavaShallow` (temporary) | Burns, glows, impassable. The lines I read show no water tag and no water body type. | Not natural liquid by our test (which asks "is the base terrain water"). Lava as a FlowWorks liquid: UNMEASURED. |
| Our typed liquids | tar, acid, brine, propane, boiling and frigid water | Ours. Painted over the game's lake or sea at map creation on a tagged tile. Rivers are not repainted. [measured: Source\LiquidTypes\RM_GenStep_LiquidShores.cs:8-36] | Same body machinery as water. |

How FlowWorks sorts every body, once, the first time the map ticks: [measured: Source\RM_MapComponent_Excavation.cs:1302-1312; Source\RM_LiquidStock.cs:212-262, 298-309]

- It walks every natural liquid square and groups them into bodies.
- A body is **limitless** if it has moving water, touches the map edge, is too big to walk (over 4,000 squares walked), or is bigger than a
  cut-off that depends on the tile's rainfall: never on a tile under 250 mm, 40,000 down to 5,000 squares up to 700 mm, down to 600 squares
  at 1,500 mm and wetter. [measured: Source\RM_StockMath.cs:105-133; Source\RM_BedMath.cs:39] These numbers are marked provisional in the code.
- Only a **limited, still** body gets a bed. [measured: Source\RM_LiquidStock.cs:235-239] The terrain is not touched; the code logs "no terrain changed".
- Once limitless, always limitless (your ruling 16). [measured: Source\RM_LiquidBody.cs]

So the brief's line "rivers, oceans and edge bodies get nothing" is nearly right: they are found and marked, but get no bed and no stock.

### 1.2 The dug-body model (what a pit is)

- **Cells.** Each dug square stores a depth in whole half-metre notches. One square is 2 square metres, so one notch of one square holds
  1,000 litres. [measured: Source\RM_LevelSolve.cs, constant U = 10,000 decilitres]
- **Water.** Stored as exact decilitres, not steps, since 2026-10-17. [measured: commit 5d6e8986c5, via `D:\ClaudeWork\rimmandrake\conductor\fill_history_20261112\HISTORY.md`]
  The old whole-step "fill N" view still exists beside it and is read on 42 lines in 26 files; your ruling today deletes it.
- **Level solve.** Fill-and-spill: water settles to one level across joined squares, lowest first, conserving every decilitre. A whole
  natural pond enters the solve as **one node** holding a table of "how many squares are at least this deep". [measured: Source\RM_LevelSolve.cs;
  Python twin `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\northstar\level_water.py:148-228`]
- **Sources.** A limitless body gives without end. A limited body gives from its stock.
- **Rain.** Falls into open, unroofed dug squares only: 0.1 notch (5 cm) per pulse at full rain. [measured: Source\RM_MapComponent_Excavation.cs:3560-3569;
  Source\RimMandrakeFlowWorksMod.cs:192] Open item `RIMMANDRAKE_SLOW_RAIN_FILL_PIT_BRIMS_IN_ONE_NIGHT` says this is too fast.
- **Groundwater.** A limited pond regains 0.13 notch (6.5 cm) per square per day in dry weather, more in rain, scaled by season (wet 1.25,
  dry 0.5, cool 0.75). [measured: Source\FluidDef.cs:124-129; Source\RM_StockMath.cs:137-161] An empty 2 m pond refills in about 31 dry days. [measured arithmetic: 4 notches / 0.13]
- **Evaporation.** None for pits or ponds. It exists only for thin overland sheet water. [measured: Source\RM_SheetMath.cs:604-618; a search of Source found no other]
- **Seepage out of a dug pit into the ground.** UNMEASURED (I found none; I did not prove there is none).
- **Walls.** A pit draws its walls from a separate picture layer. Where a pit meets natural water or the map edge, no wall is drawn.
  [measured: Source\Superdeep\RM_ExcavationWalls.cs:556-566]

### 1.3 What is already built toward "natural water as pits"

You asked on 2026-10-17: "should we just replace them on maps with our own pits right away". The answer then was option B2, ruled as R10
to R13. [measured: engine doc] Built since:

| Piece | State | Where |
|---|---|---|
| Bed map for limited still lakes, made at map load from the lake's shape, map seed and tile roughness | built | Source\RM_LakeFloorMath.cs (687 lines); ceiling 50 m, settable |
| One depth ladder of water pictures by true metres, shared by lake, pond, canal and pit (edges at 0.25, 0.75, 1.25, 1.75 m; navy tint at 5 m and 10 m) | built | Source\RM_WaterLadder.cs |
| A drained pond's dry bed is a real hollow: walls, climbing, pawns stand lower | built, on by default | Source\RM_MapComponent_Excavation.cs:575-586; setting `pondBedHollowEnabled` |
| Pond goes down in stages: deep, chest-deep, shallow, thin, mud for 2 days, lakebed | built | Source\RM_PondDepthMath.cs |
| Fish come back when a pond refills; a split body is two bodies; water plants get a grace period | built | Source\RM_WaterBodyMendGame.cs (item closed at ee9fa61fbc) |
| Swimming in water 2 m and deeper (R12) | built | Source\Swimming\RM_Swim.cs |
| Groundwater refill and the rainfall cut-off | built | Source\RM_StockMath.cs |
| River works: weirs, ferry, levee, silt | built to some degree; depth of proof UNMEASURED | Source\Rivers\ |

### 1.4 The gaps between today and "natural bodies are pits"

1. **A wet natural square is not a pit square.** Its dug depth is 0. It reads as "superdeep" by a special case, not from a grid.
   [measured: Source\RM_MapComponent_Excavation.cs:1380-1422] So nothing draws the water surface below the bank, and no bank wall shows as the level drops.
   This is the "flat texture" you described.
2. **Limitless bodies have no bed and never go down.** That covers every river, every sea, every lake that touches the map edge and every large
   lake on a wet tile. On a rainforest tile (1,500 mm and up) any lake over 600 squares is bottomless. [measured: Source\RM_StockMath.cs:105-121]
3. **A lake is one bowl.** The bed maker deliberately fills inner holes up to their rim so the "one node" shortcut stays true.
   [measured: Source\RM_LakeFloorMath.cs, "one basin"] A real pit lake would leave pools behind ridges. The probe shows the difference:
   a 1,009-square lake with a ridge, drained from the east, keeps 5% as one node and 39% as true pit squares, with the west half still
   75% full. [measured: `D:\ClaudeWork\rimmandrake\conductor\natural_water_20261112\offline_probe_out.txt`, last line]
4. **See-through water and "stands on its bottom" skip the game's own water.** Our clear-liquid pass only runs on our terrains.
   [measured: `D:\ClaudeWork\rimmandrake\conductor\clear_water_feasibility_20261112\STUDY.md`; Source\RM_LiquidSurface.cs:159-229]
5. **No direct rain into a pond and no evaporation.** A pond gains only through the groundwater rule.
6. **You cannot dig in natural water, and filling it in is not built.** [measured: engine doc, citing Designator_DigCanal.cs:73-76 and Designator_FillInCanal.cs:82-92; not re-read today]
   The probe shows why this matters: a canal that only touches the shore drains just the top half metre of the lake, because the shore square is half a metre deep.
7. **"Fill N" for water is still in the code** (today's ruling removes it).

---

## 2. What the game and its DLCs do with water, and what each one reads

This table is the heart of the answer. The question for each row: if a natural body becomes a pit whose level can fall, does the
mechanic still work? Verdicts:

- **OK** = survives unchanged.
- **OK-T** = survives as long as a wet square carries a game water terrain with the right tag (which the R10 ladder already does).
- **PATCH** = needs our code to help. "(built)" means that help already exists.
- **BREAKS** = lost unless we rebuild it ourselves.

Source for the "reads" column is the engine doc sections 1.1 and 2.1 (RimSage, 2026-10-17) unless a file is named. "Core XML" is
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\TerrainDefs\Terrain_Water.xml`.

| # | Mechanic | What it reads | Verdict | Note |
|---|---|---|---|---|
| 1 | Fishing zones and fishing work (Odyssey) | The map's water body tracker, which groups squares by the terrain's water body type (fresh, salt, other). It looks under temporary layers. | OK-T + PATCH (built) | The game rolls fish once per body by size (none under 75 squares) and never re-rolls; a dried pond loses its fish and zone squares. Our mend re-rolls and restores. [measured: Source\RM_WaterBodyMendGame.cs] |
| 2 | Animals fishing, fish shadows | Same tracker. Shadows need 12 or more squares. | OK-T | |
| 3 | Toxic fish from pollution | Body's polluted share. | OK | |
| 4 | Aquatic growing | The game has **no sowable water crop**. It has four wild water plants (reeds, lily pad, bulrush, lotus) that grow by terrain tag (fresh shallow, fresh shallow still, marshy, mud). | OK-T + PATCH (built) | Plants die the moment their square's tag stops matching. Our grace period softens it. A falling lake moves its shallow band inward, so the reed belt follows the shoreline, which looks right. [guess ~70%] |
| 5 | Aquatic grow zones from our own or other mods | UNMEASURED which mod the owner means; vanilla has none. | UNMEASURED | Owner question 5. |
| 6 | Swimming for joy | Top terrain is water, not toxic, standable, outdoors, 10 C or warmer. | OK-T | Our R12 swim in deep water is ours and reads our depth. |
| 7 | Bathing | No bathing need in the base game or DLCs. [guess ~85%] Hot spring gives a thought when walked through. [measured: Odyssey XML `HotSpring` traversedThought] | OK-T | |
| 8 | Bridges | Terrain affordance "Bridgeable" on shallow water; deep water has no affordances. [measured: Core XML] | OK-T | A bridge over a pond that drains ends up over a dry hollow. What holds it up: UNMEASURED. |
| 9 | Building on or in water, waterproof conduit | Affordances on the terrain. [measured: Core XML] | OK-T | |
| 10 | Pathing and walk speed | Terrain path cost (shallow 30, deep impassable 300) and extra cost when not drafted (180). [measured: Core XML] | OK-T | Our ladder swaps terrains by depth, so the walkable band moves as the level moves. |
| 11 | Soaking-wet thought | Terrain's traversed thought. [measured: Core XML] | OK-T | |
| 12 | Putting out fire, pawns jumping in water when burning | Terrain flag "extinguishes fire" on the top terrain. | OK-T | |
| 13 | Filth | Water accepts no filth (mask None). [measured: Core XML] | OK-T | |
| 14 | Items rotting faster in water | Terrain's extra deterioration factor 3. [measured: Core XML] | OK-T | |
| 15 | Pollution picture and spread (Biotech) | Pollution grid per square; water terrains name a polluted texture and shader. [measured: Core XML] | OK-T | Pollution riding with moved water is ours to decide: UNMEASURED today. |
| 16 | Ice (Odyssey thin ice) | Freezer lays a temporary ice layer on top terrain that can freeze, at -7 C and below, melts at 2 C. One temporary layer per square. | OK-T + PATCH (built, one fix) | The game's freezer reads the water body without a null check; we already carry a fix. [measured: Source\RM_WaterBodyFreezeCountFix.cs] Ice on a lake whose level is 3 m down a pit: picture UNMEASURED. |
| 17 | Moisture pump | Terrain's "dries to" field (shallow water dries to gravel, marsh to soil). | PATCH | A pump that turns a pit lake square to gravel must also tell our books the square is gone. Whether that hook exists: UNMEASURED. |
| 18 | Marsh | Its own terrain and tag. | OK-T | Marsh as a pit is a design choice (section 3.2). |
| 19 | River flow arrows and ripples | Base terrain tagged River. | OK-T | If a river square is drained and its terrain changes, the flow picture stops there. That is correct. |
| 20 | Water shader and depth picture | Terrain names the water depth shader; the game draws depth from the terrain. [measured: Core XML `waterDepthShader`] | OK-T, but this is where the flat look comes from | The shader has no idea of a level below the bank. Any lowered-surface look is our own drawing. |
| 21 | Ambience, beauty | Terrain stats (toxic water has beauty -6 [measured: Odyssey XML]). Water sounds: UNMEASURED. | OK-T | |
| 22 | Flood events (Odyssey) | Each water terrain names a flood terrain; a storm lays it on nearby land. | OK-T | A flood from a lake that we show as half empty would look wrong. PATCH worth a setting. [guess ~60%] |
| 23 | Map edge, caravans entering and leaving | The world reads biomes, never map terrain. No boats in the game. | OK | |
| 24 | Raids and drop pods avoiding water | UNMEASURED which check they use. Likely walkability and roof. [guess ~70%] | OK-T [guess] | A drained lake becomes a place raiders can cross. That is a feature. |
| 25 | Wild animals | One spawn check compares against the shallow ocean terrain by name. | OK | |
| 26 | Road generation | One check compares against the deep water terrain by name, at map creation. | OK | It runs before our conversion. Order must be kept: our step last. |
| 27 | Gravship landing and take-off (Odyssey) | Terrain's "gravship replacement terrain" (deep water becomes shallow under a ship). [measured: Core XML] | PATCH | A ship landing on a lake changes terrain under us. Our books must follow the change. Whether they do today: UNMEASURED. |
| 28 | Lava | Its own terrain family, not tagged water in the lines read. [measured: Odyssey XML lines 110-135] | Not affected | Lava as a moveable liquid is a separate item. |

**Reading the table.** Twenty of 28 rows survive on one condition: the wet square keeps a real game water terrain. Three need a patch that
is already built. Three need a small new patch (moisture pump, gravship, flood). One is unmeasured (row 5) and one is not affected (lava).
Nothing in the base game or DLCs BREAKS. What would
break it all is the literal reading of "replace natural water with pit terrain": our own non-water terrain on the square. That was
ruled out on 2026-10-17 and should stay ruled out. [measured: `D:\Luke\dev\RimMandrake\design\RimMandrake\flowworks_natural_water_play_2026-10-17.md` section 5.5]

So "become pits" must mean: **the pit lives in our grids and our drawing; the square's terrain stays the game's water**, chosen from the
depth ladder by how much water stands on that square. When the square has no water, it gets mud and then lakebed, and stops being water
for the game. That is exactly what the game expects of a dried pond.

One trap the table hides: the game can only show **one temporary layer per square**. Ice, flood water and shallow lava are all that one
layer. We must never use the temporary layer for our water. R10 already chose the base layer for this reason. [measured: engine doc]

---

## 3. The conversion itself

### 3.1 Where the bed map comes from

There is no height data in a RimWorld map. The only facts at map load are: which squares are wet, which terrain each has (shallow,
deep, moving, ocean, marsh), the map seed, and the tile's hilliness, rainfall and biome. The bed has to be **made up, the same way every
time**, from those. The existing bed maker already does this for limited lakes: depth grows with distance from shore, shaped by noise,
scaled by tile roughness, and every step is at most 1 m so a pawn can climb out. [measured: Source\RM_LakeFloorMath.cs]

One rule fixes most of the freedom: **at full level the map must look exactly as the game made it.** A square the game drew as shallow
must have a bed in the shallow band (about 1 m); a square drawn deep must be 2 m or more. [measured: band edges in Source\RM_WaterLadder.cs]
So the game's own shallow and deep pattern is the top of the bed map, and we only invent how deep "deep" goes.

Because the bed is a pure function of the footprint and the seed, it does not need to be saved. Only the water amount is saved.
[measured: Source\RM_LakeFloorMath.cs header: "pure function"]

### 3.2 Each kind of body

| Body | Bed | Level behaviour | Confidence |
|---|---|---|---|
| Pond, lake (still, any size, not at the edge) | Existing bed maker, unchanged. Remove the rainfall size cut-off so big lakes on wet tiles also get a bed. | Finite. Drains, refills. | [guess ~85%] |
| Lake touching the map edge | Same bed maker for the part on the map. | Your call: finite (the off-map part is ignored) or held level (the off-map part is assumed endless). | [guess ~70%] |
| Marsh | Flat bed one notch (0.5 m) down, holding 0.1 to 0.3 m of water. Exact decilitres make this possible; whole steps never could. | Finite and shallow: a marsh is the first thing to dry in a drought and the first to flood. Drained marsh becomes soil, which is what the game's own "dries to" says. [measured: engine doc] | [guess ~60%] |
| River | Bed from the game's own two depths (shallow about 1 m, chest-deep about 1.5 m), deepening to the middle of the channel. | Design B: level held by the map edge, endless, but gives water only as fast as a set flow. Design C: a real flow budget, can be dammed dry. | bed [guess ~80%], damming [guess ~50%] |
| Sea | Shelf: shallow ocean about 1 m, deep ocean sloping away with distance from shore to a cap (say 10 m). There is an open item for this: `SEABED_LAYER_DESIGN_ITS_OWN_SEA_FLOOR`. | Always held level. Nobody drains the sea. | [guess ~85%] |
| Hot spring, toxic water | As ponds. A hot spring should refill fast (it is a spring). Toxic water keeps its terrain family in the ladder: needs four more ladder rows. | Finite. | [guess ~60%] |
| Typed-liquid lake or sea (tar, propane, brine, acid) | As lake or sea. | Finite for lakes. No rain refill for tar or propane: they refill by seepage only, slowly, or not at all. | [guess ~65%] |
| Cave lake | As pond; roofed, so no rain and little evaporation. | Finite, seepage only. | [guess ~70%] |
| Lava | Not in this conversion. | Unchanged. | |

### 3.3 Starting level

Full to the brim on the day the map is made, so the first sight of the map is the game's own picture. [guess ~80% this is what you want]
A setting could start bodies lower on dry tiles or in the dry season. I would leave it off by default.

### 3.4 The water budget

One square is 2 square metres. One notch (0.5 m) on one square is 1,000 litres. [measured: Source\RM_LevelSolve.cs] Some worked sizes: [measured arithmetic]

| Thing | Litres |
|---|---|
| Canal, 100 squares, 2 m deep | 400,000 |
| Moat, 300 squares, 3 m deep | 1,800,000 |
| Pond, 200 squares, mean 2 m | 800,000 |
| Lake, 1,000 squares, mean 2 m | 4,000,000 |
| Lake, 3,000 squares, mean 4 m | 24,000,000 |

So the moat empties the pond twice over and takes 0.9 m off the 1,000-square lake. That is the scale of drama you asked for: real, visible, not instant ruin.

The flows that should exist, with a first number for each. Every number here would be a Mod Setting. All are [guess ~50%] as tuning values; the arithmetic is exact.

| Flow | Today | Proposed first value | Why |
|---|---|---|---|
| Rain straight onto a body | Only onto dug squares, 5 cm per pulse (known too fast) | 1 cm per square per rainy hour at full rain, the same for pond, lake and pit | One rule for all open water. A full rainy day adds about 0.24 m. |
| Run-off from the land around | None | Rain on the body times 2 | Stands in for the catchment. Makes lakes on wet tiles stay full without calling them bottomless. |
| Groundwater seepage | 6.5 cm per square per day, limited bodies only, always inward [measured: Source\FluidDef.cs:129] | Same top rate, but proportional to how far the level is below a "water table" height for the tile; outward when above it | Gives slow refill in drought and stops a pit on dry ground holding water for ever. The water table height comes from tile rainfall. |
| Evaporation | None for ponds or pits | 1 cm per square per day at 20 C, none at freezing, double at 40 C, none under a roof | A real lake loses 1 to 2 m a year; a RimWorld year is 60 days, so 1 cm a day is the low end of real, scaled to the short year. |
| River through-flow | Endless | Design B: a river mouth gives at most 20,000 litres a day per square of canal mouth | A canal off a river fills a 400,000 litre canal in 20 days per mouth square; a wide intake is worth building. |
| Sea | Endless | Endless | |

Check on the balance, for a 1,000-square lake: evaporation takes 20,000 litres a day (1 cm on 2,000 square metres). Seepage at full
deficit gives 130,000 litres a day. One rainy day gives about 480,000 litres direct and 960,000 with run-off. [measured arithmetic]
So with these numbers rain dominates, seepage is the steady hand, and evaporation only matters on dry tiles. If you want droughts to
bite, evaporation is the dial to raise.

---

## 4. Cost and risk

### 4.1 How many squares

Measured on 70 different saved maps, all 250 by 250 (62,500 squares). [measured: `D:\ClaudeWork\rimmandrake\conductor\natural_water_20261112\water_census_70_saves.json`, made by `census.py` beside it]

| Share of the map that is natural liquid | Value |
|---|---|
| Median | 0.4% (about 250 squares) |
| 75th percentile | 1.7% (about 1,060) |
| 90th percentile | 12.3% (about 7,700) |
| Largest | 23.2% (14,515 squares, a marsh map: 10,404 marsh) |
| Maps with none | 26 of 70 |

Largest by kind: river map 13,271 squares (12,045 moving water); coast map 12,329 (11,000 ocean); largest still lake only about 3,100
shallow squares; deep still water at most 266 squares on any one map.

Three cautions about this census. These saves are mostly test and proof maps, not a fair sample of the maps you play. No map made by
the game's large "Lake" feature is among them, so **the size of a big lake is UNMEASURED**. And my script only counted terrains whose
names contain water, marsh, ocean, lava, flood, ice, tar, acid, brine, propane, liquid or fill; a liquid named otherwise would be missed.

### 4.2 Solver cost

Today a lake is one node whatever its size. The probe ran the shipped solver's Python twin both ways. [measured: `D:\ClaudeWork\rimmandrake\conductor\natural_water_20261112\offline_probe_out.txt`]

| Lake | One node | One node per square | Ratio |
|---|---|---|---|
| 197 squares, 2 m | 0.0002 s | under 0.001 s | 2 |
| 1,009 squares, 4 m | 0.0002 s | 0.004 s | 25 |
| 3,001 squares, 6 m | 0.0002 s | 0.016 s | 84 |
| 3,001 squares, 20 m | 0.0002 s | 0.053 s | 229 |
| 9,845 squares, 6 m | 0.0002 s | 0.057 s | 283 |

These are Python times. They rank the two models; they are not what C# will cost. C# cost at this size is UNMEASURED. The shape is
clear: per-square cost grows with squares times depth, and a 12,000-square river or sea as individual nodes is not affordable every
pulse. [guess ~75%] The way through is a middle model: **one node per basin**, not per square and not per lake. A basin is a part of the bed
that drains to one low point; basins are cut once at map load. A typical lake has 1 to 10. That keeps today's speed and gives the pools-behind-ridges
behaviour. [guess ~70% it works without changing the solver, since a basin is exactly today's pond node]

### 4.3 Drawing cost and the part-drained look

- Changing a square's terrain makes the game redraw that map section and rebuild its path regions. Cost per write live: UNMEASURED.
  Today the pond painter is limited to 400 terrain writes per pulse. [measured: Source\RM_PondDepthMath.cs, DefaultStageWritesPerPulse]
  A 3,000-square lake needs 8 pulses to repaint fully. That limit stays.
- What a part-drained lake needs on screen, that it lacks today: (a) a bank face between the old shoreline and the lowered water,
  as tall as the drop; (b) the water tinted or shaded to read "lower"; (c) things in it drawn standing on the bed (today's ruling).
  All three already exist for dug pits. [measured: Source\Superdeep\RM_ExcavationWalls.cs; STUDY.md named above] The work is letting them
  run on natural squares. The one line that stops it today is the "no wall against natural water" rule at RM_ExcavationWalls.cs:556-566.
- **UNMEASURED and the biggest unknown:** whether the game's water shader, drawn at ground height, can be made to read as lowered by
  walls and tint alone. If it cannot, we draw our own water surface over vanilla terrain, which is more work (about 4 more agent-days). [guess ~60% walls and tint suffice]

### 4.4 Saves

- No migration code is owed before release (standing rule). Old maps simply form their beds again at first tick.
- The bed is recomputed from the seed, so the save grows only by the water amount per body or basin: a few numbers.
- If natural squares get real entries in the depth grid (design B), the grid is already map-sized, so the save does not grow. [guess ~80%]
- Risk: if the bed maker's code changes after release, old saves would get a different bed under the same water. After release the bed must be saved or the function frozen.

### 4.5 Every place that assumes "natural water is full and level"

Counted in Source today: [measured: grep, 2026-11-12]

| What the code asks | Lines | Files | What changes |
|---|---|---|---|
| "Is this a source square?" (natural liquid, not dug) | 31 | 16 | Each caller must decide: does it mean "water here" or "endless water here"? |
| "Is this body limitless?" | 82 | 22 | Most stay. Fewer bodies will answer yes. |
| "Is this natural liquid?" | 14 | 4 | Becomes "is there water on this square now". |
| "Is this terrain water?" | 85 | 38 | Mostly safe, since wet squares keep water terrain. Each needs a glance. |

Named single points: depth of a natural wet square is a special case, not a grid read (RM_MapComponent_Excavation.cs:1380-1422); walls skip
natural water (RM_ExcavationWalls.cs:556-566); rain skips anything not dug (RM_MapComponent_Excavation.cs:3560-3569); the dig tool refuses water;
the bed maker forces one bowl per lake. River works (weirs, ferry, levee) and pump intakes: what they assume about river level is UNMEASURED.

---

## 5. Four different designs

Agent-days are all [guess ~50%]: one agent, offline build plus proofs, not counting your live looks.

### Design A: "Finish the picture" (keep today's model, fix what you see)

- **What it is.** Keep the pond as one solver node and keep rivers and sea endless. Add what is missing on screen and in the budget:
  bank walls and lowered-water look on natural squares; see-through and "stands on its bottom" on vanilla water; rain and evaporation on ponds;
  digging into a lake bed; remove the rainfall size cut-off so big inland lakes are finite.
- **What you see.** A canal cut to a lake: the lake's surface visibly sinks below its bank, the shore steps down as a wall, reeds and
  shallows move inward, fish stay while 75 squares of water remain, the bed is a walkable hollow when dry. Rain brings it back.
  Rivers and the sea look as they do now.
- **What breaks.** Nothing in the game. Lakes still have one bowl: no pools left behind ridges.
- **Cost.** About 7 agent-days: walls on natural squares 2, see-through and bottom-standing on vanilla water 2 (shared with today's other ruling), rain and evaporation 1, dig in water 1, cut-off and settings 1.
- **Offline proof.** Read a real save's terrain grid with `D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\rimbench\savemap.py`; build beds with the bed
  maker's rules; run `level_water.py` through a script (dig a canal, 10 rainy days, 30 dry days); assert not one decilitre is lost; write one picture per day.

### Design B: "True pits for still water; river and sea are held-level edges"

- **What it is.** Everything in A, plus: every still body, of any size, edge-touching or not, is a set of **basins** cut at map load, each a
  solver node with its own level. Natural squares get real depth entries, so every pit rule (walls, climbing, rain, objects, see-through)
  applies with no special case. Rivers and sea get a bed and the pit picture, but their level is pinned by the map edge: they give water at a
  set rate and never fall.
- **What you see.** All of A. Also: a drained lake leaves pools in its deep spots; two lakes joined by your canal settle to one level;
  an island lake drains around its island; you can dig the lake bed deeper or fill part of it in; a river fills your moat at a rate that
  makes intake width matter; a moat joined to the sea is salt. A tar lake can be led by canal to a tar moat.
- **What breaks.** The "limitless by size" idea goes away for still water, so the 22 files that ask about it need review. A lake that touches
  the map edge becomes drainable (or you rule it held). Ice on a lowered lake needs a look.
- **Cost.** About 18 agent-days: A's 7, basins 3, depth entries for natural squares and removing the special cases 4, river and sea beds and flow rate 2, typed liquids and toxic ladder rows 1, proofs 1.
- **Offline proof.** As A, plus the ridge case from the probe on a real lake, plus a timing table per pulse for the largest census maps.

### Design C: "Everything is finite, rivers too"

- **What it is.** B, plus the river has a real flow: water enters at the upstream edge at a set rate and leaves downstream. A dam really
  floods upstream and dries the bed below. The sea stays endless.
- **What you see.** All of B. A weir makes a reservoir. A diverted river leaves a dry bed you can build in. Floods follow a broken dam.
- **What breaks.** River flow arrows and river fishing stop where the bed dries (correct, but needs our handling). The existing river works
  were built on a fixed river level and need rework. The solver gets its first body that is never at rest: it has only ever settled still water.
  You rejected per-tick fluid simulation before; a flowing river must be done as a pulsed budget or it is that again. [measured: `D:\Luke\dev\RimMandrake\design\RimMandrake\liquids_framework_design.md`, by way of the seat's notes]
- **Cost.** About 35 agent-days, high risk. The 2026-10-17 study put this family at 15 to 30. [measured: engine doc, option C]
- **Offline proof.** As B, plus a dam scenario on the census river map with a level-against-time chart upstream and downstream.

### Design D: "Convert on first touch"

- **What it is.** A body stays exactly as the game made it until engineering first joins it (a canal, pump or pipe). At that moment it becomes
  a design-B pit body. Untouched bodies cost nothing.
- **What you see.** Untouched water is vanilla. The moment your canal breaks through, the lake "wakes": bed, level, walls.
- **What breaks.** Two looks for the same water on one map. "Stands on its bottom" would be true in a woken lake and false in a sleeping one,
  unless drawing is done everywhere anyway (which is most of A). Rain and evaporation would not touch sleeping lakes, so a drought is invisible until you dig.
- **Cost.** About 13 agent-days. It saves solver time, which basins already save, so it buys little. [guess ~65%]
- **Offline proof.** As B, with the waking step shown before and after.

### Side by side

| | A | B | C | D |
|---|---|---|---|---|
| Removes the "flat texture" complaint | yes | yes | yes | only where touched |
| Lakes drain and refill by rain and seepage | yes | yes | yes | where touched |
| Pools behind ridges, dig the lake bed | dig only | yes | yes | where touched |
| Rivers and sea fill your works | yes, endless | yes, at a rate | yes, real budget | where touched |
| A river can be dammed dry | no | no | yes | no |
| Fuel or tar lake moved to your moat | yes | yes | yes | yes |
| Game features lost | none | none | river flow look and fishing on dried reaches | none |
| Agent-days | 7 | 18 | 35 | 13 |
| Risk | low | medium | high | medium |

---

## 6. Verdict

### 6.1 The answer

**Feasible: yes, for still bodies, at about 80% confidence.** Natural ponds, lakes, marsh and typed-liquid lakes can be real pits, with a bed
map made at map load and filled to the brim, without losing fishing, wild water plants, swimming, ice or any DLC feature.

The condition is the one from section 2: the pit is in our grids and our drawing, and each wet square keeps a game water terrain
picked by its water depth. "Replace the water with pit terrain" in the literal sense is not feasible without rebuilding fishing, plants,
ice and the water shader ourselves.

**Rivers and sea as pit pictures with a bed: yes, about 80%.** **A river that truly runs dry: possible, about 50%, and expensive.**

**Recommended path: A, then B.** A is the smallest thing that removes what you called "VERY strange", and every part of it is needed by B.
B is the design that matches your words "natural bodies of water actually become pits at game map load, filled appropriately, with a bottom
altitude map". C is a later decision once B is on screen. D is not worth its inconsistency. [guess ~70% you would pick the same]

### 6.2 The biggest unknown and the cheapest test

**Unknown:** does a natural lake whose surface is 1 to 5 m below its bank look right when drawn as vanilla water terrain plus our bank
walls and tint? Nobody has seen it. If it looks wrong, design A grows by about 4 agent-days for our own water surface layer.

**Cheapest test (half an agent-day, offline, no game):** take one real save with a lake; compute the bed; drain it to three levels
(0.5 m, 2 m, 5 m down); compose three pictures from the game's own terrain textures plus our existing wall and tint art, with a pawn, a
boulder and a reed standing on the bed. Put them beside the two mock-ups already made today
(`D:\ClaudeWork\rimmandrake\conductor\clear_water_feasibility_20261112\mockup_grid.png` and `mockup_contents.png`). You look once and say yes or no.

**Second unknown:** C# solver time with basins on the biggest maps. Test: the timing table in B's offline proof, then one live perf row.

### 6.3 Acceptance matrix (the scenes that must be looked at before anything is called done)

Each scene is looked at full, part-drained and dry, and again after rain refills it.

| # | Body | Size | Joined pit depth | Liquid | What it proves |
|---|---|---|---|---|---|
| 1 | Pond | under 75 squares | 0.5 m canal | water | Smallest case; no fish by game rule; level drop visible |
| 2 | Pond | about 200 squares | 2 m canal | water | Fish stay then go as it shrinks; reeds follow the shore |
| 3 | Lake | about 1,000 squares | 5 m pit | water | Bank wall 2 m and more; objects stand on the bed; see-through |
| 4 | Lake with a ridge | about 1,000 squares | 5 m pit on one side | water | A pool stays behind the ridge (design B) |
| 5 | Lake | 3,000 squares and up | 10 m pit | water | Navy deep tint; repaint over several pulses; perf row |
| 6 | Two lakes | 200 and 1,000 | joined by a 1 m canal | water | One level across both |
| 7 | Marsh | 5,000 squares and up | 1 m drain | water | Marsh dries to soil; map-scale repaint cost |
| 8 | River | full width | 2 m moat | water | Moat fills at the set rate; river look unchanged |
| 9 | River | full width | 10 m pit | water | Deep pit beside a river: the join nobody has looked at |
| 10 | Sea | coast | 3 m moat | salt water | Moat is salt; sea never falls |
| 11 | Lake at the map edge | any | 2 m canal | water | Whatever you rule for edge lakes |
| 12 | Typed lake | about 500 | 2 m moat | tar (opaque) | Things in tar are hidden below the line, not shown |
| 13 | Typed lake | about 500 | 2 m moat | propane or other fuel | A fuel lake led to your moat; no rain refill |
| 14 | Hot spring, toxic pond | small | 1 m canal | other | Keeps its own terrain family and thought |
| 15 | Frozen lake | about 200 | 2 m canal | water at -10 C | Ice on a lowered surface; freezer fix holds |
| 16 | Cave lake | small | 2 m canal | water | Roofed: no rain, seepage only |
| 17 | Lake under a landed gravship | about 200 | none | water | Books follow the game's terrain swap |
| 18 | Moisture pump beside a pit lake | any | none | water | Books follow the pump |

### 6.4 The questions that are yours, in order of how much they change the work

1. **Rivers and sea: bottomless, or budgeted?** Bottomless with a bed and pit picture (design B) is cheap and can never leave a map without
   water. A real river budget (design C) gives dams and dry beds, roughly doubles the work and reverses your 2026-10-17 ruling that rivers
   "never run dry". Middle course: B now, C judged later on screen.
2. **A lake that touches the map edge: finite or held?** Finite means you can drain a lake that visibly continues off the map, which may
   look false. Held means some lakes can never be drained, and the player cannot tell which without the R13 mark.
3. **Big lakes on wet tiles: finite now?** Today a lake over 600 squares on a rainforest tile is bottomless (provisional, your card of
   2026-10-18). With rain and run-off in the budget that rule is no longer needed: such a lake would be finite but refill fast. Removing it
   is simpler and more honest; keeping it guarantees wet biomes never dry.
4. **Does a drought bite?** With the numbers in 3.4, evaporation is too weak to dry a lake by itself. If you want lakes to shrink
   in a dry season with nobody touching them, say so and evaporation becomes the main dial. It also means fish and reeds die back by weather alone.
5. **"Aquatic grow zones": which do you mean?** The base game and DLCs have wild water plants but no sowable water crop. If you mean a
   zone from our own mods or want one built, that is a separate item; if you mean the wild plants, they are covered.
6. **Start full, or by season?** Full matches the game's picture on day one. By season is more real and risks a first sight of half-empty lakes.

---

## Evidence made by this study

| File | What it is |
|---|---|
| `D:\ClaudeWork\rimmandrake\conductor\natural_water_20261112\water_census_70_saves.json` | Terrain counts per save, 70 saves |
| `D:\ClaudeWork\rimmandrake\conductor\natural_water_20261112\census.py` | The script that made it |
| `D:\ClaudeWork\rimmandrake\conductor\natural_water_20261112\offline_probe.py` | One-node against per-square lake, on the shipped solver's Python twin |
| `D:\ClaudeWork\rimmandrake\conductor\natural_water_20261112\offline_probe_out.txt` | Its output |
| `D:\ClaudeWork\rimmandrake\conductor\natural_water_20261112\progress.md` | Milestones |

Not done in this study: no picture mock-up was made (the half-day test in 6.2 is the proposal); no C# was timed; no game was run.
