# BENCH_REBOOT_HANDOFF_202610292353 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610290748`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
v2's simulated lead was the owner's live steering, not autonomy: in its fit week he was active 72% of minutes (85 msgs/day, ~123 touches/day vs 28 assumed), helper launches ~3x higher when present; autonomous-only v2 ~25 closes/day (ESTIMATE). The owner then pivoted the architecture question to SIMPLE designs (Ralph loop; his Conductor + FOUNDRY[Ralph builder + blind critic] + TestPilot-per-machine, merged as TP+) decided by a REAL trial in days, not more simulation: design/RimMandrake/testpilot_merged_2026-10-29.md + architecture_switch_harness_2026-10-29.md. Binding on every design (owner 2026-10-29): "a different agent tests what was built", promptly after the build.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Trial decisions he took today (ledger notes on TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD): design cards from every arm equally (no debugging); reloads scale with reload cost, never exhaustive, targeted re-tests; 1.5x tokens for 3 measuring days; a win switches production IMMEDIATELY; minimal mod list only in the trial.
- Goodbye restart is ON by his word ("If I'm typing at the same time it's an acceptable risk."); the BENCH context backstop is OFF (only he spoke of the goodbye).
- Conductor helpers: unlimited only within 20 min of his last typed message, else 2; helpers >1 h alarm (d9b43e13a6).
- FOUNDRY model rule (his words, Agent_Policy.md dc737cf2c0): Sonnet for test-checkable code, Opus for hard-to-validate code and subjective work.
- Archmagi: while he is not playing, the 20-min idle wait for agents does not apply (flyers still never without him).
- Diagrams page: https://claude.ai/artifact/DC1BrF9fACDNrKWEWZMKxH. Unanswered: SteveDesktop setup steps are his, at the machine, from 2026-10-30; card D (hose/wall hitch) and the art-judge page wait for him.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `AUDITOR_BUILD_WAITING_INDEX_REQUEUE_SCAN` — parked by owner card pending the architecture decision, patch D:\ClaudeWork\rimmandrake\v3_build\roles\parked.patch; NEXT: drop it if the trial winner has no Auditor, else apply the patch and blind-review
- `HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES` — parked by owner card, patch in v3_build\roles\parked.patch; NEXT: drop it if the trial winner has no scheduled roles, else rebuild against the 20-min Conductor exemption
- `INNOVATOR_BUILD_EXPIRY_WATCHDOG_REVERTS` — parked by owner card, patch in v3_build\roles\parked.patch; NEXT: drop it if the trial winner has no Innovator
- `OPS_MODEL_BUILD_V3_TWIN_FIT_DAILY` — parked (owner card), patch D:\ClaudeWork\rimmandrake\v3_build\model\parked.patch; the sim must model owner presence (lesson 2b61ea3c42); NEXT: decide after the trial whether the process model is still wanted, then drop or resume
- `RALPH_LOOP_DESIGN_ONE_PROMPT_FOREVER` — design + sim done and GPT-checked (92a49748e4), folded into the TP+ merge; NEXT: close it citing testpilot_merged_2026-10-29.md once the trial items are filed
- `TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD` — owner decisions folded into the merged and harness docs (82f98c499a); 16 ARENA_* trial-build items filed --for FOUNDRY and raised in build order (ledger 3c63d8bcea), every arm made to satisfy 'a different agent tests what was built, promptly'; NEXT: watch FOUNDRY start ARENA_TASKS_BUILD_FROZEN_BEFORE_ASSIGNED and route each Opus-class ARENA item to an Opus builder per Agent_Policy.md
- `V3_HEALTH_BUILD_DAILY_PULSE_DAY_ONE` — step 1 landed (role_unit stamp 36936b258f), rest parked (v3_build\health\parked.patch); NEXT: drop or rescope after the trial picks an architecture

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- The process simulator ignores owner presence, so v2 looks autonomous when it was steered (filed: lessons 2b61ea3c42).
- `rimflow next --seat <OTHER>` takes a real lease as that seat in your clone (filed: lessons 2693899fce).
- `rimflow close` without the content sha, or an agent citing a pre-./publish local sha, records the wrong commit; seen 3x today (see: CLOSE_SHA_FIX_HEAD_FALLBACK_CLAIM_COMMITS).
- Opus-built code failed first blind GPT review 3 of 3 today; loops converged only for the small single-purpose module, and the goodbye and fold converged only after simplification (see: testpilot_merged_2026-10-29.md, brief lessons).
- Parking an item with `drop` kills it; park with release + note (see: conductor log 2026-10-29).

## Closed since the last handoff (8)

- `STEVE_LANE_UNSTICK_PAUSED_UNOWNED_F27F` — e500e9680840
- `LESSONS_KEEPER_WIRE_AUDITOR_GETS_THE_BROOM` — a179f81c7738a93544ecf5f61d4f6228cd567150
- `STEVE_LANE_UNSTICK_PAUSED_UNOWNED_15B5` — 1840f6a2a9
- `CONDUCTOR_HELPERS_TUNE_TWENTY_MINUTE_WINDOW` — d9b43e13a66fcf399b55d971ec6fbe4a05dcac46
- `AUDITOR_BUILD_HARD_FLAG_FILER_NO_AI` — 5ce76d059b59
- `FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X` — 4c0b13067d9e
- `FLOWWORKS_OWNER_RECONCILE_CUTOVER_STALE` — dea2fee7d4
- `COMPANION_GRANT_WIRE_LAPSES_AT_BEDTIME` — dd1384f31913

## Filed and still open (24) — the next seat's queue

- `CLOSE_SHA_FIX_HEAD_FALLBACK_CLAIM_COMMITS` — close --sha fell back to HEAD: FOUNDRY_CLONE_SYNC_STALE_TIMERS and FOUNDRY_SHARD_RESCUE_STRANDED_EVENTS closed on ledger-only claim commits
- `TESTQSTEWARD_FIX_ESCALATES_TO_A_GHOST` — steward.py escalates/wakes on an item ID it never filed (STEVE_LANE_UNSTICK_PAUSED_UNOWNED_F27F: claim said 'never been filed')
- `RUNNERCLONE_FIX_STRANDED_BY_HISTORY_REWRITE` — Other SteveDesktop clones (~/rm/bench, ~/mutation/RimMandrake) likely still on pre-excise history; ~/rm/runner was moved 2026-10-29 (old head = branch
- `QUARRY_DIG_FIX_VALIDATED_BUT_NEVER_FINISHES` — Quarry dig job never finishes on the test machine (26 failed / 41 partial runs) while FLOWWORKS_QUARRY_DIGGING_1 stands validated
- `FLOWWORKS_REDROWS_PROVE_FIXED_STILL_FROWN` — FlowWorks: re-run the stale red proof rows of the closed fixes on the current build
- `IMPLEMENTED_SPEED_AUDIT_DONE_IN_TWO_MINUTES` — Audit FOUNDRY items marked implemented 1-3 min after claim since the v3 cutover (Producer-raised items): real work or a fast close? Source: D:\ClaudeW
- `V3_HEALTH_BUILD_DAILY_PULSE_DAY_ONE` — Daily v3 health check by one responsible role: (1) tag owner messages keep-going/failure/direction for the kill test, (2) plant known faults and time 
- `OPS_MODEL_BUILD_V3_TWIN_FIT_DAILY` — Operational process model: v2 model fit only to v2 logs (frozen), v3 model with its own workflow parameters, both sharing a like-for-like pipeline cor
- `BOUNCE_GATE_FIX_SHAS_ORPHANED_BY_REWRITE` — Arbiter bounce gate G1_sha fails every claim closed before the 2026-10-29 history rewrite: 38 distinct pre-rewrite shas (64 of 67 bounces in D:\Claude
- `ARBITER_DOCGROWTH_WIRE_PASS_HAS_NO_DOORBELL` — The Arbiter doc-growth pass (roles/arbiter.md, a179f81c77 + 44b85e8d16) has no launch path: dispatcher_schedule.json Arbiter pending_work lists escape
- `V3_WORKFLOW_AUDIT_EVERY_CLOCK_AND_DOOR` — Document the whole RimFlow v3 agent workflow (appear/disappear, criteria, runs/day, arbitrary settings, handoffs); GPT deep skeptical review vs litera
- `PRESCREEN_SHAS_FIX_LOST_IN_THE_REWRITE` — Audit pre-screen and Arbiter tiers are blind on every close made before the origin/main history rewrite: 80 of 84 close shas (95%) no longer resolve, 
- `STEVE_WORKBAR_DIAGNOSE_MANUAL_PRIORITIES_OFF` — SteveDesktop droid_dig rows DD_droid_digs_past_2m UNMEASURED HARNESS: work bar did not take (Mining=1, manual priorities still OFF, readBack is the co
- `RIMFLOW_V3_BUILD_WHAT_WAS_ONLY_PROSE` — Build every DESIGNED-not-built part of RimFlow v3 now (as-built doc §2.19, §8 items 11-17 + config/doc disagreements 1-5), each followed by a blind Co
- `RIMFLOW_V3_SHRINK_FEWER_CHAIRS_SAME_JOBS` — Collapse RimFlow v3 to the fewest parts without loss of function, settled with the owner before freezing; build-test-until-pass-then-blind-review loop
- `CONDUCTOR_CLOSEOUT_BUILD_LEDGER_CHECK` — conductor_closeout.py check: program check of B2 step 1 (his rulings and answers in the window vs the ledger) before the goodbye restart
- `CONDUCTOR_IDENTITY_FIX_HELPERS_NEEDLE_GONE` — selftest_conductor_identity FAILs: CONDUCTOR.md no longer states 'helpers run in session mode only' (pre-existing before the goodbye build)
- `SCHEDULE_PRUNE_UNREAD_HELPER_KEYS_SIM_ONLY` — dispatcher_schedule.json keys no runtime reads: throttle_order (only Utils/sim/rimflow_v3_sim.py), throttle_bands.*.session_helpers_max, roles' helper
- `OPSWATCH_FINDINGS_WIRE_READ_THE_FOLD` — ops_watch still counts all 131 findings as untriaged and ignores findings_fold's output; count only unfolded/unjudged findings (fold state in D:\Claud
- `SELFTESTS_MAIN_REPAIR_TWO_RED_AFTER_REWRITE` — selftest_role_tokens and selftest_conductor_identity fail on main after today's doc/config rewrites; find the commit that broke each and fix the code 
- `RALPH_LOOP_DESIGN_ONE_PROMPT_FOREVER` — Deep design pass: the best simple Ralph loop for RimMandrake's goals (variant: a second Ralph loop on SteveDesktop); simulate it against v2 and v3 est
- `HUMAN_INPUT_READERS_AUDIT_QUEUED_PROMPTS` — Audit last-human-message readers for queued_command prompts
- `FOUNDRY_BACKSTOP_REPAIR_CURSOR_HIDES_INPUT` — Goodbye review 3 findings P0-2 (backstop cancel cursor can hide a newly arrived human message) and P1-3 (historical notifications defeat the backstop)
- `TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD` — Evaluate owner's three-agent design (Conductor + FOUNDRY with Ralph builder/critic subagents + TestPilot live tester that fixes in-session, reloads on

## Commits

```
565578d57c conversations: catch-up 18 record(s)
fbb1a264d5 ledger: FOUNDRY Contagion site fix implemented
6c79b7d15f ledger: FOUNDRY Contagion site fix, resubmitted
bb6024a4a7 lesson: targeted modcheck runs drop cross-chain setup
6a55588ffb CONTAGION_SITE_FIX_RETILE_LEAVES_THEROT: on-Contagion chains retile the map themselves in a targeted run
2b768d03d9 ledger: owner: different-agent test, promptly, in every design
65f4917705 ledger: RUNNER ingest of 1 testq job(s)
01b25f45a3 ledger: owner decisions for the architecture trial
b6a022acb0 ledger: DISPATCHER notes (1)
33cad8e154 ledger: owner role in trials (design cards, not debugging)
77e99952fa design: TestPilot round 3 merge (TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD)
49eadd875c design: TestPilot round 2 answer to GPT design, sim --scenario gpt/gpt_guard/gpt_1G (TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD)
2b61ea3c42 lesson: simulator ignores owner presence; v2 lead is his steering
7f600d72da ledger: DISPATCHER notes (1)
e1a10f95c0 ledger: RUNNER ingest of 1 testq job(s)
bc31f0103d ledger: RUNNER ingest of 1 testq job(s)
96201b0cab ledger: DISPATCHER notes (2)
eed8ec158f design: TestPilot (Foundry+TestPilot+Conductor) evaluated + improved TP+, sim vs zoo, selftest (TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD)
36e72bdd11 ledger: DEEP_DIG row 3 PASS, item done
46e98c2d50 ledger: RUNNER ingest of 1 testq job(s)
... 284 more: git log --oneline 3c3ab21c48..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-29T21:11:06Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M design/RimMandrake/architecture_switch_harness_2026-10-29.md   — the trial-ticketing helper; since committed in 82f98c499a / 3c63d8bcea
 M design/RimMandrake/testpilot_merged_2026-10-29.md   — the trial-ticketing helper; since committed in 82f98c499a / 3c63d8bcea
 M infrastructure/state/ledger/events/BENCH.jsonl   — the trial-ticketing helper; since committed in 82f98c499a / 3c63d8bcea
```

