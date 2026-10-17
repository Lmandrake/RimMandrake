# One ruler for all water: the unified depth spec (RULED 2026-10-17)

Item: `LIQUID_DEPTH_DESIGN_ONE_RULER_FOR_WATER`. **RULED SPEC.** The owner ruled by question card on 2026-10-17 (§10
holds every decision and its authority; the ledger carries them as `--by-card` notes on the item). This file is now the
authority for liquid depth, volume and their words and pictures; where another FlowWorks doc disagrees, this one wins
and the other is wrong. Code claims come from a read-only census of `src/RimMandrake/FlowWorks` at HEAD on 2026-10-17
(file:line given); the code is not yet changed (build items in §11).

**Later the same day (2026-10-17) the owner ruled further, by card:** water is exactly level (one surface per connected
body, exact decilitres, not whole notches); a new very-shallow look under 25 cm; colonists dig to 8 m by default
(setting 2 to 20 m), which **reverses D5**; the 2 m-keyed rules become relative to the height difference; everything is
built in one rebuild. This file is corrected to match. Build plan: `design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`.

The owner, 2026-10-17 (S5.Q1 write-in): *"We collectively ruled four across everywhere... but then we moved to meters
depth and Liters. Please do a full deep design pass right now on how to reconcile all of this. It's ok to have some
number of visual depths of liquid, as well as visual depths of canal. But we must not get confused on the depth of the
water. So please, come up with a unified way to represent all of this and present it to me. Then let's adjust all the
design docs and mechanics once and for all. As for natural sources, yes they should be able to go MUCH deeper than
level 4 canals."*

---

## Summary (one page)

**What is wrong today.** The numbers mostly agree; the *words* and the *pictures* do not.

- "Four" is true, but it is a **volume** fact (a tank square, a 2 m canal square and a shore-deep pond square all
  hold 4,000 L). It was never a supply rule.
- "Five" is dead in the code but alive in comments, a setting label and the burn rate (§2).
- "Level" means five things: a 0.5 m depth step, a fill amount, a fill *picture*, a water surface and a map control.
- "Deep" means three things: a 1.5 m canal (`Deep` = D3), 2 m of water (vanilla deep water = 4 steps), and a 2 to 4 m
  dry lakebed (`RM_Lakebed_Deep`).
- **The worst one:** a dug canal picks its water picture by *how full it is* (a third, two thirds, brim). A pond picks
  its picture by *how deep the water is*. So "half full" looks the same in a 1 m canal (0.5 m of water) and a 2 m
  canal (1 m of water). That is exactly "getting confused on the depth of the water".

**The ruling (Scheme A, adopted by card 2026-10-17): litres are the truth, metres are the ruler, and the step is 0.5 m.**

1. **Truth = litres.** Every amount of liquid, everywhere, is litres (already true in tanks, hoses, pumps and
   containers since 2026-10-16).
2. **Ruler = metres below ground.** A square is 2 m² of floor (1.41 m on a side), so in one square **1,000 L = 0.5 m**.
   Depth is never shown as a fraction, a tier name or a "level"; it is shown in metres.
3. **Step = 0.5 m, called a notch.** One notch in one square = 1,000 L. Digging goes in notches, and the picture bands
   are notches. **Water does not:** each connected body holds exact decilitres and has one level surface
   (`flowworks_level_surface_2026-10-17.md`, ruled exactly level). "Notch" is the owner's own word (2026-10-12: *"at least 4 notches deep"*).
4. **Every water picture is chosen by water depth in metres, the same for a canal, a pond or a pit:** under 25 cm (a
   new very-shallow look; he sees it first), 0.5 m, 1 m, 1.5 m, 2 m and deeper (plus darker "very deep" tints for lakes: ruled yes, owner sees them first). The **hole's** depth is shown separately,
   by the canal's walls and how low a pawn sits. Water picture = water depth; walls = hole depth. Never one for the
   other.
5. **Natural water goes much deeper.** A pond's shore is 1 m (shallow water) or 2 m (deep water). **Lake floors, owner R11 (2026-10-17, supersedes D2's fixed numbers):** floors vary per lake and per biome roughness (mountainous deep and chasm-like, plains shallow and silted), irregular, not a radial slope; the ceiling stays settable to 125 m; 50 m is an upper bound for mountainous/deep biomes only (`LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP`). Oceans and edge rivers never run down, so their depth is a picture and a readout, never a
   litre count.
6. **"Four" stays and is renamed the yardstick: 2 m = 4 notches = 4,000 L in one square.** This is one tank square and
   a shore-deep pond square. It is no longer the deepest dig (8 m by default, setting 2 to 20 m). "Five" is deleted everywhere.

**The S5 answer this gives.** One full 2 m pond square holds 4,000 L, enough for **four** 0.5 m canal squares **by
pump**. **By gravity it gives far less.** Under the ruled leveling law (2026-10-16 D2: *"It should slosh around until it
levels"*) a canal takes only the water that stands above its own floor. So a 0.5 m canal draws at most the top 0.5 m of
the pond, and only until the two surfaces are level. To drain a pond by gravity you dig as deep as the pond; to empty it
you pump. With exactly level water a 3×3 pond does wet all ten canal cells, but thinly (24 cm each), and one pond square
wets all ten at 4.5 cm, not four full cells. **Scene S5 is redrawn with these level numbers** (§6).

**Cost (ESTIMATED):** about 2 to 3 agent-days for Scheme A, no grid rescale, and one re-picture pass on load.
Alternatives considered and not taken (§8): **B** a finer 0.1 m step; **C** abstract "levels" with no metres; **D**
keep fullness pictures and only fix the numbers.

**Decided (§10):** the owner ruled the scheme (A), the lake floor ceiling (to 125 m; the floor shape was re-ruled later the same day, R11, §5.2), "20% over the head" as a visual rule only, and the new art (yes, seen by him before it
ships). **Defaulted, veto-able:** one burn rate; delete the pond-volume multiplier; restate the two north-star bars in
metres and have him re-validate them; redraw S5 with both a deep gravity canal and a pump.

---

## 1. What the engine actually holds today (MEASURED, census 2026-10-17)

| thing | stored as | unit | where |
|---|---|---|---|
| dug depth D | byte 0..4 | notch (0.5 m) | `depthGrid`; `RM_ExcavationDepth.cs:27-40` (`Shallow 1, Mid 2, Deep 3, Superdeep 4`) |
| dug fill F | byte 0..D | notch | `fillGrid` |
| natural floor (bed) | byte 0..250 | notch | `bedRecord`; shallow water 2, deep water 4, lake middle +1 per 4 squares beyond 3 from shore, cap `deepBedMaxDepth` 20 (setting 4..40), `RM_BedMath.cs:32-38`, `RimMandrakeFlowWorksMod.cs:143, :422` |
| pond water | float `stock` | "fill-unit" = notch × `volumePerTile` (1) × `sourceBudgetMultiplier` (1) | `RM_LiquidBody.cs:109-113`, `RM_StockMath.cs:55` |
| tank, hose, converter | int | decilitre | `Building_LiquidTank.storedUnits`, `CompHoseReel.heldUnits` |
| one notch in one square | — | 1,000 L | `RM_Volume.LitresPerLevel`, `.cs:26` |
| metres per notch | — | 0.5 m | `RM_Volume.MetresPerLevel`, `.cs:29` (readout only) |
| the yardstick | — | 4 notches | `RM_Volume.LevelsPerSquare`, `.cs:20` |

So the engine already has one consistent chain: **1 notch in 1 square = 0.5 m = 1,000 L**. The ruled model keeps that
chain and makes everything else obey it.

## 2. Every conflict found

### 2.1 Words

| word | meanings in use today | ruled |
|---|---|---|
| **level** | a 0.5 m step (`LevelsPerSquare`); a fill amount (`fillGrid`); a fill *picture* (burn: "one fullness level a day", `flowworks_mod_definition.md` §burn); the water surface ("levels out", level-set solve); a map control (Level Holder) | player text: "level" = **water surface** only ("the water levels out", Level Holder). A count of steps is a **notch**. Code identifiers may keep their names; a glossary line in `RM_Volume.cs` maps them. |
| **deep** | canal `Deep` = D3 = 1.5 m; vanilla deep water = 2 m; "deep notch" = 4; `RM_Lakebed_Deep` = 2 to 4 m; "deep pond square" | "deep" is never a number. Canals and pits are named by metres: "canal 0.5 m / 1 m / 1.5 m / pit 2 m". |
| **SUPERDEEP** | D4 = 2 m = the trap depth | the player sees "pit (2 m)"; the code keeps `Superdeep`. |
| **Empty** | `RM_Channel_Empty` is the **0.5 m** dug channel, not "no water" | relabel "shallow canal (0.5 m)"; defName unchanged (a save holds it). |
| **Trace / Half / Brim** | fill *fractions* of the hole (`RM_ExcavationDepth.FillTier`, `.cs:112-125`: ⅓ and ⅔) | retired as words; the four fill terrains per liquid are re-keyed to 0.5 / 1 / 1.5 / 2+ m of water (§4). |
| **thin / shallow / chest / deep** (ponds) | water depth 1 / 2 / 3 / 4+ notches (`pond_depth_design_2026-10-16.md` §4) | kept, labelled in metres. Note: "thin" is described there as *ankle-deep*, but 0.5 m is knee-deep. Relabel "knee-deep". |

### 2.2 Numbers

| number | where | status |
|---|---|---|
| **4** = the yardstick | `RM_Volume.LevelsPerSquare`; ruling 2026-10-12 | **true, kept** |
| **4** = deepest dig | `RM_ExcavationDepth.MaxDepth`, and three more hard copies: `RM_FlowKernel.Superdeep` (`.cs:123`), `RM_PitDrawMath.MaxDepth` (`.cs:28`), `RM_PitTrapMath.Superdeep` (`.cs:20`) | **no longer true** (dig default 8 m, setting 2 to 20 m): split the dig cap from the 2 m pit constant (`PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT`); four separate literals today. All read `MaxDepth`. |
| **4** = what a natural source "is" in the flow engine | `RM_FlowKernel.Superdeep`, used for every natural square whatever its floor | **wrong after deep beds**: a 1 m marsh flows as 2 m and a 10 m lake middle flows as 2 m. Fixed by the water-surface rewire (`WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND`, doing) if it reads the floor. |
| **5** = canal squares per source square | `flowworks_mod_definition.md` §5 "each supplies up to five canal cells"; `FLOWWORKS_BUILD_PROGRAM_1`; `flowworks_northstar_interrogation_2026-10-02.md:75`; `flowworks_map_controls_design_2026-10-16.md:23`; comments `FlowWorks_Fluids.xml`, `RM_FlowKernel.cs:441`, `RM_LiquidStock.cs:9`, `RM_StockMath.cs:13`; settings label `RimMandrakeFlowWorksMod.cs:103` ("the 5:1 budget") | **dead in code** (replaced 2026-10-12 by floor depth), alive in text. Delete everywhere. |
| **5** = days per source notch burned | `sourceBurnDaysPerLevel` = 5 (`RimMandrakeFlowWorksMod.cs:446-447`), from the 5:1 "density" argument | its reason is gone. One burn rate per burning square (§5.6). **Defaulted, veto-able** (D3). |
| **5** = surface bands in the level solve | `RM_FlowKernel.cs:673-710`, loops `b < 5` | a hidden copy of "depth 0..4". Must derive from the deepest floor present, or ponds deeper than 2 m cannot join a canal's solve. |
| **8** = lake "abyss" | `RM_Volume.AbyssBedLevels` (`.cs:148`), dry bed picture | 4 m. Restate in metres. |
| **2** = notches in "a natural square" for heat | `RM_LiquidHeatMath.NaturalCellLevels` (`.cs:39`) | wrong for a 2 m or 10 m square; read the square's real water depth. |
| **1.46 m vs 1.41 m** | `liquid_litres_2026-10-16.md` measured a cell at 1.46 m; 1,000 L per notch implies 1.41 m | settle by definition: **a square is 2 m² (1.41 m a side)**. The 3% gap is below the error of the "deep water is 2 m" assumption. |
| **2 m pit vs walls 20% above the head** | `PIT_SUPERDEEP_COLLAPSE_1` (2026-09-17): *"the walls are higher than their head by 20%"*; a 1.75 m human ⇒ 2.1 m; the pit is 2 m | **Ruled (D5): "20% over the head" is a visual rule only**, carried by the pit's art and the pawn's sink offset. (D5's "the pit stays 2 m" was reversed the same day: dig to 8 m by default.) |

### 2.3 Pictures

- **Dug canals:** water picture by *fraction* of the hole (⅓, ⅔, brim; `FillTier`).
- **Ponds:** water picture by *metres of water* (thin, shallow, chest, deep; `pond_depth_design` §4).
- **Dry lakebeds:** by floor depth (`LakebedFor`: below 2 m, 2 to 4 m, 4 m and more).
- **Pawn sink:** 0.3 cells per notch of the **hole** (`RM_PitDrawMath`, cap 2 m per the deep-bed design §9.5).
- **Mouseover:** already metres and litres ("1.5 m deep, 3 kL"; `RM_MouseoverDepth.cs:82, :97`). Not yet seen live.

So two pictures say "water depth" and one says "fullness". That one is the source of the confusion.

### 2.4 Settings that bend the ruler

- `sourceBudgetMultiplier` (0.2 to 5): a pond square at ×2 holds 8,000 L while its floor still reads 2 m. **The litres
  and the metres disagree.** This is the one setting that can make the depth readout lie.
- `tankCapacityMultiplier` (0.2 to 5): breaks "one tank square = 2 m". Its tooltip already says so.
- `volumePerTile` (per liquid, 1 for all): if any liquid set it to anything else, a notch would cost different litres
  in a pond and in a tank (`RM_LiquidBody.cs:178` against the tank path). A hidden unit.

## 3. The canonical model (Scheme A)

| quantity | canonical | derived views |
|---|---|---|
| amount of liquid | **litres** (stored as whole decilitres: per tank and hose, and per connected water body, which has one level surface) | kL in text |
| depth of water in a square | **metres** = litres in the square ÷ 2,000 | a picture band (§4); a notch count inside the engine |
| depth of a hole or a floor | **metres below ground** | 4 dry canal looks; 3 dry lakebed looks; pawn sink |
| water surface | **metres below ground** = floor − water depth | "the water levels out" |
| the step | **notch = 0.5 m = 1,000 L in one square** | — |
| the yardstick | **2 m = 4 notches = 4,000 L** in one square | — |

**One conversion constant.** `RM_Volume` gains `SquareAreaM2 = 2` and `MetresPerNotch = 0.5`, and derives
`LitresPerNotch = SquareAreaM2 × MetresPerNotch × 1000`. Every other number (tank size, pump pour, mouseover,
settings text, oracle) reads these. Python reads them from the C# by regex, as
`northstar/selftest_conservation_roundtrip.py:57-65` already does.

## 4. What the player sees

**Rule: the water picture says how deep the water is. The walls say how deep the hole is. Text says both in metres.**

### 4.1 Water depth bands (every liquid, every square: canal, pit, pond, lake)

| water depth | water look | source |
|---|---|---|
| under 25 cm | very shallow (**new art**, ruled by card 2026-10-17; he sees it first: `VERY_SHALLOW_WATER_RESKIN_HE_SEES_FIRST`) | new |
| 0.5 m | knee-deep (`RM_WaterThin` for water; the liquid's first fill look for others) | water: new art, already approved (D4, 2026-10-16) |
| 1 m | shallow (vanilla `WaterShallow` look) | vanilla |
| 1.5 m | chest-deep (`RM_WaterChestDeepStill`, vanilla chest-deep art) | def exists |
| 2 m and deeper | deep (vanilla `WaterDeep` look) | vanilla |
| optional: 5 m+, 10 m+ | darker "very deep" and "abyss" tints on lakes | **new art or tint; cosmetic, needs the owner's permission** |

- For canals this re-uses the four fill terrains each liquid already has (`RM_Fill_<Liquid>_Trace/Half/Brim/Superdeep`).
  Only the **rule that picks them** changes: by metres of water, not by fraction. defNames stay, so saves do not break;
  labels become "0.5 m of water" and so on.
- So "1 m of water" looks the same in a 1 m canal, a 2 m pit and a pond. That is the point.

### 4.2 Hole depth (dry or wet)

- **Dry:** the four dug looks stay (`RM_Channel_Empty/Mid/Deep/Superdeep`), labelled 0.5 m, 1 m, 1.5 m and pit 2 m.
- **Wet:** today a wet cell shows only its fill terrain, so the hole's depth vanishes. The north-star bar
  `depth_and_fill_jointly_legible` (`design/validation_walks/RimMandrake/FlowWorks.md`) needs it shown. Ruled (art): a thin
  **wall band** at the cell's edge whose height is the gap between the water and the lip (0 when brim-full, up to 2 m).
  That is an overlay, not a new terrain. **New art: approved in principle; the owner sees a sheet or in-game shot before it ships.** Until then, the pawn sink offset and the
  mouseover carry it.
- **Pawns** sink by the drop below the nearest lip, capped at the lip (`PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT`).

### 4.3 Text

- Mouseover, one fixed form: **"Water 1.5 m deep (3 kL) · floor 2 m down"**. A lake square: "Water 6 m deep (12 kL) ·
  lakebed 6 m down". Open sea or edge river: "Open water, never runs dry".
- Dig orders: "Dig to N m", in 0.5 m steps up to the dig cap (8 m by default).
- Pond inspect: "Holds 340 kL; surface 0.5 m below the brim".
- **Forbidden in player text:** "level N" as a count, "half", "brim", "trace", "5:1", "fill-units".

## 5. The mapping, thing by thing

### 5.1 Canal squares
0.5, 1, 1.5 or 2 m deep; 1,000 to 4,000 L full. The 2 m canal is the pit (traps; ruled "superdeep only",
2026-10-16 by card; the trap rules become relative to the height difference, 2026-10-17). Colonists may dig deeper: 8 m
by default, a setting from 2 to 20 m (owner, by card, 2026-10-17).

### 5.2 Ponds and lakes (limited natural water)
- Floor at the shore: shallow water 1 m, deep water 2 m (ruling 2026-10-12, unchanged).
- Beyond the shore: **Lake floors, owner R11 (2026-10-17, supersedes D2's fixed numbers):** floors vary per lake and per biome roughness (mountainous deep and chasm-like, plains shallow and silted), irregular, not a radial slope; the ceiling stays settable to 125 m; 50 m is an upper bound for mountainous/deep biomes only (`LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP`). The byte grid stores 250 notches (125 m).
- A pond's water = Σ (floor depth × 2,000 L) over its squares. **Nothing multiplies it** (§2.4).
- Each lake square shows its own water depth. A drawn-down lake shallows all over (`pond_depth_design`, D1 and D2).

### 5.3 Oceans and edge rivers (limitless)
They never run down (ruling 16), so they need no floor record and no litre count. They show the vanilla depth look and
"open water". If a dam ever cuts a piece off, that piece becomes a limited pond and gets a floor from §5.2.

### 5.4 Tanks
A tank square is a 2 m column: 4,000 L; a tall tank square is 4 m: 8,000 L (ruling 2026-10-12). The 2×2 tank is 16 kL
and the tall one 32 kL, as built. The inspect can say "2 m of water" next to the litres, using the same ruler.

### 5.5 Hoses, pipes, pumps, containers
These have no depth; they are litres only. A hose holds 5 L a cell. A pump pours one notch (1,000 L) into one square per
step. Bottle 1.5 L, bucket 15 L, barrel 208 L. All unchanged.

### 5.6 Burning
Today a canal square burns down 1 notch a day and a pond 1 notch per 5 days, from the dead 5:1 argument. **Defaulted (D3): one
rate per burning square**, 0.5 m a day. A pond still lasts far longer than a canal because its whole volume is shared
across the squares that are not burning. **Veto-able.**

### 5.7 Natural taps (drill, Source tap, subsurface reserve)
These have no depth: they are a litre reserve. Per S3.Q1 (2026-10-17): placed in a canal, a tap fills the canal; on
the surface, it needs a pipe or hose.

## 6. How many canal squares does a pond square supply?

There is no fixed number. It depends on how the water moves.

| how | one full 2 m pond square gives | why |
|---|---|---|
| **pump** | 4,000 L = **four** 0.5 m canal squares, or one 2 m pit square | volume; the yardstick |
| **gravity, canal as deep as the pond** | up to all of it, until the surfaces are level | leveling law |
| **gravity, 0.5 m canal at the brim** | at most the top 0.5 m (1,000 L), and in practice less, because the canal and the pond settle to one surface between ground and 0.5 m | leveling law: water never climbs above its surface |

**Worked S5 cases, under the leveling law with exactly level water** (`flowworks_level_surface_2026-10-17.md` §1):
- **S5-A (3×3 pond, 2 m, at the brim, 36,000 L; 10-cell 0.5 m canal):** one surface settles 0.263 m below ground. The
  pond stands 1.737 m deep and **all ten canal cells are wet, 0.237 m each**.
- **S5-B (one full pond square, 2 m, 4,000 L; same canal):** one surface settles 0.455 m below ground: **all ten canal
  cells wet at 4.5 cm**, not four full cells.

So S5 is redrawn (D6, defaulted, and the owner's card 2026-10-17 to redraw with level numbers): parts A and B keep the
0.5 m canal and claim the level numbers above;
a new part F joins one 2 m pond square to one 2 m canal square by gravity (they level at 1 m of water each, 4,000 L in
all); a new part G pumps one 2 m pond square into a 0.5 m canal (four 0.5 m squares' worth, 4,000 L, counting what the
hoses hold). `design/RimMandrake/vv_methods/water_scenes_2026-10-16.scenes.json` is re-sealed and S5 awaits the owner's
re-approval; his S3, S4 and S6 answers stand.

*Note on today's game:* the shipped engine still lets a natural square give until its stock is empty, as if it were
2 m deep everywhere (`RM_FlowKernel.Superdeep`). The leveling law is ruled (D2, 2026-10-16) and is being built in
`POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` and `WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND`. This spec assumes the ruled
law, not the shipped one.

## 7. What must change

### 7.1 Design docs and items (applied 2026-10-17)
| file | change |
|---|---|
| `design/RimMandrake/flowworks_mod_definition.md` | §5 budget "five canal cells" → volume + leveling law; §burn "5 days" → D3; ruling 19 "four depths" relabelled in metres |
| `design/RimMandrake/natural_bodies_as_canals_design_2026-10-11.md` | the 5-unit level and `UnitsPerLevel = 5` removed, old-code §8.1 deleted; §9.6 constants table → metres, cap per D2 |
| `design/RimMandrake/liquid_litres_2026-10-16.md` | add the `SquareAreaM2` definition; "level" → notch in prose |
| `design/RimMandrake/pond_depth_design_2026-10-16.md` | §4 stages in metres; "ankle-deep" → knee-deep |
| `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md`, `infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md`, `design/RimMandrake/pit_superdeep_collapse_spec.md` | D 0..4 named in metres; the 2 m against 20%-over-head line (D5) |
| `design/RimMandrake/relative_depth_climb_design_2026-10-12.md` | climb steps in metres (0.5 m easy, 1 m slow) |
| `design/RimMandrake/flowworks_northstar_interrogation_2026-10-02.md`, `design/RimMandrake/flowworks_northstar_script_plan_2026-10-02.md`, `design/RimMandrake/flowworks_map_controls_design_2026-10-16.md`, `infrastructure/state/items/FLOWWORKS_BUILD_PROGRAM_1.md` | delete the 5:1 budget |
| `design/validation_walks/RimMandrake/FlowWorks.md` | the `## north star` bars `fill_tier_legible` and `depth_and_fill_jointly_legible` say "trace, half, brimming": restate in metres. **This is the owner's hash-bound section; he re-validates it.** |
| `design/RimMandrake/vv_methods/water_scenes_2026-10-16.scenes.json` + `water_scenes_for_approval_2026-10-16.md` | legend "P holds 4 levels" → "2 m, 4,000 L"; global units → litres and metres; S5 redrawn (§6); re-seal |

### 7.2 Code, defs and settings (`src/RimMandrake/FlowWorks/`)
| place | change |
|---|---|
| `Source/RM_Volume.cs` | add `SquareAreaM2`, `MetresPerNotch`; derive litres; lakebed thresholds in metres; glossary comment |
| `Source/RM_ExcavationDepth.cs` | `FillTier` by metres of water, not fraction; `LabelOf` in metres |
| `Source/RM_LiquidLooks.cs:171` | tier map follows the new `FillTier` |
| `Source/RM_FlowKernel.cs:123, :673-710` | a natural square's depth = its floor (not 4); band count from the deepest floor, not a literal 5 |
| `Source/RM_PitDrawMath.cs:28`, `Source/RM_PitTrapMath.cs:20` | read the split constants (2 m pit, dig cap setting); `PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT` |
| `Source/RM_LiquidHeatMath.cs:39` | real water depth, not 2 |
| `Source/RM_BedMath.cs:35`, `RimMandrakeFlowWorksMod.cs:143, :422` | cap default and range per D2, shown in metres |
| `RimMandrakeFlowWorksMod.cs:103, :160, :446-447, :896-898, :964` | delete `sourceBudgetMultiplier` (D4) and the "5:1" label; burn rate per D3; strings in metres and litres |
| `Source/MapControls/RM_LevelHolder.cs:208-220`, `Source/RM_MouseoverDepth.cs` | one text form (§4.3) |
| `Languages/English/Keyed/FlowWorks_Keys.xml:21-23` | "1 to {0} levels shallower" → metres; drop the hard-coded 3 |
| `Defs/Canals/FluidDefs/*.xml` | delete the "five-cell pond supports twenty-five" comments; pin `volumePerTile` to 1 or delete it |
| `Defs/Canals/TerrainDefs/FlowWorks_Terrain.xml` | labels of `RM_Channel_*` and `RM_Fill_*` in metres (defNames unchanged) |
| `Source/RM_PumpMath.cs` | stale `PourLevels` comment ("5 units pours 2 levels") |
| Python: `northstar/selftest_flowworks_kernel_oracle.py`, `northstar/pond_pump.py:43`, `northstar/liquid_checks.py:61` | read constants from C#, no literals |
| optional art | the wall band (§4.2); lake depth tints (§4.1). Owner permission first. |

## 8. Alternatives

| | **A. Litres, metres, 0.5 m notch** (ADOPTED) | **B. Finer step: 0.1 m** | **C. Abstract levels, no metres** | **D. Keep fullness pictures, fix numbers** |
|---|---|---|---|---|
| truth | litres | litres | levels | litres |
| engine step | 0.5 m = 1,000 L | 0.1 m = 200 L | 1 level | 0.5 m |
| water picture keyed to | metres of water | metres of water | levels of water | fraction of the hole |
| what it fixes | every word and picture conflict | the same, plus smooth leveling: real surfaces like 0.26 m become possible, which ends the "0, deep, 0" family for good | words only | the 5 and the comments |
| cost (ESTIMATED) | 2 to 3 days; no grid rescale; one re-picture pass | 5 to 8 days: every grid, rate, setting, oracle row and selftest ×5; floors over 25 m need a 16-bit grid; 5× more flow work for the same water | 1 day | under 1 day |
| risk | the wall band is new art | the flow engine and its fuzz suite re-tuned; a long migration | contradicts his litres-and-metres card (2026-10-16); "level 30 lake" means nothing to a player | **leaves the exact confusion he named**: the same picture for different water depths |
| save impact | none to grids; pictures re-laid once | all grids ×5, versioned | none | none |

**Why A:** it is the smallest change that makes "how deep is this water" have one answer everywhere, and it keeps the
grids, the selftests and the conservation proofs as they are. B was never taken: the level-surface design showed a
finer fixed step still leaves steps, and the owner ruled water exactly level instead (one surface per body, exact
decilitres; `flowworks_level_surface_2026-10-17.md`).

## 9. Migration and saves (Scheme A)

- **Grids** (`depthGrid`, `bedRecord`): unchanged; a notch stays 0.5 m. `fillGrid` becomes a view derived from each
  body's volume and surface; body volumes are a new saved record (`flowworks_level_surface_2026-10-17.md` §3).
- **Pictures:** a new scribed marker `RM_depthViewModel` (absent = 0). On the first load at 1, every wet dug cell
  re-picks its fill terrain by metres (a temp-terrain write, capped per pulse like `pondStageWritesPerPulse`).
  Nothing about the water changes.
- **Pond floors already recorded** keep their record (ruling 7: a refill returns the exact shape). Only ponds formed
  after the cap change get the deeper middles. A setting could re-floor never-drawn ponds; not built.
- **`sourceBudgetMultiplier` removed:** a save where it was not 1 scales each pond's stock to keep its fullness
  fraction, logging one line per pond. This is the same move as the 2026-10-12 migration.
- **Settings file:** the burn keys and the cap key are read once under their old names.
- **Tanks, hoses, containers:** already litres; nothing.

## 10. Decisions (2026-10-17)

**Ruled by the owner, by question card, 2026-10-17** (ledger: `--by-card` notes on `LIQUID_DEPTH_DESIGN_ONE_RULER_FOR_WATER`):

| # | decision | ruling |
|---|---|---|
| D1 | scheme | **A**: litres true, metres shown, 0.5 m notch (1,000 L per square); "four" = the 2 m dig; "five" deleted everywhere |
| D2 | lake floor cap | settable to 125 m. Its 20 m default / 50 m large-lake numbers were **replaced** later the same day by R11 (floors per lake and biome roughness; 50 m only for mountainous/deep biomes) |
| D5 | pit height | his wall-height rule (walls 20% above the head) is a **visual rule only**. The morning's "the deepest pit stays 2 m" was **REVERSED** the same day by his own question: colonists dig to 8 m by default, setting 2 to 20 m (by card) |
| art | wall band on wet canals (§4.2), darker deep-lake colours (§4.1) | **yes, but he sees it before it ships**: a review sheet or an in-game shot first (cosmetic permission gate) |

**Defaulted to this spec's recommendation, veto-able** (he did not rule these; each stands until he says otherwise):

| # | decision | default | his other option |
|---|---|---|---|
| D3 | burning | one rate per burning square, 0.5 m a day | keep a pond burning 5× slower |
| D4 | `sourceBudgetMultiplier` | delete it (it makes litres and metres disagree) | keep it, labelled "breaks the depth readout" |
| D6 | S5 redraw | both: a 2 m canal by gravity and a pump (done: scenes file re-sealed, S5 awaits his re-approval) | gravity only, or pump only |
| NS | the two north-star bars `fill_tier_legible` and `depth_and_fill_jointly_legible` | restated in metres in `design/validation_walks/RimMandrake/FlowWorks.md`; **he re-validates them** (hash-bound section) | keep the old "trace, half, brimming" wording |

## 11. Build items

Filed 2026-10-17 from this spec; the code is untouched until they run:

- `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD`: §7.2 code, defs, settings, strings and Python constants (Scheme A, D3, D4).
- `LAKE_FLOOR_TUNE_TEN_TO_FIFTY_METRES` (absorbed into P4): the 125 m ceiling setting; floor shape is `LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP` (R11).
- `WATER_DEPTH_RESKIN_HE_LOOKS_FIRST`: the wall band and the deep-lake tints; owner sees a sheet or in-game shot first.
- `WATER_SCENES_JUDGE_S5_REDRAWN` (BENCH, needs owner): re-approve S5; re-validate the two metre-worded north-star bars;
  keep or veto D3, D4 and D6.

All of these are children of `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` (one rebuild, ruled 2026-10-17); order and estimates:
`design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`.
