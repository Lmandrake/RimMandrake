# RIMMANDRAKE_SWEEP_WATER_SOLVERS_ON_BIG_MAPS

## spec
Offline Python bakeoff of FlowWorks water solvers before any C#. Plan, shortlist, scenes, metrics and pass bars:
`design/plans/2026-11-12-flowworks-water-solver-bakeoff.md`. Input review (owner's document, unchanged):
`design/RimMandrake/flowworks_water_solver_literature_review.md`. Arms: A local-inertial (de Almeida 2012, coupled friction),
B0 design 7 unchanged (`D:\ClaudeWork\rimmandrake\conductor\rivers_20261112\py\implicit_v3.py`), B1 design 7 repaired
(instrumented, warm start, sleep, line solver or multigrid), C WCA2D, R first-order well-balanced full shallow water.
Sizes 250 / 325 / 400 (game max with dev test sizes, decompiled Dialog_AdvancedGameConfig.cs:12-14).
Code: `src/RimMandrake/FlowWorks/Tools/solver_bakeoff/`; results `D:\ClaudeWork\rimmandrake\flowworks_solver_bakeoff\`.

## done when
A report names a winner and runner-up with the cost table at 250/325/400 (Python ms measured; C# per tick projected from step
counts x compiled-C unit cost) and every pass bar of plan section 5.4 scored per arm, with frames judged blind.

## watch out
- Owner choices in plan section 6 (water clock, waves, size bar, tie rule) shape the pass bars; the Conductor cards them.
- The twin grid is 250 x 40, not 100 x 100 as the rivers spec says (river_models.py:10).
- The scorer is measurement machinery: GPT skeptic pass before trusting any result. One variable per experiment.
- Unit-cost probe so far: `D:\ClaudeWork\rimmandrake\bench_solver_bakeoff\probe\probe_out.txt` (cost shape only, not a solver).
