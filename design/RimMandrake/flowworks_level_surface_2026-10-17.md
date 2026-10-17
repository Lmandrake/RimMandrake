# A level water surface: ruling audit and design (PROPOSAL, 2026-10-17)

Item: `WATER_SURFACE_REPAIR_LEVEL_OR_BUST` (superseded by `WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES`). **RULED 2026-10-17
(by card):** Q1 (a) exactly level; Q2 (b) a new very-shallow look under 25 cm; Q4 (a) redraw S5; Q5 (a) one rebuild;
Q6 (a) the level north-star bar (owner said). Q3 was answered by ordering the elevation review. Digging is no longer
capped at 2 m (8 m by default). Build plan: `design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`. Before the rulings this was a proposal. Nothing in code, defs, the bridge or the game was
touched to write this, and no existing doc was changed. It sits beside the ruled depth spec
`design/RimMandrake/flowworks_unified_depth_2026-10-17.md` and proposes re-opening one part of it (the step that water
*amounts* move in). Code claims are file:line from a read-only census of `src/RimMandrake/FlowWorks` at `f1168b0c2`.
One independent outside read (GPT, `gpt_consult.py`, model gpt-6.1-sol, job `consult-20261017-094812-3247232`) is kept
verbatim beside this file as `flowworks_level_surface_2026-10-17.gpt_read.md`. It was given the problem blind (no
recommendation), and it is evidence, not authority. Its arithmetic was re-checked here. This is one design pass plus one
outside read, **not a full Deep-Design-3x3**.

The owner, 2026-10-17: *"We need VERY smooth water. That's water's one primary characteristic: a level surface. So
let's get there ASAP, and any previous ruling that's in the way needs to be re-examined. If we end up needing a finer
resolution of water depth than the four levels, so be it. But let's show that. Right now I'm seeing 0,4,0,0,4 patterns
in places that show the water isn't even flowing at all, so let's certainly fix that first."*

---

## Summary (one page)

**Two problems, not one.**

1. **A bug: water that does not flow** (whole squares 0, full, 0). Another helper is fixing it in the kernel now. It is
   the first thing to land, and it is necessary but **not sufficient**.
2. **A limit in the rules: whole half-metre steps cannot make a level surface.** Every square holds a whole number of
   0.5 m notches. Give 9 flat squares 26 notches of water: the best possible answer is eight squares at 1.5 m and one at
   1 m. That is a **half-metre step in the surface**, even with no bug at all. The true level answer is **1.44 m in all
   nine** (26,000 L ÷ 18 m²). A 0.1 m step shrinks the error to 10 cm. It never removes it.

**The finding that matters most:** the rulings did not ask for whole-notch water. The owner ruled *"litres are the
truth"* (D1, 2026-10-17) and *"It should slosh around until it levels"* (D2, 2026-10-16). Whole-notch water came from
agent-written engine text ("the engine still moves whole notches"; "lowered by whole notches"; "a sort plus an
overflow... an integer comparison"). No owner sentence forbids a level surface. **Two owner-approved things do need
re-examining:** the scene S5 bounds ("never all ten canal cells wet"), which are artefacts of whole notches, and the
pictures (four bands), which can show depth but not a continuously moving shoreline.

**Recommendation: keep the half-metre step for DIGGING and for PICTURES; stop using it for WATER.**

- Each connected body of water (a pond, a canal, or both joined) holds its water as an exact whole number of
  **decilitres** (tanks and hoses already do), and has **one surface height**, worked out from that volume and the
  floors under it.
- Every square's water depth = surface − its floor, computed when read. Every square of one body therefore sits at
  exactly the same surface. Level to well under a millimetre, by construction.
- Digging stays in 0.5 m steps (to 8 m by default since the same day's ruling). Floors and lakebeds stay as they are. Saves keep their grids.
- Pictures are water bands chosen by water depth in metres: a new very-shallow look under 25 cm (ruled), then the four. Over a flat floor, every square shows the **same**
  picture, so the water **looks** level too. A smooth shaded surface is a later, cosmetic step he sees first.
- The readout shows the real figure: "Hole 2 m · Water 1.44 m (2,889 L)" (feeds `DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE`).

**What changes for the player (worked):** a full 3×3, 2 m pond joined to a ten-square 0.5 m canal now levels to one
surface 26 cm below ground: the pond stands 1.74 m deep and **all ten canal squares are wet, 24 cm each**. Today's rules
say "at most nine wet, never all ten". One full pond square joined to the same canal wets all ten at 4.5 cm.

**Cost (ESTIMATED, not measured):** 4 to 7 agent-days, mostly the solver, the save migration, re-pointing every
"whole notch" reader, and the selftests and Python oracle. The 0.1 m step (Scheme B) costs about the same, and still
leaves 10 cm steps. **Decisions for the owner:** six cards at the end (§7).

---

## 1. Why whole steps cannot be level (the arithmetic)

Share W notches over N squares on one flat floor: W = N·q + r. The best split gives r squares q+1 notches and the rest
q. Unless r = 0, neighbouring surfaces differ by one whole step.

| case | whole 0.5 m notches | whole 0.1 m steps | one surface, exact litres |
|---|---|---|---|
| S6 pond: flat 3×3, 2 m, 26,000 L | 8 at 1.5 m, 1 at 1.0 m (**0.5 m step**). Live today: 6 full, 3 dry (the bug, worse still) | 4 at 1.5 m, 5 at 1.4 m (**0.1 m step**) | **1.444 m everywhere** |
| full 3×3 pond (36,000 L) + ten 0.5 m canal squares | at most 9 canal squares wet, each brim-full or dry | 9 pond + 10 canal share 9 steps' worth unevenly | surface −0.263 m: pond 1.737 m, **every canal square 0.237 m** |
| one full pond square (4,000 L) + same canal | at most 1 canal square wet | 2 or 3 squares at 0.1 m | surface −0.455 m: **all ten wet at 4.5 cm** |
| 26,000 L pond + canal floored 0.5 m down | no flow | no flow | no flow: surface 0.56 m down sits below the canal floor (correct) |

Checked by hand: 36,000 = 2,000 × [9(h + 2) + 10(h + 0.5)] gives h = −5/19 m. 4,000 = 2,000 × [(h + 2) + 10(h + 0.5)]
gives h = −5/11 m. The outside read reached the same numbers independently.

## 2. Every ruling and constraint in the way

**Key:** **BLOCKS** = forbids a level surface as written. **RE-EXAMINE** = owner-approved text that a level surface
changes. **CONSTRAINS** = holds, and shapes any solution. **NEUTRAL** = supports it, or is untouched. OV = owner
verbatim, CARD = by question card, AP = agent prose. Census: read-only, 2026-10-17.

| # | where | date | what it says | kind | verdict |
|---|---|---|---|---|---|
| 1 | ledger `WATER_SURFACE_REPAIR_LEVEL_OR_BUST` | 10-17 | *"We need VERY smooth water... a level surface... any previous ruling that's in the way needs to be re-examined"* | OV | **governs** |
| 2 | ledger `WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND` note | 10-16 | *"levelset down to a smooth 0 or 1 across a too-wide field like this, not 0, deep, 0"* | OV | NEUTRAL (asks for level) |
| 3 | same item | 10-16 | "How should water spread between neighbouring squares? → Level by water surface" | CARD | NEUTRAL (asks for level) |
| 4 | `pond_depth_design_2026-10-16.md:106-108`; ledger `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` | 10-16/17 | *"It should slosh around until it levels, pond or canal or otherwise."* "One flat level, flowing through the mouth." | OV + CARD | NEUTRAL (the law this design fulfils; the mouth pace stays) |
| 5 | `flowworks_unified_depth_2026-10-17.md:32-40` (D1) | 10-17 | "litres are the truth, metres are the ruler, and the step is 0.5 m... **The engine still moves whole notches**" | CARD for Scheme A; the whole-notch engine line is AP | **BLOCKS (the AP part only).** "Litres are the truth" is kept and is what this design builds on. The step stays for digging and pictures. |
| 6 | same, §8 and :297-299 | 10-17 | Scheme B (0.1 m) is "the right later step **if** leveling still looks lumpy"; costed 5-8 days | AP | RE-EXAMINE: §1 shows B still leaves 10 cm steps; the cost "×5 flow work" comes from moving one unit at a time, which a bulk solve avoids |
| 7 | same, §9 | 10-17 | "Grids (`depthGrid`, `fillGrid`, `bedRecord`): unchanged; a notch stays 0.5 m." | AP | CONSTRAINS: `depthGrid` and `bedRecord` stay; `fillGrid` becomes a derived view (§4) |
| 8 | same :9-13 (owner's write-in) | 10-17 | *"It's ok to have some number of visual depths of liquid... we must not get confused on the depth of the water."* | OV | CONSTRAINS: banded pictures are allowed; the readout must give one true depth |
| 9 | `liquid_litres_2026-10-16.md:9, 17, 42-44` | 10-16 | "The kernel stays in whole notches. Canal and pit cells hold whole notches (`fillGrid`)." | AP | **BLOCKS** |
| 10 | `flowworks_mod_definition.md:928-936` (§21 "THE ALGORITHM") and ~:903 | 09-16 | "fill lowest first, then overflow... a sort plus an overflow... an integer comparison"; depth is "a cell carrying an integer"; "head-height flow" called scope creep | AP | **BLOCKS**, and partly STALE: the 10-16 slosh ruling (row 4) already overrode "no head-height flow" |
| 11 | same :894-897 (ruling 19) | 09-16 | *"Four depths: shallow 0.5 m, mid 1 m, deep 1.5 m, SUPERDEEP 2 m"* | OV (summary) | NEUTRAL: it is about how deep you **dig**, which stays |
| 12 | `pond_depth_design_2026-10-16.md:12-17, 66-84` | 10-16 | "one flat water surface per pond, **lowered by whole notches**... The last part-level is laid as one connected patch... The fraction below one level stays in `stock` and shows nothing" | AP | **BLOCKS**. Source of the 0.5 m step in a drawn pond |
| 13 | same :44, and `flowworks_mod_definition.md:159-166` | 10-16, 09-16 | "Recession sheds whole squares... dry one more, shallowest bed first" | AP | **BLOCKS**. Source of 6-full-3-dry. Still the live path when `pondDepthEnabled` is off |
| 14 | `design/validation_walks/RimMandrake/FlowWorks.md:41` (pond bar) | 10-17 | "the last part-level is one connected patch" | AP (bar text) | **BLOCKS**: rewrite to "one surface" |
| 15 | scenes `water_scenes_2026-10-16.scenes.json` S5.a/b/c/i (~:414-470) | 10-17, **awaiting re-approval** (`WATER_SCENES_JUDGE_S5_REDRAWN`) | "never all 10", "at most 9", "cells 1-4, never a 5th", pond keeps "27,000 L" | AP, owner to approve | **RE-EXAMINE**: these are whole-notch artefacts (§1). Under a level surface all ten are wet. Re-draw before he approves the old numbers. |
| 16 | `water_scenes_for_approval_2026-10-16.md:~17-30`; scenes JSON `units` | 10-16/17 | "A level is one notch of depth. It is 1,000 L."; "a dug cell of legend depth D is D notches" | AP | **BLOCKS** the vocabulary; restate in litres and metres |
| 17 | scenes JSON G1-G3 (:20-47) | 10-17 | G2 "0 ≤ fill ≤ depth"; G3 total never rises, falls only by disclosed overflow | AP, approved scenes | CONSTRAINS (conservation; holds as litres) |
| 18 | scenes S6.Q1 (owner verdict) | 10-17 | "the same totals and the same end state; small differences on the way are fine" | CARD | NEUTRAL: a level solve passes it |
| 19 | `flowworks_mod_definition.md:174-188, 201, 560` | 09-16 | Overflow is *"the ONLY sanctioned place"* liquid leaves without being spent | OV (summary) | CONSTRAINS: exact litre conservation, `ReportOverflow` kept |
| 20 | ledger `POND_BED_DESIGN_LAKES_ARE_TALL_CANALS`; `POND_VOLUME_UNIFY_EVERY_SQUARE_HOLDS_FOUR` | 10-12 | *"1 tank square, 1 deep water square/pond, 1 deep canal square should all be the same volume."* *"pumping water between two equal-volume reservoirs through a tank gets you the same water in the end"* | OV | CONSTRAINS (volume parity, conservation): both hold |
| 21 | ledger `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` | 10-17 | "Should still ponds lose water to the sun? → No, only people and plants use water up" | CARD | CONSTRAINS (no evaporation) |
| 22 | unified spec D3 (:215, :329) | 10-17 | "one rate per burning square, 0.5 m a day" | AP, defaulted, veto-able | CONSTRAINS: restate as litres per day per square; unchanged in meaning |
| 23 | unified spec D4 | 10-17 | delete `sourceBudgetMultiplier` | AP, defaulted | NEUTRAL (helps: litres map straight to metres) |
| 24 | `FlowWorks.md:155-157` `fill_tier_legible` | 10-17 restated | "dry, and water 0.5 m, 1 m, 1.5 m and 2 m or more deep, are distinguishable from each other by looking" | AP, **hash-bound, owner re-validates** | CONSTRAINS: four bands kept. Needs one more sentence for water under 0.5 m (§7 Q2) |
| 25 | `FlowWorks.md:170-173` `depth_and_fill_jointly_legible` | 10-17 | same water depth in different holes, and different water in the same hole, all distinguishable | AP, hash-bound | CONSTRAINS: holds (bands by water depth; walls by hole depth) |
| 26 | `FlowWorks.md` (whole north star) | — | **no bar asserts a level surface** | — | GAP: propose `water_surface_level` (§7 Q6) |
| 27 | `pond_depth_design_2026-10-16.md:195-223` | 10-16 | "under 10 ms a pulse added"; terrain restages capped by `pondStageWritesPerPulse` (400) | AP | CONSTRAINS (perf, write cap) |
| 28 | `flowworks_mod_definition.md:126-128`; `:566-584` ruling 7 | 09-16 | "One fill-unit = enough... to fill one canal cell"; *"5 days (5:1 density argument)"* | AP / OV | STALE (already replaced by litres and D3) |

**Net:** every BLOCKS row is agent prose about the engine. No owner sentence forbids a level surface. The owner-facing
items that need his word are row 15 (S5's bounds, not yet re-approved), row 14 and 26 (north-star text), and row 24 (one
more picture state).

## 3. Options

All three keep: digging in 0.5 m steps (then to 2 m; now to 8 m by default); natural floors in 0.5 m steps (to the ruled 20/50/125 m); litres as the
truth; the mouth pace ("flowing through the mouth", row 4); conservation and the single overflow; pumps pouring 1,000 L.

### Option 1 — One surface per body, exact litres (RECOMMENDED)

- **Holds:** each connected body of water (pond, canal region, or both joined) has its volume as a whole number of
  decilitres, and one surface height derived from it. Per-square depth = max(0, surface − floor), computed on read.
  A per-cell 16-bit litre view (125 kB) can be cached for fast readers; it is never summed back into the books.
- **Solve:** histogram of floor heights in the body (at most ~250 levels, since floors are 0.5 m steps), then find the
  height where Σ area × (H − floor) = volume. O(squares) to build, O(levels) to solve; cached while the shape does not
  change. Water moves between bodies by surface difference at the mouth, paced as ruled.
- **The hard part (from the outside read, confirmed by reasoning):** "connected" must mean connected **below the
  surface**. Two basins joined only above the water line must not share a height. As a pond drops, a body may split; as it
  rises, two may merge. The existing band merge tree (`RM_FlowKernel.cs:936-1000`) already knows which squares connect at
  which band, so it is the place to get this from.
- **Conservation:** integer decilitres per body; transfers are integer. Exact, as tanks and hoses are today.
- **Pictures:** four bands by water depth (nearest band; a level body over a flat floor shows one picture everywhere).
  Under 0.5 m needs a ruling (§7 Q2). Terrain only re-writes when a square crosses a band.
- **Saves:** add a body-volume record and a model marker. Old `fillGrid` × 10,000 dL, old pond `stock` × its saved unit;
  log each body's before and after. `depthGrid` and `bedRecord` are untouched.
- **Cost (ESTIMATED): 4 to 7 agent-days.** Risk: body split and merge; every whole-notch reader (§5) re-pointed at once.
- **Dominates when:** the owner means "level" literally, now. It is the only option that is exactly level.

### Option 2 — Finer fixed step everywhere (0.1 m or 1 cm per square)

- **Holds:** a 16-bit water grid in 0.1 m (200 L) or 1 cm (20 L) units per square. Digging and floors stay 0.5 m.
- **Solve:** the existing band solve, made bulk (quotient plus remainder per band) so it is not 5× slower: "five times
  the flow work" was a property of moving one unit at a time, not of the step.
- **Level:** within 10 cm or 1 cm. Never exact: the remainder still piles on some squares.
- **Cost (ESTIMATED): 4 to 6 days** (close to Option 1: the same readers change), plus the spec's own 5-8 day figure if
  the old one-unit-a-move kernel is kept. It is the smallest change to the kernel's shape.
- **Dominates when:** a 1 cm staircase is invisible to him and keeping the per-square kernel matters more than exactness.

### Option 3 — Keep half-metre water; smooth only the look

- Fix the 0/4/0 bug (in hand), then draw a smooth surface over the true half-metre steps (spread the remainder in the
  picture only).
- **Cost: 1 to 2 days.** But the readout and the picture disagree with the water (one square really holds 1 m, its
  neighbour 1.5 m), canals still never wet thinly, and S5 still says "never all ten". **This is the confusion he ruled
  against** (row 8: *"we must not get confused on the depth of the water"*). Listed for honesty; not recommended.

(A fourth, from the outside read: whole basins linked by channels with flow limits. It is Option 1 plus a link layer,
and worth it only if instant levelling across a long canal looks wrong. Keep in reserve.)

| | 1. one surface, exact | 2. finer step | 3. smooth look only |
|---|---|---|---|
| level surface | exact | within 10 cm or 1 cm | no (0.5 m steps underneath) |
| readout matches picture | yes | yes | **no** |
| S5 all ten wet thinly | yes | partly | no |
| save change | body volumes added | water grid widened | none |
| cost (ESTIMATED) | 4-7 days | 4-6 days | 1-2 days |
| main risk | bodies splitting and joining | leftover staircase; kernel and oracle re-tuned | it is a lie that he will see |

## 4. Recommendation and order of work

**Option 1.** Order, given "ASAP":

1. **The 0/4/0 kernel fix lands first** (other helper, in hand). Add a diagnostic that reports the largest surface
   difference inside each connected body, in metres, so "level" is a number before it is a picture.
2. **Ponds first, offline.** Ponds already hold a float stock; drop the floor-to-whole-notch step
   (`RM_BedMath.SupportedLevels`, `RM_PondDepthMath.Drawdown/WaterAt/PickPatch`) and derive one exact surface. This alone
   turns the S6 pond from 6-full-3-dry into nine squares at 1.44 m. Smallest step that **shows** him a level surface.
3. **Canals and joins:** body volume in decilitres; the level solve returns a height, not whole notches per square.
4. **Readers and saves:** pumps, burn, heat, drowning, mouseover, Level Holder, migration with a logged audit.
5. **Show him** in a staged save (S5 redrawn, S6 pond), with the readout and the diagnostic numbers.
6. **Fold in `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD`.** Both rewrite `RM_Volume`, `FillTier`, the mouseover and the
   Python oracle constants. Two passes over the same files is waste (§7 Q5).

**What would change this:** if a 1 cm staircase is shown to be invisible in game and Option 2 ships in clearly less
time, take Option 2. If instant levelling down a long canal looks wrong to him, add the basin-link layer.

## 5. What a change would hit

**Items (rimflow):**

| item | state (ledger, 2026-10-17) | effect |
|---|---|---|
| `WATER_SURFACE_REPAIR_LEVEL_OR_BUST` | open, FOUNDRY | this design is its plan |
| `WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND` | open, BENCH (built offline, not deployed) | superseded in part by the surface solver; close on landing |
| `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` | open, BENCH (built offline, live L8 owed) | its "whole notches, one patch" core is replaced; mud timer, occupant wait and toggles kept |
| `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD` | open, FOUNDRY | fold in (§4 step 6); its "notch" constants stay for digging |
| `DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE` | open, FOUNDRY | readout gets the true figure; format to two decimals |
| `WATER_DEPTH_RESKIN_HE_LOOKS_FIRST` | open | adds the thin-water look if Q2 picks new art |
| `WATER_SCENES_JUDGE_S5_REDRAWN` | open, BENCH, owner | **hold**: S5's bounds change again; re-draw before he approves |
| `LAKE_FLOOR_TUNE_TEN_TO_FIFTY_METRES` | open | unaffected (floors stay 0.5 m steps) |
| `LEVELSET_DIAGNOSE_SHALLOW_RIM_STAYS_DRY` | closed `c82dd1c08f55` | its fix is folded into the new solver; keep its test |

**Code (`src/RimMandrake/FlowWorks/`):**

- Truth and solve: `Source/RM_FlowKernel.cs` (`LevelSetWetRegions` :798, merge tree :936-1000, `Assign` :1117-1142,
  `PickBand` :1150-1210, `Superdeep` :123, the band loop :640-710, `HeadAllows`), `Source/RM_PondDepthMath.cs`
  (:78-221), `Source/RM_BedMath.cs` (`SupportedLevels` :109-116, `ShouldShed`/`CanRestore` :121-140),
  `Source/RM_LiquidStock.cs` (`StagePond` ~:826-930, `Recede`/`Restore` ~:942-990, `TryDebit` :429, `CreditLevels` :484),
  `Source/RM_LiquidBody.cs` (`stock` float :109-113), `Source/RM_StockMath.cs`, `Source/RM_Volume.cs`.
- Grids and saves: `Source/RM_MapComponent_Excavation.cs` (`fillGrid` :52, Scribe :688-709, `TryTakeLevel` :1821,
  `TryPourLevel` :1840, fill terrain :2264-2292, rain accumulator :2198).
- Readers of whole notches: `Source/LiquidTypes/Building_LiquidPump.cs` (:114-351), `Source/RM_PumpMath.cs`,
  `Source/RM_FireMath.cs` + `Source/RM_LiquidFire.cs` (burn), `Source/RM_LiquidHeat.cs:117` +
  `Source/RM_LiquidHeatMath.cs:39-47`, `Source/RM_FillEffectMath.cs:19`, `Source/RM_MouseoverDepth.cs`,
  `Source/MapControls/RM_LevelHolder.cs`, `Source/RM_ExcavationDepth.cs` (`FillTier` :113), `Source/RM_LiquidLooks.cs`,
  `Source/FluidDef.cs:139-158`, `Source/Drilling/*` (reserve units), `RimMandrakeFlowWorksMod.cs` (settings).
- Tests: `Source/SelfTest/LevelSetChecks.cs`, `PondDepthChecks.cs`, `FlowKernelFuzz.cs`, `SequenceFuzz.cs`,
  `PumpChecks.cs`, `PondReturnChecks.cs`, `TransferChecks.cs`; Python `selftest_flowworks_kernel_oracle.py`,
  `northstar/selftest_conservation_roundtrip.py`, `northstar/pond_pump.py`, `northstar/liquid_checks.py`
  (`levelset_verdict`, `pond_depth_verdict`). The oracle must change in lockstep with the kernel.

**Docs to correct once he rules** (not touched now): `flowworks_unified_depth_2026-10-17.md` (D1's "engine moves whole
notches", §6, §8, §9); `liquid_litres_2026-10-16.md`; `pond_depth_design_2026-10-16.md` §0, §2; `flowworks_mod_definition.md`
§21 and recession; `design/validation_walks/RimMandrake/FlowWorks.md` (pond bar; new level bar, hash-bound, his to
validate); `vv_methods/water_scenes_2026-10-16.scenes.json` + `water_scenes_for_approval_2026-10-16.md` (S5, `units`).

**Saves:** every save holding FlowWorks grids or pond bodies migrates once on load (model marker). Staged review saves
for S5 and S6 must be rebuilt after the change. Back up the Saves folder before the first load.

## 6. Things not to lose

- The mouth pace (row 4, ruled): one surface **eventually**, water visibly travelling. Option 1 levels each body at
  once but moves water between bodies at the mouth's pace.
- Pumps keep 1,000 L pours. On nine wet squares that is a 5.6 cm jump per pour. Fine; smaller pours are a later tuning.
- No game rule may read the terrain picture as the amount of water (pictures lag by up to a few pulses).

## 7. Decisions for the owner (question-card wording)

**Q1. How level must water be?**
- (a) **Exactly level: every square of connected water stands at the same height. The readout shows the true depth,
  e.g. 1.44 m.** *Recommended: the only choice that is truly level; 4 to 7 days.*
- (b) Level to within 1 cm (or 10 cm). Slightly smaller change to the engine; a tiny step may remain.
- (c) Keep half-metre steps underneath and only smooth the picture. 1 to 2 days, but the picture and the readout can
  disagree with the water.

**Q2. Water shallower than half a metre (say 24 cm in a canal): what do you see?**
- (a) **The knee-deep look as soon as there is a few centimetres of water; the readout gives the real depth.**
  *Recommended: no new art, and a thinly wet canal reads as wet.*
- (b) A new, very shallow look for under 25 cm (new art: you see it before it ships).
- (c) Dry-looking below 25 cm, wet in the readout only.

**Q3. Pictures beyond the four depth looks?**
- (a) **Not yet: keep the four looks (0.5, 1, 1.5, 2 m and deeper). Level water over a flat floor shows one look
  everywhere. You judge it in game first.** *Recommended: fastest to show you.*
- (b) Build a smooth, shaded water surface now (cosmetic; you see it before it ships).

**Q4. Scene S5 said "at most nine canal cells wet, never all ten". With level water, all ten get wet, 24 cm each.
Redraw S5 with the level numbers before you approve it?**
- (a) **Yes, redraw S5 with level-water numbers.** *Recommended: the old numbers came from the half-metre steps.*
- (b) Keep S5 as drawn.

**Q5. The metres-and-litres rewiring you ruled this morning touches the same code. One rebuild or two?**
- (a) **One: fold it into this work.** *Recommended: the same files, one migration, one look for you.*
- (b) Two: finish the metres rewiring first, then level water.

**Q6. Add a north-star bar: "every square of connected still water stands at the same surface height (to within 1 cm),
read from the game, not the picture"?**
- (a) **Yes.** *Recommended: nothing in the north star tests the one thing you named as water's main trait.*
- (b) No.
