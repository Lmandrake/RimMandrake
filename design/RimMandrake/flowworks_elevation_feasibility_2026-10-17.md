# Free per-cell elevation: engine feasibility and cost (helper A, double review, 2026-10-17)

Item: `WATER_SURFACE_REPAIR_LEVEL_OR_BUST` (the owner's 2026-10-17 card answer ordered this review). **ANALYSIS, not
ruled.** Lens: engine feasibility and cost. A second Opus helper reviews the same question from another lens; the owner
rules after both. Nothing in code, defs, the bridge or the game was touched. Code claims are file:line from a read-only
census of `src/RimMandrake/FlowWorks/Source` at `664f8dd1a`. One independent outside read (GPT via `gpt_consult.py`) is
kept verbatim beside this file as `flowworks_elevation_feasibility_2026-10-17.gpt_read.md`. It is evidence, not
authority, and §7 says where it agrees and where it does not. **Every agent-day figure is an ESTIMATE**, not a
measurement. An agent-day is one focused coding agent day including selftests, with no live game time.

**RULED 2026-10-17 (by card, after this review):** Q1 (a) dig 8 m by default, a setting from 2 to 20 m; T1 and the
relative rules are built in one rebuild together with level water (so Q3's order is replaced); the four 2 m-keyed rules
become relative; **T4 is dead** (Q4 a). Q2 (dig cost) was not asked: the plan defaults to keeping the curve, veto-able.
Build plan: `design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`.

The owner, 2026-10-17 (ledger note on `WATER_SURFACE_REPAIR_LEVEL_OR_BUST`): *"how should we determine the right number
of quantized levels to support? The same goes for max pit depth. I'm starting to think we shouldn't limit the player to
just four levels of canal. Please evaluate how much more effort would be required to allow them to make say a square of
4 4 4 4 / 4 7 7 4 / 4 7 7 4 / 4 4 4 4 (arranged as a square, numbers are metres depth) if they wish. How much harder is
that? Then we would have rules like 'ladders/ramps are required to go down delta elevation, not just enter a pit of some
depth in an absolute sense.' This would allow drained lakes to really look like large stretches of depressed terrain.
... evaluate this full design space in terms of feasibility in the game engine, dev time required, and the fascinating
play experience... I realize we don't want to make a whole new z-level engine here, so where are the natural breaks in
complexity we could decide on now? Given our two primary use-cases are water storage/movement and prisoner containment.
Also plants growing on those squares if left for a while."*

---

## Summary (one page)

**The headline: most of what he describes is already built.** The "delta" rule he proposes is the relative climb
design he ruled on 2026-10-12 (`design/RimMandrake/relative_depth_climb_design_2026-10-12.md` §8, §10). It is built
offline: per-creature climb limits, a pocket grid, per-band pathfinder masks, a ramp that spans up to 1.5 m and a
ladder that spans any depth (`PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` doing; `PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS`,
`PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS` done; **live proofs still owed for all three**). Drained lakes already leave real
depressions to any recorded depth (`POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE`, `POND_ELEVATION_BUILD_LAKES_RUN_DEEP` done;
live proof owed). The depth grid is already a per-cell **height map** stored in bytes, so it can hold 0 to 127.5 m today.

**So the 4/7/7/4 square is not a z-level engine. It is mostly one constant (the 2 m dig cap) and the places that copied
it.** About a dozen code sites assume "nothing dug is deeper than 2 m" (§1.3). Fixing them is **Tier 1: about 3 to 5
agent-days, no save migration.** With Tier 1 and what is built, his square works: it holds water as one level body,
it traps prisoners by the relative rule, and pawns go in and out by ladder.

**The natural breaks (§4):**

| tier | what the player gets | cost (ESTIMATE) | save impact |
|---|---|---|---|
| **T0** today | dig to 2 m; lakes to 10 m (20 m ruled, not built); relative climb, ramps, ladders, dry-lake hollows built offline | 0 (live proofs owed) | — |
| **T1** deeper digs, same engine | dig to a set depth (recommend 8 m default, setting 2 to 20 m); the 4/7/7/4 square; deeper walls and pawn sink | **3 to 5 days** of new code, **4 to 8 with the owed climb live proofs** (GPT: 5 to 9, §7) | none: the byte grids already hold it |
| **T2** relative everywhere | the rules that still say "a pit is 2 m deep, absolute" become "a drop relative to the neighbours": prison rooms, the shooting rule, exposure, spikes | **3 to 6 days** + owner rulings (ruling 23 is his words) | none |
| **T3** land that heals | dug floors and dry lakebeds regain fertility over time; wild plants and crops grow there; returning water kills them | **2 to 4 days** + an owner look at any new art | one new byte grid; old saves start un-grown |
| **T4** real elevation | raised ground, hills, line of sight and projectiles by height, cells above cells | **DEAD** (owner, by card, 2026-10-17) | — |

T4 is dead, not deferred: it contradicts LAW 1 ("we dig down, we never build up", `RM_ExcavationDepth.cs:12`).

**How many levels, and how deep (§3).** Keep the 0.5 m dig step. Water is now continuous (exactly level, ruled
2026-10-17), so the step no longer limits water at all; it is only the size of one dig and of one climb. Containment
stops improving at about **3.5 m relative** (the tallest climber in the built table climbs 3 m). Water storage keeps
improving with depth but the work to dig grows with the **square** of depth under today's work curve, so a 7 m cell
costs 10.5 times a 2 m cell. The eye can tell about **four** hole-floor bands, whatever the dig cap; the walls show
each drop and the readout gives exact metres. **Recommendation: max dig 8 m by default, settable 2 to 20 m;** four
floor looks by absolute depth; wall height by relative drop (saturating near 4 m); water looks as ruled.

**Biggest risks.** (1) The live proofs for the relative climb, masks and ramps have never run; T1 multiplies the
depths they see, and 1.6's multithreaded pathfinding makes the per-request mask swap the riskiest seam (GPT, §7). Run
them first. (2) Raider pathing: sheer cliffs that no hostile can cross may stall raids that
vanilla expects to path (a pre-existing risk of the 2 m moat that deeper digs make easier to build). (3) The dig work
curve makes deep digs very slow (45 pawn-days for his square, §5); it needs a tuning decision.

---

## 1. How depth and elevation are stored today (MEASURED, read-only census)

### 1.1 The grids

| grid | type | range | unit | saved as | where |
|---|---|---|---|---|---|
| `depthGrid` (D, dug depth) | `byte[]` per cell | 0..4 in use; byte holds 255 | notch (0.5 m) | `RM_excavationDepthGrid`, `DataExposeUtility.LookByteArray` (deflated base64) | `RM_MapComponent_Excavation.cs:49`, scribe `:688` |
| `fillGrid` (F, water in a dug cell) | `byte[]` | 0..D | notch | `RM_excavationFillGrid` | `:52`, `:689` |
| `fluidGrid` | `byte[]` | palette index | — | `RM_excavationFluidGrid` | `:64`, `:690` |
| `bedRecord` (a lake square's floor) | `byte[]` | 0..250 (`RM_BedMath.MaxStorableDepth`) | notch | `RM_bedDepthRecord` | `:130`, `:691`; clamp `:412` |
| `bedGrid` (a dry pond square's floor) | `byte[]` | 2 or 4 today | notch | derived, not saved | `:121` |
| pond water | `float stock` per body | — | notch × fill-unit | `RM_liquidStock` | `RM_LiquidBody.cs:109-113` |

**The climb depth is already one accessor over all of them:** `HollowDepthAt` / `ClimbDepthAt`
(`RM_MapComponent_Excavation.cs:286-306`) = dug depth, else a dry bed's depth. The pocket grid, cliff masks, wall faces,
lip occlusion, pawn sink and step cost all read it. **That accessor is the height map.** Undug ground is height 0
everywhere; there is no natural relief and none is needed (relative-climb design §4, row D).

**The constants.** `RM_ExcavationDepth.Superdeep = 4`, `MaxDepth = Superdeep` (`RM_ExcavationDepth.cs:38-40`);
`RM_Volume.LevelsPerSquare = 4` (the yardstick, `RM_Volume.cs:20`), `MetresPerLevel = 0.5f` (`:29`),
`LitresPerLevel = 1000` (`:26`); `RM_BedMath.DefaultMaxBedDepth = 20` notches (`RM_BedMath.cs:35`), setting clamp
4..40 (`RimMandrakeFlowWorksMod.cs:422`).

### 1.2 What a save carries

Five byte grids of one byte per cell (62,500 cells on 250×250, deflated; mostly zero, so small). **Raising the dig cap
needs no save change:** every grid already stores 0..255, and no save today holds D above 4. **Downgrade is not
supported:** a save with D above 4 opened by today's build would be read, but its digging, drawing and flow would
misbehave (the sites in §1.3).

### 1.3 Every site that assumes the 2 m cap or reads depth the old way

| site | what it assumes | T1 change |
|---|---|---|
| `RM_ExcavationDepth.cs:38-40` `Superdeep = 4`, `MaxDepth = Superdeep` | the trap depth and the dig cap are one number | split: `PitDepth` (4, the absolute "pit" for T0 rules) and `MaxDigDepth` (a setting) |
| `RM_FlowKernel.cs:130` `Superdeep = 4`; `:686`, `:719` loops `b < 5`; `:1224`, `:1236` keys `fill − depth + Superdeep`, `(Superdeep − depth)` | depth 0..4; a deeper cell makes the sort key **negative** | replaced by the level-surface solver (`WATER_SURFACE_REPAIR_LEVEL_OR_BUST` Option 1, ruled "exactly level"); else derive from the deepest floor |
| `RM_PitDrawMath.cs:28` `MaxDepth = 4`; `SinkFor` = `min(D, 4) × 0.3` cells | pawns sink by **absolute** depth, capped at 2 m | sink by the drop below the near lip (relative), capped; the lip clamp already exists (`ClampSinkToLip`) |
| `Superdeep/RM_PitDepthDraw.cs:100` lip search `k ≤ MaxDepth × 2` | lip within 8 cells south | fine for most shapes; bound by cap, not depth |
| `RM_PitTrapMath.cs:20` `Superdeep = 4`; `IsPitDescent :103`, `StepBlocked :109`, `DryStepBaseCost :530`, `FallDropScale(maxDepth = Superdeep) :503` | absolute D 4 (the fallback rule when relative climb is off) | keep for the OFF branch; fall damage scales by drop ÷ the dig cap or a fixed 2 m (tuning) |
| `Superdeep/RM_PocketGrid.cs:57` `MaxDepth => RM_ExcavationDepth.MaxDepth`; `:129` `new Labels[MaxDepth]` | bands K = 1..MaxDepth−1, and "**K ≥ MaxDepth climbs every step there is**" | band count from the largest climb limit (4 + climber + leaper = 6), not the dig cap. With an 8 m cap the shortcut is false: a thrumbo (K 4) is held by a 3 m sheer wall |
| `Superdeep/RM_CliffMask.cs:72` `band = new NativeArray[MaxDepth]` | same | same; 1 byte per cell per band (62.5 kB per band on 250²) |
| `RM_PocketGridMath.cs:223` band lookup | `1..maxDepth−1` | same |
| `WorkGiver_DigCanal.cs:52, :55`; `Designator_DigCanal.cs:79, :82`; `JobDriver_DigCanal.cs:30` | **read the current depth from the TERRAIN def** (`DepthOfDryTerrain`: four channel terrains, one per notch) | read the grid. Beyond 2 m every cell is `RM_Channel_Superdeep` terrain, so today's code would read 4 for a 7 m cell, refuse to dig past it and price the work wrong. **The one real bug class T1 must fix** |
| `RM_ExcavationDepth.WorkToDeepen` (`:51-63`) | work = 3200 × the notch being cut: quadratic in total depth | tuning decision (§3.2, §5) |
| `RM_ExcavationDepth.DryTerrainFor` (`:76-90`) | four looks; deeper reads as SUPERDEEP's terrain (already, for lake beds) | keep the four terrains as **bands**; depth lives in the grid; a floor tint carries "deeper still" (art gate) |
| `RM_WallFaceMath.cs:25, :28, :46` face heights by drop 1..4, clamped (`:54, :70, :76`) | a 4 m and a 2 m cliff draw the same face | extend the arrays to about 8 notches with a saturating height (art gate: he looks first) |
| `RM_MapComponent_Excavation.cs:2200` rain loop `levels < MaxDepth` | rain fills at most 4 notches | read the cell's own depth |
| `Superdeep/RM_Spikes.cs:50` `depth >= 4`; `FluidDef.cs:145` `depth >= Superdeep` picks the deepest fill look | absolute pit | spikes: T2 decision; fill look: per the ruled water bands (by water depth, not hole depth) |
| `RM_ExcavationDepth.FillTier` (`:113-125`) | fill as a fraction of D | already ruled away (pictures by metres of water, `flowworks_unified_depth_2026-10-17.md` §4); depth-agnostic once rewired |
| `RimMandrakeFlowWorksMod.cs` settings text, `Languages/.../FlowWorks_Keys.xml`, designator text "shallow, mid, deep, then SUPERDEEP" (`Designator_DigCanal.cs:19`, `:84`) | four named depths | metres |
| Absolute "pit" readers via `IsSuperdeepExcavation` / `IsSuperdeepRaw` (`RM_MapComponent_Excavation.cs:241-257`): `RM_Patch_SuperdeepShooting.cs` (ruling 23), `RM_PitExposure.cs:33, :240`, `RM_LiquidFire.cs:505, :551, :842`, `RM_PitFillEffects.cs:69`, `Superdeep/RM_PitRooms.cs:65-67` (room = D ≥ 4 **and** person pocket), `Superdeep/RM_SuperdeepTrap.cs` (62 mentions, mostly the OFF-branch absolute rule), `Superdeep/RM_PitPathing.cs` (24) | "a pit is 2 m deep, absolute" | **T1: unchanged** (any cell ≥ 2 m stays "a pit"). **T2:** relative |
| Python: `northstar/selftest_flowworks_kernel_oracle.py`, `northstar/pond_pump.py`, `northstar/liquid_checks.py` | constants as literals (unified-depth spec §7.2) | read from C#, as that spec already orders |

## 2. What "free per-cell elevation to N metres" needs, system by system

| system | need | verdict |
|---|---|---|
| **data type and range** | a floor height per cell | **have it**: `byte` notches = 0..127.5 m at 0.5 m. A 0.25 m step would halve that to 63.75 m; a `ushort` grid (125 kB raw on 250²) only if a finer step is ever wanted. Not needed (§3.1) |
| **save migration** | none for a deeper cap | **none.** Grids unchanged. A new marker only if T3's regrowth grid is added (absent = 0) |
| **pathfinder, pawn sink, climbing between cells** | a step rule by delta | **built** (cliff masks per band, per-request swap, pocket grid, reachability AND). T1 only resizes the bands. Cost at 250² with 6 bands: ~375 kB of masks plus ~1.5 MB of labels; a full relabel is 6 union-find passes over 62,500 cells, at most once per 60 ticks and only when a depth changed. At 400² it is ~2.6×. Cheap |
| **ladder and ramp rules by delta** | "ramps and ladders go down a delta, not into an absolute depth" | **built** exactly so: a ramp joins its cell to the faced neighbour 1..3 notches shallower (`pitRampMaxSpan`), any pawn, flat walking; a ladder joins any shallower neighbour, slowly, with prison-door permissions. **Consequence:** a ramp needs one cell of run per 1.5 m of drop and a cell at every intermediate depth. A 7 m descent needs 5 ramp cells |
| **collapse / pit logic** | what "a pit" is | **T0/T1:** a pit is D ≥ 2 m (absolute) for rooms, spikes, shooting, exposure; trapped-ness is already relative. **T2:** all relative |
| **rendering** | floor, walls, pawn, water | walls are **already relative** (`RM_WallFaceMath.ExposedDrop` = my depth − neighbour's), clamped at a 2 m drop; floors are 4 terrain looks + 3 lakebed looks; pawn sink is absolute and capped at 2 m. T1: extend wall arrays, make sink relative, add a floor tint by depth band (no terrain def per depth, no shader). Water looks are by water depth (ruled) |
| **mapgen, drained lakes** | lakes leave depressions | **built**: `bedRecord` per lake square (slope 0.5 m per 4 squares past 3 from shore, cap 10 m today; 20 m ruled in `LAKE_FLOOR_TUNE_TEN_TO_FIFTY_METRES`), `bedGrid`, `RM_Lakebed_Shallow/Deep/Abyss`, climb and walls read it. A drained lake is already "a large stretch of depressed terrain"; it slopes, so it never traps. No mapgen work: the one world is hand-made and frozen |
| **plants, fertility, terrain growth** | dug and dry-bed cells grow plants after a while | **not built.** Every `RM_Channel_*` and `RM_Lakebed_*` terrain has fertility 0 (MEASURED from `Defs/Canals/TerrainDefs/FlowWorks_Terrain.xml`). Vanilla reads fertility in one place, `FertilityGrid.CalculateFertilityAt` (private; edifice, else `terrain.fertility`, Biotech pollution cap; RimSage). A postfix that returns a per-cell recovered fertility is one array read. When water returns, vanilla's `TerrainGrid.DoTerrainChangedEffects` destroys any plant whose cell fertility falls below its `fertilityMin`, unless the new terrain `IsFlood` and the plant is not `destroyedByFlooding` (RimSage, `Verse/TerrainGrid.cs:502-566`). So flooding a regrown bed kills the crop with no extra code. UNMEASURED: whether growing zones and the wild plant spawner accept our terrains' affordances and tags once fertility is above 0 |
| **performance at 250²+** | | All grids are bytes; every rebuild is generation-gated; the level-surface solve is a histogram over at most 250 floor heights per body. No per-tick whole-map work is added. The one hot path is ruling 23's shot check (already O(1)); a T2 relative line-of-sight would walk the shot line (§4 T2) |
| **lighting** | | vanilla glow is flat; a pit is not darker. Optional: a floor shade by depth band (cosmetic, his look first). No engine work |
| **roofs** | | the roof grid is flat and per cell; a roof over a 7 m pit is an ordinary roof (and a cover rule already exists). No "underground" roof. No change |
| **walls drawn / built on the floor** | | `RM_Channel_Superdeep` and the deep lakebeds afford only `Light` (MEASURED), so heavy buildings cannot stand on a deep floor. Beds, ladders, ramps, spikes are light. A design choice, not a limit |

## 3. Choosing the quantisation and the max depth from first principles

Four quantities have been sharing the word "level". They can and should differ.

| quantity | today | recommended | why |
|---|---|---|---|
| **dig step** (one designation, one climb unit) | 0.5 m | **0.5 m, keep** | knee-to-thigh height, the size of a stair landing; the climb bands are in this unit (small 0.5 m, person 1 m ≈ 0.6 of 1.7 m, large 1.5 m, huge 2 m); a byte holds 127.5 m. A finer step doubles clicks and work rows and re-states every ruled climb number, and buys nothing now that water is continuous |
| **water amount** | whole notches per cell | **continuous** (decilitres per body; ruled "exactly level" 2026-10-17) | already ruled; the step no longer quantises water |
| **max dig depth** | 2 m | **8 m default, setting 2 to 20 m** (§3.2) | containment saturates at ~3.5 m; storage keeps growing; work grows with the square |
| **pictures** | 4 dry-hole looks, 4 water looks | dry floor: **4 bands** by absolute depth (0.5 to 1 m, 1.5 to 2 m, 2.5 to 4 m, deeper); walls: by **relative** drop, distinct to about 4 m then saturating; water: as ruled (under 25 cm, 0.5, 1, 1.5, 2 m+, lake tints) | the eye on an oblique top-down view can tell about four floor shades; the exact number is the readout's job, as already ruled ("water picture = water depth; walls = hole depth") |

### 3.1 Why 0.5 m stays

A level surface is now a property of a body, not of a step, so the step only decides (a) how fine a player can shape a
floor and (b) the climb unit. Both are about a human body: 0.5 m is a step you can climb easily, 1 m a slow climb, 1.5 m
a trap for a person. That is the owner's own ruled table (2026-10-12 Q2). A 0.25 m step would make "a person climbs 4
steps slowly" the rule and change nothing a player can see.

### 3.2 Why about 8 m, not 4 and not 125

Three ceilings, each measured from the code or arithmetic:

1. **Containment saturates.** The largest climb limit in the built table is 4 notches (huge) plus climber and leaper
   extras (+1 each), so 6 notches = 3 m (`RM_PitTrapMath.ClimbLimit`, `:428-445`). A sheer step of 3.5 m holds every
   creature that does not fly. Deeper walls add **nothing** to prisoner containment. What deeper digs add is **nesting**
   (a pocket inside a pocket, §5), which needs room for at least two sheer steps: 2 × 3.5 m = 7 m. The owner's 7 m core
   is exactly that.
2. **Storage keeps paying, digging keeps costing more.** One cell holds 2,000 L per metre. Cumulative work to depth n
   notches is `3200 × n(n+1)/2` (`WorkToDeepen`); at MiningSpeed 1 and about one work unit per tick (ESTIMATE of the
   vanilla floor-job rate), per cell:

   | depth | notches | work | pawn-days per cell (ESTIMATE) | litres | litres per pawn-day |
   |---|---|---|---|---|---|
   | 2 m | 4 | 32,000 | 0.53 | 4,000 | 7,500 |
   | 4 m | 8 | 115,200 | 1.9 | 8,000 | 4,200 |
   | 7 m | 14 | 336,000 | 5.6 | 14,000 | 2,500 |
   | 8 m | 16 | 435,200 | 7.3 | 16,000 | 2,200 |
   | 20 m | 40 | 2,624,000 | 43.7 | 40,000 | 900 |

   Past about 8 m a cell costs more than a week of one digger, and storage per labour falls below a third of a 2 m
   cell's. That is a natural ceiling without any rule. **Tuning decision (owner's):** keep the quadratic curve (deep
   is a megaproject) or make each notch past 2 m cost a flat amount (deep is merely big).
3. **Pictures saturate.** A 2 m relative drop already hides a standing person (his "walls 20% over the head" visual
   rule, `RM_PitDrawMath`); the wall face north band is 0.5 cell at a 2 m drop. A deeper drop can grow the face to
   about 0.8 cell before it covers the cell to its north. Floors give about four tellable shades. So a player can dig
   16 depths but see about 4 floor bands and every drop's wall; the readout gives the exact metres.

**8 m** covers his example, leaves containment two full nesting steps, keeps one deep cell under about a week of one
digger, and gives each of four floor bands a 2 m span. The setting lets a player go to 20 m (matching the default lake
floor). **125 m is a lake-floor number, not a dig number:** at today's curve a 125 m cell is about 1,640 pawn-days.

### 3.3 Readout resolution

Metres to 0.5 for floors (they are notches), two decimals for water (it is continuous): "Hole 7 m (ledge 4 m) · Water
2.37 m (4,740 L)". Feeds `DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE`.

## 4. The natural breaks in complexity

### T0 — today (cost 0; live proofs owed)

Dig 0.5 to 2 m. Lake floors to 10 m (20 m ruled, `LAKE_FLOOR_TUNE_TEN_TO_FIFTY_METRES` proposed). Relative climb,
masks, ramps, ladders, dry-lake hollows: built offline, **never proven live**. Water: being rebuilt as exactly level.

### T1 — deeper digs, same engine (**3 to 5 agent-days** of new code; 4 to 8 with the owed climb live proofs)

- Split `Superdeep` (the absolute pit, stays 4) from `MaxDigDepth` (a Mod Setting, default 16 notches = 8 m, range 4
  to 40). Delete the three copied literals (`RM_FlowKernel.cs:130`, `RM_PitDrawMath.cs:28`, `RM_PitTrapMath.cs:20`) in
  favour of the two named constants.
- **Read depth from the grid in the dig workgiver, designator and job** (§1.3). Add "dig to N m" on the designator (one
  designation per notch is 14 clicks per cell for 7 m).
- Pocket grid and cliff masks sized by the largest climb limit, not the dig cap; drop the "K ≥ MaxDepth climbs
  everything" shortcut.
- Flow: depth-agnostic once the level-surface solver lands; else fix the band loop and sort keys (`RM_FlowKernel.cs:686,
  :719, :1224, :1236`). Rain loop by the cell's own depth.
- Pictures: wall arrays extended to ~8 notches, saturating; pawn sink by drop below the near lip; a floor tint per depth
  band past 2 m (**cosmetic: his look first**, folds into `WATER_DEPTH_RESKIN_HE_LOOKS_FIRST` or `EXCAVATION_WALL_ART_1`).
- Work curve per his tuning answer. Labels and settings in metres. Selftests: a 4/7/7/4 square digs, levels, traps by
  band, and reloads identically.
- **Risk:** low to medium. The bands and masks are built and selftested, but unproven live; T1 feeds them deeper steps
  (6 and 8 notches) they have never seen. **Saves:** none.
- **Subsumes / conflicts:** extends `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD` (same constants; do in one pass); depends on
  `WATER_SURFACE_REPAIR_LEVEL_OR_BUST` for flow; changes the D5 ruling of `LIQUID_DEPTH_DESIGN_ONE_RULER_FOR_WATER`
  (*"the deepest pit stays 2 m"*): **he reversed D5 by card the same day** (dig 8 m by default), and the pit rules
  become relative rather than starting at an absolute 2 m. Wall art: `EXCAVATION_WALL_ART_1` (validated) gains deeper drops.

### T2 — relative everywhere (**3 to 6 agent-days** + rulings)

The rules that still say "a pit is any cell dug 2 m or more" become relative:
- **Pit rooms:** a room = a person-band pocket (drop `IsSuperdeepRaw`, `RM_PitRooms.cs:65`). A sheer 1.5 m pit becomes a
  prison too. Small change.
- **Ruling 23 (shooting):** today an occupant of a D ≥ 4 cell trades fire only with its 8 neighbours. Relative form: a
  shot is blocked when the line crosses a cell whose floor is higher than both ends by more than a person's height.
  That walks the shot line in a hot path (`CanHitTargetFrom`). **His words define ruling 23; he must re-rule it.**
- **Exposure, fire, drowning:** keyed to pocket and water depth over pawn height (the level surface gives the depth).
- **Spikes:** on any cell with a sheer drop ≥ 2 m from a neighbour, not "D ≥ 4" (`RM_Spikes.cs:50`). Ruled "only in the
  deepest pits" (2026-10-02 Q2); re-ask.
- **Falls:** damage by drop (`FallDropScale` exists).
- **Risk:** medium (shooting is a hot path; three owner rulings re-opened). **Saves:** none.
- **Subsumes:** the absolute OFF-branch in `RM_SuperdeepTrap` could retire with it. Touches `SUPERDEEP_PRISON_ROOM_1`
  (done), `PIT_TEMPERATURE_SOFTENING_1` (validated), `CANAL_BOTTOM_SPIKES_1` (done).

### T3 — land that heals: drained lakes as depressions, plants on dug squares (**2 to 4 agent-days** + his art look)

- Drained lakes as depressions: **built** (T0). What T3 adds is life on them.
- A `regrowth` byte grid: days since a dug or bed cell was last wet. A postfix on `FertilityGrid.CalculateFertilityAt`
  returns a fertility that rises from 0 toward the **original** terrain's fertility (already recorded per dug cell,
  `originalTerrain`, `RM_MapComponent_Excavation.cs:83`) over a setting (say 30 days; PROVISIONAL), capped (say 70%:
  subsoil). Wet cells read 0.
- Wild plants then spawn by vanilla's spawner; players may sow (UNMEASURED: zone and affordance checks on our terrains).
  Refill kills plants through vanilla's own terrain-change rule (§2). Optionally the terrain look swaps to a "settled"
  look past a threshold (reuse vanilla soil art, or new art he sees first).
- Plants change the climb nothing (they are not edifices). Trees in a pit: cosmetic; tall plants still draw over walls.
- **Risk:** low to medium (one hot-ish postfix; vanilla caches nothing per cell here). **Saves:** one grid; absent = 0.
- **Subsumes / conflicts:** `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` (doing) owns the mud timer: regrowth should start
  when mud ends. `LAKE_FLOOR_TUNE_TEN_TO_FIFTY_METRES` makes the bowls deeper; no conflict.

### T4 — a real elevation engine: DEAD (owner, by card, 2026-10-17)

Raised ground (berms, mounds), natural hills, line of sight and projectile arcs by height, cover by height, a cell above
another cell (tunnels, bridges over pits). Every vanilla system assumes a flat map. **Weeks to months; very high risk.**
It also breaks LAW 1. **Ruled dead, not deferred.** No v2 parking.

### Order

T1 after the level-water solver and after the three climb live proofs; T3 can run in parallel with T1 (different
files); T2 only after he re-rules ruling 23 and spikes.

## 5. The 4/7/7/4 square, specifically

```
4 4 4 4        ring: 12 cells at 4 m (8 notches)
4 7 7 4        core:  4 cells at 7 m (14 notches)
4 7 7 4
4 4 4 4
```

| question | answer under T0 (today) | under T1 |
|---|---|---|
| can it be dug? | no: digging stops at 2 m | yes |
| work (ESTIMATE, MiningSpeed 1, soil) | — | ring 12 × 115,200 + core 4 × 336,000 = **2.73 M work ≈ 45 pawn-days**; rock ground multiplies it. With a flat cost per notch past 2 m (e.g. 12,800), about 27 pawn-days |
| designations | — | 152 one-notch cuts, or 16 with "dig to N m" |
| water it holds | — | 12 × 8 + 4 × 14 = **152 notches = 152,000 L** in 16 cells (about 4.75 tall 2×2 tanks) |
| how it fills | — | one level body: the core fills first (to 3 m of water) then the surface rises over all 16; a body splits only if the surface falls below the 4 m ledge (the core keeps its own surface). The level-surface solver does this by its histogram |
| who is trapped | — | surface → ring is an 8-notch sheer step: **nothing that walks gets out** (largest K = 6). Ring → core is 6 notches: only a K 6 creature (a huge climbing leaper) gets from core to ring, and it is still held in the ring. Prisoners: the whole square is one person-band pocket, so one pit room |
| how pawns get in and out | — | **ladders only.** A ramp spans at most 3 notches and needs a cell at each intermediate depth; the ring is one cell wide at one depth, so no ramp fits inside the square. A ladder in a ring cell reaches the surface; a ladder in a core cell reaches the ring. Or dig an approach trench outside: surface → 1.5 m → 3 m → 4 m by three ramps, then a ladder to the core |
| how it renders | — | ring and core both show the deepest dry floor terrain; today's walls draw an 8- and a 6-notch drop the same as a 4-notch drop, and pawns sink the same in both. T1's wall, sink and floor-tint changes are what make the 7 m core read deeper than the 4 m ledge |
| what is impossible | everything | seeing the core floor from an angle (no camera tilt); standing on the 4 m ledge **over** the core (no cells above cells); building heavy structures on the floor (affordance `Light` only) |

**How much harder than four levels?** For digging, holding water and trapping: **T1 only, 3 to 5 agent-days**, because
the relative rules it needs are already built. For making it **look** like a 7 m shaft inside a 4 m pit: the T1 picture
work plus an art look by him. For the shooting and prison rules to treat the ledge and core differently: T2.

## 6. Play experience (engine view)

**What becomes interesting.**
- **Stepwells and terraced cisterns.** The real-world reference is the Indian stepwell (Chand Baori, about 30 m deep,
  terraced): exactly T1 ramps plus terraces, with the water at a level surface that drops as you draw it.
- **Nested prisons.** A pocket inside a pocket: a ladder you raise at each level. A huge creature held in a 3.5 m core
  that a 2 m pit could not hold (today only K < 4 creatures are holdable).
- **Drained lakes as basins** (T0, built): gentle bowls that never trap, now with grass coming back (T3), flooded again
  when the dam opens.
- **Sunken gardens** (T3): a dug square left dry regrows; flood it and the crop dies. A real choice between water and
  food on the same ground.

**What becomes degenerate.**
- **Escape-proof prisons** are not new: a sheer 1.5 m pit already holds a person. Deeper digs add holding large
  creatures, which is intended (ruled per body size).
- **Cheap storage:** bounded by the work curve; not cheap. If the curve is flattened, storage per labour rises sharply;
  then a cap matters more.
- **Raider pathing (the real risk).** A base ringed by a sheer trench is unreachable by walking hostiles under the
  masks. Vanilla raid AI expects a path or a building to breach; a cliff is not a building. This exists already at
  2 m; deeper digs make it more common. The climb live proof (`climb_proof.py`, owed) must include a raid against a
  ringed base before T1 ships.

## 7. The outside read (GPT, evidence)

Model gpt-6.1-sol (the `gpt_consult.py` default), effort high; given the facts of §1 and the owner's question, not this
file's recommendations. Verbatim in `flowworks_elevation_feasibility_2026-10-17.gpt_read.md`.

**Agrees (independently):** keep the 0.5 m step; 8 m default dig, 20 m as the advanced maximum, 125 m for natural beds
only; size the pocket grid and masks by climb ability, not by depth (its arithmetic: at a 125 m dig cap today's
formula would make 249 bands, about 112 MB on 300²); the "K ≥ MaxDepth needs no grid" shortcut is unsafe; the dig job
must read the grid, not terrain; walls drawn from relative drops with compressed height past about 2 m; the 4/7/7/4
work is 2,726,400 (45.4 pawn-days) and 152 notch jobs; the ring is too narrow for ramps, so ladders; the real break in
complexity is **two usable spaces at one horizontal cell**, not 8 m against 20 m.

**Adds (accepted into this file):**
- **Threading.** 1.6 runs pathfinding batched and multithreaded. The per-request mask swap must be proven to hold the
  right array for the job's whole life while masks are rebuilt. That is a live-proof row the climb items owe now, and
  it is a precondition for T1.
- **Ruling 23 becomes conspicuous on a wide floor.** Two pawns far apart on one flat 2 m (or 7 m) floor cannot shoot each
  other. This is true today in any wide pit and grows with terraces. It raises T2's shooting question in priority.
- **Plants:** fertility-ignoring plants exist, so fertility 0 does not stop every plant; a water change that does not
  write terrain would skip vanilla's plant cleanup. (Our fill and pond-stage writes go through `SetTerrain`, so the
  cleanup fires; T3 must keep that true.)
- **Reachability:** "vanilla reachable AND same pocket" is necessary, not sufficient, for a real route; the logged
  false positive is already accepted in the climb design §8.5 step 6, and ladder permissions make it worse.
- **Settings decrease:** lowering the dig cap must never shallow a dug cell.

**Disagrees, and why:**
- **Cost of T1.** GPT says 5 to 9 days for "reliable dry relief to 8 m"; this file says 3 to 5. The gap is the
  connector and threading audit, which GPT counts here and this file counts under the climb items' **already-owed** live
  proofs. Combined honest figure: **3 to 5 days of new code, plus the owed climb proofs (1 to 3 days of live work), so 4
  to 8 in all.**
- **Water volume.** GPT assumed 1 m² cells (76 m³). The ruled square is 2 m² (`flowworks_unified_depth_2026-10-17.md`
  §0, item 2), so the square holds **152,000 L**, as in §5.
- **Visual classes.** GPT suggests six dry floor classes; this file says four. The difference is cosmetic and his to
  judge on a sheet.
- **Its water tier (8 to 15 days)** overlaps `WATER_SURFACE_REPAIR_LEVEL_OR_BUST` (4 to 7 days, already ruled). Not
  counted twice here.

## 8. Decisions for the owner (question-card wording)

**Q1. How deep may a player dig?**
- (a) **8 m by default, a setting from 2 m to 20 m.** *Recommended: covers your 4/7/7/4 example, two full trap
  steps, and keeps one cell under about a week of one digger.*
- (b) 4 m by default (just past where containment stops improving).
- (c) 20 m by default, the same as the lake floor.

**Q2. Should digging get much slower the deeper you go?**
- (a) **Yes, as now: each half metre costs more than the last (your 4/7/7/4 square ≈ 45 days of one digger).** Deep is
  a megaproject.
- (b) Past 2 m every half metre costs the same (≈ 27 days for the square). Deep is just big.

**Q3. Build order?**
- (a) **Deeper digs (T1) after level water and the climb tests; healing land (T3) alongside; rules made relative (T2)
  only after you re-rule shooting and spikes.** *Recommended.*
- (b) T1 now, before level water.

**Q4. Real elevation (raised ground, hills, height line of sight): mark it dead, not deferred?**
- (a) **Yes, dead.** *Recommended: it is a new engine and contradicts "we dig down, never build up".*
- (b) Keep it open for v2.
