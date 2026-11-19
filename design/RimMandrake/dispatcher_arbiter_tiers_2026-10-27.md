# RimFlow v3: the Arbiter by risk tier (2026-10-27)

Item `ARBITER_REDESIGN_RISK_TIERED_VERDICTS` (caused by `RIMFLOW_ARBITER_MEASURE_FALSE_REJECTS`).
Code: `src/RimMandrake/rimflow/arbiter_tiers.py` (+ `selftest_arbiter_tiers.py`). Role text:
`src/RimMandrake/rimflow/roles/arbiter.md`. Data for the Auditor and Operations (tier labels, history):
`D:\ClaudeWork\rimmandrake\arbiter_tiers\`. Judge-facing files (no tier labels): `D:\ClaudeWork\rimmandrake\arbiter\`
`judge_list.json` and `bounces.json`. Fixes after review Y (14 findings, all real):
`D:\ClaudeWork\rimmandrake\review_v3_Y\fixes.md`.

## 1. Why

The simulation (`rimflow_v3_sim_findings_2026-10-27.md`, findings 3-4) says an Arbiter that spends one AI verdict on
every done claim, under today's token budget, costs 8-11 sound closes a day and +18-24 blocked hours a week. It cuts
the defect fraction by only 1-2 points, and it mostly defers work. Most done claims either carry recorded evidence
that decides them without judgment, or carry nothing that marks them as risky. Judgment is spent where it changes
the answer.

Rulings this design keeps:
- The Arbiter weighs ALL the evidence: offline tests, live tests, code review and user feedback. The north star is one
  method among them. Tier 0 reads every kind that is recorded in a machine-readable form, and owner words after a
  close force a claim to tier 2.
- Its helpers never built the work. Tier-2 judges are fresh non-maker helpers (`delegation_policy.md` §4).
- It is advisory for at least the first week. Every tier writes advisory records only.
- It is token-blind. The tiering is done by code (`arbiter_tiers.py`) before the Arbiter runs. The Arbiter judges
  fully every claim it is handed and never chooses what to skip. Cost is measured by Operations, never by the
  Arbiter (§5).

## 2. Tier 0: deterministic gates (no AI)

### What a done claim records today (MEASURED, 816 closes, 2026-10-20 to 10-27)

| source | where | per claim? | coverage, last 7 days |
|---|---|---|---|
| close event | ledger `close`: `sha`, `reason`, `why` | yes | 816/816 have a sha. 19 do not resolve in either clone, or are `HEAD`/`PENDING` |
| verify events | ledger `verify`: `result` pass/partial/fail, `criterion`, `level`, `evidence`, `sha` | yes | **51/816 closes have a verify before the close** (35 pass, 11 partial, 5 fail) |
| acceptance criteria | ledger `implemented.criteria[{id, level}]` | yes | 21/816 |
| cited evidence on disk | paths inside `verify.evidence` | yes | 36 closes cite a local path. Remote `host:/path` evidence cannot be checked from here |
| code review | `infrastructure/state/code_review/*.jsonl`, sha256 per path | by file, not by claim | 164 PASS (every code file clean at the claimed content), 501 OPEN, 132 touch no code |
| owner feedback | ledger `note` with `ownerSaid`, `finding` events | yes | 3 + 3 |
| selftests | `~/.local/state/rm-selftests/records/` (tree-hash keyed pass cache), `last_run.json` (latest only) | **no** | not linked to any claim or sha |
| C# build | `<build root>/<Mod>/BUILD_SOURCE.json` | **no**: latest build per mod, overwritten | - |
| north star | `infrastructure/state/modcheck_status.json` | **no**: current status per mod, no sha | - |
| validators (`validate_patch.py`) | nothing recorded | **no** | - |

On G5 (code review) the cold run found 712 file hits that were reviewed clean only at later content, and 476 that
were never recorded. Review happens after the close, so G5 must be read at verdict time, not at close time.

### The gates (`arbiter_tiers.gates`)

| gate | reads | FAIL (bounce) | PASS |
|---|---|---|---|
| G1 build identity | close `sha` | missing, `HEAD`, or found in neither clone | resolves |
| G2 recorded verification | latest `verify` per criterion before the close | a `fail` that no later pass supersedes | every latest result is `pass` |
| G3 acceptance coverage | `implemented.criteria` vs passing verifies | (never; uncovered means OPEN) | every declared criterion has a pass |
| G4 evidence exists | local paths cited by the latest verify per criterion | every cited path is gone | every cited path exists (some gone: UNMEASURED, missing paths listed) |
| G5 code review | each touched code file's sha256 at the sha vs code-review records replayed in time order (the last verdict for a path and hash decides; files the commit deleted are skipped) | (never; unreviewed means OPEN) | every touched code file is clean at that content. A blob git could not read is UNMEASURED |
| G6 close evidence | `close_evidence.lookup(sha=, item=, paths=)`: clean-tree runs (selftests, winbuild, validate_patch, modcheck) at the close sha that cover the touched paths or are tagged with the item | the latest result of any covering run is FAIL | every covering run's latest result is PASS (UNMEASURED run: UNMEASURED) |

G2 and G6 each carry an independence gate (`G2_independent`, `G6_independent`): PASS only when the passing record is
from a seat that is not a maker of the claim (the close seat, or a claim, start, reclaim or implemented seat before
the close). A close-evidence record with no seat makes `G6_independent` UNMEASURED. A git error (timeout, failure)
is not "the sha does not resolve": G1 reads UNMEASURED, not FAIL.

**When the ledger names no builder** (no claim, start, reclaim or implemented event before the close; 34 of 56 closes
in one measured day), G6 infers one (`infer_builder`, TIERS_FIX_G6_BLIND_WITHOUT_BUILDER). The sources, in order:

1. the close seat (never OWNER);
2. the commit's author or trailers: **unusable today**. Every commit has the same author email and no seat trailer,
   so this source names nothing and is skipped;
3. the session that made the commit: its `Claude-Session` trailer, mapped to the seats that whoami-sure, MAC-checked,
   shared-tree close-evidence records ran under that bridge session (`session_seat_map`).

If exactly one seat is named across the sources, that seat is the builder (`G6_builder_inferred` records the seat and
what named it). If sources disagree, or none names a seat, G6_independent is UNMEASURED. Nothing is guessed. An
inferred builder is weaker than a ledger one, so independence then needs more: every covering passing run must come
from the runner seat (`RUNNER_SEAT`, DISPATCHER), be an isolated-tree run, and be sure of its own seat. Its session
must also differ from the commit's, and the commit session must be readable. Otherwise G6_independent is UNMEASURED.
No route closed in reviews Y to AD is reopened: G6_independent still needs MAC-checked, whoami-sure runs.

The `Claude-Session` trailer names the seat window's bridge session, and all of that window's helpers share it
(`session_01Np8` is on 857 commits in 30 days). So a run started from inside the builder's window counts as
same-session even when another agent ran it. That is correct for independence, but a helper cannot be told apart
from its seat (filed: COMMIT_SESSION_FIX_NAMES_WINDOW_NOT_HELPER).

**Who reviewed** (G5, CODE_REVIEW_WIRE_REVIEWER_SEAT). A `mark-clean` record now carries a `reviewer` and a `recorder`,
kept apart, plus `review_mac`, an HMAC under the close-evidence key (`src/RimMandrake/Utils/review_identity.py`):

- `recorder` is whoami() of the process that ran mark-clean.
- `reviewer` is one of:
  - `self` (the default);
  - `--reviewer-seat/--reviewer-session/--reviewer-agent`, which is the recorder's word only;
  - `--gpt-job <id>`. mark-clean refuses unless that gpt_consult job's MAC'd receipt (`consult/receipts.jsonl`,
    written by `gpt_consult.py` for every job) answered and inlined these exact bytes.

`identity()` reads each clean record as one of four kinds:

- `unknown`: an old record, a bad MAC, or no key;
- `self`: the seat came from whoami's own sources;
- `asserted`: named, not proven;
- `external`: `gpt_consult:<job>`, re-checked against the receipt.

A review counts as independent of the builder in only two cases:

- it is `external`;
- it is `self` by a seat the ledger names as not a maker, under a session that differs from the commit's.

Old records stay `unknown` and never count.

- **BOUNCE**: G1, G2, G4 or G6 is FAIL. While `verdicts` is `"advisory"` a bounce is a record only: a line in
  `bounces.json` with the failing gate and its evidence, and, when the Arbiter confirms it, a FAIL-module or
  FAIL-check line in `verdicts.jsonl`. Nothing is returned to the builder: no reopen, no spawned work, no message.
- **PASS0**: an independent pass (G2 PASS with G2_independent PASS, or G6 PASS with G6_independent PASS and G2 PASS
  or NONE), G1 PASS, G3, G4, G5 and G6 PASS or NONE, and no risk flag (`NOT_LOW_RISK`). A builder's own verify or
  run never passes tier 0.
- **No machine evidence** (G2 NONE, G5 not PASS, G6 NONE): never passed by code. It goes to AI review
  (`T2_NOEVIDENCE`), or is held when the AI batch is refused. Prose in the close reason is not machine evidence.
- **Unmeasured** (any gate UNMEASURED): `T2_UNMEASURED`, same handling. An unreadable input is never a pass.
- **OPEN**: everything else goes to tier 1.

### Missing gates (to build, in this order)

**Evidence for 1-4 is now recorded** (CLOSE_EVIDENCE_BUILD_GATES_CAN_DECIDE): `run_selftests.py` (outer runs, `--only`
and nightly), `winbuild.py`, `validate_patch.py` and modcheck's `status.record_run` each append one line per run to
`<agent storage>/rimmandrake/evidence/YYYY-MM-DD.jsonl` via `src/RimMandrake/Utils/close_evidence.py` (tool, HEAD sha,
dirty flag, paths, PASS/FAIL/UNMEASURED, `$RIMFLOW_ITEM`). `close_evidence.lookup(sha=, item=)` returns only clean-tree
records. G6 reads it (above), so items 1-4 below are covered by G6 once their records are trustworthy. Review Z
found they are not yet: concurrent writes can lose lines, a commit landing mid-run can be recorded as PASS, and
`lookup` ignored the paths a run covered. That fix is in `close_evidence.py` (another item). Until it lands,
`arbiter_tiers` calls `lookup(sha=, paths=)` and, if `paths=` is not accepted, falls back to a sha-only lookup
filtered by path here; every G6 result before the fix rests on unfixed records. All 8 records in the window carry
no seat, so no G6 pass is independent yet.

1. **Selftest result per claim.** The runner already caches PASS records by tree hash, but no claim names them. Fix:
   `rimflow close` or `implemented` records the `run_selftests --only` set and its result for the claimed sha (or the
   records key). Then G6 reads it.
2. **Build result per sha.** `BUILD_SOURCE.json` is overwritten and does not mark failures. Fix: winbuild appends
   `{mod, source_sha, ok}` to a log. Then G7 reads it.
3. **Validator result.** `validate_patch.py` records nothing. Fix: append `{path, sha, live, defs, result}`.
4. **North-star result per sha.** `modcheck_status.json` is current state only. Fix: keep the run record (already
   carries `run_id`) with the source sha, so a claim can be matched to the modcheck run of its build.
5. **Verify on the claim.** Only 6% of closes carry any verify event. That is the biggest gap. Until builders record
   `rimflow verify` for the checks they ran, tier 0 can pass almost nothing (1% PASS0 today). The fix is the
   Producer's named scenarios with `verify:` lines, plus a close-time reminder. A verify is not required to close.
6. Two instrument faults found while measuring, filed: `PRESCREEN_SHA_FIX_BLIND_TO_FOUNDRY` (the pre-screen looks only
   in the bench clone, so 58 of 816 closes falsely read `sha_unresolvable`; it also never checks `D:\` evidence) and
   `CLOSE_SHAS_AUDIT_NAME_NO_COMMIT` (17 BENCH closes cite commits that exist in neither clone).

## 3. Tier 1: risk rank

`audit_prescreen.score` (rules in `audit_prescreen_rules.json`, unchanged) flags every claim. Flags added here:
`owner_words_after_close`, `finding_against_item`, `review_by_closing_seat_only` (no clean review record of the touched files has a reviewer independent of the
builder, as defined in section 2) and `git_unreadable`.
`no_check_evidence` is dropped when a machine record exists, and `closed_by_maker_only` when an independent G2 or G6
pass exists.

Only OPEN claims that have machine evidence, are fully measured and are not forced are ranked (`rank_evidenced`).
Each flag is weighted by its rarity within that set, `mult * min(6, -log2(rate))`, with no rarity zeroing: a gap
shared by most of the set still weighs more than 0 (review Y F1; before, a flag on over half the window weighed 0,
so the commoner a gap, the more claims passed). Then:

- **Forced to tier 2**, whatever the score: `gate_or_harness_path`, `flowworks_or_live`, `past_audit_failed`,
  `reopened_before`, `owner_words_after_close`, `finding_against_item`. A change to the gates themselves, a live
  FlowWorks claim, or anything the owner spoke on after the close is never passed by code.
- **Risky slice**: ranked claims scoring at or above the 75th percentile of ranked scores (`SLICE_QUANTILE`) and
  above 0. Ties at the cut go in together. In the re-measured window the cut was 0.6, one
  `review_by_closing_seat_only` flag.
- The rest pass on rank (**PASS1**).

## 4. Tier 2: AI judgment

- **Who gets an AI verdict:** every T2 claim (risky slice, forced, no evidence, unmeasured), plus calibration: each
  PASS0 and PASS1 claim is drawn independently with probability 1/10 (`CALIB_EVERY`) by a keyed hash of item and sha
  (key: env `ARBITER_CALIB_SALT`, else a generated `arbiter_tiers\.calib_salt`). The draw is stable across runs, has
  no floor at small windows and cannot be predicted from the code.
- **Blinding:** the judge reads `arbiter\judge_list.json`: item and sha only, T2 and calibration claims mixed in an
  order set by a keyed hash. The tier labels stay in `arbiter_tiers\`, which the role does not read; code joins the
  tier into `verdicts_tiered.jsonl` afterwards (`arbiter_tiers.py join`).
- **Who judges:** the Arbiter with judge helpers, at most 2 at a time. They are fresh, have no maker context, and
  never touched the item's commits. The verdict classes are those of `arbiter.md`.
- **What they read:** all the evidence, including what tier 0 read, because a gate result is evidence and not a
  verdict.
- **Bounces:** tier-0 bounces are recorded by code with class `FAIL-module` (or `FAIL-check` when the failing
  evidence is the harness's). The Arbiter reviews the bounce list each batch and may overturn a bounce whose evidence
  is wrong. An overturn is a measured false reject of tier 0.

## 5. Measurement in the advisory week

Every record is advisory: nothing blocks, and no `rimflow verify` is written. Each number below has one file and one
owner.

| number | definition | recorded in | computed by |
|---|---|---|---|
| tier of each claim | T0_BOUNCE / T0_PASS / T1_PASS / T2_RISK / T2_NOEVIDENCE / T2_UNMEASURED, plus the `calibration` flag | `D:\ClaudeWork\rimmandrake\arbiter_tiers\tiers.json` (latest), `tiers_<ts>.json` (one per run, kept) and `tiers_history.jsonl` (one line per claim per run) | code, before each Arbiter batch |
| verdict | the Arbiter's class per claim, with interim reviewer verdict and evidence paths (no tier: the judge never sees it) | `D:\ClaudeWork\rimmandrake\arbiter\verdicts.jsonl`; code joins the tier into `arbiter_tiers\verdicts_tiered.jsonl` | the Arbiter; the join by code |
| **false-reject rate** | (FAIL or BOUNCE verdicts later shown sound) / (FAIL or BOUNCE verdicts). "Shown sound": the owner says so; or an Auditor sample says sound; or the same sha passes with no escape filed for 7 days. Reported separately for T0 bounces and T2 fails | `D:\ClaudeWork\rimmandrake\arbiter\outcomes.jsonl`: `{item, sha, tier, verdict, outcome: sound\|defect\|unknown, by: owner\|auditor\|live\|7day, evidence}` | Auditor (`AU-*`), from the ledger: `finding`, reopen, `ownerSaid` notes and verify fails on the item after the verdict |
| **false-pass rate** | (PASS-class verdicts or T0/T1 passes later caught defective) / (passes). "Caught": a `finding` or reopen against the item, a failing Auditor sample, a failing live run, or the owner. Reported per tier. The calibration slice gives an unbiased T0/T1 estimate: AI FAIL on a calibration claim that a gate or the rank passed | same `outcomes.jsonl` | Auditor |
| **rank lift** | defect rate in T2_RISK / defect rate in calibration claims | derived from `outcomes.jsonl` | Auditor |
| **cost per verdict** | tokens of the week's Arbiter runs / AI verdicts in those runs | numerator: the Dispatcher journal (`journal.jsonl` in the dispatcher state dir; `tokens` on each finished Arbiter run, all four usage fields). Denominator: `verdicts.jsonl` rows with tier T2 or calibration | **Operations only**. The Arbiter never sees it |
| rig minutes per verdict | wall time of the run / verdicts | Dispatcher journal | Operations |

A rate needs its word: a rate becomes MEASURED at 30 or more outcomes of its kind. Below that it is UNMEASURED, and
its point estimate is never quoted alone.

**Before any binding decision**, re-run `src/RimMandrake/Utils/sim/rimflow_v3_sim.py` with the measured values in
place of these V3_ONLY priors:
- `arb_fr_max` from the T2 false-reject rate at the strictness in use;
- `arb_s_lo`/`arb_s_hi` from 1 - false-pass on calibration claims;
- `arb_ite` from cost per verdict;
- `arb_check_min` from rig minutes per verdict.

Add a coverage knob for the AI share and one for rank lift. The sim has neither today; §6 runs a scratch subclass.
Port that into the sim as an experiment when the numbers land. The Conductor carries the re-run result to the owner
with the binding card.

## 6. The tier mix now, and the simulator's prediction

### Tier mix (MEASURED, re-measured after review Y)

Run of `arbiter_tiers.py --days 7` over 817 closes, 2026-10-20T15:48Z to 2026-10-27, with the review-Y fixes.
Output: `D:\ClaudeWork\rimmandrake\review_v3_Y\remeasure_data\tiers.json` and `remeasure.txt`. The first run
(784f31250602, 816 closes, before the fixes) is beside it for comparison.

**This mix rests on close-evidence records that are not fixed yet (review Z).** G6 found 8 records in the window and
passed 1 claim on them. When the fix lands, re-run; the mix can only move from T2_NOEVIDENCE toward ranked or T0
as records accumulate.

| tier | before fixes (816) | after fixes (817) |
|---|---|---|
| T0 BOUNCE | 25 (3.1%) | 25 (3.1%) |
| T0 PASS | 8 (1.0%) | 2 (0.2%) |
| T1 PASS on rank | 485 (59.4%) | 41 (5.0%) |
| T2 risky slice or forced | 298 (36.5%) | 153 (18.7%) |
| T2 no machine evidence | (passed or ranked) | 595 (72.8%) |
| T2 unmeasured | (passed) | 1 (0.1%) |
| **AI verdicts (T2 + calibration)** | **347 (42.5%)** | **755 (92.4%)** |

How to read it:
- The first mix passed claims with no recorded evidence on rank (F1). 595 closes (73%) carry no verify, no clean
  review of their files and no close-evidence run; by the F1 rule none of them is passed by code.
- T0 PASS fell from 8 to 2 because a builder's own verify no longer passes tier 0 (F5).
- Of the 194 ranked claims, 129 carry `review_by_closing_seat_only`. Without rarity zeroing that flag sets the cut,
  so the rank passes only 41.
- The saving the first mix promised is not there on today's records. It returns only as machine evidence is
  recorded by someone other than the maker: non-maker verifies, close-evidence runs with a seat, and code-review
  records that name the reviewer.

Limits:
- Past audits: `D:\ClaudeWork\rimmandrake\auditor\audits.jsonl` does not exist, and the module now refuses to run
  without it (exit 2). The re-measure passed an empty file, so `past_audit_failed` could not fire.
- Code-review records carry only the recording seat, never the reviewer, so a review cannot be shown independent.
- G5 accepts reviews made after the close.
- Closes include OWNER closes and non-code kinds. The live Arbiter would take the same stream.

### After builder inference and reviewer identity (MEASURED, 2026-10-27)

All runs used `--now 2026-10-27T21:56:36Z` and a fixed calibration salt. The evidence and results are in
`D:\ClaudeWork\rimmandrake\arbiter_prep\measure3\` (`compare1n.txt`, `compare7.txt`).

**One day, 56 closes, production-like store.** Here the DISPATCHER isolated runs carry no bridge session.

- G6_independent UNMEASURED fell from 38 to 27.
- 11 claims now PASS G6_independent: 3 reach T1_PASS and 8 reach T2_RISK. Before the change all 38 were T2_UNMEASURED.
- T0_PASS stayed at 0, because those claims are G5 OPEN (unreviewed).
- 26 of the 27 still unmeasured have touched paths that no isolated run covers (json and md files with no selftest).
  That is an evidence gap, not an identity gap.
- AI inflow went from 53 to 52 a day.

**Seven days, 832 closes, the prior store.** There the DISPATCHER runs were made inside the BENCH window, so they
are same-session and inference changes no G6 result.

- `review_by_closing_seat_only` rose from 132 to 161 of 161 G5 PASS claims: 29 changed. Every existing clean record
  predates the reviewer block, reads `unknown` and never counts.
- 95 claims moved from T2_RISK to T1_PASS. This is an artifact. The flag now sits on 152 of 158 ranked claims, so
  rarity weighs it about 0. A stricter flag lowered scrutiny (filed: ARBITER_RARITY_FIX_UNIVERSAL_GAP_LOWERS_RISK).
  The 7-day AI count of 787 to 706 is therefore not a real gain.

### Simulator prediction (ASSUMED; rests on assumptions)

Script: `D:\ClaudeWork\rimmandrake\arbiter_tiers\sim_tiered.py`. It is a scratch subclass of `Sim`, because the sim's
params have no coverage knob.

Setup:
- Base: the `isolate` setup (v3.2 + Arbiter), under quotas, 240 members, both structures.
- AI share 0.425 was MEASURED on the first mix. The re-measured share is 0.924, so this prediction is stale: at that
  share the tiered Arbiter is close to the all-claims one. It has not been re-run.
- Non-AI claims close at no token or rig cost and get no extra detection.
- Rank lift L is ASSUMED. L is how much likelier a claim with an undetected defect is to be sent to AI: L=1 is
  random, L=2 or 3 is a useful rank.

Results: `exp_tiered_c0.425_{park,pull}.jsonl`, `summary1.txt`. Paired median [p10, p90] against the current
all-claims Arbiter:

| variant | sound/day | escapes/week | defect fraction |
|---|---|---|---|
| no Arbiter (v3.2) | +7.9 / +10.7 | +62 / +61 | +1.8 / +1.2 pt |
| tiered, L=1 | +4.0 [1.8, 7.1] / +5.6 [2.6, 10.0] | +34 / +34 | +1.4 / +0.9 pt |
| tiered, L=2 | +3.0 [1.3, 6.3] / +4.8 [2.2, 8.6] | +18 / +17 | +0.1 / -0.3 pt |
| tiered, L=3 | +2.6 [1.1, 6.1] / +4.5 [2.0, 8.0] | +11 / +11 | -0.5 / -0.8 pt |

(park / pull. Blocked hours fall by 6.5-11 h/week in every tiered variant.)

**Reading (resting on assumptions):**
- The tiered Arbiter wins back about a third to a half of the 8-11 sound closes a day that the all-claims Arbiter
  costs.
- Whether it also keeps the quality depends entirely on the rank's lift. Random selection (L=1) gives most of the
  quality back. A rank with lift 2 or more keeps the defect fraction level with the all-claims Arbiter, or better.
- Lift is the number the advisory week must measure first, through the calibration slice.
- Every Arbiter prior (sensitivity, false-reject, cost per verdict, rig minutes) is still the guessed V3_ONLY range.
- The unlimited-token run was not done.

## 7. Rollout

1. Advisory week. Before each batch, `arbiter_tiers.py` writes `judge_list.json` and `bounces.json` for the
   Arbiter and `tiers.json` for the Auditor, and the Arbiter judges every claim on the judge list. As scheduled
   (`--since-cutoff --cap 6`, ARBITER_DECIDE_BACKLOG_NEVER_DRAINS), the list holds only claims closed after the
   Arbiter's cutoff stamp. It takes the oldest unjudged ones first, at most 6 a batch less its UNRESOLVED re-judges.
   It never includes a claim that already has a verdict line, or one whose isolated evidence was carried. Claims past
   the cap wait; they do not age out. Inflow ran at about 49 AI claims a day against 12 a day of capacity on
   2026-10-27, so the queue lag grows until the cap is re-sized from the measured verdict cost. Gate results and bounces are logged, but the interim GPT reviewer still gates closes (A-1).
   The module is not wired into `role_launch.py` yet; that is a Dispatcher change for its owner.
2. Build missing gates 1-5 as their own items. Each new gate shifts claims from T1/T2 into T0.
3. Measure (§5). Re-run the sim on the measured values. The Conductor carries the result to the owner. Binding is his
   switch, as before.
