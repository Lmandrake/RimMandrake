# 00 Measure: Gimme Some Slack (GSS) as the worked example of pipeline state sprawl

Measured 2026-11-15 in this clone (read-only). Tags: [m: how] measured, [g ~N%] guess. Tokens ~ bytes/4.
Caveat: ledger regex for the mod = `gimme ?some ?slack|GIMMESOMESLACK|GIMME_SOME|\bGSS\b` over raw event JSON; it over-matches (e.g. OPERATIONS_MONITOR_ACCOUNTS_OFF_SHARED_TABLE has 52 hits as a passing mention).

## A. Store census

### A1. Concept folder `design/concepts/GimmeSomeSlack/` [m: du -sb, find]
Total 1,786,598 B in 169 files, of which `version/` is 1,363,589 B. 114 commits touch the folder [m: git log -- path].

| Path | Holds | Bytes | Written by | Read by | Duplicates |
|---|---|---|---|---|---|
| stage.json | stage (5), status, budget, history (13.7K), results (34.2K), parks, coverage rounds, pending_decision, blocked_on | 66,170 | designer_stage.py, coverage_judge.py, maturation*.py, maturation_now.py [m: grep -l filename in src] | dispatcher, Conductor, ops_watch, owner_queue | stage + hold text also in journal "stands", ledger notes, MATURATION_NOW |
| journal.md | steward memory: "stands" top (7,109 B) + dated history | 30,810 | steward agents by hand + maturation.py / maturation_autonomy.py stage-change entries | every restarted Conductor/steward | restates stage, bars count, hold, open questions (all also in stage.json / version/) |
| log.md | older concept log | 18,947 | conductor_log_receipt.py family, agents | rarely | overlaps journal history |
| record.json | his words + inventory rows (23) | 48,759 | designer_stage / maturation_now | judges, designers | sheet.md "his words" |
| tree.json | bar leaves (26) | 45,857 | designer_stage.py, concept_tree.py | judges, test_table maker | bar count also in journal, bars.md, test_table |
| sheet.md | player-facing sheet, his words | 10,869 | designer_stage.py / maturation.py | judges | his words also in journal + record |
| plan.md | plan | 6,386 | agents | judges | - |
| scenes.json | oracle scenes | 42,755 | concept_scenes.py, Graffiti/validation.py | oracles | - |
| exam.json / floor.json | owed exam, floor | 25,860 / 1,799 | designer_stage.py, coverage_judge.py | coverage judge | - |
| coverage_verdict.json / coverage_fixes.json | judge verdict, fixes | 38,292 / 3,024 | coverage_judge.py | designer | verdict repeated in stage.json coverage_rounds (822 B) |
| park_summary.md | park text | 364 | designer_stage.py | Conductor | = stage.json parks |
| result.*.json (30 files; 27 designer incl 4 .rejected, 3 owed-exam) | one run's outcome each | ~38K total [g ~70%] | each Designer run | designer_stage.py harvest | copied into stage.json results (34,167 B) |
| turn_01..05.md, sitting_01_brief.md | owner sitting turns | ~15,990 (turns 0x + brief) [m: wc] | sitting agents | designers | - |
| mock png | art mock | 38,057 | agent | owner | - |
| version/VERSION.json, stage_record.json (6,230), run_spend.jsonl (4,971; 11 rows), bars.md (4,961), gaps_sorted.md (2,897), polish.md, preflight.json, locked_bars.json | version lock, current stage, spend, bar list | small | maturation*.py / steward | judges, Conductor | stage in stage_record AND stage.json AND journal; bars list in bars.md, tree.json, test_table |
| version/test_table.json + .md + make_test_table.py | 48 bars x tests | 305,946 + 21,910 + 32,592 | throwaway make_test_table.py | judges | .md is a read view of .json |
| version/blind_challenge/ | cycle records, lanes | 900,266 | blind judges | steward | summaries re-told in journal |
| version/evidence/ | evidence | 57,644 | agents | judges | - |
| version/preflight_throwaway.py | preflight | 16,195 | agent | - | - |

### A2. Stores outside the folder
| Store | What for GSS | Size | Writer | Reader |
|---|---|---|---|---|
| Ledger shards `infrastructure/state/ledger/events/*.jsonl` | 1,166 events naming the mod in 6 shards (BENCH 341, OWNER 60, FOUNDRY 47, DISPATCHER 44, RUNNER 24, FWDRAIN 2) [m: grep -ci per shard]; by seat of record: CONDUCTOR 448, BENCH 258, OWNER 196, FOUNDRY 132, DISPATCHER 57, RELENTLESS 35, RUNNER 27 [m: python over regex]. Kinds: note 521, file 205, verify 163, close 62, game 53, bridge 45, implemented 45 | whole ledger 52,499 events; GSS slice ~1.17K events | rimflow cli | everyone, projections |
| Ledger items touching mod | 413 distinct ids [m: python] | - | - | - |
| `infrastructure/state/items/*.md` open | 98 files match regex (28 match "gimmesomeslack" strictly, 169,574 B); all 98: 290,267 B [m: grep -li + cat \| wc -c] | | file/note | agents |
| `items/closed/*.md` | 121 files, 269,795 B | | | |
| `infrastructure/state/handoffs/` | 17 files name it, 438,495 B [m: grep -rli] (handoffs total 55 files) | | handoff skill, agents | woken agent |
| Conductor log `/mnt/d/ClaudeWork/rimmandrake/conductor/log.md` | 139 lines of 4,156 name it, 76,077 B; 48 of 600 "DETACHED RUN" lines | | Conductor | Conductor |
| `dispatcher/maturation/state.json` | `/mods/GimmeSomeSlack` 2,309 B of 30,361 | 30,361 whole | maturation_dispatch.py | dispatcher, MATURATION_NOW |
| `dispatcher/maturation/ticks.jsonl` | 1,395 lines name it | 508,727 whole | dispatcher tick | audit |
| `dispatcher/maturation/briefs/GimmeSomeSlack-*.md` | 5 briefs ~15.6-16.5K each (~79K) | | maturation.py brief | detached helper |
| hand_acts / hand_folds / releases / reading.json | 0 GSS hits in hand_acts, hand_folds, releases [m: grep -ci] | 5,041 / 2,019 / 459 / 20,104 | | |
| `conductor/MATURATION_NOW.md` | 12 GSS lines [m: grep -c] | 185,902 whole, all mods | maturation_now.py | Conductor | status page: repeats stage.json / journal / state.json |
| Code `src/RimMandrake/GimmeSomeSlack/` | 39 entries, own CHANGELOG.md, KNOWN_LIMITS.md | unknown | agents | | KNOWN_LIMITS also restates oddities in journal [g ~50%] |
| Design docs naming it | design/INDEX.md, specs 2026-11-13-mod-design-versions.md, 2026-11-15-cheap-guards...md | - | | |
| Handoff-like: dispatcher/Conductor `briefs/` | see above | | | |

### A3. Totals
Distinct logical stores: concept folder (counted as 1 store, but 20+ distinct file kinds) + ledger shards (6) + items open + items closed + handoffs + Conductor log + dispatcher state.json + ticks.jsonl + dispatcher briefs + MATURATION_NOW + src folder + design docs ~= 17 stores [m: counted from tables; counting files in folder separately gives 14 + ~25 = ~39].
Bytes that are mod-specific and unambiguous: concept folder 1,786,598 + open items (28 strict) 169,574 + closed items 269,795 (regex) + handoffs 438,495 + briefs ~79K + conductor log lines 76,077 + state.json slice 2,309 ~= 2.82 MB [m: sum]; the items/handoffs figures are upper bounds because regex hits include passing mentions.
Same fact stored twice or more (observed): current stage (stage.json `stage`, version/stage_record.json, journal "Stage now", MATURATION_NOW, state.json, ledger notes); bar count 48 (journal, bars.md, tree.json+record.json, test_table); his words (record.json, sheet.md, journal); hold text (stage.json blocked_on, journal, ledger OWNER); designer results (result.*.json + stage.json `results` 34K).

## B. Contexts

| Source | Count |
|---|---|
| Designer run result files `result.rm-role-designer-*` | 27 (4 are .rejected) [m: ls] |
| Owed-exam bench results `result.bench-gss-owed-*` | 3 |
| run_spend.jsonl rows (stages blind_challenge, in_game, offline_build ...) | 11 |
| Conductor log DETACHED RUN lines naming it | 48 of 600 total [m: grep -ci] |
| Distinct run/unit ids appearing in GSS ledger text | 126 [m: regex rm-(detached\|role)-...] |
| Distinct ledger item ids naming mod | 413 |
| Distinct seats writing GSS events | 9 |
| Ledger `spawn` events naming it | 10 |
| Dispatcher maturation briefs | 5 |
| Commits on the concept folder | 114 |
Reading: roughly 126 agent contexts have held some piece of GSS state [m: id regex; upper bound, some are the same run named twice]; 30 are Designer/exam runs.

Sample of 3 runs and what each started from:
1. Blind judge cycle 4, run `rm-detached-bench-rimmandrake-judge-gimmesomeslack-blind-c-1794794026` (ended 2026-11-16T03:20Z). Brief `dispatcher/maturation/briefs/GimmeSomeSlack-1794794026.md` 15,609 B. It points to: maturation-pipeline spec 76,854 B (section "Stages 4 and 5" only; whole file if read), FORMAT_NOTES.md 6,965 B, tree.json 45,857, sheet.md 10,869, plan.md 6,386, bars.md 4,961, test_table.json 305,946 (grep), plus the kernel code. Brief + minimal reads ~ 15.6K+6.9K+45.9K+10.9K+6.4K+5.0K = ~91K B (~23K tokens) not counting spec or code [m: wc]; with the spec section [g ~25K B] ~ 29K tokens.
2. Detached builder `RIMMANDRAKE_SLACKEN_GSS_SHORT_LEADS_UNDER_BAR` (2026-11-14, offline). Item prose 1,686 B [m: wc]; the brief text itself was not found on disk [unknown]; it must read journal 30.8K + stage.json... its journal entry records it started from the journal ("a restarted Conductor can do the next stage change from it alone").
3. Designer run `rm-role-designer-1794600004` (stage 5, outcome return to 3). Result file 2,615 B; the brief for Designer roles is generated by role_launch.py and was not found stored [unknown]; its inputs by design are stage.json 66K + record 48.8K + tree 45.9K + coverage_verdict 38.3K + sheet 10.9K ~ 210K B (~52K tokens) [g ~60%, from designer_stage reading the same files].

## C. Live-proven closes per day

Rule (mine, defensible): count distinct item ids closed in the window that ALSO carry a `verify` event with result=pass at level L1, L2, GREEN-MIN, GREEN-FULL, L3 or L4. model.py LEVEL_NEEDS makes every level except L0 need `bridge` or `owner`, i.e. in-game [m: model.py:332-337]. Weakness: the pass is joined on id over all time, not limited to the window [g ~15% inflation either way]. Note the close event's `live` field is NOT game proof: its values are timer-liveness readings ("unit=rm-ops-watch.timer reading=...", "once: rerun green") [m: Counter over 3,816 closes; 3,259 null].
Alternative rule "reason text mentions in-game/live proof/bridge/Player.log/modcheck" over-counts (hits ops text) but is shown for contrast. Both rules ("lp&rx") intersect.

| Window | Days | Close ids (all) /day | Live-proven (verify L1+ pass) ids, /day | reason regex ids /day | both /day | bridge `take` events /day | Items filed /day |
|---|---|---|---|---|---|---|---|
| A 2026-10-01..11-01 (Foundry+Bench) | 32 | 1,888 -> 59.0 | 54 -> 1.7 | 607 -> 19.0 | 37 -> 1.2 | 406 -> 12.7 | 4,122 -> 128.8 |
| B 2026-11-02..11-12 | 11 | 1,197 -> 108.8 | 32 -> 2.9 | 142 -> 12.9 | 13 -> 1.2 | 1,308 -> 118.9 | 1,110 -> 100.9 |
| C 2026-11-13..11-15 | 3 | 237 -> 79.0 | 12 -> 4.0 | 83 -> 27.7 | 7 -> 2.3 | 39 -> 13.0 | 483 -> 161.0 |
[m: python over all 19 shards; events bucketed by ts date UTC; filed = distinct `file` ids]

Take counts need care: window B has 1,308 takes of which RELENTLESS made 739 (automatic cycles); distinct (day, purpose) takes are 389 (A), 384 (B), 36 (C), i.e. 12.2/day, 34.9/day, 12.0/day [m: python set]. Bridge takes were made on 31 of 32 days in A, 11 of 11 in B, 3 of 3 in C.

Examples of live-proven closes (verify pass at bridge level, evidence file named):
- WASTELAND_LIVE_FIXTURE_FIXES_1, 2026-10-08, L2, evidence `Transient/modcheck/Wasteland_20261008T193257Z.json`.
- STILLSAND_MUURROK_EMERGENCE_1, 2026-11-03, L2, evidence `.../live/STILLSAND_MUURROK_EMERGENCE_1-A2-20261103T040032Z.log` (Relentless era).
- EXCAVATION_WALL_ART_1, 2026-11-12, L3, evidence `live_crop_D4_SPIKES.png`.

Verdict on the claim "Foundry/Bench era closed more live-proven work per day than now": NOT supported by these numbers. Live-proven closes per day by the verify rule rose (1.7, 2.9, 4.0) and the stricter both-rules count is 1.2, 1.2, 2.3 [m]. Bridge-take rate per distinct purpose is flat, 12.2 vs 12.0 [m]. Window C is only 3 days, so its mean is noisy [g ~35% error]. What the data does show: total closes per day were highest in B (109/d), mostly non-live (live share 1.7/59 = 2.9% in A, 2.7% in B, 5.1% in C) [m: arithmetic]. Open items now: items/ dir has 888 .md (the 889th entry is `closed/`) [m: ls | wc -l minus 1]; ledger-derived (filed 6,148 ids - closed 3,156 ids = 2,992) disagrees, because many ids are filed once and dropped/superseded or filed under an earlier layout [g ~60%]; trust the items dir number, flagged as one more place where two stores disagree. Closed item files 2,089.

## D. Rehydration cost for a fresh agent picking up GSS with full context [m: wc -c]

| Piece | Bytes | ~tokens |
|---|---|---|
| journal.md (all) | 30,810 | 7.7K |
| journal "the mod as it stands" top part alone (to "## History") | 7,109 | 1.8K |
| stage.json | 66,170 | 16.5K |
| version/bars.md | 4,961 | 1.2K |
| version/test_table.md (read view) | 21,910 | 5.5K |
| version/test_table.json | 305,946 | 76.5K |
| version/stage_record.json | 6,230 | 1.6K |
| record.json | 48,759 | 12.2K |
| tree.json | 45,857 | 11.5K |
| sheet.md | 10,869 | 2.7K |
| plan.md | 6,386 | 1.6K |
| exam.json + floor.json + gaps_sorted.md | 25,860 + 1,799 + 2,897 | 7.6K |
| 28 open items strictly naming GimmeSomeSlack | 169,574 | 42.4K |
| Handoffs naming it (17) | 438,495 | 109.6K |

Sums [m: arithmetic]: minimum (journal + stage_record + bars.md) = 41,001 B ~ 10K tokens. Full set without test_table.json and without items/handoffs = 272,508 B ~ 68K tokens. Plus open items = 442,082 B ~ 110K tokens. Plus test_table.json = 748,028 B ~ 187K tokens. With handoffs too, ~1.19 MB ~ 297K tokens, more than a context window; so full-context pickup is not possible in one read [m: arithmetic].
The journal's own test ("a restarted Conductor can do the next stage change from it alone") needs ~41K B but its "Waiting on" line currently reads "not yet written for this stage" [m: journal line], i.e. the top part is stale at the moment of measure.
