# RimFlow v3: the Arbiter by risk tier (2026-10-27)

Item `ARBITER_REDESIGN_RISK_TIERED_VERDICTS` (caused by `RIMFLOW_ARBITER_MEASURE_FALSE_REJECTS`).
Code: `src/RimMandrake/rimflow/arbiter_tiers.py` (+ `selftest_arbiter_tiers.py`). Role text:
`src/RimMandrake/rimflow/roles/arbiter.md`. Data: `D:\ClaudeWork\rimmandrake\arbiter_tiers\`.

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
| G4 evidence exists | local paths cited by verifies | every cited path of a verify is gone | at least one cited path exists |
| G5 code review | each touched code file's sha256 at the sha vs clean records | (never; unreviewed means OPEN) | every touched code file is clean at that content |

- **BOUNCE**: G1, G2 or G4 is FAIL. The claim goes straight back to its builder seat (Foundry, or the seat that
  closed it) with the failing gate and its evidence (`gate_evidence`). No AI is spent on it.
- **PASS0**: G2 is PASS, G3 and G5 are PASS or NONE, and no risk flag is set (`NOT_LOW_RISK` in the module).
- **OPEN**: everything else goes to tier 1.

### Missing gates (to build, in this order)

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

`audit_prescreen.score` (rules in `audit_prescreen_rules.json`, unchanged) scores every claim that was not bounced.
Each flag is weighted by its rarity in the window: `mult * min(6, -log2(rate))`. Two flags are added here:
`owner_words_after_close` and `finding_against_item`. Then:

- **Forced to tier 2**, whatever the score: `gate_or_harness_path`, `flowworks_or_live`, `past_audit_failed`,
  `reopened_before`, `owner_words_after_close`, `finding_against_item`. A change to the gates themselves, a live
  FlowWorks claim, or anything the owner spoke on after the close is never passed by code.
- **Risky slice**: OPEN claims scoring at or above the 75th percentile of OPEN scores (`SLICE_QUANTILE`) and above 0.
  Ties at the cut go in together, because tied scores carry the same flags. In the cold window the cut was 3.3,
  which is exactly one `no_check_evidence` flag.
- The rest pass on rank (**PASS1**).

## 4. Tier 2: AI judgment

- **Who gets an AI verdict:** the risky slice, plus a calibration slice of 1 in 10 of PASS0 and PASS1 claims
  (`CALIB_EVERY`). The calibration sample is seeded by day and picked by code. The judge is not told which claims
  are calibration.
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
| tier of each claim | T0_BOUNCE / T0_PASS / T1_PASS / T2_RISK, plus the `calibration` flag | `D:\ClaudeWork\rimmandrake\arbiter\tiers.json` (one file per batch run of `arbiter_tiers.py`, kept as `tiers_<ts>.json`) | code, before each Arbiter batch |
| verdict | the Arbiter's class per claim, with tier, interim reviewer verdict and evidence paths | `D:\ClaudeWork\rimmandrake\arbiter\verdicts.jsonl` (exists in `arbiter.md`), adding a field `tier` | the Arbiter |
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

### Tier mix (MEASURED)

Cold run of `arbiter_tiers.py --days 7` over 816 closes, 2026-10-20T15:21Z to 2026-10-27. Output:
`D:\ClaudeWork\rimmandrake\arbiter_tiers\tiers_cold_7d.json`.

| tier | claims | share |
|---|---|---|
| T0 BOUNCE | 25 | 3.1% |
| T0 PASS | 8 | 1.0% |
| T1 PASS on rank | 485 | 59.4% |
| T2 risky slice | 298 | 36.5% |
| **AI verdicts (T2 + calibration)** | **347** | **42.5%** |

How to read it:
- Tier 0 decides 4% today, because 94% of closes record no verify event. That is the gap in §2.
- The rank, not the gates, carries the saving. PASS1 rests on the pre-screen's precision, which is UNMEASURED; the
  calibration slice measures it.
- Of the 298 T2 claims, 75 are forced by a flag. The other 223 cross the score cut, nearly all through
  `no_check_evidence`.

Limits of the cold run:
- G4 looks at disk today, so evidence deleted since the close reads as FAIL. Only 1 claim failed G4.
- G5 accepts reviews made after the close.
- Closes include OWNER closes (46) and non-code kinds. The live Arbiter would take the same stream.

### Simulator prediction (ASSUMED; rests on assumptions)

Script: `D:\ClaudeWork\rimmandrake\arbiter_tiers\sim_tiered.py`. It is a scratch subclass of `Sim`, because the sim's
params have no coverage knob.

Setup:
- Base: the `isolate` setup (v3.2 + Arbiter), under quotas, 240 members, both structures.
- AI share 0.425 is MEASURED.
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

1. Advisory week. Before each batch, `arbiter_tiers.py` writes `tiers.json`, and the Arbiter judges T2 and
   calibration claims. Gate results and bounces are logged, but the interim GPT reviewer still gates closes (A-1).
   The module is not wired into `role_launch.py` yet; that is a Dispatcher change for its owner.
2. Build missing gates 1-5 as their own items. Each new gate shifts claims from T1/T2 into T0.
3. Measure (§5). Re-run the sim on the measured values. The Conductor carries the result to the owner. Binding is his
   switch, as before.
