# Art pipeline and art review: are they serving us? (2026-10-15)

This is a read-only review. Nothing was changed. The scripts and intermediate data are in the FOUNDRY scratchpad and are not committed.

## Verdict: PARTLY serving

| Part | Serving? | Evidence |
|---|---|---|
| Machine side (daemon, validators, facing derivation) | **Yes.** It is much better than in September. | The attempt failure rate fell from 31.6% to 23.3%. Most October failures cost nothing to render. North and south facings went from 0% to about 98% derived from a master. |
| Owner review (sheets and decisions) | **Partly.** The quality he sees is far higher, but the volume and the medium keep churning. | The owner's keep share went from about 50% in September to about 87% in W41. He made 2,588 rulings in October, against 529 in September. The medium changed three times (sheet, then in-game, then chat images). |
| Canon grader (gpt-6.1-sol, `canon_check.py` v1) | **No.** As a GATE it is not serving. | Its FAIL verdict has never predicted an owner rejection: 0 of 64. Its PASS verdict has never caught one: 32 of 32 owner rejections passed. Yet it decides retries and blocks installs. |

## 1. Instruments and their limits

- **Per-attempt time series:** `D:\Luke\dev\_artpipe\throughput.jsonl`, 8,453 result rows from 2026-09-09 to 2026-10-15. It is the only complete per-attempt series. Job files in `done\` and `failed\` are overwritten on requeue, so they record final states only.
- **Final job states:** `done\` holds 6,179 jobs and `failed\` holds 442. The naming trap: `X.json` is the job SPEC and `X.manifest.json` is the RESULT.
  - `canon_check` inside a result is a Python-repr string, not JSON.
  - 2,192 results are graded; all graded rows are from 2026-10-05 or later.
- **Lifecycle events:** `D:\Luke\dev\_artpipe\registry.jsonl`, 28,922 events.
- **Installs:** `collected.jsonl` holds 288 installs, but only from 2026-10-03 to 2026-10-08. It went stale when installs moved to the art ledger.
- **Owner decisions:** the art ledger `D:\Luke\dev\RimMandrake\infrastructure\state\art\events\{BENCH,FOUNDRY}.jsonl`, plus `archive\`. It holds 4,435 owner rulings, 925 `rejected` and 281 `install` events.
  - I excluded the 1,318 design-register rulings, which leaves 3,117 art rulings.
  - **September rulings are `legacy`/backfilled and carry no click-level provenance**, so September and October are not strictly comparable.
- **Grader against owner:** I joined owner rulings (their sha lists) to artpipe renders through the ledger's `variant kind=artpipe` sha-to-job map (6,311 shas), then to each job's canon verdict.
  - 746 graded renders carry an owner label; 36 of those are conflicted (both keep and reject) and were dropped.
  - **Selection bias:** the owner sees mostly renders that passed, so FAIL renders are under-sampled.
- **Sanity probes:**
  - Both verdict classes appear in the join (PASS 646, FAIL 64), so the join can see both.
  - I checked the verdict rule against the code: 1,988 of 1,988 PASS have passed==graded, and all 204 FAIL do not.
  - The 77-hour gap in throughput from 10-11 to 10-14 is **idle with an empty queue, not a stall**. The log says `IDLE — queue empty` at 15:39 on 10-11.

## 2. Machine-side metrics

### 2.1 Attempts by ISO week (from throughput.jsonl)

| Week | Attempts | OK | Fail % | Median s/render | Dominant failure |
|---|---|---|---|---|---|
| W37 (Sep 7–13) | 474 | 387 | 18% | 100 | worker_error and invalid self-reports |
| W38 | 505 | 346 | 31% | 104 | worker_error (147) |
| W39 | 1,811 | 1,034 | **43%** | 105 | worker_error (520) and bad_job_file (184) |
| W40 | 1,798 | 1,575 | 12% | 101 | worker_error (89) and bad_job_file (70) |
| W41 | 3,539 | 2,611 | 26% | 93 | master_failed (387), failed_canon (261), worker_error (237) |
| W42 (Oct 12–15, partial) | 326 | 252 | 23% | 93 | failed_canon (34) and master_failed (28) |

| Month | Attempts | Fail % | Worker-hours | Worker-hours spent on failures |
|---|---|---|---|---|
| Sept | 3,341 | 31.6% | 77 | 8 h (11%) |
| Oct | 5,112 | 23.3% | 120 | 13 h (11%) |

- **The failure mix changed in kind.** In September failures were infrastructure: worker_error storms from quota, auth and sandbox problems, plus bad job files. In October most were **zero-cost refusals**: master_failed (456) and bad_job_file (60) take 0 s because no render is spent. The rest are **grader rejections**: failed_canon (315), at about 2 renders each because of the in-daemon retry.
- **Machine waste is small.** About 11% of worker-hours in both months went to failures. Render cost is not the problem.
- **Failures come in bursts.** 973 of 2,248 failures (43%) arrived in 29 bursts of 8 or more same-cause failures with no success in between.
  - The worst were 09-19 (102 in 6 minutes), 09-23 (168 in 35 minutes) and 09-24 (185 in 13 minutes).
  - The newest example is 10-14 at 21:08, where a codex sandbox-seed mismatch after an upgrade burned 28 jobs as worker_error ("0 ok, 28 failed").
  - The daemon fails the whole queue instead of pausing on an environment fault.
- **Renders per finished target:**

  | Batch | Renders per finished target |
  |---|---|
  | RM_ tier, Sept 25 to Oct 11 | 1.07 |
  | bluedesert | 1.43 |
  | donorport | 1.40 |
  | donorart (today's donor-retirement wave) | 1.33 |
  | collected installs, 10-03 to 10-08 (median 1) | 1.17 |

- **Facing coherence is now structural.** North and south jobs derived from an accepted master (`derive_from`) went from 0% in W37–38 to 13% in W39, 91% in W40, 96% in W41 and 99% in W42. The median palette distance from master is 9.8 (p90 25.5).
  - **The cost is the cascade:** a failed master fails its children. That produced 456 master_failed rows, and requeueing them is still manual (`ARTPIPE_REQUEUE_AUTOMATION_1` is unbuilt).
- **Daemon uptime:** there are about 36 run logs, about 1.6 restarts a day from 09-30 to 10-14. The documented stalls are:
  - the 10-hour wedge after a quota reset (09-25);
  - stale code after an edit, because there is no hot-reload (10-05; a redo rendered without canon guidance);
  - the sandbox-seed mismatch (10-14).

  There are 23 gaps of 6 hours or more with no throughput. I could not tell idle from stalled for most of them, because there is no pending-depth history. That is UNMEASURED.
- **The failed\ backlog is clutter.** It holds 442 jobs.
  - **213 are already superseded** by a later done job for the same target and facing.
  - **229 are not superseded:** 103 failed_canon, 55 master_failed, 38 worker_error, 27 bad_job_file and 6 others.
  - Nothing triages them automatically.

## 3. Canon grader (gpt-6.1-sol, live mode v1)

### 3.1 What it outputs

- **Graded jobs:** 2,192 are graded and 910 skipped with "no canon entry and no owner note". Of the graded, 994 are canon-kind and 1,198 owner-note-kind.
- **Verdict rule:** all graded lines must pass. That gives PASS 1,988 (90.7%) and FAIL 204.
- **First-attempt pass rate:** 88% on canon-kind targets (451 of 514) and 97% on owner-kind targets.
- **Vacuous passes:** 343 PASS verdicts are **"0/0"**, meaning every line was marked na and nothing was graded. All of them are owner-kind, for example an owner note that only says "Add some variants".

  **The sheets show these as PASS.**
- **na use:** the grader uses `na` heavily and mostly correctly. North facings carry 614 na lines, against 280 for south and 310 for east.
  - The prompt already tells it that a face on a north view is na (`D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\artpipe\canon_check.py` around lines 219–223).
  - The per-job `canon_na` field exists as the deterministic override.
- **Near-misses dominate FAILs.** One line short of a pass accounts for 4/5 (39), 3/4 (36), 0/1 (29), 5/6 (17), 2/3 (10), 6/7 (7) and 1/2 (7). That is 145 of 204 FAILs.

### 3.2 Agreement with the owner (n=710 unconflicted labelled renders)

| Owner \ grader | PASS | FAIL |
|---|---|---|
| kept (678) | 614 | **64** (9.4% false fail) |
| redo / reject / out (32) | **32** (0% caught) | 0 |

- **Precision of a FAIL as a predictor of owner rejection is 0 of 64.** Recall is 0 of 32.
- Renders graded from 10-10 on show the same pattern: 80 kept PASS, 7 kept FAIL and no rejects caught.
- This repeats the 10-09 diagnosis (`D:\Luke\dev\RimMandrake\Transient\canon_check_leniency_2026-10-09.md`: 23 of 23 owner rejects passed). That diagnosis found that Must-show lines are presence tests a wrong animal satisfies, while vague or fine-detail lines fail renders he keeps.
- **The v2 candidate was tested and not adopted.** It added gate lines and a describe-then-diff pass. In `D:\Luke\dev\RimMandrake\Transient\canon_check_v2_prototype_2026-10-09.md` it caught about 2/3 of rejects but false-failed about 41% of random keeps. The daemon still runs v1.
- **Caveat:** N(neg)=32 is small, and labels are per sheet column, so a "keep" can be a lesser evil. Even so, a gate whose FAILs land only on renders he keeps is costing more than it saves.

### 3.3 Retries do not converge

| | Count |
|---|---|
| A FAIL followed by another attempt at the same target | 126 |
| That next attempt PASSes | 81 (64%) |
| That next attempt FAILs again | 45 |
| Second FAIL on the **same line** | **38 of 45** |
| Targets that FAILed at least once and **never** passed | 46 of 145 |

- **Today's three (2026-10-15) show the pattern.**
  - **Akk S:** v1, v2 and v3 each failed 4/5 on "Big round blue/violet eyes …". The reason was word-for-word the same each time: "small vertical ovals". That is about 6 renders, counting the in-daemon retries.
  - **Nexu(W) N:** v1, v2 and v3 each failed 3/4 on the BODY PLAN line ("forked tail is thick and furred rather than whip-like"). The face/mouth line was **correctly na** in all three.

    **Correction to the brief:** the failing line was not a back-view-inapplicable line. It was a strict tail-thickness reading of a body-plan line that the owner judged acceptable.
  - **Veermok S:** v1 scored 0/5 because it rendered a **wooden panel** with no creature at all. That was a correct, valuable catch. v2 scored 3/5 on "dog-like muzzle" and "not a gorilla flat face", and the owner accepted it.
  - All three were installed on his word in commit `b1e7d0152`, with the grader still saying FAIL.
- **Conclusion.** The grader earns its keep on **gross** failures: no creature, wrong object, a duplicate of the master. It is noise on **fine-detail** lines. Re-filing v2 and v3 with the same CORRECTION text spends renders and a day of calendar time without moving the verdict.

## 4. Owner-side metrics (art ledger)

| Week | Rulings | Sheets | Sittings | keep | redo | reject/out | Trust |
|---|---|---|---|---|---|---|---|
| W37 | 37 | 3 | 2 | 12 | 3 | 3 | legacy |
| W38 | 478 | 11 | 6 | 76 | 74 | 10 (+295 replace-donor) | legacy (60 are blanket "approve all") |
| W39 | 9 | 2 | 2 | 2 | 0 | 5 | legacy |
| W40 (Sep 28–Oct 4) | 207 | 13 | 6 | 125 | 82 | 0 | mixed (88 flawed-sheet) |
| W41 | **2,198** | **36** | 21 | 1,693 | 259 | 2 | ruled |
| W42 (partial) | 183 | 7 | 8 | 181 | 2 | 0 | ruled |

- **Keep share of keep+redo+reject:** about 47% in W38 (76/160, before 295 replace-donor), 60% in W40, 87% in W41 and 99% in W42.
  - What he sees is now mostly right first time. The cause is canon briefs, realism style notes and derived facings, not the grader.
- **Load:** W41 was 2,198 rulings over 36 sheets in 21 sittings, and 1,267 of them carry a note. That is a heavy week of owner attention, and most of it confirmed art that was already fine.
- **Reversals:** keep followed by a later redo/reject was 18 in W38 and 40 in October, out of about 719 subjects first seen in October.

  Redo-then-keep (N→P) is mostly the normal redo loop and is not counted as a flip. No flip has shas on both sides, so "same art ruled twice" against "new art" is UNMEASURED.
- **Lost picks:** in October sidecar history, 38 rows had a decision vanish between commits (abyss 12, twilightsea 11, warscar 4, greentide 3). These are not yet separated from enact cleanup.
  - Two known incidents are fixed: 231 duplicate ingest events, and re-lettered columns producing 28 spurious rejections.
  - Remap runs on 10-09 and 10-10 reported 0 moved and 0 orphaned.
- **Repeated rows / stale sheets:** fixed structurally.
  - `serve_gated.py` refuses stale sheets with exit 5, and the "accept unchanged" button is gone.
  - 16 stale sheets were rebuilt on 10-14.
  - It still happened on 10-12 (a GSS sheet showed an already-ruled row) before the gate landed.
- **Time to install:**

  | Measure | Median | p90 |
  |---|---|---|
  | Generation to install (281 joined installs) | 8.2 h | 118 h |
  | Target first render to install, W40 | 0.7 h | — |
  | Target first render to install, W41 | 8.3 h | — |

  Owner-accept to install is UNMEASURED: only 16 joins, by name, with a median of 17 h. Accepted-but-not-installed backlog is also UNMEASURED: "keep" usually means keep the current art, so 747 latest-keep subjects is not a backlog count.
- **Medium churn, by his own words:**
  - 10-05: "not human readable. Bad medium" and "I need to see it in the game".
  - 10-12: "I HATE the 'accept unchanged.'" and "not serving stale information".
  - 10-15: "no scale or cell width information" and "You can show me images in the chat, but not whole art sheets."

## 5. Then and now

| Pain point | September 2026 | October 2026 (now) |
|---|---|---|
| Failed attempts | 31.6%, mostly worker storms (up to 185 in 13 minutes) | 23.3%, mostly zero-cost refusals and grader FAILs. Storms still happen (28 on 10-14). |
| Wasted renders | 11% of worker-hours | 11% of worker-hours. **The new waste is grader-driven v2/v3 re-files that do not converge.** |
| Sheets redone or unusable | Truncated sprites (09-28), corpse texture in the current column (65 of 109), no scale | The freshness gate and scale panels are built. "No cell width" is still open (`ART_SHEETS_SCALE_CELLS_WIDEN_TOO_LATE`). |
| Repeated rows | Common, with no gate | A serve gate refuses stale sheets. One incident on 10-12 came before the gate. |
| Lost picks | Not observable (sidecars committed once) | 38 vanished rows in W40–41 (cause not split). Ingest and lettering bugs are fixed. |
| Donor art kept | 295 replace-donor rulings in W38. Ruling 10-05: "We're not keeping any." | The donor-retirement wave is under way: 198 donorart targets, 192 rendered OK by the machine. |
| Facings incoherent | Independent N/S renders, staring north faces (09-14) | About 98% derived from the master, with a facing stamp guard. The cost is master_failed cascades. |
| Owner keep rate | About 50% | About 87–99% |

## 6. Ranked improvements

1. **Demote the canon grader from gate to triage. This has the highest value and is cheap.**
   - Keep auto-FAIL only for **gross** failures: no creature or object, wrong subject (wooden panel), duplicate of master, or 0–1 lines passing on a canon job.
   - For a near-miss (n−1 of n), **do not retry and do not block**. Send the image to the owner with the grader's failing line printed under it as a question.
   - **Evidence:** FAIL precision 0 of 64, PASS catch 0 of 32. 38 of 45 second FAILs repeat the same line. Today all three FAILs were accepted.
   - Re-promote only after a labelled calibration set (the 710 joined renders exist) shows FAIL precision above 50%.
   - **Stop agents re-filing v2/v3 with the same CORRECTION text.** One retry, then it goes to the owner.
2. **Install on his accept, not on a grader pass.** Do not auto-install on a pass: at 0/32 catch, that would install everything he would reject.
   - Instead wire "accepted in chat or on a sheet" straight to `art.py install --owner-said` plus deploy in one command, inside the same turn. This removes the 8–118 hour generation-to-install tail.
3. **Review medium: small chat-image batches, true scale, one verdict word each.** He has asked for chat images, not whole sheets (10-15).
   - Send 6–10 images per batch. Show each at true scale beside a colonist, with the cell footprint and the grader's flagged line. Record the reply straight to the ledger.
   - Keep sheets only for large comparative passes (a whole biome roster), and always with cell rulers (`ART_SHEETS_SCALE_CELLS_WIDEN_TOO_LATE`).
   - **Do not ask him to confirm art the machine already got right.** W42 ran 99% keep.
   - Sample only first-of-species masters and anything the grader flagged as gross. Let derived facings of an accepted master ride unless the facing audit flags them.
4. **Make line-to-facing applicability deterministic.**
   - **Tags:** add per-line facing tags to the canon entries' `## Must show`, for example `[not:north]` on face/eye/mouth lines and `[east-only]` on lines like "long tail visible in profile". canon_check then marks na in code, not by model judgment. The model was inconsistent on owner-kind lines (lesson `D:\Luke\dev\RimMandrake\infrastructure\state\lessons\20261011T061409Z-BENCH-artpipe-owner-kind-canon-check-grades.md`).
   - **Vacuous passes:** count 0/0 as "UNGRADED", never PASS. There are 343 of them on sheets today.
   - **Honest limit:** today's Nexu N failure was not an applicability error, so this fixes noise but not strictness. Item 1 does that.
5. **Make failed-job triage and environment faults automatic.**
   - **Circuit breaker:** after N consecutive same-cause worker_errors (for example 5), the daemon **pauses and alerts** instead of draining the queue. 43% of all failures came in bursts, the newest being 28 jobs on 10-14 from a sandbox-seed mismatch.
   - **Nightly triage pass over `failed\`:**
     - archive the 213 already superseded;
     - auto-requeue master_failed children once their master passes (`ARTPIPE_REQUEUE_AUTOMATION_1`);
     - requeue worker_error once;
     - route the remaining failed_canon to the owner's next chat batch (item 3).
6. **Smaller items:**
   - **Daemon:** add a code-version stamp and hot-reload check (the 10-05 stale-code render).
   - **Throughput:** log pending depth in throughput or status so idle and stall can be told apart. 23 gaps of 6 hours or more are currently ambiguous.
   - **Install log:** retire or repoint `collected.jsonl`, which has been stale since 10-08, so no tool reads it as the install log.
   - **Sidecars:** split the 38 vanished rows into enact cleanup or a real loss with one audit, then close the question.

## 7. What is UNMEASURED

- Owner-accept to install latency (the name joins are too sparse).
- The accepted-but-uninstalled backlog.
- Same-art against new-art reversals (no sha on flips).
- Idle against stalled in throughput gaps.
- The grader's agreement on renders he never saw, which are most FAILs (selection bias).
- September decision provenance (legacy).
