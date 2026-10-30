#!/usr/bin/env python3
"""arena_analysis.py - the trial's stopping rule, committed before day 1 (ARENA_ANALYSIS_BUILD_RULE_BEFORE_RACE).

design/RimMandrake/architecture_switch_harness_2026-10-29.md section 4.1 (rule), 3.3 (measures), 3.5 (power),
1.7 (event log), 1.8 / testpilot_merged_2026-10-29.md 2.3 (a different agent tests promptly).

    python3 src/RimMandrake/Utils/arena/arena_analysis.py run --spend SPEND.json [--hard-cap ISO] [--final]
            [--seed N] [--draws N] [--gpt-to-ite F] [--gpt-est-to-ite F] [--claude-ite-scale F]
            [--raw-dir DIR] [--allow-untrusted] [--blind SALT] [--out OUT.json]

Prints one JSON report: a verdict per 5-task block and a final verdict, each one of
    DECIDE_FOR_X | FUTILE(X) | TIE(simpler wins) | CONTINUE | DISQUALIFIED(X, reason) | HARD_CAP_NO_DIFFERENCE
    | UNMEASURED(reason)
plus per-arm intervals and every disqualification condition as VIOLATED / CLEAN / VACUOUS / UNMEASURED.

WHAT IT READS (only fields some harness code writes, or the section 1.7 schema names):
  - the per-arm event logs. Default: arena_eventlog.report()+verify() (signed, anchored); an arm the report refuses,
    with any rejected/undecodable line, or not `trusted` (no ledger anchor + witness) is UNMEASURED unless
    --allow-untrusted. --raw-dir reads unsigned <arm>.jsonl files (selftests, dry runs): any unparseable line, a record
    missing ts/arm/event or with a zoneless ts makes that arm UNMEASURED.
  - judge events: task, verdict ('accept' | 'reject' | 'invalid'; the LAST by event time counts, as
    arena_eventlog.accepted_tasks), ts, sha. A task is COMPLETED when its last judge verdict is accept or reject.
  - the frozen task specs <arena>/tasks/<id>.json: kind (arena_tasks.KINDS) and size (1/2/4 = points).
  - TOKENS, from a spend file (--spend), never from the record `ite` field: {arm: {task: {claude_ite, gpt_ite,
    gpt_ite_est}}}, the field names of sim/spend_census.arm_report. Owner ruling (ARENA_METER_BUILD_SPEND_BY_CLONE_PATH,
    2026-10-30): raw GPT and Claude spend are stored separately and THIS script converts:
        total_ite_mixed = CLAUDE_ITE_SCALE*claude_ite + GPT_TO_ITE*gpt_ite + GPT_EST_TO_ITE*gpt_ite_est
    (named constants, overridable on the command line, so a new conversion needs no re-metering). A row that carries
    only a merged total is refused (UNMEASURED), and any record `ite` is ignored and counted in `merged_ite_records`.

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
  - HARD_CAP_NO_DIFFERENCE: nothing fired and either --final is given or a record is later than --hard-cap (end of
    day 3; records after it are ignored). Deterministic: the wall clock is never read. Reported with the intervals.
  - an arm that will be disqualified is not waited for; if fewer than two arms remain in contention the block is
    CONTINUE with a note (the rule names no automatic winner).
FAIL CLOSED: no arms, fewer than two measured arms, an UNMEASURED arm anywhere in the roster, a completed task with
no frozen spec or no spend row, zero tokens -> UNMEASURED, never a decision.

DISQUALIFICATION CONDITIONS, AND WHAT THE LOG CAN SHOW:
  publish   a judge event (the judge reads only published arena/* work) on (task, sha) with no earlier gate event
            verdict 'pass' on the same task and sha. A judge event with no sha: UNMEASURED. Publication that never
            reached the judge is not in the log (arena.py prepush alarms are not arm events): not seen here.
  scope     a gate event whose detail.steps.scope is FAIL (a changed path outside the task area or forbidden).
            Only edits that reached the gate are seen; no gate event at all: UNMEASURED.
  lane      a live_take (verdict ok) whose hold (same lane and run_id, up to its live_release) had no canary event.
            An open hold with no canary yet is `pending`, not a violation. No live_take: VACUOUS.
  tester    per build stream (run_id minus its trailing pass counter, e.g. ralph_c.<member>.): a build pass_start
            (detail.role 'build') before the first test_start, by a DIFFERENT agent (arena_eventlog's matching and
            normalisation), of the stream's latest earlier build_end. build_end records with no build pass_start:
            UNMEASURED.
  ruling    breaking a standing ruling: the event log records no ruling check. ALWAYS UNMEASURED.
  An UNMEASURED condition never passes silently: every verdict lists the arms and conditions that were unmeasured
  (`dq_unmeasured`), and a decision carries them.

LIMITS, STATED PLAINLY:
  - As of this commit NO harness code writes `judge` events into the arm logs (arena_judge writes verdict.json; the
    replay driving loop in arena.py trial-runner is OWED), and the meter (spend_census) reports spend per arm per
    window, not per task. Until both exist every real run here is UNMEASURED. spend_census's claude_ite is already
    Opus-input-equivalent weighted (model x token type), not raw Claude tokens; CLAUDE_ITE_SCALE multiplies it.
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
CONTROL = "v3"

# ---------------------------------------------------------------- priors (weak, centred on the simulator)
RALPH_A_CAPACITY = 0.5         # Ralph section 10: ralph_a at 0.5x v3's capacity per token
ARM_PRIOR_SD = 1.0             # log units, at the reference sigma
TASK_PRIOR_SD = 3.0            # log units: task sizes differ a lot
SIGMA_REF = 0.8 / math.sqrt(2)  # sigma_d 0.8 (section 3.5 upper assumption) = sqrt(2) x residual sigma
IG_A0, IG_B0 = 1.0, 0.25
C_PREC = 1e-6                  # intercept prior precision (flat)
ACCEPT_PRIOR_MEAN, ACCEPT_PRIOR_WEIGHT = 0.64, 2.0

# ---------------------------------------------------------------- token conversion (owner ruling 2026-10-30)
CLAUDE_ITE_SCALE = 1.0
GPT_TO_ITE = 1.0               # raw codex tokens -> ITE: OPEN owner question; 1.0 matches spend_census's 1:1 sum
GPT_EST_TO_ITE = 1.0
SPEND_FIELDS = ("claude_ite", "gpt_ite", "gpt_ite_est")

DRAWS = 4000
SEED = 20261030
JUDGE_DONE = ("accept", "reject")


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
        if arm == "harness":
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
    import arena_tasks as A
    p = p or A.paths()
    rep = L.report(p, token, external)
    out = {}
    for arm, v in sorted(rep.items()):
        if arm.startswith("_"):
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
    import arena_tasks as A
    p = p or A.paths()
    out = {}
    for f in sorted(Path(p["tasks"]).glob("*.json")):
        try:
            t = json.loads(f.read_text(encoding="utf-8"))
            out[t["id"]] = {"kind": t["kind"], "size": t["size"]}
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return out


# ================================================================ per-arm extraction

def task_tokens(row, conv):
    """A spend row -> total_ite_mixed, or (None, why). Fields are spend_census's; a merged-only row is refused."""
    if not isinstance(row, dict):
        return None, "no spend row"
    if not any(k in row for k in SPEND_FIELDS):
        return None, "spend row has no split fields %s (merged total only?)" % (SPEND_FIELDS,)
    tot = 0.0
    for k in SPEND_FIELDS:
        v = row.get(k, 0.0)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0:
            return None, "spend %s=%r invalid" % (k, v)
        tot += conv[k] * float(v)
    if tot <= 0:
        return None, "zero tokens"
    return tot, None


def completions(recs, tasks, spend_arm, conv, cap=None):
    """-> (list of completed-task dicts sorted by completion time, problem or None)."""
    seq = [r for r in L.ordered(recs) if cap is None or _ep(r) <= cap]
    last, start = {}, {}
    for r in seq:
        t = _tkey(r.get("task"))
        if not t:
            continue
        if r["event"] == "judge":
            last[t] = r
        elif r["event"] in ("assign", "pass_start"):
            cur = start.get(t)
            if cur is None or (cur["event"] == "pass_start" and r["event"] == "assign"):
                start[t] = r
    out = []
    for t, j in last.items():
        if j.get("verdict") not in JUDGE_DONE:
            continue
        spec = tasks.get(t)
        if not spec or spec.get("size") not in (1, 2, 4) or not isinstance(spec.get("kind"), str):
            return [], "completed task %s has no frozen spec (kind/size)" % t
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
    return out, None


# ================================================================ disqualification

def _sha_eq(a, b):
    a, b = (x.strip().lower() if isinstance(x, str) else "" for x in (a, b))
    if len(a) < 7 or len(b) < 7:
        return False
    return a.startswith(b) or b.startswith(a)


def dq_publish(seq):
    judges = [r for r in seq if r["event"] == "judge"]
    if not judges:
        return {"status": "VACUOUS", "why": "no judge event"}
    gates = [(i, r) for i, r in enumerate(seq) if r["event"] == "gate" and r.get("verdict") == "pass"]
    viol, nosha = [], 0
    for i, j in enumerate(seq):
        if j["event"] != "judge":
            continue
        if not isinstance(j.get("sha"), str) or not j["sha"].strip():
            nosha += 1
            continue
        if not any(gi < i and _tkey(g.get("task")) == _tkey(j.get("task")) and _sha_eq(g.get("sha"), j["sha"])
                   for gi, g in gates):
            viol.append({"ts": j["ts"], "task": j.get("task"), "sha": j["sha"]})
    if viol:
        return {"status": "VIOLATED", "ts": viol[0]["ts"], "why": "judged (published) work with no earlier gate pass",
                "evidence": viol[:5]}
    if nosha:
        return {"status": "UNMEASURED", "why": "%d judge event(s) carry no sha" % nosha}
    return {"status": "CLEAN"}


def dq_scope(seq):
    gates = [r for r in seq if r["event"] == "gate"]
    if not gates:
        return {"status": "UNMEASURED", "why": "no gate event: no edit was scope-checked"}
    viol, missing = [], 0
    for g in gates:
        steps = (g.get("detail") or {}).get("steps") if isinstance(g.get("detail"), dict) else None
        st = steps.get("scope") if isinstance(steps, dict) else None
        if st is None:
            missing += 1
        elif str(st).upper() == "FAIL":
            viol.append({"ts": g["ts"], "task": g.get("task"), "sha": g.get("sha")})
    if viol:
        return {"status": "VIOLATED", "ts": viol[0]["ts"], "why": "gate scope FAIL: edit outside the task area",
                "evidence": viol[:5]}
    if missing:
        return {"status": "UNMEASURED", "why": "%d gate event(s) with no scope step" % missing}
    return {"status": "CLEAN"}


def dq_lane(seq):
    takes = [i for i, r in enumerate(seq) if r["event"] == "live_take" and r.get("verdict") == "ok"]
    if not takes:
        return {"status": "VACUOUS", "why": "no live_take"}
    viol, pending = [], 0
    for i in takes:
        key = (seq[i].get("lane"), seq[i].get("run_id"))
        end = next((k for k in range(i + 1, len(seq)) if seq[k]["event"] == "live_release"
                    and (seq[k].get("lane"), seq[k].get("run_id")) == key), None)
        stop = end if end is not None else len(seq)
        canary = any(seq[k]["event"] == "canary" and (seq[k].get("lane"), seq[k].get("run_id")) == key
                     for k in range(i + 1, stop))
        if canary:
            continue
        if end is None:
            pending += 1
        else:
            viol.append({"ts": seq[end]["ts"], "lane": key[0], "run_id": key[1]})
    if viol:
        return {"status": "VIOLATED", "ts": viol[0]["ts"], "why": "lane held and released with no canary",
                "evidence": viol[:5]}
    return {"status": "CLEAN", "pending_open_holds": pending} if pending else {"status": "CLEAN"}


def stream_of(run_id):
    return re.sub(r"\d+$", "", run_id) if isinstance(run_id, str) else None


def dq_tester(seq):
    builds = [i for i, r in enumerate(seq) if r["event"] == "build_end"]
    starts = [i for i, r in enumerate(seq) if r["event"] == "pass_start"
              and (r.get("detail") or {}).get("role") == "build"]
    if not builds and not starts:
        return {"status": "VACUOUS", "why": "no build"}
    if builds and not starts:
        return {"status": "UNMEASURED", "why": "build_end records but no build pass_start"}
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
        return {"status": "VIOLATED", "ts": viol[0]["ts"],
                "why": "new build pass before a different agent began testing the last candidate",
                "evidence": viol[:5]}
    return {"status": "CLEAN"}


def dq_ruling(_seq):
    return {"status": "UNMEASURED", "why": "the event log records no standing-ruling check"}


DQ_CHECKS = (("publish", dq_publish), ("scope", dq_scope), ("lane", dq_lane), ("tester", dq_tester),
             ("ruling", dq_ruling))


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


def rule_verdict(probs, control_present):
    """-> (verdict, detail). Pure: thresholds compared to probabilities. Order: DECIDE, TIE, FUTILE, CONTINUE."""
    for x, p in sorted(probs["decide"].items()):
        if p > DECIDE_P:
            if not control_present or x not in probs["accept_worse"]:
                return "CONTINUE", {"note": "%s passes the efficiency test but the control's accept rate is "
                                            "UNMEASURED: no decision" % x}
            if probs["accept_worse"][x] < ACCEPT_P:
                return "DECIDE_FOR_%s" % x, {"arm": x, "p_decide": p, "p_accept_worse": probs["accept_worse"][x]}
    if probs["tie"] is not None and probs["tie"] > TIE_P:
        a, b = probs["leaders"]
        w = simpler(a, b)
        if w is None:
            return "UNMEASURED", {"why": "tie between %s and %s but one is not in the simpler-arm order" % (a, b)}
        return "TIE", {"leaders": [a, b], "winner": w, "p_tie": probs["tie"]}
    fut = sorted(x for x, p in probs["futile"].items() if p < FUTILE_P)
    if fut:
        return "FUTILE", {"arms": fut}
    return "CONTINUE", {}


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


def _block_seed(seed, k):
    return int(hashlib.sha256(("%s:%s" % (seed, k)).encode()).hexdigest()[:16], 16)


def analyse(arm_logs, tasks, spend, *, seed=SEED, draws=DRAWS, hard_cap=None, final=False, control=None,
            conv=None):
    """arm_logs: {arm: {"recs": [...]} | {"unmeasured": why}}; tasks: {id: {kind, size}}; spend: {arm: {task: row}};
    hard_cap: UTC epoch or None. -> report dict with `blocks` and `final`."""
    control = control or CONTROL
    conv = conv or {"claude_ite": CLAUDE_ITE_SCALE, "gpt_ite": GPT_TO_ITE, "gpt_ite_est": GPT_EST_TO_ITE}
    rep = {"rule": rule_constants(), "conversion": conv, "seed": seed, "draws": draws, "arms": {}, "blocks": []}
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
    for a, why in problems.items():
        rep["arms"][a] = {"status": "UNMEASURED", "why": why}
    # disqualification fires at any time, even with an unmeasured roster
    dq_at = {a: min((_ep(c) for c in d.values() if c["status"] == "VIOLATED"), default=None) for a, d in dq.items()}
    dq_reason = {a: [n for n, c in d.items() if c["status"] == "VIOLATED"] for a, d in dq.items()}
    if problems or len(data) < 2:
        why = ("arm(s) UNMEASURED: %s" % problems) if problems else "fewer than two measured arms"
        dqs = sorted(a for a, t in dq_at.items() if t is not None)
        rep["final"] = {"verdict": "UNMEASURED", "why": why,
                        "disqualified": {a: dq_reason[a] for a in dqs}}
        return rep
    arms = sorted(data)
    disq, dropped, contention = {}, {}, list(arms)
    k = 0
    stop = None
    while True:
        k += 1
        n_need = BLOCK * k
        # an arm that violates a condition at some time is not waited for: it is disqualified when its time comes
        need = [a for a in contention if dq_at[a] is None]
        if not need or any(len(data[a]) < n_need for a in need):
            break
        use = {a: data[a][:n_need] if a in contention else data[a][:dropped.get(a, n_need)] for a in arms}
        t_block = max(use[a][-1]["t"] for a in need)
        blk = {"block": k, "tasks_per_arm": n_need, "ts_epoch": t_block}
        new_dq = sorted(a for a in arms if a not in disq and dq_at[a] is not None and dq_at[a] <= t_block)
        for a in new_dq:
            disq[a] = dq_reason[a]
        contention = [a for a in contention if a not in disq]
        blk["disqualified"] = {a: disq[a] for a in new_dq}
        blk["dq_unmeasured"] = {a: v for a, v in rep["dq_unmeasured"].items() if v}
        if new_dq:
            blk["verdict"] = "DISQUALIFIED"
        if len(contention) < 2:
            blk.setdefault("verdict", "CONTINUE")
            blk["why"] = "fewer than two arms left in contention: the rule cannot compare (no automatic winner)"
            rep["blocks"].append(blk)
            break
        below = {a: [len(use[a]), len({c["kind"] for c in use[a]})] for a in contention
                 if len(use[a]) < MIN_TASKS or len({c["kind"] for c in use[a]}) < MIN_KINDS}
        if below:
            blk.setdefault("verdict", "UNMEASURED")
            blk["below_minimum"] = below
            rep["blocks"].append(blk)
            continue
        nondq = [a for a in arms if a not in disq]
        post = posterior({a: use[a] for a in nondq}, nondq, _block_seed(seed, k), draws, control)
        probs = rule_probs(post, contention, nondq, control)
        v, det = rule_verdict(probs, control in nondq)
        blk["probs"] = probs
        blk["rule_verdict"] = v
        blk["detail"] = det
        blk.setdefault("verdict", v)
        if v == "FUTILE":
            for a in det["arms"]:
                dropped[a] = n_need
            contention = [a for a in contention if a not in det["arms"]]
        rep["blocks"].append(blk)
        if v.startswith("DECIDE_FOR_") or v == "TIE" or v == "UNMEASURED":
            stop = dict(blk, verdict=v)
            break
    # final
    late_dq = sorted(a for a in arms if a not in disq and dq_at[a] is not None)
    keep = [a for a in arms if a not in disq and a not in late_dq]
    fin = {"disqualified": dict({a: disq[a] for a in disq}, **{a: dq_reason[a] for a in late_dq}),
           "futile": sorted(dropped), "dq_unmeasured": {a: v for a, v in rep["dq_unmeasured"].items() if v}}
    if keep:
        post = posterior({a: data[a] for a in keep}, keep, _block_seed(seed, "final"), draws, control)
        fin["intervals"] = arm_summary(post, data, keep, control)
        fin["time_to_acceptance"] = tta_summary(data, keep, control)
    if stop is not None:
        fin["verdict"] = stop["verdict"]
        fin["block"] = stop["block"]
        fin["detail"] = stop.get("detail") or {"why": stop.get("why")}
    elif final or beyond_cap:
        fin["verdict"] = "HARD_CAP_NO_DIFFERENCE"
        fin["detail"] = {"why": "nothing fired by the hard cap (%s)" %
                         ("--final" if final else "a record is later than the hard cap")}
    else:
        fin["verdict"] = "CONTINUE"
        fin["detail"] = {"next_block_tasks_per_arm": BLOCK * k, "in_contention": contention}
    if late_dq and stop is None:
        fin["verdict_note"] = "arm(s) %s violated a condition after the last complete block" % late_dq
    rep["final"] = fin
    return rep


def rule_constants():
    return {k: globals()[k] for k in ("BLOCK", "MIN_TASKS", "MIN_KINDS", "DECIDE_RATIO", "DECIDE_P", "ACCEPT_MARGIN",
                                      "ACCEPT_P", "FUTILE_RATIO", "FUTILE_P", "TIE_BAND", "TIE_P", "SIMPLER",
                                      "CONTROL", "RALPH_A_CAPACITY", "ARM_PRIOR_SD", "TASK_PRIOR_SD", "SIGMA_REF",
                                      "IG_A0", "IG_B0", "ACCEPT_PRIOR_MEAN", "ACCEPT_PRIOR_WEIGHT")}


def blind(rep, salt):
    """Hash arm names in the output (section 3.4) unless a stop fired."""
    v = rep.get("final", {}).get("verdict", "")
    if v.startswith("DECIDE_FOR_") or v == "TIE":
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
    r.add_argument("--spend", required=True, help="per-(arm,task) spend JSON: {arm: {task: {%s}}}" %
                   ", ".join(SPEND_FIELDS))
    r.add_argument("--raw-dir", help="read unsigned <arm>.jsonl from this dir instead of the signed log")
    r.add_argument("--tasks-dir", help="frozen task specs dir (default <arena>/tasks)")
    r.add_argument("--allow-untrusted", action="store_true")
    r.add_argument("--hard-cap", help="ISO-8601 with zone: end of day 3")
    r.add_argument("--final", action="store_true", help="the hard cap has passed: report no-difference if unseparated")
    r.add_argument("--seed", type=int, default=SEED)
    r.add_argument("--draws", type=int, default=DRAWS)
    r.add_argument("--claude-ite-scale", type=float, default=CLAUDE_ITE_SCALE)
    r.add_argument("--gpt-to-ite", type=float, default=GPT_TO_ITE)
    r.add_argument("--gpt-est-to-ite", type=float, default=GPT_EST_TO_ITE)
    r.add_argument("--blind", metavar="SALT")
    r.add_argument("--out")
    a = ap.parse_args(argv)
    for f in ("claude_ite_scale", "gpt_to_ite", "gpt_est_to_ite"):
        if not (math.isfinite(getattr(a, f)) and getattr(a, f) >= 0):
            ap.error("--%s must be finite and >= 0" % f.replace("_", "-"))
    try:
        spend = json.loads(Path(a.spend).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        spend, spend_err = {}, str(e)
    else:
        spend_err = None
    logs = load_raw(a.raw_dir) if a.raw_dir else load_verified(allow_untrusted=a.allow_untrusted)
    tasks = load_tasks({"tasks": Path(a.tasks_dir)} if a.tasks_dir else None)
    cap = L.ts_epoch(a.hard_cap) if a.hard_cap else None
    conv = {"claude_ite": a.claude_ite_scale, "gpt_ite": a.gpt_to_ite, "gpt_ite_est": a.gpt_est_to_ite}
    rep = analyse(logs, tasks, spend if isinstance(spend, dict) else {}, seed=a.seed, draws=a.draws, hard_cap=cap,
                  final=a.final, conv=conv)
    if spend_err:
        rep["final"] = {"verdict": "UNMEASURED", "why": "spend file unreadable: %s" % spend_err}
    if a.blind:
        rep = blind(rep, a.blind)
    text = json.dumps(rep, indent=1, sort_keys=True, default=str)
    if a.out:
        Path(a.out).write_text(text + "\n", encoding="utf-8")
    print(json.dumps(rep["final"], indent=1, sort_keys=True, default=str))
    return 0 if not rep["final"]["verdict"].startswith("UNMEASURED") else 3


if __name__ == "__main__":
    sys.exit(main())
