# BENCH_REBOOT_HANDOFF_202611152326 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611152121`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The owner made rulings today that change how this window works; all verbatim on the ledger. (1) Evidence-for-Ask (CLAUDE.md): take the obvious answer unless you hold evidence against it. (2) ~12:45-12:50 PM PST on `RIMMANDRAKE_HARDEN_PIPELINE_WHERE_HANDS_CLEANED_UP`: "Fix the process wherever it didn't work, ok? Make the pipeline better, don't keep cleaning up after it and leaving it alone" and "the Pipeline fixes its own issues once detected ... It's not a ticket for someone else, it's a ticket to file then do yourself." (now in standing_rulings and every run brief, ef0eff1e54). Every hand workaround of the pipeline gets its permanent fix launched in the same turn. He also asked for, BY NAME, a coherent discussion in the fresh window about the failing nightly tests: read `D:\ClaudeWork\rimmandrake\conductor\nightly_reds_report_20261115.md` IN FULL before your first substantive reply and open with it. The previous handoff (BENCH_REBOOT_HANDOFF_202611152121) never fired its restart: this seat clone could not sync (a stray uncommitted Pyrelands verdict), so every ledger commit read as unpushed and seat_restart REFUSED silently for two hours while the window kept saying HANDOFF READY. If a HANDOFF READY does not restart the window, run `seat_restart.py request --seat CONDUCTOR --ticket HANDOFF --fresh --now` and read its REFUSED line.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
He is at the keyboard. He was told all of the below except where marked UNREAD; reports marked UNREAD have not been read by any Conductor and must be read before he is told what they say.
- THE DISCUSSION HE ASKED FOR: nightly tests ("What the heck did we build, what do they add in terms of value, and why are they always failing and unfixable?"; then "I'm losing faith in nightly tests on a rapidly evolving system. Perhaps it has been deployed at the wrong phase? Who writes these tests anyway? Are they just regression sensors?"). Report UNREAD: `D:\ClaudeWork\rimmandrake\conductor\nightly_reds_report_20261115.md`. Check it answers the three later questions (authorship, share that only pins current behaviour, whether a nightly fits this phase); launch a short follow-up if not. My stated view to him: the nightly sweep is the wrong tool now, tests themselves stay; move the check to the moment of change, tier the suite. He has not ruled.
- Pyrelands: ANSWERED, do not bring it to him. The final look's one gap (furnace-beast size bar) went to him by card and he answered at 3:53 PM PST ("Keep 'twice', raise body to 9+", bigger art); built (RIMMANDRAKE_ENLARGE_FURNACE_BEAST_TWICE_THE_ZEER_MEANS_NINE, RIMMANDRAKE_REDRAW_FURNACE_BEAST_BIGGER_ART_CARD_PROMISED_IT) and the coverage judge signed covered at 00:52Z.
- Codex experiment (his order; all five lanes ended; outputs UNREAD except lane B): `D:\ClaudeWork\rimmandrake\codex_experiment_20261115\` (README explains). Lane B said Pyrelands' judge has no finite stopping rule. Lane C: 6 nightly reds already green, 6 turned green by Codex patches (unreviewed), 1 still red. Scoring owed.
- Fable census of Conductor interventions (his order): run ended 2:32 PM PST, "census published and ten of the Conductor's hand judgements now..." (rest UNREAD): `D:\Luke\dev\RimMandrake\design\RimMandrake\pipeline_interventions_census_2026-11-15.md`.
- Spend unit: he noticed the dollars are API list prices, not his subscriptions; lukas week went 100% -> 94% in 80 min at 4 slots. A card with the measured conversion is owed (`RIMMANDRAKE_MEASURE_SPEND_IN_WEEK_SHARE_NOT_LIST_DOLLARS`). Watch the account's pace first.
- SteveDesktop: waits on a person for the BIOS visit (`D:\ClaudeWork\rimmandrake\steve_diag\hw_20261115\vcore_20261115\BIOS_VISIT_STEPS.md`). Lane PAUSED.
- My assessment, not yet a goal in CONDUCTOR_GOALS.md: no mod has passed 0.1.0; drive ONE small mod (Gimme Some Slack, then ExplosiveKnockback) to a recorded pass before adding mods or stages.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `RIMMANDRAKE_AUTOBUILD_GRAFFITI_THIRTY_THREE_BARS_LEFT` — - `RIMMANDRAKE_DRAIN_NIGHTLY_REDS_WHILE_PIPELINE_SLEEPS` -- analysis report written 2:18 PM PST, unread; NEXT: read it in full, then hold the discussion with him.
- `RIMMANDRAKE_HARDEN_PIPELINE_WHERE_HANDS_CLEANED_UP` -- parent; a stray newer Pyrelands coverage_verdict.json (stamped 22:10:21Z) was found uncommitted in this seat clone and restored to HEAD at 3:26 PM PST, copy at `D:\ClaudeWork\rimmandrake\conductor\bench_dirty_pyrelands_20261115_1440\`; NEXT: launch a detached builder to find which run writes into /home/mandrake/rm/bench and whether an eighth judge look ran after the one final look, and fix the writer.
- `RIMMANDRAKE_BUILD_CONDUCTOR_INTERVENTIONS_INTO_PIPELINE_ITSELF` -- Fable run ended success 2:32 PM PST, item still open; NEXT: `rimflow show` it, read the census, tell him the counts, close or note what is left.
- `RIMMANDRAKE_SCORE_CODEX_EXPERIMENT_FOUR_LANES_NO_CLAUDE` -- all five lanes ended; NEXT: launch a detached opus judge to score each lane and land the sound patches through the normal checks; before Pyrelands is judged again, have the criteria fixer weigh lane B's proposed change to the judge's brief.
- `RIMMANDRAKE_FINISH_SPARSE_PUBLISH_AND_PINNED_TESTS_TURN_LIMIT` -- detached opus run ...-1794782442 live at wrap; NEXT: read its DETACHED RUN ENDED line and report.
- `RIMMANDRAKE_MEASURE_SPEND_IN_WEEK_SHARE_NOT_LIST_DOLLARS` -- filed, unworked; NEXT: launch a detached helper to measure list dollars per 1% of a week, then card him.
- `RIMMANDRAKE_AUTOBUILD_GRAFFITI_THIRTY_THREE_BARS_LEFT` -- the pipeline's own build item for Graffiti, started by the tick this window, not by hand; NEXT: leave it to the tick; check the status page's Graffiti line.
- `STEVE_LANE_UNSTICK_BRAKED_UNOWNED_EB2A` -- waits on the BIOS visit; NEXT: when he says it was done, launch a helper to count fault windows at 24 h and 72 h.
- `RIMMANDRAKE_BIND_ADVANCE_TO_EXIT_READINGS` -- not started, with the certificate, one-build and calibration items beside it and the Stage 7 check + pass record (Codex lane D drafted a Stage 7 design, unread); NEXT: launch one detached builder per item, tests first.
- `RIMMANDRAKE_RELEASE_STAGE_CEILING_PER_MOD_ONLY_GLOBAL_KNOB` -- release works (used on ExplosiveKnockback, rel-26ce199c1062, owed to his digest); NEXT: `rimflow show` it and close or note.
- `RIMMANDRAKE_DRAIN_NIGHTLY_REDS_WHILE_PIPELINE_SLEEPS` — report written, unread (see the first pointer above); NEXT: read the report in full, then hold the discussion with him
- `RIMMANDRAKE_FINISH_SPARSE_PUBLISH_AND_PINNED_TESTS_TURN_LIMIT` — detached run live at wrap; NEXT: read its DETACHED RUN ENDED line and report
- `RIMMANDRAKE_JUDGE_GIMMESOMESLACK_BLIND_CYCLE_THREE_TESTS_FIRST` — the pipeline's own judge run on Gimme Some Slack, launched by the tick, live at wrap; NEXT: leave it to the tick; read its result on the status page and tell him where Gimme Some Slack stands
- `RIMMANDRAKE_PIN_TUNABLES_OUT_OF_SELFTESTS` — the turn-limited builder's item for the pinned-config sweep; batches 2 and 3 landed (7220592bf5, ae843b4b0a); the finisher run continues it; NEXT: when the finisher ends, close this item with its sha or note what is left

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `RIMMANDRAKE_ADMIT_INGAME_SPAWN_RUNNER_REFUSES_GAME_UP` -- pipeline in-game runs now launch (FlowWorks 12:21 PM, ExplosiveKnockback live at wrap); NEXT: confirm closed.; NEXT: - HANDOFF READY does not restart the window when seat_restart refuses, and the refusal is silent to the window: read `seat_restart.py request ...`'s output. (filed: lessons)
- `./publish` prints PUBLISHED while the seat clone stays unsynced if a dirty file overlaps upstream; the local commits then read as unpushed forever. `./sync` names the file. (filed: lessons)
- `--owner-said` refuses a question: record his questions with `--why` and his words inside the text. (filed: lessons)
- In-process rm-builder helpers stop at 250 turns with no report; give big sweeps to detached runs. (filed: lessons)

## Closed since the last handoff (36)

- `RIMMANDRAKE_READ_LOCKED_CHANGE_AS_REEXAM_NOT_DISAGREEMENT` — 1b2f800b8d
- `RIMMANDRAKE_PROVE_PROOF_GATE_EXIT_AN_OR_PASSED_GREEN` — f181d3b6ea8c
- `RIMMANDRAKE_CERTIFY_FIRST_TOUCH_BY_OWNER_LOCK` — 7d5ca1bf71
- `RIMMANDRAKE_RUN_STOREROOM_RESTORE_WAIVER_TAKEN_ON_TRUST` — f181d3b6ea8c
- `RIMMANDRAKE_SWITCH_ELECTRICAL_BURN_WITH_FIRE_HALF_FLAME_HEIR` — bace1c29cc1d
- `RIMMANDRAKE_STOP_RETRYING_A_PRE_PUSH_REFUSAL` — 5f04cfb4a0
- `RIMMANDRAKE_RETAKE_PYRELANDS_EXAM_AFTER_LOCKED_CHANGE` — 2b9f9817e7
- `RIMMANDRAKE_ALIGN_BLIND_BRIEF_EXIT_WITH_JUDGE_OWED_READER` — 228cb916deb0
- `RIMMANDRAKE_ROUTE_EXPLOSIVEKNOCKBACK_CYCLE_THREE` — d3cf239cf2ef
- `RIMMANDRAKE_SKIP_BUILDER_STOP_ON_ZERO_REFUSED_BARS` — c269d7039e78
- `RIMMANDRAKE_RETRY_FAILED_LAUNCH_ONCE_CODE_CHANGES` — c269d7039e78
- `RIMMANDRAKE_REFUND_KILLED_RUN_DOLLARS_AT_THE_CEILING` — c269d7039e78
- `RIMMANDRAKE_CARRY_NIGHT_RECONCILE_RULES_INTO_BRIEFS` — c269d7039e78
- `RIMMANDRAKE_SWEEP_RUN_DOLLARS_AND_DEAD_RUNS_ON_TICK` — c269d7039e78
- `RIMMANDRAKE_RECORD_HAND_ACTS_TICK_ONLY_SAW_ITS_OWN` — c269d7039e78
- `RIMMANDRAKE_TRIAGE_STALLED_BUILDER_GRAFFITI_WAITED_ON_HELPERS` — 9eac6686d381
- `RIMMANDRAKE_PASS_FORWARD_STAGES_PAST_DESIGNER_CHAIN_CAP` — 2bcce1d52664
- `RIMMANDRAKE_WIDEN_GSS_NO_HOSE_SCAN_PIPE_PLANT_PASSED` — 349f9aa86b450efd0fbc5f77bab84d126ed2a07d
- `RIMMANDRAKE_STEWARD_GRAFFITI_HAND_STEP` — 8c9ef6def5
- `RIMMANDRAKE_COMPLETE_UNFINISHED_BLIND_CYCLE_RECORD_BY_STEWARD` — 1bf22855c4f8
- `RIMMANDRAKE_BUILD_CONDUCTOR_INTERVENTIONS_INTO_PIPELINE_ITSELF` — 1bf22855c4f8
- `RIMMANDRAKE_IGNORE_STAGE_MOVE_LOCK_LEFT_BY_EVERY_MOVE` — 34f26e40921c51bd55ae438a4b7aca5909dd4532
- `RIMMANDRAKE_ROUTE_GIMMESOMESLACK_CYCLE_TWO_FAILURES_BACK` — 34f26e40921c51bd55ae438a4b7aca5909dd4532
- `RIMMANDRAKE_KEEP_GRAFFITI_RAID_TAGS_OFF_NATURAL_ROCK` — c0db7ce0c2b52ab14cb28ac74059e88ffa14a08c
- `RIMMANDRAKE_PIN_GRAFFITI_WEATHER_FADE_CURVE_OFFLINE` — c0db7ce0c2b52ab14cb28ac74059e88ffa14a08c
- `RIMMANDRAKE_RESTORE_GRAFFITI_RAID_WEATHER_CHECKS_FROM_BUNDLE` — c0db7ce0c2b52ab14cb28ac74059e88ffa14a08c
- `RIMMANDRAKE_GIVE_DETACHED_UNITS_WINDOWS_PATH_PYTHON_EXE_VANISHED` — a1720b9c985a
- `RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_ONE_FAILURES_BACK` — fd45a8b6d805
- `RIMMANDRAKE_CLEAR_POLISH_LANE1_FAIL_WITHOUT_ANY_FIX` — 52c3efecf878
- `RIMMANDRAKE_JUDGE_EXPLOSIVEKNOCKBACK_BLIND_CYCLE_FOUR` — 8df3e495944b
- `RIMMANDRAKE_SCRIPT_GRAFFITI_MOOD_SCENES_THREE_FOR_SIX_BARS` — 92afc031c624ac0d5fa97ab883a4534564ba9100
- `RIMMANDRAKE_BUILD_FLOWWORKS_COATING_WASH_PASSED_ON_NOTHING` — ade1f4d4296eb3bf0017f01b8c33c13b49215841
- `RIMMANDRAKE_LIST_FLOWWORKS_SEVENTEEN_SWITCHES_NO_FLOOR_KNEW` — ade1f4d4296eb3bf0017f01b8c33c13b49215841
- `RIMMANDRAKE_CONFIRM_EXPLOSIVEKNOCKBACK_CYCLE_FOUR_EXIT` — 74535793d746
- `RIMMANDRAKE_ISOLATE_DISPATCH_SELFTEST_FROM_CONVERGENCE` — done by verify, no close
- `RIMMANDRAKE_FLAG_DETACHED_SUCCESS_LEAVING_ITEM_OPEN` — done by verify, no close

## Filed and still open (37) — the next seat's queue

- `RIMMANDRAKE_BUDGET_DESIGNER_EXAM_HELPERS_FIVE_READERS_ZERO_SLOTS` — Designer stage 4 (exam) needs five fresh helpers but its spawns are counted against CONDUCTOR's slot budget, which was N=0
- `RIMMANDRAKE_UNGATE_STEWARD_EXAM_HELPERS_WINDOW_BUDGET_AT_ZERO` — slot hook: a detached steward's exam helpers draw on the Conductor window budget, N=0 when he is away
- `RIMMANDRAKE_CLEAR_STALE_BLOCK_REASON_ON_LIFT` — a lifted Designer block keeps its blocked_on reason: Pyrelands reads ready with a released stop as its why
- `RIMMANDRAKE_MEASURE_SPEND_IN_WEEK_SHARE_NOT_LIST_DOLLARS` — Pipeline spend is counted in API list-price dollars (claude's total_cost_usd, costBasis list), which he never pays on flat subscriptions; measure the 
- `RIMMANDRAKE_SCORE_CODEX_EXPERIMENT_FOUR_LANES_NO_CLAUDE` — Score the Codex experiment launched 2026-11-15 ~1:50 PM PST (D:\ClaudeWork\rimmandrake\codex_experiment_20261115\README.md): per lane (A code review, 
- `RIMMANDRAKE_GUARD_PROOF_VERDICTS_FIVE_WEAKENED_STAYED_GREEN` — Polish, EK: five weakened live verdict expressions in the proof scenes (flying_off skip, goods wall position, deep water, container 0 cells, fireHalf 
- `RIMMANDRAKE_CLEAR_KNOCKBACK_HAUL_MEMORY_STATIC_OUTLIVES_GAME` — Polish, EK: RM_Patch_PawnFlyer_KnockbackLanding.Hauling is a static Dictionary<Pawn,Job>, never cleared on game load and not saved; a pawn dying mid-f
- `RIMMANDRAKE_TEST_JOLT_DECAY_DOC_PROMISES_UNTESTED` — Polish, EK: RM_KnockbackMath.JoltOffset's doc promises a decaying shake; a planted no-decay passed T_KERNEL and lane 1 (only the bound is tested). No 
- `RIMMANDRAKE_JUDGE_FLOWWORKS_REVIEW_SAVE_FOUR_LOOK_QUESTIONS` — FlowWorks review save: four look questions for a judge or his walk (visit 1)
- `RIMMANDRAKE_PROVE_GSS_GEOMETRY_RAN_COUNT_IS_ONLY_TELL` — GSS Polish: T_CORD_GEOMETRY_OFFLINE passes rc 0 when --geometry is dropped (wrapper or Program.cs); only the check count tells; its M2c lab site is NO
- `RIMMANDRAKE_SCRIPT_GRAFFITI_WALL_AND_ART_SCENES_DRAFTS_DIED` — Graffiti: script the wall close-up, spree variety and art skill scenes (6 bars)
- `RIMMANDRAKE_EXERCISE_GSS_CORD_GUARDS_THREE_PLANTS_SURVIVE` — GSS Polish: three cord-lay guards (StrandFaults taut, hop bend allowance, slacken flat long edge) can be weakened with T_CORE and T_CORD_GEOMETRY_OFFL
- `RIMMANDRAKE_SCRIPT_GRAFFITI_SOCIAL_SCENES_FIVE_FOR_SEVEN_BARS` — Graffiti: script the mockery, answer wall, tribute, fights and visitors scenes (7 bars)
- `RIMMANDRAKE_SCRIPT_GRAFFITI_SETTINGS_SCENES_IDEO_RELOAD_TOO` — Graffiti: script the breach-bias raid, settings and ideoligion-reload scenes (4 bars)
- `RIMMANDRAKE_REWORD_GSS_NO_PIPE_BAR_POLES_ON_PURPOSE` — GSS bar no_hose_in_gss says 'No hose, reel or pipe is drawn by this mod', but GSS's aerial engine draws FlowWorks pipe-pole spans by design (pipe_pole
- `RIMMANDRAKE_SCRIPT_GRAFFITI_WALL_LOSS_SOAK_AND_WALK_SCENES` — Graffiti: script the wall loss, lived-in soak and walk scenes (4 bars)
- `RIMMANDRAKE_REPIN_GSS_ASYNC_FAULT_CAP_FIFTY_SEVEN_USED` — GSS T_CORE async worker-fault check asserts builds5 < 60 while the live scene's async lay now takes ~57 Builds: one slow machine from a false red; a b
- `RIMMANDRAKE_SIZE_DISPATCH_BUILDS_THIRTY_THREE_BARS_ONE_RUN` — Maturation dispatch: split a large refused-bar set into builder items of about six bars
- `RIMMANDRAKE_FINISH_SPARSE_PUBLISH_AND_PINNED_TESTS_TURN_LIMIT` — Finish the sparse-clone publish fix, the pinned-config selftest sweep and the per-ruling shard routing left by a turn-limited builder
- `RIMMANDRAKE_PAINT_GRAFFITI_ROOFED_TWIN_RANDOM_ENEMY_WONT_DO` — Graffiti: a probe that paints the raid's own faction a roofed twin mark (sc_weathered_raid_mark's start)
- `RIMMANDRAKE_REBUILD_FLOWWORKS_SOURCE_PAYS_SCENE_POND_NEVER_THERE` — FlowWorks sc_source_pays UNMEASURED (SITE): the draft assumes a natural pond and a lake the calm map lacks (visit 1)
- `RIMMANDRAKE_REBUILD_FLOWWORKS_PAWN_HEIGHT_SCENE_ZEROS_PASSED` — FlowWorks sc_pawn_height UNMEASURED (HARNESS): 17 sink reads all 0 passed PH_offset_follows_depth; the swim row read an unreached pit (visit 1)
- `RIMMANDRAKE_REBUILD_FLOWWORKS_ICE_SCENE_BASIN_NEVER_FROZE` — FlowWorks sc_ice UNMEASURED (HARNESS): ProofStageBasin got 'x,z,5,5;freeze' against its x;z;w;h;levels;waterM;FluidDef contract, nothing froze (visit 
- `RIMMANDRAKE_REBUILD_FLOWWORKS_ISLANDS_SCENE_SPAWNED_A_DRAW_STYLE` — FlowWorks sc_islands UNMEASURED (HARNESS): spawns RM_SuspensionBridge, a DrawStyleCategoryDef, not a ThingDef; never stages a winch loss (visit 1)
- `RIMMANDRAKE_REBUILD_FLOWWORKS_GARDEN_SCENE_MACHINES_NEVER_PIPED` — FlowWorks sc_garden UNMEASURED (SITE): clock stopped on starving colonists, machines not piped; five blind-cycle cases and three planted faults unseen
- `RIMMANDRAKE_FINISH_FLOWWORKS_WALK_SCENE_HALF_THE_BAR_UNASKED` — FlowWorks sc_walk UNMEASURED (HARNESS): toggle and save/reload asked on his 316-mod list; the pond paying again, no leftovers and a clean log not aske
- `RIMMANDRAKE_REPAIR_FLOWWORKS_OL_SHADOW_JUDGE_PRESUMED_STALE` — FlowWorks OL_OWNER_LOOK_READS UNMEASURED: 130 OL_no_surface_shadow + 7 OL_labels_fade FAIL from a judge presumed stale against shadow-under-the-sheet 
- `RIMMANDRAKE_PASS_BRIDGE_STATIC_CALL_INT64_POUR_LABELS_UNASKED` — PIT_LOOK_1114_LIVE UNMEASURED: the bridge's static_call refuses the Int64 argument of RM_GodLiquidMath.StepLabel, so 3 pour-label rows cannot be asked
- `RIMMANDRAKE_PIN_FLOWWORKS_FILL_SCENE_FIXES_RED_BEFORE_GREEN` — FlowWorks sc_fill_front and sc_fill_tiers: earlier FAIL rows fixed in the sitting with no red-before test; pin the harness fixes and rerun in visit 2
- `RIMMANDRAKE_BUILD_FLOWWORKS_TOSS_FLAME_JOBDEF_STILL_UNKNOWN` — FlowWorks: build the 'toss a flame' order (sc_toss_flame FAIL, MOD: Unknown JobDef RM_TossFlame), visit 1
- `RIMMANDRAKE_REBUILD_FLOWWORKS_MOAT_SCENE_PASSED_ON_REFUSED` — FlowWorks sc_moat_raid FAIL: the raid never swam, ProofTank args wrong, MOAT_chemfuel_pumped passed on a REFUSED reply (visit 1)
- `RIMMANDRAKE_REBUILD_FLOWWORKS_HOSE_SCENE_PUMP_HAD_NO_SOURCE` — FlowWorks sc_hose_look UNMEASURED (HARNESS): the draft pump had no source, power or laid hose, so plump-vs-flat was never asked (visit 1)
- `RIMMANDRAKE_REBUILD_FLOWWORKS_TRENCH_SCENE_READ_LID_PROOF` — FlowWorks sc_trench_cover UNMEASURED (HARNESS): the draft read ProofCover (pit lids), not combat cover; its raider row passed with no raid (visit 1)
- `RIMMANDRAKE_REBUILD_FLOWWORKS_FETCH_SCENE_RAID_NEVER_CAME` — FlowWorks sc_fetch_fallen UNMEASURED (HARNESS): the raid never reached the pit within the wait, no fallen, no ladder (visit 1)
- `RIMMANDRAKE_REBUILD_FLOWWORKS_PITTRAP_SCENE_STOPPED_BY_OWN_RAID` — FlowWorks sc_pit_trap_raid UNMEASURED (HARNESS): the clock gate stopped on the raid the scene fired itself (GovernorStop hostile_arrival) (visit 1)
- `RIMMANDRAKE_STOP_KNOCKBACK_HIT_ACROSS_SANDBAG_NO_CONTACT` — Polish (ExplosiveKnockback 0.1.0, blind cycle 4): RM_KnockbackMath.Resolve: a pawn thrown over a sandbag cell straight into a pawn, wall or door backs
- `RIMMANDRAKE_PROBE_GRAFFITI_CLEAN_BREAK_GATE_FORCE_SKIPS_IT` — Graffiti: a probe that reads the cleaning break's gate (forcing skips it)

## Commits

```
c24075011d conversations: catch-up 8 record(s)
ce5382926e ledger: BENCH shard
a6f7a04225 ledger: RIMMANDRAKE_FINISH_SPARSE_PUBLISH_AND_PINNED_TESTS_TURN_LIMIT note; lesson on timer drift checks
299f563de6 ledger: ops_watch alarm(s) note:STEVE_INCIDENT_UNCLAIMED:steve.incident_unclaimed_min
afba73e908 selftests: maturation_dispatch and known_reds run on pinned numbers, shipped file range-checked (batch 5)
bf3005d87e ledger: maturation dispatch filed RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_VISIT_TWO
a873519668 ledger: RIMMANDRAKE_CONFIRM_EXPLOSIVEKNOCKBACK_CYCLE_FOUR_EXIT clone bundled
223c9b7f03 ledger: RIMMANDRAKE_BUILD_FLOWWORKS_COATING_WASH_PASSED_ON_NOTHING clone bundled
5a698d223f maturation: spend rows of ended runs (Dispatch step)
fc2de66194 conversations: catch-up 1 record(s)
c60d452290 ledger: detached run on RIMMANDRAKE_CONFIRM_EXPLOSIVEKNOCKBACK_CYCLE_FOUR_EXIT ended
cb64abae64 conversations: catch-up 1 record(s)
74af4757de ledger: detached run on RIMMANDRAKE_BUILD_FLOWWORKS_COATING_WASH_PASSED_ON_NOTHING ended
03a6b09cee ledger: RIMMANDRAKE_CONFIRM_EXPLOSIVEKNOCKBACK_CYCLE_FOUR_EXIT closed
c92e94470b ledger: RIMMANDRAKE_BUILD_FLOWWORKS_COATING_WASH_PASSED_ON_NOTHING closed
74535793d7 ExplosiveKnockback: steward advances blind cycle 4 to in_game; test table remade (closed known_reds dropped)
f1c1164a5c FlowWorks road-back evidence: coating build and toggle-list selftests
ade1f4d429 FlowWorks: wading out of oil, tar, blood or slime coats a pawn; water washes it (bar inv_liquid_coating)
9ebd529a42 ledger: RIMMANDRAKE_FINISH_SPARSE_PUBLISH_AND_PINNED_TESTS_TURN_LIMIT note
a1b237418a tunable_sweep: every git call has a deadline
... 159 more: git log --oneline d086163083..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : UP  → corrected to DOWN, measured now
- Bridge: FREE    since 2026-11-15T22:34:51Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
 M deployed/config/ModsConfig.before-tier-pyrelands.xml   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
 M infrastructure/state/art_eval/briefs/RM_Chellow.json   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
 M infrastructure/state/art_eval/briefs/RM_Gembug.json   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
 M infrastructure/state/art_eval/briefs/RM_Krissek.json   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
 M infrastructure/state/art_eval/briefs/RM_Lirrith.json   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
 M infrastructure/state/art_eval/briefs/RM_TheUnfinished.json   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
 M infrastructure/state/art_eval/briefs/RM_Wuum.json   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
 M infrastructure/state/art_eval/briefs/RM_Ysvaltha.json   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
 M infrastructure/state/art_eval/briefs/RM_Zrrik.json   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
 M infrastructure/state/art_eval/briefs/SWPotF_RaceDef_ysalamir.json   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? cards.json   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? deployed/config/ModsConfig.before-tier-mods__mandrake_rm_explosiveknockback__mandrake_rm_flowworks__mandrake_rm_gimmesomeslack__mandrake_rm_patches.xml   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? design/RimMandrake/designer_drawing_out.md   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? design/concepts/Contagion/exam_control/   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_FWLIVE.md   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE1.md   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE2.md   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE3.md   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_FWLIVE.md   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE1.md   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE2.md   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE3.md   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE4.md   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE5.md   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE6.md   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE7.md   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE8.md   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? infrastructure/state/queue/CODEX_ARCHMAGI_FWDRAIN.md   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? infrastructure/state/queue/CODEX_STEVEDESKTOP_HUGETHINGS.md   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? ralph/.context_warned   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
?? shortcuts.ps1.txt   not this window's: already dirty or untracked in the bench clone when this window woke (queue renders, ModsConfig backups, art-eval briefs)
```

