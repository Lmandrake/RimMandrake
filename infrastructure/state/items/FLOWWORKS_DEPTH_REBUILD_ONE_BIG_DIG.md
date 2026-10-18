## spec
Plan: `design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md` (ordered packages P1-P10, ESTIMATED agent-days,
dependency order, risks, veto-able defaults V1-V8, what he must look at). Design inputs:
`flowworks_level_surface_2026-10-17.md`, `flowworks_elevation_feasibility_2026-10-17.md`,
`flowworks_elevation_play_2026-10-17.md`, `flowworks_unified_depth_2026-10-17.md` (all in `design/RimMandrake/`).
Ticket consolidation (every FlowWorks item and its verdict): `design/RimMandrake/flowworks_ticket_consolidation_2026-10-17.md`.

Owner rulings 2026-10-17 (ledger notes on this item, `--by-card`): R5 dig 8 m default, 2-20 m setting; R6 one big
rebuild; R7 the four 2 m-keyed rules relative; R8 real elevation (T4) dead. R9 (owner said, `OWNER.jsonl` tsn
1792258162801304562): the level-surface north-star bar, now written into
`design/validation_walks/RimMandrake/FlowWorks.md` as `still_water_one_surface_height`.
R8 amended 2026-10-18 (owner said): pawns may walk UNDER the new FlowWorks span structures (the walk-under
"bridges", building type) — *"only for these new bridges uniquely, NOT actual tunnels."* Everything else in R8 stands.

## the shared acceptance language (every child uses it)
- **Stock:** each connected still body holds an exact whole number of decilitres; nothing is created or lost.
- **Level:** one surface height per connected body (connected below the surface); every square of it reads the same
  surface to within 1 cm, from game state, never from the picture.
- **Readout:** hole depth and water depth as two figures, water volume in litres in parentheses
  (default form "Hole 7 m (ledge 4 m) · Water 2.37 m (4,740 L)").
- **Very shallow:** water under 25 cm has its own look (new art, his look first).
- **Dig depth:** colonists dig to 8 m by default; a Mod Setting from 2 to 20 m; 0.5 m step.
- **Relative rules:** drowning, fall damage, spikes and shooting key on height differences, never on "2 m deep".

## children, in dependency order
| plan | item | needs | after |
|---|---|---|---|
| P1 | `WATER_SCENES_PROVE_AFTER_THE_CREEP_FIX` | deploy | `WATER_SCENES_WALK_MEND_TRIPS_AFTER_S4` |
| P2 | `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH` | bridge | none (gates SHIPPING P5) |
| P3 | `WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES` (absorbed `WATER_SURFACE_REPAIR_LEVEL_OR_BUST`, `WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND`, `KERNEL_SELFTEST_WIRE_SHIPPED_TUPLE_NEVER`) | offline | none; folds in `WATER_NATURAL_DECIDE_ONE_SURFACE` when it lands |
| P4 | `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD` (absorbed `LAKE_FLOOR_TUNE_TEN_TO_FIFTY_METRES`, `LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS`) | offline | same pass as P3 |
| P5 | `PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT` | offline | P3+P4; ships only after P2 passes |
| P6 | `DIG_COST_TUNE_DEEP_IS_A_MEGAPROJECT` | offline | inside P5's pass |
| P7 | `PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE` | offline | P5 (lands with it) |
| P8 | `DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE` | offline | P3 |
| P9 | `VERY_SHALLOW_WATER_RESKIN_HE_SEES_FIRST` + `WATER_DEPTH_RESKIN_HE_LOOKS_FIRST` (+ `CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES`) | offline, then his look | any time; one review |
| P10 | this epic: integration, S5 redrawn, staged save, deploy, full live walk | deploy + bridge | P1-P9 |
| owner | `WATER_SCENES_S5_JUDGE_THIRD_DRAFT` (replaced `WATER_SCENES_JUDGE_S5_REDRAWN`), `FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING`, `DEPTH_DEFAULTS_ASK_ELEVEN_VETOES`, `DEPTH_QUESTIONS_ASK_RAIDERS_FIRST`, `WATER_NATURAL_DECIDE_ONE_SURFACE` | owner | cards any time; S5 and bars after P10 |

## verify
1. Every child closed.
2. L2: in game, every square of each connected still body reads one surface height within 1 cm (state read, not picture):
   `src/RimMandrake/FlowWorks/northstar/level_surface_bar.py` (stub today, `validation.py` chain `water_level_surface`)
   made real on P3's per-body surface-gap diagnostic, run live and recorded with modcheck.
3. L2: the 4/7/7/4 square digs, fills as one level body, holds by the relative climb rule, and reloads identically.
4. L2: S5 redrawn with level numbers and re-sealed; S2, S5 and S6 of `northstar/water_scenes_walk.py` run live and match.
5. L4: he has looked at the one art review (P9) and the staged save (S5, S6 pond, 4/7/7/4 square, each with readout and
   surface-gap diagnostic), and re-validated the north-star section (`FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING`).
