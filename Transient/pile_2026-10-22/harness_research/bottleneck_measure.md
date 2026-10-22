# Who waits on whom — measured from the logs (2026-10-22)

Item: `HARNESS_BOTTLENECK_MEASURE_WHO_WAITS_ON_WHOM`. Owner, 2026-10-22 ~16:05 PDT: *"You see game time as the limiting
factor? Is that true? If we could test twice as many things in game but the llm delays were the same how much would that
help? Look at the logs to find out."* and, on per-writer clones: *"You keep changing your mind on this. I would need to see
evidence based on our stats that this is an improvement."*

**Short answer.** Inside the live belt, the game is the main cost: 79% of the belt's wall time was game running or
restarting. **But the game was not what held the day back.** For 321 minutes (09:56–13:41 and 13:42–15:17) the
orchestrator was frozen inside two open question cards. Helper slots sat empty, and the bugs the belt found waited a
median of 152 min for a fixer. Doubling game throughput would have finished the belt ~2 h 16 min sooner, but the
day's fix → re-prove chain **0 min sooner**, because the fixers could not start until the card was answered at 15:17.

## Sources and method (every number below is MEASURED unless marked otherwise)
- **Transcripts** (stream-parsed, never read whole):
  - belt `agent-aa84a5958d27682c0.jsonl`, walk rebuild `agent-a95636a2fbad20c90.jsonl`, orchestrator
    `5453bc27-….jsonl`, all under `/home/mandrake/.claude/projects/-home-mandrake-rm-bench/5453bc27-3eb8-4e2e-b5ef-b3cc25266b27/`;
  - for the publish census, all 2,334 BENCH and FOUNDRY transcripts modified since 2026-10-08.
- **Per tool call**: start = the timestamp of the assistant record holding the `tool_use`; end = the timestamp of the
  record holding its `tool_result`. Overlapping calls are merged on a one-second timeline, so time is never counted twice.
- **Classes:**
  - **game** = a Bash call running `python.exe`, the bridge client the proofs use;
  - **restart+deploy** = `deploy_custom_mods`, `./game`, `wait_menu`, a DLL copy, plus the ledger's
    `game DOWN→UP` windows;
  - **publish/git** = `./publish` or git write verbs;
  - **offline** = any other tool;
  - **LLM turn** = any second with no tool running. That covers model thinking and writing plus harness overhead.
- **Times** are PDT. Ledger `ts` is UTC and was converted.
- **Scripts** (scratch, not committed):
  `/home/mandrake/.seat-tmp/BENCH/claude-1000/-home-mandrake-rm-bench/5453bc27-3eb8-4e2e-b5ef-b3cc25266b27/scratchpad/{tl,share,gsplit,pub,git22}.py`.

## 1. Timeline breakdown

### 1a. Live proof belt, 08:48:00–14:44:34 (356.6 min, 684 tool calls)
| class | min | share |
|---|---|---|
| (a) game running proofs / ticking (`python.exe` calls) | 271.7 | **76.2%** |
| (b) cold loads, deploys, restarts | 8.6 | 2.4% |
| (c) LLM turns (no tool running) | 51.7 | **14.5%** |
| offline tools (edits, greps, rimflow, mocks) | 14.4 | 4.1% |
| publish/git | 10.1 | 2.8% |
| (d) waiting on fixers, inside the belt | 0 | the belt never slept; it ran other proofs, then **ended** at 14:44 with re-proves blocked on fixers |
| (e) bridge idle during the belt | 0 | |

- **LLM turn gaps:** 656 gaps, median 4 s, p90 9 s, max 36 s. **None longer than 2 min.**
  The belt.md gaps the harness report quoted (12:36→12:52, 13:13→13:41) were **not** LLM idle. They were a 595-s
  `thirst_live` run and four `flow_bignet_live` runs (510 s, 354 s, 323 s, 303 s). The report's "dispatch latency" reading of
  those gaps was wrong for the belt.
- **Restarts:** 4 game DOWN→UP windows (09:37, 09:56, 10:46, 11:14), 1.2–2.4 min each on the 14-mod tier. Three were DLL
  redeploys and one was a wedge after loading a save made on another mod list.
- **Hourly game share:** 59–87%. LLM share 9–24%.
- **Inside (a), not split further.** How long went to map generation, ticking and bridge round trips is UNMEASURED.
  - Python calls of 60 s or more: 75 calls, 240 min.
  - Python calls under 60 s (ad-hoc bridge pokes): 147 calls, 28 min.
  - Three runs were cut off at the 595 s shell cap (29.8 min).
  - **Upper bound of 143 min:** long runs of a script that was run again later. This bound includes deliberate
    regression reruns on a new DLL and chunked groups. How much of it was HARNESS churn is UNMEASURED.

### 1b. Walk rebuild, 15:17:35–16:15:20 (57.8 min so far; the helper is still running)
| class | min | share |
|---|---|---|
| (a) game | 23.9 | 41.4% |
| (b) restart+deploy | 11.0 | **19.0%**: 4 DOWN→UP cycles, one per fixer DLL that landed (c8eb3b2c83, 8d6a1913ab, 29d29cbc9d, d84d296f3d) |
| (c) LLM turns | 12.3 | 21.3% (median gap 3 s, max 34 s) |
| offline | 4.5 | 7.9% |
| publish/git | 6.0 | 10.4% (37% of the 16:00 hour) |

### 1c. The orchestrator's day (07:38–16:17), which is where the waiting is
- **Blocked inside AskUserQuestion: 423 min**, across 17 cards.
- **Two big blocks:**
  - **09:56:06 → 13:41:52 (225.8 min):** three helper notifications (10:01, 10:02, 10:06) queued unread.
  - **13:42:16 → 15:17:05 (94.8 min):** the belt's completion notice (14:44:34) queued unread for 33 min.
- **Helper concurrency over 516.9 min:**
  - 0 helpers for 33.0 min (bridge idle 14:44→15:17);
  - **exactly 1 helper (the belt) for 316.9 min**;
  - 2–5 helpers for 166.9 min;
  - mean 1.75.
  - **Between 10:06:38 and 14:44:34, no helper ran except the belt.**
- **Bug filed → fixer dispatched**, for the 8 MOD/HARNESS findings the belt filed:
  - **dispatched early:** DRAWDOWN 09:25 → fixer E at 09:51 (26 min), the only one before the block. Its fix was deployed
    at 11:15 and re-proved in the belt at 11:24;
  - **dispatched at 15:17–15:18:**
    - CAUSEWAY: filed 09:15, waited 362 min;
    - OVERFLOW_FIRST_WET_RUN: filed 10:11, waited 307 min;
    - SPILL: filed 10:56, waited 262 min;
    - SUSPENSION_BUTTONS: filed 11:50, waited 208 min;
    - RAILING: filed 13:41, waited 96 min;
    - SETTINGS_SEARCH: filed 14:30, waited 48 min;
    - GLOWTANK: filed 14:35, waited 43 min;
  - **across all 8:** median **152 min** waiting, against 8–30 min of fixer wall time once a fixer was running
    (fixer G 15.1, fixer H 30.2, overflow 2b 21.6, fixer I 12.8 min).

**Who waited on whom:**
1. The orchestrator waited on the owner's card.
2. The fixers waited on the orchestrator.
3. The re-proves waited on the fixers.
4. The walk rebuild then paid one game restart per fixer landing.

The belt itself waited on nothing. It ran the game about 3/4 of the time.

## 2. Counterfactuals (Amdahl, from the shares above)
**Assumptions:**
- "2× in-game throughput" halves class (a). Restarts (b) stay serial: a second lane does not shorten one relaunch.
- LLM turns and offline time are unchanged, and one LLM can feed two lanes without slower turns. That last part is
  UNMEASURED and optimistic.
- The orchestrator's card blocks are unchanged unless stated.

| scenario | belt (356.6 min) | walk rebuild (57.8 min so far) | the day's fix → re-prove chain |
|---|---|---|---|
| **2× game throughput** | −135.9 min (ends ~12:28, not 14:44): 1.62× | −12.0 min (21%) | **0 min sooner.** Fixers could not start before 15:17 (card answered 15:17:05). The bridge would sit idle ~169 min instead of 33 |
| **Halve LLM turn latency** | −25.9 min (7.3%) | −6.2 min | **0 min.** The block was the owner card, not model speed |
| **Zero orchestrator idle** (helpers dispatched as bugs are filed, nothing blocks on a card) | ~+5–10 min (ESTIMATE, not measured: each extra fixer DLL costs one 1.2–2.4 min restart, plus the deploy) | most of its 4 restarts and re-proves would have fallen inside the belt | **~55–60 min sooner** for the day's end (ESTIMATE). The last bug was filed 14:35; the measured 8–30 min fixer time plus a ~2 min restart plus a re-prove puts the end near 15:15, against ≥16:15 measured (still running). Median **152 min sooner** per fix |
| **Zero publish collisions** | ≤ −10.1 min (an upper bound: all publish/git time, successful ones included) | ≤ −6.0 min | ≤ ~10 min. Across both seats, every refused publish call today cost 7.3 min in total |

**Plain statement.** The game IS the limiting factor *inside the belt*, at 79% including restarts. It is NOT the limiting
factor *for the day*. Today's binding constraint was the orchestrator blocking on an owner question card for 5 h 21 min
in two stretches while the belt was its only running helper. A second game lane today would have produced an earlier
idle bridge, not an earlier finish. It pays only once dispatch never blocks; after that, the belt's 76% game share says
2× lanes would cut belt time by ~38%.

## 3. Shared-clone cost, from our stats

### 3a. Publish refusals per PDT day (every `./publish` call in BENCH and FOUNDRY transcripts since 10-08)
| day | calls | dirty shared tree (`reset --keep`) | rebase conflict (of which on the DLL) | DLL/source stamp guard |
|---|---|---|---|---|
| 10-08 | 229 | 0 | 5 (1) | 0 |
| 10-09 | 135 | 0 | 0 | 0 |
| 10-10 | 63 | 0 | 1 | 0 |
| 10-11 | 104 | 9 | 0 | 1 |
| 10-12 | 100 | 0 | 0 | 0 |
| 10-13 | 31 | 0 | 0 | 0 |
| 10-14 | 118 | 4 | 0 | 0 |
| 10-15 | 293 | 11 | 2 | 4 |
| 10-16 | 276 | 18 | 1 (1) | 1 |
| 10-17 | 169 | 7 | 4 (4) | 0 |
| 10-18 | 268 | 7 | 3 (3) | 2 |
| 10-19 | 217 | 0 | 0 | 2 |
| 10-20 | 250 | 6 | 3 (3) | 0 |
| 10-21 | 206 | 5 | 0 | 1 |
| **10-22** | **240** | **15** | **28 (23)** | **2** |
| **total** | 2,699 | **82** | **47 (35)** | **13** |

Benign refusals ("nothing to publish", usage errors: 115) are excluded. Today's 45 collision refusals are 3× any earlier
day, and 23 of them were on the FlowWorks DLL.

### 3b. Other costs
- **Time lost in refused calls today:** 7.3 min in total (stamp 4.0, conflict 1.9, dirty 1.4).
- **Recovery commands today** (reset --soft, cherry-pick, merge-tree/commit-tree, scratch or shared clones, `./sync`):
  50 BENCH calls (4.3 min) and 15 FOUNDRY calls (0.2 min).
- **All publish calls today:** BENCH 236 (58.2 min) and FOUNDRY 148 (49.6 min), median 7 s. These ran in parallel
  helpers and mostly off the critical path.
- **DLL rebuilt after a rebase or merge:** 13 commits on origin/main today whose subject says so. Today's `winbuild.py`
  calls numbered 193, median 4.4 s, max 199 s, 59.9 min summed across both seats.
- **Commit → landing** (author date → committer date on origin/main; a rebase or replay resets the committer date):
  - today: 432 commits, median 0.0 min, p90 3.1 min, max 25 min; 17 took longer than 10 min and none longer than 60;
  - earlier days had a p90 of ≤0.4 min, except 10-16 (3.8).
  - Stranded episode: the belt's 08:58 commit 8e13037d85 sat behind a peer's uncommitted `RM_SheetMath.cs` and landed
    +20 min.
- **Work lost:** none found. `origin/main..main` holds 2 BENCH commits and 1 FOUNDRY commit, all made at 16:17–16:19,
  i.e. in flight. Committed work lost to the shared clone is UNMEASURED beyond that check.
- **Correctness incidents from the shared tree, today** (lessons filed):
  - `winbuild` baked another helper's uncommitted C# into a DLL (lesson 2026-10-22 16:37Z; the stamp guard caught it);
  - a side-clone workaround pushed with the wrong e-mail to the PUBLIC repo (2b85094eb0, lesson 16:01Z).
  - 9 of the 45 lessons that mention publish/rebase/srchash were filed today.
- **Already drifting toward clones.** Agents now build and land from throwaway clones as a workaround (lessons 09:09Z,
  16:37Z, 16:51Z). That workaround has its own trap: the Windows `obj/` cache built a stale DLL in a scratch clone
  (fixer I, lesson 22:36Z).

### 3c. What per-writer clones + a serial lander would and would not remove (projection, NOT measured)
- **Removed by construction:** the 82 dirty-shared-tree refusals (10 days of 15 had some) and the
  "winbuild bakes a peer's edit" class.
- **Not removed:** the 47 true rebase conflicts. They move to the lander. 35 are on the DLL, and those go away **only if
  the lander (one builder) rebuilds DLLs from the merged source**. That design also clears the 13 stamp-guard refusals,
  **and it does not need clones**: it works in the shared clone too.
- **Added costs:**
  - **Disk:** a full copy measured 60.6 s and 6.13 GB (objstore trial, 2026-10-08). Borrowed clones save ~6 GB and
    ~60 s each, but the store costs ~6 GB itself.
  - **Stray clones:** 18 strays filled 276 GB on 2026-10-11 (GIT_WORKFLOW.md).
  - **Later conflicts:** a conflict surfaces at landing, after the writer has left. Today the median commit landed
    in 0.0 min.
  - **Build cost:** per-clone `obj/` caches that can go stale (lesson 22:36Z).
- **Upper bound of the saving on today's critical path:** ≤10 min on the belt and ≤6 min on the walk rebuild. That is
  all of their publish/git time, successful publishes included.

### 3d. What was decided when, and what agents recommended (the "changing your mind" history)
| date | what agents did or recommended | evidence / owner ruling |
|---|---|---|
| ≤ 09-18 | Worktree agents, merged into `worktree-agent-*` branches | commits "Merge remote-tracking branch 'origin/main' into worktree-agent-…" |
| 09-23 | **Agents recommended worktrees:** "default multi-file or long-running subagents to `isolation:"worktree"`" (580ff317a1, citing index-lock contention) | agent doctrine, not an owner ruling |
| 09-25 | A merge in the shared tree lost 215 files; doctrine "worktree agents land their own work" (80386ce4b8) | incident |
| 10-01 | Git research and plan (`git_workflow_plan_2026-10-01.md`) measured worktree week: 132 worktrees, 146 branches, **68 never merged holding 257 unique commits**, `/tmp` 100%, throughput 268 → 178 commits/day, recovery commits 2.4% → 4.2% (one confounded week). Plan: **separate seat clones** + a subagent worktree pool | agent plan |
| 10-02 05:15 | **Owner, by card: Worktrees OFF** (513fe46a41). 05:35: the pool was retired, *"owner 2026-10-02: worktrees were a mistake"* (b3d14cc2e4). GIT_WORKFLOW: "Why: worktree agents duplicated whole checkouts and stranded work on side branches." Rule: "Writing helpers run one at a time when their paths could overlap." | **owner ruling** |
| 10-08 | Object-store trial, so throwaway clones borrow objects (`objstore_trial_2026-10-08.md`) | agent trial |
| 10-11 | 92 of 93 old worktrees deleted, 374 GB freed. 18 stray scratch clones had filled 276 GB | cleanup |
| 10-22 | Helpers land and build from throwaway clones as a workaround (lessons). Harness report **R2 recommends one clone per writer + a serial lander** | agent recommendation |

So agents went from a shared tree, to worktrees (09-23), to seat clones plus a worktree pool (10-01), to one shared clone
per seat by your ruling (10-02), and now to per-writer clones (10-22). The owner ruled once. Agents changed the
recommendation four times, each time after one bad week. A per-writer clone is not a worktree (no shared index, no side
branches left behind). But it brings back the failure that drove 10-02, stranded work in places nobody looks, unless the
lander is the only path to origin.

## 4. Verdicts

**Q1: is game time the limit; would 2× in-game throughput help?** Inside the belt, yes: the game took 76% and restarts
2%, so 2× lanes would cut the belt by ~2 h 16 min (1.62×). For today's actual finish, **no: 0 min**. The fix → re-prove
chain was gated by the orchestrator blocking 321 min on two owner cards. During that time only the belt ran, and found
bugs waited a median of 152 min for a fixer that takes 8–30 min. The cheapest large gain is dispatch that never blocks
on a card (helpers spawned the moment a bug is filed). That would have ended the day ~1 h sooner and landed most fixes
2.5–6 h sooner. Only after that does a second lane pay.
- **Evidence:** strong for the shares and the blocking (transcripts, to the second). Medium for the "~1 h sooner" figure:
  it projects fixer times measured on other bugs.
- **To settle it:** run one belt day with non-blocking cards (questions sent and the session continuing) and
  auto-dispatch of fixers on `filed` events, then re-run this script. If the belt's game share stays above 70% and the
  bridge never idles, test the second lane (report E1.2: ≥1.5× proofs per hour).

**Q2: would per-writer clones + a lander beat the shared clone?** The stats do **not** show a large time cost. Refused
publishes cost 7.3 min of call time today. Landing delay has a median of 0 and a max of 25 min. No committed work was
found lost. What they do show:
- 82 dirty-tree refusals over 15 days, which clones would remove;
- 47 true conflicts, 35 of them on the DLL, which clones would only move to the lander;
- today, a rising curve (45 collision refusals, 3× any earlier day) and two correctness incidents (a peer's C# baked
  into a DLL; the wrong e-mail pushed to the public repo).

Most of today's pain comes from the DLL being built by each writer. **"One builder rebuilds the DLL from merged
source at landing" removes 48 of the 142 collisions with no clone change.** I would do that first and keep your 10-02
model.
- **Evidence:** medium. The refusal counts are strong; the time cost of the recovery LLM turns that follow a refusal is
  UNMEASURED.
- **To settle it:** for one week, tag every refusal-recovery turn (or measure time from refusal to PUBLISHED per commit).
  Separately, run report E2.1 (3 clones, overlapping edits, an interrupted landing): 0 lost commits and conflicts reported
  with lineage. Switch only if the weekly recovery time exceeds the lander's measured cost.
