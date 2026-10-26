# Baseline: the two-seat operating system, tagged 2026-10-26

**Tag:** `system-baseline-two-seat-2026-10-26` (annotated, on the published commit that adds this file).
**Owner, 2026-10-26, verbatim:** "please do put a special tag right now on RimMandrake's current system. This works. we
want to keep this tag here well documented with what worked, why, and what we're trying to fix, and the metrics by
which we'll measure that."

This is the system before the single-primary redesign (`design/RimMandrake/single_primary_design_2026-10-26.md`, not
built; it waits on cards D1-D7). It is written so that, after the redesign, anyone can answer two questions with
numbers: did it get better, and how do we go back.

Conventions: **[M]** = measured by me on 2026-10-26 (16:30-17:00 PDT) with the named command; raw output is in
`D:\ClaudeWork\rimmandrake\baseline_2026-10-26\` (scratch, program-read). **[Q]** = quoted from a document, with its
source and date, not re-measured. **UNMEASURED** = no instrument exists or I could not make one honestly.
Token numbers are "ITE" (Opus-input-token equivalents; relative list prices Opus 1 : Sonnet 0.6 : Haiku 0.2, an
assumption stated in `spend_census.py`).

---

## 1. What the system is

Two Claude Code windows on one machine (Archmagi, WSL), each in its own git clone, plus a lot of no-AI machinery. BENCH
talks with the owner and does live work; FOUNDRY works the queue by itself.

| piece | what it does | implemented by |
|---|---|---|
| BENCH desk | the window the owner talks to; live debugging, bridge, FlowWorks and GSS (all of it), acceptance looks | `infrastructure/agents/BENCH.md`, clone `/home/mandrake/rm/bench` |
| FOUNDRY window | autonomous queue worker, no owner present | `infrastructure/agents/FOUNDRY.md`, clone `/home/mandrake/rm/foundry` |
| two clones, one remote | each seat edits only its own clone; `./publish` pushes; mirror read-only on the Windows side | `~/rm/{bench,foundry,mirror.git,store.git}`, `publish`, `rm-mirror.timer` |
| rimflow sharded ledger | append-only events per seat (`BENCH/FOUNDRY/OWNER/RUNNER.jsonl`), queue and item files derived from it; verbs file/claim/start/close/verify/implemented/block/needs | `src/RimMandrake/rimflow/` (`cli.py`, `model.py`), `infrastructure/state/ledger/events/` |
| items | one prose file per item, `SUBJECT_INTENT_TWIST` names, verify levels L0-L4 | `infrastructure/state/items/`, `rimflow namecheck`, `.claude/hooks/queue_lint.py` |
| leases | 45-minute claim, renewed every 10 min | `src/RimMandrake/rimflow/lease.py` |
| slot allocator | no-AI program, every 15 min sets N (helpers allowed at once) per seat from token pace, review queues and where the owner is | `src/RimMandrake/Utils/slot_allocator.py`, `slot_rules.json`, `pulse/streams.py` (writes `streams/allocation.json`), `design/RimMandrake/operating_modes_2026-10-26.md` |
| over-N hook | refuses an Agent spawn when the seat already runs N | `.claude/hooks/block_agent_over_slots.py` (commit e4614f3bba) |
| bounded helpers | rm-* agent definitions: compact at 150k, omitClaudeMd, tool allowlist, rules digest, base context 45k to 18.5k | `.claude/agents/rm-{bridge,builder,fixer,judge,search}.md` (commits 258d8c17fa, 1f37da7100), `.claude/hooks/block_unbounded_agent.py`, `block_agent_without_model.py` |
| handoff ritual + wake | a seat writes what dies with its context; the next one consumes it | `src/RimMandrake/Utils/handoff.py`, skill `handoff`, `infrastructure/state/BENCH_HANDOFF.md` |
| compaction instructions | "Compact Instructions" section: keep NEXT pointers, unfiled lessons, dated owner rulings, bridge holds, running helpers, uncommitted paths, HANDOFF OWED | `CLAUDE.md` line 347 |
| compaction_watch hook | PreCompact: logs each compaction and whether a handoff was written; after: tells the seat to repair | `~/dev/Lodestar/bin/hooks/compaction_watch.py`, wired in `~/.claude/settings.json`, log `D:\ClaudeWork\logs\compactions.jsonl` |
| testq on SteveDesktop | second machine; batch test lane with a no-AI steward and heartbeat watcher | `src/RimMandrake/Utils/testq/`, `infrastructure/stevedesktop/`, timers `testq-tick`, `testq-sweep`, `testq-steward-watch` |
| RimPulse | the owner's dashboard: streams panel, health, testing panel, usage tile | `src/RimMandrake/Utils/pulse/` (`pulse.py`, `streams.py`, `systemd/`), timers `rm-pulse-*` |
| digests | 06:00 and 17:30 scheduled digests, plus a brief | `rm-pulse-digest.timer`, `rm-pulse-brief.timer`, `pulse/brief.py`, output `D:\ClaudeWork\rimmandrake\dashboard\digests\` |
| art pipeline | generate, auto-judge (Opus first, GPT second look), art ledger, install guard | `src/RimMandrake/Utils/art/` (`art.py`, `art_guard.py`, `enact.py`), `src/RimMandrake/Utils/artpipe/`, `art_eval/`, skills `rimworld-art-evaluation`, `generating-rimworld-sprites` |
| review sheets and artifacts | owner keeps/cuts art in a gated HTML sheet; his picks become ledger rulings | `art/art_sheet.py`, `serve_gated.py`, `art.py review awaiting-pick`, skills `review-sheets`, `rimworld-review-sheets`, hook `block_hand_edited_sheet.py` |
| selftests nightly | all `selftest_*.py` at 03:00 | `run_selftests.py`, `rm-selftests-nightly.timer` |
| code-review status | a file is DIRTY until reviewed; standing review loop | `src/RimMandrake/Utils/code_review_status.py`, `rm-codebase-health.timer` |
| token meter | measured remaining quota per Claude account every 15 min | `account_usage.py`, `rm-account-usage.timer`, `claude-account-*.timer` |
| bridge lock | one holder of the live game at a time | `infrastructure/state/BRIDGE`, `./bridge`, `rimflow bridge` |

Live allocator reading at baseline time [M, `python3 src/RimMandrake/Utils/slot_allocator.py now`]:
"CRUISE+OWNER PAYDOWN BENCH N=4, FOUNDRY 0 (total 4)", with the owner's standing word that BENCH may exceed the usual
limit for interactive work (until 2026-10-27 13:14 PDT). `slot_rules.json` gives FOUNDRY a 0.25 share of a total of 10 at most.

---

## 2. What worked, and why

**2.1 The bounded-helper fix of 2026-10-23 stopped the biggest leak.** Before it, helpers (subagents) re-read
300k-966k-token contexts on a 1M window that never compacted; after, they compact at 150k, load no CLAUDE.md, and start
at 18.5k instead of 45k (commits 258d8c17fa, 1f37da7100, 2026-10-23). Measured per day, BENCH + FOUNDRY, subagents only
[M, `D:\ClaudeWork\rimmandrake\baseline_2026-10-26\daily_spend.py 10`, built on `Utils/sim/spend_census.py`;
day = local date; 10-26 is a part day]:

| day | total M ITE | subagent share of spend | subagent calls made at >100k context | subagent ITE spent in >100k-context calls |
|---|---|---|---|---|
| 10-18 | 182.7 | 87.0% | 71.8% | 80.4% |
| 10-19 | 162.9 | 88.7% | 70.0% | 80.7% |
| 10-20 | 170.9 | 89.6% | 76.6% | 83.8% |
| 10-21 | 141.2 | 89.9% | 79.8% | 85.7% |
| 10-22 | 393.5 | 93.9% | 82.2% | 89.6% |
| 10-23 (fix day) | 339.3 | 90.8% | 57.6% | 76.3% |
| 10-24 | 181.4 | 87.7% | 17.0% | 21.1% |
| 10-25 | 159.8 | 87.9% | 14.7% | 20.0% |
| 10-26 | 320.5 | 87.8% | 14.7% | 20.0% |

The owner-cited figure (76-88% before, 15-17% after) matches the "calls made at >100k" column to within a few points
(70-82% before, 15-17% after); by the ITE-weighted column it is 80-90% before and 20-21% after. Either way the leak fell
by roughly four-fifths. **Why it worked:** the cost of a call is its whole context, so the fix attacked context size
(early compaction, no CLAUDE.md, a short rules digest) rather than the number of helpers. **What it did not change:**
subagents still take about 88% of all spend, because the spend itself is real work (see 3.1). Lesson on reading this:
`infrastructure/state/lessons/20261026T230819Z-BENCH-7-day-spend-census-pooled-across.md` (a pooled week hides a fix;
split by day).

**2.2 Compact Instructions keep the handoff alive across compaction.** Source: `design/RimMandrake/compaction_retention_test_2026-10-26.md`
[Q, 2026-10-26: 18 real compactions audited offline plus a two-arm headless probe, about $1.43]. Owner sentences survive
93% verbatim with or without the instructions (the built-in summary template does that); the instructions are the
measured cause of three things: HANDOFF OWED survived in 5 of 6 compactions after they were added against 0 of 4 before;
in the probe the rulings kept their dates 5/5 with them against 0/5 without (without, the quiz dated all five "today",
confidently wrong for four); helper agentIds 3/3 against 0/3. Probe totals 31/31 against 23/31. Known limits, same
source: open item IDs survive only 52% at real sizes; owner quotes carry a date in only 3% of summaries; agentIds 4 of 20.
Items filed against these include `OWNER_RULINGS_HARDEN_DATES_ON_DISK` and `HELPER_IDS_RESTORE_AFTER_COMPACTION`.

**2.3 The ledger is a real throughput engine.** [M, `python3 src/RimMandrake/Utils/rimflow_metrics.py --days 7`, as of
ledger 2026-10-26T23:24Z, 28,684 events]: 1,513 items filed, 914 done, 557 net in 7 days; median lead time 0.03 d,
p90 1.83 d; 823 closes since 10-19, rising from 13-54 a day (10-19..10-23) to 113, 92 and 444 on 10-24, 10-25, 10-26 (the
last includes bulk closes; 683 items of the 7-day window were done never started, 191 within 5 minutes of filing; the
design docs treat those as not real work, so read the count as an upper bound). The ledger is sharded one file per seat (BENCH, FOUNDRY, OWNER, RUNNER), so two clones append without editing each
other's file; the instrument reports 10 replay refusals and 0 tolerated fields in 28,684 events. Queue wait median 0.01 d.

**2.4 The no-AI machinery keeps running without tokens.** 23 user timers are live (allocator re-check, token meter,
pulse streams and health, digests, testq steward, selftests nightly, mirror, scratch reaper, memwatch, codebase
health). The allocator and its hook are live and hold N (peak-vs-N logging is not yet built, see 3.5). The testq steward
has made 17 state changes and its AI wake has never fired [Q, orchestration_review 2026-10-26 14:01-14:10].

**2.5 The owner-facing loop converts picks into installs without agents guessing.** Art picks are ledger rulings that
`art.py enact` carries out; the guard refuses a texture change the ledger did not make. The pick queue fell from 132 rows
(24 sheets) in the 10-26 design docs [Q] to 71 rows (38 sheets) [M] the same day.

**2.6 Honest limits of "this works".** It works in the sense that work gets filed, done and published at a high rate,
without losing owner words or ledger events. It does not yet show that the work is *right* or *finished*: see Section 3.

---

## 3. What we are trying to fix

Sources: `design/RimMandrake/orchestration_review_2026-10-26.md` (GPT's skeptical review, checked against our numbers),
`single_primary_design_2026-10-26.md`, `owner_cards_2026-10-27.md`, `infrastructure/state/items/OWNER_QUESTIONS_DESIGN_RICH_CARDS.md`,
`perpetual_orchestrator_context_2026-10-26.md`, `D:\ClaudeWork\rimmandrake\perpetual_ctx\matter.md`.

**3.1 The owner watches all day.** Owner, 2026-10-26, by card 13:08 PDT (single-primary design): "Right now I have to log
in all day and look. Inefficient." He asks whether the Bench/Foundry split is still worth it, "FOUNDRY seems an oddly
manual appendix", and "would I log into the orchestrator? My questions might burn up its context unnecessarily", and
wants "something entirely for human interaction/review (the original Bench design)" apart from a master orchestrator
with subagents only. The design's answer: BENCH becomes the one window; a no-AI engine runs the queue with headless
workers; FOUNDRY retires after a pilot.

**3.2 Context self-management, awareness, focus, planning, a real "this week's plan".** Owner, verbatim, 2026-10-26
(`OWNER_QUESTIONS_DESIGN_RICH_CARDS`): "how does Bench self-manage its context so I don't have to? How can I track work
being done so I'm aware? And if there's only one agent per mod, that implies we will always be working on many mods
again. We only started making real progress closing mods when we focused hard on 1-2 at a time. So I'd like to know what
we will have in place to bring back that intense focus to really grind on something to finish it, instead of make slow
progress across many items. Lastly, it seems potentially valuable to use "blocked by" when we plan out tickets so that
there's some shadow of the plan that can be computed and tracked. I really need some kind of "this week's plan" shown
graphically and parts being ticked off as we go... REALLY ticked off, not just "text generated towards code" as it is
today." These are cards Q1-Q5 in `owner_cards_2026-10-27.md`; D1-D7 are the engine decisions. He said not to build UI:
only to say what answers such a view needs.

**3.3 The orchestrator's own context.** `perpetual_orchestrator_context_2026-10-26.md` and `matter.md`: the top-level
seat is only 9.3% of total spend [Q, 7-day census, 270.4M ITE/day], so its context policy is a small lever, but within
it BENCH's practice (hand off near 347k) costs about 1.6x the best policy in the offline simulation (restart at about
125k absolute, minus 31% of the orchestrator's cost, minus 2.9% of total spend). Letting a 1M window compact at 750k is
76.6% worse than today's practice. Biggest lever there: a lean wake (about 47.5k tokens cached). Correction found by that
research: the Q1 claim that a seat "cannot /clear itself / loses RC" is wrong (a mod can run `/clear`; Remote Control
keeps the session).

**3.4 "Published" is not "accepted".** GPT's finding, our verdict "partly": the ledger records verify levels but nothing
refuses a close without them. Baseline numbers in Section 4: most closes carry no verify level; 521 built items wait for
verification; rework runs about 13%. Items filed: `ENGINE_CLOSE_ENFORCE_ACCEPTANCE_EVIDENCE` and
`ENGINE_ADMISSION_ENFORCE_PAYDOWN` (the verify backlog must stop growing).

**3.5 Leases do not fence effects; spend control cannot see running work; the over-N hook logs nothing.** Two clones can
both lease an item (`lease.py` line 31: "TWO CLONES ARE NOT COORDINATED"); 19 contested claims on record; 166 open items
with a lapsed lease. The budget flag sees only finished results. The hook writes no refusal log, so "holds N" is
UNMEASURED. Filed: `LEDGER_LEASE_HARDEN_ATTEMPT_TOKEN`, `ENGINE_BUDGET_ENFORCE_RESERVE_AT_LAUNCH`,
`SLOT_HOOK_MEASURE_REFUSALS_AND_PEAK`.

**3.6 Owner waits and re-asks.** 49 items wait on him, 32 for more than 3 days, the oldest 45 days [M]; he has had to say
"I've already ruled" repeatedly (Section 4). Filed: `OWNER_CARDS_HARDEN_DECISION_RECEIPTS`.

**3.7 Idle capacity and the 25% split.** FOUNDRY's fixed 0.25 share is wrong for a design where the engine takes the
queue; ledger silences reach 23.2 h (an upper bound) [Q, single_primary §1.2]. Filed: `ENGINE_SLOTS_WIRE_TOTAL_MINUS_DESK`.

---

## 4. Metrics

All "baseline" values are [M] 2026-10-26 unless marked. "Command" is what reproduces it; scripts I wrote live in
`D:\ClaudeWork\rimmandrake\baseline_2026-10-26\`. Targets and kill thresholds are the designs' own proposals (source
named); where a design gives none the cell says "none given".

| # | metric | baseline value (measured now) | command / script | target | kill threshold |
|---|---|---|---|---|---|
| M1 | daily token spend, 10-day window | 61 to 394 M ITE/day; 10-24: 181.4, 10-25: 159.8, 10-26 (part day): 320.5; 7-day total 270.8 M/day average, about 1.91 B raw tokens/day | `baseline_2026-10-26/daily_spend.py 10`; `python3 src/RimMandrake/Utils/sim/spend_census.py` | cost per accepted item at most 1.25x FOUNDRY's last 7 days (single_primary §6) | daily cost ceiling hit twice (single_primary kill rule) |
| M2 | seat vs subagent split | seats 12% (BENCH top-level 6.6%, FOUNDRY top-level 2.4% over 7 d; 6-13% per day), subagents 87.7% on 10-26 (BENCH 43.0%, FOUNDRY 40.2% over 7 d); art-eval headless 5.6% | same | none given (orchestrator is only 9.3% of spend, matter.md [Q]) | none given |
| M3 | subagent spend in >100k-context calls | 20.0% ITE-weighted, 14.7% of calls (10-26); was 80-90% / 58-82% before 10-23 | `daily_spend.py` | stay under 25% (my proposal; no design number) | above 50% on any full day (my proposal) |
| M4 | throughput: filed / done / net, 7 d | 1,513 / 914 / net +557; 823 closes since 10-19 | `rimflow_metrics.py --days 7` | net at or below 0 under PAYDOWN (ENGINE_ADMISSION_ENFORCE_PAYDOWN) | pile grows over 10% in 7 d |
| M5 | owner-wait items | 49 open, 32 over 3 d, median 3.38 d, oldest 45.2 d; 62 resolved in 7 d, median 1.59 d | `rimflow_metrics.py` (owner_wait_open / resolved) | under 10 over 3 d (operating_modes PAYDOWN line) [Q] | none given |
| M6 | owner "already ruled" messages | 7 human-origin messages matching an "already ruled/told/answered" pattern 10-11..10-25 (6 of them 10-12..10-25); regex proxy over all BENCH/FOUNDRY transcripts | `baseline_2026-10-26/already_ruled.py` | 0 in 14 days (OWNER_CARDS_HARDEN_DECISION_RECEIPTS) | any re-ask of a decision that has a receipt |
| M7 | rework rate of closes | 195 of 1,513 new items (12.9%) cite an already-done item as cause, 7 d; 342 have any cause. Review quoted 14.2% (77 of 541) for 10-26 morning [Q] | `rimflow_metrics.py` (rework) | at or below 14.2% (ENGINE_CLOSE_ENFORCE_ACCEPTANCE_EVIDENCE) | above 17.8% at day 14; two rework items in one day from engine closes (single_primary) |
| M8 | closes with no verify level | 813 of 823 closes since 10-19 (98.8%) have no verify event with a level before the close; 792 (96.2%) have neither a level nor an `implemented` event. The brief quoted 799/823 under another definition [Q] | `baseline_2026-10-26/ledger_measures.py 2026-10-19` | the close gate refuses without evidence (ENGINE_CLOSE_ENFORCE_ACCEPTANCE_EVIDENCE) | built-not-verified pile up over 10% |
| M9 | "doing" items with a live lease | 0 of 123 (74 never leased, 39 lapsed, 10 released) | `baseline_2026-10-26/doing_leases.py` | every doing item leased or released | none given |
| M10 | lapsed leases open now / contested claims | 166 open items with lapsed lease; 19 contested claims total | `rimflow_metrics.py` (leases) | 0 contested on engine items (LEDGER_LEASE_HARDEN_ATTEMPT_TOKEN) | any stale effect accepted |
| M11 | V0 / verify backlog | 521 built items waiting; owed levels L1 134, L2 327, L3 51, L4 110, GREEN-MIN 67, GREEN-FULL 7; median age 17.0 d | `rimflow_metrics.py` (verify_backlog) | stops growing | grows over 10% in 7 d |
| M12 | verify results, 7 d | 314 pass, 52 fail, 115 partial | `rimflow_metrics.py` | none given | none given |
| M13 | art picks waiting on the owner (A1) | 71 rows from 38 of 73 open sheets (21 more skipped as manifest sheets) | `python3 src/RimMandrake/Utils/art/art.py review awaiting-pick --dry-run` | under 30 (CLEAR) | at 100 new art generation stops (operating_modes) |
| M14 | compactions without handoff | log counter: 681 rows, 19 distinct sessions, every row but 2 read MISSING (BENCH 437, FOUNDRY 230+2, pulse 8, RimMandrake 4). **Counter is suspect** (`COMPACTION_LOG_FIX_HELPERS_COUNTED_AS_SEAT`: one session logs many rows, so helpers appear to be logged as the seat). Independent count: 9 real `compact_boundary` records since 10-16 in top-level transcripts (BENCH 4, FOUNDRY 5), 5 of 9 with a handoff write earlier in the same file (loose proxy) | `baseline_2026-10-26/compactions.txt` (logger `D:\ClaudeWork\logs\compactions.jsonl`; transcript scan) | every compaction preceded by a handoff | none given |
| M15 | allocator peak helpers vs N | UNMEASURED (the hook logs nothing; `SLOT_HOOK_MEASURE_REFUSALS_AND_PEAK`). Current N: BENCH 4, FOUNDRY 0; 2 BENCH helpers running at 16:30 | `slot_allocator.py now`; `streams/allocation.json` | peak at or below N in 99% of 15-min windows | the hook ignores an owner override |
| M16 | worker failure rate, engine idle minutes, start cost | UNMEASURED (no engine exists; these judge the pilot only). Idle upper bound from ledger silences: up to 23.2 h [Q] | n/a | failure under 15%; idle under 10 min/day (single_primary §6) | failure over 30% of last 10; no accepted item for 6 h with ready items |
| M17 | owner checking time ("status?" turns, digest visits) | UNMEASURED at baseline (design: count BENCH turns that were only "status?" / "what needs me?") | none yet | falling day over day | none given |
| M18 | mods finished (a mod reaching done, verified) | **UNMEASURED**: no ledger event says "this mod is finished". Proxies exist but are not that: git touches (102 mods in 7 d), 130 mods known, items per mod | none | owner's goal: 1-2 mods ground to done at a time (FOCUS, Q3) | n/a |
| M19 | pushes to the owner per day and answer p90 | UNMEASURED (no push channel exists; D2 answer-latency reads 0 resolved and is suspected wrong [Q]) | n/a | at most 3/day; answer p90 under 24 h when home | none given |

Other numbers taken at the same time: leases take 362, renew 300, release 52 in 7 days; bounce (items re-opened) 195,
7 with 3 or more; blocked items 114 (median 22.8 d), the top blocker being the single-primary design itself (16 items);
bridge held BENCH 77.5 h, FOUNDRY 20.2 h, OWNER 8.8 h in the window (longest hold 21.1 h, BENCH); ledger instrument:
10 replay refusals, 0 tolerated fields.

---

## 5. How to return to this baseline

**The code and docs.** The tag marks the exact commit.
```
git fetch origin --tags
git checkout system-baseline-two-seat-2026-10-26            # read-only look, detached HEAD
git diff system-baseline-two-seat-2026-10-26 origin/main -- infrastructure/agents CLAUDE.md .claude   # what the redesign changed
git switch -c restore-two-seat system-baseline-two-seat-2026-10-26   # to work from it
```
Do not reset or force `main`. To revert only the redesign's changes, `git revert` its commits, or copy the files named
above from the tag with `git show system-baseline-two-seat-2026-10-26:<path> > <path>`.
The ledger is append-only and never rolled back: a later event cannot be un-written, so returning to the baseline
means returning to its *rules*, not erasing what the new system filed.

**The processes.** At baseline, the user systemd timers listed in
`D:\ClaudeWork\rimmandrake\baseline_2026-10-26\timers_enabled_2026-10-26.txt` (23) were active. After the redesign, any
timer the engine added (the tick, its triage and push timers; names not yet known) is switched off with
`systemctl --user disable --now <name>.timer`; re-enable a missing baseline timer with
`systemctl --user enable --now <name>.timer` (pulse units: `src/RimMandrake/Utils/pulse/systemd/install.sh`). The
engine's stop switch, per the design, is `touch engine.stop`.

**The seats.** Reopen the FOUNDRY window in `/home/mandrake/rm/foundry` (its clone is untouched until step 4 of the
rollout, which archives it) and start it on `infrastructure/agents/FOUNDRY.md`. BENCH needs nothing. Set the allocator
back to a FOUNDRY share with `python3 src/RimMandrake/Utils/slot_allocator.py set --seat FOUNDRY --n 1 --owner-said "<his words>"`
(the baseline had FOUNDRY at N=1 earlier on 10-26, 0 at the moment of tagging) and check `slot_allocator.py now`.
The `~/.claude/settings.json` hooks (compaction_watch, Placard, Machinist guards) are user-level and not in the repo;
this doc records that they were wired (Section 1).

**To measure the return,** rerun the scripts in Section 4 and compare with the baseline column.
