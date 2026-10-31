#!/usr/bin/env python3
"""arena_analysis.py - the trial's stopping rule, committed before day 1 (ARENA_ANALYSIS_BUILD_RULE_BEFORE_RACE).

design/RimMandrake/architecture_switch_harness_2026-10-29.md section 4.1 (rule), 3.3 (measures), 3.5 (power),
1.7 (event log), 1.8 / testpilot_merged_2026-10-29.md 2.3 (a different agent tests promptly).

    python3 src/RimMandrake/Utils/arena/arena_analysis.py run --spend SPEND.json [--hard-cap ISO] [--final]
            [--seed N] [--draws N] [--gpt-to-ite F] [--gpt-est-in-to-ite F] [--gpt-est-out-to-ite F]
            [--claude-ite-scale F] [--claude-model-weight FAMILY=W ...] [--claude-token-weight FIELD=W ...]
            [--raw-dir DIR] [--allow-untrusted] [--blind SALT] [--out OUT.json]

Prints one JSON report: a verdict per 5-task block and a final verdict, each one of
    DECIDE_FOR_X | FUTILE(X) | TIE(simpler wins) | CONTINUE | DISQUALIFIED(X, reason) | HARD_CAP_PICK(X)
    | HARD_CAP_NO_DIFFERENCE(control stays) | CUT_SHORT_UNDECIDED(trial cut before the newest era) | UNMEASURED(reason)
plus per-arm intervals and every disqualification condition as VIOLATED / CLEAN / VACUOUS / UNMEASURED.
Exit status: 0 a verdict, 3 UNMEASURED, 4 CUT_SHORT_UNDECIDED (the trial ended before the newest era was compared).

WHAT IT READS (only fields some harness code writes, or the section 1.7 schema names):
  - the per-arm event logs. Default: arena_eventlog.report()+verify() (signed, anchored); an arm the report refuses,
    with any rejected/undecodable line, or not `trusted` (no ledger anchor + witness) is UNMEASURED unless
    --allow-untrusted. --raw-dir reads unsigned <arm>.jsonl files (selftests, dry runs): any unparseable line, a record
    missing ts/arm/event or with a zoneless ts makes that arm UNMEASURED.
  - judge events: task, verdict ('accept' | 'reject' | 'invalid'; the LAST by event time counts, as
    arena_eventlog.accepted_tasks), ts, sha. A task is COMPLETED when its last judge verdict is accept or reject.
  - the frozen task specs <arena>/tasks/<id>.json: kind (arena_tasks.KINDS) and size (1/2/4 = points).
  - TOKENS, from a spend file (--spend, schema arena_task_spend/2, written by arena_spend.py), never from the record
    `ite` field: {"schema", "window", "logs", "blocking", "arms": {arm: {task: row}}, "overhead", "flags"}, row = {"claude": {model: {input,
    cache_read, cache_write_5m, cache_write_1h, output}}, "gpt": {tokens, in_est, out_est, ...}, "ambiguous_calls",
    "claude_ite" (derived, IGNORED here)}. Owner ruling (ARENA_METER_BUILD_SPEND_BY_CLONE_PATH, 2026-10-30) and
    Conductor refinement: RAW Claude tokens per model and RAW GPT tokens are stored separately and THIS script weights:
        claude = CLAUDE_ITE_SCALE * sum_model CLAUDE_MODEL_WEIGHT[family(model)] * sum_f CLAUDE_TOKEN_WEIGHT[f]*n_f
        total_ite_mixed = claude + GPT_TO_ITE*gpt.tokens + GPT_EST_IN_TO_ITE*gpt.in_est + GPT_EST_OUT_TO_ITE*gpt.out_est
    (named constants, overridable on the command line, so a new conversion needs no re-metering; the defaults
    reproduce sim/spend_census's ITE). Refused (UNMEASURED for that task): a row with no raw counts (derived or merged
    total only), a row missing its claude or gpt section, a gpt section missing tokens/in_est/out_est, a claude model
    entry missing any raw field (the meter always writes them all: a missing field is never read as 0), a Claude model
    of no known family carrying tokens, an unweighted token field, a task whose calls
    overlapped another task's span (ambiguous_calls > 0), a task with a metered call whose raw count was invalid
    (invalid_calls > 0), a claude or gpt section present but not a dict, and any bool/negative/non-finite/overflowing count. The
    WHOLE spend file is refused (spend_doc_problem: UNMEASURED) when its `blocking` list is not empty (the meter lost
    spend or may have put it on the wrong arm), when its `logs` binding (record count + digest per arm) differs from
    the logs analysed (stale: the log moved on after metering), or when its `window` does not cover every analysed
    record (and the report then carries no per-block verdicts: `blocks_withheld` counts them). A task whose LAST judge
    event (by time, or among live lane-"judge" events by append order) is
    arena_judge.py's pending marker (detail.pending: a judgment started and its verdict was never appended) makes its
    arm UNMEASURED, as do live judge events whose append order and time order disagree (a clock ran backwards). Any record `ite` is ignored, counted in
    `merged_ite_records`.

THE MODEL (all small-n safe: exact conjugate posteriors, Monte Carlo FROM the posterior, fixed seed; no bootstrap):
  - log tokens per completed task: y[a,t] = c + mu[a] + tau[t] + e, e ~ N(0, s2); normal-inverse-gamma conjugate
    prior (c flat-ish, mu[a] ~ N(m[a], s2*V0a), tau[t] ~ N(0, s2*V0t), s2 ~ IG(A0, B0)). Replay runs the same task in
    every arm, so tau pairs each task with itself. The task block is eliminated exactly (Schur complement), so the
    posterior of (c, mu) given s2 is an exact multivariate normal and s2 an exact inverse gamma.
  - log time-to-acceptance (first assign, else first pass_start -> the accepting judge event), the same model.
    REPORTED ONLY: the section 4.1 rules do not use it.
  - acceptance per arm: Beta(prior) x binomial (completed tasks, accepted) -> exact Beta posterior.
  - accepted points per token, X over Y: (theta[X] / theta[Y]) * exp(mu[Y] - mu[X]).
  - priors, weak and centred on the simulator: m[ralph_a] = ln(1/RALPH_A_CAPACITY) (0.5x v3's capacity per token
    = twice the tokens per task), m[others] = 0, prior SD ARM_PRIOR_SD = 1.0 in log units at the reference sigma;
    acceptance Beta centred on the v2 first-try pass share 0.64 with weight 2.
THE RULE (section 4.1, thresholds are the owner's; module constants, never tuned here):
  - checked after every block of BLOCK=5 completed tasks per arm in contention (block k uses each arm's first 5k
    completions; an arm dropped for futility keeps the completions it had);
  - DISQUALIFIED(X) at any time, minimum exempt (conditions below);
  - nothing else may fire until EVERY arm in contention has >= MIN_TASKS=10 completed tasks over >= MIN_KINDS=2
    kinds: such a block is UNMEASURED(below minimum);
  - DECIDE_FOR_X: P(eff X >= 1.25 x the best other non-disqualified arm) > 0.95 AND P(accept[control] - accept[X]
    >= 0.10) < 0.2 (control = v3; no control data -> no decision);
  - TIE: P(|eff1/eff2 - 1| < 0.15) > 0.9 for the two leading arms in contention (by posterior mean log eff) -> the
    simpler of the two wins, order ralph_a < ralph_c < trio < v3c < v3;
  - FUTILE(X), X not the control: P(eff X >= 1.1 x control) < 0.05 -> X gets no new tasks;
  - ERA GATE (ARENA_STOP_RULE_HOLD_DECIDE_TILL_NEWEST; Conductor ruling 2026-10-30, owner authority): planners run
    tasks oldest first (sibling order, ARENA_PLANNERS_ENFORCE_SIBLING_ORDER), so an early look sees only old tasks
    and an arm x era effect can fire a false DECIDE from that prefix. The trial's tasks (--trial-tasks; default the
    committed list trial_tasks.json, N tasks (default 50, arena_trial.py --n) over all three eras, arena_trial.py) are ranked by `chrono`
    (`git rev-list --count base_sha`, --era-repo) into ERAS=3 bins, equal keys in one bin at the tie's upper rank. A
    look at which some arm in contention has not COMPLETED every task of the newest bin may neither stop nor drop: a
    would-be DECIDE_FOR_X, TIE, decision-blocked UNMEASURED or FUTILE is reported as verdict CONTINUE with `held` (the
    would-be verdict, its detail, the arms FUTILE would drop, the newest-era tasks each arm still lacks), and the
    trial goes on (FUTILE held too: ARENA_FUTILE_GATE_FIX_OLD_TASK_DROPS, Conductor ruling 2026-10-30). A task with
    no chronology key leaves the gate UNMEASURED: every stop and drop is held, and the end of the trial is UNMEASURED.
    Under the oldest-first order the gate therefore opens only at the full trial size: decisions land there, never
    earlier.
    THE FINAL LOOK: at the end of the trial (--final, a record past the hard cap, or the pool exhausted: every arm
    in contention has completed every trial task) with no stop, the rule is applied once more on the final snapshot,
    GATED: only if every kept arm has completed the whole newest era, and only if that snapshot is not exactly the
    data the last block looked at. A DECIDE/TIE/UNMEASURED there is the final verdict (detail.final_look); otherwise
    the hard-cap clause below, in which an arm short of the newest era is not a candidate (with the control short of
    it, none is). A trial cut short of the newest era, or an arm gone silent before it, is never decided on its
    older prefix (ARENA_FINAL_LOOK_FIX_UNGATED_AT_CAP).
  - HARD CAP: nothing fired and either --final is given, a record is later than --hard-cap (end of day 3; records
    after it are ignored), or the pool is exhausted (no further block can exist). Deterministic: the wall clock is never read. Clause added by the Conductor 2026-10-30
    (owner authority): from the final posterior, walk the simpler-arm order (control excluded) and pick the FIRST arm
    with P(accept[control] - accept[X] >= HARDCAP_ACCEPT_MARGIN=0.10) < HARDCAP_ACCEPT_P=0.2 AND P(accepted points
    per token X < HARDCAP_EFF_RATIO=0.9 x control) < HARDCAP_EFF_P=0.2 (both strict) and no non-exempt UNMEASURED
    disqualification check: HARD_CAP_PICK, detail.winner = X. None qualifies: HARD_CAP_NO_DIFFERENCE, detail.winner
    = the control (the control stays). CUT SHORT (ARENA_CUT_TRIAL_FIX_SAYS_NO_DIFFERENCE): when the trial ends with
    the control, or every other kept arm, short of the newest era, the verdict is CUT_SHORT_UNDECIDED (detail.winner
    None): nothing was compared on the newest era, so "no difference" would be false. An arm short of the newest era
    (cut or silent) is skipped by the final look, which runs on the arms that finished; it never blocks their look.
    The wall clock is never read, so a stuck arm leaves the trial CONTINUE until the driver re-runs with --final at the
    end of its budget (the driver MUST do so). Every candidate's two probabilities and 90% intervals are in detail.candidates,
    the per-arm intervals alongside. A futile arm is a candidate, on its frozen data.
  - CONTROL: a decision, TIE or hard-cap pick needs the control. The first block (with two or more arms in
    contention) at which the control is absent or already disqualified stops the trial UNMEASURED and carries no
    comparison verdict. A control disqualified only after the last block: final verdict UNMEASURED (never CONTINUE,
    never "no difference", never a hard-cap pick); with fewer than two survivors the verdict stays DISQUALIFIED (a
    non-decision naming the violation).
  - A decision needs the winner's OWN disqualification checks measured: a DECIDE_FOR_X or TIE won by X while X has an
    UNMEASURED check not in DQ_EXEMPT stops the trial as UNMEASURED (the checks are whole-trial, so more data cannot
    measure them).
  - CHRONOLOGY: block k sits at the time the last arm in contention reaches 5k completions. Violations are walked in
    time order first: an arm that violated before that time, or while it was still being waited for, leaves at its
    violation time and the block time is recomputed without it (block times never go backwards). An arm short of 5k
    with no violation is waited for. Fewer than two arms left in contention: CONTINUE with a note (no automatic
    winner). After a stop, later violations are reported (`violations_after_stop`), not applied; with no stop, any
    violation disqualifies. Each arm's reasons are split by each condition's own first time.
  - final intervals come from the trial's own snapshot: the stopping block's data, or (no stop) all data with each
    futile arm frozen where it was dropped. No stop and fewer than two measured arms survive disqualification:
    DISQUALIFIED (or UNMEASURED), never a hard-cap verdict; a live arm below the minimum: UNMEASURED.
FAIL CLOSED: no arms, fewer than two measured arms, an UNMEASURED arm anywhere in the roster, a completed task with
no frozen spec (kind in arena_tasks.KINDS, int size 1/2/4) or no spend row, zero or overflowing tokens, a judge record
with no task or an unknown verdict -> UNMEASURED, never a decision.

DISQUALIFICATION CONDITIONS, AND WHAT THE LOG CAN SHOW:
  publish   a judge event (the judge reads only published arena/* work) on (task, sha) with no earlier gate event
            verdict 'pass' on the same task and sha (shas of >= 12 hex; a shorter prefix never matches). A judge event
            with no usable sha or task: UNMEASURED. Publication that never
            reached the judge is not in the log (arena.py prepush alarms are not arm events): not seen here.
  scope     a gate event whose detail.steps.scope is FAIL (a changed path outside the task area or forbidden).
            Only edits that reached the gate are seen; no gate event, or a scope status other than PASS/FAIL:
            UNMEASURED.
  lane      a live_take (verdict ok) whose hold (same lane and run_id, up to its live_release) had no canary event.
            An open hold with no canary yet is `pending`, not a violation. A take with no lane or run_id:
            UNMEASURED. No live_take: VACUOUS.
  tester    per build stream (run_id minus its trailing pass counter, e.g. ralph_c.<member>.): a build pass_start
            (detail.role 'build') before the first test_start, by a DIFFERENT agent (arena_eventlog's matching and
            normalisation), of the stream's latest earlier build_end. A proven violation stands; otherwise build
            records with no run_id, or a build_end with no earlier build pass_start of its run: UNMEASURED.
  ruling    breaking a standing ruling: the event log records no ruling check. ALWAYS UNMEASURED.
  An UNMEASURED condition never passes silently: every verdict lists the arms and conditions that were unmeasured
  (`dq_unmeasured`). EXEMPTION, stated in full (DQ_EXEMPT): only `ruling`, because it is UNMEASURED for every arm in
  every trial (requiring it would forbid every decision); it stays listed, and standing rulings are enforced by review.
  Every other check of the winning arm must be measured (`dq_blocking`) or there is no decision; a VIOLATED check
  that also had unidentifiable records carries `unmeasured` and blocks too (its violation may be dated after the
  decision). Only the WINNER's
  checks gate: an unmeasured check of a losing arm or of the control is listed, not blocking.

LIMITS, STATED PLAINLY:
  - ORDER IS NOT SIMULATED: every MEASURED number below (and testpilot_sim) assumes exchangeable tasks, with no task
    order, era or arm x era term; the era gate's effect on them is not measured there (fixtures put the newest era
    first, so the gate opens early and those numbers still describe the rule's other parts). The confound and the
    final-look remedy were measured separately on assumed effects (item ARENA_STOP_RULE_HOLD_DECIDE_TILL_NEWEST).
    The report carries this as era_gate.limit. The old 24-37 tasks/arm forecast is DEAD: planners run oldest first,
    so the gate holds every stop until the newest era is in and decisions land only at the full trial size N. That
    fits the budget only with a trial of about 50 tasks or fewer, hence the explicit default list (trial_tasks.json,
    arena_trial.py; ARENA_TRIAL_TASKS_FIX_DEFAULT_ALL_FROZEN).
  - `judge` events are written by arena_judge.py (`judge` command, signed, lane "judge") and per-task spend by
    arena_spend.py, which attributes each metered call to the task whose signed-event span (one execution of a
    (run_id, task): first event to pass_end) contains it. Attribution is BY TIME: a call whose meter clock disagrees
    with the event clock, or an execution whose events stop early, can put a call on the wrong task or in overhead
    with no signal here (GPT review r1 #1; residual until calls carry a task/execution key). A call inside spans of two different tasks of one arm (concurrent members, e.g.
    ralph_c) is AMBIGUOUS and makes those tasks UNMEASURED; calls outside every span are reported as `overhead` and are
    NOT in the efficiency. GPT real tokens are a total (codex reports no in/out split), so GPT_TO_ITE weights them
    flat; only estimated GPT tokens carry an in/out split.
  - Points per token assumes acceptance is independent of task size within an arm and that arms draw from the same
    task pool (true for replay); a size-acceptance interaction is not modelled.
  - Tokens of tasks never completed (all judge verdicts invalid, or never judged) are not in the efficiency.
  - The analyst-blinding of section 3.4 is only a label mask (--blind SALT hashes arm names in the output until a
    stop fires); the rule itself needs arm identity for the control and the simpler-arm order.
  - Monte Carlo error at DRAWS=4000 is about 0.0035 at a probability near 0.95; a probability within that of a
    threshold can flip with the seed. Same log + seed + draws = same verdict.
  - MEASURED (selftest_arena_analysis.py --calib / --power, 2026-10-30; numbers reported, thresholds NOT tuned):
    null, 3 equal arms (trio/v3c/v3), accept 0.64, sigma_d 0.8, up to 40 tasks/arm, 8 looks: false DECIDE 7/1000
    (0.7%, 1000 draws) and 4/400 (1.0%, 4000 draws); no TIE; some arm FUTILE in 40% of null trials, which is the rule
    doing its job (an equal arm cannot beat the control by 10%), not a false alarm.
    POWER, 2 arms, one 1.5x more efficient (tokens/1.5), accept 0.64 both, sigma_d 0.8: DECIDE by 25 tasks/arm in
    28%, by 35 in 36%, by 40 in 40%, by 60 in 50% (1000 seeds). The rule does NOT reliably decide a 1.5x difference
    by 24-37 tasks per arm: the 1.25x bar at P > 0.95 leaves ln(1.5/1.25) = 0.18 of margin, and the binomial noise
    in the accept rate at p = 0.64 alone gives the log-efficiency difference an SD near 0.17 at 37 tasks per arm.
    Equal arms practically never TIE inside 40 tasks per arm for the same reason (a 15% band at P > 0.9 needs an SD
    near 0.09).
    HARD-CAP PICK (selftest_arena_analysis.py --hardcap 1000, 2026-10-30; --final at 40 tasks/arm, accept 0.64 unless
    stated, sigma_d 0.8, 1000 seeds each, 1000 draws; thresholds NOT tuned):
      3 equal arms (trio/v3c/v3): pick 496 (trio 343, v3c 153 when trio narrowly failed), control stays 497, false
        DECIDE 7 (trio 6, v3c 1). Half the time an equal simpler arm is NOT picked: P(eff < 0.9x) < 0.2 needs a log-efficiency SD near
        0.12, and 40 tasks give 0.17 or more (above), so "not credibly worse" is often unproven between equal arms.
      trio truly 1.5x: DECIDE_FOR_trio 386 + pick 206 = trio 592; control stays 408; no wrong stop.
      WRONG PICKS (a truly worse simpler arm picked): trio 1.5x LESS efficient: 13 picks + 2 false DECIDE (1.5%);
        trio accept 0.49 vs 0.64: 39 picks + 8 DECIDE (4.7%).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_eventlog as L  # noqa: E402
import arena_tasks as A  # noqa: E402

# ---------------------------------------------------------------- the rule (owner's thresholds; section 4.1)
BLOCK = 5
MIN_TASKS = 10
MIN_KINDS = 2
DECIDE_RATIO = 1.25
DECIDE_P = 0.95
ACCEPT_MARGIN = 0.10
ACCEPT_P = 0.2
FUTILE_RATIO = 1.1
FUTILE_P = 0.05
TIE_BAND = 0.15
TIE_P = 0.9
SIMPLER = ("ralph_a", "ralph_c", "trio", "v3c", "v3")
# day-3 hard-cap clause (Conductor 2026-10-30): when nothing fired by the cap, the simplest arm not credibly worse
HARDCAP_ACCEPT_MARGIN = 0.10   # accept rate worse than control by at least this ...
HARDCAP_ACCEPT_P = 0.2         # ... with probability below this
HARDCAP_EFF_RATIO = 0.9        # accepted points per token below this x control ...
HARDCAP_EFF_P = 0.2            # ... with probability below this
CONTROL = "v3"
# era gate (ARENA_STOP_RULE_HOLD_DECIDE_TILL_NEWEST, Conductor ruling 2026-10-30, owner authority): the trial's tasks are
# split into ERAS chronological bins by their `chrono` key; no decision before every arm in contention has completed
# every task of the newest bin
ERAS = 3
CUT_SHORT = "CUT_SHORT_UNDECIDED"   # the trial ended before the newest era was compared: no verdict on it
TRIAL_DEFAULT = HERE / "trial_tasks.json"   # the committed trial population (arena_trial.py build)

# ---------------------------------------------------------------- priors (weak, centred on the simulator)
RALPH_A_CAPACITY = 0.5         # Ralph section 10: ralph_a at 0.5x v3's capacity per token
ARM_PRIOR_SD = 1.0             # log units, at the reference sigma
TASK_PRIOR_SD = 3.0            # log units: task sizes differ a lot
SIGMA_REF = 0.8 / math.sqrt(2)  # sigma_d 0.8 (section 3.5 upper assumption) = sqrt(2) x residual sigma
IG_A0, IG_B0 = 1.0, 0.25
C_PREC = 1e-6                  # intercept prior precision (flat)
ACCEPT_PRIOR_MEAN, ACCEPT_PRIOR_WEIGHT = 0.64, 2.0

# ---------------------------------------------------------------- token conversion (owner ruling 2026-10-30)
SPEND_SCHEMA = "arena_task_spend/2"
# Claude model family -> Opus-input-equivalent weight (sim/spend_census.MODEL_X), matched as a substring of the
# lower-cased model id. A model of no listed family that carries tokens is REFUSED, never silently weighted.
CLAUDE_MODEL_WEIGHT = {"opus": 1.0, "sonnet": 0.6, "haiku": 0.2}
# raw Claude token field -> weight relative to one input token (spend_census.ite)
CLAUDE_TOKEN_WEIGHT = {"input": 1.0, "cache_read": 0.1, "cache_write_5m": 1.25, "cache_write_1h": 2.0,
                       "output": 5.0}
CLAUDE_ITE_SCALE = 1.0
GPT_TO_ITE = 1.0               # raw codex tokens -> ITE: OPEN owner question; 1.0 matches spend_census's 1:1 sum
GPT_EST_IN_TO_ITE = 1.0        # estimated GPT tokens (no usage line): spend_census.gpt_ite_of = in + 5*out
GPT_EST_OUT_TO_ITE = 5.0
GPT_FIELDS = {"tokens": "gpt_tokens", "in_est": "gpt_in_est", "out_est": "gpt_out_est"}
GPT_INFO_FIELDS = ("calls", "est_calls")


def default_conv():
    return {"claude_model": dict(CLAUDE_MODEL_WEIGHT), "claude_token": dict(CLAUDE_TOKEN_WEIGHT),
            "claude_scale": CLAUDE_ITE_SCALE, "gpt_tokens": GPT_TO_ITE, "gpt_in_est": GPT_EST_IN_TO_ITE,
            "gpt_out_est": GPT_EST_OUT_TO_ITE}

DRAWS = 4000
SEED = 20261030
JUDGE_DONE = ("accept", "reject")
JUDGE_ALL = ("accept", "reject", "invalid")


# ================================================================ small linear algebra (stdlib)

def _chol(m):
    n = len(m)
    lo = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = m[i][j] - sum(lo[i][k] * lo[j][k] for k in range(j))
            if i == j:
                if s <= 0:
                    raise ValueError("matrix not positive definite")
                lo[i][j] = math.sqrt(s)
            else:
                lo[i][j] = s / lo[j][j]
    return lo


def _inv_spd(m):
    n = len(m)
    lo = _chol(m)
    inv = [[0.0] * n for _ in range(n)]
    for c in range(n):
        e = [1.0 if i == c else 0.0 for i in range(n)]
        z = [0.0] * n
        for i in range(n):
            z[i] = (e[i] - sum(lo[i][k] * z[k] for k in range(i))) / lo[i][i]
        x = [0.0] * n
        for i in range(n - 1, -1, -1):
            x[i] = (z[i] - sum(lo[k][i] * x[k] for k in range(i + 1, n))) / lo[i][i]
        for i in range(n):
            inv[i][c] = x[i]
    return inv


def _matvec(m, v):
    return [sum(a * b for a, b in zip(row, v)) for row in m]


# ================================================================ the two-way normal-inverse-gamma model

def nig_fit(obs, arms, prior_mean):
    """obs: [(arm, task, y)]. -> posterior of (c, mu[arms]) with tau eliminated exactly, or None if no obs.
    Returns {arms, mean (c, mu...), chol (of the covariance factor), an, bn, n}."""
    if not obs:
        return None
    k = len(arms) + 1
    idx = {a: i + 1 for i, a in enumerate(arms)}
    v0a = (ARM_PRIOR_SD / SIGMA_REF) ** 2
    v0t = (TASK_PRIOR_SD / SIGMA_REF) ** 2
    q = [[0.0] * k for _ in range(k)]
    b = [0.0] * k
    q[0][0] = C_PREC
    m0q = 0.0
    for a in arms:
        q[idx[a]][idx[a]] += 1.0 / v0a
        b[idx[a]] += prior_mean.get(a, 0.0) / v0a
        m0q += prior_mean.get(a, 0.0) ** 2 / v0a
    tasks, yy = {}, 0.0
    for a, t, y in obs:
        i = idx[a]
        for u in (0, i):
            for w in (0, i):
                q[u][w] += 1.0
            b[u] += y
        rec = tasks.setdefault(t, {"n": 0.0, "qs": [0.0] * k, "b": 0.0})
        rec["n"] += 1.0
        rec["qs"][0] += 1.0
        rec["qs"][i] += 1.0
        rec["b"] += y
        yy += y * y
    s = [row[:] for row in q]
    r = b[:]
    for rec in tasks.values():
        qtt = 1.0 / v0t + rec["n"]
        qs = rec["qs"]
        for u in range(k):
            r[u] -= qs[u] * rec["b"] / qtt
            for w in range(k):
                s[u][w] -= qs[u] * qs[w] / qtt
    s_inv = _inv_spd(s)
    mn = _matvec(s_inv, r)
    mqm = sum(x * y for x, y in zip(mn, b))
    for rec in tasks.values():
        qtt = 1.0 / v0t + rec["n"]
        mt = (rec["b"] - sum(x * y for x, y in zip(rec["qs"], mn))) / qtt
        mqm += mt * rec["b"]
    an = IG_A0 + len(obs) / 2.0
    bn = IG_B0 + 0.5 * max(yy + m0q - mqm, 0.0)
    return {"arms": list(arms), "mean": mn, "chol": _chol(s_inv), "an": an, "bn": bn, "n": len(obs)}


def nig_draw(fit, rng):
    """One exact posterior draw of {arm: mu[arm]} (intercept dropped: only contrasts are used)."""
    s2 = 1.0 / rng.gammavariate(fit["an"], 1.0 / fit["bn"])
    sd = math.sqrt(s2)
    z = [rng.gauss(0.0, 1.0) for _ in fit["mean"]]
    lz = _matvec(fit["chol"], z)
    th = [m + sd * x for m, x in zip(fit["mean"], lz)]
    return {a: th[i + 1] for i, a in enumerate(fit["arms"])}


def prior_means(arms):
    return {a: (math.log(1.0 / RALPH_A_CAPACITY) if a == "ralph_a" else 0.0) for a in arms}


# ================================================================ reading the log

def _ep(r):
    return L.ts_epoch(r.get("ts"))


def _tkey(x):
    return x.strip() if isinstance(x, str) else None


def load_raw(dirpath):
    """Unsigned <arm>.jsonl files -> {arm: {"recs": [...]} | {"unmeasured": why}}. Fails closed per arm."""
    out = {}
    for f in sorted(Path(dirpath).glob("*.jsonl")):
        arm = f.stem
        if arm == "harness" or arm in L.NON_ARENA_ARMS:     # critic calibration is not a competing arm
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            out[arm] = {"unmeasured": "unreadable log: %s" % e}
            continue
        recs, bad = [], None
        for n, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                r = json.loads(line)
                if not isinstance(r, dict) or not all(isinstance(r.get(k), str) for k in ("ts", "arm", "event")):
                    raise ValueError("record missing ts/arm/event")
                if r["arm"] != arm:
                    raise ValueError("record arm %r in %s.jsonl" % (r["arm"], arm))
                _ep(r)
            except ValueError as e:
                bad = "unparseable line %d: %s" % (n, str(e)[:120])
                break
            recs.append(r)
        out[arm] = {"unmeasured": bad} if bad else {"recs": recs}
    return out


def load_verified(p=None, token=None, external=None, allow_untrusted=False):
    """Signed logs through arena_eventlog.report(): refused / rejected-line / untrusted arms are UNMEASURED."""
    p = p or A.paths()
    rep = L.report(p, token, external)
    out = {}
    for arm, v in sorted(rep.items()):
        if arm.startswith("_") or arm in L.NON_ARENA_ARMS:     # critic calibration is not a competing arm
            continue
        if v.get("refused"):
            out[arm] = {"unmeasured": "eventlog refused: %s" % "; ".join(map(str, v["refused"]))[:300]}
        elif v.get("rejected") or v.get("undecodable_lines"):
            out[arm] = {"unmeasured": "%d rejected / %d undecodable line(s)" % (v.get("rejected", 0),
                                                                             v.get("undecodable_lines", 0))}
        elif not v.get("trusted") and not allow_untrusted:
            out[arm] = {"unmeasured": "untrusted log (%s)" % v.get("trust_note", "no ledger anchor")}
        else:
            out[arm] = {"recs": L.verify(p, arm, token)["accepted"]}
    return out


def load_tasks(p=None):
    p = p or A.paths()
    out = {}
    for f in sorted(Path(p["tasks"]).glob("*.json")):
        try:
            t = json.loads(f.read_text(encoding="utf-8"))
            out[t["id"]] = {"kind": t["kind"], "size": t["size"], "base_sha": t.get("base_sha")}
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return out


def chrono_keys(tasks, repo=None):
    """Sets tasks[id]["chrono"] = `git rev-list --count <base_sha>` in `repo` (default arena_tasks.REPO): the number of
    commits behind the task's base, so a task whose base descends from another's has the larger key (strictly, on
    any history). A task with no base_sha, or one git cannot count, gets no key: the era gate is then UNMEASURED and
    holds every decision until the final look (fail closed). -> {id: why} for the tasks left without a key."""
    import subprocess
    repo = str(repo or A.REPO)
    missing, memo = {}, {}
    for tid, spec in sorted(tasks.items()):
        b = spec.get("base_sha") if isinstance(spec, dict) else None
        if not (isinstance(b, str) and _HEX.match(b)):
            missing[tid] = "no base_sha"
            continue
        if b not in memo:
            try:
                r = subprocess.run(["git", "-C", repo, "rev-list", "--count", b], capture_output=True, text=True,
                                   timeout=60)
                memo[b] = int(r.stdout.strip()) if r.returncode == 0 else None
            except (OSError, ValueError, subprocess.SubprocessError):
                memo[b] = None
        if memo[b] is None:
            missing[tid] = "git cannot count base %s in %s" % (b[:12], repo)
        else:
            spec["chrono"] = memo[b]
    return missing


# ================================================================ per-arm extraction

def _count(v):
    """A raw token count: a non-bool finite number >= 0, else None."""
    try:
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(float(v)) or v < 0:
            return None
        return float(v)
    except OverflowError:
        return None


def model_family(model, weights):
    m = str(model).lower()
    hits = sorted((f for f in weights if f and f.lower() in m), key=len, reverse=True)
    if not hits or (len(hits) > 1 and len(hits[0]) == len(hits[1])):
        return None                        # no family, or two equally specific ones: refuse, never guess
    return hits[0]                         # the most specific family wins ('opus-4' over 'opus')


def task_tokens(row, conv):
    """A raw spend row -> total_ite_mixed, or (None, why). The derived claude_ite column is ignored: the weighting
    happens HERE from the raw per-model counts, with the factors in `conv` (default_conv())."""
    if not isinstance(row, dict):
        return None, "no spend row"
    claude, gpt = row.get("claude"), row.get("gpt")
    if not isinstance(claude, dict) and not isinstance(gpt, dict):
        return None, "spend row has no raw per-model counts (derived claude_ite / merged total only?)"
    for sec in ("claude", "gpt"):
        if sec in row and not isinstance(row[sec], dict):
            return None, "spend %s section is %s, not a dict" % (sec, type(row[sec]).__name__)
    # arena_spend.new_row() always writes BOTH sections, every GPT field and (per model) every raw Claude field, so a
    # missing one is a row the meter did not write: UNMEASURED, never read as 0 (ARENA_SPEND_ROW_HARDEN_MISSING_GPT_FIELD)
    for sec in ("claude", "gpt"):
        if sec not in row:
            return None, "spend row has no %s section (the meter always writes one)" % sec
    miss = [k for k in GPT_FIELDS if k not in gpt]
    if miss:
        return None, "spend gpt section is missing field(s) %s (never read as 0)" % miss
    for model, toks in claude.items():
        miss = [k for k in CLAUDE_TOKEN_WEIGHT if isinstance(toks, dict) and k not in toks]
        if miss:
            return None, "spend claude[%r] is missing raw field(s) %s (never read as 0)" % (model, miss)
    inv = row.get("invalid_calls", 0)
    if _count(inv) is None or inv > 0:
        return None, "spend has %r invalid metered call(s) (a bad raw count)" % (inv,)
    amb = row.get("ambiguous_calls", 0)
    if _count(amb) is None:
        return None, "spend ambiguous_calls=%r invalid" % (amb,)
    if amb > 0:
        return None, "%d metered call(s) overlapped another task's span (ambiguous attribution)" % amb
    tot = 0.0
    try:
        for model, toks in (claude or {}).items():
            if not isinstance(toks, dict):
                return None, "spend claude[%r] not a dict" % (model,)
            sub = 0.0
            for k, v in toks.items():
                if k not in conv["claude_token"]:
                    return None, "spend claude[%r] has unweighted token field %r" % (model, k)
                n = _count(v)
                if n is None:
                    return None, "spend claude[%r].%s=%r invalid" % (model, k, v)
                sub += conv["claude_token"][k] * n
            if sub == 0:
                continue
            fam = model_family(model, conv["claude_model"])
            if fam is None:
                return None, "spend claude model %r has tokens but no known family %s" % (
                    model, sorted(conv["claude_model"]))
            tot += conv["claude_scale"] * conv["claude_model"][fam] * sub
        if gpt is not None and not isinstance(gpt, dict):
            return None, "spend gpt not a dict"
        for k, v in (gpt or {}).items():
            if k in GPT_INFO_FIELDS:
                if _count(v) is None:
                    return None, "spend gpt.%s=%r invalid" % (k, v)
                continue
            if k not in GPT_FIELDS:
                return None, "spend gpt has unweighted field %r" % (k,)
            n = _count(v)
            if n is None:
                return None, "spend gpt.%s=%r invalid" % (k, v)
            tot += conv[GPT_FIELDS[k]] * n
    except OverflowError:
        return None, "converted tokens overflow"
    if not math.isfinite(tot):
        return None, "converted tokens overflow"
    if tot <= 0:
        return None, "zero tokens"
    return tot, None


def spend_log_binding(arm_logs):
    """{arm: {"n", "digest"} | {"unmeasured": True}}: what a spend doc was metered against. arena_spend.py writes it;
    spend_doc_problem() compares it with the logs being analysed, so stale spend (the log moved on) is refused."""
    out = {}
    for arm, lg in sorted((arm_logs or {}).items()):
        if not isinstance(lg, dict) or "recs" not in lg:
            out[arm] = {"unmeasured": True}
            continue
        blob = json.dumps(lg["recs"], sort_keys=True, default=str, separators=(",", ":"))
        out[arm] = {"n": len(lg["recs"]), "digest": hashlib.sha256(blob.encode("utf-8")).hexdigest()}
    return out


def spend_doc_problem(doc, arm_logs):
    """-> why the spend doc cannot be used with these logs, or None. Refuses: wrong schema; blocking meter problems
    (spend lost or possibly on the wrong arm); a doc metered against a different log (stale or partial); a meter
    window that does not cover every analysed record of an arm."""
    if not isinstance(doc, dict) or doc.get("schema") != SPEND_SCHEMA or not isinstance(doc.get("arms"), dict):
        return "spend file is not schema %s (write it with arena_spend.py)" % SPEND_SCHEMA
    blocking = doc.get("blocking")
    if not isinstance(blocking, list):
        return "spend file has no blocking list"
    if blocking:
        return "spend metering incomplete: %s" % "; ".join(str(b) for b in blocking[:5])
    bound, now = doc.get("logs"), spend_log_binding(arm_logs)
    if not isinstance(bound, dict):
        return "spend file is not bound to an event log (no logs binding)"
    for arm, b in now.items():
        if "digest" in b and bound.get(arm) != b:
            return "spend file is stale for arm %s: metered against %r, analysing %r" % (arm, bound.get(arm), b)
    win = doc.get("window")
    if not isinstance(win, dict):
        return "spend file has no meter window"
    try:
        since, until = float(win["since"]), float(win["until"])
        for arm, lg in (arm_logs or {}).items():
            ts = [_ep(r) for r in lg.get("recs", ())] if isinstance(lg, dict) else []
            if ts and not (since <= min(ts) and max(ts) < until):
                return "spend window [%s, %s) does not cover arm %s's records [%s, %s]" % (
                    since, until, arm, min(ts), max(ts))
    except (KeyError, TypeError, ValueError) as e:
        return "spend window unreadable: %s" % e
    return None


def analyse_spend_doc(arm_logs, tasks, doc, **kw):
    """analyse() on a whole spend doc: the doc must pass spend_doc_problem() against THESE logs, else UNMEASURED."""
    why = spend_doc_problem(doc, arm_logs)
    arms = doc.get("arms") if isinstance(doc, dict) and isinstance(doc.get("arms"), dict) else {}
    rep = analyse(arm_logs, tasks, arms, **kw)
    rep["spend_overhead"] = doc.get("overhead") if isinstance(doc, dict) else None
    rep["spend_flags"] = doc.get("flags") if isinstance(doc, dict) else None
    if why:
        # a refused doc yields no verdict anywhere: per-block verdicts computed from it are withheld, not reported
        rep["blocks_withheld"] = len(rep.get("blocks") or [])
        rep["blocks"] = []
        rep["final"] = {"verdict": "UNMEASURED", "why": why}
    return rep


def _spec_ok(spec):
    return (isinstance(spec, dict) and type(spec.get("size")) is int and spec["size"] in (1, 2, 4)
            and spec.get("kind") in A.KINDS)


def completions(recs, tasks, spend_arm, conv, cap=None):
    """-> (list of completed-task dicts sorted by completion time, problem or None). A judge record with no task or
    a verdict outside accept/reject/invalid makes the whole arm a problem (never silently dropped)."""
    seq = [r for r in L.ordered(recs) if cap is None or _ep(r) <= cap]
    last, start = {}, {}
    for r in seq:
        t = _tkey(r.get("task"))
        if r["event"] == "judge":
            if not t:
                return [], "judge record at %s has no task" % r.get("ts")
            if r.get("verdict") not in JUDGE_ALL:
                return [], "judge record at %s has verdict %r" % (r.get("ts"), r.get("verdict"))
            last[t] = r
        elif t and r["event"] in ("assign", "pass_start"):
            cur = start.get(t)
            if cur is None or (cur["event"] == "pass_start" and r["event"] == "assign"):
                start[t] = r
    # precedence must not rest on a clock alone (GPT review r2 #3). arena_judge.py appends its judge events live
    # (lane "judge"; never late imports), so among THOSE the last appended must also be the last by time, else the
    # clock ran backwards between judgments; and a pending marker that is the last appended is an unrecorded verdict
    # whatever its timestamp says. Other-lane judge records keep the late-import rule (event time decides).
    live_app, live_time = {}, {}
    for r in recs:
        if r.get("event") == "judge" and r.get("lane") == "judge" and (cap is None or _ep(r) <= cap):
            live_app[_tkey(r.get("task"))] = r
    for r in seq:
        if r["event"] == "judge" and r.get("lane") == "judge":
            live_time[_tkey(r.get("task"))] = r
    out = []
    for t, j in last.items():
        a = live_app.get(t)
        if a is not None and a is not live_time.get(t):
            return [], "task %s: its last live judge event by time is not its last appended (clock went backwards)" % t
        if a is not None and isinstance(a.get("detail"), dict) and a["detail"].get("pending") is True:
            j = a
        if isinstance(j.get("detail"), dict) and j["detail"].get("pending") is True:
            return [], "task %s: a judgment started at %s was never recorded (pending judge event is last)" % (
                t, j.get("ts"))
        if j.get("verdict") not in JUDGE_DONE:
            continue
        spec = tasks.get(t)
        if not _spec_ok(spec):
            return [], "completed task %s has no valid frozen spec (kind in KINDS, size 1/2/4)" % t
        tok, why = task_tokens((spend_arm or {}).get(t), conv)
        if tok is None:
            return [], "task %s: %s" % (t, why)
        tta = None
        if j["verdict"] == "accept" and t in start:
            m = (_ep(j) - _ep(start[t])) / 60.0
            tta = m if m > 0 else None
        out.append({"task": t, "t": _ep(j), "accepted": j["verdict"] == "accept", "kind": spec["kind"],
                    "points": spec["size"], "tokens": tok, "tta_min": tta})
    out.sort(key=lambda c: (c["t"], c["task"]))
    if not math.isfinite(sum(c["tokens"] for c in out)):
        return [], "the arm's token total overflows"
    return out, None


# ================================================================ disqualification

_HEX = re.compile(r"^[0-9a-f]{7,64}$")
SHA_MIN_PREFIX = 12   # an abbreviated sha shorter than this is not accepted as identifying a commit


def _sha(x):
    s = x.strip().lower() if isinstance(x, str) else ""
    return s if _HEX.match(s) else None


def _sha_eq(a, b):
    a, b = _sha(a), _sha(b)
    if not a or not b:
        return False
    if a == b:
        return True
    short, long_ = sorted((a, b), key=len)
    return len(short) >= SHA_MIN_PREFIX and long_.startswith(short)


def _also(res, unmeasured_why):
    """A VIOLATED check that ALSO had unidentifiable records keeps that fact: the violation may be dated after a
    decision, and until then the check was unmeasured (dq_blocking reads `unmeasured`)."""
    if unmeasured_why:
        res["unmeasured"] = unmeasured_why
    return res


def dq_publish(seq):
    judges = [r for r in seq if r["event"] == "judge"]
    if not judges:
        return {"status": "VACUOUS", "why": "no judge event"}
    gates = [(i, r) for i, r in enumerate(seq) if r["event"] == "gate" and r.get("verdict") == "pass"]
    viol, unid = [], 0
    for i, j in enumerate(seq):
        if j["event"] != "judge":
            continue
        if not _sha(j.get("sha")) or (len(_sha(j["sha"])) < SHA_MIN_PREFIX) or not _tkey(j.get("task")):
            unid += 1
            continue
        if not any(gi < i and _tkey(g.get("task")) == _tkey(j.get("task")) and _sha_eq(g.get("sha"), j["sha"])
                   for gi, g in gates):
            viol.append({"ts": j["ts"], "task": j.get("task"), "sha": j["sha"]})
    if viol:
        return _also({"status": "VIOLATED", "ts": viol[0]["ts"], "why": "judged (published) work with no earlier "
                      "gate pass", "evidence": viol[:5]}, unid and "%d judge event(s) with no usable sha or task" % unid)
    if unid:
        return {"status": "UNMEASURED", "why": "%d judge event(s) with no usable sha or task" % unid}
    return {"status": "CLEAN"}


def dq_scope(seq):
    gates = [r for r in seq if r["event"] == "gate"]
    if not gates:
        return {"status": "UNMEASURED", "why": "no gate event: no edit was scope-checked"}
    viol, unknown = [], 0
    for g in gates:
        steps = (g.get("detail") or {}).get("steps") if isinstance(g.get("detail"), dict) else None
        st = steps.get("scope") if isinstance(steps, dict) else None
        st = st.upper() if isinstance(st, str) else None
        if st == "FAIL":
            viol.append({"ts": g["ts"], "task": g.get("task"), "sha": g.get("sha")})
        elif st != "PASS":
            unknown += 1
    if viol:
        return _also({"status": "VIOLATED", "ts": viol[0]["ts"], "why": "gate scope FAIL: edit outside the task area",
                      "evidence": viol[:5]}, unknown and "%d gate event(s) whose scope step is not PASS or FAIL" % unknown)
    if unknown:
        return {"status": "UNMEASURED", "why": "%d gate event(s) whose scope step is not PASS or FAIL" % unknown}
    return {"status": "CLEAN"}


def _ident(x):
    return x.strip() if isinstance(x, str) and x.strip() else None


def dq_lane(seq):
    takes = [i for i, r in enumerate(seq) if r["event"] == "live_take" and r.get("verdict") == "ok"]
    if not takes:
        return {"status": "VACUOUS", "why": "no live_take"}
    viol, pending, unid = [], 0, 0
    for i in takes:
        key = (_ident(seq[i].get("lane")), _ident(seq[i].get("run_id")))
        if None in key:
            unid += 1
            continue

        def same(k):
            return (_ident(seq[k].get("lane")), _ident(seq[k].get("run_id"))) == key
        end = next((k for k in range(i + 1, len(seq)) if seq[k]["event"] == "live_release" and same(k)), None)
        stop = end if end is not None else len(seq)
        if any(seq[k]["event"] == "canary" and same(k) for k in range(i + 1, stop)):
            continue
        if end is None:
            pending += 1
        else:
            viol.append({"ts": seq[end]["ts"], "lane": key[0], "run_id": key[1]})
    if viol:
        return _also({"status": "VIOLATED", "ts": viol[0]["ts"], "why": "lane held and released with no canary",
                      "evidence": viol[:5]}, unid and "%d live_take(s) with no lane or run_id" % unid)
    if unid:
        return {"status": "UNMEASURED", "why": "%d live_take(s) with no lane or run_id" % unid}
    return {"status": "CLEAN", "pending_open_holds": pending} if pending else {"status": "CLEAN"}


def stream_of(run_id):
    r = _ident(run_id)
    return re.sub(r"\d+$", "", r) if r else None


def dq_tester(seq):
    builds = [i for i, r in enumerate(seq) if r["event"] == "build_end"]
    starts = [i for i, r in enumerate(seq) if r["event"] == "pass_start"
              and (r.get("detail") or {}).get("role") == "build"]
    if not builds and not starts:
        return {"status": "VACUOUS", "why": "no build"}
    # unidentifiable records are set aside and reported, never allowed to mask a violation proven elsewhere
    unid = [i for i in builds + starts if not stream_of(seq[i].get("run_id"))]
    builds = [i for i in builds if i not in unid]
    starts = [i for i in starts if i not in unid]
    orphan = [j for j in builds
              if not any(p < j and _ident(seq[p].get("run_id")) == _ident(seq[j].get("run_id")) for p in starts)]
    first = L._first_different_test(seq)      # {build index: first different-agent test_start index}
    viol = []
    for p in starts:
        st = stream_of(seq[p].get("run_id"))
        prev = [j for j in builds if j < p and stream_of(seq[j].get("run_id")) == st]
        if not prev:
            continue
        j = prev[-1]
        ti = first.get(j)
        if ti is None or ti > p:
            viol.append({"ts": seq[p]["ts"], "stream": st, "untested_build_task": seq[j].get("task"),
                         "build_sha": seq[j].get("sha")})
    if viol:
        return _also({"status": "VIOLATED", "ts": viol[0]["ts"],
                      "why": "new build pass before a different agent began testing the last candidate",
                      "evidence": viol[:5]},
                     (unid or orphan) and "%d build record(s) with no run_id; %d orphan build_end(s)" %
                     (len(unid), len(orphan)))
    if unid or orphan:
        return {"status": "UNMEASURED", "why": "%d build record(s) with no run_id (stream unknown); %d build_end(s) "
                "with no earlier build pass_start of the same run" % (len(unid), len(orphan))}
    return {"status": "CLEAN"}


def dq_ruling(_seq):
    return {"status": "UNMEASURED", "why": "the event log records no standing-ruling check"}


DQ_CHECKS = (("publish", dq_publish), ("scope", dq_scope), ("lane", dq_lane), ("tester", dq_tester),
             ("ruling", dq_ruling))
# A decision (DECIDE_FOR_X, a TIE won by X, a hard-cap pick of X) needs every one of X's OWN disqualification checks
# MEASURED (CLEAN or VACUOUS), except the checks listed here, each with its reason. UNMEASURED inputs never yield a
# decision (ARENA_WINNER_ENFORCE_MEASURED_DQ_CHECKS); this is the whole, stated exemption list.
DQ_EXEMPT = {
    "ruling": "structurally UNMEASURED: no harness code writes a standing-ruling check into the arm event log, so it "
              "is UNMEASURED for every arm in every trial; requiring it would make the rule unable to decide at all. "
              "Breaking a standing ruling stays a disqualification, enforced outside this script (review), and the "
              "check is still listed in dq_unmeasured on every verdict.",
}


def dq_blocking(dq):
    """{arm: [non-exempt UNMEASURED checks]} for arms with at least one: these arms may not be decided for. A VIOLATED
    check that also had unidentifiable records counts (its violation can be dated after the decision)."""
    out = {}
    for a, d in (dq or {}).items():
        v = [n for n, c in d.items() if (c["status"] == "UNMEASURED" or c.get("unmeasured")) and n not in DQ_EXEMPT]
        if v:
            out[a] = v
    return out


def disqualifications(recs, cap=None):
    seq = [r for r in L.ordered(recs) if cap is None or _ep(r) <= cap]
    return {name: fn(seq) for name, fn in DQ_CHECKS}


# ================================================================ posterior probabilities and the verdict

def _q(xs, p):
    s = sorted(xs)
    if not s:
        return None
    k = (len(s) - 1) * p
    lo, hi = int(math.floor(k)), int(math.ceil(k))
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def posterior(data, arms, seed, draws, control=None):
    """data: {arm: [completions]} -> draws of log efficiency and accept rate per arm (deterministic)."""
    control = control or CONTROL
    rng = random.Random(seed)
    obs = [(a, c["task"], math.log(c["tokens"])) for a in arms for c in data[a]]
    fit = nig_fit(obs, arms, prior_means(arms))
    a0 = ACCEPT_PRIOR_MEAN * ACCEPT_PRIOR_WEIGHT
    b0 = (1 - ACCEPT_PRIOR_MEAN) * ACCEPT_PRIOR_WEIGHT
    kn = {a: (sum(c["accepted"] for c in data[a]), len(data[a])) for a in arms}
    le = {a: [] for a in arms}
    th = {a: [] for a in arms}
    for _ in range(draws):
        mu = nig_draw(fit, rng)
        for a in arms:
            k, n = kn[a]
            t = rng.betavariate(a0 + k, b0 + n - k)
            th[a].append(t)
            le[a].append(math.log(max(t, 1e-300)) - mu[a])
    return {"le": le, "theta": th, "fit": fit, "kn": kn}


def rule_probs(post, contention, nondq, control=None):
    """Every probability the rule needs, from posterior draws (thresholds applied here)."""
    control = control or CONTROL
    le, th = post["le"], post["theta"]
    n = len(next(iter(le.values())))
    out = {"decide": {}, "accept_worse": {}, "futile": {}, "tie": None, "leaders": None}
    lr, lf, lt = math.log(DECIDE_RATIO), math.log(FUTILE_RATIO), TIE_BAND
    for x in contention:
        others = [y for y in nondq if y != x]
        if others:
            out["decide"][x] = sum(1 for i in range(n) if le[x][i] - max(le[y][i] for y in others) >= lr) / n
        if control in th:
            out["accept_worse"][x] = sum(1 for i in range(n) if th[control][i] - th[x][i] >= ACCEPT_MARGIN) / n
            if x != control:
                out["futile"][x] = sum(1 for i in range(n) if le[x][i] - le[control][i] >= lf) / n
    if len(contention) >= 2:
        lead = sorted(contention, key=lambda a: (-sum(le[a]) / n, a))[:2]
        a, b = lead
        out["leaders"] = lead
        out["tie"] = sum(1 for i in range(n) if abs(math.exp(le[a][i] - le[b][i]) - 1.0) < lt) / n
    return out


def simpler(a, b):
    if a not in SIMPLER or b not in SIMPLER:
        return None
    return a if SIMPLER.index(a) < SIMPLER.index(b) else b


def rule_verdict(probs, control_present, blocked=None):
    """-> (verdict, detail). Pure: thresholds compared to probabilities. Order: DECIDE, TIE, FUTILE, CONTINUE.
    blocked: {arm: [non-exempt UNMEASURED DQ checks]} (dq_blocking): a decision that would go to such an arm is
    UNMEASURED instead (its own disqualification was never measured)."""
    blocked = blocked or {}
    for x, p in sorted(probs["decide"].items()):
        if p > DECIDE_P:
            if not control_present or x not in probs["accept_worse"]:
                return "CONTINUE", {"note": "%s passes the efficiency test but the control's accept rate is "
                                            "UNMEASURED: no decision" % x}
            if probs["accept_worse"][x] < ACCEPT_P:
                if x in blocked:
                    return "UNMEASURED", {"why": "%s passes the decision test but its own disqualification check(s) %s "
                                                 "are UNMEASURED: no decision" % (x, blocked[x]),
                                          "arm": x, "dq_unmeasured": blocked[x], "p_decide": p}
                return "DECIDE_FOR_%s" % x, {"arm": x, "p_decide": p, "p_accept_worse": probs["accept_worse"][x]}
    if probs["tie"] is not None and probs["tie"] > TIE_P:
        a, b = probs["leaders"]
        w = simpler(a, b)
        if w is None:
            return "UNMEASURED", {"why": "tie between %s and %s but one is not in the simpler-arm order" % (a, b)}
        if not control_present:
            return "UNMEASURED", {"why": "TIE between %s and %s but the control is absent or disqualified: no "
                                         "reference, no decision" % (a, b), "p_tie": probs["tie"]}
        if w in blocked:
            return "UNMEASURED", {"why": "TIE would go to %s but its own disqualification check(s) %s are UNMEASURED"
                                         % (w, blocked[w]), "arm": w, "dq_unmeasured": blocked[w], "p_tie": probs["tie"]}
        return "TIE", {"leaders": [a, b], "winner": w, "p_tie": probs["tie"]}
    fut = sorted(x for x, p in probs["futile"].items() if p < FUTILE_P)
    if fut:
        return "FUTILE", {"arms": fut}
    return "CONTINUE", {}


def hardcap_pick(post, arms, control, blocked, missing=None):
    """Day-3 hard-cap clause: -> (winner, detail). Walk SIMPLER (simplest first, control excluded); pick the first arm
    present in `arms`, not in `blocked`, with P(accept rate worse than control by >= HARDCAP_ACCEPT_MARGIN) <
    HARDCAP_ACCEPT_P AND P(accepted points per token < HARDCAP_EFF_RATIO x control) < HARDCAP_EFF_P. None: control.
    missing: newest_era_missing over `arms`: an arm short of the newest era is never picked (a pick on older tasks
    alone is the order confound; ARENA_FINAL_LOOK_FIX_UNGATED_AT_CAP), and with the control short of it no arm is."""
    missing = missing or {}
    le, th = post["le"], post["theta"]
    if control not in th:
        return None, {"candidates": [], "picked": False, "why": "the control (%s) has no posterior: no pick" % control}
    n = len(th[control])
    lr = math.log(HARDCAP_EFF_RATIO)
    cands = []
    for a in [x for x in SIMPLER if x != control and x in arms] + sorted(x for x in arms if x not in SIMPLER and
                                                                         x != control):
        c = {"arm": a}
        if a not in SIMPLER:
            c["skipped"] = "not in the simpler-arm order"
        elif a in blocked:
            c["skipped"] = "own disqualification check(s) %s UNMEASURED" % blocked[a]
        elif control in missing:
            c["skipped"] = "the control has not completed the newest era (%d task(s)): no comparison on it" % \
                len(missing[control])
        elif a in missing:
            c["skipped"] = "has not completed the newest era (%d task(s)): not judged on older tasks alone" % \
                len(missing[a])
        d = [th[a][i] - th[control][i] for i in range(n)]
        r = [math.exp(le[a][i] - le[control][i]) for i in range(n)]
        c["p_accept_worse"] = sum(1 for i in range(n) if th[control][i] - th[a][i] >= HARDCAP_ACCEPT_MARGIN) / n
        c["p_eff_below"] = sum(1 for i in range(n) if le[a][i] - le[control][i] < lr) / n
        c["accept_diff_vs_control_90"] = [_q(d, 0.05), _q(d, 0.5), _q(d, 0.95)]
        c["eff_vs_control_90"] = [_q(r, 0.05), _q(r, 0.5), _q(r, 0.95)]
        c["qualifies"] = ("skipped" not in c and c["p_accept_worse"] < HARDCAP_ACCEPT_P
                          and c["p_eff_below"] < HARDCAP_EFF_P)
        cands.append(c)
    win = next((c["arm"] for c in cands if c["qualifies"]), None)
    return (win or control), {"candidates": cands, "picked": win is not None}


def arm_summary(post, data, arms, control=None):
    control = control or CONTROL
    out = {}
    le, th = post["le"], post["theta"]
    for a in arms:
        k, n = post["kn"][a]
        pts = sum(c["points"] for c in data[a] if c["accepted"])
        tok = sum(c["tokens"] for c in data[a])
        s = {"completed": n, "accepted": k, "kinds": sorted({c["kind"] for c in data[a]}),
             "accepted_points": pts, "tokens_total_ite_mixed": tok,
             "points_per_mtoken_observed": (pts / tok * 1e6) if tok else None,
             "accept_rate_90": [_q(th[a], 0.05), _q(th[a], 0.5), _q(th[a], 0.95)]}
        if control in le and a != control:
            r = [math.exp(x - y) for x, y in zip(le[a], le[control])]
            s["eff_vs_control_90"] = [_q(r, 0.05), _q(r, 0.5), _q(r, 0.95)]
        out[a] = s
    return out


def tta_summary(data, arms, control=None):
    control = control or CONTROL
    obs = [(a, c["task"], math.log(c["tta_min"])) for a in arms for c in data[a] if c["tta_min"]]
    per = {a: sum(1 for c in data[a] if c["tta_min"]) for a in arms}
    if control not in arms or per.get(control, 0) < 2:
        return {"status": "UNMEASURED", "why": "control has < 2 timed acceptances", "n": per}
    fit = nig_fit(obs, arms, {a: 0.0 for a in arms})
    rng = random.Random(SEED + 1)
    ds = {a: [] for a in arms if a != control}
    for _ in range(2000):
        mu = nig_draw(fit, rng)
        for a in ds:
            ds[a].append(math.exp(mu[a] - mu[control]))
    return {"status": "MEASURED", "n": per, "note": "reported only; not a section 4.1 rule input",
            "time_ratio_vs_control_90": {a: ([_q(v, 0.05), _q(v, 0.5), _q(v, 0.95)] if per[a] >= 2 else
                                             "UNMEASURED (< 2 timed acceptances)") for a, v in ds.items()}}


ERA_LIMIT = ("the stopping rule's simulators (selftest_arena_analysis.py --calib/--power/--hardcap, testpilot_sim) "
             "model exchangeable tasks: no task order, no era, no arm x era effect. Their false-DECIDE, power and "
             "hard-cap numbers are for that case only; the era gate is the remedy for the order confound measured "
             "separately (ARENA_STOP_RULE_HOLD_DECIDE_TILL_NEWEST: assumed effects, false DECIDE 9-27% under the "
             "chronological order vs about 0.5% shuffled; final-look-only about 0) and is not calibrated by them. "
             "Under the gate a decision lands only at the full trial size (oldest-first order), so the per-block "
             "power curves overstate early decisions; FUTILE is held by the same gate.")


def era_map(tasks):
    """-> (eras {id: 0..ERAS-1, oldest 0} or None, why). ERAS bins of the tasks ranked by `chrono`; tasks with equal
    keys share a bin, ranked at the LAST position of their tie (bin = floor(ERAS * (#tasks with a key <= k, minus 1)
    / n)): a tie straddling a cut goes UP, so the newest era is never smaller than an untied third (a tie at the 2/3
    cut used to leave it one task; ARENA_STOP_GATE_FIX_SMALL_LEFTOVERS). Any task without an int key: None."""
    keys = {t: s.get("chrono") if isinstance(s, dict) else None for t, s in tasks.items()}
    bad = sorted(t for t, k in keys.items() if type(k) is not int)
    if not keys:
        return None, "no trial tasks"
    if bad:
        return None, "%d trial task(s) have no chronology key (e.g. %s)" % (len(bad), bad[0])
    n = len(keys)
    srt = sorted(keys.values())
    import bisect
    return {t: min(ERAS - 1, ERAS * (bisect.bisect_right(srt, k) - 1) // n) for t, k in keys.items()}, None


def newest_era_missing(use, contention, newest):
    """{arm in contention: [newest-era tasks it has not completed in `use`]} for arms short of any (empty = gate open).
    newest None (no era map): every arm is short (the gate stays shut until the final look)."""
    if newest is None:
        return {a: ["(era map UNMEASURED)"] for a in contention}
    out = {}
    for a in contention:
        miss = sorted(newest - {c["task"] for c in use[a]})
        if miss:
            out[a] = miss
    return out


def held_kind(v):
    """A look's verdict that stops the trial on a would-be decision: what the era gate holds back."""
    return v.startswith("DECIDE_FOR_") or v in ("TIE", "UNMEASURED")


def gated(v):
    """What the era gate holds at a look short of the newest era: every stop (held_kind) AND a FUTILE drop, which
    judged on older tasks alone recreates the order confound (true winners dropped, all challengers emptied out;
    ARENA_FUTILE_GATE_FIX_OLD_TASK_DROPS, Conductor ruling 2026-10-30: the same gate, the simplest correct rule)."""
    return held_kind(v) or v == "FUTILE"


def _block_seed(seed, k):
    return int(hashlib.sha256(("%s:%s" % (seed, k)).encode()).hexdigest()[:16], 16)


def analyse(arm_logs, tasks, spend, *, seed=SEED, draws=DRAWS, hard_cap=None, final=False, control=None,
            conv=None):
    """arm_logs: {arm: {"recs": [...]} | {"unmeasured": why}}; tasks: {id: {kind, size}}; spend: {arm: {task: row}};
    hard_cap: UTC epoch or None. -> report dict with `blocks` and `final`."""
    control = control or CONTROL
    conv = conv or default_conv()
    rep = {"rule": rule_constants(), "conversion": conv, "seed": seed, "draws": draws, "arms": {}, "blocks": []}
    eras, era_why = era_map(tasks if isinstance(tasks, dict) else {})
    newest = None if eras is None else {t for t, e in eras.items() if e == max(eras.values())}
    rep["era_gate"] = {"status": "UNMEASURED" if eras is None else "MEASURED", "eras": ERAS,
                       "trial_tasks": len(tasks) if isinstance(tasks, dict) else 0,
                       "newest_era": sorted(newest) if newest is not None else None, "limit": ERA_LIMIT}
    if era_why:
        rep["era_gate"]["why"] = era_why + ": every decision is held until the final look"
    if not isinstance(arm_logs, dict) or not arm_logs:
        rep["final"] = {"verdict": "UNMEASURED", "why": "no arm logs"}
        return rep
    problems, data, dq = {}, {}, {}
    merged = 0
    beyond_cap = False
    for arm in sorted(arm_logs):
        v = arm_logs[arm]
        if "recs" not in v:
            problems[arm] = v.get("unmeasured") or "unmeasured"
            continue
        recs = v["recs"]
        try:
            beyond_cap = beyond_cap or (hard_cap is not None and any(_ep(r) > hard_cap for r in recs))
        except (ValueError, TypeError):
            pass
        merged += sum(1 for r in recs if r.get("ite") is not None)
        try:
            comp, why = completions(recs, tasks, (spend or {}).get(arm), conv, hard_cap)
            dq[arm] = disqualifications(recs, hard_cap)
        except (ValueError, TypeError, KeyError) as e:
            comp, why = [], "unreadable record: %s" % e
        if why:
            problems[arm] = why
        elif not comp:
            problems[arm] = "no completed (judged accept/reject) task"
        else:
            data[arm] = comp
    rep["merged_ite_records"] = merged
    rep["dq"] = dq
    rep["dq_unmeasured"] = {a: [n for n, c in d.items() if c["status"] == "UNMEASURED"] for a, d in dq.items()}
    blocked = dq_blocking(dq)
    rep["dq_blocking"] = blocked
    for a, why in problems.items():
        rep["arms"][a] = {"status": "UNMEASURED", "why": why}
    # disqualification fires at any time, even with an unmeasured roster. Each condition carries its own first time.
    viols = {a: sorted((_ep(c), n) for n, c in d.items() if c["status"] == "VIOLATED") for a, d in dq.items()}
    dq_at = {a: (v[0][0] if v else None) for a, v in viols.items()}

    def reasons(a, lo=None, hi=None):
        return [n for t, n in viols.get(a, ()) if (lo is None or t > lo) and (hi is None or t <= hi)]
    if problems or len(data) < 2:
        why = ("arm(s) UNMEASURED: %s" % problems) if problems else "fewer than two measured arms"
        rep["final"] = {"verdict": "UNMEASURED", "why": why,
                        "disqualified": {a: reasons(a) for a in sorted(a for a in dq_at if dq_at[a] is not None)}}
        return rep
    arms = sorted(data)
    disq, disq_t, dropped, contention = {}, {}, {}, list(arms)
    k = 0
    stop = None
    last_look = None           # {arm: completions} the rule last ran on (the final look never re-runs the same data)
    floor = -math.inf          # block times never go backwards
    while True:
        k += 1
        n_need = BLOCK * k
        # ONE chronological cutoff. Block k is at the time the last arm in contention reaches 5k completions. Walk
        # the violations in time order first: an arm whose violation comes before that cutoff (or while it is still
        # being waited for) leaves contention at its violation time, and the cutoff is recomputed without it, so a
        # disqualified arm's later completions never set the cutoff and a silent short arm never blocks forever.
        new_dq = []
        while True:
            cand = max((data[a][n_need - 1]["t"] if len(data[a]) >= n_need else math.inf) for a in contention) \
                if contention else math.inf
            t_eff = max(cand, floor)
            pend = [a for a in arms if a not in disq and dq_at[a] is not None and dq_at[a] <= t_eff]
            if not pend:
                break
            e = min(dq_at[a] for a in pend)
            for a in sorted(a for a in pend if dq_at[a] == e):
                disq[a], disq_t[a] = reasons(a, hi=e), e
                new_dq.append(a)
            contention = [a for a in contention if a not in disq]
            floor = max(floor, e)
        if len(contention) >= 2 and t_eff == math.inf:
            break          # an arm in contention is short of 5k completions and has not violated: wait for it
        blk = {"block": k, "tasks_per_arm": n_need, "ts_epoch": (None if t_eff == math.inf else t_eff)}
        floor = max(floor, t_eff) if t_eff != math.inf else floor
        use = {a: data[a][:n_need] if a in contention else data[a][:dropped.get(a, 0)] for a in arms}
        blk["disqualified"] = {a: disq[a] for a in new_dq}
        blk["dq_unmeasured"] = {a: v for a, v in rep["dq_unmeasured"].items() if v}
        if new_dq:
            blk["verdict"] = "DISQUALIFIED"
        if len(contention) < 2:
            blk.setdefault("verdict", "CONTINUE")
            blk["why"] = "fewer than two arms left in contention: the rule cannot compare (no automatic winner)"
            rep["blocks"].append(blk)
            break
        nondq = [a for a in arms if a not in disq]
        if control not in nondq:
            # no reference arm: no block verdict can be a comparison; the trial ends UNMEASURED here
            # (ARENA_CONTROL_HARDEN_ABSENT_NOT_NO_DIFF; GPT r2 #1)
            det = {"why": "the control (%s) is %s: no reference to compare against" %
                   (control, "disqualified" if control in disq else "absent")}
            blk.update(rule_verdict="UNMEASURED", detail=det)
            blk.setdefault("verdict", "UNMEASURED")
            rep["blocks"].append(blk)
            stop = dict(blk, verdict="UNMEASURED", _use={a: use[a] for a in nondq})
            break
        below = {a: [len(use[a]), len({c["kind"] for c in use[a]})] for a in contention
                 if len(use[a]) < MIN_TASKS or len({c["kind"] for c in use[a]}) < MIN_KINDS}
        if below:
            blk.setdefault("verdict", "UNMEASURED")
            blk["below_minimum"] = below
            rep["blocks"].append(blk)
            continue
        post = posterior({a: use[a] for a in nondq}, nondq, _block_seed(seed, k), draws, control)
        probs = rule_probs(post, contention, nondq, control)
        v, det = rule_verdict(probs, control in nondq, blocked)
        blk["probs"] = probs
        last_look = {a: len(use[a]) for a in nondq}
        short = newest_era_missing(use, contention, newest)
        if short and gated(v):
            # ERA GATE: tasks run oldest first (sibling order), so this look has not seen the newest era: a
            # would-be stop or FUTILE drop is held, reported, and the trial goes on
            # (ARENA_STOP_RULE_HOLD_DECIDE_TILL_NEWEST, ARENA_FUTILE_GATE_FIX_OLD_TASK_DROPS)
            blk["held"] = {"would_be": v, "detail": det, "newest_era_missing": short,
                           # a would-be DECIDE is checked before FUTILE: name the arms FUTILE would drop too
                           "futile_would_be": sorted(x for x, p in probs["futile"].items() if p < FUTILE_P),
                           "why": "the newest era has not run for every arm in contention: no decision, no drop yet"}
            v, det = "CONTINUE", {"held": v}
        blk["rule_verdict"] = v
        blk["detail"] = det
        blk.setdefault("verdict", v)
        if v == "FUTILE":
            for a in det["arms"]:
                dropped[a] = n_need
            contention = [a for a in contention if a not in det["arms"]]
        rep["blocks"].append(blk)
        if v.startswith("DECIDE_FOR_") or v == "TIE" or v == "UNMEASURED":
            stop = dict(blk, verdict=v, _use={a: use[a] for a in nondq})
            break
    rep["era_gate"]["held_blocks"] = [b["block"] for b in rep["blocks"] if b.get("held")]
    # final. With a stop, the trial ended at the stop's time: later violations are reported, not applied. With no
    # stop, a violation at any time disqualifies. Reasons are always split by their own times.
    if stop is not None:
        cut = stop["ts_epoch"]
        late_dq = []
        after = {a: reasons(a, lo=(max(disq_t[a], cut) if a in disq_t else cut)) for a in arms}
    else:
        late_dq = sorted(a for a in arms if a not in disq and dq_at[a] is not None)
        after = {a: reasons(a, lo=disq_t[a]) for a in disq}
    keep = [a for a in arms if a not in disq and a not in late_dq]
    fin = {"disqualified": dict({a: disq[a] for a in disq}, **{a: reasons(a) for a in late_dq}),
           "futile": sorted(dropped), "dq_unmeasured": {a: v for a, v in rep["dq_unmeasured"].items() if v}}
    after = {a: v for a, v in after.items() if v}
    if after:
        fin["violations_after_stop" if stop is not None else "later_violations_of_disqualified"] = after
    # intervals come from the trial's own snapshot: the stop's data, or every arm frozen where the rule left it
    snap = stop["_use"] if stop is not None else {a: (data[a][:dropped[a]] if a in dropped else data[a]) for a in keep}
    keep = [a for a in keep if a in snap]
    post = None
    if keep:
        post = posterior({a: snap[a] for a in keep}, keep, _block_seed(seed, "final"), draws, control)
        fin["intervals"] = arm_summary(post, snap, keep, control)
        fin["intervals_snapshot"] = ("block %d" % stop["block"]) if stop is not None else "all data (futile arms frozen)"
        fin["time_to_acceptance"] = tta_summary(snap, keep, control)
    live = [a for a in keep if a not in dropped]
    trial = set(tasks) if isinstance(tasks, dict) else set()
    # every arm in contention has completed every trial task: no further block can exist, the trial is over
    # (a CONTINUE to an unreachable block was ARENA_STOP_GATE_FIX_SMALL_LEFTOVERS item 3)
    exhausted = bool(trial and live) and all(trial <= {c["task"] for c in data[a]} for a in live)
    below = {a: [len(data[a]), len({c["kind"] for c in data[a]})] for a in live
             if len(data[a]) < MIN_TASKS or len({c["kind"] for c in data[a]}) < MIN_KINDS}
    if stop is not None:
        fin["verdict"] = stop["verdict"]
        fin["block"] = stop["block"]
        fin["detail"] = stop.get("detail") or {"why": stop.get("why")}
    elif below:
        fin["verdict"] = "UNMEASURED"
        fin["detail"] = {"why": "below the minimum (%d tasks, %d kinds per arm in contention)%s" %
                         (MIN_TASKS, MIN_KINDS, " at the hard cap" if (final or beyond_cap) else ""),
                         "below_minimum": below}
    elif len(keep) < 2:
        fin["verdict"] = "DISQUALIFIED" if fin["disqualified"] else "UNMEASURED"
        fin["detail"] = {"why": "fewer than two measured arms survive disqualification: no comparison and no "
                         "automatic winner%s" % ("" if control in keep else "; the control (%s) is not among them"
                                                 % control), "surviving": keep}
    elif control not in keep:
        # without the control there is no reference: never "no difference" and never "keep going"
        # (ARENA_CONTROL_HARDEN_ABSENT_NOT_NO_DIFF)
        fin["verdict"] = "UNMEASURED"
        fin["detail"] = {"why": "the control (%s) is %s: no reference to compare against, no hard-cap pick" %
                         (control, "disqualified" if control in fin["disqualified"] else "absent"),
                         "surviving": keep}
    elif (final or beyond_cap or exhausted) and newest is None:
        # gate UNMEASURED (a trial task with no chronology key): no look could ever see the newest era, so neither a
        # decision nor a hard-cap pick may be made on this population (ARENA_FINAL_LOOK_FIX_UNGATED_AT_CAP)
        fin["verdict"] = "UNMEASURED"
        fin["detail"] = {"why": "the era gate is UNMEASURED (%s): no decision and no hard-cap pick on a trial whose "
                                "newest era cannot be named" % (era_why or "no era map")}
    elif final or beyond_cap or exhausted:
        cap = ("--final" if final else "a record is later than the hard cap" if beyond_cap else
               "pool exhausted: every arm in contention completed every trial task")
        fl = None
        # THE FINAL LOOK, GATED like every other look (ARENA_FINAL_LOOK_FIX_UNGATED_AT_CAP): the rule runs once more
        # on the final snapshot only when every kept arm has completed every newest-era task, and only when that
        # snapshot is not the data the last block already looked at. A trial cut short of the newest era (the
        # hard cap, a silent dead arm) is never decided on its older prefix: it falls to the hard-cap clause, in
        # which an arm short of the newest era is not a candidate.
        miss = newest_era_missing(snap, keep, newest)
        # an arm short of the newest era (cut, or gone silent) is SKIPPED by the final look, never a reason to skip
        # the look for the arms that finished (ARENA_CUT_TRIAL_FIX_SAYS_NO_DIFFERENCE: one dead arm used to block it)
        seen = [a for a in keep if a not in miss]
        live_seen = [a for a in live if a not in miss]
        cut = control in miss or not any(a != control for a in seen)
        fresh = (last_look is None or set(last_look) != set(seen)
                 or any(len(snap[a]) != last_look.get(a) for a in seen))
        if cut:
            fin["final_look"] = {"ran": False, "why": "the %s has not completed the newest era: no look on older "
                                 "tasks alone" % ("control" if control in miss else "every other arm"),
                                 "newest_era_missing": miss}
        elif not fresh:
            fin["final_look"] = {"ran": False, "why": "the last block already applied the rule to exactly this data"}
        else:
            fprobs = rule_probs(post, live_seen, seen, control)
            fl = rule_verdict(fprobs, control in seen, blocked)
            fin["final_look"] = {"ran": True, "rule_verdict": fl[0], "detail": fl[1], "probs": fprobs,
                                 "arms": seen, "newest_era_missing": miss}
            if miss:
                fin["final_look"]["skipped_short"] = sorted(miss)
        win, pick = hardcap_pick(post, keep, control, blocked, miss)
        if miss:
            pick = dict(pick, newest_era_missing=miss)
        if cut:
            # a cut trial is UNDECIDED, never "no difference": the control, or every arm compared with it, never ran
            # the newest era, so nothing was compared on the population the rule is defined over
            # (ARENA_CUT_TRIAL_FIX_SAYS_NO_DIFFERENCE; was HARD_CAP_NO_DIFFERENCE, winner = the control)
            fin["verdict"] = CUT_SHORT
            fin["detail"] = dict(pick, winner=None, why="the trial ended (%s) before %s completed the newest era: "
                                 "no comparison was made on it, so there is no decision, no pick and no 'no "
                                 "difference'; run the newest era (or rerun) to decide" %
                                 (cap, "the control" if control in miss else "any arm besides the control"))
        elif fl is not None and held_kind(fl[0]):
            fin["verdict"] = fl[0]
            fin["detail"] = dict(fl[1], final_look=True, why_final_look="the final look (%s) decides on all data "
                                 "of the arms %s, the newest era in for each%s" % (
                                     cap, seen, "; skipped (newest era not run): %s" % sorted(miss) if miss else ""))
        elif pick["picked"]:
            fin["verdict"] = "HARD_CAP_PICK"
            fin["detail"] = dict(pick, winner=win, why="nothing fired by the hard cap (%s): %s is the simplest arm "
                                 "not credibly worse than the control" % (cap, win))
        else:
            fin["verdict"] = "HARD_CAP_NO_DIFFERENCE"
            fin["detail"] = dict(pick, winner=control, why="nothing fired by the hard cap (%s) and no simpler arm "
                                 "qualifies: the control stays" % cap)
            if miss:
                fin["detail"]["not_judged"] = sorted(miss)
                fin["detail"]["why"] += ("; arm(s) %s never completed the newest era and were not judged"
                                         % sorted(miss))
    else:
        fin["verdict"] = "CONTINUE"
        nxt = min(BLOCK * k, len(trial)) if trial else BLOCK * k
        fin["detail"] = {"next_block_tasks_per_arm": nxt, "in_contention": contention,
                         "waiting_for": sorted(a for a in live if len(data[a]) < nxt),
                         # the wall clock is never read: a stuck arm keeps this CONTINUE until the driver ends it
                         "end_of_budget": "the driver must re-run with --final at the end of the budget"}
    if late_dq:
        fin["verdict_note"] = "arm(s) %s violated a condition after the last complete block" % late_dq
    rep["final"] = fin
    return rep


def rule_constants():
    return {k: globals()[k] for k in ("BLOCK", "MIN_TASKS", "MIN_KINDS", "DECIDE_RATIO", "DECIDE_P", "ACCEPT_MARGIN",
                                      "ACCEPT_P", "FUTILE_RATIO", "FUTILE_P", "TIE_BAND", "TIE_P", "SIMPLER",
                                      "CONTROL", "RALPH_A_CAPACITY", "ARM_PRIOR_SD", "TASK_PRIOR_SD", "SIGMA_REF",
                                      "IG_A0", "IG_B0", "ACCEPT_PRIOR_MEAN", "ACCEPT_PRIOR_WEIGHT",
                                      "HARDCAP_ACCEPT_MARGIN", "HARDCAP_ACCEPT_P", "HARDCAP_EFF_RATIO",
                                      "HARDCAP_EFF_P", "ERAS")}


def blind(rep, salt):
    """Hash arm names in the output (section 3.4) unless a stop fired."""
    v = rep.get("final", {}).get("verdict", "")
    if v.startswith("DECIDE_FOR_") or v in ("TIE", "HARD_CAP_PICK"):
        return rep
    names = set(rep.get("arms", {})) | set(rep.get("dq", {})) | set(SIMPLER)
    text = json.dumps(rep, sort_keys=True)
    for a in sorted(names, key=len, reverse=True):
        h = "arm_" + hashlib.sha256((salt + ":" + a).encode()).hexdigest()[:8]
        text = re.sub(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(a), h, text)
    return json.loads(text)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--spend", required=True, help="per-(arm,task) raw spend JSON, schema %s (arena_spend.py)" %
                   SPEND_SCHEMA)
    r.add_argument("--raw-dir", help="read unsigned <arm>.jsonl from this dir instead of the signed log")
    r.add_argument("--tasks-dir", help="frozen task specs dir (default <arena>/tasks)")
    r.add_argument("--trial-tasks", help="file of the trial's task ids (arena_trial.py JSON, a JSON list, or one per "
                   "line): the era gate's population (default: the committed list %s, N tasks, default 50; never every "
                   "frozen task)" % TRIAL_DEFAULT.name)
    r.add_argument("--era-repo", help="git repo holding the tasks' base shas, for their chronology (default %s)" % A.REPO)
    r.add_argument("--allow-untrusted", action="store_true")
    r.add_argument("--hard-cap", help="ISO-8601 with zone: end of day 3")
    r.add_argument("--final", action="store_true", help="the budget has ended: final look and hard-cap clause now (CUT_SHORT_UNDECIDED if the newest era was not compared); the driver must pass this at the end of the budget")
    r.add_argument("--seed", type=int, default=SEED)
    r.add_argument("--draws", type=int, default=DRAWS)
    r.add_argument("--claude-ite-scale", type=float, default=CLAUDE_ITE_SCALE)
    r.add_argument("--gpt-to-ite", type=float, default=GPT_TO_ITE)
    r.add_argument("--gpt-est-in-to-ite", type=float, default=GPT_EST_IN_TO_ITE)
    r.add_argument("--gpt-est-out-to-ite", type=float, default=GPT_EST_OUT_TO_ITE)
    r.add_argument("--claude-model-weight", action="append", default=[], metavar="FAMILY=W",
                   help="override/add a Claude model family weight (default %s)" % CLAUDE_MODEL_WEIGHT)
    r.add_argument("--claude-token-weight", action="append", default=[], metavar="FIELD=W",
                   help="override a raw Claude token-field weight (default %s)" % CLAUDE_TOKEN_WEIGHT)
    r.add_argument("--blind", metavar="SALT")
    r.add_argument("--out")
    a = ap.parse_args(argv)
    for f in ("claude_ite_scale", "gpt_to_ite", "gpt_est_in_to_ite", "gpt_est_out_to_ite"):
        if not (math.isfinite(getattr(a, f)) and getattr(a, f) >= 0):
            ap.error("--%s must be finite and >= 0" % f.replace("_", "-"))
    conv = default_conv()
    conv.update(claude_scale=a.claude_ite_scale, gpt_tokens=a.gpt_to_ite, gpt_in_est=a.gpt_est_in_to_ite,
                gpt_out_est=a.gpt_est_out_to_ite)
    for opt, key in ((a.claude_model_weight, "claude_model"), (a.claude_token_weight, "claude_token")):
        for kv in opt:
            name, _, w = kv.partition("=")
            try:
                wf = float(w)
            except ValueError:
                wf = float("nan")
            if not name or not math.isfinite(wf) or wf < 0:
                ap.error("bad weight %r (want NAME=W, W finite >= 0)" % kv)
            if key == "claude_token" and name not in CLAUDE_TOKEN_WEIGHT:
                ap.error("unknown Claude token field %r (have %s)" % (name, sorted(CLAUDE_TOKEN_WEIGHT)))
            conv[key][name.lower() if key == "claude_model" else name] = wf
    read_err = None
    try:
        doc = json.loads(Path(a.spend).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        doc, read_err = None, str(e)
    logs = load_raw(a.raw_dir) if a.raw_dir else load_verified(allow_untrusted=a.allow_untrusted)
    tasks = load_tasks({"tasks": Path(a.tasks_dir)} if a.tasks_dir else None)
    trial_err = None
    try:
        # the population is ALWAYS an explicit list: with every frozen task (241) the newest era is 80 tasks and the
        # gate never opens within budget (ARENA_TRIAL_TASKS_FIX_DEFAULT_ALL_FROZEN)
        import arena_trial
        ids = arena_trial.read_list(a.trial_tasks or TRIAL_DEFAULT)
        unknown = sorted(set(ids) - set(tasks))
        if unknown:
            trial_err = "trial task(s) with no frozen spec: %s" % unknown[:5]
        tasks = {t: tasks[t] for t in ids if t in tasks}
    except (OSError, ValueError, TypeError, AttributeError) as e:
        trial_err = "trial task list %s unreadable: %s" % (a.trial_tasks or TRIAL_DEFAULT, e)
        tasks = {}
    no_chrono = chrono_keys(tasks, a.era_repo)
    cap = L.ts_epoch(a.hard_cap) if a.hard_cap else None
    rep = analyse_spend_doc(logs, tasks, doc, seed=a.seed, draws=a.draws, hard_cap=cap, final=a.final, conv=conv)
    if no_chrono:
        rep["era_gate"]["no_chrono"] = dict(sorted(no_chrono.items())[:20], **({"...": "%d more" % (len(no_chrono) - 20)}
                                                                               if len(no_chrono) > 20 else {}))
    if read_err is not None or trial_err is not None:
        rep["final"] = {"verdict": "UNMEASURED", "why": ("spend file unreadable: %s" % read_err) if read_err is not None
                        else trial_err}
        if trial_err is not None:              # wrong population: no per-block verdict computed from it stands
            rep["blocks_withheld"], rep["blocks"] = len(rep.get("blocks") or []), []
    if a.blind:
        rep = blind(rep, a.blind)
    text = json.dumps(rep, indent=1, sort_keys=True, default=str)
    if a.out:
        Path(a.out).write_text(text + "\n", encoding="utf-8")
    print(json.dumps(rep["final"], indent=1, sort_keys=True, default=str))
    v = rep["final"]["verdict"]
    return 3 if v.startswith("UNMEASURED") else 4 if v == CUT_SHORT else 0


if __name__ == "__main__":
    sys.exit(main())
