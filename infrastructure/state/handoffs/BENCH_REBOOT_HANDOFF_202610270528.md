# BENCH_REBOOT_HANDOFF_202610270528 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610262128`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**RimFlow v3 is approved to build, Dispatcher first** — `design/RimMandrake/rimflow_v3_2026-10-26.md` is the design of record (roles: Conductor [the one he talks to; quick + session mode, absorbs Bench], Producer, Arbiter [takes his north-star calls], Auditor, Innovator, Operations [incl. economy pass], Dispatcher [a program], Foundry [the one autonomous builder]). Owner 2026-10-26: *"Ok, we ARE going to build this, I just wanted that review."* The grounding review says the diagnosis is measured but the roles are hypotheses: build v3.0 Dispatcher, run a week, keep only roles a number justifies; **process-commit share is 70% (above the 61% that triggered redesign #4)** — v3 must lower it. And: every independent review today found real defects in work its author marked clean; never let a maker grade itself.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Cards owed for v3** (he has the diagram https://claude.ai/artifact/8dMLHJKVSRd1ci4psfaP4a): which shape to start (Bench recommends 1 → 2 → 3), what the Arbiter may rule alone vs bars that come back to him, confirm roles/names as drawn.
- **Delegations ruled today by card** (all in canon.yml + delegation_policy.md): geometric art corrections (18:46); newest mark wins, free bridge + 20 min idle, archive-then-delete leftovers (19:06); **his sheet X = delete forever + ban** (19:54, replaces "X archives"). Measured before the ban: 366 re-X's, 232 re-shows of X'd pictures.
- Stick food collapsed to one roast-on-a-stick anyone can roast (cards 17:59/18:xx); 7 old stick drawings retired by his card.
- Pipe elbow seams fixed on kept art by his card (18:46).
- The full-list "TPS collapse" was a non-like-for-like comparison (second 325 map loaded); calm save still 355 TPS. Real cost found: FlowWorks Excavation 0.87 ms/tick on the big map — fixed offline f7fbbce8ca, live re-measure owed.
- Scratch reaper had been dry-run 8 days (240 GB of clones); switched to --apply 630669a1.
- Frustration census: 27.5% of his messages signal a failure, rising — `D:\ClaudeWork\rimmandrake\csuite\frustration_census.md`.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `RIMFLOW_V3_BUILD_DISPATCHER_FIRST` — design of record written 6a97fcf202; NEXT: put the three v3 cards to him, then spawn an Opus builder for v3.0 (schedule file, wake/verify/retry/record, leases, 48 h unattended proof).
- `EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES` — fixed offline f7fbbce8ca + reviewed 62f6824d60; NEXT: deploy and re-measure on the 325 map (bar < 0.2 ms/tick, max < 20 ms).
- `HOSE_TICK_FIX_SPIKES_AT_SUPERFAST` — r10 rebuilds 1/101 ticks, 26.9 ms worst; one 153 ms hose tick unexplained; NEXT: read HoseTickWatch.Read("1") in the next live round and close or narrow.
- `HOSE_LAY_FIX_GARBAGE_FORCES_FULL_GC` — r10 7.6 MB/s, 3 GCs/89 s, full GC still ~1.24 s; NEXT: decide the bar (GC count per wave) and close if met.
- `HOSE_FRAME_FIX_CHOKES_325_BASIN_MAP` — parent; children mostly closed, residual frame cost is not hose (r10); NEXT: close with the r10 evidence or re-scope to the non-hose stalls.
- `GSS_SLICE_FIX_LONE_REBUILD_HITS_140MS` — r9 one 44.6 ms first slice (named phases, not GC); NEXT: fix snapshot copy cost or accept and close the three GSS slice items.
- `ROAST_STICK_FIX_DISABLED_COOK_STAT_ERRORS` — confirmed live r10 (two red errors); NEXT: suppress the disabled-stat reads for the BasicWorker roast bill.
- `ART_X_BUILD_DELETE_FOREVER_BAN` — built a9a6c82cd6, reviewed+hardened 58a9390e76; NEXT: fix ARTLEDGER_BAN_FIX_PH_FROM_LIVE_FILE and ART_GUARD_FIX_ALLOWS_LIVE_OF_BANNED, then close.
- `LEFTOVERS_BUILD_ARCHIVE_THEN_DELETE` — reviewed 0d2a7409d5, safe for saves/clones/settings/modfolders/patches, pictures refused; NEXT: independent re-review of leftovers.py, then a real run on the safe kinds.
- `CARDS_ENFORCE_DELEGATED_CLASSES_STOP` — hook live, held-out recall 0.87 < 0.9 (selftest RED honestly); NEXT: replay full card bodies from transcripts and raise recall.
- `SCRATCH_CLONES_SHRINK_SPARSE_NOT_FULL` — filed; NEXT: default scratch_clone.py to sparse checkout and change helper briefs.
- `COMPACTION_LOG_FIX_HELPERS_COUNTED_AS_SEAT` — filed; NEXT: fix compaction_watch attribution (helpers logged as the seat).
- `FWSHEET_BUILDING_LOOKS` — artifact https://claude.ai/artifact/NvWyM4dbx3UEhRjPR8FTgh had 0 picks at 14:45; NEXT: ArtifactData list picks, merge if answered.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A comparison across different scenes looked like a 3× TPS regression; readings now carry a scene key and refuse to compare (filed: lessons; see TPS_SCENE_KEY_ENFORCE_LIKE_FOR_LIKE).
- A safety mechanism installed report-only is not on: the scratch reaper was dry-run 8 days (filed: lessons 20261027T025828Z).
- Builders that write their own acceptance test lower the bar to pass (filed: lessons 20261027T023437Z).
- A 7-day census pooled across a fix reports old waste as live (filed: lessons 20261026T230819Z).
- rimflow file refuses names outside SUBJECT_INTENT_TWIST and my grep hid the error — two items I reported filed were not (see: rimflow namecheck before filing).
- `rimflow close --sha PENDING` records the literal string; close after the commit (see: using-rimflow skill).
- The leftovers checker called 162 in-use pictures unused (bare-name, Graphic_Random, C#-built paths) (see: LEFTOVER_PICTURES_RETIRE_VIA_ART_LEDGER).

## Closed since the last handoff (15)

- `HOSE_DRAW_FIX_CROSS_SHADOW_QUADRATIC` — bf24416b7b
- `HOSE_RELAY_FIX_WAVE_FRAME_OVER_BUDGET` — bf24416b7b
- `HOSE_RELAY_FIX_BUDGET_STARVES_LATE_REELS` — ca7e0b67e1
- `SELFTEST_BUILD_DECLARED_INPUT_PASS_CACHE` — cca88f0211
- `CARBON_PRESS_FIX_PACK_TAKES_WHOLE_STACKS` — 17e9ecf967
- `HOSE_SNAPSHOT_FIX_MISSES_CLIMB_GENERATION` — 92af8fe9ac
- `CARBON_PACK_FIX_NUTRITION_READ_AS_PIECES` — 92af8fe9ac
- `PIPE_ELBOW_FIX_SEAM_JOGS` — PENDING
- `CTX_SIM_FIX_COLD_RESTART_DOUBLE_CHARGE` — f93125b477
- `ART_MARKS_BUILD_NEWEST_WINS_ARCHIVE` — a8f8e15616
- `CUISINE_STICKS_MERGE_SEVEN_INTO_ONE_ROAST` — 140cb1d156
- `HOSE_DRAW_FIX_STALLS_WHILE_WORKER_LAYS` — 295a658f86
- `ARCHIVED_SHAS_FIX_LIVE_SUBTRACTION` — 58a9390e767b
- `STEVE_LANE_UNSTICK_BRAKED_UNOWNED_BACB` — 04ab5ee31e
- `TPS_SCENE_KEY_ENFORCE_LIKE_FOR_LIKE` — 33d7b4b518

## Filed and still open (40) — the next seat's queue

- `HOSE_LAY_FIX_GARBAGE_FORCES_FULL_GC` — MOD: at speed with worker lays the heap grows ~40 MB/s (3.69->4.01 GB in 8 s) and each full GC on the 3.45 GB live heap freezes a frame ~1.1 s (T2 Roo
- `GSS_SLICE_FIX_LONE_REBUILD_HITS_140MS` — MOD: one sliced cord rebuild took 140.3 ms on the 325 map (bar 20) outside any counted GC; MapComponentUpdate max 28-141 ms; maxSliceMs is a lifetime 
- `COMPACTION_LOG_FIX_HELPERS_COUNTED_AS_SEAT` — compactions.jsonl: 435/435 BENCH-clone compactions read handoff MISSING (203 on 10-26); helpers sharing the cwd are likely logged as the seat and the 
- `HELPER_WAITS_FIX_5MIN_CACHE_REWRITES` — Helper foreground waits >5 min rewrite the whole 5-min-cached context: 3.8% of total; cap waits under 5 min (540 s timeout allows 9)
- `HELPER_WAITS_FIX_CACHE_GOES_COLD` — Helper foreground waits >5 min rewrite the whole 5-min-cached context: 3.8% of total spend; cap waits under 5 min (540 s timeout allows 9)
- `COMPACTION_RESTORE_OPEN_ITEMS_FROM_LEDGER` — Real compactions keep only 34/66 open item IDs exactly (some shortened past grep); a SessionStart(compact) hook should inject 'rimflow next --seat' fr
- `OWNER_RULINGS_HARDEN_DATES_ON_DISK` — Summaries quote the owner verbatim (93%) but date only 3% (10/316); without Compact Instructions the probe dated every ruling 'today'. Keep dated ruli
- `HELPER_IDS_RESTORE_AFTER_COMPACTION` — Summaries keep a helper's task but its agentId only 4/20 (the harness labels the ID 'do not mention to user'); add an on-disk helper registry that is 
- `HOSE_TICK_FIX_SPIKES_AT_SUPERFAST` — MOD: at Superfast on the 325 basin map with worker lays, RM_MapComponent_Hoses.MapComponentTick max 183 ms (T2 bridge ticks 47 ms), DoSingleTick max 4
- `BRIDGE_LOAD_FIX_READY_WHILE_INITIALIZING` — HARNESS: first load_game_ready after a cold launch returned success/game_loaded while programState stayed MapInitializing (SmashTools DetachedMapCompo
- `TEST_ENV_FIX_TRIBAL_VISIT_STOPS_SETUP` — TEST-ENV: on the staged 325 basin map (tile 96532) a 3-pawn Tribal arrival at tick 8358 tripped the clockgate GovernorStop (hostile_arrival) during ho
- `QUOTA_LEFT_AT_RESET_MEASURE_PER_ACCOUNT` — Record usable quota left unspent at each limit reset, per account, over several reset cycles; the one number that decides whether idle seats cost anyt
- `CODE_REVIEW_ENFORCE_REVIEWER_NOT_AUTHOR` — code_review_status mark-clean accepts the author's own mark: the r9 hose fixer marked its own 10 files CLEAN (2bb9d38c30, same timestamp as fix ab9a53
- `MOD_COMPLETION_MEASURE_HOW_DONE_IS_DONE` — Mod completion assessment computed only from evidence: content inventory vs player-truths passing, art accepted+functional, owner-pending reviews, cod
- `CUISINE_STICKS_BUILD_HUNGRY_SELF_ROAST` — Self-serve roast: a hungry colonist with no meal in reach walks to a campfire, roasts one roast-on-a-stick (raw food + skewer) and eats it, instead of
- `CTX_SIM_FIX_UNCACHED_INPUT_PRICE` — ctx_strategy_sim line ~166: real_ite/warm_window fold uncached input_tokens into cc (priced at 1h cache-write 2x, should be 1x); fix needs recalibrati
- `ROAST_STICK_FIX_DISABLED_COOK_STAT_ERRORS` — Roast-on-a-stick by a Cooking-incapable pawn hits vanilla's dev-mode 'disabled stat' ErrorOnce twice: CookSpeed (recipe workSpeedStat, skillNeedOffset
- `BRIDGE_IDLE_BUILD_TWENTY_MINUTE_WATCH` — Windows idle-input probe + free-bridge watcher: take/deploy/restart after 20 min owner-idle; never flyer flight
- `LEFTOVERS_BUILD_ARCHIVE_THEN_DELETE` — One checker (nothing reads it + pushed) for saves/folders/settings/patches; archive under agent storage, then delete, digest
- `CARDS_ENFORCE_DELEGATED_CLASSES_STOP` — Warn/refuse a question card whose class is already delegated (§1 work order/helper count, §2.4 twins)
- `ENACT_X_FIX_PURGE_OF_KEPT_ART` — enact still purges ✕'d in-game (Graphic_Random) and once-kept pictures; card says archive, never purge
- `REFTEX_SELFTEST_FIX_IGNORED_INPUTS` — selftest_reference_textures red only on clones with stale gitignored subjects.json; pre-existing, not ART_MARKS
- `ART_X_BUILD_DELETE_FOREVER_BAN` — Sheet X = purge bytes forever + permanent ban (exact sha + perceptual near-duplicate) refused by sheet build, art install and every redraw (artpipe re
- `SCRATCH_CLONES_SHRINK_SPARSE_NOT_FULL` — 65 BENCH scratch clones hold 240 GB: history is shared (21-42 MB .git each) but every helper checks out the whole 3.6 GB tree; default scratch_clone.p
- `FULLLIST_TPS_DIAGNOSE_THIRD_OF_LAST_WEEK` — Full-list game speed fell from 346 TPS / 60 FPS (10-20) to 112-145 TPS / 12-14 FPS (10-26/27); recorded but not surfaced; bisect by mod (FlowWorks/GSS
- `LEFTOVER_PICTURES_RETIRE_VIA_ART_LEDGER` — Leftover pictures (704 SAFE before fixes; 162 were referenced) must leave via art.py archive-then-delete; leftovers.py now refuses the picture kind
- `STANDIN_COPIES_CULL_DEAD_BYTES` — StandIn/ texture copies differ in bytes from the same-mod donor-path copies the defs actually draw; the StandIn copies are unreferenced dead weight (5
- `ART_REFTEXTURES_FIX_SELFTEST_ON_DISK` — art/selftest_reference_textures.py FAILs on on-disk sheets: xeno_heads_new_vs_borrowed_sheet_2026-10-18 rows XenoHead_Lasat/Nelvaanian/Ortolan (+ othe
- `ENACT_STALE_LANE_FIX_VACUOUS_CHECKS` — art/selftest_enact_stale_lane.py had 4+3 checks failing or vacuous at HEAD after the 19:06 newest-mark-wins rule (purged set ignored archive; 3 cross-
- `BUILDBATCH_FIX_REPLACE_LEAVES_OLD_THING` — jawa/build_batch wipeExisting=true reported displaced[] 'destroyed RM_Ladder, sameDefReplacedInPlace' at 134,9 but the old unowned RM_Ladder122099 sta
- `DRAWALL_DIAGNOSE_PAUSED_FRAME_STALL` — Full list, 325 basin map, game PAUSED and idle: Root_Play max 148 ms / DrawAll max 145 ms per 60 s while every profiled DrawAll child is under 1.2 ms;
- `MAPPRETICK_DIAGNOSE_FULL_LIST_STALL` — Full list, 325 basin map at Superfast: worst ticks 316-1697 ms sit in Verse.Map:MapPreTick (312-414 ms profiled) with HoseTickWatch hoseMs <=11.9 and 
- `ARTLEDGER_BAN_FIX_PH_FROM_LIVE_FILE` — x_delete computes ph/ph_mirror only from store bytes (ph_of falls back to variant ph); when the store lacks the bytes but the game file holds them, th
- `ART_GUARD_FIX_ALLOWS_LIVE_OF_BANNED` — art_guard._authorized has no ban check: a live event installing an exact banned sha after its ban passes on a mechanical/backfill reason; install() re
- `REFTEX_SELFTEST_FIX_BUILT_SHEETS_RED` — selftest_reference_textures.py RED: 107 fails on built sheets on disk (xeno_heads_new_vs_borrowed 2026-10-18, art_eval_shadow_br1e_ports_bore 2026-10-
- `THIRST_CHAIN_UNSTICK_STILL_SIPPING` — FlowWorks chain 'thirst' hangs on SteveDesktop: two filler jobs INVALID/HARNESS (J20261027T022443Z-6675e4 stalled ~17 min in 'FlowWorks C# SelfTest (o
- `EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES` — RM_MapComponent_Excavation (mandrake.rm.flowworks) costs 0.87 ms/tick mean with 158-172 ms single-tick spikes on the 325x325 RM_PerfSite map, the larg
- `CSUITE_PAWNBAND_VET_FRESH_EYES` — Independent full-file review of csuite_tps.py + selftest_csuite_tps.py + RM_PocketGrid.cs after 62f6824d60 (reviewer added --pawn-band and removed dea
- `EXCAVATION_TICKCHECK_HARDEN_SIM_COPY` — ExcavationTickChecks simulates the incremental rebuild policy with a Sim COPY pinned to production by regex (RiverSwitchFlipChecks.Has); truth is the 
- `RIMFLOW_V3_BUILD_DISPATCHER_FIRST` — RimFlow v3.0: build the Dispatcher (no AI) per design/RimMandrake/rimflow_v3_2026-10-26.md §6 — schedule file, wake/handoff/verify/retry/record, lease

## Commits

```
3f0b7a5334 conversations: catch-up 3 record(s)
6a97fcf202 design: RimFlow v3 — the integrator layer (Conductor, Producer, Arbiter, Auditor, Innovator, Operations, Dispatcher, Foundry); build v3.0 Dispatcher first
a5150e91a3 ledger: RUNNER ingest of 1 testq job(s)
9f38ec81ad ledger: RUNNER ingest of 1 testq job(s)
6ae0872e30 ledger: RUNNER ingest of 1 testq job(s)
ba88642629 ledger: RUNNER ingest of 1 testq job(s)
b9730be934 ledger: RUNNER ingest of 1 testq job(s)
96303938ba ledger: RUNNER ingest of 1 testq job(s)
faf3779ade ledger: BENCH shard (excavation review items)
1a925a910f code_review: mark-clean RM_WallReach, RM_WallReachMath, ExcavationTickChecks, Program (review of f7fbbce8ca)
db0d75d65f review f7fbbce8ca+33d7b4b518: drop dead RM_PocketGrid.RampJoins; csuite_tps opt-in --pawn-band PCT
fd6b181424 ledger: RUNNER ingest of 1 testq job(s)
5aeb59d9fe ledger: BENCH shard (excavation fix, TPS scene key)
33d7b4b518 csuite_tps: TPS_SCENE_KEY_ENFORCE_LIKE_FOR_LIKE - key every reading to its scene, refuse unlike compares
85f64b58d6 ledger: RUNNER ingest of 1 testq job(s)
f7fbbce8ca FlowWorks: EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES - wall-reach and pocket-grid rebuild only on real input change
b72c5d8faa ledger: RUNNER ingest of 1 testq job(s)
77d08e2a8e ledger: BENCH TPS bisect - full-list drop is the 2-map PerfSite scene, not mods (355 vs 354 TPS like-for-like); file EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES; lesson tps-not-like-for-like
4a31cf5064 ledger: BENCH unstick Steve lane (reconcile bridge marker, proof job); file THIRST_CHAIN_UNSTICK_STILL_SIPPING
72921cbe8d ledger: RUNNER ingest of 1 testq job(s)
... 140 more: git log --oneline 6d4e90ee17..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : LOADING  → corrected to UP, measured now
- Bridge: FREE    since 2026-10-27T03:48:40Z

Working tree clean apart from untracked `Transient/`.

