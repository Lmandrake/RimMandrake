# FlowWorks bridges: span anything (DESIGN, 2026-10-17)

Item: `FLOWWORKS_BRIDGES_DESIGN_SPAN_ANYTHING` (design, v1, for BENCH). **Design only: nothing in code, defs, the
bridge or the game was touched to write this.** Code claims are file:line at HEAD `3c1acfb11e`; vanilla claims are from
the defs on disk under `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data` (Core, Odyssey). Anything not
read is marked UNMEASURED.

Owner, verbatim (2026-10-17): *"make a ticket to add bridges to the redesign of FlowWorks, generalized over water or
non-water, or even grated ones that would allow fire up through them, or even at non-surface altitudes within a larger
area"*

It sits inside the one rebuild (`design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`, epic
`FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG`) and obeys its rulings, above all **R8: real z-level elevation is dead — no
raised ground, hills, height line of sight, or cells above cells.** Every place this design comes near R8 says so.

---

## Summary (one page)

- **We already have a bridge; it is called a pit cover.** `Building_PitCover`
  (`src/RimMandrake/FlowWorks/Source/Pits/Building_PitCover.cs`) is a 1×1 non-edifice building over a 2 m cell that
  turns the hole into ground for everything that walks, joins its neighbours into one deck, sums the weight on the
  whole deck, and drops everyone through the pit's own descent event when the rating (40 / 120 / 220 kg) is crossed.
  Seven systems already ask "is this cell covered?" (pathing, step cost, shooting, exposure, fill effects, slime slip,
  liquid fire). **A bridge is the visible, rated, non-trap sibling of the cover**, and the cheapest correct build is to
  lift the cover's machinery into one "span" base class and teach those seven call sites one word: *decked*.
- **What a bridge is, in our model:** a deck that gives a cell a **walking height** different from its **floor**.
  Water, fire, heat, gas and flow live at the floor (they keep working unchanged underneath); pawns, items and
  buildings live on the deck. One cell, one walking height. That is the whole trick, and it is why R8 does not forbid it.
- **Over anything:** a span may be built over any cell that is lower than the deck by at least 0.5 m: a dry trench, a
  wet canal, a pit of any depth, a drawn-down lake, natural shallow water. Deep and moving natural water need a pier
  (open question Q5). Vanilla's `Bridge` / Odyssey's `HeavyBridge` stay as they are for vanilla water.
- **Grated:** a span flag. A grated deck lets fire reach the people on it, lets rain and spilled liquid fall through
  into the water below, and shows the liquid beneath. Heat, gas and light already "rise through" everything, because
  RimWorld keeps them per cell and per room, never per height (§4.2: an engine fact, not a choice).
- **At non-surface altitudes:** a **sunken deck** is a span whose walking height is below ground, for example at the
  4 m ledge of the 4/7/7/4 square, crossing the 7 m core. This fits one walking height per cell, so it is buildable.
  What is **not** buildable without breaking R8: anyone walking *under* a deck. Q2 asks him whether he wants that one
  exception.
- **Build cost (ESTIMATE): about 10 to 15 agent-days in six stages,** plus his art look, after the rebuild's water
  (P3/P4/P14) and depth (P5/P7) packages land. Stage S0 (the cover refactor) can start any time.
- **Recommendation for the biggest decision (Q1): the deck is a building, not a floor terrain.** A building burns,
  breaks, carries the four styles and lets floodwater through; a floor terrain does none of these. The one thing a
  building cannot do by itself (let others build on it) is a small patch.

---

## 1. What already exists (searched first)

| thing | where | what it gives a bridge |
|---|---|---|
| **Pit covers** (3 tiers) | `Source/Pits/Building_PitCover.cs`, `Source/Pits/Trigger/{CompPitCoverTrigger,PitCoverTier}.cs`, `Defs/Pits/ThingDefs/RM_PitCovers.xml` | the whole deck model: non-edifice building (`isEdifice false`, `Standable`, `pathCost 1`, `altitudeLayer FloorEmplacement`); `RM_PitCoverUtility.Deck()` 4-way flood of connected covers, no size cap (`COVER_DECK_TUNE_QUADRATIC_CENSUS`); mass trigger per deck every 30 ticks; collapse drops pawns through the descent event; `TerrainMimicPrinter` hides the hole |
| "a covered cell is ground" | `Superdeep/RM_PitStepCost.cs:56-78`, `RM_Patch_SuperdeepShooting.cs:93-95`, `RM_PitExposure.cs:33`, `RM_PitFillEffects.cs:58-60`, `RM_SlimeSlip.cs:43`, `RM_LiquidFire.cs:506-513, :552-559` (`RM_FireMath.AttachChance(heldInPit, onCover, flying)`) | the seven call sites a span must also answer |
| blasts break covers | `RimMandrakeFlowWorksMod.cs:197-198` `blastsBreakPitCovers` (owner 2026-10-06, Q5/Q9) | the damage rule, already ruled for covers |
| covers' settings | `trapTriggerEnabled`, `trapSensitivityMultiplier`, `superdeepCapturesOwnFaction` (`RimMandrakeFlowWorksMod.cs:667, :1136`) | the shape of span settings |
| ramps and ladders | `Superdeep/RM_PitRamp.cs`, `RM_LadderUtility.cs` | how pawns reach a sunken deck |
| pocket grid and cliff masks | `Superdeep/RM_PocketGrid.cs`, `RM_CliffMask.cs`, `RM_PitPathing.cs` | the per-height pathing a sunken deck plugs into |
| ford stones | `Defs/Rivers/RM_FordStones.xml` (affordance `RM_Fordable`, shallow moving water only, layered "like a bridge") | the cheap river crossing; a bridge is the expensive one |
| ferry post rope | `Defs/Rivers/RM_BankWorks.xml:151` `RM_FerryPost`, `Rivers/RM_FerryAndLevee.cs` | deep-water crossing without a bridge; pathing already routes "to bridges/fords" (`RM_RiverWorks.cs:143-146`, owner card 2026-10-03) |
| weir in four styles | `Defs/Rivers/RM_BankWeirStyles.xml` (`RM_BankWeir_{Scrapper,Industrial,Modern,Futuristic}`) | the style pattern a span copies |
| sluice and grate doors | `FLOWWORKS_DOOR_FAMILY_1` (`flowworks_pits_unified_model_2026-10-02.md:128`) | a grate that passes liquid exists as a *door*; a grated deck is its floor cousin |
| other mods' decks | `TheSump/.../RM_SumpWalkways.xml` (duckboards, Light-affordance floors), `FeverWood/.../RUT_StiltPlatform.xml` (`ParentName="Bridge"`), `FeverWood/.../RUT_Boughway.xml` | biome walkways, terrain-based; not FlowWorks' business, but they show a `Bridge` child works in our defs |
| the "bridge silently destroyed" trap | `EnvironmentalHazards/Source/RM_GradientAxisRepaint.cs:10-45` | MEASURED against the 1.6 decompile: `TerrainGrid.SetTerrain` with a non-layerable terrain **overwrites the top layer and clears the under layer**, so a blind repaint deletes a player's bridge. Any FlowWorks writer that repaints water under a vanilla bridge must write the under layer |
| floods stop at foundations | `Rivers/RM_FerryAndLevee.cs:132-135` | vanilla `Flood.CanFloodSpreadInto` refuses a cell with a foundation or an edifice. A floor-terrain bridge is a levee; a non-edifice building is not |

**Nothing found** for: a bridge over dry ground or a dug cell, a grated deck, a deck below ground, or a span length rule.

### 1.1 Vanilla and Odyssey bridges (read from disk)

| def | file | facts |
|---|---|---|
| `BridgeBase` (abstract) | `Core/Defs/TerrainDefs/Terrain_Foundation.xml` | `layerable`, `bridge`, `isFoundation` true; `terrainAffordanceNeeded Bridgeable`; `destroyBuildingsOnDestroyed` true; `destroyEffect Bridge_Collapse` / `Bridge_CollapseWater`; `autoRebuildable`; `preventCraters` |
| `Bridge` | same | affordance `Light` only; 12 wood; WorkToBuild 1500; Flammability 0.8; `destroyOnBombDamageThreshold 35` |
| `HeavyBridge` | `Odyssey/Defs/TerrainDefs/Terrain_Foundation.xml` | affordances `Light, Medium, Heavy, Walkable`; 14 steel; WorkToBuild 2500; research `HeavyBridges` (800, Industrial) |
| `AncientHeavyBridge` | same | map-generated, not buildable |
| `Bridgeable` affordance | `Core/Defs/Misc/TerrainAffordanceDefs/TerrainAffordances.xml:49` | carried by shallow and chest-deep water; **not** by `WaterDeep` (no affordances at all; `flowworks_natural_water_engine_2026-10-17.md:92`) |

So vanilla: a bridge is a **floor terrain**, gated by one affordance, with **no weight limit, no span limit, no hit
points** (it breaks only from a bomb over 35 damage), and it carries buildings by affordance. It cannot cross deep
water, a dry trench or a pit. Its fire behaviour: the terrain is flammable (0.8), so fire spreads over it, but a terrain
has no hit points, so fire never brings a vanilla bridge down (UNMEASURED in the decompile; RimSage is Windows-only).

---

## 2. What a bridge is in our water/elevation model

The ruled model (`flowworks_unified_depth_2026-10-17.md`): each cell has a **floor** (metres below ground, 0.5 m
notches, up to the dig cap of 8 m by default or a lake floor to 125 m), and water stands on it to a **level surface**
per connected body.

**A span adds one number per cell: the deck height `H`** (metres below ground, in 0.5 m notches; 0 = a surface
bridge). Rules:

1. **One walking height per cell.** On a decked cell, everything that walks, stands, lies, is hauled or is built is at
   `H`. Nothing can stand below the deck (R8: no cells above cells).
2. **The floor keeps its own life.** Water, flow, fill, burning liquid, spikes, the floor's terrain, its depth record
   and its body membership are at the floor `F` and are untouched by the deck. The flow kernel never reads buildings,
   so water flows under a span as if it were not there.
3. **A span needs a drop.** `F − H ≥ 0.5 m`. A deck flush on its floor is just a floor; build a floor.
4. **The water may rise to the deck.** If the body's surface rises above `H`, the deck is awash: pawns on it stand in
   `surface − H` of water (the same drowning, swimming and slime rules as any cell at that height). This is the one
   new read every pawn-in-liquid rule makes: "water depth at the walking height", not "at the floor".
5. **For the pathing and pocket systems a decked cell's depth is `H`, not `F`.** Today a cover reads as depth 0
   (`RM_PitStepCost.cs:56-65`). A span generalises that to `H`.

That is all. It does not need a second map, a second terrain layer, or any cell above any cell.

### 2.1 Building or floor? (Q1, the biggest choice)

| | **A. A building deck** (recommended; the pit cover's shape) | **B. A floor terrain** (vanilla's shape) | **C. Floor terrain + a per-cell record** |
|---|---|---|---|
| burns, takes damage, breaks | **yes, natively** (hit points, Flammability by stuff) | no hit points; only a bomb over 35 breaks it | by our own code |
| the four styles | **yes**: `ThingStyleDef` per building, the shared picker (`Machinery/PipeLook.cs`), as the weir does | no: a terrain has no style; four terrain defs per tier | four terrain defs per tier |
| others build on top | **needs a small patch**: placement reads the cell's terrain affordances; the patch adds the deck's | **yes, natively** (Light, or Light/Medium/Heavy) | yes |
| floodwater passes under | **yes** (not an edifice, not a foundation) | **no**: vanilla treats a foundation as a levee (`RM_FerryAndLevee.cs:132-135`) | no, without a patch |
| water engine can clobber it | **no**: it is not terrain | **yes**, the `SetTerrain` trap (§1); every P14 writer must write the under layer | yes |
| other mods see "a bridge" | no (a mod reading `TerrainDef.bridge` misses it) | yes | yes |
| reuses the cover's code | **all of it** | little | some |
| ESTIMATE, base deck | 2 to 3 days | 2 to 3 days, plus a damage system | 3 to 4 days |

**Recommendation: A.** It is the cover we already built, made visible and rated. The cost of A is one Harmony patch
(affordances); the costs of B are hit points, styles, floods and the terrain trap, each larger.

**Vanilla bridges stay.** `Bridge` and `HeavyBridge` remain buildable over vanilla's bridgeable water. Q6 asks what to
do when one is placed over one of **our** dug squares: after P14, a wet canal shows vanilla shallow water, which is
`Bridgeable`, so a vanilla bridge could go down there and then sit on a dry `RM_Channel_*` floor when the canal drains.
Recommended: refuse vanilla `Bridge`/`HeavyBridge` on any cell the excavation component owns, with the message "Use a
span over dug ground", and make every P14 writer use the under layer under an existing bridge (the §1 trap).

---

## 3. Spans over water vs over dry trenches, pits, canals

One building, one placement rule: the cell is at least 0.5 m below the deck and is **spannable**:

| what is under it | spannable? | notes |
|---|---|---|
| dry dug cell (trench, canal, pit, any depth) | yes | the new case vanilla cannot do; the commonest use: a moat crossing |
| wet dug cell (any liquid) | yes | the liquid stays live underneath (§7) |
| drawn-down or dry lakebed | yes | lake floors vary to 125 m (R11); span-length rules (§6) limit how far |
| natural shallow / chest-deep water, still | yes | overlaps vanilla `Bridge`; ours is rated and styled |
| natural deep water, still (lakes) | **with a pier** every N cells (Q5) | vanilla cannot; a pier is a span cell flagged "supported" whose column reaches the floor |
| moving water (rivers) | shallow: yes; deep: **with a pier** (Q5) | the current never carries anyone on a deck (same exemption as fords, `RM_MapComponent_RiverCurrent.NearFord`) |
| ocean, edge river | **open question** (Q5) | limitless water (R13): piers into the sea are a big promise |
| level ground | no | build a floor |
| another mod's chasm / lava | out of scope | named so nobody assumes it |

**Abutments.** A span cell is *supported* if a neighbour (4-way) is solid walkable ground at the deck's height (± 0.5 m),
or if it carries a pier. Everything else is held by the span's strength (§6).

**Over water vs over dry: what differs** is only what a fall lands in. A collapse over a dry 4 m trench is a 4 m fall
(V3 fall damage by metres). Over 3 m of water in a 4 m pit it is a 1 m fall into water a person can swim in (R12). Over
burning fuel, it is the fire. The descent event already resolves all three for covers.

---

## 4. Grated bridges

A grated span is the same building with `grated = true` in its extension. Steel or scrap-mesh only (it must not burn
away from the very fire it is built to pass).

### 4.1 What a grate changes (our own rules, each one at a call site that already exists)

| effect | solid deck | grated deck | call site |
|---|---|---|---|
| burning liquid below sets the people above alight | low (today's `onCover` chance: 0.4 / 0.6) | **high**: as if standing beside an inferno (proposed: the open-pit chance × 0.75) | `RM_LiquidFire.cs:506-513, :552-559`, `RM_FireMath.AttachChance` gains a grated flag |
| the deck itself catches fire | by its stuff (wood burns, then breaks, then everyone falls) | steel does not burn; it **heats**: pawns on a grate over a fire take vanilla burns over time | the burn is a vanilla `Burn` injury, never a new hediff (the one-kind-of-heat ruling, 2026-09-29/30: *"It can't be a new "kind" of heat."*) |
| rain and snow into the hole | **the deck sheds it**: no rain fill below a solid deck (a roof for the water engine's rain loop) | **passes**: rain fills as if open | rain loop (P5: "rain loop by the cell's own depth") |
| pit exposure (weather on someone in the hole) | n/a: nobody is under a deck | n/a | `RM_PitExposure.cs:33` already skips covered cells |
| liquid spilled or poured on the deck | stays on the deck (vanilla filth) | **drains into the body below** (a grate over a canal is a drain) | new, small: a spill on a grated deck over a wet or dug cell adds its litres to the cell's body |
| items on the deck | stay | stay (Q4 offers "small items fall through") | — |
| shooting | a deck is ground at `H` | same | `RM_Patch_SuperdeepShooting.cs:93-95` reads `H` |
| what you see | the deck hides the floor | **the liquid below shows through** the holes (art with real alpha; §8) | draw order: liquid (terrain) under the grate building, naturally |
| slime and fill splash | none above a deck | **splash reaches** (proposed: half the open-pit chance) | `RM_SlimeSlip.cs:43`, `RM_PitFillEffects.cs:58-60` |

### 4.2 What a grate cannot change (engine facts, not choices)

RimWorld keeps **temperature per room**, **gas per cell** (1.6 gas grid), **light per cell** (glow grid) and **roofs per
cell**, all flat. None of them has a "below the deck". So:

- **Heat, gas and light already rise through every deck, grated or solid.** A fire in a pit heats the room the deck is
  in; toxic gas from below is on the deck; a burning pit lights the bridge. A *solid* deck **cannot** trap smoke or heat
  beneath it, because there is no beneath. The grated/solid difference for these three is therefore only the
  direct-exposure rules above (fire attach, burns), which are ours.
- A deck is **not a roof** and does not make a room. It cannot shelter the people on it from rain, and it cannot turn
  the space beneath into a room (nobody can be beneath it anyway).

---

## 5. Bridges at non-surface altitudes: sunken decks, and the engine's limits

### 5.1 What we can build: the sunken deck

A sunken deck is a span with `H > 0`. Example, the 4/7/7/4 square (`flowworks_elevation_feasibility_2026-10-17.md`
§5): a ring of 4 m cells round a 7 m core. Two sunken spans at `H = 4 m` across the core connect the west and east
ring cells; pawns walk the ring and the bridge at 4 m; the core floor is 3 m below the deck; water in the core stands
under it and can rise to it.

- **Abutments at height.** A sunken span's supports are neighbours whose floor is at `H` (± 0.5 m): ledges, ramps
  (`RM_PitRamp`), or ladders' landings. It is reached the way that ledge is reached. No new climbing rule.
- **Pathing.** The pocket grid and cliff masks (`RM_PocketGrid.cs`, `RM_CliffMask.cs`) already give each person-band its
  own passability. A decked cell enters them at depth `H`. This rides on the per-request mask swap that P2
  (`PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH`) must prove under 1.6's multithreaded pathfinding; **sunken decks wait for
  P2**.
- **Drawing.** A pawn on a sunken deck sinks by the drop below the nearest lip, as on any floor at `H` (P5's sink rule).
  The deck is drawn at the pit's floor-emplacement layer with a ledge shadow so it reads as "down in the hole", not "on
  the surface". UNMEASURED: whether the lip-occlusion pass (`RM_PitLipOcclusion.cs`) cuts a sunken deck correctly.
- **Built how.** The builder stands on an abutment at `H`. A span is built outward from support, one cell at a time,
  never from a cell it has not reached (no floating starts).

### 5.2 What we cannot build without breaking R8

| wanted | why not | what it would take |
|---|---|---|
| **walking under a deck** (a pawn on the pit floor passes beneath a surface bridge) | two walking heights in one cell = cells above cells (R8). Pawns draw at one altitude, so the one below would be drawn on top of the deck; targeting, hauling, fire, items and the room system all assume one height | per-request masks could fake the pathing; drawing, targeting and items cannot be faked cheaply. **Weeks; reopens R8.** Q2 asks him |
| **a deck over a deck** (two bridges at different heights over one cell) | the same | the same |
| **a bridge above ground level** (an overpass over a road) | raised ground is dead (R8, and LAW 1 *"we dig down, we never build up"*, `RM_ExcavationDepth.cs:12`) | dig the road down instead: a sunken road under a surface span **is** cells above cells; a surface span over a sunken road with no traffic under it is buildable |
| **seeing the floor beneath a solid deck** | no camera tilt | a grate shows the liquid; the readout says the floor depth |
| **shooting under or through a deck by height** | no projectile height (R8, height line of sight dead) | V5's shot-line rule reads walking heights only |

**So the consequence a player meets:** a surface bridge over a moat is a **wall** for anyone down in the moat (the
decked cell's walking height is the surface; from the floor it is a sheer climb). A prisoner pit with a bridge over its
middle becomes two pits. That is honest and playable, and the readout and the pit-room code must say it.

---

## 6. Building, load and collapse rules

### 6.1 Tiers (proposed; numbers are starting points for the playtest, not measurements)

| tier | look | built from | load per span (kg) | longest unsupported run (cells) | grated? | lends affordance |
|---|---|---|---|---|---|---|
| **Rope walk** | planks on rope | wood, cloth | 150 | 6 | no | none (walking only) |
| **Timber span** | beams and boards | wood (stuffable: wood) | 600 | 4 | no | Light |
| **Steel span** | girders and plate | steel (stuffable: metallic) | 2,000 | 8 | **yes** (grated variant) | Light, Medium |
| **Heavy span** | box girder | steel, components; research `HeavyBridges` | 8,000 | 12 | yes (grated variant) | Light, Medium, Heavy |
| **Pier** | a column to the floor | stone blocks or steel | — | resets the run | — | — |

The pit covers stay as the **trap** tier (40 / 120 / 220 kg, hidden, superdeep only per the 2026-10-16 card), in the
same family.

### 6.2 Load

- **A span** = the decked cells connected to each other and lying between supports. Load is checked per span, not per
  deck (a long bridge with piers is several spans). The cover's whole-deck sum (`RM_PitCoverUtility.Deck`) becomes
  "the cells between supports".
- **Mass counted:** pawns (vanilla mass), items on it, and buildings on it (their mass by cost list, cached on build).
- **Over the rating:** the inspect pane shows "Load 640 / 600 kg" and a warning for a slow rise; a span over its rating
  **gives way** (Q3 asks whether player bridges should break from weight at all, or only from damage).
- **Settings:** a load multiplier (0.25 to 4) and an on/off for weight collapse.

### 6.3 Collapse

A span cell collapses when (a) its hit points reach 0 (fire, blasts: `blastsBreakPitCovers` generalised), (b) its span
is over load, or (c) it loses every support (an abutment dug out, a pier destroyed): the cells beyond the nearest
remaining support go, as a chain, one tick per cell so the player sees it run.

On collapse, per cell: pawns **descend** through the existing descent event (fall damage by metres fallen, V3; water
and fire as §3); items drop to the floor (they are then in the hole); buildings on the deck are destroyed and leave
their deconstruct share as minified-free rubble (vanilla bridge behaviour, `destroyBuildingsOnDestroyed`). Vanilla's
`Bridge_Collapse` / `Bridge_CollapseWater` effects play by what is below. A letter names the span and who fell.

### 6.4 Building rules

- Placement: the cell is spannable (§3), has no edifice, and is supported or next to a cell already decked or designated
  in the same order (so a whole bridge can be laid out in one drag, built from the ends inward).
- Work: from an adjacent supported cell. The run limit is checked at placement; the build order shows the run length
  ("4 / 4 cells unsupported").
- Digging under an existing deck is refused ("remove the span first"); filling in under a deck is refused. Nobody can
  stand there to do it (§5.2).
- Deconstructing a span with pawns or buildings on it is refused until it is clear.

---

## 7. Interactions with flow, flooding, canals, pits/superdeep

| system | interaction | change needed |
|---|---|---|
| **Flow kernel, level surface (P3)** | none: the kernel reads the depth grid and bodies, not buildings | none |
| **Water on the base layer (P14)** | our span is not terrain, so no clash. A **vanilla** bridge over water whose band changes is the `SetTerrain` trap (§1) | P14 writers check for a bridge and write the under layer; noted on `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` when that is built |
| **Water rising to the deck** | rule 4 of §2: an awash deck is a cell at `H` with water on it | every "water depth for this pawn" read uses the walking height; P7/P12 own the rules |
| **Moving water and floods (`Flood_FlowWorks`, vanilla `SeasonalFlood`)** | a non-edifice span lets floodwater through. A flood running **over** a deck: rope walks and timber spans take damage per hour awash in moving water (proposed 5% of hit points); steel and heavy do not | small: one damage tick in the flood pass |
| **River current** | nobody on a deck is carried | reuse the fords' exemption |
| **Canals** | span after digging; a dug canal under a span keeps flowing; sluices and grate doors stay where they are (doors are edifices; a span cell cannot hold one) | dig and fill-in designators refuse decked cells |
| **Pits / superdeep (`PIT_SUPERDEEP_COLLAPSE_1`)** | a decked cell is ground at `H` for capture, climb, shooting and exposure, as covers are today. A pit room is the pocket below; a deck **splits** a pit room's floor (§5.2). The ladder prison-door rule is unchanged | the seven call sites read "decked at `H`" instead of "covered" |
| **Spikes** | spikes are at the floor; a fall through a collapsed span lands on them | none (descent already resolves spikes) |
| **Drowning, swimming (R12)** | a fall into 2 m+ water is a swim, not a drowning | none beyond P12 |
| **Burning liquid (`RM_LiquidFire`)** | §4.1; a wooden span over burning fuel catches, burns and drops its people into the fire | `AttachChance` gains the grated flag; the deck's own flammability is vanilla |
| **Raiders (Q7 of the rebuild, unasked)** | a span over a sheer moat is a path in. Raid AI will use it; sappers and breachers may target it. A span the player deconstructs or burns is the drawbridge the moat design was missing | none; worth saying to him alongside the raider card |
| **Pit covers** | the trap tier of the same family; a cover is still hidden and superdeep-only | refactor, no behaviour change (stage S0) |
| **Readout (P8)** | "Span (steel, grated) · deck at surface · load 210 / 2,000 kg · below: Hole 4 m, Water 2.4 m (4,800 L)" | one line added to the P8 form |

---

## 8. Art needs (the four styles)

The four styles are **Scrapper, Industrial, Modern, Futuristic** (`liquid_containers_four_styles_2026-10-16.md`),
carried as one `ThingStyleDef` per building per style, picked by `Machinery/PipeLook.cs`, as `RM_BankWeir_*` does.

| asset | per style | count | notes |
|---|---|---|---|
| solid deck tile | 1 | 4 | linked graphic so neighbouring cells read as one deck (`Graphic_Linked` family; UNMEASURED which linker suits a 1×1 non-edifice) |
| grated deck tile | 1 | 4 | **real alpha holes** so the liquid terrain shows through; Scrapper = mesh, Futuristic = light grid |
| railing / edge pieces | 1 set | 4 | drawn on the deck's open edges; the visible difference between a span and a hidden cover |
| pier cap | 1 | 4 | seen from above only |
| sunken-deck ledge shadow | 1 shared overlay | 1 | so a deck at 4 m reads as down in the hole |
| collapse debris (filth or skip) | 1 | 4 | what is left in the hole |
| rope walk | Scrapper only, by nature | 1 | the rope tier has one look |

**About 26 textures.** Stuff colours the solid tiles (wood vs steel) as the stuffable buildings do. Every one is shown
to him at true scale beside a vanilla human before it ships (cosmetic permission; `rimworld-review-sheets` skill), the
grated tiles **over live liquid**, because that is the whole point of them. Check `artpipe_state.py find` for existing
deck, grate or catwalk art before generating any.

---

## 9. Mod Settings

All under a new **"Bridges and spans"** section of FlowWorks' settings, defaults = shipped behaviour, all off degrades
cleanly (existing spans become plain walkable decks that never break from weight; nothing is deleted from a save).

| setting | default | range | off means |
|---|---|---|---|
| Spans can be built | on | — | no build buttons; existing spans stay |
| Spans give way under weight | on | — | they break only from damage and lost supports |
| Span load multiplier | 1 | 0.25 to 4 | — |
| Unsupported run multiplier | 1 | 0.5 to 3 | — |
| Spans fall when their supports go | on | — | a span with no support stays up |
| Grates pass fire to people above | on | — | grated decks shield like solid ones |
| Grates drain spills into the water below | on | — | spills stay on the deck |
| Solid decks keep rain out of the hole below | on | — | rain falls through every deck |
| Sunken decks (below ground) | on | — | spans only at the surface |
| Floods damage light spans | on | — | — |
| Vanilla bridges refused over dug ground | on | — | allowed (with the terrain risks of §2.1) |
| Your own people fall when a span gives way | on | — | own faction is held (mirrors `superdeepCapturesOwnFaction`) |

---

## 10. Staged build plan (ESTIMATES, agent-days, no live time unless said)

| stage | item name (proposed) | what | ESTIMATE | depends on | needs live |
|---|---|---|---|---|---|
| **S0** | `SPAN_BASE_REWIRE_COVERS_STEP_OUT` | lift `Building_PitCover` into a span base class; one `RM_SpanUtility.DeckedAt(map, c, out H)` replaces `IsCovered` at the seven call sites; covers become the trap tier; no behaviour change; selftests prove it | 1 to 1.5 | nothing (can start now) | none |
| **S1** | `SPAN_BUILD_SURFACE_DECKS_OVER_ANY_HOLE` | surface spans over dug and natural-shallow cells: placement, supports, run limits, load per span, collapse chain, descent, affordance-lending patch, dig/fill refusal, readout line, settings | 3 to 4 | P3/P4/P14 (water semantics), S0 | 0.5 (minimal list: build, overload, burn, collapse into water) |
| **S2** | `SPAN_BUILD_GRATES_LET_THE_FIRE_UP` | grated variant: fire attach, burns, spill drain, rain pass, splash; selftests on `RM_FireMath` | 1.5 to 2 | S1 | 0.5 (a grate over burning fuel) |
| **S3** | `SPAN_BUILD_PIERS_INTO_DEEP_WATER` | piers, deep and moving water, flood damage, current exemption; vanilla-bridge refusal and the P14 under-layer guard | 1.5 to 2.5 | S1; Q5, Q6 | 0.5 (a river crossing in flood) |
| **S4** | `SPAN_BUILD_SUNKEN_DECKS_IN_THE_HOLE` | `H > 0`: abutments at height, pocket/mask integration, sink and ledge shadow, readout | 2 to 3 | P2 proved, P5, P7; S1 | 1 (the 4/7/7/4 square with a sunken crossing; raiders vs. moat with and without a span) |
| **S5** | `SPAN_RESKIN_FOUR_STYLES_HE_SEES_FIRST` | the ~26 textures; review sheet at true scale; grates over live liquid in game | 1 to 2 + his look | S1 (any time for the sheet) | his look |
| **S6** | (inside each stage) | validation script rows (`design/RimMandrake/debug_process.md`): build, load, collapse-into-water, collapse-into-fire, grate-fire, flood-over-deck, sunken-crossing; proposed north-star bars for him to validate | included above | — | — |

**Total ESTIMATE: about 10 to 15 agent-days plus about 3 days live, plus his art look.** Not yet filed as items: the
names above are proposals; filing waits on his answers to Q1 and Q2 (they change S1 and S4).

**Proposed north-star bars (his to validate; hash-bound section):** *span_holds_and_breaks_legibly* (a loaded span's
load is readable before it breaks; a break shows who fell and where); *grate_shows_what_is_below* (the liquid under a
grate is visible at play zoom); *sunken_deck_reads_as_down* (a deck at 4 m reads as inside the hole, not on the
surface).

---

## 11. Open questions for the owner (plain language; options and trade-offs)

**Q1. Is a bridge a building or a floor?**
- **(a) A building (recommended).** It can burn and break, comes in the four styles, and floodwater flows under it. Other
  mods that look for "a bridge" will not see it.
- (b) A floor, like the game's own bridge. Other mods see it, but it has no hit points (fire cannot drop it), no style
  picker, and the game treats it as a dam for floods.

**Q2. Can anyone walk *under* a bridge?** (You ruled out "cells above cells" this morning.)
- **(a) No (recommended).** A bridge over a moat is a wall to anyone down in the moat; a bridge over a prisoner pit
  splits it in two. Cheap and honest.
- (b) Yes, when the deck is at least 2.5 m above the floor: a real underpass. Weeks of work, risky, and it undoes part of
  this morning's ruling.

**Q3. Should your own bridges collapse from weight?**
- **(a) Yes, with the load shown on the bridge (recommended).** Rope walks and timber spans have a limit you can read
  before you cross it.
- (b) No; bridges break only from fire, explosions and losing their supports. Simpler, less drama.
- (c) Yes, but only for enemies and animals, like the pit covers' "own people are spared" setting.

**Q4. What falls through a grate?**
- **(a) Spilled liquid only (recommended).** A grate over a canal works as a drain; dropped items stay put.
- (b) Spilled liquid and small items (a few kilos and under). More realistic; haulers will lose things into canals.
- (c) Nothing. Simplest.

**Q5. Bridges over deep water, rivers and the sea?**
- **(a) Deep lakes and rivers need a pier every few cells; never the sea (recommended).**
- (b) Anywhere, piers included, the sea too. Big crossings, but a bridge to nowhere over limitless water.
- (c) Only where the game's own bridge can go, plus dug ground. Smallest.

**Q6. The game's own bridge over a dug canal?**
- **(a) Refuse it there and point to our span (recommended).** Avoids a vanilla bridge left standing on a drained ditch.
- (b) Allow it. Works, but it never breaks, and it dams floods.

**Q7. How do you reach a sunken bridge?**
- **(a) From a ledge at its own height, or a ramp or ladder to it (recommended).** It works like any other floor at that
  depth.
- (b) Also by a ladder down from the surface at either end, built into the bridge. Handier, more art.

**Q8. Do the trap covers join the bridge family's look?**
- **(a) No (recommended).** A cover must stay hidden; a bridge must be seen. Same code, different pictures.
- (b) Yes, a "cover" becomes a bridge without railings. Easier to spot, worse trap.

**Q9. Does a solid bridge keep the rain out of the hole beneath it?**
- **(a) Yes (recommended).** A deck sheds rain; a grate lets it through. This is the only thing a solid deck can
  actually shelter, because heat, smoke and light rise through everything in this game.
- (b) No; rain fills the hole regardless.
