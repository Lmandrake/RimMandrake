# FlowWorks 0.1.0 — in-game acceptance, visit 6

Driver: detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_SIX, game b on Archmagi.
Ran 2026-11-21 11:05 PM to 2026-11-22 12:30 AM PST (bound 2:05 AM).

Why this visit: commit 65c45b6e98 changed the inferno deck rule (RM_LiquidFire, RM_FuelFireMath) and the pit prisoner's
food (RM_PitRoomMath, RM_PitPrisonCare). `rerun_relation.py` named 8 of 31 checks as touched [measured]; the brief adds
OL_OWNER_LOOK_READS.

## Build and list

- Game b (its own install, `D:\ClaudeWork\rimmandrake\instances\b\game`). FlowWorks deployed in sync at 65c45b6e98: the
  dry run read "in sync (1038 files)" [measured]. No mod code changed in this visit.
- List: the 13-mod flowworks tier (modset_builder.py, all five DLC), written to game b's own ModsConfig with the game down,
  then game b relaunched (bridge up after 28 s). Every row carries `build_match.py identity --tier flowworks`.

## Results [measured]

| check | verdict (last row) | runs | notes |
|---|---|---|---|
| sc_hole_prison | PASS | 3 | three PASS in a row; each run's awake prisoner (3 tendable wounds) got DeliverFood |
| sc_toss_flame | PASS | 1 | |
| sc_moat_raid | PASS | 1 | |
| sc_pit_trap_raid | PASS | 1 | |
| sc_pit_reads | PASS | 1 | extension_proof plot_G_pit: 7 PASS, calm site CLEAN |
| sc_canal_fire | PASS | 1 | calm site loaded and verified first |
| sc_hung_bridge | **FAIL** (last row PASS) | 6 | 3 FAIL, 3 PASS; two MOD lines, both filed, below |
| sc_walk | UNMEASURED | 0 | game b: tier list only beside game a; game a runs it later |
| OL_OWNER_LOOK_READS | UNMEASURED (visit 4 row) | 0 | not run, below |

### sc_hung_bridge: two MOD lines, not fixed in the sitting

1. **SB_islands_restore_reach**, FAIL in 3 of 6 proof runs and 2 of 4 diagnostic runs (`diag_reach.py`, which logs the
   worker's job and needs at every 500-tick wait). Read directly (diag_reach_3): the worker holds RM_FillInCanalJob with its
   gravel carried, stands beside the square at (172,225), and does no work for 15000 ticks. The tip toil never ran (the
   gravel is still carried). Theory, unproven: JobDriver_FillInCanal's `GotoCell(A, Touch)` never completes from a
   diagonal stand square; no bridge call reads the toil. Not caused by needs: in diag_reach_2 the worker starved (food 0)
   and lay down while the fills still landed. Filed: `RIMMANDRAKE_UNSTICK_FLOWWORKS_FILL_JOB_HOLDS_GRAVEL_BESIDE_THE_HOLE`
   (acceptance test: five diag_reach runs with no stalled job).
   - The proof now tops up the worker's food and rest before each fill (staging care: food fell 0.79 to 0 over one row).
     It is not the fix and is not recorded as a check repair. Planted reading on the edited proof: labour 500 (a fill too
     slow to ground) reads FAIL reached_not_grounded (`evidence/reach_planted.json`); real build: PASS in 2 of 3 runs, FAIL
     in 1 (the stall).
2. **GRATE_fire_burns_people_above**, grate/solid burns 10/8 PASS, 9/9 FAIL, 8/6 PASS, then 13/1, 8/3, 7/0 PASS. The
   65c45b6e98 rule gives a solid-deck rider 0.35 per 60-tick check, near certain over one burn, so the row (grate > solid) is
   chance. The design (flowworks_bridges_design_2026-10-17 §4.1) says a solid deck gives a "low" chance; the row says solid
   riders stay unburnt. Which one is right is a design ruling, so the fix is not known. Filed:
   `RIMMANDRAKE_DECIDE_FLOWWORKS_SOLID_DECK_LOW_CHANCE_SATURATES_IN_ONE_BURN` (same cause as finding
   GRATE_FIRE_FIX_SOLID_DECK_BURNS_TOO). The fall in solid burns after run 3 is unexplained and is written on that item.

Owed case "three GRATE runs in a row": runs 4-6 PASS in a row; not counted as met while the verdict is chance.

### OL_OWNER_LOOK_READS: not run

`rerun_relation.py` reads it untouched since visit 4. Its one BLOCKED row waits on a C# reader that is not built
(RIMMANDRAKE_REPORT_SUBMERGE_SHADOW_QUEUE_JUDGE_CANNOT_SEE_ORDER, open). A rerun on the same build reads the same
UNMEASURED; visit 4's row carries, unrepaired, with that owner.

## Owed cases from the blind challenge (cycle 4) and the road back

- sc_hole_prison three PASS in a row (RIMMANDRAKE_TRACE_FLOWWORKS_AWAKE_PRISONER_MEAL_SKIPPED_ONE_RUN_IN_TWO): met on 65c45b6e98.
- sc_hung_bridge GRATE three runs in a row (RIMMANDRAKE_GATE_INFERNO_DECK_CHANCE_SOLID_OUTBURNS_GRATE): see above; not met.
- sc_hung_bridge red run (`maturation.py red-seen FlowWorks sc_hung_bridge`): not recorded. A planted C# fault reaches the
  game only through a build and deploy, and `red-seen` patches the source tree only. The table's command for this check also
  carries a note in parentheses, so it cannot run as written. `red-seen` now refuses that case by name
  (RIMMANDRAKE_REFUSE_LIVE_RED_SEEN_ON_A_FAULT_THE_GAME_NEVER_LOADS, 1909b51fab: selftest_red_seen RED 17/18 on the base,
  GREEN 18/18). The edited proof's own red: the planted slow fill read FAIL (`evidence/reach_planted.json`).
- sc_walk: UNMEASURED on game b; owed on game a.
- The four blind-cycle Problems, the six planted faults and the three lanes (sc_garden, sc_fill_front, sc_one_surface,
  OL, sc_fill_tiers, PIT_LOOK_1114_LIVE): untouched by 65c45b6e98 and not run in this visit; visit 5's readings stand.
- The other road-back rows (sc_fill_front, sc_fill_tiers, sc_garden, sc_hose_look, sc_source_pays, sc_trench_cover,
  sc_fetch_fallen, sc_geyser_tub, sc_ice, PIT_LOOK_1114_LIVE): untouched, their visit 3 to 5 rows carry.

## Beyond the checks

The diagnostic runs found the fill-job stall. One desktop capture (game b on the calm site, nothing odd). Five strange
things, each filed or explained (`strange.jsonl`).

## The savegame

No savegame was made on game b (a tier list; his walk is on his full list). The walk savegame stays visit 4's:
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1727.rws`
(13.6 MB, 5:29 PM PST) [measured].

## Items filed

- RIMMANDRAKE_REFUSE_LIVE_RED_SEEN_ON_A_FAULT_THE_GAME_NEVER_LOADS (pipeline, fixed and closed at 1909b51fab)

- RIMMANDRAKE_UNSTICK_FLOWWORKS_FILL_JOB_HOLDS_GRAVEL_BESIDE_THE_HOLE (MOD, the fill-job stall)
- RIMMANDRAKE_DECIDE_FLOWWORKS_SOLID_DECK_LOW_CHANCE_SATURATES_IN_ONE_BURN (MOD, needs a design ruling)

## Exit
```
ingame_rows: {sc_canal_fire: pass, sc_pit_reads: pass, sc_hung_bridge: fail, sc_moat_raid: pass, sc_hole_prison: pass, sc_toss_flame: pass, sc_walk: unmeasured, sc_pit_trap_raid: pass, OL_OWNER_LOOK_READS: unmeasured}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1727.rws
exit_met: false
```
