# FlowWorks water solver bakeoff: plan (2026-11-12)

Ledger item: `RIMMANDRAKE_SWEEP_WATER_SOLVERS_ON_BIG_MAPS`. Plan only; no solver code was written for it.
Source review (owner's document, copied unchanged): `design/RimMandrake/flowworks_water_solver_literature_review.md`.
Context: `design/specs/2026-11-12-flowworks-rivers-design.md` (design 7, the per-square level model),
`design/specs/2026-11-12-flowworks-natural-water-as-pits-feasibility.md`, and
`D:\ClaudeWork\rimmandrake\conductor\rivers_20261112\FINAL_REPORT.md` (same text as the rivers spec).

Owner, 2026-11-12: *"We'll likely want to do a bakeoff in Python first to check performance on realistic Rimworld map sizes
(I like to play on big maps) with rivers and lakes and oceans and even maybe waves."*

Rulings this plan works inside: water is true height and true decilitres only; natural water becomes filled pits with a bed map;
algorithms are swept offline in Python before any C#; no worldgen.

Every number is `[measured: where]` or `[guess ~N%]` (N = how sure I am).

## 1. What the review says, in five lines

1. Keep design 7's **bookkeeping** (bed height plus exact water per square, one shared transfer per edge, dams and weirs as edge
   rules, current read from the water that really crossed each edge). Do not yet pick its **engine**.
2. The engine should be chosen by measurement. The leading race is a **local-inertial** solver (each edge remembers its flow)
   against a **properly repaired** version of today's implicit solver, with a full shallow-water solver as the accuracy referee.
3. The 1,600 iterations per pulse are a property of one solver as written, not of the physics.
4. "Stable at any pulse length" is not "correct": the moat that fills in 625 s or 3,753 s depending on pulse length is a defect.
5. Speed-ups like coarse cells over a fine bed, sleeping settled water and tight memory layout are separate layers, measured
   one at a time after the engine is chosen.

## 2. What the shipped code does today (measured, so the bakeoff starts from fact)

| Part | What it is | Evidence |
|---|---|---|
| Dug bodies and ponds | Fill-and-spill: every connected body jumps straight to one level each pulse, exact to the dL. No flow, no travel time, no current. | `src/RimMandrake/FlowWorks/Source/RM_LevelSolve.cs` (749 lines) |
| Overland sheet water | Neighbour seeping, one fifth of the level difference per pass, then each puddle levelled | `RM_SheetMath.cs:480` (`diff / 5`), `:440` |
| Rivers | Printed current lanes, not computed from moved water | `Rivers/RM_MapComponent_RiverCurrent.cs` (696 lines) |
| Pulse | 250 ticks by default, settable 60 to 2,500 | `RimMandrakeFlowWorksMod.cs:50,1155`; `RM_FireMath.cs:49` |
| Square | 2 m², so 1.414 m across; 1 notch (0.5 m) of one square is 10,000 dL | `RM_LevelSolve.cs` header; twin `river_models.py:9` |

The design-7 twin (`D:\ClaudeWork\rimmandrake\conductor\rivers_20261112\py\implicit_v3.py`) nests three loops per pulse: an outer
re-linearising loop, a wet/dry loop (up to 25), and a conjugate-gradient solve with only a diagonal preconditioner (up to 4,000
iterations) [measured: `implicit_v3.py:28-52`]. A diagonal preconditioner on a long thin river needs roughly as many iterations as
the river is long, which fits the ~1,600 seen [guess ~70%]. That is the textbook case that line solves or multigrid fix.

**Factual correction:** the rivers spec and the review both say the twin ran on "100 x 100 squares". The code runs 250 long by
40 wide (10,000 squares, river 12 wide = 3,000 wet) [measured: `river_models.py:10`].

## 3. The candidates in plain words

Cost below is per wet square per solver step. "Step" for an explicit solver is one small time step; it must be short enough that a
wave cannot jump a square, so deep water needs more steps (the CFL limit: step ≤ about 0.5 × 1.414 m / √(9.81 × depth)).
That gives about 5 steps per river-second at 1.5 m depth, 14 at 10 m, 31 at 50 m (the lake-floor ceiling) [measured arithmetic;
50 m ceiling from the feasibility study, `RM_LakeFloorMath.cs`].

Unit costs measured on this machine (Intel Core Ultra 5 245K): numpy, one local-inertial step over an all-wet grid, 52 to 60 ns
per square; one conjugate-gradient iteration, 16 to 21 ns per square [measured:
`D:\ClaudeWork\rimmandrake\bench_solver_bakeoff\probe\probe_out.txt`, grids 250², 325², 400²]. Plain C, one local-inertial
step about 20 ns per square [measured: `...\rivers_20261112\py\bench_kernels_out.txt`].

### A. Local-inertial shallow water (Bates 2010, de Almeida 2012) — the review's first choice
Each edge keeps its flow from the last step. Each step: push it by the level difference, slow it by bed friction, move the water.
- Cost: a dozen sums per edge per step; no big system to solve. ~5 to 14 steps per river-second.
- Volume: exact if water moves only as edge transfers with a limiter that never lets a square go below empty.
- Tick rates: cannot take a 250-tick pulse in one step; needs many small steps, which can be spread over ticks (a few per tick).
- Rivers with real flux: good; this is what it was built for (floods, rivers, backwater behind a dam).
- Lakes: good when still (a lake at rest must stay exactly at rest, a must-test). Deep lakes force small steps.
- Oceans: fine if most of the sea is held level and only a shore band is simulated; the deep sea would set the step.
- Waves: carries slow surges and sloshing; not breaking bores or fast jets (it drops part of the momentum physics).
- Pits and bed maps: native (works on any bed height per square). Deep pits make steps smaller unless the still ones sleep.
- Player digs: very easy: change one bed height or one edge kind; nothing to rebuild.
- Weak at: fronts running out over dry ground and draining wet/dry edges (Cozzolino 2019); must be tested.

### B. Implicit diffusion wave (today's design 7, repaired)
Solve all levels together once per pulse from "flow follows slope and friction". No memory of flow.
- Cost: one large linear solve per pulse. Today ~1,600 iterations per pulse even when settled [measured:
  `out_implicit3_cg.txt`]. With warm starts, sleeping, a line solver or multigrid the review expects far fewer; UNMEASURED.
- Volume: exact (already 0 dL in all twin scenes) [measured: `out_implicit3_a.txt`].
- Tick rates: stays bounded at any pulse, but timing is wrong at long pulses (625 s against 3,753 s) [measured: `out_implicit3_e.txt`].
- Rivers: good levels and backwater; current read from flux works. Lakes: excellent (a calm lake costs nothing in steps).
- Oceans: fine as a held-level edge. Waves: none (no momentum, so no slosh and no surge).
- Pits: native; depth does not shrink the step, its main advantage over A.
- Player digs: the matrix and any cached preconditioner must be rebuilt for the touched body.

### C. Weighted cellular automaton (WCA2D / CADDIES, Guidolin 2016)
Each square hands water to lower neighbours in weighted shares, with a published rule for how much and how often.
- Cost: cheapest local rule; adaptive steps. Published: 3 to 5 times faster than a local-inertial code on one urban test
  (not a forecast for us).
- Volume: naturally bounded and exact if done as edge transfers.
- Rivers: levels fine; current is rougher (no momentum), worst in gaps and jets, which is where pawns get shoved.
- Lakes: good. Oceans: fine as held level. Waves: none. Pits: native. Digs: trivial.
- It is the fallback if filling and draining matter more than true current.

### D. Virtual pipes (O'Brien and Hodgins 1995)
Each edge is a pipe whose flow is pushed by the level difference. In practice this is A with game-engine coefficients instead of
published ones. Same behaviour as A; extra tuning burden. **Folded into A**, not a separate arm.

### E. First-order full shallow water, well-balanced (Audusse 2004 hydrostatic reconstruction)
The full momentum physics on the same grid.
- Cost: about 1.5 to 2.5 times A in one published comparison; same step limit. More code.
- Volume: exact with positivity-preserving fluxes. Lake at rest: exact by construction ("well-balanced").
- Rivers: best for dam breaks, breaches, jets, fronts on dry ground. Waves: the only candidate that carries real travelling waves
  and bores. Pits: native, deep pits cost small steps. Digs: easy.
- Role: the accuracy referee for the others, and the winner if its extra cost turns out small.

### Not solvers, but layers (measured later, one at a time)
- **Fill-spill-merge / today's fill-and-spill (`RM_LevelSolve.cs`):** equilibrium only. Use for the starting state of pits at map
  load and for still bodies that sleep as one node.
- **Coarse water cells over the fine bed (subgrid):** fewer unknowns for big calm lakes and sea; full detail at dams, gaps, digs.
  Never merge across a wall.
- **Sleeping and caching:** a steady river is not empty; it sleeps only when its flows are steady and its edges unchanged.
- **Memory layout:** flat arrays, skip dry squares; the review quotes 4 to 8 times from this alone (LISFLOOD-FP).
- **The owner's smoothing pass** (OWNER.jsonl 2026-11-12T21:30): allowed only as a conservative exchange between neighbours, so
  it becomes an optional damping term inside A, C or E and is scored by the weir jitter scene.

### Cut, and why
- **Kinematic wave:** no backwater, so a dam cannot raise the water behind it. Wrong for dams and pits.
- **Lattice Boltzmann:** not cheaper on a CPU, its own stability problems, no gain for us.
- **Neighbour seeping (design 2, today's sheet kernel):** 26,000 to 166,000 passes to settle [measured: `out_D.txt`].
- **Printed vectors (design 1):** currents wrong with player works [measured: `out_OPR.txt`].
- **The old wave prototype (design 4):** replaced by E, built from a published scheme and tested against textbook cases.

## 4. Shortlist for the bakeoff

| Arm | Solver | Why it is in |
|---|---|---|
| A | Local-inertial with coupled friction (de Almeida 2012) | The review's front runner; cheap steps, flow memory, easy digs |
| B0 | Design 7 as it is (`implicit_v3.py`, unchanged) | The baseline every number is compared with |
| B1 | Design 7 repaired: instrumented, warm start, residual sleep, then line solver or multigrid | The serious implicit contender, strongest for deep still water |
| C | WCA2D | The cost floor: if C passes everything that matters, nothing dearer is needed |
| R | First-order well-balanced full shallow water | Referee for accuracy, the only route to simulated waves, possible winner |

Four candidates plus the baseline. One variable changes at a time: no arm gets coarse cells or new boundary rules during the race.

## 5. Bakeoff design

### 5.1 Map sizes
RimWorld offers 200, 225, 250, 275, 300 and 325 squares a side; with the dev option "test map sizes" also 350 and 400
[measured: decompiled `Dialog_AdvancedGameConfig.cs:12-14`]. The owner's 613-mod list has no map-size mod
[measured: `deployed/config/ModsConfig.before-tier-kineticarms.xml`, parsed]. Every one of the 198 owner saves whose map size I
read is 250 × 250; the other 184 saves were not read [measured: header scan of the Saves folder, 2026-11-12].

Sizes raced: **250** (what he plays now), **325** (largest normal), **400** (largest the game can make; 160,000 squares).

Wet load per size, from the 70-save census on 250 maps (river map 13,271 wet, coast 12,329, marsh 14,515)
[measured: feasibility study 4.1], scaled up:

| Load | 250 | 325 | 400 |
|---|---|---|---|
| River map (rivers grow with map width) | 13,300 | 17,300 [guess ~60%] | 21,200 [guess ~60%] |
| Coast map (sea grows with area) | 12,300 | 20,800 [guess ~50%] | 31,600 [guess ~50%] |
| Stress: half the map wet | 31,250 | 52,800 | 80,000 |

### 5.2 Scenes (one bed and forcing file each, identical for every arm)
1. **Lake at rest** on a rough bed, closed: nothing may move. Tests false floods and drift.
2. **River**: plain 12-wide river along the grid and at 45 degrees; 3-square gap; weir; full dam closed and opened mid-run.
3. **Lake fed by the river**: the river runs through a natural lake made as a filled pit from a bed map (3,000 squares, 6 m).
4. **Ocean edge**: coast map, sea held level beyond a shore band; river mouth into it; a dug canal from sea to an inland pit.
5. **Dam break**: wet-bed and dry-bed, against the textbook answer (SWASHES Stoker and Ritter cases).
6. **Pit fill and player digs**: a 300-square 3 m moat filled by a dug canal; a trench dug into a running river mid-run; a dam
   built in deep water (displaced water must be pushed, never deleted).
7. **Settled river for 10,000 pulses**: the cost of a river nobody touches.
8. **Ledger fuzz**: 1,000 random dig, dam and demolish sequences.
9. **Swell (waves, only if cheap)**: the sea edge rises and falls 0.3 m every 8 s. At 10 m depth the wave is about 56 squares long,
   at 1 m about 18, so the grid can show it [measured arithmetic]. Run for A and R only (B and C carry no waves).

### 5.3 Metrics, per scene, arm and size
- **Python cost**: ms per river-second, steps and iterations counted [measured, numpy].
- **Projected C# cost per tick**: counted steps × measured C cost per square-step × a C#/C factor of 1.2 to 2 [guess ~50%; fixed by
  one C# console timing in stage C of the rivers plan]. The projection uses counts from Python and unit cost from compiled C,
  never Python wall time, because numpy time is mostly numpy overhead.
- **Volume**: committed dL error (must be 0) and the uncommitted fractional residue.
- **Settle time**: river-seconds until levels change under 1 mm per pulse, and CPU spent getting there.
- **Timing truth**: moat fill time and dam-break front arrival when the step is halved and cut by ten.
- **Hydraulics**: discharge against the Manning hand formula, weir against its formula, 45-degree error, lowest depth ever,
  limiter activity.
- **Frames**: one depth-plus-current image per scene at fixed times, all arms side by side, judged blind by an rm-judge pass;
  only a contested scene goes to the owner.

### 5.4 Pass bars (proposed; the cost lines are guesses until stage C)
| Bar | Line |
|---|---|
| Books | 0 dL over 100,000 pulses and all 1,000 fuzz sequences; no square ever below empty |
| Lake at rest | under 1 mm movement over 10,000 river-s, 0 dL change |
| Discharge | plain channel within 2% of hand formula; 45 degrees within 10% target, 20% fail line |
| Weir | within 5% of formula; jitter under 1 mm |
| Timing | fill time and front arrival change under 10% when the step is halved |
| Dam break (A, R) | front position within 10% of the textbook answer |
| Settled cost | under 5% of disturbed cost |
| Cost at 400 × 400, projected C# | realistic map under 0.5 ms per tick on average; 50%-wet stress under 2 ms per tick; settled under 0.05 ms per tick [guess ~40% that these are the right lines; the game tick is 16.7 ms at speed 1] |

### 5.5 What the arithmetic says before any run
With one river-second per 60 ticks (the rivers design assumed this; not a ruling) [measured: `01_designs.md:191`]:
- A on the 400 river map: 21,200 squares × 30 ns × 5 steps per river-s ÷ 60 ≈ 0.05 ms per tick [guess ~50%].
- A on the 400 stress load with 10 m water: 80,000 × 30 ns × 14 ÷ 60 ≈ 0.6 ms per tick [guess ~50%].
- B0 on the 400 river map: 1,600 iterations × 21,200 × ~5 ns ≈ 0.17 s per pulse, more if the iteration count grows with river
  length as I expect [guess ~50%]. That is the number B1 must beat.
- Python wall time for the whole race at 400: an all-wet step is 9 ms [measured: probe], so a 10-river-minute dam break for A is
  about 8,400 steps or 76 s; B0 at 1,600 iterations × 3.4 ms is about 5.5 s per pulse [measured unit cost, guess counts].
  The full matrix fits in one night of compute.

### 5.6 Where it lives, how long it takes
- Code: `src/RimMandrake/FlowWorks/Tools/solver_bakeoff/` (one file per arm behind one `advance(dt)` interface, shared scenes and
  scorer). Results and frames: `D:\ClaudeWork\rimmandrake\flowworks_solver_bakeoff\`.
- Order: harness, scenes and scorer first (with B0 reproducing its published numbers), then A and R, then B1, then C.
- Effort: harness and scenes 1.5 agent-days, A 1.5, R 1.5, B1 1.5, C 1, runs, frames and report 1: **about 8 agent-days**
  [guess ~50%], plus one GPT skeptic pass on the scorer (measurement machinery) before any result is trusted.
- Output: a winner and a runner-up, with the cost table at 250, 325 and 400, ready for stage C (offline C# console).

## 6. Choices for the owner (for the Conductor's question card)

1. **Water clock: how much river time passes per game tick?**
   (a) one river-second per real second at speed 1 (60 ticks) — today's assumption; (b) water tied to game time (a game hour of
   flow per game hour, about 86 times more work); (c) (a) plus an automatic slow-down when the game is under load (his own
   "only slowly updating" idea). Recommend **(c)**. Trade: (b) is the most "true" to the calendar but multiplies every cost by
   about 86 [measured arithmetic: 86,400 game-s per 60,000-tick day ÷ 1 s per 60 ticks]; (c) costs least and slows water, not frames.
2. **Waves: a goal, or drawn only?**
   (a) drawn surge only (cheapest; any arm can win); (b) the bakeoff runs the swell scene and simulated waves become a feature if
   A or R carries them inside the cost bar. Recommend **(b)**: it costs about one scene, and the result decides.
3. **Which map size must pass?**
   (a) 250, what all his read saves use; (b) 325, the largest normal size; (c) 400, the dev "test map sizes" ceiling.
   Recommend **(c)**: he says he likes big maps; racing at 400 costs only compute time.
4. **When two arms pass, which wins: the cheapest or the most physical?**
   (a) cheapest that passes (likely C or A); (b) most physical that fits the cost bar (likely A or R). Recommend **(b)**:
   the projected costs leave room, and better currents and waves are what the player sees. Trade: (b) is more code and more risk
   at wet/dry edges.

## 7. Instructions found inside the review (treated as data, not acted on)

The document addresses agents directly in three places; none was carried out as an order:
- §0: "Do not yet commit to design 7 as the final numerical engine." (consistent with this plan; recorded as the review's advice)
- §11 "Benchmark plan for Claude Code" and §11.1 to §11.5 (used as input to section 5 above, adapted).
- §14 "Suggested immediate task for the next Claude session": instrument implicit v3 and build a de Almeida twin in parallel.
  This plan schedules the same work through the ledger item instead.
