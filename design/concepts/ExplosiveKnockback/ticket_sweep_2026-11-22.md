# Explosive Knockback: ticket sweep, 2026-11-22

Item RIMMANDRAKE_SWEEP_KNOCKBACK_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE. This was a detached run of the Conductor
(seat BENCH), on the owner's order of 2026-11-22 about 3:05 PM PST. The mod is at Design Version 0.1.0 (locked
2026-11-13) and in the blind challenge stage (Stages 4 and 5; blind cycle 6 has no record). The pipeline has it switched
OFF (pipe act ct_000026, 2026-11-18).

## Was an earlier sweep done?

- `D:\ClaudeWork\rimmandrake\conductor\triage_20261105\` (the first queue sweep): no line names Explosive Knockback
  (searched with grep, case-insensitive).
- 2026-11-17: the Fable Rescue (RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX) sorted 51 open ledger items that
  matched the mod's name into classes. It closed 2 of them. The sort is in `version/rescue_2026-11-17/tickets_sorted.md`.
  It was a sort, not a clean-up: most of its "built, still open on paper" items were still open today.
- No other sweep of the mod is in the ledger (searched every shard for "sweep" together with "knock").

## How the items were found

`model.replay()` over the whole ledger (history plus every shard), at origin/main of 2026-11-22 about 3:10 PM PST. The
search took every OPEN item and matched `knockback|explosivekn|\bEK\b|_EK_|RM_Kb|KbGrid|KbFrame|bench-ek` against its
id, its title, its prose file (`infrastructure/state/items/<ID>.md`, never `closed/`), its ledger events and its
`caused_by`. Result: **82 open items** matched [measured]. Each one was read with `rimflow show`. 40 of them only mention
the mod (Cauldron, FlowWorks, GSS and pipeline items, plus notes in passing). 42 were read in full. Of those 42:

- **34 are about Explosive Knockback** (the Conductor's rough count was 35).
- 8 are about something else and name the mod. They were left alone:
  - RIMMANDRAKE_ISOLATE_GAME_FREEZES_SMALLEST_LIST_BEYOND_ONE_MOD: freezes that happen with the mod on or off. His
    words: "a consistent issue well beyond this mod".
  - RIMMANDRAKE_KILL_LIVE_HOLDER_RESUME_AFTER_FIRST_SESSION: a pipeline live test that uses an EK holder run. Killing a
    live run is the Conductor's act.
  - RIMMANDRAKE_PORT_SUITES_TO_SCENE_RUNNER_PIT_EXPOSURE_FIRST and RIMMANDRAKE_PROVE_SCENE_RUNNER_LIVE_SAME_ROWS_FEWER_CALLS:
    scene-runner tooling.
  - RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE: the SteveDesktop test lane.
  - RIMMANDRAKE_PROVE_FLOWWORKS_RAILINGS_HOLD_AGAINST_BLAST_THROWS: FlowWorks. The FlowWorks sweep runs today.
  - KINETIC_BLAST_WEAPONS_1: Kinetic Arms. Its EK half (the per-projectile lookup) is built and inside 0.1.0's
    blast-power bar.
  - FALLEN_WIRE_SHOCK_1: Gimme Some Slack.

What this sweep could not look at: the mod ledger (`design/concepts/ExplosiveKnockback/ledger/`) was not read for
findings that are not rimflow items, because its findings are mined from rimflow items. The live game was not looked at:
nothing here ran a live row.

## Count per class (34)

| class | n | items |
|---|---|---|
| DONE | 17 | BUILD_KNOCKBACK_CREATURE_MASS_AND_BLAST_POWER, BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN, CHAIN_FLAMMABLE_GAS_CLUMPS, DEPLOY_KNOCKBACK_DRAWING_STORAGE_OPEN, FLY_KNOCKBACK_GOODS_WILD, KNOCK_PEOPLE_HEAVY_GOODS, LIMIT_KNOCKBACK_STORAGE_CLOSED, PROVE_KNOCKBACK_HIDING_LOCKER_LIVE, READ_WALK_TICK_COST_RUNNING_PAUSED_READ_ZERO, REWRITE_KNOCKBACK_PROOFS_REAL_CONTROLS, SPLIT_KNOCKBACK_SWEEP_OFFLINE_TABLE_LIVE_WIRING, CHALLENGE_KNOCKBACK_BLIND_TWO_FIRST_EXIT_MISSED, PILOT_BLIND_CHALLENGE_ON_KNOCKBACK_NEVER_RUN_BEFORE, DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_ACCEPTANCE_FIRST, RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX, REPOINT_EK_JOURNAL_JOLT_CHECKS_AFTER_PLAN_MOVE (fixed here), RESTORE_EK_FUZZ_MUTANTS_TWO_TARGETS_VANISHED (fixed here) |
| DUPLICATE | 0 | none. The merges below join current-version Problems that share a run or a file group. |
| STALE | 1 | NOTE_KNOCKBACK_CALLER_MUTANTS_OWED_TO_STAGE_SIX |
| DEAD | 0 | none |
| NOT WORTH THE TOUCH | 6 | CLEAR_KNOCKBACK_HAUL_MEMORY_STATIC_OUTLIVES_GAME, SHOVE_PAWNS_STANDING_ON_COVERS_IN_BURNING_GAS, STOP_KNOCKBACK_HIT_ACROSS_SANDBAG_NO_CONTACT, TEST_JOLT_DECAY_DOC_PROMISES_UNTESTED, RETAKE_KNOCKBACK_EXAM_NO_SCENARIO_READS_LEAF, FIND_DARK_HAZE_EAST_OF_GAS_CHAIN (one line each in `version/polish.md`, "Not worth the touch") |
| NEEDS HIM | 0 tickets | his one open question is listed below. It is not a ticket. |
| KEEP, CURRENT VERSION | 7 | PROVE_KNOCKBACK_ALL_FLY_PERF, KEEP_SPARED_SLEEPER_IN_BED_ON_FULL_LIST, FIX_KNOCKBACK_RAID_NULL_PAWN_STORM_780_TICKS, PROVE_KNOCKBACK_OUTERRIM_BLAST_LANES, READ_CONTAINER_JOLT_OFFSET_IN_PROOF, DRAW_CONTAINER_JOLT_AS_MOVE_NOT_GHOST (these six are merged below), STOP_GAS_SHOVE_PAST_WALL_CORNER_UNSEEN |
| KEEP, NEXT VERSION | 3 | BRUISE_KNOCKBACK_LANDING_ON_PAWN, FLING_KNOCKBACK_CARRY_ON_OWN_ARC, ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS |

All ids above start with `RIMMANDRAKE_`. The one-line evidence for each class is the `--reason` of its close, supersede or
drop event (`rimflow show <ID>`).

DONE evidence, in short:
- The built behaviour items pass live on the 34-mod tier list. The rescue's run of 2026-11-17 has 66 scenes PASS
  (`version/rescue_2026-11-17/live/all_scenes_300_ticks.txt`, landed in ffc3937ee7). Its four non-passes each have their own
  record: pit_goods_fetch passes in its own 60,000-tick run; frame_probe_selfcheck and barrage_perf are the full-list rows
  merged below.
- The "his look still owed" lines on CHAIN_FLAMMABLE_GAS_CLUMPS and KNOCK_PEOPLE_HEAVY_GOODS come from the pipeline
  before the Maturation Pipeline. Under the Maturation Pipeline, his look is his walk of 0.1.0 (one of his five acts), so
  these lines move to that walk. No words of his were dropped.
- The pipeline-record items name a stage that has run, and its record is on disk: blind cycle 1 and FORMAT_NOTES.md,
  cycle 2, in-game visit 1, and the rescue.

## The modern tickets that remain

Current version (0.1.0):
- **RIMMANDRAKE_RUN_KNOCKBACK_ROWS_TIER_LIST_CANNOT_DECIDE** (new; it merges four items): sc_barrage_perf and
  sc_walk_raid on the owner's full list, a watch for the walk's two NRE storms, the walk save's spared sleeper, and
  sc_blast_kinds' Outer Rim lanes. It carries his flagship words and his barrage approval. Offline acceptance for the
  Outer Rim half: `grep -l OuterRim .../RM_KnockbackProof*.cs` prints nothing today (watched red).
- **RIMMANDRAKE_MEASURE_KNOCKBACK_JOLT_PER_CONTAINER_NOT_GHOST** (new; it merges two items): the jolt rows read a
  per-container drawn offset (today they print the literal `drawnOffset=UNMEASURED`), and one judge rules on the ghost
  draw. Acceptance: `grep -c 'drawnOffset=UNMEASURED' .../RM_KnockbackProof_StageThree.cs` prints 1 today (watched red)
  and must print 0. Then the live closed_containers run.
- **RIMMANDRAKE_STOP_GAS_SHOVE_PAST_WALL_CORNER_UNSEEN** (kept as it is; filed 2026-11-17 in the new grammar): a burning
  gas clump shoves things past a wall corner with no line of sight. It is classed Problem by the obvious reading: a
  player would see a stack hop behind a sealed corner. Its acceptance is live only (map_agreement case), not yet watched
  fail.

Next version (marked target v2; it never moves a 0.1.0 bar):
- RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN (his card, 2026-11-14: "Bruise in the next version").
- RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC (his words, 2026-11-14: "For today have them hold it. Next version it should go flying independently of the person holding it. Different trajectories.").
- RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS (his card, 2026-11-12: "Absorb the idea into Knockback"). It is
  Divergent by the obvious reading, because the 0.1.0 vision holds no blast visuals. It is now entered in
  `version/next_version/README.md`.

## What was built in this run (offline, tests first)

- `860f017c50`: `selftest_explosiveknockback_journal_jolt.py` reads the throw rules where ffc3937ee7 moved them
  (`RM_KnockbackPlan.cs`), and checks that the map component hands the plan `Rules()`. Red on the base: 6 faults, 11 of 16
  planted breaks caught. Green: 0 faults, 21 of 21.
- `feec252970`: the fuzz mutation list (`Utils/mutate_explosiveknockback_fuzz.py`) drops the two per-tick budget mutants, whose target
  was removed by design in 0808c55303 (all-fly, no throw caps). It retargets the two pit mutants at the current pit rule
  and adds a mutant for the covered-pit rule that the K-08 flip established. Red on the base: 59 caught, 4 missed
  (MUTATION TARGET NOT FOUND), exit 1. Green: 62 caught, 0 missed, exit 0.

Nothing in this run changed the mod's shipped source, so no DLL was rebuilt. No live check ran.

## For the Conductor

- **NEEDS HIM:** the rescue's question Q2 of 2026-11-17 (`D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX\questions.md`)
  is unanswered. In his words: when a blast throws a stack at a pit cell that already holds a stack, where should it end?
  The built default: on the pit floor beside that cell. If that floor is full, on the side it came from, never past the
  pit. His other pick (a pit floor cell that holds several stacks) would be next-version work in FlowWorks. His walk of
  0.1.0 also carries the looks that older tickets said were owed (the gas clumps, heavy goods, the flagship storeroom
  bomb).
- To switch the mod on, release its stage ceiling and run blind cycle 6, then Stage 6, is the Conductor's act. Nothing
  here did it.
- RIMMANDRAKE_RUN_KNOCKBACK_ROWS_TIER_LIST_CANNOT_DECIDE needs the owner's full list (ArchBig, or a game that holds the full list).
- The certificate's "RM_KnockbackProof.cs did not load: SyntaxError" line is a wording fault (a fault of form) in
  `judge_certificate.py`. A test row whose file is a `.cs` with an entry goes to the Python suite adapter, so the line
  reads as a load failure instead of "no empty-game adapter". The certificate's real refusals are stale runs (red_seen
  and ran_on_this_build), which `maturation_dispatch.py` reruns. Not fixed here: it changes no verdict, and pipeline
  repair lanes are live on that file today.

## End state (measured with model.replay(), 2026-11-22 about 4:30 PM PST)

Of the 34 items about the mod: 17 done, 7 dropped, 6 superseded into the two new tickets, 4 open (STOP_GAS_SHOVE and the
three next-version tickets, now target v2). With the two new tickets, 3 current-version tickets and 3 next-version
tickets are open.
