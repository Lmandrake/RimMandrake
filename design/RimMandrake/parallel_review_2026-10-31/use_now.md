# Use now: parallel capacity tonight (2026-10-31)

Item: PARALLEL_BUILD_REVIEW_DEFEND_EVERY_LIMIT. Read-only review; measured 15:52 to 16:00 PDT with all three arms in their first task.
Sibling docs: `arms.md` (arm design), `handoff_context.md` (concurrency, worktrees). Neither topic is repeated here.

**Bottom line.** The machine and the budget can carry 6 to 8 FOUNDRY helpers tonight beside the arms. FOUNDRY has been allowed 8 and has averaged 1.6. The limit is what the seat offers itself, plus two real hazards: the trial runs out of the live FOUNDRY tree, and the arms share one 12 GB test slice. Keep commits to mod source and keep tests small, and both hazards are contained.

## 1. Measured capacity

| Resource | Now (MEASURED) | Free for FOUNDRY tonight | Watch |
|---|---|---|---|
| WSL memory | 35 GB total, 26 available; PSI memory avg10 0.03 | Plenty | Page cache is most of what looks used |
| Seat memory | `claude-seats.slice` 5.9 GB of a 24 GB cap (46 h: p50 5.8, p95 7.9, max 11.6 across seats + harness) | About 16 GB. 8 helpers fit if each is under about 2 GB | A single python of 6 GB has killed a seat twice |
| Test slice | `rm-harness.slice` at its 12 GB cap: anon 0.36, file cache 10.56. `memory.events max` 4.4M and rising (reclaim, not kills) | **None to spare.** The one shared resource to protect | Arm services have no MemoryMax or CPU quota of their own |
| OOM kills | `oom_kill` 59 in 5.8 days, unchanged at 16:00; none since 09:03. Today 4: two test scopes, the replay's 12.5 GB python (08:53), one seat python 5.9 GB | Trend: no global exhaustion; each kill is one big process hitting a cgroup cap | Memwatch samples each minute and missed the 12.5 GB spike (sampled max 1.5 GB). Do not read its maxima as peaks |
| CPU | 14 logical, 2.8 cores busy (20 s sample), load 5.4 at 16:00, PSI cpu some 5.1, full 0 | About 6 to 8 cores, after allowing for arm suites at load near 10 | Sampled early in the run. A full-suite peak was not captured under three arms |
| Disk | `/` 435 GB, D: 1.9 TB; brake at 210 GB | Fine while expiry runs: every helper's clone must stay reclaimable (`rimflow_v3_2026-10-26.md` section 3.1) | Replay clones are 41 GB and have no expiry yet |
| Windows host | 63 GB, **7.2 GB available**, commit 69.5 of 83.3; vmmemWSL 29 GB | Enough for a minimal-list game; not for the full list | Full list is a 25 min load and the main memory contender |
| Bridge | FREE, game DOWN, held 1.5% of 24 h | All of it. Trial tasks do not use it: the 7 hits in `trial_tasks.json` are prose and mod names | Standing bridge rules apply |
| SteveDesktop | RUNNING, no fault, 1 running, 0 pending, 156 jobs in 24 h, invalid streak 0, 66% busy | Capacity is there but misdirected: last 2 days 100% FlowWorks; 515 of 637 jobs in 7 d found nothing (ESTIMATE, 55 h) | `STEVE_INCIDENT_UNCLAIMED` looks stale: steward shows no incident |
| Claude | system 63% left, 93 h to reset, live login. lukas 100%, 96 h. steven closed (at his line, past 48 h) | See below | Do not touch steven |
| Codex | 40% used, 80 h to reset, runway 1.49 | Keep for evidence machinery | |

**Budget.** The allocator's slope is 0.49%/h with 1.6 helpers, about 0.31%/h per helper (MEASURED over the 3 h before the arms, so a quiet window). The longer-window burn behind ops `RUNWAY_LOW` (0.35) is about 1.9%/h. The two disagree, and the arms will push both up.

- ESTIMATE, 6 helpers for 8 h at 0.31%/h: about 15% of system. At the 1.9%/h pessimistic rate, spread across the night: about 15% to 40% with the arms.
- ESTIMATE, arms: power card says 174 to 261M ITE, about one normal day's spend at the 270M/day census. No %-per-ITE calibration exists, so that is not a percentage.
- Only one arm has a measured burn (v3 first build pass: 19 messages, 13.9k output, 824k cache read). Trio and ralph_a were not found in transcripts.
- Pool left is about 159 points over 93 h, or 1.7%/h (ESTIMATE). `account_failover.py` already moves to lukas near 0%, so tonight's budget does not need a login switch. A switch closes every Claude window, so **do not switch by hand during the arms.**
- **Blind spot:** the `session_pct_used` series for system last has a value at 00:37. The 90% five-hour brake may be working from a stale reading. I did not trace how it handles that. Treat it as possibly off, and go by the weekly slope and any throttle errors.

**Stop lines for the night.** Trial first. Drop to 3 helpers if system burns over 3%/h for an hour, if `memory.events oom` moves on `rm-harness.slice`, if a new `oom_kill` lands in an arm unit, or if host available falls under 3 GB. Do not restart them until the cause is known.

## 2. Ready work, offline and disjoint from frozen arena code

**Frozen code is wider than `arena/`.** `trial-runner` runs from `/home/mandrake/rm/foundry/src/RimMandrake/Utils/arena/arena.py` with cwd in foundry: the live FOUNDRY working tree (HEAD 9301e7970d, 151 dirty paths), not a pinned copy. I found no hash of the code tree in the replay's records, only `freeze_hash` over tasks and seed. The import closure is 67 files (AST, over-approximate) and reaches `account_usage`, `art/`, `art_eval/`, `modcheck/`, `pulse/`, `slot_allocator`, `gpt_consult`, `ops_watch`, `telemetry/` and others.

Rule through the Sunday 08:00 stop line:

- FOUNDRY commits **only** under mod source (`src/RimMandrake/<Mod>/`) and `design/`. Nothing in `src/RimMandrake/Utils/` or `rimflow/`.
- **Before any pull in foundry**, run `git diff --name-only HEAD..origin/main -- src/RimMandrake/Utils` and, if it lists anything in the closure, do not pull. Other seats (including the Conductor's own Utils work) can otherwise reach the runner this way.
- Ledger shards are data and are not in the closure, but a pull brings everything with it, so the check applies to them too.
- No full `run_selftests.py`: tests only with `--only`. The suite lock is no protection. Both repair arms hold overlay-private lock files, so they do not share the flock with each other or with seats, and a suite from FOUNDRY would not wait.

**Queue.** 1567 items. `NEXT` shows 7, all reconcile chores. Offline in proposed state: 656; 584 after removing process prefixes; 234 of those have real prose. By kind: task 429, bug 63, design 22, art 20, build 9, feature 9, finding 8, defect 4. Heaviest game prefixes: HOSE 16, BIOME 12, ART 11, SHEET 9, PIT 8, ROT 7, COLD 6, DONOR 6. FlowWorks 11 and GSS 15 are FOUNDRY's anyway. Built: 508, of which bridge 487.

Named picks, all mod source unless marked. I read titles and kinds, not each item's full body: the helper confirms the item's files before starting.

- **Bugs:** `DONOR_PACK_TEX_REPAIR_SEVEN_LEFT_BEHIND`, `ZRRIK_VAMPIRIC_STAB_REBUILD_OWN_BLOODLUST`, `SITE_SPEC_WIRE_TOWER_COST_KEY` (confirm location).
- **Build chain:** `COLD_STORAGE_BUILD_OWN_LINE_DROP_RIMFRIDGE`, then `COLD_STORAGE_CUISINE_BUILD_PRESERVE_DISHES`, `COLD_STORAGE_CHAMBER_BUILD_DRINKS_CHILLER`, `STASIS_LOCKER_BUILD_ANCIENT_COMPLEX_LOOT`, `RAKATAN_STASIS_LOOT_BUILD_HELD_PROVISIONS`. `RIMFRIDGE_DROP_FIX_INBOUND_REFS` needs an owner step: leave it. `CANOPY_LAYER_BUILD_ROOF_OF_THE_WORLD` is the second build if a helper frees up.
- **Reconciles from NEXT:** `CAULDRON_SOILS_BUILD_DIRT_THAT_BREATHES`, `CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED`.
- **Review:** `DIRTY_CODE_REVIEW_LOOP_CONTINUE_NOT_DONE`, about 140 dirty non-FlowWorks, non-GSS C# files.

**Held until the replay ends** (they are in the closure or the harness): `ROUND_SERIES_FIX_SAME_SECOND_RESTART`, `WORLDFACE_SHEET_FIX_WIPE_BEFORE_SOURCE`, `GIZKA_SHEET_FIX_ALTERNATE_SHOWN_AS_RENDER`, `FRESH_SERIES_STOP_FIX_AFTER_OWNER_KEEP`, `TRANSFER_LINT_HARDEN_REFUSED_CREDIT_PASSES`, `STOCK_SELFTEST_WIDEN_RUNNER_TIMEOUT`, all other Utils tooling.

## 3. Lanes and fair checks

Eight helpers at most; start with six. The rule is that nobody checks their own lane. The checker never reads the maker's reasoning first: it gets the item text and the diff.

| Helper group | Helpers | Work | Files | Checked by | Fair check |
|---|---|---|---|---|---|
| Bug fixes | 2 | Section 2 bugs, then next offline `bug`/`defect` items in mod source | One mod per helper | Review-wave reviewer | Full-file review of each C# file (`code_review_status`); XML through `validate_patch.py` |
| Cold storage chain | 1 or 2 | Build chain in order | Own mod plus design | Bug-fix helper, swapped | Reviews against the item's stated acceptance; runs defs validation; states L1 owed |
| Review wave | 2 | Dirty C# outside FlowWorks/GSS, oldest first, then the bug-fix and cold-storage output | Reads C#; records review | Cold-storage helper spot-checks 1 in 10 | Reviewer never made the file; a finding becomes a filed item, not a quiet fix |
| Content XML | 1 | ROT, BIOME (no worldgen), PIT, reconciles | Mod defs, textures | Review-wave reviewer | `validate_patch.py`; `measure` for counts. Art stays with `rimworld-art-evaluation`; nothing to the owner unread |
| Steve feed | 1 | Build L1 chains for non-FlowWorks built items from the 487; submit with `testq` | No code. Runs elsewhere | RUNNER verdict, triaged by a non-maker | Outcome on Steve; a pass closes only with its receipt |
| Bridge sitting | 1, optional | L1 on a 13-mod minimal list for the built items that list can prove | Game on Archmagi | Different helper reads the log | Only with host available above 5 GB, minimal list only, `bridge take`, no flyer flight, no fullscreen or focus |

C# builds go through `winbuild.py`. That runs on the Windows side and does not use the test slice; it does use host memory, so one build at a time. The content and bridge-sitting helpers share deploys: plan before `--apply`, and refuse another seat's files.

The Steve feed is the best value per token in this plan: it costs one helper, converts idle Steve hours, and starts paying down built-but-unproven work. The bridge sitting is the first to drop if the host is tight.

**Order of landing.** Each helper commits explicit paths. Ledger goes in its own commit. Only FOUNDRY publishes, after the pull check in section 2.

## 4. Top 10 limits attacked

[O] means owner-ruled, [A] agent proposal. Only the first two change tonight's output directly. Nothing below reverses an [O] ruling.

| # | Limit | What it limits | Requirement it claims | Survives? | Verdict |
|---|---|---|---|---|---|
| 1 | `next` as the seat's work source: offers 7 reconcile chores while 584 offline game items sit proposed | Whether FOUNDRY sees work at all. Probably the main reason 8 slots ran at 1.6 | Offer only `ready` and `doing`; reconcile before new work | No. The queue view itself says any item can be claimed and started | **Remove tonight**: claim batches by helper group from PROPOSED. Reconciles run with the content helper, not as a gate |
| 2 | Full belt "one subagent building offline" (owner 2026-10-03) read as the number to run | Builders at one. The text says floor, not ceiling | Keep the belt moving, no busywork | The floor survives [O]. The reading does not | **Loosen the reading**: the ceiling is the allocator's N. 584 items is not padding. Conductor to word this in `FOUNDRY.md` |
| 3 | PAYDOWN: "no new art or owner-facing design, half the slots enact and close", entered on D1 12 with A1 71 | Half the slots, while the owner is not at a sheet. D1 waits on a decision nobody is deciding | Do not pile work on an owner who is behind [A] | Partly. New art for him does wait. Offline builds never cost him time | **Loosen**: PAYDOWN gates what reaches him, not building. Have the Conductor decide the 12 D1 items under his authority |
| 4 | Allocator pace looks only at the burn account; spare "never switched automatically" | Machine total shows 2 with lukas at 100% unused. Only his 8 hides this | Do not overdraw the live account; do not switch silently [A] | The switching rule survives, because a switch closes every window. Single-account pacing does not, since `account_failover.py` already moves on [O] | **Loosen**: plan against pool left minus floors. No live switch during arms. Once the Utils freeze ends |
| 5 | `total_max` 10 "never paid" | Nothing tonight: his word gives 16. After 11-04 it returns | `operating_modes` §3.1 [A], never ruled | Unproved. Today's evidence is 1.6 mean helpers, so nobody has tested 10 with useful work | **Keep as a default, retest**: record items per helper-hour tonight at 4, 6 and 8 |
| 6 | Steve fill: 100% FlowWorks guard, 3 mods in 14 d, 72.9% wasted attempts, 515 of 637 jobs found nothing | The only free test rig, while 487 built items owe a bridge check | Guard against regressions in FlowWorks, FOUNDRY-owned | Guard itself survives. The share does not. `unchanged_rerun` is not even measured | **Loosen**: reserve at least half of Steve for other mods' L1; the Steve feed starts it tonight by hand |
| 7 | One driver on the one live game | One live proof at a time | Two drivers corrupt the session | Yes, as a lock. It is not the bottleneck: held 1.5% of 24 h | **Keep the lock; use the bridge.** The real failure is that it sat idle |
| 8 | Verification gates: `implemented` needs a published sha, and L1 per item; V0 547 built unverified | Closes. `verify` events run high but mostly in process work (98.2% of commits in 24 h are process-only) | Nothing is done until shown done | Yes for the gate. Not for one sitting per item | **Keep the gate, batch it**: one sitting clears many L1s; publish a game-items-closed count beside `verify` |
| 9 | Review backlog: 391 DIRTY, full-file review only, maker cannot mark clean | Commits are unblocked but debt grows; review capacity is one lane at best | Independence, a whole-file view | Independence survives. Order does not | **Loosen**: cross-lane swaps, as in section 3. Files with no planned edit go last |
| 10 | Reviews sent to Codex out of habit | Spends a scarce line (runway 1.49), and queues on it | Second model. Role docs and `POLICY` do not require it for ordinary review; the `chatgpt-consult` skill asks for it on evidence machinery | For evidence machinery, yes. Elsewhere no: a fresh helper that did not make it is the standing naive judge | **Loosen**: Codex for scorers, oracles, parsers and big sheets only |

Also seen, smaller: wake caps of 12/h and 96/day are not binding at this load. Close-out refused while a helper lives is correct, but one ring per ticket can hold a seat idle after a batch; check after tonight. `conductor_window` 20 min [O] stays. The RUNNER/ops routing to BENCH with no consumer (`OPS_STEVE_UNSTICK_UNCLAIMED_A00D`, stale alarm 247 min) costs attention more than throughput: `process.share_7d` 86% against a target of under 61 is the larger picture of the same problem.

## 5. Items per night, now vs after (ESTIMATE)

All 8 h figures are ESTIMATES. There is no measured items-per-helper-hour for game work, and `v3.accepted_per_day` is UNMEASURED. The baseline is thin: 11 non-process commits in the last 24 h, 554 in 7 d (MEASURED). `implemented` of 117 and 142 on the last busy days is mostly arena and process.

| Per 8 h night | Now | After, 6 helpers | After, 8 helpers |
|---|---|---|---|
| Game items built | 3 to 5 | 15 to 25 | 20 to 30, if the per-helper rate holds, unproved |
| Files reviewed clean | 5 to 15 | 30 to 60 | 40 to 80 |
| L1 evidence on built items | 0 to 3 | 15 to 30 (mostly Steve) | 20 to 40 |
| Token cost, system % | 3 to 5 | 15 to 20, arms extra | 20 to 25, arms extra |

Assumes 1.5 to 2 h per item per builder, about 3 builders, and about 25% rework. Measure it tonight: count game-item `implemented` events by lane and per helper-hour at Sunday 08:00. That number answers limit 5.

## Not done, by the terms of this review

- **Findings not filed.** The brief is read-only and uncommitted, so these still need an owner seat to file them:
  1. the trial runs from the live foundry tree with no code hash;
  2. arm suite locks are overlay-private;
  3. the arms have no MemoryMax in a shared slice;
  4. the session meter has read nothing for system since 00:37;
  5. `STEVE_INCIDENT_UNCLAIMED` looks stale.
- **Unmeasured:** trio and ralph_a token burn; memory and CPU under three concurrent suites.
- Figures are from one point early in the run. Re-read section 1 before raising past 6.
