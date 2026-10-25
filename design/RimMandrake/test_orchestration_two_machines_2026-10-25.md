# Test orchestration on two machines: combined plan (2026-10-25)

**Asked by:** Lukas, 2026-10-25 16:20 PDT. He asked for a full design pass, three alternatives from GPT, an independent
Opus recommendation, then a single combined plan.

**Inputs:**
- Facts brief: `D:\ClaudeWork\rimmandrake\test_orch\brief.md`.
- GPT's three alternatives: `D:\ClaudeWork\rimmandrake\Transient\test_orch_gpt.md`.
- Opus's independent recommendation, written before GPT's reply was opened: `D:\ClaudeWork\rimmandrake\Transient\test_orch_opus.md`.

**Measurement scripts:** `D:\ClaudeWork\rimmandrake\test_orch\{waste,bridge_util,history_waste}.py`.

**Tags used below:**
- [M] measured.
- [P] proxy measurement.
- [A] assumption or proposal.

## 0. In five lines
1. **Most of the time was lost to choosing what to run, not to a lack of game capacity.** In run7, 66% of chain-minutes
   went to offline work done inside the live slot (32%), to re-testing chains already known to pass (32%), and to
   stale-only rows (2%) [M]. Across 95 historical runs, 58% of re-executed rows went PASS->PASS [M]. A second machine
   running the same selection would just waste twice as much.
2. **Architecture.** Agents *submit* test jobs to one deterministic queue on Archmagi and go back to other work. A dispatcher
   with no LLM sends jobs over SSH to a **durable worker on SteveDesktop**. That worker runs from a pinned sha and keeps
   a local outbox, so a dropped SSH link loses nothing. Archmagi's own game stays the **interactive** lane; SteveDesktop
   is the **batch** lane. Both GPT and Opus picked this design independently.
3. **Before anything runs, a known-good gate** drops every row whose dependency manifest matches a valid PASS already on
   record. **One host guard per machine** (BRIDGE widened by host, and taken by modcheck as well) keeps it to one
   driver per game.
4. **The dispatcher handles failures, not agents.** A game hang, a red canary, SSH loss or WSL interop loss each get one
   bounded recovery attempt; if that fails the lane is quarantined. An agent sees a 20-line summary only.
5. **Measurement.** A daily `modcheck metrics` file tracks WASTE, lane busy/held, queue age, minutes-to-decision, reuse
   hits and sweep misses, with alarms. Two writing helpers work in the bench clone on disjoint directories until Wed
   15:00. FOUNDRY keeps doing content.

## 1. What we already know (recalled and measured)
| quantity | value | source |
|---|---|---|
| run7 WASTE (chain-min) | offline-in-live 32% + known-good 32% + stale-only 2% = **66%** of 48.3 min, plus an ~11 min load | `waste.py` [M] |
| run6 WASTE | 39% + 21% + 4% = **64%** of 39.5 min | `waste.py` [M] |
| History: 95 run JSONs, 44 mods | 3,792 of 6,492 re-executed rows (58%) went PASS->PASS. FlowWorks 45%, Wasteland 74%, CreatureBehaviors 97% | `history_waste.py` [M] |
| Bridge, 2026-10-25 07:06-23:31Z | held 449 min; minutes containing a call 216 (48%); total call wall time 137 min (**31% of held**); 5 gaps of more than 60 min, 606 min in total | `bridge_util.py` [M] |
| Bridge, last 30 days | held a mean of 12.4 h/day; 19 h/day on 10-22..24, almost all of it BENCH (56.3 h vs 3.6 h) | second_workstation_study [M] |
| 2026-10-01 live pass | **8% productive**; 40% setup-gate failures, 30% harness defects | northstar_time_ledger [M] |
| Cold load | minimal list 22 s; Steve minimal 54 s; the owner's full list 11-25 min | [M] |
| Steve targeted run | sync 39 s + load 54 s + run 34 s for 9 rows, 9/9 PASS | stevedesktop_testcentre [M] |
| Game DOWN | 127 gaps totalling 47 h over 8 days | second_workstation_study [M] |
| Tokens | ~80K output tokens per closed item; 85% of tokens spent in subagents; ~1.5 Max accounts per week | [M]/owner |
| Owner answer latency | median 2.2 h, p75 14 h, **p90 66 h**; 148 items still open | ledger [P] |
| Tokens per live run; LLM vs script wall time per test | **UNMEASURED** | - |

**Already built since this morning:**
- targeted `--item/--chains/--rows` runs with StopAfter and a NOT_RUN tail (GPT believed this was still missing; it
  shipped in `modcheck/targeting.py`);
- offline chains skipped in targeted live runs;
- per-chain `phase_s`;
- `validity`/`freshness` fields;
- run manifests, plus reuse for the six external drivers.

**Still missing:**
- a known-good skip for modcheck's own chains (152 of run7's 159 stale rows had no manifest at all [M]);
- a queue, since an agent still watches every run inside its context;
- a host guard that modcheck itself respects;
- metrics produced as a daily number instead of reconstructed by hand, as for this doc.

**How to read the bridge numbers.** Held minus busy is mostly LLM think time between calls, plus holds kept while an
agent does offline work. Hold time is therefore a poor measure of capacity. The fix is to take scripted driving out of
the agent's context, not to add a second agent to the same game.

## 2. The three alternatives and how GPT and Opus each ranked them
The two writers described the space in different terms but arrived at the same ranking.

| | GPT | Opus | verdict |
|---|---|---|---|
| A. Thin SSH: an agent calls `remote_modcheck.sh` and waits | (the starting point for its Alt 2) | Alt 1: works today, but an LLM babysits every run, and Steve goes idle when the agent's context dies | **keep only as a manual escape hatch** |
| B. Central queue on Archmagi, deterministic dispatcher, SSH transport, durable worker on Steve | Alt 2, recommended, 36-53 h [A] | Alt 2, recommended, ~30-40 h [A] | **adopt** |
| C. Git-only immutable job queue: Steve polls git | Alt 1, 40-59 h; survives an SSH outage | not proposed: it puts queue churn into git, which is the contention he asked us to avoid | **defer**; build only if SSH proves unreliable |
| D. Delegated campaign runner: Steve chooses rows inside a bounded policy | Alt 3, 50-73 h; highest risk ("a faulty policy can efficiently generate useless tests") | - | **shadow mode after Wednesday** |
| E. Steve as a peer Claude seat | - | Alt 3: rejected. It breaks "a token-free runner, not a second agent farm", adds a third writer to src/, and costs more tokens per result | **reject**; only if Archmagi is down for days |

**What GPT added that Opus lacked, now adopted:**
- A durable worker and outbox on Steve, so execution does not depend on a live SSH session.
- Execution from a **pinned sha**, never from a moving `main`.
- **Unique attempt directories.**
- A host guard that also covers deploy and launch, and that **modcheck** takes; today modcheck takes no lock.
- **Fencing:** an expired lease never allows a second driver until the first process is confirmed dead.
- A WASTE metric in which unknown manifests are reported as *unclassified*, never counted as zero waste.
- Shared setup allocated across the rows that benefit from it.
- An incremental cost model for each job.

**What Opus added that GPT lacked, now adopted:**
- **Trains:** batch jobs by profile, so one deploy and one load serve many jobs. A full-list load departs only when the
  value queued for it is at least twice the load time.
- **Archmagi backfill:** the dispatcher uses Archmagi's game only when the bridge is free and has been silent for 10 min.
- The **queue lives outside git**, so it creates no commits.
- A **RUNNER ledger shard** written from its own clone, one writer per shard, which means no contention with BENCH or
  FOUNDRY.
- A per-case filter for the C# SelfTest, to recover the 4.5 min spent on rivers_switch_flips.
- **Script-the-second-probe:** any bridge probe an agent repeats becomes a script.
- A daily owner packet.

**Where the two disagreed, and how it was resolved:**
1. **Queue location.**
   - GPT: `infrastructure/state/test_jobs/` in git.
   - Opus: `D:\ClaudeWork\rimmandrake\testq\`, outside git.
   - **Resolution:** outside git. Only the *results* that close items reach the ledger. Jobs are ephemeral.
2. **Ledger writer.**
   - GPT: keep the RUNNER seat deferred, and have BENCH import results.
   - Opus: a RUNNER shard from a dispatch clone.
   - **Resolution:** RUNNER shard. Relaying through BENCH puts an LLM back in the loop, and into BENCH's git index.
     This goes on card Q2.
3. **Who builds it.**
   - GPT: a FOUNDRY-clone helper owns the modcheck work.
   - Opus: everything in the bench clone, FOUNDRY untouched.
   - **Resolution:** bench clone, two helpers on disjoint directories. FOUNDRY is the Sonnet content seat, and BENCH
     owns FlowWorks. This goes on card Q5.
4. **WASTE alarm level.**
   - Opus: 15%.
   - GPT: targeted 20% over 6 h with at least 20 classified minutes; 25% daily overall.
   - **Resolution:** GPT's thresholds. They do not fire on small samples.

## 3. Architecture

```
agents (BENCH/FOUNDRY helpers)            Archmagi WSL (no LLM)                    SteveDesktop (no LLM)
  testq submit --item X --rows ...  --->  D:\ClaudeWork\rimmandrake\testq\        ~/rm/runner @ pinned sha
  ...go do offline work...                pending/ running/ done/  (atomic mv)    worker: deploy, guard, load,
  testq show <id>  (20 lines)  <-------   dispatcher (systemd user timer, 60 s):    canary, rows, outbox/<attempt>/
                                            plan = modcheck --preview               |
                                            gate = known-good / manifest reuse      | ssh (start detached,
                                            train = group by host+profile           |  poll heartbeat,
                                            lane pick: Steve batch | Archmagi       |  fetch outbox)
                                              backfill when bridge free+quiet <-----+
                                            ingest -> RUNNER shard (~/rm/dispatch)
                                            FAIL -> finding on the item
                                            metrics -> daily file + Pulse tile
```

**Job record** (an immutable JSON file):
- `id, item, mod, selector (--item/--chains/--rows), profile, purpose (fix|guard|sweep|sensitivity|flake|commission),
  priority, not_before, requested_by, source_sha`
- `supersedes, owner_gate`

**Result record:**
- deployed identities (DLL/defs hash, ModsConfig hash) and the attempt id;
- per-row verdict plus `validity`/`freshness`;
- `phase_s`, the suspected cause, and artifact hashes.

A requested sha is never taken as the deployed identity; the worker attests what is actually deployed.

**Lanes:**
- **SteveDesktop, batch lane:**
  - every scripted targeted job, by default;
  - full-list profile probes;
  - the sweep rotation: at most one `--full` per mod per day, the stalest mod first, and only overnight;
  - C# SelfTest and T0 offline runs on its own CPU, so they never stall a game that is in use.
- **Archmagi, interactive lane:** agents debug live through the bridge and stage owner walkthroughs. The dispatcher may
  backfill it, taking the `archmagi` host guard.

**Selection, unchanged from focused_testing_plan:**
- T0 offline first, then T1 one runtime quantity, then T2 named-row prefixes, then T3 item chains.
- `--full` at most daily and never as a quota. "Unknown impact" returns `BLOCKED_SELECTION` to the requester and never
  escalates to `--full`.
- Every selected row names the decision it could change.

**Known-good gate:**
- A row is skipped and recorded `freshness=reused@<run>` when its full dependency manifest matches a valid PASS on
  record. The manifest covers chain `INPUTS` files, DLL hash, defs, test code and profile.
- Unknown `INPUTS` means "no reuse".
- A DLL change invalidates every C# row.
- The purposes `sweep`, `sensitivity`, `flake` and `commission` bypass the gate and are counted separately.

## 4. Deterministic helpers, ranked and sized [A]
| # | helper | where (one writer per directory) | replaces | hours |
|---|---|---|---|---|
| 1 | **Host guard**: BRIDGE keyed by host; modcheck, deploy and `rw_game` all take it; fencing; canary and identity preflight | `rimflow/`, `modcheck/session` | two drivers on one game; unsafe hand-overs | 6-8 |
| 2 | **Known-good gate**: per-chain `INPUTS` for modcheck's own chains; reuse inside `run_suite`; purpose bypass; audit | `modcheck/`, `FlowWorks/validation.py` | **32% of run7's minutes** | 6-10 |
| 3 | **Durable Steve worker**: pinned sha, unique attempt directory, heartbeat, outbox JSON, watchdog (extends `remote_modcheck.sh`) | `infrastructure/stevedesktop/` | fragile SSH sessions; HTML-only results | 4-6 |
| 4 | **`testq` plus dispatcher**: submit/show/cancel, plan via preview, trains, lane choice, backfill, ingest | new `src/RimMandrake/Utils/testq/` | an agent babysitting every run | 8-10 |
| 5 | **RUNNER shard ingest**: verify events from `~/rm/dispatch`; one finding per FAIL | `testq/ingest.py` + rimflow seat registration | verify lines relayed by hand | 2-3 |
| 6 | **`modcheck metrics`**: daily file, Pulse tile, alarms (section 5) | new `modcheck/metrics.py` | archaeology passes like this one | 4-6 |
| 7 | **C# SelfTest per-case filter** | FlowWorks `Program.cs` (serialise the DLL build) | 4.5 min of offline time spent in the live slot | 2 |
| 8 | **Owner packet builder**: one pre-reviewed phone page per day | `Utils/` | scattered pings | 3 |
| - | Campaign planner (GPT Alt 3) in shadow mode | after Wed | - | - |
| - | Pinned per-account `CLAUDE_CONFIG_DIR` | test in a disposable session only (card Q4) | - | - |

**Total:** about 35-48 h of helper time inside a 70 h window. Two helpers in parallel make this feasible, with about 20%
margin for the commissioning drills.

## 5. Metrics, dashboard, alarms
**WASTE (the exact definition):** executed live minutes on rows whose most recent trustworthy result was a VALID PASS
under the *same complete* dependency and profile manifest, with no invalidation since, plus minutes of offline-tagged
chains run live.
- Shared setup and teardown are split equally across the rows that benefit from them.
- Deploy and load are reported separately as "load overhead".
- Rows with an unknown manifest are counted as **unclassified**, never as zero waste.
- The figure is reported per lane per day as `WASTE / classified minutes`, alongside the unclassified share.
- `sweep` and `commission` minutes are tagged and budgeted, and kept out of the targeted WASTE.
- Until per-row manifests exist, `test_orch/waste.py` is the proxy: a chain-level PASS->PASS with nothing changed.

**Alarms [A]:**
- Targeted WASTE above 20% over 6 h, with at least 20 classified minutes: the dispatcher pauses duplicate admissions and
  files a finding.
- All-work WASTE above 25% a day.
- Unclassified above 30%: the gate is blind, so a manifest gap needs fixing.

**The safety twin of WASTE is sweep misses:** a valid new FAIL on a row that reuse or targeting skipped at the same
identity. Every miss raises an alarm, and the manifest responsible loses reuse until it is fixed.

**Also tracked:**
- Steve: busy%, idle-with-queue (target 0; alarm if the oldest ready job waits more than 10 min while the worker is
  idle), idle-empty.
- Bridge busy/held per host (target at least 60%; alarm if a hold sits idle more than 5 min while work is ready).
- Queue age p50/p90.
- Minutes from request to decision.
- Reuse hit rate, invalid attempts per attempt, load overhead per train.
- Accepted results per token (weekly).
- Owner queue: size and oldest age.

**Dashboard:**
- **Pulse tile:** WASTE, unclassified, misses, Steve busy/idle-with-queue, queue age, owner queue.
- **Daily file:** `D:\ClaudeWork\rimmandrake\testq\metrics\YYYY-MM-DD.json`.

**Baseline to beat:** run7 at 66%, bridge busy/held at 31%.

## 6. When things go wrong (the dispatcher acts; agents only read outcomes)
| failure | automatic response |
|---|---|
| Game hang (no reply within 2 x the chain's p90, minimum 120 s) | Mark the attempt INTERRUPTED and capture its evidence. Stop the owned process, run one clean restart plus canary, and retry once with the changed condition recorded. If that fails: `INVALID(HARNESS)` and the train moves on. Expected-row accounting stops partial output from reading as PASS. |
| Canary red after a load | The train is marked HARNESS, no mod row runs, the lane pauses, and a finding is filed |
| SSH/Tailscale down | Steve finishes the jobs it has already admitted into its outbox. The dispatcher stops sending there, re-routes profile-compatible jobs to the Archmagi backfill, and probes every 5 min. On reconnect it asks for the attempt id before any retry. Heartbeat missing more than 2 min: alarm. |
| WSL interop lost on Archmagi | The Archmagi lane goes down and Steve carries on. The journal and outbox survive on disk. |
| Runner `pull`/pin fails | The lane pauses and a finding is filed. The runner never commits, so this means someone wrote there. |
| Two drivers | The newcomer is rejected. A stale lease needs fencing (process confirmed dead) before a takeover. The owner's `./bridge` override uses the same host identity. |
| Publish rebase or conflict | Results are keyed by job id, never by sha. Publication stops and the outbox is kept. No game re-runs to recover a commit; no reset or stash. |
| Account exhausted | The lanes are token-free and carry on. Agents stop at pushed checkpoints and the next account resumes from the progress file. |
| Owner-only decision | Waits indefinitely. Never times out into approval. Other jobs carry on. |

## 7. Context windows and account switches
- **Test output never enters a context raw.** Agents see `testq show <id>`, which is at most 20 lines with paths.
  Waiting means submitting the job and then doing other work.
- **Checkpoints.** Helpers stay one item each, with progress files written skeleton-first. They checkpoint at about 100K
  tokens, before the 150K auto-compaction.
- **Account switches (three a week):** the runner and dispatcher use no tokens, so a switch never stops testing.
  - Switch only at handoff or wave boundaries, using the handoff ritual.
  - **Warm all three accounts tonight**, before he leaves.
  - No `/login` while Remote Control is in use: it drops every window on the machine.
  - Pinned per-account config dirs are the real fix, but they mean a 3-day migration. This week they are tested in a
    disposable session only (card Q4).
- **Seats don't message each other.** FOUNDRY's live needs become `testq submit` jobs, and the queue is the only channel.

## 8. Owner-away mode, Mon 10-26 to Wed 10-28 15:00 PDT (Work Laptop and iPhone)
- Only the reserved list (delegation_policy section 2) blocks on him. Everything else follows the charter: act first,
  and his word closes it.
- **Card windows:** cards are batched into two fixed windows a day (card Q3). Each card is pre-reviewed (presenter plus
  naive judge). Decision cards are kept apart from informational progress.
- **One daily packet** for the phone. It shows the decisions, the delegated-decision digest, the metrics tile, and any
  review sheet that passed prereview.
- **Walkthroughs** are queued as savegames plus zoomed captures that a script stages on Steve. A naive Opus judges them
  first. They are never presented as if he had walked through them himself.
- **Nights:**
  - Steve runs its targeted queue, then one rotating budgeted sweep.
  - Archmagi agents work through offline items and submit live needs to the queue.
  - When the queue is empty, Steve runs mapped missing evidence or sits idle. It **never re-runs greens to look busy**.

## 9. Build schedule to Wed 15:00 PDT (from Sun 16:45; about 70 h)
**Crew:** two writing helpers at a time, both in the **bench clone**, each owning its own directories. BENCH
orchestrates and integrates. FOUNDRY continues its content queue and touches no `modcheck/`, `rimflow/`, `testq/` or
`stevedesktop/` file.

| window (PDT) | helper H-A (`rimflow/`, `infrastructure/stevedesktop/`, `testq/`) | helper H-B (`modcheck/`, FlowWorks validation) |
|---|---|---|
| Sun 17:00 - Mon 05:00 | #1 host guard; #3 durable Steve worker | #2 known-good gate (INPUTS for FlowWorks chains first) |
| Mon 05:00 - Mon 21:00 | #4 testq + dispatcher; #5 RUNNER ingest | #6 metrics; #7 SelfTest filter (DLL build serialised) |
| Mon 21:00 - Tue 12:00 | **Commissioning:** the same frozen job on both lanes with equivalence checked; drills for a killed game, dropped SSH, duplicate delivery and a publish conflict | gate audit: one deliberate `--full` sweep to measure misses |
| Tue 12:00 - Wed 06:00 | Real workload: FlowWorks goes queue-only, other mods follow; #8 owner packet | fixes from the drills; WASTE alarm tuning |
| Wed 06:00 - 15:00 | Soak, no new architecture. A metrics review against the run7 baseline goes into the Wed 15:00 report | - |

**Commit discipline:**
- Explicit-path commits per unit, and `./publish` immediately. Only one helper publishes at a time, by convention.
- A partial commit inside a shared clone uses a private index (lesson 20261025T223731Z).
- FlowWorks DLL builds are serialised, so that no peer's dirty DLL blocks publish (DLL_SOURCE_STAMP_GUARD).
- FlowWorks SelfTest staging is never run by two helpers at once.
- Interfaces between the two helpers (the job and result schemas) are committed first, in H-A's directory.

## 10. Owner questions (card-ready; recommendation marked)
**Q1. How should Archmagi and SteveDesktop be coupled?**
Context: GPT and Opus independently ranked these the same way. The choice sets the next 70 h of building.
- **(Recommended) A central queue on Archmagi, an SSH dispatcher, and a durable worker on Steve.**
  - For: it extends the route that works today, keeps one authority, uses no tokens on Steve, and survives brief SSH
    drops.
  - Against: if Archmagi goes down, new dispatch stops.
- A git-only job queue that Steve polls.
  - For: it survives an SSH outage.
  - Against: it puts job churn into git, which is exactly the contention to avoid, and costs about 6 h more.
- A delegated campaign runner on Steve.
  - For: the most autonomy.
  - Against: a bad policy generates useless tests at scale, and it is not credible by Wednesday. It would only run in
    shadow mode.

**Q2. Where do test results enter the ledger?**
- **(Recommended) A new RUNNER shard, written by the dispatcher from its own clone.**
  - For: one writer per shard means no git contention, and no LLM sits in the loop.
  - Against: it is a fourth shard, and the RUNNER seat would no longer be deferred.
- A BENCH seat relays the verify lines.
  - For: no new writer.
  - Against: an LLM and BENCH's index are back in every result.
- Keep results only in testq files for this week.
  - For: zero ledger work.
  - Against: items cannot close on that evidence until someone relays it.

**Q3. When will you look at cards this week?**
- **(Recommended) Two fixed windows, e.g. 07:30 and 12:15 PDT, with one batched pre-reviewed packet each.**
  - For: agents can plan around these times, and you are not pinged ad hoc.
  - Against: an urgent card waits up to about 12 h.
- One evening window.
  - For: the least interruption.
  - Against: a decision can take up to 24 h.
- No fixed windows: packets queue and you open them when you can.
  - For: no commitment from you.
  - Against: agents cannot plan, and the p90 owner latency is already 66 h.

**Q4. How should account switching be handled this week?**
- **(Recommended) Warm all three accounts tonight, no `/login` during Remote Control use, switch only at handoffs, and
  test pinned config dirs in a disposable session only.**
  - For: no risk of losing Remote Control while you are away.
  - Against: the real fix waits until after Wednesday.
- Adopt pinned per-account config dirs now.
  - For: switches stop disrupting work.
  - Against: a roughly 3-day migration of Archmagi with you unreachable.
- No change.
  - For: zero work.
  - Against: one mistimed `/login` drops every window.

**Q5. Who builds it?**
- **(Recommended) Two helpers in the bench clone on disjoint directories; FOUNDRY stays on content.**
  - For: BENCH owns FlowWorks and modcheck, and the content queue keeps moving.
  - Against: everything waits on BENCH's single clone and publisher.
- GPT's split: a BENCH-clone helper for the queue, transport and guard, and a FOUNDRY-clone helper for the modcheck
  work.
  - For: two publishers, more parallel.
  - Against: FOUNDRY writes BENCH-owned code, and content stalls.
- Three helpers in the bench clone.
  - For: faster.
  - Against: shared-index and SelfTest staging collisions, as measured today.

## 11. Evidence and provenance
- **Waste:** `D:\ClaudeWork\rimmandrake\test_orch\waste.py`, run over `live_20261025` runs 5-7.
- **History:** `history_waste.py` produces `history_waste.txt`.
- **Bridge utilisation:** `bridge_util.py` produces `bridge_util.txt`, from `scratch/bridge_calls.jsonl` and the ledger.
- **Recalled studies:**
  - `design/RimMandrake/focused_testing_plan_2026-10-25.md`
  - `second_workstation_study_2026-10-24`
  - `stevedesktop_bringup_plan_2026-10-24`
  - `northstar_time_ledger_2026-10-01`
  - `D:\Luke\dev\claude-remote-control\docs\2026-10-25-account-switching-design.md`
- **The raw outputs of both writers are kept unedited:** `Transient\test_orch_gpt.md`, `Transient\test_orch_opus.md`.
