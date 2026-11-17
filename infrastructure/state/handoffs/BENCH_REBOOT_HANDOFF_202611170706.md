# BENCH_REBOOT_HANDOFF_202611170706 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611170447`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The owner went AFK at 10:25 PM PST 2026-11-16: "I need to go AFK for awhile. Stay light orchestration but keep it all going, ok?" (ends when he next writes; he is in fact working in the second window CONDUCTOR-DESIGNER on a Designer Cleanse). At 10:34 PM he released this window's reset hold, helpers first. Gimme Some Slack is top priority "at any cost". TWO FIRST ACTS for the next window, in this order: (1) re-arm the question watcher: a Monitor (30 min, re-arm on expiry) on `questions.md` in `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN\` (the live Slack Fable asks there) and on Conductor log lines DETACHED RUN ENDED / RESCUE PROPOSED / DESIGNER WINDOW, excluding `restart:BENCH` lines; relay each new question with its picture opened on his desktop, his answer verbatim into `answers.md` plus a ledger note. (2) The moment the Slack Fable run ends, RELEASE MY HOLD on GimmeSomeSlack (three `kind hold` lines, stages 6, 3 and 4+5, in `design/concepts/GimmeSomeSlack/journal.md`, published 0c2828de2f): until then the pipeline moves nothing on that mod. Read every "untested or open" line of a closing report as work and resume the run before telling him it is done.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
He is away; nothing was carded. Waiting for his return, in value order:
- Gimme Some Slack in-game visit 1 does NOT pass (178 of 198 pass, 6 fail, 14 unmeasured; published 736d7d8728; pictures `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_VISIT_ONE\`; his review map on tonight's build is the save `GSS_VISIT1_WALK_20261116.rws`). The same Fable now holds the whole mod: all visit failures, the ten tickets needed for 0.1.0, three unwritten tests. Told to him at 10:52 PM PST.
- Pyrelands rescue landed 49e11870b4 (wind-carried fire, 24 cells wide, bar `burn_line_walks` reworded by him); offline only. The first live run is going on game b; pictures of the real fire are owed to him from `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_RUN_PYRELANDS_WEEK_SKY_FREE_NEVER_ONCE_SEEN\`.
- Judge prompt proposals with GPT's 28-point critique: `D:\ClaudeWork\rimmandrake\conductor\role_prompt_upgrades_20261116.md` sections 6 and 7; four YOUR CALL points (11, 14, 19, 26); my leans were given at about 10:32 PM PST. Offline and in-game tester prompt changes are proposal only too. NOT opened on his screen yet: open it in Typora when he is back.
- One card owed (after the live results): bars that pin numbers (Graffiti: variety counts, re-read once a day, moods about plus or minus 3, fade over the last 40 percent; Pyrelands: six, listed in the rescue sheet), three proposed Pyrelands bars (the first still says "a line, never a flood": reword it to his loosened wording first), and whether "black rain fills moats and tanks" stays in 0.1.0.
- Ticket sweeps: `D:\ClaudeWork\rimmandrake\conductor\ticket_sweep_gss_20261116.md` (62 to 35 open: 10 needed, 17 polish, 6 plumbing) and `ticket_sweep_pyrelands_20261116.md` (60 to 32 open: 15 needed, 2 his calls, 4 art, 4 polish). Owed: a proposal to move polish to one polish list per mod (his confirmation).
- Token unit: weighted_v2 is live (one Opus 5.5 input token = 1; Fable 5.2 is 2x, Sonnet 5.5 is 0.5x; the rule is in his top-level instructions, Lodestar 7f06b9d4). Tonight recomputed, old to new: Slack Fable rescue 8,326,348 to 9,106,441; Pyrelands Fable rescue 5,420,721 to 5,490,635; the earlier Opus Slack fixer 5,543,229 to 3,517,744; Graffiti builder 2,659,965 to 1,742,459; Slack in-game stage total about 36.0M to about 25.7M. NOT yet told to him. Some printers still show v1 (four items filed by the helper); the main item RIMMANDRAKE_WEIGH_TOKENS_BY_MODEL_OPUS_INPUT_UNIT is still open.
- Rescue detector is live; two proposals tonight, both declined by me with reasons (ExplosiveKnockback: both open Problems were fixed by Opus fixers, cycle 6 judges; FlowWorks: one criterion at its minimum). Hindsight: it would have flagged Slack 28 hours early and Pyrelands 7.5 hours early (ceiling only). Stats: `python3 src/RimMandrake/rimflow/maturation_rescue.py status`.
- His musing on building with Fable from the start: I proposed an experiment (the next mod built by Fable start to finish against one on Opus 5.5 with the new prompts); he has not said which mod.
- Hand acts for his digest: ceiling release rel-5788c9fe1df8 (GimmeSomeSlack in-game, about 11.6M weighted tokens v1) and rel-d355a652e496 (ExplosiveKnockback); my Pyrelands hold released 9:57 PM; my GimmeSomeSlack hold placed about 10:47 PM.
- Five pipeline selftests are red on main and were red before tonight's token change (incident, dispatcher F1, role_unit_stamp, wrapup W1, no_bare_cuts), per the token helper [not re-measured by me].
- The CONDUCTOR-DESIGNER window (Fable 5.2, not the seat) is open; its brief is `D:\ClaudeWork\rimmandrake\conductor\designer_window_brief.md`; it logs to the Conductor log as `DESIGNER WINDOW:`. Its Codex fleet shares the pool of work clones: Slack wins if the pool runs short.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `RIMMANDRAKE_LAY_SLACK_CLOSE_FITTINGS_TWENTY_ONE_UNLAID` — Fable run rm-detached-bench-rimmandrake-lay-slack-close-fittings-twe-1794892548 LIVE (session 0f924521-1b2a-4e01-8482-87e58a50c67f), close fittings published 9ed2b6e1d77b, now ordered (answers.md, 10:41 and 10:47 PM PST) to finish the whole mod: visit-1 failures, ten needed tickets, three unwritten tests; no spend stop on it; NEXT: read its DETACHED RUN ENDED line; if any case is left open resume it (`detached_helper.py launch --seat CONDUCTOR --item <ID> --brief-file <F> --model fable --budget-usd 0 --resume 0f924521-1b2a-4e01-8482-87e58a50c67f`), else do the hold release below and tell him
- `RIMMANDRAKE_RELEASE_SLACK_PIPELINE_HOLD_WHEN_FABLE_ENDS` — owed item, open; my hold stands on GimmeSomeSlack stages 6, 3 and 4+5; NEXT: when that Fable run ends, append three `- CONDUCTOR INTERVENED (stage <6|3|4+5>, <time>, kind release): ...` lines to design/concepts/GimmeSomeSlack/journal.md, commit by path, ./publish, check `maturation.py next GimmeSomeSlack` shows no refused hold, close the item `--no-code` naming the sha
- `RIMMANDRAKE_RUN_PYRELANDS_WEEK_SKY_FREE_NEVER_ONCE_SEEN` — first Opus run was stopped by the outside spend watchdog at its default cap at 11:06 PM PST (no result; its clone bundled); RESUMED at 11:09 PM PST with a larger cap (session de7f2ecc-3444-4b57-8561-865e160ce3c1, game b), first live run of the wind-carried fire; the pipeline's blind cycle 3 waits on it; the stop also showed a weighted_v2 defect: the run's spend read UNMEASURED because the alias opus has no ANTHROPIC_DEFAULT_OPUS_MODEL in that unit's environment; NEXT: read its ended line, LOOK at its pictures in the showings folder, tell him what the real fire looks like, file each failure, and file the UNMEASURED-alias defect with its fix
- `RIMMANDRAKE_LAUNCH_BOTH_GAMES_STEAM_REFUSES_A_BESIDE_B` — Opus fixer rm-detached-bench-rimmandrake-launch-both-games-steam-refu-1794898927 LIVE since 11:02 PM PST (Steam refuses game a while game b runs; visit 1's full-list walk was probably spoiled by the workaround); NEXT: read its ended line; if LEFT OPEN do the named live step
- `RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_VISIT_ONE` — visit 1 recorded, exit not met, its run left the item open listing seven filed items; the Fable holds the failures; NEXT: leave it to the pipeline after the hold release (the next visit launches when the failures close)
- `RIMMANDRAKE_WEIGH_TOKENS_BY_MODEL_OPUS_INPUT_UNIT` — code landed 381db58f59, item still open because its verify names no criterion; four follow-ups filed; touched files unreviewed; NEXT: name the criterion (the selftest of model weights), close it, and give him the recomputed table from `D:\ClaudeWork\rimmandrake\weighted_v2\recompute.txt`
- `RIMMANDRAKE_ENACT_INVENTION_WHEN_BARS_CONFLICT_GRADIENT_TOO_EASY` — rescue brief v2 landed with his positive steps restored, "no open cases", and "takes the whole mod" (c2a56e33bd); builder, fixer and Test Pilot prompts landed (68bf672a17, 45c9c5a2d9); tester and judge changes are proposals awaiting him; NEXT: when he is back open role_prompt_upgrades_20261116.md in Typora and take his four calls, then land what he approves
- `RIMMANDRAKE_PIN_FABLE_ALIAS_TO_FIVE_TWO_FOR_SPAWNS` — filed by a helper: Agent-tool spawns with the bare alias fable may resolve to 5.1 (unmeasured); NEXT: measure one spawn's model id from its transcript and bring him the config change if it is 5.1
- `RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS` — still open from the previous handoff; two ceiling releases (rel-d355a652e496, rel-5788c9fe1df8) are unfolded hand acts; NEXT: file the item that makes a ceiling-paused mod raise a RAISE FIRST line to the Conductor and fold both acts into it (`maturation_hands.py fold <act> --item <ID>`) before the one-day alarm
- `RIMMANDRAKE_RELEASE_CONTAGION_JUDGE_ONE_LOOK_HIS_WORD_GIVEN` — owed item, parked: Contagion is held by the owner; NEXT: leave it parked until he lifts the Contagion hold

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A closing report's "untested or open" list is work: the 21 unlaid poses were a real bug across 1,969 of 13,248 poses (filed: lessons)
- An in-window code helper's uncommitted edits in the shared clone block every publish; publish urgent lines from a clean scratch clone; `scratch_clone.py clone` takes the purpose first (filed: lessons)
- The Dispatch tick reads /home/mandrake/rm/dispatch (origin): an unpublished journal hold holds nothing; hold the stages when a Fable takes a whole mod (filed: lessons)
- Times told to him are read from `date` each turn; a Monitor over the Conductor log must exclude restart:BENCH lines (filed: lessons)
- Two games: Steam refuses game a while game b runs (see: RIMMANDRAKE_LAUNCH_BOTH_GAMES_STEAM_REFUSES_A_BESIDE_B)
- Never write "the family" bare to him or in a prompt (see: memory never-say-the-family-bare)
- `pkill -f <pattern>` in a compound command killed my own shell mid-command; kill by pid from `ps | grep "[x]..."` (see: ~/.claude/CLAUDE.md, never pkill -f your own literal)

## Closed since the last handoff (38)

- `RIMMANDRAKE_REPIN_GRAFFITI_UGLINESS_BAR_STAT_NOBODY_INSPECTS` — 1bee0c2e9634
- `RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN` — 6ecfb14c822b
- `RIMMANDRAKE_STOP_KNOCKBACK_THROW_AT_PAWN_ON_PIT_COVER` — 42225e0686a331386267dfe27628448d52039610
- `RIMMANDRAKE_RESCUE_PYRELANDS_BLACK_RAIN_DOUSES_NEEDED_FIRE` — 49e11870b4b4
- `RIMMANDRAKE_JUDGE_EXPLOSIVEKNOCKBACK_BLIND_CYCLE_FIVE` — 63348273c47d3ef831f1a7e3768c32da56adc1e0
- `RIMMANDRAKE_TEACH_RESTORE_CHECK_CLOSURES_PYRELANDS_TRIPPED_EK` — 20eca8db5d96
- `RIMMANDRAKE_ROUTE_EXPLOSIVEKNOCKBACK_CYCLE_FIVE_FAILURES` — e86a6e36f6b9
- `RIMMANDRAKE_SIT_GSS_OWED_EXAM_AND_JUDGE_LOCKED_FIRST` — 45c9c5a2d9
- `RIMMANDRAKE_CHALLENGE_GSS_BLIND_RESTS_ON_ONE_TEST` — 45c9c5a2d9
- `RIMMANDRAKE_JUDGE_GIMMESOMESLACK_BLIND_CYCLE_TWO_TESTS_FIRST` — 45c9c5a2d9
- `GSS_SCENES_BUILD_EVERY_CORD_A_FOIL` — 45c9c5a2d9
- `GSS_SCRIPT_MEASURE_SITE_PREP_AND_CONTROLS` — 45c9c5a2d9
- `GSS_TREE_RECONCILE_FRESH_EYES_VS_OLD` — 45c9c5a2d9
- `RIMMANDRAKE_ADVANCE_GIMMESOMESLACK_OFFLINE_BESIDE_THE_PILOT` — 45c9c5a2d9
- `GSS_MODERN_STRIP_BUILD_PLUGS_AT_LAST` — 45c9c5a2d9
- `RIMMANDRAKE_DECIDE_GSS_HANGING_SWAY_LOST_ITS_ONLY_CORD` — 45c9c5a2d9
- `RIMMANDRAKE_CARRY_GSS_GATE_ROWS_SCENES_NEVER_SAW` — 45c9c5a2d9
- `RIMMANDRAKE_BIND_SLACK_STUB_ANGLE_RULE_FOURTH_ASK` — 45c9c5a2d9
- `RIMMANDRAKE_STEADY_GSS_FAULTED_GRAPH_JOB_NEVER_SETTLES` — 45c9c5a2d9
- `RIMMANDRAKE_ADVANCE_PYRELANDS_PAST_OFFLINE_BUILD` — bb6d1e8972
- `RIMMANDRAKE_ADVANCE_PYRELANDS_OFFLINE_BESIDE_THE_PILOT` — bb6d1e8972
- `RIMMANDRAKE_CHALLENGE_PYRELANDS_BLIND_JUDGE_REFUSED_FIRST` — bb6d1e8972
- `RIMMANDRAKE_SIT_PYRELANDS_OWED_EXAM_AND_JUDGE_LOCKED_FIRST` — bb6d1e8972
- `PYRELANDS_SCORCHFRUIT_SOURCE_VERIFY_BUILT` — bb6d1e8972
- `RIMMANDRAKE_TRIPLE_FIREHAWK_REACH_PREFERS_FARTHEST_FUEL` — bb6d1e8972
- `RIMMANDRAKE_ANNOUNCE_FIREHAWK_EMBER_LETTER_ON_FIRST_SIGHTING` — bb6d1e8972
- `RIMMANDRAKE_ACCEPT_PYRELANDS_IN_GAME_RAIN_FIX_NEVER_RUN` — bb6d1e8972
- `RIMMANDRAKE_ADD_PRISTINE_EMBERHAWK_CRESTFEATHER_HUNT_TROPHY` — bb6d1e8972
- `RIMMANDRAKE_EXTEND_NO_RAIN_SCENE_WITH_FORCED_WEATHER` — bb6d1e8972
- `HARNESS_REPAIR_CAUSE_17704C88` — 361469752f
- `RIMMANDRAKE_DROP_THROWS_INTO_COVERED_PITS_K08_MUST_FLIP` — 610b127ba830
- `RIMMANDRAKE_AUTOBUILD_PYRELANDS_ZERO_BARS_LEFT` — 2a81b79286
- `RIMMANDRAKE_AUTOBUILD_PYRELANDS_ZERO_LEFT` — 2a81b79286
- `RIMMANDRAKE_CLEAR_STALE_BLOCK_REASON_ON_LIFT` — 2a81b79286
- `RIMMANDRAKE_PROPOSE_RESCUE_WHEN_MOD_CIRCLES_BOTH_HAND_LAUNCHED` — ce15651c27
- `RIMMANDRAKE_UNDO_REFUSED_PUBLISH_COMMIT_NEXT_RUN_LANDED_IT` — c3dfdd729335
- `RIMMANDRAKE_GUARD_PROOF_VERDICTS_FIVE_WEAKENED_STAYED_GREEN` — 3792dbb557
- `RIMMANDRAKE_LIFT_PROOF_VERDICTS_INTO_TESTED_CODE_NINE_SLIPPED` — 3792dbb557

## Filed and still open (34) — the next seat's queue

- `RIMMANDRAKE_TIE_GRAFFITI_REPIN_TEST_TEXT_COMMIT_NO_CARD` — designer_stage repin refuses Graffiti: 68f199064a moved scenes as test text, re-pinned in bars.md only, tied to no card
- `RIMMANDRAKE_RECALIBRATE_COVERAGE_BRIEF_UNTESTED_SINCE_LAST_EDIT` — coverage_judge brief reads UNTESTED since its last edit: every coverage refusal is advisory
- `RIMMANDRAKE_RETRY_OWED_ACTIONS_JUDGE_UNLAUNCHED_QUESTION_STUCK` — GPT's first step of work (review 2026-11-16, gpt_review_pipeline_changes_20261116.md §5): every owed action (a stage launch, a question to the owner) 
- `RIMMANDRAKE_LAY_SLACK_CLOSE_FITTINGS_TWENTY_ONE_UNLAID` — Gimme Some Slack: the 21 of 288 close-fitting poses the live-end lay left unlaid are laid, or proved unreachable in game by a permanent check. Accepta
- `RIMMANDRAKE_HIDE_SPEND_IN_PROMPTS_COST_LINE_SURVIVED` — Spend still reaches launched agents through prompt text, against the owner's 2026-11-16 ruling (no launched agent is told its spend): relentless.py:48
- `RIMMANDRAKE_RUN_PYRELANDS_WEEK_SKY_FREE_NEVER_ONCE_SEEN` — Pyrelands visit 2: run the wind-carried burn live, then a walked week with the weather unlocked and the fire mechanics on, and read the burn stamps (n
- `RIMMANDRAKE_SHOVE_PAWNS_STANDING_ON_COVERS_IN_BURNING_GAS` — ExplosiveKnockback Polish (gas_goes_clump_by_clump): RM_MapComponent_Knockback.PawnSkipReason and Execute skip anything on a superdeep cell as in_pit 
- `RIMMANDRAKE_TEST_WALK_FRAME_JUDGE_OFFLINE_TWO_MUTANTS_LIVED` — ExplosiveKnockback Polish (walk_storeroom_raid): PF_V_FRAME_OVER_LOOSE (10% -> 50%) and PF_V_FRAME_ROW_ALWAYS_PASS in validation.py survived every off
- `RIMMANDRAKE_NOTE_KNOCKBACK_CALLER_MUTANTS_OWED_TO_STAGE_SIX` — ExplosiveKnockback Polish (the_spared): 10 planted faults in game-side callers survived offline, as expected for Verse code: PF_MC_GRID_IGNORES_PAWNS,
- `RIMMANDRAKE_POOL_ELIGIBLE_FINISH_ITEMS_LEFT_OUT` — selftest_relentless t_real_effects red on the real ledger: 2 eligible needs=bridge FINISH items absent from pool_order
- `RIMMANDRAKE_FLAG_NUMBER_ONLY_DIFFS_IN_MATURATION_NEXT` — maturation.py next prints a note when a builder's diff changes only numbers (tuning tripwire T1; never refuses)
- `RIMMANDRAKE_LIST_THINNEST_MARGINS_IN_CERTIFICATE_RUN` — maturation.py certificate --run lists the thinnest margins first and the checks that print no margin (T2; verdict unchanged)
- `RIMMANDRAKE_MEND_SLACK_FRESH_BUILD_DIFFERS_BY_ONE_EDGE` — GSS live: a fresh CordBuilder differs from the incremental one on matrix board B00_ground (F00_T0_S0, D00_n1_S0: 1 edge missing, 1 extra): D2 FAIL; pa
- `RIMMANDRAKE_RULE_SLACK_UNDER_CHECK_IGNORES_DEPTH_WRITE` — GSS check judged wrong: scene_rows.under_verdict fails a cord piece queued 2901 under a Cutout thing queued 2900, though the thing writes depth and th
- `RIMMANDRAKE_RETIRE_SLACK_ROWS_WANTING_SPARKING_WALL_ENDS` — GSS older proof rows M1_node_census, B4_downed_wire_bursts, B4d_spark_budget_shared_visible_first need a live sparking WALL end, which the owner's 202
- `RIMMANDRAKE_BEND_SLACK_BOX_LEADS_NINETEEN_OFF_SLOPE_LIVE` — GSS live stub joins FAIL on the owner's review map: 19 of 399 joins off slope (box T 15, box X 2, plug 2), 1 off line, 4 empty stubs, worst 83 deg at 
- `RIMMANDRAKE_STOP_GAME_B_TRIAL_LEFT_RUNNING_BLOCKS_STEAM` — Second-game trial left game B (pid 39464) running 8 h idle; with it up, Steam ignored two launches of game a (steam://rungameid/294100)
- `RIMMANDRAKE_WEIGH_TOKENS_BY_MODEL_OPUS_INPUT_UNIT` — Weigh spend tokens by model too (weighted_v2: list price per field / Opus 5.5 input price; one table MODEL_PRICES in role_launch). Acceptance: selftes
- `RIMMANDRAKE_MEND_SLACK_DEAD_CUT_END_MISSING_FROM_ENDS` — GSS live: after a one-cell cut the dead end is drawn (frayed, dark) but absent from the probe's ends list (LaidPiece.Ends): M8 east=null; passed 05:42
- `RIMMANDRAKE_ALIGN_PILOT_SKILL_WITH_SITTING_HOLDS_BRIEF` — test-pilot-sitting skill: align three lines with the brief's HOW A SITTING HOLDS steps (skill not edited on order)
- `RIMMANDRAKE_PIN_FABLE_ALIAS_TO_FIVE_TWO_FOR_SPAWNS` — Set ANTHROPIC_DEFAULT_FABLE_MODEL=claude-fable-5-2 so a bare 'fable' spawn (Agent tool, agent-file frontmatter) is Fable 5.2, not 5.1
- `RIMMANDRAKE_UPGRADE_DESIGNER_CLEANSE_SIXTY_FOUR_BARS_LOCKED` — Designer Cleanse: comprehensive mod definitions, extras to next version, a new definition of a bar, mass Codex runs on every biome but Pyrelands
- `RIMMANDRAKE_SPARE_EXPERIENCE_GAPS_FROM_BAR_WORD_DETECTOR` — bar_rule.detect demotes real experience gaps: bare 'ingestible' (bar_rule.py:45) fires whatever the judge called the gap
- `RIMMANDRAKE_SPLIT_SLACK_WALK_FAILS_FULL_LIST_OR_MOD` — GSS sc_walk FAIL on the full list (316 mods): cords (no cord to a lamp hooked to the conduit; reconnect live != fresh) and ui 2/24 (free-end toggle st
- `RIMMANDRAKE_RELEASE_SLACK_PIPELINE_HOLD_WHEN_FABLE_ENDS` — When the Fable run on RIMMANDRAKE_LAY_SLACK_CLOSE_FITTINGS_TWENTY_ONE_UNLAID ends: append kind release lines for stages 6, 3 and 4+5 to design/concept
- `RIMMANDRAKE_LAUNCH_BOTH_GAMES_STEAM_REFUSES_A_BESIDE_B` — Both RimWorld games can be started in either order and a live run picks a free one: Steam refuses game a while game b runs, and a launched without Ste
- `RIMMANDRAKE_UNFENCE_LIVE_HOLDER_WHEN_RIVAL_NEVER_STARTED` — Pipeline: Dispatch granted EK lease token 13 to run-1794896974 one minute after live holder run-1794896914 (token 12); B ended never_started 7 s later
- `RIMMANDRAKE_FREE_PYRE_SITE_SKY_TUTOR_PINS_CLEAR_FOREVER` — Pyrelands test sites are saved with the Tutor storyteller, so their weather never leaves Clear even unlocked
- `RIMMANDRAKE_MIGRATE_STORE_SPEND_TO_WEIGHTED_V2_WITH_LIMITS` — Relentless store spend and item_spend_limit/run_reserve still weighted_v1
- `RIMMANDRAKE_SHOW_PYRE_GRASS_UNDER_ASH_COVER_COUNTED_UNSEEN` — After the ash falls on a Pyrelands map the grass carpet stops being drawn: the map reads bare grey ash while 81 percent of open ground holds grass
- `RIMMANDRAKE_WIDEN_PYRE_BURN_FRONT_COMB_LANES_NOT_SWATHE` — The wind-carried Pyrelands burn reads as thin scratches and comb lanes, not a grass fire moving across the map
- `RIMMANDRAKE_STAMP_STAGE_SPEND_ROWS_ONE_UNIT` — maturation.py stage spend rows mix weighted_v1 history with weighted_v2 rows
- `RIMMANDRAKE_CONVERT_DESIGNER_BUDGETS_TO_WEIGHTED_V2` — designer_stage DEFAULT_CAP 4,000,000 and stored concept budgets still weighted_v1
- `RIMMANDRAKE_RELABEL_SPEND_PRINTERS_STILL_V1` — spend printers that still show weighted_v1 history: relentless_strikes, relentless.py item_spend_limit note, maturation stage spend

## Commits

```
85a5f732ce ledger: L0 verify pass for RIMMANDRAKE_WEIGH_TOKENS_BY_MODEL_OPUS_INPUT_UNIT at 381db58f59
f93f3ef7e2 ledger: RUNNER ingest of 0 testq job(s)
8128d8b461 Found by the whole census on 9ed2b6e1d77b (1 of 75,582 live ends left as handed, whip removed: random world 257). That world and door rooms are challenge cases in the suite (RIMMANDRAKE_LAY_SLACK_CLOSE_FITTINGS_TWENTY_ONE_UNLAID).
4b24d787a0 acceptance: RIMMANDRAKE_FREE_PYRE_SITE_SKY_TUTOR_PINS_CLEAR_FOREVER; ledger: pyre week readings
a715d909d3 ledger+lessons: weighted_v2 follow-up items (store spend, stage rows, designer budgets, printers) and five findings
deb4e85d17 ledger: live sweep OPS_SCRATCH_DIRT_MEASURE_AT_END_YOGQ kept
c2a56e33bd fable_rescue: a rescue takes every ticket its mod needs for the version (owner 2026-11-16)
b6abd9ba93 ledger: RUNNER ingest of 0 testq job(s)
381db58f59 Weighted tokens are weighted by model too: unit weighted_v2 (Opus 5.5 input = 1)
b8593bded1 ledger: RIMMANDRAKE_LIFT_PROOF_VERDICTS_INTO_TESTED_CODE_NINE_SLIPPED clone bundled
13454d44b2 conversations: catch-up 1 record(s)
f5e09906db modledger: run.end of ended pilot runs (Dispatch step)
eaa2e656fc maturation: spend rows of ended runs (Dispatch step)
c1a3bc8855 ledger: RUNNER ingest of 0 testq job(s)
bbf418e79a ledger: detached run on RIMMANDRAKE_LIFT_PROOF_VERDICTS_INTO_TESTED_CODE_NINE_SLIPPED ended
686d6d788c ledger: close RIMMANDRAKE_LIFT_PROOF_VERDICTS_INTO_TESTED_CODE_NINE_SLIPPED and the five-weakened sibling at 3792dbb557; 7 Stage-6 checks UNRUN Files RIMMANDRAKE_UNFENCE_LIVE_HOLDER_WHEN_RIVAL_NEVER_STARTED with its repro (red at 3792dbb557).
7302fbbf18 maturation: spend rows of ended runs (Dispatch step)
f364c15501 ledger: RIMMANDRAKE_ROUTE_GIMMESOMESLACK_VISIT_ONE_FAILURES_BACK clone bundled
e088dd074a conversations: catch-up 1 record(s)
de15b5b606 ledger: detached run on RIMMANDRAKE_ROUTE_GIMMESOMESLACK_VISIT_ONE_FAILURES_BACK ended
... 168 more: git log --oneline de2dd0e8b9..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running; BRIDGE NOT PROBED — no port found in the environment or in Player.log, so LOADING here is a DEFAULT, not a reading.)
- recorded  : DOWN  → corrected to LOADING, measured now
- Bridge: other   archmagi.b  BENCH  since 2026-11-17T06:58:29Z  for: pyre week reshoots

Working tree clean apart from untracked `Transient/`.

