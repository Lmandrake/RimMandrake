# The ratchet workflow and the token burst to Wed 16:00

*Design, BENCH design lead, 2026-10-11 evening (v2, revised after GPT's skeptical review). Answers the owner's two
questions of 2026-10-11 ~17:55 PDT. Status: DRAFT until he rules on §F.*

**Sources.**
- Evidence was measured tonight by seven read-only agents. Each file carries its own commands:
  `design/RimMandrake/ratchet_evidence_2026-10-11/ev_*.md`.
- GPT's review is verbatim in `ratchet_evidence_2026-10-11/gpt_review.md`, with every point dispositioned in §E.

## Executive summary (phone-sized)

1. **We produce faster than we converge.** In 30 days: 8,726 commits, 1,882 items filed, 1,172 ended, 850 open.
   modcheck shows 1 of 73 mods GREEN. Code-review debt went from ~100 to ~4,265 files, partly because the scope widened.
2. **Your review time is unshaped.** 107 sheets served; 18 carry your ruling. Today's GSS sheet had 151 rows and 4
   needed you. Agent pre-fills sit in the same field as your choices, and a sheet's "ruled" flag never flips when you
   click.
3. **Validation mostly re-confirms.** GSS `proof_all` ran 15 times (2.4 h), and the last 3 were identical.
   modcheck runs changed a mod's status ~6% of the time.
4. **The parts mostly exist; nobody has closed one full loop with them.** rimflow levels, modcheck, artboard
   pre-review (built, never run live), RimPulse and telemetry are all there.
5. **GPT's sharpest objection, accepted:** *"the plan responds to failed tool adoption by building another control
   plane before proving one complete convergence cycle."* So the burst starts with **one pilot**: one biome taken
   end to end (offline → live proof → your sitting). Only then does it fan out.
6. **The ratchet, revised:**
   - What only rises is the **last accepted version** of each biome: frozen and certified.
   - The **current candidate** is shown separately as valid / stale / failed.
   - Status is a set of evidence facets: offline, behaviour, art coverage, your acceptance, compatibility. It is not
     one ladder.
7. **Your queue:** at most 3 decisions per 10-minute window. Each one says *what you're judging* and *what happens if
   you skip*. Skipping keeps the accepted state; it never ships anything.
8. **Burst plan:**
   - Sun night: sheet and provenance fixes plus the pilot.
   - Mon noon: gate. If the pilot cycle works, add biome writers.
   - Every lane gets its own clone, and one integrator lands everything.
   - One live-game runner owns the game outright, overnight included.
9. **Target:**
   - Base: 2 biomes proven at current build and 1 accepted by you.
   - Stretch: 6 proven and 3 accepted.
   - The portable method is written from what the pilot actually showed.
10. **5 decisions for you in §F.** Recommended: pilot Pyrelands · skip = keep accepted state · no new features on
    pilot biomes during the burst · pace to ~90% of weekly allowance · status summary as text in RimPulse.

---

## A. Diagnosis — the failure modes, measured

Caveats GPT raised (§E 5–6) are folded in. These numbers show dysfunction more firmly than they show its causes.

| # | failure mode | evidence (with its limits) |
|---|---|---|
| F1 | **Inflow beats convergence** | 30 d: 1,882 filed vs 1,102 closed + 41 dropped + 29 superseded. Open: 850 by the ledger, 469 by item prose files; the gap is unreconciled (`ev_git_ledger.md` §2). Review debt (dirty + never-entered): ~100 on 09-25 → ~4,265 now. This is partly scope growth (FlowWorks/GSS code) and partly hash decay (`ev_slowloops.md` §2). modcheck: 1 GREEN of 73 by `modcheck status`; 61 RED by snapshot. |
| F2 | **Bookkeeping crowds the history** | The top-15 most-churned files (30 d) are all ledger, queue views, health JSON or DLLs. 1,762 of 8,726 subjects are ledger syncs. Lodestar: 57% of commits are mechanical, and the sweep has produced 0 improvements (`ev_lodestar.md`). *Limit:* commit churn is not agent cost. The health timer costs ~1 s/run and stopped committing on 10-02. |
| F3 | **Owner review is unshaped** | 107 sheets served since 09-11; 18 carry `by=owner` (502 rows, ~28/sitting). Today: 151 rows served, 4 needed him. Pre-fill is written into `decision` itself (`{"decision":"A","prefill":"A"}`). `reviewStatus.state` stayed `prefill` after 26 writes including his 4 clicks. There is no purpose field: *"I need to know what I'm reviewing FOR"* (`conversations/2026-10-11-2000-edefebc8.md` ~l.688). Two junk-reskin sheets (517 rows) were never opened. RimPulse: 155 "needs owner input" alarms, 28.4 h cumulative wait in 3 days (`ev_art_review.md`, `ev_review_validation.md`). *Limit:* a missing owner timestamp does not prove he did not decide; snapshots inflate entry counts. |
| F4 | **Inputs and memories trusted without a check** | The sheet builder read a 7-day-old pre-rename `defs.sqlite`. `scale_panel.py:111-112` records the fingerprint and compares nothing. Code-drawn GSS art has no def, so a def-driven sheet cannot see it. "The regenerated clamp" was recalled, not looked up, and no other version exists (`ev_art_review.md` causes 1, 2, 7). |
| F5 | **Validation re-confirms** | GSS `proof_all`: 15 runs, 8,543 s, last 3 identical 105/105, and an identical pair on 10-10 (`ev_slowloops.md` §4). modcheck: ≥235 runs, 15 status changes. One item was verified 13 times. The 10-11 overnight run found 12 faults, 1 of them a mod bug: "mostly ceremony" (`ev_existing_designs.md`). *Limit:* identical PASS output does not prove identical inputs, and regression checks may legitimately re-confirm. No results join exists (`NORTHSTAR_RESULTS_JOIN_1`), so run-to-status attribution is inferred. |
| F6 | **Status decays faster than it is restored** | Clean marks and modcheck GREEN bind to whole-file/whole-mod hashes; any edit zeroes them. 356 clean marks landed on 10-11, and the same pass then fixed 34 dirty files (`df1df9e62a`). |
| F7 | **Rediscovery; built-but-unadopted tools** | "Four of six 'new' mechanisms already existed" (CLAUDE.md, 09-23). *"Each one rediscovered the same things ... three more question cards ... most of the two hours on Leaning Scrub"* (`conversations/2026-10-08-1428-de9591de.md` l.647). Artboard pre-review: 26/26 selftests, 0 live runs. `human_review.py` exists only for GSS. `queue/HUMAN.md` was last edited 08-26 (`ev_existing_designs.md`). |
| F8 | **Parallel writers collide in git** | Worktree week: 132 worktrees, 68 unmerged branches, 268 → 178 commits/day, then the ban. ~8 index.lock incidents; 215 files lost on 09-25; 53 stranded by autostash on 10-10. Today publish was refused over another clone's untracked `Transient/` files. Per-seat ledger shards: 0 conflicts since 10-02 (`ev_git.md`). |
| F9 | **No biome has closed the loop** | 26 biome mods, all with C#, settings and `validation.py`; none has `northstar/proof_all.py`; 24 DRAFT. UNCOVERED walk lines: 1–18 per biome. CLEAN review: 0/28 to 15/32 (`ev_biomes.md`). Pyrelands has the only VALIDATED north star, and its stored run is RED and old. GSS (a conduit mod, not a biome) is the reference: one proof, 0 uncovered, 69/70 CLEAN, its own tier, and a human-look layer apart from the pass bars. |

**One sentence.** The instruments are excellent. What's missing is a loop that turns passing evidence into an accepted
version that cannot be lost, and a filter on what reaches the owner. No biome has yet been carried around that loop
once.

---

## B. Part 1 — the ratchet workflow

Each recommendation: **what** · evidence · pros/cons · cost (agent-hours) · **the test that shows it works** ·
burst status (**NOW** = in the burst, **AFTER PILOT** = only if the pilot shows it's needed, **LATER**).

### R1. Monotonic accepted versions; explicit current-candidate validity — NOW

- **What.** Two things are tracked per biome, in one file per mod:
  `infrastructure/state/ratchet/<Mod>.json`, written by **one writer**, the integrator (§R11).
  - **Accepted version.** This is what rises.
    - It is an immutable *candidate*: published sha, deployed build identity, checker/oracle versions and mod-list
      fingerprint.
    - It records every evidence facet (R2) passed, plus the owner's acceptance.
    - It never goes down. A newer candidate only *replaces* it after earning the same facets.
  - **Current candidate.** valid / stale / failed against each facet. It is shown honestly. Old evidence never
    certifies new edits.
- **Why changed from v1.** GPT §E 2: a "ratchet" whose rungs drop is not monotonic, and refusing legitimate
  regression would make the board lie. History is monotonic; confidence in an edited build is not.
- **Evidence.** F1, F6, F9.
- **Pros.**
  - Progress you can never lose.
  - Truthful about the edited build.
  - Uses existing sha, modcheck and proof outputs.
- **Cons.** Accepted versions must stay deployable. Tag them (`accepted/<Mod>/<n>`) so any can be redeployed.
- **Cost.** ~3 h.
- **Test.** Replay GSS 10-05 → 10-11:
  - accepted version created 10-05
  - candidate failed 10-10 (15 rows)
  - new accepted version on 10-10's green run
  - the 10-05 accepted version never displayed as lost.

### R2. Evidence facets, not one ladder — NOW (coarse), finer AFTER PILOT

- **The facets.** Independent, each a set of executed check IDs with a manifest version. Unexecuted means UNKNOWN,
  never pass.

  | facet | the check(s) | exists today? |
  |---|---|---|
  | offline | `validate_patch.py --live --defs`, mod selftests, deploy dry-run clean | yes, scattered |
  | spec | walk has 0 UNCOVERED `must be true` lines (`modcheck floor`) | yes |
  | behaviour | `proof_all` on the mod's own tier at this candidate | GSS only |
  | art coverage | manifest = every texPath **and** every code-drawn texture shipped, each own-art + Tier A pixel pass; diffed against `Textures/` | Tier A yes; coverage diff no |
  | owner acceptance | his JUDGEMENT rows ruled `by: owner` on this candidate (or a predecessor whose art is byte-identical) | sheets yes; provenance broken |
  | compatibility | full-list load + save/load soak | ad hoc |

- **Prerequisites are explicit, not a ladder.**
  - Behaviour needs offline.
  - Owner acceptance needs art coverage + behaviour, because he shouldn't judge a build that fails its own proof.
  - "Ship-ready" = all six on one candidate.
- **Why changed.** GPT §E 3: the v1 ladder forced art before behaviour and conflated "seen" with "accepted".
- **Cost.** ~2 h on top of R1.
- **Test.** For the pilot biome, the board shows six facets with IDs. A deliberately skipped check shows UNKNOWN, not
  PASS.

### R3. Conservative invalidation first; narrow only where it pays — NOW (coarse)

- **What.** A candidate's evidence identity hashes:
  - the **whole mod root**, including directory membership, so adds and deletes count
  - its shared dependencies (`Utils/` libs it imports, the shared C# core)
  - the checker/oracle code, build config, the mod-list fingerprint, and the relevant fixtures and saves

  Any change invalidates broadly. Narrower dependency sets are derived later from manifests, build deps and
  observed reads, and only where measured re-run savings justify them.
- **Why changed.** GPT §E 4/16: hand-written input globs are unsound and would rot. A false "still valid" is worse than
  a re-run.
- **Cost.** ~2 h. modcheck's `run_identity` module exists.
- **Test.** Touching any file in the mod, a shared lib it imports, or the checker marks the candidate stale. Touching
  an unrelated mod does not.

### R4. Sheet contract: purpose, needs-you rows, provenance, fresh inputs, coverage — NOW (pilot-critical)

Applied in `art_sheet.py`, the general review-sheet template and `serve_gated.py`.

- **(a) Header the server refuses to serve without:** "You are judging: … · **N of M rows need you** · if you skip:
  the accepted art stays".
- **(b) Row classes.** Rows are classed NEEDS_YOU / EVIDENCE / FYI, and the default view is NEEDS_YOU only. Today's
  sheet becomes 4 rows plus "147 checked by machine (show)".
- **(c) Provenance per row.**
  - `prefill` is a separate field.
  - `decision` is written only by his click, with `by: owner, at`.
  - The sidecar flips `reviewStatus.state` to `ruled` when every NEEDS_YOU row has an owner decision.
  - Three distinct outcomes are stored: `owner-approved` / `policy-defaulted` / `deferred`. A default never counts as
    owner acceptance (GPT §E 19).
- **(d) Inputs.**
  - The builder refuses a def capture whose `modlist_fingerprint` ≠ live.
  - Art sheets diff rows against shipped `Textures/` and refuse < 100% coverage without a stated exclusion.

Scope and test:
- **Scope cut (GPT §E 27).** No global migration of the 195 decisions files and no sweep retiring the 35 builders.
  Fix the shared tools; migrate a sheet only when it is next served.
- **Evidence.** F3, F4; all 7 root causes in `ev_art_review.md`.
- **Cost.** ~4 h.
- **Test.** Re-run today's GSS case:
  1. The builder refuses the 10-04 dump.
  2. With a fresh dump it shows 4 NEEDS_YOU rows.
  3. State reads `ruled` after his 4 clicks.
  4. It reports 120/120 code-drawn textures covered.

### R5. The owner queue, bounded by minutes and arrivals — NOW (minimal: rimflow `--for OWNER` + fields, no new CLI)

- **Each item carries:**
  - `you_are_judging`
  - `if_skipped` (default: *keep the accepted state; the item stays pending*)
  - `est_minutes`
  - `evidence` (native path)
  - `unblocks` (which facet on which candidate)
- **Bounds (GPT §E 18):**
  - ≤ 3 decisions per 10-minute window, with 2 minutes reserved for context and saving.
  - ≤ 2 prepared biome review packs waiting at once.
  - If the backlog exceeds the next day's review budget, **stop producing review-dependent work**: the lanes switch
    to offline facets.
  - Evening sittings price in setup (load the review save) and follow-up repairs.
  - Estimates are calibrated from his first two sittings.
- **Auto-accept.** Only for categories he explicitly pre-authorizes (§F Q2), visible on the summary and cheap to roll
  back.
- **Why changed.** GPT §E 10/19: silence-as-approval hides the bottleneck. In v1 a skip shipped the default; now a skip
  keeps what's accepted.
- **Evidence.** F3.
- **Cost.** ~1.5 h: fields on `rimflow file --for OWNER` plus a `next --seat OWNER --minutes 10` packing order. A full
  inbox CLI is **LATER**.
- **Test.**
  - Over the burst, every item reaching him has `you_are_judging`.
  - Arrivals never exceed the window cap.
  - Median estimate error < 2× after calibration.

### R6. Machine pre-review as assisted triage — NOW for GSS calibration; per-biome AFTER PILOT

- **What.** Run the built artboard pipeline live (`rich_screenshot_art_prereview.md`):
  1. Grid capture, crops, Tier A pixel checks, one batched vision read.
  2. Its dispositions are **provisional**.
  3. First live run on GSS: he inspects the flagged rows **and** a deliberately varied sample of machine-passes
     (~10, not a 5% sample of 147 ≈ 7).
  4. The automatic fix loop stays **off** until the error rate is known (GPT §E 11/24).
- **This needs the game.** v1 wrongly put it among "needs neither game nor you". It is a LIVE-lane job.
- **Evidence.** F3, F7.
- **Cost.** ~3 h to first live run. Budget one evening for harness bugs.
- **Test.** On GSS it flags the 4 clamp rows (a regression test, not calibration). His sample disagreement is recorded
  as the first error estimate.

### R7. Run only well-defined questions: cache, cheapest tier first, budget, bisect — NOW

- **What.**
  - **Cache key.** `(check id + checker/oracle version, candidate identity per R3, tier, environment)`.
    - Deterministic offline PASS is reused.
    - Live evidence has an explicit policy for seeds, repeats and environment changes, so a repeat for flakiness is
      allowed when declared.
  - **Every run declares** the facet and candidate it serves. A run serving nothing is refused.
  - **Cheapest tier first.** Offline → 13-mod minimal list (22 s load) → quicktest (~90 s) → mod tier → full list
    (13–19 min).
  - **Failures.**
    - Fail fast on a prerequisite failure.
    - Keep running independent cheap checks when that saves another load.
    - Bisect failing rows at the lowest reproducing tier.
    - A missing or malformed result file is a failure even if the process exits 0.
  - **Results join** (`NORTHSTAR_RESULTS_JOIN_1`). The result is written straight to the candidate's facet.
- **Evidence.** F5.
- **Cost.** ~3 h (run-identity and vacuity modules exist in `modcheck/`).
- **Test.** During the burst, no live run executes for a cache hit unless it declares a repeat policy. Live minutes
  per facet established are logged by telemetry.

### R8. Converge before expanding — NOW for burst biomes (his call, Q3)

- **What.** While a biome is in the burst, new *feature* items for it are parked. Bugs and facet work are exempt.
  `rimflow next` offers facet-advancing work first. This is a priority rule, not the loop WIP cap he rejected (D24).
- **Evidence.** F1.
- **Cost.** ~1 h.
- **Test.** Open items on pilot biomes fall over the burst.

### R9. Learning capture that changes behaviour — method yield NOW (fields only); backfill and expiry LATER

- **(a) Found-by.** Every finding (a bug that caused a change) records `found_by` (offline lint / selftest / quicktest
  / live proof / artboard / owner look / GPT / agent review), its class and its cost. It is recorded forward from
  tonight. The 30-day backfill is **LATER** (GPT §E 27).
- **(b) Hypotheses** are items with `predicts:` / `falsified_by:` and outcome **supported / contradicted /
  inconclusive under stated conditions**, separating harness failure from hypothesis failure (GPT §E 25).
- **(c) A prior-art line** (`prior_art:` = the search over `src/`, design/ and `artpipe_state.py find`) is required on
  `rimflow file --kind build`. Cheap, and it hits F7 at the moment of filing.
- **LATER:** lesson expiry (lessons → checks or deletion); existence-claim id policing (handoff `--check` refuses
  "regenerated" without a job id).
- **Cost.** ~1.5 h now.
- **Test.** By Wed, ≥ 10 findings carry `found_by`. The pilot retro uses them.

### R10. One status summary — NOW as generated text; hub tab LATER

- **What.** A generated three-line summary posted by RimPulse's digest and at each check-in:
  - **advanced:** accepted versions and facets gained
  - **regressed:** candidates gone stale or failed
  - **needs you:** N items, ~M min
  - plus a per-biome facet table in `Transient/ratchet_status.md`.

  The hub-artifact tab is **LATER** (GPT §E 27).
- **Measures** (replacing v1's runs-per-rung targets, which GPT showed can be gamed, §E 26):
  - accepted candidates
  - owner minutes including rework
  - end-to-end elapsed time per accepted version
  - escaped defects (found by him after acceptance)
  - live minutes per facet, kept as a diagnostic only
- **Cost.** ~1 h.
- **Test.** He can answer "what moved and what needs me" from the phone in < 1 min.

### R11. Private clones plus one integrator — NOW

- **What.** Each concurrent *writer* gets its own borrowed sparse clone (`scratch_clone.py`). Writing helpers inside a
  clone run serially. A writer submits a commit plus `{base sha, owned paths, evidence}`.
- **The integrator** (the orchestrator seat, FOUNDRY) does all of the following:
  - lands submissions one at a time against fresh origin/main (`LAND_REPO=… land.sh`)
  - refuses overlapping paths
  - proves publication with `merge-base --is-ancestor`
  - runs the offline facet on the integrated result
  - is the only writer of rimflow and `ratchet/*.json`

  Before going above 2 writers, two lanes are exercised with simultaneous submissions and a stale hook (GPT §E 20).
- **The live runner exclusively owns the game environment** (GPT §E 21): deploys, mod lists, settings, launches, def
  captures, review saves. Jobs name immutable candidates, and nobody deploys under a running proof.
- **Evidence.** F8; the constraints at the end of `ev_git.md`. Respects the worktree ban: these are clones.
- **Cost.** ~2 h. A wrapper/reaper tool is **LATER**; the reaper rule "0 unpushed, 0 untracked" is enforced by hand.
- **Test.** The burst ends with 0 index.lock incidents in lane clones, 0 lost commits, 0 untracked strays, and every
  landed sha an ancestor of origin/main.

### R12. Bookkeeping off the critical path — LATER

- **What.**
  - Batch ledger commits per seat per ~10 min.
  - Lodestar heartbeats go out of git.
- **Evidence.** F2.
- **Deferred because** it doesn't move a biome this week, and GPT §E 5 is right that churn ≠ cost.

---

## C. Part 2 — the token burst, Sun 2026-10-11 ~18:30 → Wed 2026-10-14 16:00 PDT

### Capacity, honestly

- **How the allowance is metered.** The Max plan is metered by rolling usage windows and a weekly cap. Remaining
  allowance is read from `/usage` at each check-in; it is not predicted here.
- **Measured tonight.** Sonnet evidence agents spent 84k–137k tokens each in 1.5–7 min.
- **What really binds.** Elapsed time is not compute. The real limits are **one game, one owner, one integrator**
  (GPT §E 7/22).
- **Pacing (his call, Q4).** Aim to end near the cap, not over it.
  - At each check-in, compare *% allowance used* with *% burst elapsed*.
  - Under by > 15 points → add a writer **only if** the integrator and game queue have slack; otherwise put the
    surplus on read-only work (below).
  - Over by > 15 points → drop a writer.
- **Read-only surplus work** consumes tokens without git or review load: GPT red-teams of walks, coverage audits,
  method-yield backfill, Lodestar kit drafting. It is the release valve.

### Stages and gates

| stage | when | writers | what |
|---|---|---|---|
| **S0** | Sun ~18:30 → Mon 08:00 | INFRA (1 opus + ≤2 read-only sonnet), PILOT (1 opus), LIVE (1 sonnet runner) | INFRA: R4 sheet contract, R1–R3 coarse candidate/facet file, R7 cache + results join, R5 owner fields, R10 text summary. PILOT: offline + spec facets on the pilot biome. LIVE overnight: GSS artboard first live run (R6 calibration), then the pilot's behaviour proof as soon as offline is green. |
| **Gate 1** | Mon ~12:00 (his lunch) | — | Pass = the pilot has offline + spec + behaviour on one candidate, a prepared review pack, and no bespoke rescue was needed. Fail → S1 is *fix the loop*, not fan out. |
| **S1** | Mon 12:00 → Tue 08:00 | + BIOME-2 (1 opus). + BIOME-3 only after a two-lane simultaneous-landing test passes | Same loop on the next biomes. INFRA narrows invalidation only where re-runs measurably hurt. Mon evening: his pilot sitting → **first accepted version**. |
| **Gate 2** | Tue ~12:00 | — | Pass = one accepted version, one more biome at behaviour, owner queue within its cap, 0 git incidents → allow up to 4 biome writers. |
| **S2** | Tue 12:00 → Wed 14:00 | ≤ 4 biome writers + INFRA + LIVE | Fan out. Tue evening: 1–2 sittings. |
| **Close** | Wed 14:00 → 16:00 | — | Freeze, final summary, pilot retro, method write-up (§D gets updated from what actually happened). |

### Who does what

| lane | agents | owns (paths) |
|---|---|---|
| INFRA | 1 opus writer + read-only sonnet helpers | sheet tools, `modcheck/` run identity, `infrastructure/state/ratchet/` schema (the integrator writes the data), rimflow field additions |
| PILOT / BIOME-n | 1 opus writer each, serial writing helpers, read-only sonnet helpers | that biome's `src/.../<Mod>/`, `Transient/lanes/<lane>/` |
| LIVE | 1 sonnet runner + opus on red | the whole game environment, `Transient/lanes/live/` |
| Integrator | the FOUNDRY seat | landing, rimflow, `ratchet/*.json` |
| Read-only surplus | sonnet, as allowance permits | no writes outside `Transient/lanes/ro/` |

Peak concurrency is therefore ~6 writers-or-runners plus read-only helpers. The v1 table permitted ~18, which GPT
caught (§E 7).

### Pilot choice (Q1 decides)

| biome | why it's the recommended pilot | why not |
|---|---|---|
| **Pyrelands** (recommended) | Only VALIDATED north star, so his spec is already real. `PYRELANDS_SHIP_READINESS_1` already defines a ship rung. 8 must-be-true lines, 0 uncovered. Art 15/24 own. | 11 open items, 12/42 CLEAN; its stored run is RED and old |
| NightsideIce | smallest: 8 files, 1 item, 5/5 art | thin spec (no plan, 2 uncovered); small paperwork ≠ small difficulty (GPT §E 9) |
| TheSump / TheRot | small item counts, much of the art own | RED, 0 CLEAN, specs unvalidated |

After the pilot, the order is chosen by **his** priority (Q1) and then by measured gap. DivingInteraction is not
"re-run only": it spans 6 biomes (GPT §E 9).

### His windows (capped)

| when | length | what he gets |
|---|---|---|
| Sun night | 5 min | §F cards |
| Mon morning | 10 min | ≤ 3 items: GSS artboard results, flagged rows + ~10 machine-passes to sample |
| Mon lunch | 10 min | Gate 1 summary (3 lines) + ≤ 3 items |
| Mon evening | 60–90 min | pilot sitting in game from a saved review map, then accept or reject the candidate. ~10 min board walk |
| Tue morning / lunch | 10 + 10 | ≤ 3 items each; Gate 2 at lunch |
| Tue evening | 60–90 min | ≤ 2 prepared biome packs |
| Wed morning / lunch | 10 + 10 | last items |
| Wed 16:00 | — | summary + retro |

### Overnight (unattended; full lists allowed)

- **Sun→Mon:**
  - GSS artboard live capture (R6)
  - the pilot's behaviour proof on its own tier
  - one full-list load of the pilot candidate if time remains (compatibility facet)
- **Mon→Tue, Tue→Wed:**
  - behaviour proofs for the biomes whose offline facet went green that day
  - artboard captures for those that reached art coverage
  - one compatibility soak per night

Every night ends with the three-line summary.

### Expected outcome by Wed 16:00

- **Base** (expected if Gate 1 passes):
  - sheet contract enforced
  - candidate/facet files and the run cache live
  - **2 biomes with behaviour proven on a current candidate, 1 accepted by him**
  - GSS artboard error estimate in hand
  - ≥ 10 `found_by` findings
  - the method rewritten from evidence
- **Stretch:** 6 proven, 3 accepted.
- **If Gate 1 fails:** the burst's output is a working loop and a precise list of what broke it. That is still the
  thing he asked for in Q1.

### Candidate burst uses, ranked by worth

| rank | use | needs him? | needs game? | stage |
|---|---|---|---|---|
| 1 | Sheet contract + provenance fix (R4) | no | no | S0 |
| 2 | Pilot loop end to end (R1–R3, R7 coarse) | Mon evening | yes | S0–S1 |
| 3 | GSS artboard first live run (R6 calibration) | 10 min sample | yes | S0 night |
| 4 | Owner fields + window cap (R5) and text summary (R10) | no | no | S0 |
| 5 | Further biomes through the proven loop | Tue evening | yes | S1–S2 |
| 6 | Read-only surplus: GPT red-team of every biome walk ("what is untested?") → UNCOVERED candidates | no | no | any |
| 7 | Read-only surplus: art-coverage audit of all 26 biomes against shipped `Textures/` and code-drawn art | no | no | any |
| 8 | Read-only surplus: method-yield backfill from 30 d of verify/finding events | no | no | any |
| 9 | Diff-based C# review of the burst biomes only | no | no | S1–S2 |
| — | **don't:** new art without a pre-review path; repo-wide review; new mechanics on burst biomes; an 850-item drop sweep mid-burst (it can hide unfinished work, GPT §E 13); new dashboards | | | |

---

## D. Part 3 — the method, without RimWorld

**The Ratchet Method** for pipelines that produce, review, learn and evolve toward a goal. It is written to be
revised: after Wednesday, rewrite this section from the pilot's retro, keeping only what the pilot showed works
(GPT §E 27).

1. **What only rises is an accepted version.** Freeze each deliverable's accepted candidate (code + data + config +
   evaluator versions). Show the current candidate's validity separately. Never let old evidence certify new work.
2. **Status is evidence facets with explicit prerequisites.** Each facet is a set of executed check IDs at a manifest
   version. Unexecuted means unknown.
3. **Invalidate conservatively; narrow by measurement.** Hash the whole deliverable plus its shared dependencies and
   the evaluator. Narrow dependency sets only where re-runs measurably cost.
4. **Never re-ask an identical question.** Cache by (check + evaluator version, candidate identity, tier,
   environment). Every run names the facet it serves. A missing or malformed result is a failure.
5. **Cheapest instrument first, budgeted.** Static → small fixture → realistic → full system. Fail fast on
   prerequisites. Bisect rather than re-run.
6. **Machines triage; humans adjudicate.** Machine dispositions are provisional until their error rate is measured on
   a varied human-checked sample. Auto-fix loops wait for that number.
7. **One human queue, bounded by minutes and arrivals.** Each item states what is being judged, what happens on skip,
   reversibility and time. Skip preserves the accepted state. When the backlog exceeds tomorrow's review budget, stop
   producing review-dependent work.
8. **Provenance is a field.** Suggestion, policy default, deferral and human decision are four different stored values.
9. **Check inputs and memories at the point of use.** Generators refuse stale inputs by fingerprint. "It exists" claims
   carry an id.
10. **Prove one full loop before fanning out.** Then add parallel workers one gate at a time.
11. **Parallel workers: private copies, declared write sets, one integrator.** The integrator lands serially, refuses
    overlaps, verifies publication and re-checks the integrated result. Exclusive resources (a lab instrument, a GPU
    box, a live system) have exactly one owner.
12. **Hypotheses are tracked objects.** Each has a prediction, a falsifier, and an outcome: supported / contradicted /
    inconclusive *under stated conditions*. Harness failure is kept distinct from hypothesis failure. Version
    algorithm, data, baseline, seeds and protocol together. Separate exploratory tuning from held-out confirmation.
    Keep negative results with their scope.
13. **Measure methods and delivery, not activity.** Track which method found which defect at what cost; accepted
    versions; human minutes including rework; escaped defects. Activity counts (runs, rungs, commits) are diagnostics,
    never targets.
14. **Converge before expanding.** New scope for a deliverable waits until it has an accepted version. This is a
    priority rule, not a ban.
15. **Evolving goals get new evidence versions.** When the question changes, start a new manifest version rather than
    forcing ascent on an old ladder.

**Port first at work:** 1, 4, 7 and 8. They need a status file per deliverable, a result cache, and a decisions queue
with purpose/skip/provenance fields.

---

## E. GPT consult — findings and disposition

Consulted 2026-10-11 ~18:00 via `gpt_consult.py` (default model, effort high), with the v1 draft plus five evidence
files. Verbatim answer: `ratchet_evidence_2026-10-11/gpt_review.md`.

**Sharpest objection (§1):** *"the plan responds to failed tool adoption by building another control plane before
proving one complete convergence cycle."* v1 totalled ~41 agent-hours of infrastructure next to six biome
completions. **Accepted.** It is the main change in v2: S0 pilot, gates, and the cuts below.

| # | point (abridged) | disposition |
|---|---|---|
| 1 | Prove one convergence cycle before building a control plane | **Adopted**: pilot + Gate 1/2 (§C) |
| 2 | Rungs that drop aren't monotonic | **Adopted**: accepted versions rise; candidate validity shown separately (R1) |
| 3 | Ladder conflates independent dimensions; "seen" ≠ "accepted" | **Adopted**: facets with explicit prerequisites (R2); owner acceptance is its own facet |
| 4 | Input globs unsound; "texture edit never reopens R3" unsupported | **Adopted**: conservative whole-root + deps invalidation (R3) |
| 5 | Evidence shows dysfunction more than causes; mixed denominators; churn ≠ cost | **Adopted**: caveats in §A; F2 demoted; bookkeeping deferred (R12) |
| 6 | Validation economics overstated; identical PASS ≠ identical inputs | **Adopted**: §A F5 limit; removed the "189 bridge-h / 15 changes" ratio; repeat policy in R7 |
| 7 | 70 h ≠ compute; lane table allowed ~18 agents | **Adopted**: peak ~6 writers/runners; pacing by `/usage`; read-only surplus as release valve |
| 8 | Critical path relies on uncommissioned machinery; R4 needs the game | **Adopted**: artboard moved to LIVE and treated as commissioning; Gate 1 doesn't depend on it |
| 9 | Biome order measures paperwork, not difficulty; DivingInteraction isn't "re-run only" | **Adopted**: pilot chosen for spec quality (Pyrelands, Q1); his priority orders the rest |
| 10 | Silence-as-default hides the bottleneck | **Adopted**: skip keeps accepted state; auto-accept only for pre-authorized categories (R5, Q2) |
| 11 | 4 known rows is a regression test, not calibration; 5% of 147 ≈ 7 | **Adopted**: varied ~10-row sample, provisional dispositions (R6) |
| 12 | Clones remove shared indexes, not coordination; deploys/game are shared | **Adopted**: integrator + exclusive live runner (R11) |
| 13 | Many recommendations create fresh churn; 850-item sweep badly timed | **Adopted**: inbox CLI, reaper, hub tab, lesson expiry, claim policing → LATER; sweep cut from burst |
| 14 | GSS fix then one biome through the full cycle | **Adopted**, with Pyrelands proposed over NightsideIce (spec quality, his Q1) |
| 15 | Immutable accepted candidates; freeze accepted scope in the burst | **Adopted** (R1, R8) |
| 16 | Conservative dependency closure, narrow by measured savings | **Adopted** (R3) |
| 17 | Independent facets; one writer derives status | **Adopted** (R2, R11 integrator writes `ratchet/*.json`) |
| 18 | ≤ 3 decisions / 10 min, ≤ 2 packs waiting, stop review-dependent work on backlog | **Adopted verbatim** (R5) |
| 19 | Store owner-approved / policy-defaulted / deferred separately | **Adopted** (R4c, R5) |
| 20 | Private clones + one integrator; test simultaneous submissions before N > 2 | **Adopted** (R11, S1 condition) |
| 21 | Live runner owns the entire game environment | **Adopted** (R11) |
| 22 | Start 1 infra + 1 biome + 1 live; base 2 proven / 1 accepted | **Adopted** as base; 6/3 kept as stretch, since he explicitly wants the allowance spent, routed to read-only surplus when writers can't grow |
| 23 | Cache keys incl. evaluator/env; malformed result = fail; live repeat policy | **Adopted** (R7) |
| 24 | Pre-review as assisted triage; auto-fix off | **Adopted** (R6) |
| 25 | Part 3: hypothesis outcomes under conditions, versioned protocols, held-out confirmation, negatives kept | **Adopted** (§D 12, 15) |
| 26 | Measure delivery, not rung activity; drop runs-per-rung targets | **Adopted** (R10 measures) |
| 27 | Cut to adoption essentials; write the method after the pilot | **Mostly adopted.** Kept §D as a draft *to be rewritten from the retro*, because he asked for it explicitly. Kept the R9 `found_by` field (minutes of work, and the retro needs it). |

**Where I disagree with GPT.** It would leave most of the allowance unspent. He said tokens unused by Wednesday are
lost, so v2 keeps the stretch target. It routes surplus into **read-only** work (walk red-teams, coverage audits,
yield backfill) that adds no git or review load. That fits the spirit of point 22 without forfeiting the budget.

---

## F. Owner questions (card-ready; recommended option first)

**Q1. Which biome goes around the loop first?**
- **Pyrelands (recommended).** Your north star is already validated and a ship rung is defined, so the pilot tests the
  loop, not the spec. Larger: 11 open items, review mostly not done.
- **NightsideIce.** Smallest and fastest to finish, but its spec is thin, so a pass proves less.
- **TheSump.** Small, much of its art already ours; spec unvalidated.
- **One you name.** Your priority wins; the plan adapts.

**Q2. When you skip a review item, what happens?**
- **Keep the accepted state; it waits (recommended).** Nothing ships on silence. The cost is that skipped items pile up,
  and the cap stops new review work when they do.
- **Pre-authorize a category to auto-accept (e.g. pixel-level art fixes).** Faster, visible and rollback-able. The risk
  is a wrong fix in that category ships unseen.
- **Everything waits for you, no categories ever.** Safest, slowest.

**Q3. During the burst, new feature ideas for the burst biomes…**
- **…are parked until that biome has an accepted version (recommended).** Converges, but delays new mechanics a few
  days. Your word overrides any one.
- **…are only ordered behind facet work, not parked.** Gentler, less convergence.
- **…no rule.** Today's behaviour.

**Q4. How hard to spend the allowance?**
- **Pace to ~90% of the weekly allowance by Wed 16:00, checked at each check-in (recommended).** Leaves headroom for
  failures.
- **All-out early, front-loaded Sun/Mon.** More gets tried before Gate 1 proves the loop, and that is the mess GPT
  warned about.
- **Conservative ~50%.** Leaves value unused.

**Q5. Where do you want the status?**
- **Three text lines in RimPulse's digest and at each check-in (recommended).** Zero new UI; works on the phone.
- **A new tab on the hub artifact.** Prettier, and another thing to keep current (deferred by default).
- **Both.**

## G. Owner rulings (card, 2026-10-11 18:12 PDT)
- **Q1 pilot biome: Pyrelands.**
- **Q2 skipped review items: keep the last accepted state.**
- **Q3 new features on loop biomes: parked until the biome has an accepted version.**
- **Q4 pace — owner typed:** *"Ignore the burst spend concept for now. This is a good process independent of that."* → the ratchet workflow is adopted as the PROCESS, not as a token-spend plan; no spend targets.
- Q5 (status surface) not yet asked.
- **Pilot scope widened (owner typed, 20:15):** *"I would like to take the Pyrelands + flowworks + gimme some slack together as the "around the loop" example. All three mods loaded together and pushed together."* → the pilot is ONE combined unit: Pyrelands + FlowWorks + GimmeSomeSlack on one mod list, one accepted version, checked and accepted together.
- **Seat split for the pilot (owner, card 20:17):** *"For this experiment only, Bench will own everything. This is NOT a change of policy, just an experiment."* BENCH builds, runs the live game and lands commits for Pyrelands + FlowWorks + GimmeSomeSlack; FOUNDRY stays off those three mods and off the bridge for them until the pilot closes. Item: `RATCHET_PILOT_PROVE_THREE_MODS_ONE_LOOP`.

## H. Pilot verdict - Pyrelands + FlowWorks + GimmeSomeSlack (BENCH, 2026-10-12; criteria met and pilot closed 2026-10-16)

Evidence: `Transient/bench_live_20261012{,b,c,d}/SITTING.md`, handoff `BENCH_REBOOT_HANDOFF_202610121341`.
Numbers below are from those sittings (MEASURED there); nothing here is estimated.

**What worked.** One loop ran unattended overnight: offline fixer agents, then one live-driver agent per pass
from a fresh `git archive` of all of src/ at HEAD, on one 23-mod tier (ratchet_pilot + mandrake.rm.patches),
owner list restored after each (md5 ee01dae9).
- GimmeSomeSlack proof_all 106/106 PASS (MEASURED, pass 1).
- FlowWorks validation_v2 GREEN 61/61 on passes 1 and 4 (MEASURED); river extension 17 PASS / 3 UNMEASURED / 0 FAIL (pass 4), breach_wash held 3 -> 0 (MEASURED).
- Pyrelands main run 20 PASS / 2 FAIL / 5 UNMEASURED (pass 2, MEASURED), then the census row PASSed on pass 3 after a harness fix.
- Four live passes closed 9 items; a regression and its fix were each proved live inside the same night.
- Tick rate: stepped 58.1 t/s vs Ultrafast 451.2 t/s vs burst 467.8 t/s (MEASURED), so a tick-burst tool buys nothing.

**What bottlenecked.**
1. One live game and one bridge: passes are strictly serial; every pass pays a ~100 s tier start (MEASURED) plus the suite wall time (v2 295 s, Pyrelands main 26 min, regrow 16 min).
2. Long game-time waits at ~58 ticks/s stepped (embergrass regrow is a 180,000-tick wait, ~50 min) once timed the shell out.
3. Harness faults masquerading as mod faults (census probe host, 300-char evidence cut, regrow burn length): each cost a full live pass to unmask.
4. Owner gates: art look in game, design cards (pit climb, pond units, canal look), threshold rulings. These did not block the machine loop, but they block "accepted".
5. Stale fixtures: a reloaded site save predates later patches (anima), so a fresh site is needed per mod-block change.

**Exit criterion: "full cycle done" for the pilot (machine-checkable except the last line).**
All hold at one HEAD sha on the 23-mod tier, recorded by `rimflow verify`:
1. `proof_all` GSS: 0 FAIL, 0 UNMEASURED.
2. FlowWorks `validation_v2 --live --fresh-map`: 0 FAIL, 0 UNMEASURED; river extension_proof: 0 FAIL (UNMEASURED only if classed SITE with a filed item).
3. Pyrelands north star (`northstar_driver run --mod Pyrelands`, fresh site fixture): 0 FAIL; every non-PASS row is INFERRED (its verified components named) or a labelled gap with a filed item for the missing tool; `modcheck floor --all` shows the validated hash current. *(Owner by card 2026-10-13, replacing "0 UNMEASURED"; see `debug_process.md` § "Long-duration properties".)*
4. Every BENCH-owned pilot item (PYRE_*, CANAL_*, POND_*, WEIR_*, ANIMA_*, RIVER_SITE_*) is `done` or `superseded`; none `doing`/`built` with a live recheck owed.
5. selftests N/N (`run_selftests.py`) and `code_review_status.py check` CLEAN on changed files.
6. The owner review queue `Transient/ratchet_owner_review_2026-10-12.md` rows 1-4, 6, 8 have owner provenance on the ledger (`--owner-said` / `--by-card`). This is the only non-machine line.

Outcome: all six criteria met; `RATCHET_PILOT_PROVE_THREE_MODS_ONE_LOOP` closed 2026-10-16T01:46Z at 682da5d82c (C1 GSS proof_all 118/119 + S12d PASS in validation_style, counted by owner card; C2 FlowWorks v2 61/61, river 20/0/1 owed by design; C3 Pyrelands 35 PASS / 0 FAIL, regrow INFERRED; C4-C5 met; C6 owner rows ruled). The owner walked the Pyrelands review save and approved every station (2026-10-16). Release meaning, by card 2026-10-15: ready, not published - built, tested, reviewed, packaged (About, preview, version), deployed into his game; Workshop upload later. Release-readiness work after the close is tracked on the ledger, not here.