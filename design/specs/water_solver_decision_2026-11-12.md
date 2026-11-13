# FlowWorks natural water: which solver, and the water clock (2026-11-12)

Item: `RIMMANDRAKE_SWEEP_WATER_SOLVERS_ON_BIG_MAPS`. Inputs: the plan `design/plans/2026-11-12-flowworks-water-solver-bakeoff.md`
(published 19e26c039250), the MandrakeModels bakeoff (`~/dev/MandrakeModels`, github Lmandrake/MandrakeModels, results at
fad3ee1 and later: `results/results.md`, `results/crosscheck.md`), the rivers report
`design/specs/2026-11-12-flowworks-rivers-design.md`, the owner's rulings of 2026-11-12 quoted in section 2, and the stage C
C# measurement (`~/dev/MandrakeModels/results/stagec.md`, MandrakeModels f61afdb; item
`RIMMANDRAKE_TIME_LOCAL_INERTIAL_IN_CSHARP_FIGURES_STILL_GUESSES`).
Owner questions: `D:\ClaudeWork\rimmandrake\conductor\water_models_20261112\QUESTIONS.md`.

Tags: [measured] = run by a harness and readable on disk; [guess ~N%] = my estimate with rough confidence.

**Updated 2026-11-13 by the stage-2 review (`RIMMANDRAKE_HARDEN_FAST_WATER_SOLVERS_VIA_GPT_PIPES_RING`; MandrakeModels
`results/stage2.md`, 252407e): the winner is refined, not changed.** The engine is local-inertial **with every face
discharge capped at the critical-flow (weir) value, face Froude 0.544** (`local_inertial_frcap`): plain local-inertial floods
early, and the cap puts it on the referee's schedule at the same cost. Virtual pipes is no longer a fallback.

## 1. Recommendation in six lines

1. **Engine: local-inertial shallow water with a Froude 0.544 face cap** (Bates 2010, de Almeida 2012; MandrakeModels
   `local_inertial_frcap`), on design 7's bookkeeping: whole decilitres per square, one shared transfer per edge, current read
   off the water that crossed each edge. Without the cap floods arrive early (dam-break water 1.48 x the referee; pit 0.72 m
   vs 0.42 at 128); with it 1.09 x and 0.44 m (0.26 vs 0.26 at 250), at the same cost, for 12% less river water delivered
   to the outfall [measured, `results/stage2.md`]. No cap value keeps both within 15% and 5% (0.6 to 0.7 swept).
2. **Referee and runner-up: first-order full shallow water** (`swe_hll`): the only arm that carries real bores and
   dam-break fronts, about 3 to 4 times the cost per tick of local-inertial [measured, numpy, section 4].
3. **Two clocks.** Flow runs at eye speed (one water-second per 60 ticks at game speed 1, so water moves at a natural pace
   on screen). The slow terms (evaporation, groundwater, edge refill, rain, season, drought) run on the calendar, once per
   pulse per body, as booked volume changes. Water that has settled sleeps.
4. **Every natural boundary is a forcing term, not a solver feature**: map-edge cells as sources, sinks or level-setters,
   groundwater seeping from a per-map table, evaporation from biome wetness, temperature and Direct Sun. All four exist in
   the MandrakeModels base class and act identically under every solver [measured: `src/mandrakemodels/base.py`
   `apply_forcing`]; the solver only decides how fast their effect spreads.
5. **Cut:** game cellular automaton, WCA2D (flood fronts 10 to 30 times late, worse on bigger maps), kinematic wave (no
   backwater), both diffusion-wave CG and explicit forms (cost), lattice-Boltzmann shallow water (cost), and virtual pipes:
   its pipe size ignores depth (a 1 cm film runs 8.8 times its Manning speed; the river holds 54% of the referee's water),
   and its claimed compiled-cost edge rested on a probe kernel without friction [measured, stage-2 review]. Theta smoothing
   (`pipes_theta`) removes its ringing on screen but not its early floods.
6. **Stage C measured it:** on RimWorld's own Mono, local-inertial on integer decilitres costs **0.163 ms per tick on a
   realistic 325 river map** (bar 0.5: pass), 1.45 ms on the 50%-wet stress (bar 2: pass), books exactly 0 dL [measured,
   section 4a]. Two things the game build must carry: each 12-tick recompute splits into equal substeps (a ragged split makes
   the scheme slosh), and the recompute's work is spread over its 12 ticks (it is a spike otherwise). Settled water does not
   sleep yet, so the settled bar fails. These are figures for the uncapped scheme; the cap adds one multiply and one
   square root per wet face (numpy cost unchanged within noise [measured]; C# UNMEASURED).

## 2. The owner's rulings this has to obey

- Edge lakes, 2026-11-12: *"(3) because rivers will require this same work (boundary areas that are sources, sinks, or
  level-setters)"* = finite, refilling slowly from the map edge.
- Wet-biome lakes: *"(1) finite, but they will have high groundwater levels (faster refill) plus abundant rain"*.
- Drought and evaporation: *"even on a river tile, if the player fills a moat and then closes it, we want evaporation to
  shrink it absolutely. So yes. But evaporation rate should be calculated by wet/dry biome, temperature, and direct sunlight
  exposure"*.
- Day one: *"Seasonal level, and when a Drought is declared, this can also be effected by effectively lowering the
  groundwater level hence the refill rate from below"*.
- Elevation, 2026-11-12 3:18 PM PST: *"Ok, so no >0 elevation will be pursued. It is official."* Every bed is at or below
  ground; water lives in pits, channels and dug works, and an overflow spreads as a thin sheet on a flat plain.
- Exposed lakebeds (idea, 2:59 PM PST): water that recedes reveals a gently deepening bed that is muddy, wet, then dries.

What follows from them for the solver:
- The flat plain at 0 makes **thin sheets on flat ground** a common case (every spill). That is where pipes runs too fast
  (its pipe size ignores depth) and full shallow water carries noisy speeds in films; local-inertial is built for it
  (it is the LISFLOOD-FP floodplain model) [guess ~75%].
- Receding water must leave a clean wet/dry edge (the exposed lakebed). Every surviving arm handles wet and dry squares
  with exact volume [measured: every water arm conserves to 1e-14 relative or better, `results/results.md`]; the mud, dying
  plants and drying ground are a terrain layer on top, not solver work.
- Rivers on a world with no ground above 0 are channels cut below ground and driven by **the levels held at the two map
  edges**, not by a hill. Held levels at both ends were stable in every rivers-twin run [measured: rivers report, 01_designs].

## 3. What changed in the evidence today

- **The bakeoff's pit-dig scene never flooded.** Its canal was cut a fixed 2 m into a bank that climbs away from the river,
  leaving a sill above the river: all 60 pit-dig rows measured a dry pit. Fixed (canal bed now falls from the river bed to
  the pit, pit nearer), with a test that fails on the old scene for all 7 solvers it can run and passes on the fix
  [measured: MandrakeModels 03ba39e; `D:\ClaudeWork\mandrakemodels\pitfix\test2_on_base.log`]. Pit-dig rows re-run.
- **The moat scene did not visibly dry** (0.24 m off 1.5 m). It now tilts and evaporates at an exaggerated 15 mm/s, so the
  shallow side goes dry on camera; test fails 7/7 on the old scene, passes on the new [measured: fad3ee1].
- **The cellular automata get later as the map grows.** Pit mean depth at 150 s after the fix [measured,
  `D:\ClaudeWork\mandrakemodels\pitfix\after2_*.txt`]:

  | solver | 64 cells | 128 | 250 |
  |---|---|---|---|
  | local_inertial | 1.55 m | 0.72 | 0.49 |
  | local_inertial_frcap (stage 2) | 1.30 | 0.44 | 0.26 |
  | pipes | 1.42 | 0.77 | 0.58 |
  | swe_hll (referee) | 1.12 | 0.42 | 0.26 |
  | diffusion_wave_implicit_adi | 1.48 | 0.37 | not run |
  | wca2d | 0.66 | 0.08 | 0.01 |
  | ca_game | 0.20 | 0.01 | 0.002 |

  They spread a fixed number of squares per pass, so a bigger map (more squares between river and pit) is slower in
  water-seconds. Their low cost buys water that arrives late, and later on the maps the owner likes.

## 4. The survivors, side by side

Cost columns are the median over the 9 water scenes of the bakeoff, full grid (every square stepped, wet or dry, no sleeping),
one water-second per 60 ticks. Python is [measured] numpy on this machine under shared load (load 7 to 34 on 14 cores). Only
local-inertial has been ported to C#; its measured C# cost is section 4a. No other solver has a C# figure.

| solver | Python ms/tick 250 | 325 | dam-break water vs referee | volume |
|---|---|---|---|---|
| local_inertial_frcap | 0.37 | 0.75 | 1.09 x | exact [measured] |
| local_inertial | 0.40 | 0.74 | 1.48 x (early) | exact |
| swe_hll | 1.19 | 2.53 | 1.00 (reference; ANUGA agrees to 0.2%) | exact |
| pipes (cut) | 0.49 | 1.04 | 1.59 x | exact |
| pipes_theta (visual only) | 0.57 | 1.14 | 1.56 x | exact |
| diffusion_wave_implicit_adi | 1.38 | 3.02 | 1.55 x | exact |
| wca2d (cut) | 0.51 | 1.62 | 0.09 x (late) | exact |
| ca_game (cut) | 0.06 | 0.12 | 0.03 x (late) | exact |

Sources: `~/dev/MandrakeModels/results/results.csv` (medians computed from it), `results.md` "Flood timing" and
`crosscheck.md`; refreshed at MandrakeModels 252407e, after stable_dt was timed with the step (wca2d's cost roughly doubled).

Deep water shortens the step: a 6 m lake needs 0.11 s steps, a 50 m lake 0.04 s (about 3 times the work of the 6 m lake)
[measured arithmetic, CFL 0.6]; capping depth at 2 m in the wave-speed term gave the same answer in the rivers twin
[measured, 01_designs].

### 4a. Local-inertial in C#, measured (stage C, 2026-11-13)

A standalone console port (`~/dev/MandrakeModels/csharp/`, not mod code): water an int per square in dL, one double discharge
and a sub-dL rounding residue per face, integer donor limiter, every face moving whole dL once with opposite signs. Clock as
the owner chose it: a recompute every 12 ticks (0.2 water-s), in CFL substeps. Wet-only stepping in 16x16 blocks gives
bitwise the same water as the full grid. Runtime: **RimWorld's own Mono** (the game's `mono-2.0-bdwgc.dll` and
`RimWorldWin64_Data\Managed`, "Mono 6.13.0"), hosted outside Unity, single thread [measured]; in-game cost is likely within
+30% of these figures because the game's main thread shares the cache [guess ~70%].

Fidelity against the Python reference (tolerances fixed before the first run): 40 of 40 checkpoint rows pass on river,
lake at rest, pit dig, dam break and swell at 128 and 250; worst relative depth difference 1e-4, books 0 dL [measured;
planted faults in Manning and theta turn 16 and 32 rows red].

Mean ms per tick, wet-only, Unity Mono (the recompute's cost over its 12 ticks; p95 within 15% of the mean) [measured]:

| load | wet squares 250 / 325 / 400 | 250 | 325 (binding) | 400 | bar (plan 5.4) |
|---|---|---|---|---|---|
| realistic river map (sized to the 70-save census) | 13,178 / 17,121 / 21,094 | 0.123 | **0.163 pass** | 0.206 | 0.5 ms |
| 50%-wet stress, up to 10 m deep, swelling edge | 32,462 / 53,853 / 79,656 | 0.855 | **1.452 pass** | 2.154 (over) | 2 ms |
| settled lake (nothing moving; no sleeping built) | 24,873 / 38,553 / 63,314 | 0.573 | **0.859 fail** | 1.376 | 0.05 ms |
| swell scene (79% wet, 8 m) | 48,564 / 83,686 / 126,113 | 1.340 | 2.316 | 3.585 | none |

- **Equal substeps, or it sloshes.** Splitting a recompute as full CFL steps plus a short remainder (0.17 s, then 0.03 s)
  made the lake at rest slosh 2.1 m within 20 water-s, in Python float64 as well as in C#; with equal substeps the C# lake moves
  0.2 mm over 10,000 water-s [measured, `D:\ClaudeWork\mandrakemodels\stagec\drift\`].
- **Fixed-point stability passes:** books 0 dL over 100,000 recomputes (river at 250, 20,000 water-s) and over 1,000 fuzz
  sequences (50,037 random digs, earth dams, walls and demolitions); no square ever below empty; swell, dam break, pit dig
  and the stress scene stay finite for 2,000 water-s [measured]. The fuzz found and fixed one bug (forcing wrote into a square
  walled over a source, which a demolish then deleted).
- **The recompute is a spike:** unspread, its whole cost lands in one tick: 1.9 ms on the 325 river map, 17 to 20 ms on the
  325 stress load (a whole 16.7 ms frame) [measured]. The game build must spread each recompute's substeps or blocks over the
  12 ticks.
- **Mono is about 3 times .NET 8** on this kernel (2.1 to 4.9 by scene; .NET Framework 4.8 is 2% to 38% slower than .NET 8)
  [measured]; tightening the face loop for Mono (no bounds checks or edge tests, cheaper cube root) gained about 5%.

What each looks like (stills at 128, `D:\ClaudeWork\mandrakemodels\compare\stills\`, looked at 2026-11-12, notes in
`LOOKED.md` of the output folder):
- **local_inertial**: reads as water everywhere; stripes in the dam-break reservoir upstream of the gap (wall reflections it
  never damps; the first-order referee damps them).
- **local_inertial_frcap** (looked at 2026-11-13, `LOOKED2.md` beside the stage-2 review): looks like local_inertial; its pit
  fills on the referee's schedule; the reservoir stripes stay (the cap never binds in slow water).
- **swe_hll**: the cleanest picture; sharp dam-break front and its reflected arc.
- **swell scene**: reference, local-inertial, pipes and ANUGA all show swell bands bending through the breakwater gap; the
  cellular automata and implicit ADI show a flat sea (no waves at all).
- **pipes**: a checkerboard ripple over the whole lake in the draining-lake scene and along the river; it never quite
  settles to a mirror. `pipes_theta` removes it in every scene (looked at 2026-11-13).
- **diffusion_wave_implicit_adi**: smooth and slightly blurred; no fronts.
- **wca2d, ca_game**: water mounds and sprays at the river inlet; floods creep.

What each cannot do:

| | rivers | edge sources, sinks, level-setters | pits and canals | FlowWorks pit/canal system already shipped |
|---|---|---|---|---|
| local_inertial (capped) | yes; no momentum advection, so it is capped at critical flow on each face: floods on time, but a fast steep reach delivers ~12% less than the referee | yes (shared forcing) | yes; pit fills with true travel time | replaces fill-and-spill for any body joined to natural water; fill-and-spill stays for the starting state at map load and for sealed still bodies |
| swe_hll | yes, including bores and hydraulic jumps | yes | yes | as local_inertial, at about 3 to 4 times the cost |
| pipes | yes, but a 1 cm sheet accelerates like a 3 m channel: spills on the flat plain run too fast | yes | yes, with slosh that rings | as above |
| implicit ADI | yes, big steps; but in the design-7 implicit twin (its cousin) fill time depended on step length (625 s vs 3,753 s) | yes | yes | the only arm that could run flow on the calendar clock, at the highest per-step cost |

Today's shipped FlowWorks (`RM_LevelSolve.cs` fill-and-spill, `RM_SheetMath.cs` neighbour seeping, printed river currents,
250-tick pulse, `RM_TerrainWriteBudget` capping picture writes at 200 per tick) is the frame the engine plugs into, not a
rival: the picture budget and the decilitre ledger stay; the printed current and the seeping sheet kernel go.

## 5. The water clock (first owner question)

Answered by card 2026-11-12 22:52 PST (as relayed in the stage C brief): the natural on-screen clock, recomputed every 12 ticks,
with the slow terms on the calendar.

Two speeds anchor the question [measured arithmetic]: at game speed 1 the game runs 60 ticks per real second, and the
calendar runs 60,000 ticks per 86,400 game seconds (1.44 game seconds per tick). Water that moves at a natural pace on
screen therefore runs **86 times slower than the calendar**.

- **Eye-speed flow, calendar budget (recommended).** Flow runs at one water-second per 60 ticks, so water pours, spreads and
  drains at the pace the eye expects at speed 1 (and faster at speed 2 and 3, like everything else). In calendar terms a
  basin that would fill in 10 real minutes takes about 0.6 game days. Evaporation, groundwater, edge refill, rain, season and
  drought follow the calendar, booked once per pulse per body. Cost: section 4a, 0.123 ms per tick at 250 and 0.163 at 325
  for local-inertial on a realistic river map, wet squares only, on RimWorld's Mono [measured]. Between solver steps (one every
  ~12 ticks) the player sees the last state;
  terrain looks change only when a square crosses a depth band, within today's 200-writes-per-tick budget.
- **Calendar flow.** A game hour of flow per game hour: a dug canal fills its moat in game minutes, which at speed 1 looks
  like fast-forward. Cost about 86 times the above: about 11 ms per tick for a river map at 250 and 14 at 325 [measured cost
  times 86, arithmetic], far over the 0.5 ms line. Only an implicit solver with long steps could approach it, and those smear timing.
- **Pulsed levels (today's shipped way).** Solve once per 250-tick pulse and jump to the result: cheapest, but water moves in
  visible steps every ~4 real seconds and has no current between pulses.
- **Automatic slow-down (a safety valve, not a choice).** Whichever clock he picks, under heavy load the flow clock slows
  rather than the frame rate dropping (his own "only slowly updating" idea, plan option 6.1c). Recommended as built-in.

## 6. Other open choices (in QUESTIONS.md, recommendation first)

Answered by the same card 2026-11-12 22:52 PST: swell plus drawn chop (no full shallow water in game); 325 must pass and 400
is measured but not binding; groundwater both ways.

- **Waves:** local-inertial already carries swell and its diffraction through a breakwater gap, much like the reference
  (swell still at 27 s, looked at 2026-11-12); full shallow water adds breaking bores and hydraulic jumps at about 3 to 4
  times the cost. Recommend local-inertial swell plus a drawn chop layer (MandrakeModels `linear_wave` or a shader).
- **Map size the cost bar must pass:** 250, 325 or 400. Recommend 325 with 400 measured but not binding.
- **Groundwater both ways:** the table refills a body below it; should a body above it also seep away (a dry-biome pond
  leaks into the ground as well as evaporating)? Recommend yes, slowly. The MandrakeModels model seeps up only today.

## 7. What is not yet known

- In-game cost: section 4a ran RimWorld's Mono outside Unity; the in-game figure is UNMEASURED.
- Settled water sleeping and spreading a recompute over its 12 ticks are not built; the settled bar fails until the first is.
- No solver other than local-inertial has been ported to C#.
- All nine water scenes were re-rendered at 128 with the stage-2 competitors and looked at (2026-11-13); the other-physics
  pages were not re-rendered.
- The Froude cap is not in the C# port yet; stage C's figures are for the uncapped scheme.
- Python timings were taken on a loaded machine; an idle re-time is owed in MandrakeModels.
