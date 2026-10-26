# BENCH_REBOOT_HANDOFF_202610262128 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610261756`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Token pacing is now automatic and enforced: `slot_allocator.py now` sets N per seat from the account meter (`account_usage.py`) every 15 min, and a PreToolUse hook REFUSES Agent spawns over N (it blocked me twice today; that is it working). Owner rulings behind it: interactive overage is allowed and repaid later (`SLOT_OVERAGE_BUILD_PAYBACK_LATER`, done); his `set --seat BENCH --n 4 --owner-said ...` override expires 2026-10-27 13:14; the "steven" account is off-limits until its reset Wed 10-28 15:00 and capped 50%/10%-floor after (memory steven-account-is-steves-use-sparingly). SteveDesktop now logs in as the.mandrake.system account by his word, and runs with `bcdedit numproc 18` because logical CPU 18 computes wrong hashes (revert: `bcdedit /deletevalue {current} numproc`). The owner reviews remotely through claude.ai artifacts (his device is NOT on the tailnet): `sheet_to_artifact.py` -> publish with `capabilities {db:{}}` -> read picks with ArtifactData -> `sheet_artifact_merge.py --apply`.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Review page live, 5 questions (~3 min):** https://claude.ai/artifact/NvWyM4dbx3UEhRjPR8FTgh (FlowWorks building looks: Desal, Detox, Pumping, Tar sets; ferry rope). Read picks with ArtifactData `list picks`, merge with `sheet_artifact_merge.py`. His earlier 20 picks are saved in D:\ClaudeWork\rimmandrake\sheet_artifact\flowworks_walk_picks_20261026\ (10 clean ones merged).
- **Design review page:** https://claude.ai/artifact/HcaHSQ1nFExpuf9WPQHPa4 (orchestration review; source design/RimMandrake/orchestration_review_2026-10-26.md). He has NOT yet answered single-primary cards D1-D7 nor the operating-modes questions.
- **His many questions for the next card session** are verbatim in `infrastructure/state/items/OWNER_QUESTIONS_DESIGN_RICH_CARDS.md` (context self-management, tracking, FOCUS on 1-2 mods vs one-worker-per-mod, blocked-by planning, a computed this-week plan with REAL tick-offs; no UI building). Cards must be rich with context.
- SteveDesktop CPU 18 fault mitigated, real fix (CPU/BIOS) is his call: `STEVEDESKTOP_DIAGNOSE_CPU18_FLUNKS_MATH`.
- Muttavaq s1r3 installed on his word; polish later: `MUTTAVAQ_ART_POLISH_NORTH_SIZE_AND_FACE`.
- PAYDOWN is on (A1 ~154 art picks waiting incl. the rebuilt GSS sheet, D1 32 items >3 d): no new art generation; the facing audit is paused with ~36 regens filed.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `HOSE_DRAW_FIX_STALLS_WHILE_WORKER_LAYS` — fix ee99572366 deployed by live round 7 helper (still running at handoff, holds the bridge); NEXT: read its report and close or file per its verdict.
- `GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS` — fix 0f395589f2 in live round 7; NEXT: read round 7's gslice verdict and close the item and GSS_SLICE_FIX_EDGE_OVERSHOOTS_BUDGET on a pass.
- `COLD_STORAGE_PROOF_VERIFY_ROT_RATES_LIVE` — rates PASS in round 6; sealed/aging/wall/gravship plus the carbon-press smoke in round 7; NEXT: read round 7 and close or file.
- `SINGLE_PRIMARY_DESIGN_RETIRE_FOUNDRY_WINDOW` — design done d45d727e81, amended by orchestration_review 31d7807888; NEXT: put cards D1-D7 (amended) to the owner with rich context, together with OWNER_QUESTIONS_DESIGN_RICH_CARDS.
- `OWNER_QUESTIONS_DESIGN_RICH_CARDS` — filed with his verbatim questions; NEXT: draft the answer cards (data sources for focus, blocked-by, weekly plan, real tick-offs) before he is next at the bench.
- `FWSHEET_BUILDING_LOOKS` (sheet `flowworks_building_looks_sheet_2026-10-26`, served as the artifact above) — awaiting his 5 answers; NEXT: ArtifactData list picks, then `sheet_artifact_merge.py --apply` and enact.
- `PIT_CAPTURE_FIX_WARDEN_HURT_AT_LIP` — S7 capture unmeasured (warden hurt at the lip every run); NEXT: diagnose the attacker offline, then re-run S7.
- `JAWABENCH_TPSARCHIVE_FIX_SKIPPED_AFTER_FAULT` — CPU-18 fix makes SteveDesktop trustworthy now; NEXT: run 20 cold starts on SteveDesktop and close both JAWABENCH items if no new Crash_* folder.
- `FACING_AUDIT_BUILD_REDRAW_BATCH` — paused under PAYDOWN (~36 regens filed, unrendered); NEXT: resume only when the owner's waiting art picks are under 100.
- `HOSE_CROSS_FIX_LEGACY_TOGGLE_STALE_INDEX` — low, debug-only; NEXT: fix when the next FlowWorks builder is free.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Finished background agents can stay listed RUNNING across /clear. (filed: lessons 20261026T182554Z; machine-level sweep in Lodestar ae26a228)
- A pre-reviewed sheet still asked a malformed question (mixed objects, split coupled states); prereview now checks sheet shape. (filed: lessons 20261026T205345Z)
- A bad CPU core makes hashes differ run to run, so mod-hash attestations read UNMEASURED. (filed: lessons, see STEVEDESKTOP_DIAGNOSE_CPU18_FLUNKS_MATH)
- testq brake only cleared on FILLER jobs, so a hand-submitted DONE never released it; and the dispatch clone could not see modcheck. (filed: lessons 20261026T195400Z)
- Helpers rebuild in the seat clone and leave files identical to origin uncommitted, blocking ./publish; compare `git hash-object` to origin and checkout the identical ones. (filed: infrastructure/state/lessons/20261026T212933Z-BENCH-helpers-that-rebuild-or-install-seat.md)

## Closed since the last handoff (34)

- `REVIEW_MAP_FILL_FIVE_UNSTATIONED_DEFS` — 6cbfcdfc0ddb
- `GSS_PROOF_DRIVERS_FIX_FALSE_PASS` — 6cbfcdfc0ddb
- `DRAWBRIDGEPROOF_FIX_SWEEP_KILLS_COLONY` — 47a60bd154
- `MODCHECK_HARDEN_RESTORE_RAISE_LOSES_SHEET` — 47a60bd154
- `TESTQTICK_SILENCE_GIT_GC_LEFTOVERS` — 59d27b43cf
- `GSS_ASYNC_TEST_FIX_STALE_CORRIDOR_GAP` — 2987f99d6e98
- `COLD_STORAGE_CARBONFREEZE_BUILD_FOOD_PRESS` — 287d027b9fd7
- `PITWALK_FIX_HUGE_TRUNK_BLOCKERS_IN_SITE` — ed7ff8bbd2
- `PITWALK_FIX_SPRUNG_DECK_READS_ABSENT` — ed7ff8bbd2
- `PITWALK_FIX_SWIM_COMPRESSION_SKIPS_WARNING` — ed7ff8bbd2
- `PITWALK_FIX_GOVERNOR_STOP_CRASHES_WALK` — ed7ff8bbd2
- `SHADOW_ROWID_FIX_SERIES_TAG_SLIPS_THROUGH` — 78d9f9c7d285
- `SHADOW_VIEW_ROWS_FIX_MERGED_UNLABELLED` — 78d9f9c7d285
- `STEVE_STEWARD_BUILD_NO_LLM_OWNER` — 4102db4416
- `STREAM_METRICS_UNIFY_ONE_SERIES` — 8ea9cb96f36d
- `MODCHECK_METRICS_RETIRE_INTO_HOURLY` — 8ea9cb96f36d
- `RIMPULSE_STREAMS_BUILD_VS_TIME` — 8ea9cb96f36d
- `L1_DONOR_SELFTEST_FIX_UNKNOWN_COMMIT` — d13c498c40
- `TESTQ_FILL_RANK_BY_EVIDENCE_GAPS` — 78db3805c3
- `STEVE_LANE_UNSTICK_BRAKED_UNOWNED_C80D` — 78db3805c3
- `SLOT_ALLOCATOR_BUILD_RULES_FILE` — a8725799ee
- `SLOT_CAP_ENFORCE_HOOK_REFUSES_OVER_N` — e4614f3bba
- `ACCOUNT_USAGE_WIRE_PULSE_TILE_ALLOCATOR` — 76c6f0d37f
- `SHEET_ARTIFACT_BUILD_REMOTE_REVIEW_ROUTE` — e702b31687
- `SLOT_OVERAGE_BUILD_PAYBACK_LATER` — 7512d82ce059
- `CARBON_PRESS_FIX_NO_WORKGIVER_RUNS_BILLS` — cb5a4d557f
- `COLD_INSPECT_FIX_PARTIAL_SAYS_ALL_HELD` — cb5a4d557f
- `FWSHEET_CULL_MIXED_CONTAINER_ROWS` — c26e1a42b6da
- `FWSHEET_UNIFY_COUPLED_STATE_ROWS` — c26e1a42b6da
- `PREREVIEW_ENFORCE_SHEET_SHAPE` — 8bba47008bd8
- `FWSHEET_FILL_PUMPING_KLUDGED` — c26e1a42b6da
- `SHEET_ARTIFACT_EXPLAIN_ANSWERED` — f39988136f48
- `SHEET_ARTIFACT_FIX_PREFILL_ANSWERED` — f39988136f48
- `FWSHEET_DEDUPE_FORDSTONES_COLUMNS` — c26e1a42b6da

## Filed and still open (48) — the next seat's queue

- `FLOWWORKS_DIAGNOSE_FREEZE_AFTER_DRAWBRIDGE` — SteveDesktop testq J20261026T152116Z-162d96: after the drawbridges chain (59 PASS, drawbridge_proof saved RM_DRAWBRIDGE_MIDRAISE) the kept game's main
- `COLDSTART_PROVE_NTDLL_CRASH_NO_FOLDER` — SteveDesktop 15:37:00Z 2026-10-26: a fresh RimWorld (pid 25940) died ~44 s into startup, right after 'TPS sampler installed': Windows APPCRASH ntdll c
- `MODCHECK_DIAGNOSE_DRIVER_DIES_MID_SETFOG` — testq J20261026T182927Z-c2508c: drawbridge_proof exited rc1 44 s in, during prepare_site, its jawa/set_fog cid d90b07462fa14791 'client interrupted' (
- `LEDGER_MOD_FIELD_DECIDE_OR_DROP` — Decide whether rimflow items get a mod field; close-from-proposed inflates throughput
- `GSS_SLICE_FIX_EDGE_OVERSHOOTS_BUDGET` — GSS sliced planned build overshoots its 8 ms frame budget: the budget is checked between edges and one LayEdge costs ~6 ms mean, 28 ms max (live, prof
- `TESTQ_MODS_WIRE_BEYOND_FLOWWORKS` — [L ~8 h for first 5 mods] 1 of 132 harnessed mods is selectable by testq; wire the next mods by bridge backlog, with a bad_selection probe per mod fee
- `ARCHMAGI_BACKFILL_WIRE_TRIAL_SWITCH` — [S-M 3-5 h] turn the built-but-off Archmagi backfill into the §2 trial switch: S1 saturation / S2 failover / S3 never, 30-min cooldown, latched INVALI
- `OWNER_WALK_MEASURE_STAGED_AND_DONE` — [S 2 h] no ledger event marks an owner live walk or its staging (ranBy only BENCH/FOUNDRY): add walk-staged / walk-done events so W1-W4 are measurable
- `ART_OVERRIDE_MEASURE_AGENT_VS_OWNER` — [S-M 3-4 h] join art-pipeline verdicts to owner rulings so the override rate (A4) exists; feeds the shadow-sheet trust rule
- `OWNER_WAIT_RESOLVED_PROBE_ZERO_READING` — [S 1 h] rimflow_metrics owner_wait_resolved read 0 in a day with 101 OWNER events: probe whether resolutions without a needs change are invisible (ins
- `STEVEDESKTOP_DIAGNOSE_CPU18_FLUNKS_MATH` — SteveDesktop's logical CPU 18 computes SIMD results wrongly: Windows python.exe pinned to CPU 18 (start /affinity 40000) hashes the same buffer with s
- `COLD_STORAGE_CARBONFREEZE_REDRAW_INTERIM_ART` — Carbon-freezing press line draws vanilla interim art: own art for RSW_CarbonFreezingPress (2x2, Graphic_Multi, drawSize 3, now SerumCentrifuge), 4 RSW
- `PIT_CAPTURE_FIX_WARDEN_HURT_AT_LIP` — S7 RM_CaptureDown: warden at the pit lip hurt (Scratch, Crack) while the held undowned hostile is 4 m below; capture never completes. MOD presumed, at
- `ART_EVAL_SHADOW_FIX_VIEW_ROWS_UNLABELLED` — shadow.py:151 tag() labels only subjects containing '__'; after row_id strips the view, RM_X_n and RM_X_s share one row with no per-view label in why/
- `TOKEN_PACE_MEASURE_USAGE_SERIES` — [S 2 h] append each pulse/usage.py reading to a series; compute pace ratio P per account and %-of-week per helper-hour (join with token_burn.json); fe
- `ACCOUNT_USAGE_MEASURE_DORMANT_GAP` — Dormant Claude login measurable only ~8h/day (warm once daily, probe never refreshes); decide warm cadence or locked refresh
- `MUTTAVAQ_ART_POLISH_NORTH_SIZE_AND_FACE` — Polish the installed Muttavaq redraw (s1r3): north view drawn smaller than south/east (F_SIZE_JUMP), front face slightly cartoonish (STYLE_CARTOON). O
- `CASTROSTER_FIX_STILL_NAMES_CUT_XENOTYPES` — selftest_xenotype_defcut RED: 5 cast rows still name Hussar/Yttakin (cut) as race
- `ARTSHEET_FIX_REFERENCE_TEXTURES_PICKABLE` — selftest_reference_textures RED: 7 built sheets make reference textures pickable or hide them
- `FLOWWORKS_STOCK_BISECT_RED_CHECK` — selftest_flowworks_stock RED at 991/992, failing check not in the nightly tail
- `COLD_STORAGE_DEFS_FIX_DOUBLED_CATEGORY` — MOD: 16 new Cold Storage / Cuisine defs log 'Config error in <def>: has duplicate thingCategory' (x2 each, 32 lines) on the Archmagi full-list load of
- `SINGLE_PRIMARY_DESIGN_RETIRE_FOUNDRY_WINDOW` — Design one owner-facing seat + a timer-run headless orchestrator engine replacing FOUNDRY's window; push-based owner contact (notifications, digest, b
- `SLOT_STREAMS_BUILD_SPLIT_R1_R7` — Per-stream split R1-R7 of the allocator's per-seat N
- `HOSE_DRAW_FIX_CROSS_SHADOW_QUADRATIC` — MOD: DrawCrossShadow goes all-pairs again whenever any hose re-lays: 833600 calls, 13.3 s total, 138 ms max frame share in T3 (paused, 400 relays, 200
- `HOSE_DRAW_FIX_STALLS_WHILE_WORKER_LAYS` — MOD: DrawAll takes up to 3.1 s per frame while worker LayFromOn runs (T2, 300 ticks @80), and no profiled child accounts for it; GC is not the cause n
- `GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS` — MOD: a sliced GSS build with no edge laid (AsyncLay, laidOnCaller 0) still costs up to 97 ms on the main thread, and the first slices after a spawn gr
- `ENGINE_TICK_BUILD_DRYRUN_SHADOW_FIRST` — (M) rm-engine-tick: no-AI timer, --dry-run shadow first
- `ENGINE_WORKER_BUILD_SOLE_CLAIMER_LAUNCH` — (M) engine worker launch: tick is sole claimer+renewer, ENGINE.md brief
- `ENGINE_RESULTS_MONITOR_BREAKER_PULSE_ROW` — (M) engine results check, breaker, daily cost ceiling, RimPulse row
- `ENGINE_TRIAGE_BUILD_HOURLY_CAPPED` — (S) hourly capped Sonnet triage pass writing engine/journal.md
- `ENGINE_NEWS_WIRE_DESK_PROMPT_HOOK` — (S) UserPromptSubmit hook: engine news since your last turn, at most 3 lines
- `SLOT_CAP_WIDEN_DESK_WHILE_OWNER_PRESENT` — (S) allocator: BENCH may use whole total while owner present, engine yields
- `PHONE_PUSH_WIRE_AFTER_CHANNEL_RULING` — (S) wire pulse notify_phone to the channel the owner picks (D4/D5)
- `STEWARD_ESCALATION_REWIRE_TO_ENGINE` — (S) steward T+10 items --for FOUNDRY, LLM wake off
- `ENGINE_FAULTS_PROVE_SIX_DRILL_CASES` — (S) engine fault drill: six cases before the pilot
- `GSS_GRAPH_JOB_PROVE_SUSTAINED_CHANGE` — GSS graph job: prove sustained-change staleness bound, de-flake the wall-clock gate
- `HOSE_CROSS_FIX_LEGACY_TOGGLE_STALE_INDEX` — Hose cross-shadow index goes stale if FrameLegacy is toggled at runtime
- `ENGINE_SLOTS_WIRE_TOTAL_MINUS_DESK` — [S] engine slots = total minus BENCH running, replacing FOUNDRY_share 0.25. Confirm: engine idle-with-ready-work <10 min/day over pilot; kill: >60 min
- `ENGINE_CLOSE_ENFORCE_ACCEPTANCE_EVIDENCE` — [M] workers mark built only; close needs evidence of the owed verify level. Confirm: 7-day rework of engine closes <=14.2%; kill: >17.8% at day 14 or 
- `LEDGER_LEASE_HARDEN_ATTEMPT_TOKEN` — [M] per-attempt token; ledger refuses moves/closes from a stale token; bridge workers off until bridge checks it. Confirm: 0 contested claims on engin
- `ENGINE_BUDGET_ENFORCE_RESERVE_AT_LAUNCH` — [S] reserve worker budget at launch; ceiling counts finished+reserved. Confirm: (finished+reserved)/ceiling <=1 over 72 h; kill: >1.1
- `ENGINE_ADMISSION_ENFORCE_PAYDOWN` — [S] under PAYDOWN the tick admits only verify/fix/close work. Confirm: V0 (521) not growing, net flow <=0 over 7 d; kill: V0 +10%
- `ENGINE_WORKERS_ENFORCE_ONE_PER_MOD` — [S] one worker per mod/csproj conflict domain. Confirm: publish/rebase failures <=5 per 100 workers; kill: >15 per 100 or blocked-idle >60 min/day
- `OWNER_CARDS_HARDEN_DECISION_RECEIPTS` — [M] cards carry decision id, revision, addressee; each answer gets an enactment receipt. Confirm: 0 already-ruled messages in 14 d (5 in 10-05..10-24)
- `ENGINE_TRIAGE_REWIRE_ON_SHARED_FAILURE` — [S-M] classify shared-infra failures apart from bad work; triage on event, not hourly. Confirm: drill restore p90 <=30 min; kill: >120 min
- `SLOT_HOOK_MEASURE_REFUSALS_AND_PEAK` — [S] block_agent_over_slots.py logs each refusal and peak running (logs nothing today). Confirm: peak <=N in >=99% of 15-min windows over 7 d; kill: an
- `SINGLE_PRIMARY_DOC_FIX_TICK_HOME` — [S] single_primary: give the tick a home that survives step 4 (it lives in ~/rm/foundry, archived at step 4); work_allocation l235: R3 example says no
- `OWNER_QUESTIONS_DESIGN_RICH_CARDS` — Next card session: answer the owner's 2026-10-26 questions (context self-management, tracking work, focus vs one-agent-per-mod, blocked-by planning, a

## Commits

```
7df9494b7b conversations: catch-up 1 record(s)
2dfa350ecd item: owner's questions for the next card session, verbatim
cca9bbfad5 ledger: OWNER shard
d02d321a49 ledger: BENCH shard (sheet rebuild items)
1a55544cb4 ledger: RUNNER ingest of 1 testq job(s)
c26e1a42b6 fw sheet: merge 10 owner picks; building-looks sheet (5 questions) decisions + snapshot
f39988136f sheet artifact: plain state names, prefill is not an answer, phone one-column sets
6f61781f7c ledger: BENCH files 10 improvements from the orchestration review (7 blocked on the single-primary cards)
31d7807888 design: orchestration review, GPT skeptical + improvements rounds fact-checked against measured numbers (0 contradicted)
019cbc7876 ledger: RUNNER ingest of 1 testq job(s)
8bba47008b art sheets: a question offers one object; coupled states are one set question (prereview criteria + shape lint, art_sheet state-set tags, sheet_to_artifact --questions, no 'mark done')
019fa771ce code review: HoseCrossShadows.cs, HoseCrossShadowChecks.cs clean (ee99572366 review)
7e7f4d50f1 ledger: notes on HOSE_DRAW_FIX_CROSS_SHADOW_QUADRATIC / HOSE_DRAW_FIX_STALLS_WHILE_WORKER_LAYS (fixed offline at ee99572366; live re-run NEXT)
ee99572366 hose draw: indexed crossing shadows -- a landed lay re-checks only near strands, spans via segment grids (HOSE_DRAW_FIX_CROSS_SHADOW_QUADRATIC, HOSE_DRAW_FIX_STALLS_WHILE_WORKER_LAYS)
7fcf46c457 ledger: RUNNER ingest of 1 testq job(s)
53ad52ab91 ledger: RUNNER ingest of 1 testq job(s)
91701783ad lesson: a sheet row must offer one object; coupled states must be one question
394bdccb29 ledger: RUNNER ingest of 1 testq job(s)
28996f7ea4 code review: GSS graph worker (0f395589f2) CordBuilder, CordScaleBench, SliceGateChecks clean
561d822a47 ledger: BENCH shard
... 92 more: git log --oneline b056148973..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     live round 7: hose, GSS slice, press, cold storage

Working tree clean apart from untracked `Transient/`.

