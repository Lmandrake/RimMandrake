# FlowWorks natural water: which solver, and the water clock (2026-11-12)

Item: `RIMMANDRAKE_SWEEP_WATER_SOLVERS_ON_BIG_MAPS`. Inputs: the plan `design/plans/2026-11-12-flowworks-water-solver-bakeoff.md`
(published 19e26c039250), the MandrakeModels bakeoff (`~/dev/MandrakeModels`, github Lmandrake/MandrakeModels, results at
fad3ee1 and later: `results/results.md`, `results/crosscheck.md`), the rivers report
`design/specs/2026-11-12-flowworks-rivers-design.md`, and the owner's rulings of 2026-11-12 quoted in section 2.
Owner questions: `D:\ClaudeWork\rimmandrake\conductor\water_models_20261112\QUESTIONS.md`.

Tags: [measured] = run by a harness and readable on disk; [guess ~N%] = my estimate with rough confidence.

## 1. Recommendation in six lines

1. **Engine: local-inertial shallow water** (Bates 2010, de Almeida 2012; MandrakeModels `local_inertial`), on design 7's
   bookkeeping: whole decilitres per square, one shared transfer per edge, current read off the water that crossed each edge.
2. **Referee and runner-up: first-order full shallow water** (`swe_hll`): the only arm that carries real bores and
   dam-break fronts, about 2.5 times the cost of local-inertial [measured, numpy, section 4].
3. **Two clocks.** Flow runs at eye speed (one water-second per 60 ticks at game speed 1, so water moves at a natural pace
   on screen). The slow terms (evaporation, groundwater, edge refill, rain, season, drought) run on the calendar, once per
   pulse per body, as booked volume changes. Water that has settled sleeps.
4. **Every natural boundary is a forcing term, not a solver feature**: map-edge cells as sources, sinks or level-setters,
   groundwater seeping from a per-map table, evaporation from biome wetness, temperature and Direct Sun. All four exist in
   the MandrakeModels base class and act identically under every solver [measured: `src/mandrakemodels/base.py`
   `apply_forcing`]; the solver only decides how fast their effect spreads.
5. **Cut:** game cellular automaton, WCA2D (flood fronts 10 to 30 times late, worse on bigger maps), kinematic wave (no
   backwater), both diffusion-wave CG and explicit forms (cost), lattice-Boltzmann shallow water (cost). Virtual pipes is
   kept only as the cheap fallback if the C# timing of local-inertial misses the bar.
6. **Next:** a C# console timing of local-inertial on integer decilitres at 250 and 325 (stage C), then the owner's water
   clock answer fixes the pass bar.

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
  | pipes | 1.42 | 0.77 | 0.58 |
  | swe_hll (referee) | 1.12 | 0.42 | 0.26 |
  | diffusion_wave_implicit_adi | 1.48 | 0.37 | not run |
  | wca2d | 0.66 | 0.08 | 0.01 |
  | ca_game | 0.20 | 0.01 | 0.002 |

  They spread a fixed number of squares per pass, so a bigger map (more squares between river and pit) is slower in
  water-seconds. Their low cost buys water that arrives late, and later on the maps the owner likes.

## 4. The survivors, side by side

Cost columns are the median over the 9 water scenes of the bakeoff, full grid (every square stepped, wet or dry, no sleeping),
one water-second per 60 ticks. Python is [measured] numpy on this machine under shared load (load 7 to 34 on 14 cores).
C# is MandrakeModels' projection: numpy time divided by the measured numpy/numba ratio, times a Mono factor of 1.5 to 4
[guess ~50% that the true C# figure lands inside the range].

| solver | Python ms/tick 250 | 325 | C# ms/tick 250 | 325 | dam-break water vs referee | volume |
|---|---|---|---|---|---|---|
| local_inertial | 0.40 | 0.82 | 0.11 to 0.30 | 0.23 to 0.61 | 1.48 x (early) | exact [measured] |
| swe_hll | 1.16 | 2.89 | 0.20 to 0.52 | 0.49 to 1.30 | 1.00 (reference; ANUGA agrees to 0.2%) | exact |
| pipes | 0.54 | 1.21 | 0.02 to 0.06 | 0.05 to 0.12 | 1.59 x | exact |
| diffusion_wave_implicit_adi | 1.38 | 3.02 | 0.23 to 0.62 | 0.51 to 1.35 | 1.55 x | exact |
| wca2d (cut) | 0.44 | 0.86 | 0.07 to 0.20 | 0.15 to 0.39 | 0.09 x (late) | exact |
| ca_game (cut) | 0.06 | 0.13 | 0.01 to 0.03 | 0.02 to 0.06 | 0.03 x (late) | exact |

Sources: `~/dev/MandrakeModels/results/results.csv` (medians computed from it), `results.md` "Flood timing" and
`crosscheck.md`. Pipes looks cheapest in C# because its numpy/numba ratio was 39 against 5.3 for local-inertial
[measured, `results.md` probe table]: the numba local-inertial kernel is the less optimised one [guess ~60%], so the
true gap is probably smaller.

**Realistic load, not full grid.** A river map at 250 has about 13,300 wet squares [measured: 70-save census in the
plan], 21% of the grid. Stepping wet squares only, local-inertial in C# is about 13,300 × 18 ns (numba, measured) × 1.5 to 4
(Mono) × 0.088 steps per tick ≈ **0.03 to 0.09 ms per tick at 250**, and about **0.04 to 0.11 at 325** with 17,300 wet
squares [guess ~50%; the 325 wet count is itself a guess ~60%]. Deep water shortens the step: a 6 m lake needs 0.11 s
steps, a 50 m lake 0.04 s (about 3 times the work of the 6 m lake) [measured arithmetic, CFL 0.6]; capping depth at 2 m in the
wave-speed term gave the same answer in the rivers twin [measured, 01_designs], and settled lakes sleep.

What each looks like (stills at 128, `D:\ClaudeWork\mandrakemodels\compare\stills\`, looked at 2026-11-12, notes in
`LOOKED.md` of the output folder):
- **local_inertial**: reads as water everywhere; faint striping in deep water just behind the dam-break gap.
- **swe_hll**: the cleanest picture; sharp dam-break front and its reflected arc.
- **pipes**: a checkerboard ripple over the whole lake in the draining-lake scene and along the river; it never quite
  settles to a mirror.
- **diffusion_wave_implicit_adi**: smooth and slightly blurred; no fronts.
- **wca2d, ca_game**: water mounds and sprays at the river inlet; floods creep.

What each cannot do:

| | rivers | edge sources, sinks, level-setters | pits and canals | FlowWorks pit/canal system already shipped |
|---|---|---|---|---|
| local_inertial | yes; no momentum advection, so fast jets through a gap are softened (valid below Froude ~0.5) | yes (shared forcing) | yes; pit fills with true travel time | replaces fill-and-spill for any body joined to natural water; fill-and-spill stays for the starting state at map load and for sealed still bodies |
| swe_hll | yes, including bores and hydraulic jumps | yes | yes | as local_inertial, at about 2.5 times the cost |
| pipes | yes, but a 1 cm sheet accelerates like a 3 m channel: spills on the flat plain run too fast | yes | yes, with slosh that rings | as above |
| implicit ADI | yes, big steps; but in the design-7 implicit twin (its cousin) fill time depended on step length (625 s vs 3,753 s) | yes | yes | the only arm that could run flow on the calendar clock, at the highest per-step cost |

Today's shipped FlowWorks (`RM_LevelSolve.cs` fill-and-spill, `RM_SheetMath.cs` neighbour seeping, printed river currents,
250-tick pulse, `RM_TerrainWriteBudget` capping picture writes at 200 per tick) is the frame the engine plugs into, not a
rival: the picture budget and the decilitre ledger stay; the printed current and the seeping sheet kernel go.

## 5. The water clock (first owner question)

Two speeds anchor the question [measured arithmetic]: at game speed 1 the game runs 60 ticks per real second, and the
calendar runs 60,000 ticks per 86,400 game seconds (1.44 game seconds per tick). Water that moves at a natural pace on
screen therefore runs **86 times slower than the calendar**.

- **Eye-speed flow, calendar budget (recommended).** Flow runs at one water-second per 60 ticks, so water pours, spreads and
  drains at the pace the eye expects at speed 1 (and faster at speed 2 and 3, like everything else). In calendar terms a
  basin that would fill in 10 real minutes takes about 0.6 game days. Evaporation, groundwater, edge refill, rain, season and
  drought follow the calendar, booked once per pulse per body. Cost: section 4, about 0.03 to 0.11 ms per tick at 250 to 325
  for local-inertial on wet squares [guess ~50%]. Between solver steps (one every ~12 ticks) the player sees the last state;
  terrain looks change only when a square crosses a depth band, within today's 200-writes-per-tick budget.
- **Calendar flow.** A game hour of flow per game hour: a dug canal fills its moat in game minutes, which at speed 1 looks
  like fast-forward. Cost about 86 times the above: 3 to 7 ms per tick for a river map at 250 [guess ~50%], over the
  0.5 ms line. Only an implicit solver with long steps could approach it, and those smear timing.
- **Pulsed levels (today's shipped way).** Solve once per 250-tick pulse and jump to the result: cheapest, but water moves in
  visible steps every ~4 real seconds and has no current between pulses.
- **Automatic slow-down (a safety valve, not a choice).** Whichever clock he picks, under heavy load the flow clock slows
  rather than the frame rate dropping (his own "only slowly updating" idea, plan option 6.1c). Recommended as built-in.

## 6. Other open choices (in QUESTIONS.md, recommendation first)

- **Waves:** drawn only (local-inertial plus the `linear_wave` visual layer), or simulated (full shallow water, about 2.5
  times the cost). Recommend drawn.
- **Map size the cost bar must pass:** 250, 325 or 400. Recommend 325 with 400 measured but not binding.
- **Groundwater both ways:** the table refills a body below it; should a body above it also seep away (a dry-biome pond
  leaks into the ground as well as evaporating)? Recommend yes, slowly. The MandrakeModels model seeps up only today.

## 7. What is not yet known

- C# cost: every C# figure here is a projection; the stage-C console timing on integer decilitres is the next measurement.
- Fixed-point stability of local-inertial: UNMEASURED.
- The 400 row: full-grid medians are in `results.md` (local-inertial 1.49 Python ms/tick, C# 0.42 to 1.12 guess); a
  wet-only figure at 400 is not computed.
- Python timings were taken on a loaded machine; an idle re-time is owed in MandrakeModels.
