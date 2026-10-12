# The ratchet workflow and the token burst to Wed 16:00

*Design, BENCH design lead, 2026-10-11 evening. Answers the owner's two questions of 2026-10-11 ~17:55 PDT.
Evidence (measured by seven read-only agents tonight, commands inside each file):
`design/RimMandrake/ratchet_evidence_2026-10-11/ev_*.md`. Status: DRAFT until he rules on §F.*

## Executive summary (phone-sized)

1. **We produce faster than we converge.** In 30 days: 8,726 commits, 1,882 items filed and 1,172 ended,
   so 850 are open now. Only 1 of 73 mods is GREEN on modcheck. Code-review debt went from ~100 files to
   ~4,265. The work is not slow. It is open-loop.
2. **Your review time is unshaped.** 107 sheets served, 18 ruled by you. Today's GSS sheet had 151 rows and 4 needed
   you. Agent pre-fills are stored where your choices go, and 64% of all recorded "decisions" carry no owner timestamp.
3. **Validation mostly re-confirms.** GSS `proof_all` ran 15 times (2.4 h), and the last 3 were identical. 235 modcheck
   runs changed a mod's status 6% of the time. 189 bridge-hours were held.
4. **Most of the parts already exist and aren't connected.** rimflow levels, the modcheck per-mod ladder, the artboard
   machine pre-review (built, never run live), RimPulse and telemetry are all there. The missing piece is one ladder
   per biome that only moves forward, plus one queue for you.
5. **The ratchet:** each biome climbs 7 rungs (R0–R6). A rung advances only when a check writes evidence. An edit
   re-checks only the rungs it touched. Every item that reaches you says *what you're judging and what happens if
   you skip it*.
6. **The burst (Sun night → Wed 16:00):**
   - One infrastructure lane builds the board, your inbox and the sheet fixes by Monday noon.
   - Four biome lanes, each in its own clone and owning its own paths, push the smallest-gap biomes up the ladder.
   - One live-game lane runs a single overnight queue.
   - Your load is capped at ~10 min in the morning, ~10 at lunch and 60–90 in the evening.
7. **Target, not prediction:**
   - 6 biomes at R3 (offline-complete plus a live proof at the current hash).
   - 3 at R5 (your look done).
   - Board and inbox live.
   - A method kit you can take to work.
8. **Decisions for you are in §F:** rung definitions, the skip-means-default policy, the convergence budget, which
   biomes, and the burst cap.

---

## A. Diagnosis — the failure modes, measured

| # | failure mode | evidence |
|---|---|---|
| F1 | **Open-loop production: inflow beats convergence** | 1,882 filed vs 1,102 closed + 41 dropped + 29 superseded in 30 d, and 850 open by the ledger (`ev_git_ledger.md` §2). Review debt (dirty + never-entered) went from ~100 on 09-25 to ~4,265 now (`ev_slowloops.md` §2). modcheck has RED 61, GREEN 11, DRAFT 5, and 1 GREEN of 73 by `modcheck status` (`ev_existing_designs.md`). Codebase-health green flat at ~1.8–1.96k while files tripled (2,186 → 7,046). |
| F2 | **Bookkeeping crowds out work** | The top-15 most-churned files in 30 d are all ledger shards, queue views, health JSON or DLLs, and none is mod source (`ev_git_ledger.md` §1). Subjects classed "ledger sync": 1,762 of 8,726. Lodestar has 1,370 of 2,412 commits (57%) that are mechanical heartbeats or touches, and its sweep has produced 0 improvements (`ev_lodestar.md`). |
| F3 | **Owner review is unshaped** | 107 sheets served since 09-11; 18 carry `by=owner` (502 rows, ~28 rows/sitting) (`ev_review_validation.md` §1). Today: 151 rows served, 4 needed you (2.6%). Across 195 decisions files, 4,560 of 12,687 entries (36%) carry an owner timestamp. The `prefill` and `ruled` state never flips on your click (`gss_all_art_sheet_2026-10-11.decisions.json`: writeCount 26, state still `prefill`). Pre-fill is written into `decision` itself. There is no purpose field: you asked *"I need to know what I'm reviewing FOR"* (`conversations/2026-10-11-2000-edefebc8.md` ~l.688). 2 junk-reskin sheets (517 rows) were never opened. RimPulse logged 155 "needs owner input" alarms with 28.4 h of cumulative waiting in 3 days. 246 `AskUserQuestion` calls across 26 sessions. (`ev_art_review.md`) |
| F4 | **Inputs and memories trusted without a check** | The sheet builder read a `defs.sqlite` 7 days old from before the rename. `scale_panel.py:111` records the fingerprint and compares nothing. Code-drawn GSS art has no def, so a def-driven sheet cannot see it. "The regenerated clamp" was recalled, not looked up; no artpipe job exists (`ev_art_review.md` causes 1, 2, 7). |
| F5 | **Validation re-confirms instead of discovering** | GSS `proof_all`: 15 runs, 8,543 s, the last 3 identical 105/105 (`ev_slowloops.md` §4). modcheck: ≥235 runs on 77 mods, 15 status changes (~6%). 436 verify events, with one item verified 13 times. 167 bridge holds totalling 189 h, 8 over 6 h. The overnight run on 10-11 found 12 faults, 1 of them a mod bug, which you called "mostly ceremony" (`ev_existing_designs.md`). No join exists from proof output to item status (`NORTHSTAR_RESULTS_JOIN_1`, open). |
| F6 | **Status decays faster than it is restored** | Clean marks and modcheck GREEN are bound to the whole-file or whole-mod hash, so any edit sends them back to zero (`debug_process.md` §1; `ev_slowloops.md` §2: 356 clean marks on 10-11, and the same pass then fixed 34 dirty files). With high edit rates the ratchet slips backwards. |
| F7 | **Rediscovery and built-but-unadopted tools** | "Four of six 'new' mechanisms already existed" (CLAUDE.md, 09-23). An agent's own account: *"Each one rediscovered the same things ... three more question cards. That alone accounts for most of the two hours on Leaning Scrub"* (`conversations/2026-10-08-1428-de9591de.md` l.647). The artboard pre-review is built with 26/26 selftests and was never run live. `human_review.py` exists for GSS only. The telemetry design says "nothing built" though it is built. `queue/HUMAN.md` was last edited 08-26 (`ev_existing_designs.md`). |
| F8 | **Parallel writers collide in git** | Worktree week: 132 worktrees, 68 unmerged branches, throughput 268 → 178 commits/day, then the owner banned worktrees on 10-02. ~8 index.lock incidents. 215 files lost on 09-25. 53 files stranded by autostash on 10-10. Today, publish was refused over another clone's untracked `Transient/` files (`ev_git.md`). Since 10-02, per-seat ledger shards measure 0 conflicts. The remaining risk is a **shared index** and **generated output tracked in git**. |
| F9 | **No per-biome "done" ladder that anyone climbs** | 26 biome mods. All have C#, settings and `validation.py`. None has `northstar/proof_all.py`. 24 are DRAFT. UNCOVERED walk lines run 1–18 per biome. CLEAN review runs from 0/28 to 15/32 (`ev_biomes.md`). Pyrelands is the only VALIDATED north star, and its stored run is RED and old. GSS (not a biome) is the reference: one proof, 0 uncovered, 69/70 CLEAN, its own tier, and a human-look layer kept apart from the pass bars. |

**One sentence.** The project has excellent instruments but no ratchet: nothing turns a passing check into a
status that only rises. Nothing stops new work from being filed against a mod that has not converged. Nothing
shapes what reaches you.

---

## B. Part 1 — the ratchet workflow

Each recommendation has the shape: **what** · evidence · pros / cons · build cost · **the test that shows it works**.
Costs are agent-hours of opus/sonnet work, not owner time.

### R1. One ladder per biome, advanced only by evidence (the spine)

- **What.** Each biome mod gets a row in `infrastructure/state/ratchet/<Mod>.json`, one file per mod so writers never
  share one. The rungs are below. Each rung names **one command** whose exit code and output file are the only way to
  advance it. A rung records `{sha, inputs_fingerprint, evidence_path, at, by_check}`.

  | rung | name | the check that advances it | built today? |
  |---|---|---|---|
  | R0 | loads | offline: `validate_patch.py --live --defs`, selftests named for the mod, deploy dry-run clean | yes, scattered |
  | R1 | specified | walk has 0 UNCOVERED `must be true` lines (`modcheck floor`) | yes |
  | R2 | art-complete | art manifest = every texPath **and** every code-drawn texture the mod ships; each has own art passing Tier A pixel checks; manifest diffed against the mod's `Textures/` (coverage, not rows) | partial (Tier A built; coverage diff not) |
  | R3 | proven | `proof_all` on the mod's own minimal tier, at the current hash, all PASS, recorded through the results join | GSS only |
  | R4 | pre-reviewed | artboard live capture → STAGING/ART_FIX auto-resolved; only JUDGEMENT rows remain, now in your inbox | built offline, never live |
  | R5 | owner-seen | your JUDGEMENT rows ruled (by your click, not a pre-fill) | sheets exist; provenance broken |
  | R6 | ship-ready | C# CLEAN, settings screen selftest, full-list load + save/load soak | partial |

- **Regression rule.** A rung drops only when **its own inputs** change. Each check declares its input globs, and the
  ledger re-runs the cheapest affected check on change. A texture edit re-opens R2 and R4 for that one row. It does
  not reopen R3. This replaces whole-mod-hash STALE (F6).
- **Evidence.** F1, F6, F9. GSS shows the rungs are reachable (`ev_biomes.md` "What GSS has").
- **Pros.**
  - One number per biome you can read.
  - "Done" becomes a property of evidence, not prose.
  - It reuses modcheck, the levels and `proof_all`.
- **Cons.**
  - Declaring input globs per check is real work.
  - A wrong glob silently fails to regress. Mitigation: a weekly "full re-verify" sample of 1 random reached rung per
    mod, where any disagreement is a bug in the globs.
- **Cost.** ~6 h: schema, `ratchet advance|check|board` CLI, glob declarations for R0–R3.
- **Test.** Replay 10-05 → 10-11 GSS history. The ladder must show GSS reaching R3 on 10-05, dropping on the 10-10
  edits that failed 15 rows, and re-reaching R3 on 10-10. Touching a GSS texture must drop R2/R4 only.

### R2. One inbox for the owner: decisions only, each with a purpose and a default

- **What.** Everything that needs you becomes one record in `infrastructure/state/inbox/` (ledger-backed; builds on
  `rimflow file --for OWNER` and `pulse hand`). Each record has:
  - `you_are_judging` (one sentence)
  - `default_if_skipped` and `reversible: yes/no`
  - `est_seconds`
  - `evidence` (a native path or URL)
  - `rung_it_unblocks`
  - `expires`

  `inbox serve --minutes 10` packs the highest-unblocking items into a sitting that fits the time, so it fits
  morning, lunch or evening.
- **Review by exception.** A *reversible* item you skip takes its default at `expires` and is recorded as
  `--per-ruling INBOX_DEFAULTS` (needs your ruling, §F Q2). Irreversible items never default.
- **Evidence.** F3: 155 owner-input alarms with 28.4 h waiting. 246 question cards. You asked "what am I reviewing FOR".
- **Pros.**
  - Your time is spent only where it unblocks a rung.
  - Silence stops being a blocker.
  - Every ask states its purpose.
- **Cons.**
  - A wrong default ships silently. Mitigation: defaults are visible on the board and reversible by definition.
  - It needs discipline that nothing bypasses the inbox. Cards in-session remain allowed when you're present.
- **Cost.** ~4 h.
- **Test.**
  - Over 2 days, ≥80% of inbox items are resolved inside their sitting.
  - Median `est_seconds` error is under 2×.
  - Zero items reach you without `you_are_judging`.

### R3. Sheet contract: purpose, needs-you count, provenance, fresh inputs, coverage

Four mandatory changes to `art_sheet.py`, the general review-sheet template, and `serve_gated.py` (the server gate):
- **(a) Header.** "You are judging: … · **N of M rows need you** · if you skip: …". The server refuses without it.
- **(b) Rows are classed** NEEDS_YOU / EVIDENCE / FYI.
  - The default view shows NEEDS_YOU only.
  - Completeness rows live behind a toggle.
  - The 151-row sheet becomes 4 rows plus "147 checked by machine (show)".
- **(c) Provenance per row.**
  - The pre-fill lives in `prefill`.
  - `decision` is written **only** by your click, with `by: owner, at`.
  - The sidecar flips `reviewStatus.state` to `ruled` when every NEEDS_YOU row has an owner decision.
  - `review_status.py` refuses any `decision` without `by`.
- **(d) Inputs.**
  - The builder refuses a def capture whose `modlist_fingerprint` does not match the live set. The comparison already
    exists in the deploy skill; this applies it.
  - For art sheets it diffs rows against the mod's shipped `Textures/` and refuses if the coverage is < 100% without
    a stated exclusion.

Also:
- **One builder.** Retire the 23 `src/` and 12 `Transient/` hand-rolled builders behind `art_sheet.py`, `nonart_sheet.py`
  and the generic template. New sheets go through one of those or are refused by the serve gate.
- **Evidence.** F3, F4. All 7 root causes in `ev_art_review.md`.
- **Pros.**
  - It removes today's incident class at the tool, not by memory.
  - Pre-fill can no longer impersonate you.
- **Cons.**
  - 35 builders take time to retire. Retire on next use, not by sweep.
  - Existing decisions files need migrating. A script moves `decision==prefill && no at` → `prefill`.
- **Cost.** ~5 h plus migration.
- **Test.** Re-run today's GSS case from its 10-11 inputs. The builder must:
  1. Refuse the 10-04 dump.
  2. With a fresh dump, show 4 NEEDS_YOU rows.
  3. Show `state: ruled` after your 4 clicks.
  4. Report coverage 120/120 of code-drawn textures.

### R4. Machine pre-review before any human look

- **What.** Run the built artboard pipeline live (`rich_screenshot_art_prereview.md`, `gss_looks_prereview.md`): one
  staged grid capture per biome, crops, Tier A pixel checks, one batched vision read, then
  `autofix.py` → STAGING (re-stage) / ART_FIX (back to artpipe) / JUDGEMENT (inbox). Only JUDGEMENT reaches you.
- **Audit.** 5% of auto-resolved rows are sampled into your inbox, labelled as an audit, to measure machine error.
- **Evidence.** F3, F7: built, 26/26 selftests, 0 live runs.
- **Pros.**
  - It cuts rows to you by an order of magnitude.
  - Unattended overnight live driving is allowed.
- **Cons.**
  - Vision reads have false negatives. The audit sample measures them.
  - The first live run will find harness bugs: budget 1 evening.
- **Cost.** ~3 h to first live run, then per biome ~20 min of game time.
- **Test.** On GSS (whose 151 rows you have now judged): machine JUDGEMENT ⊇ your 4 clamp rows, and the audit sample
  disagreement is < 10%.

### R5. Validation that pays for itself: cache, cheapest tier first, budget, bisect

1. **Skip identical runs.** A run's identity is `(check, inputs_fingerprint, tier)`. If a PASS exists for that identity,
   the run is skipped and cited. This alone removes the last 3 GSS runs (1,668 s) and the identical 10-10 pair.
2. **Declare the question.** Every run names the rung or item it could change. A run that can change nothing is refused.
3. **Cheapest tier first.** Offline → 13-mod minimal list (22 s load) → quicktest (~90 s) → mod tier → full list
   (13–19 min). A higher tier runs only when the lower one is green.
4. **Budget and early stop.**
   - Each run has a wall-clock budget.
   - At 2× budget it stops and files a harness item.
   - On the first red row in a matrix, it stops the matrix unless `--all`.
5. **Bisect, don't re-run.** On red, re-run only the failing rows at the lowest tier that reproduces them.
6. **Results join** (`NORTHSTAR_RESULTS_JOIN_1`). A finished run writes its rung advance or regression directly, so a
   result nobody joins can't exist.
7. **No-news alarm.** Three consecutive runs that change no rung or item post a RimPulse line: "this check is
   re-confirming; stop or change the question".

- **Evidence.** F5.
- **Pros.** Wall-clock goes to discovery.
- **Cons.**
  - The cache trusts the fingerprint. A fingerprint that misses an input gives a false skip. Mitigation: the same
    weekly random re-verify as R1.
- **Cost.** ~4 h (the run-identity and vacuity modules already exist in `modcheck/`).
- **Test.** Over the burst:
  - runs per rung-change ≤ 3 (today ≈ 16)
  - bridge-hours per rung-change falls by ≥ 50% against the 30-day baseline.

### R6. Scoped invalidation and review-the-diff

- **What.**
  - Clean marks and rung evidence bind to the **declared inputs**, not the whole file or mod.
  - Code review marks clean **a diff whose parent was clean** ("review the change"). A file edited after being reviewed
    needs only its diff reviewed.
  - The review debt metric counts reachable, shipped files only. `ORPHANED` and unreachable files leave the
    denominator (CLAUDE.md: check reachability first).
- **Evidence.** F6: debt went from 100 to 4,265 while 356 marks landed in a day.
- **Pros.** Converges.
- **Cons.**
  - Diff review can miss cross-file effects. Mitigation: R6 rung still needs one full-file pass per mod.
- **Cost.** ~3 h.
- **Test.** Debt on the burst's target biomes falls monotonically day over day.

### R7. A convergence budget: finish before you start

- **What.** For any mod not yet at R3, new *feature* items for that mod go to a parked `later` lane. Bugs and rung work
  are exempt.
- Equivalently, the queue offers rung-advancing work first (`rimflow next` orders by "rungs unblocked per hour").
- This is not a WIP cap on loops, which you rejected for Lodestar (D24). It is a priority rule on what gets offered.
- **Evidence.** F1: inflow 1,882 vs end 1,172. 850 open.
- **Pros.** Turns production into convergence without banning anything.
- **Cons.**
  - It slows new mechanics.
  - You may want a specific feature now. Your word always overrides.
- **Cost.** ~1 h (an ordering key in `next`).
- **Test.** Open items per biome fall over the burst, and the share of agent hours on rung work is ≥ 60%.
- **His call:** §F Q3.

### R8. One board: what advanced, what regressed, what needs you

- **What.** A biomes × rungs grid. Each cell shows its rung's date and evidence link, with a red mark on any rung lost
  in the last 24 h. Above it: "advanced today / regressed today / needs you (N items, ~M min)".
- It is rendered into the existing hub artifact
  (`https://claude.ai/code/artifact/ec893765-f01c-4cd8-a0b2-58e5b0bf2257`) as a new tab.
- RimPulse's twice-daily digest (`rm-pulse-digest`) posts the three lines.
- Telemetry (just built) feeds a run-cost panel: minutes of game time per rung advanced.
- **Evidence.**
  - F1/F9: no single per-biome view exists.
  - modcheck status is mostly "RED (last run failed)" with no per-component record for 70 of 73.
- **Pros.**
  - Transparent.
  - You can check progress from the phone at work.
- **Cons.** Another view to keep current. It must be generated from the ratchet files and never edited.
- **Cost.** ~3 h.
- **Test.** You can answer "which biome moved today and what needs me" in < 1 min from the phone.

### R9. Learning capture that changes behaviour

- **(a) Method yield.** Every finding (a bug that caused a code or art change) records `found_by ∈ {offline lint,
  selftest, quicktest, live proof, artboard, owner look, GPT, agent review}`, plus its cost and its class. A weekly
  table shows which methods find which classes per hour. Validation budget moves toward the methods that find bugs.
  Directly addresses "12 faults, 1 mod bug".
- **(b) Lessons become checks or expire.** A lesson that can be machine-checked becomes a selftest or hook within a
  week, per `debug_process.md` §2. A lesson that cannot is reviewed at the weekly cleaning and either kept with a
  reason or deleted. 214 lesson files exist today, and their consumption is unmeasured.
- **(c) Hypotheses are items.** `rimflow file --kind hypothesis` carries `predicts:` and `falsified_by:`. When the
  check runs, it closes as confirmed or refuted, and refuted ones are kept (debug_process already asks for
  "informative false theories").
- **(d) Prior-art line before filing a build.** `rimflow file --kind build` requires `prior_art:` (the result of a
  search over `src/`, design/ and `artpipe_state.py find`). This addresses F7 at the moment of filing.
- **Cost.** ~4 h for all four.
- **Test.** After two weeks the method-yield table exists with ≥ 30 findings, and at least one validation budget was
  moved because of it.

### R10. Claims about existence carry an id

- **What.** Any statement "X exists / was regenerated / is deployed" in a handoff, sheet or reply carries the artifact
  id (artpipe job, sha, path + hash). Handoff `--check` refuses a "regenerated" claim without a job id.
- **Evidence.** F4 (the clamp).
- **Cost.** ~1 h.
- **Test.** Zero un-id'd existence claims in handoffs for one week (grep).

### R11. Bookkeeping off the critical path

- **What.**
  - Batch ledger commits: one ledger commit per seat per 10 min, not per event.
  - Lodestar heartbeats go to a non-git log, or are amended into one daily commit.
  - Generated views stay out of git (health JSON already moved on 10-02).
- **Evidence.**
  - F2: ledger sync is 20% of commits.
  - Lodestar is 57% mechanical, with 1,110 heartbeat commits in 45 d.
- **Pros.**
  - Less churn.
  - Faster git.
  - History becomes readable.
- **Cons.**
  - A batched ledger widens the crash window to 10 min. That is acceptable: it is append-only, and the next
    `rimflow` write re-commits.
- **Cost.** ~2 h (Lodestar change is his repo's own loop).
- **Test.** Commits per day down ≥ 30% with rung advances unchanged or up.

### R12. Lanes that cannot collide (used by the burst; durable afterwards)

- **What.** A *lane* is one agent tree with:
  - its own borrowed clone: `scratch_clone.py clone "<lane>" --sparse <its paths>`, ~0.01 s and ~110 KB.
  - a declared path set: its mod folder, its `ratchet/<Mod>.json`, and `Transient/lanes/<lane>/`.
  - landing only via `LAND_REPO=<clone> land.sh -m "…" <paths>`. Plumbing on fresh origin/main; it never touches a
    seat index.
- Lanes never write: the ledger (they return results to the orchestrator seat, which writes rimflow), shared `Utils/`
  (only the infrastructure lane does), or tracked output outside their dir.
- A lane that needs a path outside its set **reports** it and does not edit.
- A reaper deletes a lane clone only if it has 0 unpushed and 0 untracked files.
- **Evidence.** F8, and the "safe N-lane" constraints (`ev_git.md` end). It respects the worktree ban: these are clones,
  not worktrees.
- **Pros.** No shared index. Disjoint paths. One landing path that already exists.
- **Cons.**
  - Shared-tool changes serialize through one lane.
  - Clones need disk (sparse keeps it small).
- **Cost.** ~2 h: `lane.py open|land|close` wrapping the existing tools, plus the reaper.
- **Test.** Burst ends with 0 index.lock incidents, 0 publish refusals from lane clones, and 0 untracked strays
  (`lane.py audit`).

### R13. Measures that say whether the workflow works

These are tracked on the board daily, against their 30-day baselines:

| measure | baseline (30 d) | burst target |
|---|---|---|
| precision of what reaches you (rows needing you ÷ rows served) | 4/151 today; ~0.3 overall | ≥ 0.8 |
| your minutes per rung advanced | unmeasured (start now) | falling |
| runs per rung or status change | ~16 (6% modcheck) | ≤ 3 |
| bridge-hours per rung change | 189 h / ~15 changes | −50% |
| open items per target biome | see `ev_biomes.md` | falling daily |
| regressions caught by the ratchet vs found by you | n/a | ratchet > you |

---

## C. Part 2 — the token burst, Sun 2026-10-11 night → Wed 2026-10-14 16:00 PDT (~70 h)

### Budget reality

- **The account.** A $200/mo Max plan is metered by rolling 5-hour usage windows and a weekly cap, not by dollars.
  Neither number is published in a form I can measure from here, so the plan is **throttled by observation**. At each
  of your check-ins the orchestrator reads `/usage` and reports `% of weekly used` against `% of burst elapsed`.
  - Over by > 15 points: drop one biome lane.
  - Under by > 15 points: add one.
- **Measured unit cost tonight.** A sonnet evidence agent spent 84k–137k tokens in 1.5–7 min. An opus-led design or
  build agent with helpers is roughly 3–5× that per hour of work. Sizing assumes ~6–9 concurrent agents at peak and
  ~3–4 overnight.
- **Why the burst is rate-limited.** It is limited by **convergence capacity** (one live game, your review windows),
  not tokens. That is why it spends tokens on offline rungs (R0–R2) and machine pre-review (R4), which need neither
  the game nor you.

### Lanes

| lane | agents | owns (paths) | delivers |
|---|---|---|---|
| **INFRA** (starts first) | 1 opus lead + 2 sonnet | `src/RimMandrake/Utils/{ratchet,inbox,lane}*`, sheet tools, `infrastructure/state/ratchet/`, hub tab | R1 ladder CLI + R3 sheet contract + R2 inbox + R12 lane tool + R5 cache/skip + results join, by **Mon 12:00**; R8 board by Mon evening |
| **BIOME-1..4** | 1 opus lead + ≤2 sonnet each | one biome's `src/.../<Mod>/`, `ratchet/<Mod>.json`, `Transient/lanes/<lane>/` | climb R0→R2 offline (close UNCOVERED lines, art coverage manifest + Tier A, selftests, diff-review of its C#); hand R3 runs to LIVE; prep R4 grid spec |
| **LIVE** (single driver, holds the bridge) | 1 sonnet runner + 1 opus triage on red | the bridge, `Transient/lanes/live/` | serial run queue: cheapest tier first, R5 rules (cache, budget, bisect); overnight R4 artboard captures for every biome at R2; full-list soak for R6 candidates |
| **LEARN** (low priority, troughs) | 1 sonnet | `design/RimMandrake/method_yield/`, Lodestar kit draft | backfill method-yield table from 30 d of verify and finding events; draft the generalization kit (§D) as a template |
| **TRIAGE** (Sunday night only) | 2 sonnet | ledger via seat | stale-drop sweep of the 850 open items with one probe each (CHARTER stale default) so the queue the lanes read is true |

**Biome order** (smallest measured gap first, from `ev_biomes.md`), pending your Q4:
1. **NightsideIce** (8 files, 1 item)
2. **TheSump**
3. **TheRot**
4. **DivingInteraction** (re-run only)
5. **LongShade**
6. **Pyrelands** (only VALIDATED north star)
7. **Webwork**
8. **TheForge**

A lane that reaches R3 takes the next biome. Big-gap biomes (Stillsand, Scarlands, TerminalBiomes) wait.

**Git safety in one paragraph.**
- Every lane works in its own borrowed sparse clone (R12) and lands only its declared paths with `land.sh`.
- The orchestrator seat (FOUNDRY, with BENCH for you) alone writes rimflow, from lane reports.
- INFRA alone touches shared `Utils/`. Biome lanes that need a tool change file a request to INFRA.
- No worktrees, stash, `reset --hard` or force. Conflicts are reported, never cleared.
- The two seat clones keep working as today. Lanes never land into them, only onto origin.

### Your windows (capped)

| when | length | what you get |
|---|---|---|
| **Sun night** (now) | 5 min | the §F cards: rung definitions, defaults policy, convergence budget, biome order, burst cap |
| **Mon morning** | 10 min | inbox: ≤ 8 items, e.g. confirm R0–R2 checks on NightsideIce look right; 1 GSS audit sample |
| **Mon lunch** | 10 min | inbox: first R4 JUDGEMENT rows from overnight-1 capture, or defaults apply |
| **Mon evening** | 60–90 min | two biome sittings (R5), ~20 min each, in game from a saved review map (`Save user review options as save games`); board walk-through 10 min |
| **Tue morning / lunch** | 10 + 10 | inbox |
| **Tue evening** | 60–90 min | 2–3 biome sittings; burst mid-course correction |
| **Wed morning / lunch** | 10 + 10 | last inbox; final rungs |
| **Wed 16:00** | — | board snapshot + retro (what the method-yield table says) |

**Total ask:** ~4.5 h over 3 days, every minute pre-sized by `inbox serve`.

### Overnight (unattended live game; allowed, full lists included)

**Sun → Mon:**
- LIVE runs the R3 queue for whatever reached R2 (likely NightsideIce, TheSump, DivingInteraction) on minimal tiers.
- Then the first live artboard capture on GSS. This doubles as the R4 calibration against your 4 known rows.

**Mon → Tue and Tue → Wed:**
- R3 for the next biomes.
- R4 captures for every biome at R2.
- One full-list load + save/load soak for the R6 candidates.

Each night ends with a 3-line RimPulse digest.

### Expected outcome by Wed 16:00 (target, with what would make it miss)

- **Board and inbox live.** Sheet contract enforced. Lane tool proven. Run cache on.
- **6 biomes at R3 or above, 3 at R5.** The likely misses are:
  - the first artboard live run eating Monday evening (harness bugs)
  - full-list loads at 13–19 min each limiting R6 to 1–2 mods
  - your windows slipping. Defaults on reversible items keep that from stalling.
- **Method kit** drafted (§D) and the method-yield table backfilled.
- **Open item count down** by the triage sweep (count reported, not guessed).

### Candidate burst uses, ranked by worth

| rank | use | why worth it | needs you? | needs game? |
|---|---|---|---|---|
| 1 | INFRA: ratchet + sheet contract + inbox + run cache | every later hour is cheaper; removes today's incident class | 5 min (cards) | no |
| 2 | biome lanes R0→R2 on smallest-gap biomes | pure offline convergence, parallel-safe | no | no |
| 3 | live artboard pre-review (R4) for all R2 biomes, overnight | converts your review from 151 rows to the few that need you | via inbox | yes, unattended |
| 4 | R3 proofs through the cache/budget runner | first biome proofs at current hash | no | yes |
| 5 | stale-drop triage of 850 open items | true queue = no rediscovery | no | no |
| 6 | diff-based code review of the target biomes' C# | R6 and debt converge where it matters | no | no |
| 7 | method-yield backfill + generalization kit | the thing you take to work | no | no |
| 8 | GPT red-team of each biome walk (what's untested?) | cheap, finds UNCOVERED we don't know | no | no |
| 9 | retire hand-rolled sheet builders on touch | stops recurrence | no | no |
| 10 | bookkeeping diet (R11) | lower churn | no | no |
| — | **don't**: new art generation without R4 ahead of it; repo-wide code review; new mechanics on biomes below R3; Lodestar sweep "improvement" | each grows review debt or burns wall-clock without moving a rung | | |

---

## D. Part 3 — the method, without RimWorld

**The Ratchet Method** for pipelines that produce, review, learn and evolve toward a goal.

1. **Status is a ladder of evidence, per deliverable.** Each rung names one check, and its output is the only way up.
   Prose never advances status.
2. **Regress only what changed.** Each check declares its inputs. A change re-opens the rungs whose inputs it touched,
   and re-runs the cheapest affected check automatically. Whole-artifact hashes make status decay faster than you can
   restore it.
3. **Never re-run an identical question.** Cache results by (check, input fingerprint, tier). Every run declares which
   status it could change, and a run that can change nothing is not run.
4. **Cheapest instrument first.** Static check → small fixture → realistic fixture → full system. Climb only on green.
   Budget each run. Stop at the first red. Bisect instead of re-running.
5. **Machines pre-review; humans adjudicate.** Machine passes sort findings into auto-fixable, needs-re-run and
   needs-judgement. Only the last reaches a human. Sample the auto-resolved ones to measure machine error.
6. **One human queue, decisions only.** Each item states *what you are judging*, *the default if you skip*, whether it
   is reversible, and an estimated time. The queue packs itself into the human's actual time windows. Reversible items
   default on expiry.
7. **Provenance is a field, not a convention.** A suggestion and a decision are stored in different fields. A decision
   carries who and when. Nothing a machine wrote may look like a human choice.
8. **Inputs and memories are checked at the point of use.** A generator refuses stale inputs, by fingerprint not
   timestamp. A claim that something exists carries its id.
9. **Converge before you expand.** New scope for a deliverable waits until it reaches the "proven" rung. This is a
   priority rule, not a ban.
10. **Measure methods, not just results.** Every finding records which method found it and at what cost. Reallocate
    validation effort to the methods that find things. A check that re-confirms three times in a row raises an alarm.
11. **Hypotheses are tracked objects** with a prediction and a falsifier. Refuted ones are kept: they are the cheapest
    knowledge you own.
12. **Lessons become checks or expire.** A lesson that a machine could check becomes a test. Otherwise it is
    re-justified or deleted on a schedule.
13. **Parallel workers own disjoint paths and land through one door.** Use a private copy each, a declared write set,
    and one landing tool that refuses conflicts rather than resolving them. Shared state is written by one coordinator.
14. **Bookkeeping is off the critical path.** Heartbeats and generated views are not history.
15. **One board answers three questions:** what advanced, what regressed, what needs me.

**What to port first at work:** 1, 3, 6 and 7. They need the least machinery: a status file per deliverable, a result
cache keyed on inputs, and a decisions queue with purpose and default fields.

---

## E. GPT consult

*(filled after the consult; see below)*

---

## F. Owner questions (card-ready, recommended first)

*(filled after the consult)*
