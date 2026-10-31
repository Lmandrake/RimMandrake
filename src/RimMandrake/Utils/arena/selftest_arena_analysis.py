#!/usr/bin/env python3
"""selftest_arena_analysis.py - the stopping rule (arena_analysis.py) on synthetic logs.

    python3 src/RimMandrake/Utils/arena/selftest_arena_analysis.py              # units + scenarios + small sims
    python3 src/RimMandrake/Utils/arena/selftest_arena_analysis.py --mutants    # break each threshold: suite must fail
    python3 src/RimMandrake/Utils/arena/selftest_arena_analysis.py --calib N    # null false-DECIDE rate over N seeds
    python3 src/RimMandrake/Utils/arena/selftest_arena_analysis.py --power N    # 1.5x, sigma_d 0.8: tasks to decide

Sections: (1) the owner's thresholds pinned; (2) rule boundaries with LITERAL numbers (1.25, 0.95, 0.15, 0.2, 1.1,
0.05, 0.15, 0.9) so a changed module constant fails here; (3) token conversion and fail-closed input; (4) scenarios:
clear winner decides only once 10 tasks / 2 kinds are in, an early fluke does not stop, a clear loser is futile, equal
arms tie to the simpler arm, hard cap, determinism; (5) each disqualification path, firing before the minimum;
(6) small null-calibration and power runs (the full-size numbers come from --calib / --power and are reported, not
asserted against a target: the thresholds are the owner's, not tuned here).
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_analysis as AA  # noqa: E402

FAILS: list[str] = []
QUIET = False
T0 = 1793491200  # 2026-11-01T00:00:00Z
KINDS = ("python-util", "xml-def-patch")
DRAWS = 2000


def check(name, ok, detail=""):
    if not ok:
        FAILS.append(name)
    if not QUIET:
        print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -- " + str(detail)) if detail else ""))


def iso(t):
    import datetime as dt
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat()


# ---------------------------------------------------------------- synthetic logs

def make_tasks(n, kinds=None, chrono=None):
    """chrono(i) -> the era gate's key. Default n - i: the NEWEST era comes FIRST in completion order, so the gate is
    open from the first look and every older scenario keeps testing its own mechanics (the order is not simulated;
    t_era_gate tests the gate with the real oldest-first order, chrono = i)."""
    kinds = kinds or (lambda i: KINDS[i % 2])
    chrono = chrono or (lambda i: n - i)
    return {"T%03d" % i: {"kind": kinds(i), "size": (1, 2, 4)[i % 3], "chrono": chrono(i)} for i in range(n)}


def arm_log(arm, rows, offset=0, drop=(), extra=()):
    """rows: [(task, accepted)] in completion order -> one arm's records (a full build/test/gate/judge cycle)."""
    recs = []
    for i, (task, acc) in enumerate(rows):
        t = T0 + offset + i * 600
        rid, b, sha = "%s.%d" % (arm, i), "b-%s-%d" % (arm, i), hashlib.sha1(("%s/%s" % (arm, task)).encode()).hexdigest()
        ev = [("assign", t, {}), ("pass_start", t + 10, {"detail": {"role": "build", "agent": b}}),
              ("build_end", t + 100, {"sha": sha, "detail": {"builder": b, "build_id": "bid%d" % i}}),
              ("test_start", t + 110, {"detail": {"tester": "q-%s-%d" % (arm, i), "build_id": "bid%d" % i}}),
              ("gate", t + 200, {"sha": sha, "verdict": "pass", "detail": {"steps": {"scope": "PASS"}}}),
              ("judge", t + 300, {"sha": sha, "verdict": "accept" if acc else "reject"})]
        for name, ts, more in ev:
            if (i, name) in drop:
                continue
            r = {"ts": iso(ts), "arm": arm, "lane": "L1", "run_id": rid, "task": task, "event": name}
            r.update(more)
            recs.append(r)
    for r in extra:
        recs.append(dict({"arm": arm, "lane": "L1", "task": None}, **r))
    return recs


OPUS = "claude-opus-5-5"


def raw_row(opus_input=0.0, **kw):
    """A per-task spend row in the meter's RAW shape (arena_spend.py, schema arena_task_spend/2)."""
    row = {"claude": {OPUS: {"input": opus_input, "cache_read": 0, "cache_write_5m": 0, "cache_write_1h": 0,
                             "output": 0}},
           "gpt": {"tokens": 0, "in_est": 0, "out_est": 0, "calls": 0, "est_calls": 0}, "ambiguous_calls": 0}
    row.update(kw)
    return row


def R(claude=None, gpt=None, **kw):
    """A FULL raw row as the meter writes it (every Claude field per model, every GPT field), partial counts filled
    with 0: since ARENA_SPEND_ROW_HARDEN_MISSING_GPT_FIELD a missing field is refused, never read as 0."""
    row = {"claude": {m: dict({f: 0 for f in AA.CLAUDE_TOKEN_WEIGHT}, **v) for m, v in (claude or {}).items()},
           "gpt": dict({"tokens": 0, "in_est": 0, "out_est": 0, "calls": 0, "est_calls": 0}, **(gpt or {})),
           "ambiguous_calls": 0}
    row.update(kw)
    return row


def spend_for(rows_tokens):
    return {t: raw_row(tok) for t, tok in rows_tokens}


def spend_file(spend, logs):
    """A schema /2 spend doc bound to `logs` (as arena_spend.meter writes it), window covering every record."""
    ts = [AA._ep(r) for lg in logs.values() for r in lg.get("recs", ())]
    return {"schema": "arena_task_spend/2", "arms": spend, "overhead": {}, "flags": [], "blocking": [],
            "logs": AA.spend_log_binding(logs), "window": {"since": min(ts), "until": max(ts) + 1}}


def scenario(arms, n, tasks=None, draws=DRAWS, seed=7, **kw):
    """arms: {arm: (token_factor, accept_fn(i)->bool, token_noise_sd)} -> analyse() report."""
    tasks = tasks or make_tasks(n)
    ids = sorted(tasks)[:n]
    rng = random.Random(seed)
    base = {t: math.log(1e5) + rng.gauss(0, 1.0) for t in ids}
    logs, spend = {}, {}
    for j, (arm, (fac, acc, sd)) in enumerate(sorted(arms.items())):
        rows = [(t, acc(i)) for i, t in enumerate(ids)]
        logs[arm] = {"recs": arm_log(arm, rows, offset=j * 7, **kw.pop(arm, {}))}
        spend[arm] = spend_for((t, math.exp(base[t] + rng.gauss(0, sd)) * fac) for t in ids)
    return AA.analyse(logs, tasks, spend, draws=draws, **kw)


def all_acc(_i):
    return True


# ---------------------------------------------------------------- (1) pins

def t_pins():
    want = {"BLOCK": 5, "MIN_TASKS": 10, "MIN_KINDS": 2, "DECIDE_RATIO": 1.25, "DECIDE_P": 0.95,
            "ACCEPT_MARGIN": 0.15, "ACCEPT_P": 0.2, "FUTILE_RATIO": 1.1, "FUTILE_P": 0.05, "TIE_BAND": 0.15,
            "TIE_P": 0.9, "SIMPLER": ("ralph_a", "ralph_c", "trio", "v3c", "v3"), "CONTROL": "v3", "ERAS": 3}
    bad = {k: getattr(AA, k) for k, v in want.items() if getattr(AA, k) != v}
    check("pins: section 4.1 thresholds are the owner's numbers", not bad, bad)


# ---------------------------------------------------------------- (2) rule boundaries, literal numbers

def fake(le, th):
    return {"le": {a: list(v) for a, v in le.items()}, "theta": {a: list(v) for a, v in th.items()}}


def t_rule_probs():
    n = 100
    th = {"trio": [0.8] * n, "v3": [0.8] * n}
    p = AA.rule_probs(fake({"trio": [math.log(1.25 * 1.04)] * n, "v3": [0.0] * n}, th), ["trio", "v3"], ["trio", "v3"])
    check("decide ratio: 1.30x counts as >= 1.25x", p["decide"]["trio"] == 1.0, p["decide"])
    p = AA.rule_probs(fake({"trio": [math.log(1.25 * 0.96)] * n, "v3": [0.0] * n}, th), ["trio", "v3"], ["trio", "v3"])
    check("decide ratio: 1.20x does not", p["decide"]["trio"] == 0.0, p["decide"])
    # best OTHER: a third arm at 1.2x raises the bar for trio at 1.3x (1.3/1.2 < 1.25)
    p = AA.rule_probs(fake({"trio": [math.log(1.3)] * n, "v3": [0.0] * n, "v3c": [math.log(1.2)] * n},
                           dict(th, v3c=[0.8] * n)), ["trio", "v3", "v3c"], ["trio", "v3", "v3c"])
    check("decide compares to the best OTHER arm, not the control", p["decide"]["trio"] == 0.0, p["decide"])
    p = AA.rule_probs(fake({"trio": [0.0] * n, "v3": [0.0] * n}, {"trio": [0.8 - 0.155] * n, "v3": [0.8] * n}),
                      ["trio", "v3"], ["trio", "v3"])
    check("accept margin: 0.155 worse counts as >= 0.15", p["accept_worse"]["trio"] == 1.0, p["accept_worse"])
    p = AA.rule_probs(fake({"trio": [0.0] * n, "v3": [0.0] * n}, {"trio": [0.8 - 0.145] * n, "v3": [0.8] * n}),
                      ["trio", "v3"], ["trio", "v3"])
    check("accept margin: 0.145 worse does not", p["accept_worse"]["trio"] == 0.0, p["accept_worse"])
    p = AA.rule_probs(fake({"trio": [math.log(1.1 * 1.03)] * n, "v3": [0.0] * n}, th), ["trio", "v3"], ["trio", "v3"])
    check("futility ratio: 1.133x counts as >= 1.1x control", p["futile"]["trio"] == 1.0, p["futile"])
    p = AA.rule_probs(fake({"trio": [math.log(1.1 * 0.97)] * n, "v3": [0.0] * n}, th), ["trio", "v3"], ["trio", "v3"])
    check("futility ratio: 1.067x does not", p["futile"]["trio"] == 0.0, p["futile"])
    check("the control is never futile against itself", "v3" not in p["futile"], p["futile"])
    p = AA.rule_probs(fake({"trio": [math.log(1.14)] * n, "v3": [0.0] * n}, th), ["trio", "v3"], ["trio", "v3"])
    check("tie band: 14% apart is inside 15%", p["tie"] == 1.0, p["tie"])
    p = AA.rule_probs(fake({"trio": [math.log(1.16)] * n, "v3": [0.0] * n}, th), ["trio", "v3"], ["trio", "v3"])
    check("tie band: 16% apart is outside", p["tie"] == 0.0, p["tie"])
    p = AA.rule_probs(fake({"trio": [1.0] * n, "v3": [0.0] * n, "ralph_a": [2.0] * n},
                           dict(th, ralph_a=[0.8] * n)), ["trio", "v3"], ["trio", "v3", "ralph_a"])
    check("tie leaders come from arms in contention only", sorted(p["leaders"]) == ["trio", "v3"], p["leaders"])


def probs(decide=None, aw=None, futile=None, tie=None, leaders=("trio", "v3")):
    return {"decide": decide or {}, "accept_worse": aw or {}, "futile": futile or {}, "tie": tie,
            "leaders": list(leaders) if tie is not None else None}


def t_rule_verdict():
    v = AA.rule_verdict(probs({"trio": 0.96}, {"trio": 0.1}), True)[0]
    check("DECIDE when P > 0.95 (0.96)", v == "DECIDE_FOR_trio", v)
    v = AA.rule_verdict(probs({"trio": 0.94}, {"trio": 0.1}), True)[0]
    check("no DECIDE at P 0.94", v == "CONTINUE", v)
    v = AA.rule_verdict(probs({"trio": 0.95}, {"trio": 0.1}), True)[0]
    check("no DECIDE at exactly 0.95 (strict >)", v == "CONTINUE", v)
    v = AA.rule_verdict(probs({"trio": 0.99}, {"trio": 0.19}), True)[0]
    check("DECIDE when P(accept worse) 0.19 < 0.2", v == "DECIDE_FOR_trio", v)
    v = AA.rule_verdict(probs({"trio": 0.99}, {"trio": 0.21}), True)[0]
    check("accept guard blocks DECIDE at 0.21", v == "CONTINUE", v)
    v = AA.rule_verdict(probs({"trio": 0.99}, {}), False)[0]
    check("no control data -> no DECIDE", v == "CONTINUE", v)
    v = AA.rule_verdict(probs(futile={"trio": 0.04}), True)
    check("FUTILE when P(>=1.1x control) 0.04 < 0.05", v[0] == "FUTILE" and v[1]["arms"] == ["trio"], v)
    v = AA.rule_verdict(probs(futile={"trio": 0.06}), True)[0]
    check("not futile at 0.06", v == "CONTINUE", v)
    v = AA.rule_verdict(probs(tie=0.91), True)
    check("TIE at P 0.91 > 0.9, simpler (trio) wins over v3", v[0] == "TIE" and v[1]["winner"] == "trio", v)
    v = AA.rule_verdict(probs(tie=0.89), True)[0]
    check("no TIE at 0.89", v == "CONTINUE", v)
    v = AA.rule_verdict(probs(tie=0.95, leaders=("v3", "v3c")), True)
    check("TIE v3 vs v3c -> v3c (simpler)", v[1].get("winner") == "v3c", v)
    v = AA.rule_verdict(probs(tie=0.95, leaders=("ralph_c", "ralph_a")), True)
    check("TIE ralph_c vs ralph_a -> ralph_a", v[1].get("winner") == "ralph_a", v)
    v = AA.rule_verdict(probs(tie=0.95, leaders=("mystery", "v3")), True)[0]
    check("TIE with an arm outside the order -> UNMEASURED", v == "UNMEASURED", v)
    v = AA.rule_verdict(probs({"trio": 0.99}, {"trio": 0.0}, {"v3c": 0.0}), True)[0]
    check("precedence: DECIDE before FUTILE", v == "DECIDE_FOR_trio", v)


# ---------------------------------------------------------------- (3) tokens and fail-closed input

def t_tokens_and_inputs():
    conv = AA.default_conv()
    full = {"claude": {OPUS: {"input": 100, "cache_read": 1000, "cache_write_5m": 8, "cache_write_1h": 5,
                              "output": 10}}, "gpt": {"tokens": 50, "in_est": 0, "out_est": 0}}
    tok, why = AA.task_tokens(full, conv)
    check("raw opus 100 in + 0.1x1000 read + 1.25x8 + 2x5 + 5x10 out = 270, + 50 gpt = 320", tok == 320.0, (tok, why))
    tok, why = AA.task_tokens(R({"claude-sonnet-4-5": {"input": 1000}}), conv)
    check("sonnet raw 1000 in -> 600 (model weight 0.6)", tok == 600.0, (tok, why))
    tok, why = AA.task_tokens(R({"claude-haiku-4-5": {"output": 100}}), conv)
    check("haiku raw 100 out -> 100 (0.2 x 5)", tok == 100.0, (tok, why))
    tok, why = AA.task_tokens(R(gpt={"tokens": 0, "in_est": 40, "out_est": 10}), conv)
    check("gpt estimate 40 in + 5x10 out = 90", tok == 90.0, (tok, why))
    c2 = dict(conv, gpt_tokens=2.0, claude_scale=3.0)
    tok, why = AA.task_tokens(R({OPUS: {"input": 10}}, {"tokens": 50}), c2)
    check("conversion factors apply at analysis time: 3x10 + 2x50 = 130", tok == 130.0, (tok, why))
    c3 = dict(conv, claude_model=dict(conv["claude_model"], sonnet=0.5))
    tok, why = AA.task_tokens(R({"claude-sonnet-4-5": {"input": 1000}}), c3)
    check("a model weight is changed without re-metering: sonnet 0.5 -> 500", tok == 500.0, (tok, why))
    tok, why = AA.task_tokens(R({OPUS: {"input": 100}}, claude_ite=99999), conv)
    check("the derived claude_ite column is ignored (raw wins)", tok == 100.0, (tok, why))
    tok, why = AA.task_tokens({"claude_ite": 500, "gpt_ite": 0, "gpt_ite_est": 0}, conv)
    check("a row with only derived/merged ITE (no raw per-model counts) is refused", tok is None and "raw" in why,
          why)
    tok, why = AA.task_tokens({"total_ite_mixed": 500}, conv)
    check("merged-only spend row refused", tok is None and "raw" in why, why)
    tok, why = AA.task_tokens(R({"gemini-x": {"input": 10}}), conv)
    check("an unknown Claude model with tokens is refused (no silent weight)", tok is None and "model" in why, why)
    tok, why = AA.task_tokens(R({"<synthetic>": {"input": 0, "output": 0}, OPUS: {"input": 7}}), conv)
    check("an unknown model with zero tokens is harmless", tok == 7.0, (tok, why))
    tok, why = AA.task_tokens(R({OPUS: {"input": 10, "reasoning": 5}}), conv)
    check("an unweighted token field is refused", tok is None and "reasoning" in why, why)
    tok, why = AA.task_tokens(raw_row(100, ambiguous_calls=2), conv)
    check("a task with calls that overlapped another task's span is refused", tok is None and "ambiguous" in why,
          why)
    tok, why = AA.task_tokens(R({OPUS: {"input": 0}}), conv)
    check("zero tokens refused", tok is None and "zero" in why, why)
    tok, why = AA.task_tokens(R({OPUS: {"input": -5}}), conv)
    check("negative tokens refused", tok is None, why)
    tok, why = AA.task_tokens(R({OPUS: {"input": True}}), conv)
    check("boolean tokens refused", tok is None, why)
    tok, why = AA.task_tokens(R(gpt={"tokens": float("nan")}), conv)
    check("non-finite gpt tokens refused", tok is None, why)
    r = AA.analyse({}, {}, {})
    check("empty log -> UNMEASURED", r["final"]["verdict"] == "UNMEASURED", r["final"])
    tasks = make_tasks(10)
    ids = sorted(tasks)
    logs = {"trio": {"recs": arm_log("trio", [(t, True) for t in ids])}, "v3": {"recs": []}}
    sp = {"trio": spend_for((t, 1e5) for t in ids), "v3": {}}
    r = AA.analyse(logs, tasks, sp, draws=200)
    check("an arm with zero rows -> UNMEASURED", r["final"]["verdict"] == "UNMEASURED"
          and r["arms"].get("v3", {}).get("status") == "UNMEASURED", r["final"])
    logs["v3"] = {"recs": arm_log("v3", [(t, True) for t in ids])}
    sp["v3"] = spend_for((t, 1e5) for t in ids[:-1])
    r = AA.analyse(logs, tasks, sp, draws=200)
    check("a completed task with no spend row -> UNMEASURED", r["final"]["verdict"] == "UNMEASURED",
          r["final"].get("why"))
    sp["v3"] = spend_for((t, 1e5) for t in ids)
    r = AA.analyse(logs, {k: v for k, v in tasks.items() if k != ids[3]}, sp, draws=200)
    check("a completed task with no frozen spec -> UNMEASURED", r["final"]["verdict"] == "UNMEASURED",
          r["final"].get("why"))
    r = AA.analyse(dict(logs, v3c={"unmeasured": "eventlog refused: x"}), tasks, sp, draws=200)
    check("a refused arm makes the whole result UNMEASURED", r["final"]["verdict"] == "UNMEASURED", r["final"])
    logs2 = {"trio": logs["trio"], "v3": {"recs": [dict(x, ite=123) for x in logs["v3"]["recs"]]}}
    r = AA.analyse(logs2, tasks, sp, draws=200)
    check("a record `ite` is ignored and counted", r["merged_ite_records"] == len(logs["v3"]["recs"]),
          r["merged_ite_records"])
    with tempfile.TemporaryDirectory() as d:
        Path(d, "trio.jsonl").write_text("\n".join(json.dumps(x) for x in logs["trio"]["recs"]) + "\n")
        Path(d, "v3.jsonl").write_text(json.dumps(logs["v3"]["recs"][0]) + "\n{not json\n")
        Path(d, "v3c.jsonl").write_text(json.dumps(dict(logs["v3"]["recs"][0], arm="v3c", ts="2026-11-01T00:00:00"))
                                        + "\n")
        raw = AA.load_raw(d)
    check("load_raw: a good arm loads", "recs" in raw.get("trio", {}) and len(raw["trio"]["recs"]) == 60,
          {k: list(v) for k, v in raw.items()})
    check("load_raw: an unparseable line -> arm UNMEASURED", "unmeasured" in raw.get("v3", {}), raw.get("v3"))
    check("load_raw: a zoneless ts -> arm UNMEASURED (for the ts, not an arm mismatch)",
          "unmeasured" in raw.get("v3c", {}) and "record arm" not in raw["v3c"]["unmeasured"], raw.get("v3c"))


def t_cli():
    tasks = make_tasks(10)
    ids = sorted(tasks)
    with tempfile.TemporaryDirectory() as d:
        for arm in ("trio", "v3"):
            Path(d, arm + ".jsonl").write_text("\n".join(json.dumps(x) for x in
                                                         arm_log(arm, [(t, True) for t in ids])) + "\n")
        td = Path(d, "tasks")
        td.mkdir()
        import subprocess
        shas = subprocess.run(["git", "-C", str(AA.A.REPO), "rev-list", "-n", str(len(ids)), "HEAD"],
                              capture_output=True, text=True, timeout=60).stdout.split()
        for (t, v), b in zip(sorted(tasks.items()), shas):     # real bases: the CLI computes chrono with git
            Path(td, t + ".json").write_text(json.dumps(dict(v, id=t, base_sha=b)))
        Path(d, "trial.txt").write_text("\n".join(ids) + "\n")
        sp = {a: spend_for((t, 1e5) for t in ids) for a in ("trio", "v3")}
        logs = AA.load_raw(d)
        Path(d, "spend.json").write_text(json.dumps(spend_file(sp, logs)))
        Path(d, "bare.json").write_text(json.dumps(sp))
        old = dict(spend_file(sp, logs), schema="arena_task_spend/1")
        Path(d, "old.json").write_text(json.dumps(old))
        stale = spend_file(sp, {a: {"recs": lg["recs"][:-1]} for a, lg in logs.items()})
        Path(d, "stale.json").write_text(json.dumps(stale))
        blk = dict(spend_file(sp, logs), blocking=["meter unreadable_files: 1"])
        Path(d, "blk.json").write_text(json.dumps(blk))
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            tl = ["--trial-tasks", str(Path(d, "trial.txt"))]
            rc = AA.main(["run", "--spend", str(Path(d, "spend.json")), "--raw-dir", d, "--tasks-dir", str(td),
                          "--draws", "300", "--out", str(Path(d, "out.json"))] + tl)
            rc_def = AA.main(["run", "--spend", str(Path(d, "spend.json")), "--raw-dir", d, "--tasks-dir", str(td),
                              "--draws", "300", "--out", str(Path(d, "out_def.json"))])
            rc_nol = AA.main(["run", "--spend", str(Path(d, "spend.json")), "--raw-dir", d, "--tasks-dir", str(td),
                              "--draws", "300", "--trial-tasks", str(Path(d, "nolist.txt"))])
            rc2 = AA.main(["run", "--spend", str(Path(d, "nope.json")), "--raw-dir", d, "--tasks-dir", str(td),
                           "--draws", "300"])
            rc3 = AA.main(["run", "--spend", str(Path(d, "bare.json")), "--raw-dir", d, "--tasks-dir", str(td),
                           "--draws", "300"])
            rc4 = AA.main(["run", "--spend", str(Path(d, "spend.json")), "--raw-dir", d, "--tasks-dir", str(td),
                           "--draws", "300", "--claude-model-weight", "opus=0.5", "--gpt-est-out-to-ite", "4",
                           "--out", str(Path(d, "out4.json"))] + tl)
            for n, txt in (("jnull", "null"), ("jint", "123"), ("jtrue", "true"), ("jstr", '"unreadable"'),
                           ("jlist", "[]")):
                Path(d, n + ".json").write_text(txt)
            rcs = {}
            for n in ("old", "stale", "blk", "jnull", "jint", "jtrue", "jstr", "jlist"):
                try:
                    rcs[n] = AA.main(["run", "--spend", str(Path(d, n + ".json")), "--raw-dir", d, "--tasks-dir",
                                      str(td), "--draws", "300"])
                except Exception as e:                      # noqa: BLE001
                    rcs[n] = "crash %r" % e
        out = json.loads(Path(d, "out.json").read_text())
        out4 = json.loads(Path(d, "out4.json").read_text()) if Path(d, "out4.json").is_file() else {}
        out_def = json.loads(Path(d, "out_def.json").read_text())
    check("CLI: runs end to end on raw logs and writes the report", rc == 0 and "final" in out and out["blocks"],
          (rc, out.get("final", {}).get("verdict")))
    check("CLI: chrono comes from git for the listed tasks (era gate MEASURED over the 10 listed)",
          out.get("era_gate", {}).get("status") == "MEASURED" and out["era_gate"]["trial_tasks"] == 10,
          out.get("era_gate"))
    check("CLI: no --trial-tasks -> the committed default list, never every frozen task: here its ids have no "
          "spec in the test bank -> UNMEASURED, exit 3, blocks withheld",
          rc_def == 3 and "no frozen spec" in out_def["final"].get("why", "") and out_def["blocks"] == [],
          (rc_def, out_def["final"]))
    check("CLI: a missing --trial-tasks file -> UNMEASURED, exit 3", rc_nol == 3, rc_nol)
    check("CLI: unreadable spend file -> UNMEASURED, exit 3", rc2 == 3, rc2)
    check("CLI: a spend file without the arena_task_spend/2 schema -> UNMEASURED, exit 3", rc3 == 3, rc3)
    check("CLI: an old /1 doc, a doc metered against another log (stale), and a doc with blocking meter problems "
          "-> each UNMEASURED, exit 3; so does a JSON scalar/list document (r2#6), without a crash",
          set(rcs.values()) == {3} and len(rcs) == 8, rcs)
    check("CLI: conversion overrides reach the report", rc4 == 0 and out4["conversion"]["claude_model"]["opus"] == 0.5
          and out4["conversion"]["gpt_out_est"] == 4.0, out4.get("conversion"))


# ------------------------------------------------- stray / stale arm logs (ARENA_ANALYSIS_FIX_STRAY_LOGS_VOID_VERDICT)

def _signed_lines(arm, recs, tok, stale=(), tail=()):
    """stale unsigned prefix lines + a real HMAC chain from GENESIS + unsigned tail lines (raw strings)."""
    L, prev, out = AA.L, AA.L.GENESIS, [json.dumps(x) for x in stale]
    for r in recs:
        r = dict(r)
        r["sig"] = L._sign(tok, prev, r)
        prev = r["sig"]
        out.append(json.dumps(r, sort_keys=True))
    return out + [json.dumps(x) for x in tail]


def _fake_eventlog(files, tok):
    """{arm: [raw lines]} -> (report, verify) stand-ins over the REAL verify_lines chain check."""
    def verify(_p, arm, _token=None):
        return dict(AA.L.verify_lines(files[arm], tok, arm), undecodable=0)

    def report(_p, _token=None, _external=None):
        out = {}
        for arm in files:
            v = verify(None, arm)
            out[arm] = {"accepted": len(v["accepted"]), "rejected": len(v["rejected"]),
                        "recoverable": len(v["recoverable"]), "undecodable_lines": 0, "trusted": bool(v["accepted"])}
        return out
    return report, verify


def t_stray_logs():
    tasks = make_tasks(10)
    ids = sorted(tasks)
    arms = ("ralph_a", "trio", "v3")
    tok = "k" * 64
    import contextlib
    import io
    import subprocess
    with tempfile.TemporaryDirectory() as d:
        clean, stray = Path(d, "clean"), Path(d, "stray")
        clean.mkdir(); stray.mkdir()
        recs = {a: arm_log(a, [(t, True) for t in ids], offset=j * 7) for j, a in enumerate(arms)}
        for dd in (clean, stray):
            for a in arms:
                Path(dd, a + ".jsonl").write_text("\n".join(json.dumps(x) for x in recs[a]) + "\n")
        # the live leftovers: a non-replayed lane arm's log with probe lines, plus a junk line no reader accepts
        Path(stray, "ralph_c.jsonl").write_text(json.dumps({"ts": "2026-10-30T02:59:22Z", "arm": "ralph_c",
                                                            "event": "canary"}) + "\n{not json\n")
        td = Path(d, "tasks")
        td.mkdir()
        shas = subprocess.run(["git", "-C", str(AA.A.REPO), "rev-list", "-n", str(len(ids)), "HEAD"],
                              capture_output=True, text=True, timeout=60).stdout.split()
        for (t, v), b in zip(sorted(tasks.items()), shas):
            Path(td, t + ".json").write_text(json.dumps(dict(v, id=t, base_sha=b)))
        Path(d, "trial.txt").write_text("\n".join(ids) + "\n")
        sp = {a: spend_for((t, 1e5 * (2.0 if a == "ralph_a" else 1.0)) for t in ids) for a in arms}
        Path(d, "spend.json").write_text(json.dumps(spend_file(sp, AA.load_raw(clean))))
        nocfg = str(Path(d, "no-arm.toml"))
        Path(d, "bad.toml").write_text("mode = [broken\n")
        common = ["--spend", str(Path(d, "spend.json")), "--tasks-dir", str(td), "--draws", "300",
                  "--trial-tasks", str(Path(d, "trial.txt"))]

        def run(extra, name, **patch):
            saved = {k: getattr(AA, k) for k in patch}
            try:
                for k, v in patch.items():
                    setattr(AA, k, v)
                with contextlib.redirect_stdout(io.StringIO()):
                    rc = AA.main(["run"] + common + extra + ["--out", str(Path(d, name + ".json"))])
            finally:
                for k, v in saved.items():
                    setattr(AA, k, v)
            return rc, json.loads(Path(d, name + ".json").read_text())

        rc0, base = run(["--raw-dir", str(clean), "--arm-config", nocfg], "base")
        rc1, got = run(["--raw-dir", str(stray), "--arm-config", nocfg], "stray")
        rcm, mut = run(["--raw-dir", str(stray), "--arm-config", nocfg], "mut_arms",
                       restrict_arms=lambda logs, a: (dict(logs), []))
        rcb, bad = run(["--raw-dir", str(clean), "--arm-config", str(Path(d, "bad.toml"))], "badcfg")
        rcx, onl = run(["--raw-dir", str(stray), "--arms", "trio,v3"], "only2")

        # signed path: trio.jsonl starts with 311-style unsigned probe lines from BEFORE the trial
        old = [{"ts": "2026-10-30T%02d:00:00Z" % (4 + i % 14), "arm": "trio", "event": "canary", "lane": "steve",
                "run_id": "trio-archmagi-x", "writer": "arena_lane"} for i in range(311)]
        files = {a: _signed_lines(a, recs[a], tok) for a in arms}
        files["trio"] = _signed_lines("trio", recs["trio"], tok, stale=old)
        files["ralph_c"] = [json.dumps({"ts": "2026-10-30T02:59:22Z", "arm": "ralph_c", "event": "canary"})] * 27
        rep_fn, ver_fn = _fake_eventlog(files, tok)
        saved = (AA.L.report, AA.L.verify)
        AA.L.report, AA.L.verify = rep_fn, ver_fn
        try:
            sig_logs = AA.load_verified(p={"root": d})
            Path(d, "spend_sig.json").write_text(json.dumps(spend_file(
                sp, {a: sig_logs[a] for a in arms})))
            common[1] = str(Path(d, "spend_sig.json"))
            rcs, sig = run(["--arm-config", nocfg], "signed")
            rcsm, sigm = run(["--arm-config", nocfg], "signed_mut", stale_prefix=lambda v: None)
            neg = {}
            first = recs["trio"][0]["ts"]
            for name, kw in (("junk after the trial's records", {"tail": [old[0]]}),
                             ("a prefix line dated at/after the first record", {"stale": [dict(old[0], ts=first)]}),
                             ("a prefix line carrying a sig", {"stale": [dict(old[0], sig="ab" * 32)]})):
                files["trio"] = _signed_lines("trio", recs["trio"], tok, **kw)
                neg[name] = AA.load_verified(p={"root": d}).get("trio", {})
        finally:
            AA.L.report, AA.L.verify = saved
    fv = lambda r: r["final"]["verdict"]   # noqa: E731
    check("stray: baseline (3 replay arms, ralph_a 2x tokens) reaches a verdict", rc0 != 3 and
          not fv(base).startswith("UNMEASURED"), (rc0, base["final"]))
    check("stray: a planted non-replayed ralph_c.jsonl (with a junk line) is ignored: same verdict as without it, "
          "listed in ignored_arms", (rc1, fv(got)) == (rc0, fv(base)) and got["replay_arms"]["ignored_arms"] ==
          ["ralph_c"] and got["replay_arms"]["arms"] == list(arms), (rc1, got["final"], got.get("replay_arms")))
    check("stray MUTANT: keeping every arm's log (no replay filter) -> UNMEASURED, so the row above has teeth",
          rcm == 3 and fv(mut).startswith("UNMEASURED"), (rcm, mut["final"]))
    check("stray: an arm.toml that exists but does not parse -> UNMEASURED, blocks withheld",
          rcb == 3 and "replay arms unknown" in bad["final"].get("why", "") and bad["blocks"] == [], bad["final"])
    check("stray: --arms overrides the replay set (trio,v3 only; ralph_a and ralph_c ignored)",
          onl["replay_arms"]["ignored_arms"] == ["ralph_a", "ralph_c"] and rcx != 3, (rcx, onl.get("replay_arms")))
    check("stale: trio's 311 unsigned pre-trial lines are skipped and counted, every signed record kept",
          sig_logs["trio"].get("stale_prefix") == 311 and len(sig_logs["trio"].get("recs", ())) == len(recs["trio"]),
          {k: sorted(v) for k, v in sig_logs.items()})
    check("stale: the signed run with stale trio + stray ralph_c gives the baseline verdict, not UNMEASURED",
          (rcs, fv(sig)) == (rc0, fv(base)) and sig["replay_arms"]["stale_prefix"] == {"trio": 311},
          (rcs, sig["final"], sig.get("replay_arms")))
    check("stale MUTANT: treating the stale prefix as tampering (old behaviour) -> UNMEASURED",
          rcsm == 3 and fv(sigm).startswith("UNMEASURED"), (rcsm, sigm["final"]))
    for name, lg in neg.items():
        check("stale: %s is NOT a leftover -> trio UNMEASURED" % name, "unmeasured" in lg and "recs" not in lg, lg)


# ---------------------------------------------------------------- (4) scenarios

def t_winner():
    r = scenario({"trio": (0.25, all_acc, 0.1), "v3": (1.0, all_acc, 0.1)}, 20)
    b = r["blocks"]
    check("winner: block 1 (5 tasks) is below the minimum, not a stop",
          b[0]["verdict"] == "UNMEASURED" and "below_minimum" in b[0], b[0].get("verdict"))
    check("winner: DECIDE_FOR_trio at block 2 (10 tasks, 2 kinds)",
          r["final"]["verdict"] == "DECIDE_FOR_trio" and r["final"]["block"] == 2 and b[1]["tasks_per_arm"] == 10,
          (r["final"]["verdict"], r["final"].get("block")))
    one_kind = make_tasks(20, kinds=lambda i: KINDS[0] if i < 10 else KINDS[1])
    r = scenario({"trio": (0.25, all_acc, 0.1), "v3": (1.0, all_acc, 0.1)}, 20, tasks=one_kind)
    check("winner on one kind for 10 tasks: no stop until a 2nd kind (block 3)",
          r["final"]["verdict"] == "DECIDE_FOR_trio" and r["final"]["block"] == 3,
          (r["final"]["verdict"], r["final"].get("block")))
    r = scenario({"trio": (0.25, all_acc, 0.1), "v3": (1.0, all_acc, 0.1)}, 9)
    check("winner with 9 tasks per arm: never decides", not r["final"]["verdict"].startswith("DECIDE"),
          r["final"]["verdict"])
    worse = scenario({"trio": (0.25, lambda i: i % 2 == 0, 0.1), "v3": (1.0, all_acc, 0.1)}, 20)
    check("winner on tokens but accepting far less: accept guard blocks DECIDE",
          not worse["final"]["verdict"].startswith("DECIDE"), worse["final"]["verdict"])


def t_fluke():
    # a fluke: the first 5 tasks of trio cost a tenth
    tasks = make_tasks(5)
    ids = sorted(tasks)
    logs = {a: {"recs": arm_log(a, [(t, True) for t in ids], offset=j)} for j, a in enumerate(("trio", "v3"))}
    sp = {"trio": spend_for((t, 1e4) for t in ids), "v3": spend_for((t, 1e5) for t in ids)}
    r = AA.analyse(logs, tasks, sp, draws=DRAWS)
    check("early fluke (10x after 5 tasks): block 1 UNMEASURED(below minimum), final UNMEASURED, no stop",
          r["blocks"] and r["blocks"][0]["verdict"] == "UNMEASURED" and r["final"]["verdict"] == "UNMEASURED",
          (r["blocks"][0].get("verdict") if r["blocks"] else None, r["final"]["verdict"]))
    r = AA.analyse(logs, tasks, sp, draws=DRAWS, final=True)
    check("early fluke at the hard cap: UNMEASURED(below minimum), never DECIDE or HARD_CAP",
          r["final"]["verdict"] == "UNMEASURED" and "below_minimum" in r["final"]["detail"], r["final"]["verdict"])


def t_loser():
    r = scenario({"ralph_a": (4.0, all_acc, 0.1), "trio": (1.0, all_acc, 0.1), "v3": (1.0, all_acc, 0.1)}, 20)
    fut = [b for b in r["blocks"] if b.get("rule_verdict") == "FUTILE"]
    check("clear loser: FUTILE(ralph_a) at block 2", bool(fut) and fut[0]["block"] == 2
          and fut[0]["detail"]["arms"] == ["ralph_a"], [(b["block"], b.get("verdict")) for b in r["blocks"]])
    check("clear loser: not futile before the minimum", r["blocks"][0]["verdict"] == "UNMEASURED",
          r["blocks"][0].get("verdict"))
    check("futile arm is dropped and reported", r["final"].get("futile") == ["ralph_a"], r["final"].get("futile"))


def t_tie():
    r = scenario({"trio": (1.0, all_acc, 0.02), "v3": (1.0, all_acc, 0.02)}, 60)
    check("equal arms tie, the simpler arm (trio) wins",
          r["final"]["verdict"] == "TIE" and r["final"]["detail"].get("winner") == "trio",
          (r["final"]["verdict"], r["final"].get("block"), r["final"].get("detail")))
    check("tie fires only at/after the minimum", r["final"].get("block", 0) >= 2, r["final"].get("block"))
    r = scenario({"v3c": (1.0, all_acc, 0.02), "v3": (1.0, all_acc, 0.02)}, 60)
    check("equal v3c / v3 tie -> v3c", r["final"]["detail"].get("winner") == "v3c", r["final"].get("detail"))


def t_hardcap_determinism():
    rng_acc = lambda i: (i * 7) % 10 < 6  # noqa: E731
    r = scenario({"trio": (1.0, rng_acc, 0.8), "v3": (1.0, rng_acc, 0.8)}, 15, final=True)
    check("noisy equal arms at the hard cap: a hard-cap verdict (pick or no difference) with intervals",
          r["final"]["verdict"] in ("HARD_CAP_PICK", "HARD_CAP_NO_DIFFERENCE") and "eff_vs_control_90" in r["final"]["intervals"]["trio"],
          r["final"]["verdict"])
    cap = T0 + 12 * 600
    r = scenario({"trio": (1.0, rng_acc, 0.8), "v3": (1.0, rng_acc, 0.8)}, 15, hard_cap=cap)
    check("records after --hard-cap are ignored and the cap counts as passed",
          r["final"]["verdict"] in ("HARD_CAP_PICK", "HARD_CAP_NO_DIFFERENCE")
          and r["final"]["intervals"]["trio"]["completed"] <= 12, r["final"].get("intervals", {}).get("trio"))
    a = json.dumps(scenario({"trio": (0.8, rng_acc, 0.5), "v3": (1.0, rng_acc, 0.5)}, 20, seed=3), sort_keys=True)
    b = json.dumps(scenario({"trio": (0.8, rng_acc, 0.5), "v3": (1.0, rng_acc, 0.5)}, 20, seed=3), sort_keys=True)
    check("deterministic: same log and seed -> identical report", a == b)


# ---------------------------------------------------------------- (5) disqualification

ARMS3 = ("trio", "v3", "v3c")


def dq_run(arm_kw, n=10, final=False):
    tasks = make_tasks(n)
    ids = sorted(tasks)
    logs, sp = {}, {}
    for j, a in enumerate(ARMS3):
        logs[a] = {"recs": arm_log(a, [(t, True) for t in ids], offset=j, **arm_kw.get(a, {}))}
        sp[a] = spend_for((t, 1e5 * (1 + 0.01 * j)) for t in ids)
    return AA.analyse(logs, tasks, sp, draws=500, final=final)


def t_dq():
    r = dq_run({})
    check("clean logs: publish/scope/lane/tester not VIOLATED for any arm",
          all(c["status"] != "VIOLATED" for d in r["dq"].values() for c in d.values()), r["dq"])
    check("standing ruling is always UNMEASURED and listed", all(r["dq_unmeasured"][a] == ["ruling"] for a in ARMS3),
          r["dq_unmeasured"])
    r = dq_run({"trio": {"drop": {(1, "gate")}}})
    check("publish: judged work with no gate pass -> DISQUALIFIED(trio, publish) at block 1 (minimum exempt)",
          r["dq"]["trio"]["publish"]["status"] == "VIOLATED" and r["blocks"][0]["verdict"] == "DISQUALIFIED"
          and r["blocks"][0]["disqualified"] == {"trio": ["publish"]}, r["blocks"][0] if r["blocks"] else r["final"])
    check("a disqualified arm is out of the intervals", "trio" not in r["final"].get("intervals", {}),
          list(r["final"].get("intervals", {})))
    recs = arm_log("trio", [("T000", True)])
    for x in recs:
        if x["event"] == "gate":
            x["verdict"] = "fail"
    check("publish: gate FAILED then judged -> VIOLATED", AA.dq_publish(AA.L.ordered(recs))["status"] == "VIOLATED")
    recs = arm_log("trio", [("T000", True)])
    for x in recs:
        if x["event"] == "judge":
            x.pop("sha")
    check("publish: judge with no sha -> UNMEASURED", AA.dq_publish(AA.L.ordered(recs))["status"] == "UNMEASURED")
    recs = arm_log("trio", [("T000", True)])
    for x in recs:
        if x["event"] == "gate":
            x["detail"]["steps"]["scope"] = "FAIL"
    r = AA.dq_scope(AA.L.ordered(recs))
    check("scope: gate scope FAIL -> VIOLATED", r["status"] == "VIOLATED", r)
    r = AA.dq_scope(AA.L.ordered(arm_log("trio", [("T000", True)], drop={(0, "gate")})))
    check("scope: no gate event -> UNMEASURED", r["status"] == "UNMEASURED", r)
    t = T0 + 50

    def lane(evs):
        return [{"ts": iso(t + k), "arm": "trio", "lane": "LIVE", "run_id": "trio.0", "task": "T000", "event": e,
                 "verdict": v} for k, (e, v) in enumerate(evs)]
    r = AA.dq_lane(AA.L.ordered(lane([("live_take", "ok"), ("live_release", None)])))
    check("lane: held and released with no canary -> VIOLATED", r["status"] == "VIOLATED", r)
    r = AA.dq_lane(AA.L.ordered(lane([("live_take", "ok"), ("canary", "pass"), ("live_release", None)])))
    check("lane: canary inside the hold -> CLEAN", r["status"] == "CLEAN", r)
    r = AA.dq_lane(AA.L.ordered(lane([("live_take", "ok")])))
    check("lane: open hold with no canary yet -> pending, not a violation",
          r["status"] == "CLEAN" and r.get("pending_open_holds") == 1, r)
    r = AA.dq_lane(AA.L.ordered(lane([("live_take", "refused"), ("live_release", None)])))
    check("lane: a refused take is not a hold", r["status"] == "VACUOUS", r)
    rr = dq_run({"v3c": {"extra": [dict(x, run_id="v3c.0") for x in
                                   lane([("live_take", "ok"), ("live_release", None)])]}})
    check("lane: DISQUALIFIED(v3c, lane) through analyse", rr["blocks"][0]["disqualified"] == {"v3c": ["lane"]},
          rr["blocks"][0].get("disqualified") if rr["blocks"] else rr["final"])
    r = dq_run({"trio": {"drop": {(2, "test_start")}}})
    check("tester: new build pass before the last candidate was tested -> DISQUALIFIED(trio, tester)",
          r["dq"]["trio"]["tester"]["status"] == "VIOLATED"
          and r["blocks"][0]["disqualified"] == {"trio": ["tester"]}, r["dq"]["trio"]["tester"])
    recs = arm_log("trio", [("T000", True), ("T001", True)])
    for x in recs:
        if x["event"] == "test_start" and x["task"] == "T000":
            x["detail"]["tester"] = "b-trio-0"
    r = AA.dq_tester(AA.L.ordered(recs))
    check("tester: a same-agent test does not count -> VIOLATED", r["status"] == "VIOLATED", r)
    recs = arm_log("trio", [("T000", True), ("T001", True)], drop={(0, "pass_start"), (1, "pass_start")})
    r = AA.dq_tester(AA.L.ordered(recs))
    check("tester: build_end with no build pass_start -> UNMEASURED", r["status"] == "UNMEASURED", r)
    recs = arm_log("trio", [("T000", True)])
    late = [{"ts": iso(T0 + 5000), "arm": "trio", "lane": "L1", "run_id": "trio.other.1", "task": "T009",
             "event": "pass_start", "detail": {"role": "build", "agent": "z"}}]
    r = AA.dq_tester(AA.L.ordered(recs + late))
    check("tester: a different stream's build pass does not count against this stream", r["status"] == "CLEAN", r)
    r = dq_run({"trio": {"drop": {(8, "gate")}}}, n=10)
    check("a violation after block 1 disqualifies at block 2",
          [b.get("disqualified") for b in r["blocks"]][:2] == [{}, {"trio": ["publish"]}],
          [(b["block"], b.get("disqualified")) for b in r["blocks"]])


# ---------------------------------------------------------------- (5b) review round 1: boundaries, malformed data, chronology

def t_exact_boundaries():
    v = AA.rule_verdict(probs({"trio": 0.99}, {"trio": 0.2}), True)[0]
    check("no DECIDE at P(accept worse) exactly 0.2 (strict <)", v == "CONTINUE", v)
    v = AA.rule_verdict(probs(futile={"trio": 0.05}), True)[0]
    check("not futile at exactly 0.05 (strict <)", v == "CONTINUE", v)
    v = AA.rule_verdict(probs(tie=0.9), True)[0]
    check("no TIE at exactly 0.9 (strict >)", v == "CONTINUE", v)


def winner_logs(n=20, drop=None, extra_trio=(), tasks=None, spend_patch=None):
    tasks = tasks or make_tasks(n)
    ids = sorted(tasks)[:n]
    rng = random.Random(11)
    base = {t: math.log(1e5) + rng.gauss(0, 1.0) for t in ids}
    logs = {"trio": {"recs": arm_log("trio", [(t, True) for t in ids], drop=drop or (), extra=extra_trio)},
            "v3": {"recs": arm_log("v3", [(t, True) for t in ids], offset=7)}}
    sp = {"trio": spend_for((t, math.exp(base[t]) * 0.25) for t in ids), "v3": spend_for((t, math.exp(base[t]))
                                                                                        for t in ids)}
    if spend_patch:
        spend_patch(sp)
    return logs, tasks, sp


def t_malformed():
    logs, tasks, sp = winner_logs()
    r = AA.analyse(logs, tasks, sp, draws=DRAWS)
    check("baseline for malformed cases decides for trio", r["final"]["verdict"] == "DECIDE_FOR_trio",
          r["final"]["verdict"])

    def huge(s):
        s["trio"]["T003"] = raw_row(1e308, gpt={"tokens": 1e308, "in_est": 0, "out_est": 0})
    logs, tasks, sp = winner_logs(spend_patch=huge)
    r = AA.analyse(logs, tasks, sp, draws=500)
    check("overflowing spend (1e308 + 1e308) -> UNMEASURED", r["final"]["verdict"] == "UNMEASURED",
          r["final"].get("why"))
    for bad in ("accpet", None):
        logs, tasks, sp = winner_logs()
        for x in logs["trio"]["recs"]:
            if x["event"] == "judge" and x["task"] == "T019":
                x["verdict"] = bad
        r = AA.analyse(logs, tasks, sp, draws=500)
        check("judge verdict %r -> arm UNMEASURED, not silently dropped" % bad,
              r["final"]["verdict"] == "UNMEASURED", r["final"].get("why"))
    logs, tasks, sp = winner_logs()
    for x in logs["trio"]["recs"]:
        if x["task"] == "T019" and x["event"] in ("gate", "judge"):
            x["task"] = None
    r = AA.analyse(logs, tasks, sp, draws=500)
    check("judge with no task -> UNMEASURED", r["final"]["verdict"] == "UNMEASURED", r["final"].get("why"))
    t2 = make_tasks(20, kinds=lambda i: "python-util" if i % 2 else "not-a-kind")
    logs, tasks, sp = winner_logs(tasks=t2)
    r = AA.analyse(logs, tasks, sp, draws=500)
    check("a kind outside arena_tasks.KINDS -> UNMEASURED", r["final"]["verdict"] == "UNMEASURED",
          r["final"].get("why"))
    t3 = make_tasks(20)
    t3["T004"]["size"] = True
    logs, tasks, sp = winner_logs(tasks=t3)
    r = AA.analyse(logs, tasks, sp, draws=500)
    check("a boolean task size -> UNMEASURED", r["final"]["verdict"] == "UNMEASURED", r["final"].get("why"))


def t_chronology():
    logs, tasks, sp = winner_logs(drop={(18, "gate")})
    r = AA.analyse(logs, tasks, sp, draws=DRAWS)
    check("violation after the stop: the stop stands, reported as violations_after_stop, not disqualified",
          r["final"]["verdict"] == "DECIDE_FOR_trio" and "trio" not in r["final"]["disqualified"]
          and r["final"].get("violations_after_stop") == {"trio": ["publish"]},
          (r["final"]["verdict"], r["final"]["disqualified"], r["final"].get("violations_after_stop")))
    # v3c violates early and then stops completing: the others' blocks are not held up, v3c is out at block 1
    tasks = make_tasks(20)
    ids = sorted(tasks)
    logs, sp = {}, {}
    for j, a in enumerate(ARMS3):
        n = 3 if a == "v3c" else 20
        logs[a] = {"recs": arm_log(a, [(t, True) for t in ids[:n]], offset=j, drop={(1, "gate")} if a == "v3c" else ())}
        sp[a] = spend_for((t, 1e5 * (0.25 if a == "trio" else 1.0)) for t in ids[:n])
    r = AA.analyse(logs, tasks, sp, draws=DRAWS)
    check("an arm short of data that violated earlier does not hold up the blocks",
          r["blocks"] and r["blocks"][0]["disqualified"] == {"v3c": ["publish"]}
          and r["final"]["verdict"] == "DECIDE_FOR_trio",
          ([b.get("disqualified") for b in r["blocks"]], r["final"]["verdict"]))
    # an arm short of data with NO violation is waited for: no block evaluates without it
    logs["v3c"] = {"recs": arm_log("v3c", [(t, True) for t in ids[:3]], offset=2)}
    r = AA.analyse(logs, tasks, sp, draws=DRAWS)
    check("an arm short of data with no violation is waited for (no block, no decision)",
          not r["blocks"] and not r["final"]["verdict"].startswith("DECIDE"), (len(r["blocks"]), r["final"]["verdict"]))


def t_dq_identity():
    recs = arm_log("trio", [("T000", True)])
    for x in recs:
        if x["event"] == "gate":
            x["detail"]["steps"]["scope"] = "ERROR"
    r = AA.dq_scope(AA.L.ordered(recs))
    check("scope: a status other than PASS/FAIL -> UNMEASURED", r["status"] == "UNMEASURED", r)
    recs = arm_log("trio", [("T000", True), ("T001", True)], drop={(0, "pass_start")})
    r = AA.dq_tester(AA.L.ordered(recs))
    check("tester: one build_end without its pass_start -> UNMEASURED", r["status"] == "UNMEASURED", r)
    recs = arm_log("trio", [("T000", True), ("T001", True)], drop={(0, "test_start")})
    for x in recs:
        x.pop("run_id", None)
    r = AA.dq_tester(AA.L.ordered(recs))
    check("tester: no run_id -> UNMEASURED, not a violation", r["status"] == "UNMEASURED", r)
    recs = [{"ts": iso(T0 + k), "arm": "trio", "task": "T000", "event": e, "verdict": v}
            for k, (e, v) in enumerate([("live_take", "ok"), ("canary", "pass"), ("live_release", None)])]
    r = AA.dq_lane(AA.L.ordered(recs))
    check("lane: a hold with no lane/run_id -> UNMEASURED, not CLEAN", r["status"] == "UNMEASURED", r)
    recs = arm_log("trio", [("T000", True)])
    for x in recs:
        if x["event"] == "gate":
            x["sha"] = x["sha"][:7]
    r = AA.dq_publish(AA.L.ordered(recs))
    check("publish: a 7-char gate sha prefix does not identify the judged commit -> VIOLATED", r["status"] == "VIOLATED",
          r)
    recs = arm_log("trio", [("T000", True)])
    for x in recs:
        if x["event"] == "judge":
            x["sha"] = "not-a-sha"
    r = AA.dq_publish(AA.L.ordered(recs))
    check("publish: a malformed judge sha -> UNMEASURED", r["status"] == "UNMEASURED", r)


def _old_dq_publish(seq):
    """The pre-ARENA_PUBLISH_DQ_FIX_PARKED_REJECT_VIOLATES rule (any judge event with no earlier gate pass is a
    violation): the mutant t_publish_parked must catch."""
    gates = [(i, r) for i, r in enumerate(seq) if r["event"] == "gate" and r.get("verdict") == "pass"]
    if not any(r["event"] == "judge" for r in seq):
        return {"status": "VACUOUS"}
    for i, j in enumerate(seq):
        if j["event"] == "judge" and not any(gi < i and g.get("task") == j.get("task")
                                             and AA._sha_eq(g.get("sha"), j.get("sha")) for gi, g in gates):
            return {"status": "VIOLATED", "ts": j["ts"]}
    return {"status": "CLEAN"}


def t_publish_parked():
    """ARENA_PUBLISH_DQ_FIX_PARKED_REJECT_VIOLATES: the runner judges every task, parked and gate-failed ones too."""
    base, head = "ba" * 20, "ce" * 20

    def seq(*evs):
        out = []
        for k, (ev, sha, verdict, detail) in enumerate(evs):
            r = {"ts": iso(T0 + 10 * k), "arm": "trio", "lane": "judge" if ev == "judge" else "gate",
                 "run_id": ev, "task": "T000", "event": ev, "sha": sha, "verdict": verdict}
            if detail is not None:
                r["detail"] = detail
            out.append(r)
        return AA.L.ordered(out)
    B = {"base": base}
    P = {"base": base, "pending": True}
    gf = ("gate", None, "fail", {"steps": {"scope": "PASS"}})
    gp = ("gate", None, "pass", {"steps": {"scope": "PASS"}})

    def g(t, sha):
        return (t[0], sha, t[2], t[3])
    rows = [
        ("parked: gate fail at base, judge reject at base -> CLEAN",
         seq(g(gf, base), ("judge", base, "invalid", P), ("judge", base, "reject", B)), "CLEAN"),
        ("parked: no gate at all, judge reject at base -> CLEAN",
         seq(("judge", base, "reject", B)), "CLEAN"),
        ("parked: judge invalid at base -> CLEAN", seq(g(gf, base), ("judge", base, "invalid", B)), "CLEAN"),
        ("gate-failed: published head, gate fail, judge reject -> CLEAN",
         seq(g(gf, head), ("judge", head, "invalid", P), ("judge", head, "reject", B)), "CLEAN"),
        ("gate-failed: judge reject with no detail.base (gate ran) -> CLEAN",
         seq(g(gf, head), ("judge", head, "reject", None)), "CLEAN"),
        ("pending marker only, no gate -> not VIOLATED (VACUOUS)", seq(("judge", head, "invalid", P)), "VACUOUS"),
        ("pending marker then accept after a gate pass -> CLEAN",
         seq(g(gp, head), ("judge", head, "invalid", P), ("judge", head, "accept", B)), "CLEAN"),
        ("judge ACCEPT after a gate FAIL -> VIOLATED",
         seq(g(gf, head), ("judge", head, "accept", B)), "VIOLATED"),
        ("judge ACCEPT with no gate at all -> VIOLATED", seq(("judge", head, "accept", B)), "VIOLATED"),
        ("judge ACCEPT at base with no gate pass -> VIOLATED", seq(g(gf, base), ("judge", base, "accept", B)),
         "VIOLATED"),
        ("real publish: sha != base, no gate ran, judge reject -> VIOLATED",
         seq(("judge", head, "reject", B)), "VIOLATED"),
        ("real publish: gate ran on a DIFFERENT sha only -> VIOLATED",
         seq(g(gf, base), ("judge", head, "reject", B)), "VIOLATED"),
        ("real publish: gate fail recorded AFTER the judge -> VIOLATED",
         seq(("judge", head, "reject", B), g(gf, head)), "VIOLATED"),
        ("an ACCEPT carrying a stale pending flag is still checked -> VIOLATED",
         seq(("judge", head, "accept", P)), "VIOLATED"),
        ("a pending marker after a violating accept does not erase it -> VIOLATED",
         seq(("judge", head, "accept", B), ("judge", head, "invalid", P)), "VIOLATED"),
        ("gate invalid (it ran) then judge reject -> CLEAN",
         seq(("gate", head, "invalid", {"steps": {"scope": "PASS"}}), ("judge", head, "reject", B)), "CLEAN"),
        ("an earlier violating accept survives a later gated accept -> VIOLATED",
         seq(("judge", head, "accept", B), g(gp, head), ("judge", head, "accept", B)), "VIOLATED"),
        ("two distinct full shas sharing 12 hex are not the base -> VIOLATED",
         seq(("judge", "0123456789ab" + "1" * 28, "reject", {"base": "0123456789ab" + "0" * 28})), "VIOLATED"),
        ("no gate, no usable base, non-accept -> UNMEASURED", seq(("judge", head, "reject", None)), "UNMEASURED"),
        ("no gate, a short base prefix, non-accept -> UNMEASURED",
         seq(("judge", head, "reject", {"base": base[:7]})), "UNMEASURED"),
    ]
    for name, s, want in rows:
        r = AA.dq_publish(s)
        check("publish: " + name, r["status"] == want, r)
    r = AA.dq_publish(seq(("judge", head, "reject", B)))
    check("publish: a real publish names its kind", (r.get("evidence") or [{}])[0].get("kind")
          == "published_without_gate", r)
    # the arm-level consequence: one parked task (gate fail at base, reject at base) no longer disqualifies an arm
    logs, tasks, sp = winner_logs()
    t0 = sorted(tasks)[0]
    tr = logs["trio"]["recs"]
    last = max(AA._ep(x) for x in tr)
    tr += [{"ts": iso(last + 5), "arm": "trio", "lane": "gate", "run_id": "gate", "task": t0, "event": "gate",
            "sha": base, "verdict": "fail", "detail": {"steps": {"scope": "PASS"}}},
           {"ts": iso(last + 9), "arm": "trio", "lane": "judge", "run_id": "judge", "task": t0, "event": "judge",
            "sha": base, "verdict": "reject", "detail": B}]
    check("publish: an arm with a parked task judged at base is not publish-disqualified",
          AA.dq_publish(AA.L.ordered(tr))["status"] == "CLEAN", AA.dq_publish(AA.L.ordered(tr)))


def t_nig_oracle():
    """nig_fit (task block eliminated by Schur complement) against the full-design conjugate posterior."""
    arms = ["trio", "v3", "ralph_a"]
    obs = [("trio", "a", 1.0), ("v3", "a", 1.4), ("ralph_a", "a", 2.2), ("trio", "b", 0.3), ("v3", "b", 0.9),
           ("trio", "c", 2.5), ("trio", "c", 2.7), ("v3", "d", -0.4), ("ralph_a", "d", 0.8), ("ralph_a", "e", 1.1)]
    pm = AA.prior_means(arms)
    fit = AA.nig_fit(obs, arms, pm)
    tasks = sorted({t for _, t, _ in obs})
    k = 1 + len(arms) + len(tasks)
    v0a = (AA.ARM_PRIOR_SD / AA.SIGMA_REF) ** 2
    v0t = (AA.TASK_PRIOR_SD / AA.SIGMA_REF) ** 2
    prec = [AA.C_PREC] + [1 / v0a] * len(arms) + [1 / v0t] * len(tasks)
    m0 = [0.0] + [pm[a] for a in arms] + [0.0] * len(tasks)
    q = [[prec[i] if i == j else 0.0 for j in range(k)] for i in range(k)]
    b = [prec[i] * m0[i] for i in range(k)]
    yy = 0.0
    for a, t, y in obs:
        x = [0.0] * k
        x[0] = 1.0
        x[1 + arms.index(a)] = 1.0
        x[1 + len(arms) + tasks.index(t)] = 1.0
        for i in range(k):
            b[i] += x[i] * y
            for j in range(k):
                q[i][j] += x[i] * x[j]
        yy += y * y
    qi = AA._inv_spd(q)
    mean = [sum(qi[i][j] * b[j] for j in range(k)) for i in range(k)]
    bn = AA.IG_B0 + 0.5 * (yy + sum(prec[i] * m0[i] ** 2 for i in range(k))
                           - sum(mean[i] * sum(q[i][j] * mean[j] for j in range(k)) for i in range(k)))
    m_err = max(abs(fit["mean"][i] - mean[i]) for i in range(1 + len(arms)))
    lo = fit["chol"]
    cov = [[sum(lo[i][r] * lo[j][r] for r in range(len(lo))) for j in range(len(lo))] for i in range(len(lo))]
    c_err = max(abs(cov[i][j] - qi[i][j]) for i in range(len(lo)) for j in range(len(lo)))
    check("NIG oracle: Schur posterior mean of (c, mu) equals the full-design mean (unbalanced design)",
          m_err < 1e-6, m_err)
    check("NIG oracle: Schur covariance equals the full-design covariance block", c_err < 1e-6, c_err)
    check("NIG oracle: bn equals the full-design bn", abs(fit["bn"] - bn) < 1e-6, (fit["bn"], bn))
    check("NIG oracle: an = a0 + n/2", fit["an"] == AA.IG_A0 + len(obs) / 2)
    rng = random.Random(5)
    ds = [AA.nig_draw(fit, rng) for _ in range(20000)]
    d = [x["trio"] - x["v3"] for x in ds]
    mu_d = sum(d) / len(d)
    var_d = sum((x - mu_d) ** 2 for x in d) / (len(d) - 1)
    i, j = 1 + arms.index("trio"), 1 + arms.index("v3")
    want_var = fit["bn"] / (fit["an"] - 1) * (qi[i][i] + qi[j][j] - 2 * qi[i][j])
    check("NIG draws: E[mu_trio - mu_v3] matches the posterior mean", abs(mu_d - (mean[i] - mean[j])) <
          4 * math.sqrt(want_var / len(d)), (mu_d, mean[i] - mean[j]))
    check("NIG draws: Var[mu_trio - mu_v3] matches the Student-t variance (within 5%)",
          abs(var_d / want_var - 1) < 0.05, (var_d, want_var))


# ---------------------------------------------------------------- (5c) review round 2: chronology, masking, snapshots

def t_ratio_boundaries():
    """The owner's ratios are inclusive (>=): a draw exactly at 1.25x / 1.1x / a 0.15 drop counts."""
    le = {"trio": [math.log(1.25)] * 4, "v3": [0.0] * 4}
    th = {"trio": [0.0] * 4, "v3": [0.15] * 4}
    p = AA.rule_probs({"le": le, "theta": th}, ["trio", "v3"], ["trio", "v3"])
    check("a draw exactly at 1.25x counts for DECIDE (>=)", p["decide"]["trio"] == 1.0, p["decide"])
    check("an accept drop of exactly 0.15 counts as worse (>=)", p["accept_worse"]["trio"] == 1.0, p["accept_worse"])
    le = {"trio": [math.log(1.1)] * 4, "v3": [0.0] * 4}
    p = AA.rule_probs({"le": le, "theta": th}, ["trio", "v3"], ["trio", "v3"])
    check("a draw exactly at 1.1x control counts against futility (>=)", p["futile"]["trio"] == 1.0, p["futile"])


def scope_fail(ts):
    return {"ts": iso(ts), "event": "gate", "sha": "ab" * 20, "verdict": "fail", "detail": {"steps": {"scope": "FAIL"}}}


def t_chronology_r2():
    # (1) a short arm that violates AFTER block 1's would-be time is removed at its violation, not waited for forever
    logs, tasks, sp = winner_logs()
    ids = sorted(tasks)
    logs["v3c"] = {"recs": arm_log("v3c", [(t, True) for t in ids[:3]], offset=3, extra=[scope_fail(T0 + 3500)])}
    sp["v3c"] = spend_for((t, 1e5) for t in ids[:3])
    r = AA.analyse(logs, tasks, sp, draws=DRAWS)
    check("a short arm violating after the block-1 time is disqualified then; the trial proceeds",
          r["final"]["verdict"] == "DECIDE_FOR_trio" and r["blocks"][0]["disqualified"] == {"v3c": ["scope"]}
          and r["blocks"][0]["ts_epoch"] == T0 + 3500,
          (r["final"]["verdict"], [(b["block"], b.get("disqualified"), b.get("ts_epoch")) for b in r["blocks"]]))
    # (2) an arm disqualified early must not set the cutoff with its late completions; (4) reasons split by time
    logs, tasks, sp = winner_logs(extra_trio=[scope_fail(T0 + 50000)])
    late_judge = {"ts": iso(T0 + 60000), "event": "judge", "task": ids[0], "sha": "cd" * 20, "verdict": "invalid",
                  "detail": {"base": "ef" * 20}}     # published (sha != base) with no gate at all -> publish VIOLATED
    logs["v3c"] = {"recs": arm_log("v3c", [(t, True) for t in ids[:5]], offset=10 ** 6,
                                   extra=[scope_fail(T0 + 100), late_judge])}
    sp["v3c"] = spend_for((t, 1e5) for t in ids[:5])
    r = AA.analyse(logs, tasks, sp, draws=DRAWS)
    f = r["final"]
    check("an early-disqualified arm's late completions do not push the cutoff past the winner's later violation",
          f["verdict"] == "DECIDE_FOR_trio" and "trio" not in f["disqualified"],
          (f["verdict"], f["disqualified"], [(b["block"], b.get("ts_epoch")) for b in r["blocks"]]))
    check("violation reasons are split by their own times (v3c out for scope; publish reported after the stop)",
          f["disqualified"].get("v3c") == ["scope"]
          and f.get("violations_after_stop") == {"trio": ["scope"], "v3c": ["publish"]},
          (f["disqualified"], f.get("violations_after_stop")))
    check("block times never go backwards", all(a["ts_epoch"] <= b["ts_epoch"] for a, b in
                                                 zip(r["blocks"], r["blocks"][1:])),
          [b["ts_epoch"] for b in r["blocks"]])


def t_tester_masking():
    def rec(ev, run, k, **kw):
        return dict({"ts": iso(T0 + k), "arm": "trio", "task": "T000", "event": ev, "run_id": run}, **kw)
    b = {"detail": {"role": "build"}}
    seq = [rec("pass_start", "trio.0", 1, **b), rec("build_end", "trio.0", 2, detail={"build_id": "x0"}),
           rec("pass_start", "trio.1", 3, **b), rec("build_end", "trio.2", 4, detail={"build_id": "x2"})]
    r = AA.dq_tester(AA.L.ordered(seq))
    check("tester: an orphan build_end does not mask a proven violation", r["status"] == "VIOLATED", r)
    seq2 = seq[:3] + [dict(rec("build_end", None, 4, detail={"build_id": "x2"}))]
    seq2[-1].pop("run_id")
    r = AA.dq_tester(AA.L.ordered(seq2))
    check("tester: a record with no run_id does not mask a proven violation", r["status"] == "VIOLATED", r)
    r = AA.dq_tester(AA.L.ordered(seq[:2] + seq2[3:]))
    check("tester: with no provable violation, an unidentified record -> UNMEASURED", r["status"] == "UNMEASURED", r)


def t_final_r2():
    tasks = make_tasks(4)
    logs = {a: {"recs": arm_log(a, [("T000", True)], offset=j, drop={(0, "gate")})} for j, a in enumerate(("trio", "v3"))}
    sp = {a: spend_for([("T000", 1e5)]) for a in ("trio", "v3")}
    r = AA.analyse(logs, tasks, sp, draws=300, final=True)
    check("final: every arm disqualified -> DISQUALIFIED, never HARD_CAP_NO_DIFFERENCE",
          r["final"]["verdict"] == "DISQUALIFIED" and sorted(r["final"]["disqualified"]) == ["trio", "v3"],
          (r["final"]["verdict"], r["final"]["disqualified"]))
    r = scenario({"ralph_a": (4.0, all_acc, 0.1), "trio": (1.0, all_acc, 0.1), "v3": (1.0, all_acc, 0.1)}, 20)
    iv = r["final"].get("intervals", {})
    check("final intervals keep a futile arm frozen at its drop (10 tasks, not 20)",
          iv.get("ralph_a", {}).get("completed") == 10 and iv.get("trio", {}).get("completed") == 20,
          {a: v.get("completed") for a, v in iv.items()})
    logs, tasks, sp = winner_logs()
    r = AA.analyse(logs, tasks, sp, draws=DRAWS)
    check("a stop's intervals are the stop's snapshot (10 tasks at block 2, not all 20)",
          r["final"]["intervals"]["trio"]["completed"] == 10 and r["final"]["intervals_snapshot"] == "block 2",
          (r["final"]["intervals"]["trio"]["completed"], r["final"].get("intervals_snapshot")))


def t_overflow_r2():
    tok, why = AA.task_tokens(R({OPUS: {"input": 10 ** 400}}), AA.default_conv())
    check("an int too big for a float is refused, not raised", tok is None and "invalid" in why, (tok, why))

    def big(s):
        for t in s["trio"]:
            s["trio"][t] = raw_row(1e308)
    logs, tasks, sp = winner_logs(spend_patch=big)
    r = AA.analyse(logs, tasks, sp, draws=300)
    check("rows each finite but summing past float range -> UNMEASURED", r["final"]["verdict"] == "UNMEASURED",
          r["final"].get("why"))


# ---------------------------------------------------------------- (5c) BENCH verify 2026-10-30 findings (red first)

def t_spend_missing_field():
    """ARENA_SPEND_ROW_HARDEN_MISSING_GPT_FIELD: the meter always writes every field, so a missing one is UNMEASURED,
    never 0 (BENCH probe a_spend_missing_gpt_fields decided for trio)."""
    conv = AA.default_conv()
    for k in ("tokens", "in_est", "out_est"):
        row = R({OPUS: {"input": 100}})
        del row["gpt"][k]
        tok, why = AA.task_tokens(row, conv)
        check("missing gpt.%s -> refused, not read as 0" % k, tok is None and k in (why or ""), (tok, why))
    tok, why = AA.task_tokens({"claude": R({OPUS: {"input": 100}})["claude"], "ambiguous_calls": 0}, conv)
    check("missing gpt section -> refused", tok is None and "gpt" in (why or ""), (tok, why))
    tok, why = AA.task_tokens({"gpt": R()["gpt"], "ambiguous_calls": 0}, conv)
    check("missing claude section -> refused", tok is None and "claude" in (why or ""), (tok, why))
    row = R({OPUS: {"input": 100}})
    del row["claude"][OPUS]["output"]
    tok, why = AA.task_tokens(row, conv)
    check("a Claude model missing a raw field -> refused", tok is None and "output" in (why or ""), (tok, why))
    tok, why = AA.task_tokens(R({OPUS: {"input": 100}}), conv)
    check("a full row still converts (100)", tok == 100.0, (tok, why))

    def strip(sp):
        for t in sp["trio"]:
            sp["trio"][t] = {"claude": sp["trio"][t]["claude"], "ambiguous_calls": 0}
    logs, tasks, sp = winner_logs(spend_patch=strip)
    r = AA.analyse(logs, tasks, sp, draws=DRAWS)
    check("winner whose rows lack the gpt section -> UNMEASURED, not DECIDE_FOR_trio",
          r["final"]["verdict"] == "UNMEASURED", r["final"]["verdict"])

    def strip1(sp):
        for t in sp["trio"]:
            del sp["trio"][t]["gpt"]["out_est"]
    logs, tasks, sp = winner_logs(spend_patch=strip1)
    r = AA.analyse(logs, tasks, sp, draws=DRAWS)
    check("winner whose rows lack gpt.out_est -> UNMEASURED", r["final"]["verdict"] == "UNMEASURED",
          r["final"]["verdict"])


def t_refused_spend_doc_withholds_blocks():
    """GPT r1 #3: a refused spend doc leaves no decisive verdict anywhere in the report."""
    logs, tasks, sp = winner_logs()
    doc = {"schema": AA.SPEND_SCHEMA, "arms": sp, "blocking": ["meter lost spend"]}
    r = AA.analyse_spend_doc(logs, tasks, doc, draws=DRAWS)
    check("refused spend doc -> final UNMEASURED and per-block verdicts withheld (no DECIDE anywhere)",
          r["final"]["verdict"] == "UNMEASURED" and r["blocks"] == [] and r.get("blocks_withheld", 0) > 0
          and "DECIDE_FOR" not in json.dumps(r), (r["final"], len(r["blocks"]), r.get("blocks_withheld")))


def _mut_recs(logs, arm, event, fn):
    for x in logs[arm]["recs"]:
        if x["event"] == event:
            fn(x)


def t_dq_measured_for_winner():
    """ARENA_WINNER_ENFORCE_MEASURED_DQ_CHECKS: no decision for an arm whose own non-exempt DQ check is UNMEASURED."""
    ex = getattr(AA, "DQ_EXEMPT", {})
    check("the exemption list is stated and is exactly {ruling}", set(ex) == {"ruling"}
          and all(isinstance(v, str) and v for v in ex.values()), ex)
    logs, tasks, sp = winner_logs()
    r = AA.analyse(logs, tasks, sp, draws=DRAWS)
    check("ruling-only UNMEASURED (the stated exemption) still decides", r["final"]["verdict"] == "DECIDE_FOR_trio"
          and r["final"]["dq_unmeasured"].get("trio") == ["ruling"], (r["final"]["verdict"], r["final"]["dq_unmeasured"]))
    logs, tasks, sp = winner_logs()
    _mut_recs(logs, "trio", "gate", lambda x: x["detail"]["steps"].update(scope="SKIP"))
    r = AA.analyse(logs, tasks, sp, draws=DRAWS, final=True)
    check("winner's scope check UNMEASURED (scope=SKIP) -> UNMEASURED, not DECIDE_FOR_trio",
          r["final"]["verdict"] == "UNMEASURED" and "scope" in json.dumps(r["final"]), r["final"]["verdict"])
    logs, tasks, sp = winner_logs()
    _mut_recs(logs, "trio", "judge", lambda x: x.update(sha=x["sha"][:8]))
    r = AA.analyse(logs, tasks, sp, draws=DRAWS, final=True)
    check("winner's publish check UNMEASURED (8-hex judge shas) -> UNMEASURED, not DECIDE_FOR_trio",
          r["final"]["verdict"] == "UNMEASURED" and "publish" in json.dumps(r["final"]), r["final"]["verdict"])
    logs, tasks, sp = winner_logs()
    _mut_recs(logs, "v3", "gate", lambda x: x["detail"]["steps"].update(scope="SKIP"))
    r = AA.analyse(logs, tasks, sp, draws=DRAWS)
    check("only the WINNER's own checks gate its decision (control's scope UNMEASURED: still DECIDE, listed)",
          r["final"]["verdict"] == "DECIDE_FOR_trio" and "scope" in r["final"]["dq_unmeasured"].get("v3", []),
          r["final"]["verdict"])
    v = AA.rule_verdict(probs({"trio": 0.99}, {"trio": 0.0}), True, {"trio": ["scope"]})
    check("rule_verdict: DECIDE blocked by the arm's unmeasured check -> UNMEASURED naming it",
          v[0] == "UNMEASURED" and v[1].get("dq_unmeasured") == ["scope"], v)
    v = AA.rule_verdict(probs(tie=0.95), True, {"trio": ["tester"]})
    check("rule_verdict: TIE winner with an unmeasured check -> UNMEASURED", v[0] == "UNMEASURED", v)
    v = AA.rule_verdict(probs(tie=0.95), True, {"v3": ["tester"]})
    check("rule_verdict: the TIE loser's unmeasured check does not block the simpler winner",
          v[0] == "TIE" and v[1]["winner"] == "trio", v)
    # GPT r1 #2: an early unidentifiable gate (scope SKIP) masked by a LATER scope FAIL dated after the decision
    skip = {"ts": iso(T0 + 5), "event": "gate", "sha": "c" * 40, "verdict": "pass",
            "detail": {"steps": {"scope": "SKIP"}}}
    fail = {"ts": iso(T0 + 40 * 600), "event": "gate", "sha": "d" * 40, "verdict": "pass",
            "detail": {"steps": {"scope": "FAIL"}}}
    logs, tasks, sp = winner_logs(extra_trio=(skip, fail))
    r = AA.analyse(logs, tasks, sp, draws=DRAWS)
    r0 = r
    logs, tasks, sp = winner_logs(extra_trio=(fail,))
    r = AA.analyse(logs, tasks, sp, draws=DRAWS)
    check("early scope SKIP + scope FAIL after the decisive block -> UNMEASURED(trio, scope) at the block the "
          "decision would have fired (the check was unmeasured then)",
          r0["final"]["verdict"] == "UNMEASURED" and r0["final"]["detail"].get("arm") == "trio"
          and r0["final"]["detail"].get("dq_unmeasured") == ["scope"] and r0["final"].get("block") is not None
          and r0["final"].get("block") == r["final"].get("block") and r0["dq"]["trio"]["scope"].get("unmeasured"),
          (r0["final"]["verdict"], r0["final"].get("detail"), r0["final"].get("block"), r["final"].get("block")))
    check("a later scope FAIL alone (all earlier gates measured) -> DECIDE_FOR_trio stands, violation after stop",
          r["final"]["verdict"] == "DECIDE_FOR_trio" and "trio" in r["final"].get("violations_after_stop", {}),
          (r["final"]["verdict"], r["final"].get("violations_after_stop")))


def t_control_absent():
    """ARENA_CONTROL_HARDEN_ABSENT_NOT_NO_DIFFERENCE: no control -> UNMEASURED, never HARD_CAP_NO_DIFFERENCE."""
    arms = {"trio": (1 / 3.0, all_acc, 0.1), "v3c": (1.0, all_acc, 0.1)}
    r = scenario(arms, 20, final=True)
    check("control absent, trio 3x v3c, --final -> UNMEASURED(control), not HARD_CAP_NO_DIFFERENCE",
          r["final"]["verdict"] == "UNMEASURED" and "control" in json.dumps(r["final"].get("detail")),
          (r["final"]["verdict"], r["final"].get("detail")))
    r = scenario(arms, 20)
    check("control absent mid-trial -> UNMEASURED, not CONTINUE", r["final"]["verdict"] == "UNMEASURED",
          r["final"]["verdict"])
    v = AA.rule_verdict(probs(tie=0.95, leaders=("trio", "v3c")), False)
    check("rule_verdict: TIE with the control absent -> UNMEASURED (GPT r1 #1)", v[0] == "UNMEASURED", v)
    r = scenario({"trio": (1.0, all_acc, 0.01), "v3c": (1.0, all_acc, 0.01)}, 20)
    check("control absent, two identical arms -> UNMEASURED, never TIE; no block carries a comparison verdict",
          r["final"]["verdict"] == "UNMEASURED" and r["blocks"]
          and all(b.get("rule_verdict") in (None, "UNMEASURED") for b in r["blocks"]),
          (r["final"]["verdict"], [b.get("rule_verdict") for b in r["blocks"]]))
    late = {"ts": iso(T0 + 10 ** 7), "event": "gate", "sha": "e" * 40, "verdict": "pass",
            "detail": {"steps": {"scope": "FAIL"}}}
    eq = {"trio": (1.0, all_acc, 0.3), "v3c": (1.0, all_acc, 0.3), "v3": (1.0, all_acc, 0.3)}
    r = scenario(eq, 20, final=True, v3={"extra": (late,)})
    check("control disqualified only AFTER the last block, --final -> UNMEASURED(control disqualified), never a "
          "hard-cap pick or NO_DIFFERENCE", r["final"]["verdict"] == "UNMEASURED"
          and "v3" in r["final"]["disqualified"] and "disqualified" in r["final"]["detail"].get("why", "")
          and all(b.get("rule_verdict") != "UNMEASURED" for b in r["blocks"]),
          (r["final"]["verdict"], r["final"].get("detail"), [b.get("rule_verdict") for b in r["blocks"]]))
    r = dq_run({"v3": {"drop": {(1, "gate")}}}, final=True)
    check("control disqualified, two arms left, --final -> UNMEASURED(control), DQ still listed",
          r["final"]["verdict"] == "UNMEASURED" and "v3" in r["final"]["disqualified"]
          and "control" in json.dumps(r["final"].get("detail")), (r["final"]["verdict"], r["final"].get("detail")))


def t_judge_gate_order():
    """ARENA_ANALYSIS_WIDEN_JUDGE_GATE_ORDER_TESTS: which judge verdict counts, and a gate pass AFTER the judge."""
    logs, tasks, sp = winner_logs()
    for x in [x for x in logs["trio"]["recs"] if x["event"] == "judge"]:
        logs["trio"]["recs"].append(dict(x, verdict="reject", ts=iso(AA._ep(x) - 50)))
    r = AA.analyse(logs, tasks, sp, draws=DRAWS)
    check("an EARLIER reject before each accept: the last (accept) counts -> DECIDE_FOR_trio, all accepted",
          r["final"]["verdict"] == "DECIDE_FOR_trio" and r["final"]["intervals"]["trio"]["accepted"] == 10,
          (r["final"]["verdict"], r["final"].get("intervals", {}).get("trio", {}).get("accepted")))
    logs, tasks, sp = winner_logs()
    for x in [x for x in logs["trio"]["recs"] if x["event"] == "judge"]:
        logs["trio"]["recs"].append(dict(x, verdict="reject", ts=iso(AA._ep(x) + 50)))
    r = AA.analyse(logs, tasks, sp, draws=DRAWS, final=True)
    check("a LATER reject after each accept: the last (reject) counts -> trio accepts nothing, never DECIDE_FOR_trio",
          r["final"]["verdict"] != "DECIDE_FOR_trio"
          and r["final"].get("intervals", {}).get("trio", {}).get("accepted") == 0,
          (r["final"]["verdict"], r["final"].get("intervals", {}).get("trio")))
    recs = arm_log("trio", [("T000", True)])
    g = next(x for x in recs if x["event"] == "gate")
    g["ts"] = iso(AA._ep(g) + 500)
    check("publish: a gate pass recorded AFTER the judge -> VIOLATED", AA.dq_publish(AA.L.ordered(recs))["status"]
          == "VIOLATED", AA.dq_publish(AA.L.ordered(recs)))
    logs, tasks, sp = winner_logs()
    g = [x for x in logs["trio"]["recs"] if x["event"] == "gate"][3]
    g["ts"] = iso(AA._ep(g) + 500)
    r = AA.analyse(logs, tasks, sp, draws=DRAWS)
    check("gate-after-judge on one trio task -> trio DISQUALIFIED(publish), never DECIDE_FOR_trio",
          r["final"]["disqualified"].get("trio") == ["publish"] and r["final"]["verdict"] != "DECIDE_FOR_trio",
          (r["final"]["verdict"], r["final"]["disqualified"]))


def t_hardcap_pick_unit():
    """Day-3 hard-cap clause (Conductor 2026-10-30): simplest arm not credibly worse than control on accept rate
    (P(worse by >= 0.10) < 0.2) AND on accepted points per token (P(< 0.9x control) < 0.2); else the control stays."""
    want = {"HARDCAP_ACCEPT_MARGIN": 0.10, "HARDCAP_ACCEPT_P": 0.2, "HARDCAP_EFF_RATIO": 0.9, "HARDCAP_EFF_P": 0.2}
    bad = {k: getattr(AA, k, None) for k, v in want.items() if getattr(AA, k, None) != v}
    check("hard-cap pick thresholds are the Conductor's numbers", not bad, bad)
    n = 100
    eq = [0.0] * n

    def pick(le, th, arms=None, blocked=None):
        arms = arms or sorted(le)
        return AA.hardcap_pick(fake(le, th), arms, "v3", blocked or {})
    th = {a: [0.7] * n for a in ("trio", "v3c", "v3", "ralph_c")}
    w, det = pick({"trio": eq, "v3c": eq, "v3": eq}, th)
    check("equal arms: the simplest (trio) is picked over v3c", w == "trio", (w, det))
    w, _ = pick({"ralph_c": eq, "trio": eq, "v3": eq}, th)
    check("order: ralph_c before trio", w == "ralph_c", w)
    worse = [math.log(0.9 * 0.97)] * n
    w, _ = pick({"trio": worse, "v3c": eq, "v3": eq}, th)
    check("eff 0.873x control (credibly < 0.9x) is skipped -> next simplest (v3c)", w == "v3c", w)
    w, _ = pick({"trio": [math.log(0.9 * 1.03)] * n, "v3": eq}, th)
    check("eff 0.927x control is not credibly < 0.9x -> picked", w == "trio", w)
    w, _ = pick({"trio": eq, "v3": eq}, dict(th, trio=[0.7 - 0.105] * n))
    check("accept 0.105 below control (>= 0.10) -> not picked, control stays", w == "v3", w)
    w, _ = pick({"trio": eq, "v3": eq}, dict(th, trio=[0.7 - 0.095] * n))
    check("accept 0.095 below control -> picked", w == "trio", w)
    # probability boundaries: 20 of 100 draws worse is P = 0.2 (not < 0.2); 19 of 100 is
    mix = lambda k, bad_v, good_v: [bad_v] * k + [good_v] * (n - k)  # noqa: E731
    w, _ = pick({"trio": mix(20, math.log(0.85), 0.0), "v3": eq}, th)
    check("P(eff < 0.9x) exactly 0.2 -> not picked (strict <)", w == "v3", w)
    w, _ = pick({"trio": mix(19, math.log(0.85), 0.0), "v3": eq}, th)
    check("P(eff < 0.9x) 0.19 -> picked", w == "trio", w)
    w, _ = pick({"trio": eq, "v3": eq}, dict(th, trio=mix(20, 0.5, 0.7)))
    check("P(accept worse) exactly 0.2 -> not picked (strict <)", w == "v3", w)
    w, _ = pick({"trio": eq, "v3": eq}, dict(th, trio=mix(19, 0.5, 0.7)))
    check("P(accept worse) 0.19 -> picked", w == "trio", w)
    w, _ = pick({"trio": eq, "v3c": eq, "v3": eq}, th, blocked={"trio": ["scope"]})
    check("an arm with an unmeasured non-exempt DQ check is never picked", w == "v3c", w)
    w, det = pick({"trio": eq, "v3": eq}, th)
    c = det["candidates"][0]
    check("the pick reports both probabilities and intervals per candidate",
          {"p_accept_worse", "p_eff_below", "eff_vs_control_90", "accept_diff_vs_control_90"} <= set(c), c)


def t_hardcap_pick_scenario():
    # trio 1.18x as efficient (below the 1.25x decision ratio), same accepts: nothing fires, trio not credibly worse
    r = scenario({"trio": (0.85, all_acc, 0.3), "v3": (1.0, all_acc, 0.3)}, 15, final=True)
    check("hard cap, nothing fired, trio not credibly worse -> HARD_CAP_PICK trio, intervals alongside",
          r["final"]["verdict"] == "HARD_CAP_PICK" and r["final"]["detail"].get("winner") == "trio"
          and "eff_vs_control_90" in r["final"]["intervals"]["trio"], (r["final"]["verdict"], r["final"].get("detail")))
    r = scenario({"trio": (0.85, all_acc, 0.3), "v3": (1.0, all_acc, 0.3)}, 15, tasks=make_tasks(20))
    check("no hard cap yet (15 of a 20-task trial) -> CONTINUE (the pick fires only at the cap)",
          r["final"]["verdict"] == "CONTINUE", r["final"]["verdict"])
    skip = {"ts": iso(T0 + 5), "event": "gate", "sha": "c" * 40, "verdict": "pass",
            "detail": {"steps": {"scope": "SKIP"}}}
    r = scenario({"trio": (0.85, all_acc, 0.3), "v3c": (0.85, all_acc, 0.3), "v3": (1.0, all_acc, 0.3)}, 15,
                 final=True, trio={"extra": (skip,)})
    c = {x["arm"]: x for x in (r["final"].get("detail") or {}).get("candidates", [])}
    check("hard cap end-to-end: the simplest arm with an unmeasured scope check is skipped, the next qualifying wins",
          r["final"]["verdict"] == "HARD_CAP_PICK" and r["final"]["detail"]["winner"] == "v3c"
          and "skipped" in c.get("trio", {}), (r["final"]["verdict"], r["final"].get("detail")))
    half = lambda i: i % 2 == 0  # noqa: E731
    r = scenario({"trio": (1.0, half, 0.8), "v3": (1.0, all_acc, 0.8)}, 15, final=True)
    check("hard cap, trio accepts credibly less -> control stays (HARD_CAP_NO_DIFFERENCE, winner v3)",
          r["final"]["verdict"] == "HARD_CAP_NO_DIFFERENCE" and r["final"]["detail"].get("winner") == "v3",
          (r["final"]["verdict"], r["final"].get("detail")))


# ---------------------------------------------------------------- (6) simulations: calibration and power

def sim(arms, n, seed, sigma_d=0.8, draws=1000, block_kinds=True, final=False, full=False):
    """arms: {arm: (tokens_factor, p_accept)}; same tasks in every arm (replay). -> final verdict, block."""
    rng = random.Random(seed)
    tasks = make_tasks(n)
    ids = sorted(tasks)
    base = {t: math.log(1e5) + math.log(tasks[t]["size"]) + rng.gauss(0, 0.5) for t in ids}
    s = sigma_d / math.sqrt(2)
    logs, sp = {}, {}
    for j, (a, (fac, p)) in enumerate(sorted(arms.items())):
        rows = [(t, rng.random() < p) for t in ids]
        logs[a] = {"recs": arm_log(a, rows, offset=j)}
        sp[a] = spend_for((t, math.exp(base[t] + rng.gauss(0, s)) * fac) for t in ids)
    r = AA.analyse(logs, tasks, sp, draws=draws, seed=seed, final=final)
    if full:
        return r
    return r["final"]["verdict"], r["final"].get("block"), [b.get("rule_verdict") for b in r["blocks"]]


def calib(nseeds, n=40, draws=1000, start=0):
    arms = {"trio": (1.0, 0.64), "v3c": (1.0, 0.64), "v3": (1.0, 0.64)}
    out = {"decide": 0, "tie": 0, "futile_any": 0, "seeds": nseeds, "tasks_per_arm": n, "draws": draws}
    for s in range(start, start + nseeds):
        v, _b, bl = sim(arms, n, 1000 + s, draws=draws)
        out["decide"] += v.startswith("DECIDE")
        out["tie"] += v == "TIE"
        out["futile_any"] += any(x == "FUTILE" for x in bl)
    return out


def power(nseeds, n=60, draws=1000, start=0):
    arms = {"trio": (1 / 1.5, 0.64), "v3": (1.0, 0.64)}
    when = []
    wrong = 0
    for s in range(start, start + nseeds):
        v, b, _bl = sim(arms, n, 5000 + s, draws=draws)
        if v == "DECIDE_FOR_trio":
            when.append(b * AA.BLOCK)
        elif v.startswith("DECIDE") or v == "TIE":
            wrong += 1
    return {"seeds": nseeds, "max_tasks_per_arm": n, "draws": draws, "decided": len(when), "wrong_stop": wrong,
            "by_25": sum(w <= 25 for w in when), "by_35": sum(w <= 35 for w in when),
            "by_40": sum(w <= 40 for w in when), "tasks_when_decided": sorted(when)}


HARDCAP_SCENARIOS = {
    # name: (arms {arm: (tokens_factor, p_accept)}, seed base, the right answer at the cap)
    "equal3": ({"trio": (1.0, 0.64), "v3c": (1.0, 0.64), "v3": (1.0, 0.64)}, 1000, "trio"),
    "trio_1.5x": ({"trio": (1 / 1.5, 0.64), "v3": (1.0, 0.64)}, 5000, "trio"),
    "trio_1.5x_worse": ({"trio": (1.5, 0.64), "v3": (1.0, 0.64)}, 7000, "v3"),
    "trio_accept_-0.15": ({"trio": (1.0, 0.49), "v3": (1.0, 0.64)}, 9000, "v3"),
}


def hardcap_sim(name, nseeds, n=40, draws=1000, start=0):
    """Final verdict at the hard cap (--final after n tasks/arm, sigma_d 0.8) over seeds; same harness as --calib/--power.
    "off_target" = a stop or pick for an arm other than the scenario's right answer (control staying is a miss, not wrong,
    unless the control is the right answer)."""
    arms, base, right = HARDCAP_SCENARIOS[name]
    out = {"scenario": name, "arms": {a: list(v) for a, v in arms.items()}, "right": right, "seeds": nseeds,
           "tasks_per_arm": n, "draws": draws, "verdicts": {}, "winner": {}, "off_target": 0, "off_target_seeds": []}
    for s in range(start, start + nseeds):
        f = sim(arms, n, base + s, draws=draws, final=True, full=True)["final"]
        v = f["verdict"]
        w = (v[len("DECIDE_FOR_"):] if v.startswith("DECIDE_FOR_") else (f.get("detail") or {}).get("winner"))
        out["verdicts"][v] = out["verdicts"].get(v, 0) + 1
        out["winner"][str(w)] = out["winner"].get(str(w), 0) + 1
        if w is not None and w != right and not (v == "HARD_CAP_NO_DIFFERENCE" and right != AA.CONTROL):
            out["off_target"] += 1
            out["off_target_seeds"].append([base + s, v, w])
    return out


def t_small_sims():
    c = calib(6, n=30, draws=600)
    check("null calibration (small, 6 seeds x 30 tasks): no false DECIDE", c["decide"] == 0, c)
    p = power(4, n=60, draws=600)
    check("power smoke (4 seeds, 1.5x): no wrong-direction stop", p["wrong_stop"] == 0, p)
    if not QUIET:
        print("INFO  small power run (not a target): %s" % json.dumps(p))


# ---------------------------------------------------------------- era gate (ARENA_STOP_RULE_HOLD_DECIDE_TILL_NEWEST)

def run_part(tasks, n_run, final=False, arms=None):
    """Like scenario(), but every arm completes only the first n_run of the trial's tasks (in id order)."""
    arms = arms or {"trio": (0.25, all_acc, 0.1), "v3": (1.0, all_acc, 0.1)}
    ids = sorted(tasks)[:n_run]
    rng = random.Random(7)
    base = {t: math.log(1e5) + rng.gauss(0, 1.0) for t in ids}
    logs, spend = {}, {}
    for j, (arm, (fac, acc, sd)) in enumerate(sorted(arms.items())):
        logs[arm] = {"recs": arm_log(arm, [(t, acc(i)) for i, t in enumerate(ids)], offset=j * 7)}
        spend[arm] = spend_for((t, math.exp(base[t] + rng.gauss(0, sd)) * fac) for t in ids)
    return AA.analyse(logs, tasks, spend, draws=DRAWS, final=final)


def t_era_map():
    e, why = AA.era_map({"T%02d" % i: {"chrono": i} for i in range(20)})
    newest = sorted(t for t, v in e.items() if v == 2)
    check("era_map: 20 distinct keys, 3 eras -> the newest era is exactly T14..T19 (bin = 3*rank//20)",
          why is None and newest == ["T%02d" % i for i in range(14, 20)] and e["T00"] == 0 and e["T13"] == 1, newest)
    e, _ = AA.era_map({"A": {"chrono": 5}, "B": {"chrono": 5}, "C": {"chrono": 9}})
    check("era_map: equal keys share a bin, ranked at their UPPER position (A, B middle; C newest)",
          e == {"A": 1, "B": 1, "C": 2}, e)
    keys = {"T%03d" % i: {"chrono": i} for i in range(13)}
    keys.update(("T%03d" % i, {"chrono": 13}) for i in range(13, 19))
    keys["T019"] = {"chrono": 19}
    e, _ = AA.era_map(keys)
    newest = sorted(t for t, v in e.items() if v == 2)
    check("FORCED (ARENA_STOP_GATE_FIX_SMALL_LEFTOVERS): a tie straddling the 2/3 cut never shrinks the newest era "
          "(T013..T019, 7 tasks; was T019 alone)", newest == ["T%03d" % i for i in range(13, 20)], newest)
    e, _ = AA.era_map({"A": {"chrono": 1}, "B": {"chrono": 1}, "C": {"chrono": 1}, "D": {"chrono": 2}})
    check("era_map: 3 tied + 1 -> the tied three are not the oldest era by default", e["D"] == 2 and e["A"] == 1, e)
    e, why = AA.era_map({"A": {"chrono": 1}, "B": {"kind": "x"}})
    check("era_map: a task with no key -> no map (gate UNMEASURED)", e is None and "no chronology key" in why, why)
    e, why = AA.era_map({"A": {"chrono": True}})
    check("era_map: a bool is not a chronology key", e is None, e)


def t_era_gate():
    tasks = make_tasks(20, chrono=lambda i: i)          # oldest first: the newest era (T014..T019) runs last
    r = run_part(tasks, 20)
    b = {x["block"]: x for x in r["blocks"]}
    early = [b[k] for k in (2, 3) if k in b]
    check("FORCED: early looks with a decisive margin (blocks 2, 3) are held: verdict CONTINUE, would_be DECIDE",
          len(early) == 2 and all(x["verdict"] == "CONTINUE" and x["rule_verdict"] == "CONTINUE"
                                  and x.get("held", {}).get("would_be") == "DECIDE_FOR_trio" for x in early),
          [(x["block"], x.get("verdict"), x.get("held", {}).get("would_be")) for x in early])
    check("FORCED: the held look names the newest-era tasks still missing",
          early and early[0]["held"]["newest_era_missing"].get("trio") == ["T%03d" % i for i in range(14, 20)],
          early and early[0]["held"]["newest_era_missing"])
    check("no DECIDE verdict before the newest era is in", not any(
        x["verdict"].startswith("DECIDE") for x in r["blocks"] if x["block"] < 4), [x["verdict"] for x in r["blocks"]])
    check("once the newest era is in (block 4, 20 tasks) the look decides normally",
          r["final"]["verdict"] == "DECIDE_FOR_trio" and r["final"].get("block") == 4,
          (r["final"]["verdict"], r["final"].get("block")))
    check("report carries the era gate and its simulator limit",
          r["era_gate"]["status"] == "MEASURED" and "no task order" in r["era_gate"]["limit"]
          and len(r["era_gate"]["newest_era"]) == 6, r["era_gate"].get("status"))
    ctl = scenario({"trio": (0.25, all_acc, 0.1), "v3": (1.0, all_acc, 0.1)}, 20)
    check("control: the same data with the newest era first decides at block 2 (the hold is the order's)",
          ctl["final"]["verdict"] == "DECIDE_FOR_trio" and ctl["final"].get("block") == 2, ctl["final"].get("block"))
    r = run_part(tasks, 15)
    check("FORCED: newest era never run (15 of 20 tasks): no DECIDE anywhere, final CONTINUE",
          r["final"]["verdict"] == "CONTINUE" and "DECIDE_FOR" not in json.dumps(
              [x["verdict"] for x in r["blocks"]]), (r["final"]["verdict"], [x["verdict"] for x in r["blocks"]]))
    r = run_part(tasks, 15, final=True)
    check("FORCED (ARENA_FINAL_LOOK_FIX_UNGATED_AT_CAP, ARENA_CUT_TRIAL_FIX_SAYS_NO_DIFFERENCE): --final with the "
          "newest era never run -> the final look does not run, no DECIDE, every arm skipped, and the verdict is "
          "CUT_SHORT_UNDECIDED with no winner (was HARD_CAP_NO_DIFFERENCE, winner v3)",
          not r["final"]["verdict"].startswith("DECIDE") and r["final"].get("final_look", {}).get("ran") is False
          and r["final"]["verdict"] == AA.CUT_SHORT and r["final"]["detail"].get("winner") is None
          and all("skipped" in c for c in r["final"]["detail"].get("candidates", [])),
          (r["final"]["verdict"], r["final"].get("final_look")))
    eq = {"trio": (1.0, all_acc, 0.8), "v3": (1.0, all_acc, 0.8)}
    r = run_part(tasks, 15, final=True, arms=eq)
    check("FORCED (CUT_TRIAL): equal arms cut before the newest era, --final -> CUT_SHORT_UNDECIDED, never a "
          "hard-cap verdict", r["final"]["verdict"] == AA.CUT_SHORT, r["final"]["verdict"])
    r = run_part(tasks, 20, final=True, arms=eq)
    check("final look with nothing decisive falls to the hard-cap clause",
          r["final"]["verdict"].startswith("HARD_CAP") and "final_look" not in r["final"]["detail"],
          r["final"]["verdict"])
    nokey = {t: {k: v for k, v in s.items() if k != "chrono"} for t, s in tasks.items()}
    r = run_part(nokey, 20)
    check("FORCED: no chronology key -> gate UNMEASURED, every decision held; all tasks in -> UNMEASURED, no verdict",
          r["era_gate"]["status"] == "UNMEASURED" and r["final"]["verdict"] == "UNMEASURED"
          and any(x.get("held") for x in r["blocks"]), (r["era_gate"].get("why"), r["final"]["verdict"]))
    r = run_part(nokey, 15)
    check("gate UNMEASURED mid-trial -> CONTINUE (held)", r["final"]["verdict"] == "CONTINUE", r["final"]["verdict"])
    r = run_part(nokey, 20, final=True)
    check("gate UNMEASURED at --final -> UNMEASURED (no era named, no decision on unknown order)",
          r["final"]["verdict"] == "UNMEASURED", r["final"]["verdict"])
    tie = make_tasks(60, chrono=lambda i: i)
    r = run_part(tie, 50, arms={"trio": (1.0, all_acc, 0.02), "v3": (1.0, all_acc, 0.02)})
    check("FORCED: a would-be TIE before the newest era is held too",
          r["final"]["verdict"] == "CONTINUE" and any(x.get("held", {}).get("would_be") == "TIE" for x in r["blocks"]),
          (r["final"]["verdict"], [x.get("held", {}).get("would_be") for x in r["blocks"]]))
    los = run_part(tasks, 15, arms={"ralph_a": (4.0, all_acc, 0.1), "trio": (1.0, all_acc, 0.1),
                                    "v3": (1.0, all_acc, 0.1)})
    fut = [x for x in los["blocks"] if x.get("held", {}).get("would_be") == "FUTILE"]
    check("FORCED (ARENA_FUTILE_GATE_FIX_OLD_TASK_DROPS): FUTILE before the newest era is held: CONTINUE, no arm "
          "dropped, would_be FUTILE names ralph_a",
          bool(fut) and all(x["verdict"] == "CONTINUE" for x in fut) and not los["final"].get("futile")
          and fut[0]["held"].get("futile_would_be") == ["ralph_a"],
          [(x["block"], x.get("verdict"), x.get("held", {}).get("would_be")) for x in los["blocks"]])
    r = run_part(tasks, 20, arms={"ralph_a": (4.0, all_acc, 0.1), "trio": (0.9, all_acc, 0.3),
                                  "v3": (1.0, all_acc, 0.3)})
    b4 = [x for x in r["blocks"] if x["block"] == 4]
    check("FUTILE once the newest era is in (block 4) fires normally (ralph_a dropped)",
          "ralph_a" in r["final"].get("futile", []) and b4 and b4[0]["verdict"] == "FUTILE",
          (r["final"]["verdict"], r["final"].get("futile")))


def t_stop_gate_fixes():
    """The tester's failing scenarios (verify_stop/forced.py) must now be held or CONTINUE."""
    t30 = make_tasks(30, chrono=lambda i: i)
    r = run_part(t30, 15, final=True, arms={"ralph_a": (0.25, all_acc, 0.1), "v3": (1.0, all_acc, 0.1)})
    check("FORCED (FINAL_LOOK): ralph_a .25x on 15 of 30 (older only), --final -> no DECIDE, final look not run",
          not r["final"]["verdict"].startswith("DECIDE") and r["final"].get("final_look", {}).get("ran") is False,
          (r["final"]["verdict"], r["final"].get("final_look")))
    r = run_part(t30, 15, final=True, arms={"ralph_a": (4.0, all_acc, 0.1), "trio": (0.9, all_acc, 0.1),
                                            "v3": (1.0, all_acc, 0.1)})
    check("FORCED (FUTILE gate, CUT_TRIAL): loser + trio, 15 of 30, --final -> no FUTILE drop, no pick on older "
          "tasks alone, CUT_SHORT_UNDECIDED", not r["final"].get("futile") and r["final"]["verdict"] == AA.CUT_SHORT,
          (r["final"]["verdict"], r["final"].get("futile")))
    # a dead arm: trio stops at 15 of 20 tasks (newest era T014..T019 never run), v3 and v3c finish
    tasks = make_tasks(20, chrono=lambda i: i)
    ids = sorted(tasks)
    rng = random.Random(7)
    base = {t: math.log(1e5) + rng.gauss(0, 1.0) for t in ids}
    logs, spend = {}, {}
    for j, (arm, fac, n) in enumerate((("trio", 0.25, 15), ("v3", 1.0, 20), ("v3c", 1.0, 20))):
        logs[arm] = {"recs": arm_log(arm, [(t, True) for t in ids[:n]], offset=j * 7)}
        spend[arm] = spend_for((t, math.exp(base[t] + rng.gauss(0, 0.1)) * fac) for t in ids[:n])
    r = AA.analyse(logs, tasks, spend, draws=DRAWS, final=True)
    cands = {c["arm"]: c for c in r["final"].get("detail", {}).get("candidates", [])}
    check("FORCED (FINAL_LOOK): a dead arm (trio stopped before the newest era) is never decided for: the hard cap "
          "skips it and the final look runs without it (CUT_TRIAL: it no longer blocks the look for v3, v3c)",
          r["final"]["verdict"] != "DECIDE_FOR_trio" and r["final"].get("detail", {}).get("winner") != "trio"
          and r["final"].get("final_look", {}).get("skipped_short") == ["trio"]
          and (r["final"].get("final_look", {}).get("ran") or "skipped" in cands.get("trio", {})),
          (r["final"]["verdict"], r["final"].get("detail", {}).get("winner"), cands.get("trio")))
    t22 = make_tasks(22, chrono=lambda i: i)
    r = run_part(t22, 22)
    check("FORCED (SMALL_LEFTOVERS): pool exhausted (22 of 22), no --final -> never CONTINUE to a block that cannot "
          "exist; the final look runs on the full data and decides", r["final"]["verdict"] == "DECIDE_FOR_trio"
          and r["final"].get("final_look", {}).get("ran") is True, (r["final"]["verdict"], r["final"].get("final_look")))
    r = run_part(make_tasks(20, chrono=lambda i: i), 20, arms={"trio": (1.0, all_acc, 0.8), "v3": (1.0, all_acc, 0.8)})
    check("FORCED (SMALL_LEFTOVERS): pool exhausted on a block boundary, flat -> the hard cap, not CONTINUE",
          r["final"]["verdict"].startswith("HARD_CAP"), r["final"]["verdict"])
    r = run_part(t22, 17)
    check("CONTINUE mid-trial names a reachable next block (<= the trial size) and what it waits for",
          r["final"]["verdict"] == "CONTINUE" and r["final"]["detail"].get("next_block_tasks_per_arm") <= 22
          and "waiting_for" in r["final"]["detail"], r["final"].get("detail"))
    r = run_part(t22, 22, final=True)
    check("FORCED (FINAL_LOOK): 22 tasks --final -> the final look runs gated (ran True) and decides",
          r["final"]["verdict"] == "DECIDE_FOR_trio" and r["final"]["final_look"]["ran"] is True
          and not r["final"]["final_look"].get("newest_era_missing"), r["final"].get("final_look"))
    r = run_part(t30, 15, arms={"ralph_a": (4.0, all_acc, 0.1), "trio": (0.25, all_acc, 0.1),
                                "v3": (1.0, all_acc, 0.1)})
    held = [x["held"] for x in r["blocks"] if x.get("held", {}).get("would_be") == "DECIDE_FOR_trio"]
    check("FORCED (SMALL_LEFTOVERS): a held DECIDE no longer masks a FUTILE: the held look names futile_would_be",
          bool(held) and held[-1].get("futile_would_be") == ["ralph_a"], held and held[-1])
    check("report lists every held block", r["era_gate"].get("held_blocks") == [x["block"] for x in r["blocks"]
                                                                                  if x.get("held")],
          r["era_gate"].get("held_blocks"))


def _dead_arm(tasks, arms):
    """arms: ((arm, token factor, tasks completed), ...): each arm runs the first n tasks (oldest first), all accepted."""
    ids = sorted(tasks)
    rng = random.Random(7)
    base = {t: math.log(1e5) + rng.gauss(0, 1.0) for t in ids}
    logs, spend = {}, {}
    for j, (arm, fac, n) in enumerate(arms):
        logs[arm] = {"recs": arm_log(arm, [(t, True) for t in ids[:n]], offset=j * 7)}
        spend[arm] = spend_for((t, math.exp(base[t] + rng.gauss(0, 0.1)) * fac) for t in ids[:n])
    return logs, spend


def t_cut_trial():
    """ARENA_CUT_TRIAL_FIX_SAYS_NO_DIFFERENCE: a cut trial is UNDECIDED; a dead arm is skipped, not a blocker."""
    n = 20
    tasks = make_tasks(n, chrono=lambda i: i)
    cut = n * 3 // 4                                         # every arm stuck before the newest era
    logs, spend = _dead_arm(tasks, (("trio", 1.0, cut), ("v3", 1.0, cut), ("v3c", 1.0, cut)))
    r = AA.analyse(logs, tasks, spend, draws=DRAWS)
    check("stuck trial, no --final -> CONTINUE naming the end-of-budget duty (the wall clock is never read)",
          r["final"]["verdict"] == "CONTINUE" and "--final" in r["final"]["detail"].get("end_of_budget", ""),
          r["final"].get("detail"))
    r = AA.analyse(logs, tasks, spend, draws=DRAWS, final=True)
    check("FORCED: every arm stuck before the newest era, --final -> CUT_SHORT_UNDECIDED, winner None (was "
          "HARD_CAP_NO_DIFFERENCE, winner v3)", r["final"]["verdict"] == AA.CUT_SHORT
          and r["final"]["detail"].get("winner") is None and "HARD_CAP" not in r["final"]["verdict"],
          (r["final"]["verdict"], r["final"]["detail"].get("winner")))
    logs, spend = _dead_arm(tasks, (("trio", 1.0, n), ("v3", 1.0, cut), ("v3c", 1.0, n)))
    r = AA.analyse(logs, tasks, spend, draws=DRAWS, final=True)
    check("FORCED: the control alone stuck before the newest era, --final -> CUT_SHORT_UNDECIDED",
          r["final"]["verdict"] == AA.CUT_SHORT and "control" in r["final"]["detail"].get("why", ""),
          r["final"]["verdict"])
    logs, spend = _dead_arm(tasks, (("ralph_a", 1.0, cut), ("trio", 0.25, n), ("v3", 1.0, n)))
    r = AA.analyse(logs, tasks, spend, draws=DRAWS, final=True)
    fl = r["final"].get("final_look", {})
    check("FORCED: a dead arm (ralph_a stopped before the newest era) is skipped by the final look, which decides "
          "for the arms that finished (was: the look did not run, HARD_CAP_PICK)",
          r["final"]["verdict"] == "DECIDE_FOR_trio" and fl.get("ran") is True
          and fl.get("skipped_short") == ["ralph_a"] and "ralph_a" not in fl.get("arms", []),
          (r["final"]["verdict"], fl.get("ran"), fl.get("skipped_short")))
    logs, spend = _dead_arm(tasks, (("ralph_a", 1.0, cut), ("trio", 1.0, n), ("v3", 1.0, n)))
    r = AA.analyse(logs, tasks, spend, draws=DRAWS, final=True)
    check("a dead arm next to two equal finished arms: never decided for; if the control stays, the report names the "
          "arm not judged", r["final"]["verdict"] != "DECIDE_FOR_ralph_a"
          and r["final"].get("detail", {}).get("winner") != "ralph_a"
          and (r["final"]["verdict"] != "HARD_CAP_NO_DIFFERENCE"
               or r["final"]["detail"].get("not_judged") == ["ralph_a"]),
          (r["final"]["verdict"], r["final"].get("detail", {}).get("not_judged")))


# ---------------------------------------------------------------- ledger anchors (ARENA_ANALYSIS_WIRE_LEDGER_ANCHORS_TRUST)

LEDGER_ENV = ("ARENA_ROOT", "ARENA_EVENT_TOKEN_FILE", "ARENA_ANCHOR_FILE", "ARENA_WITNESS")


def _ledger_note(path, text):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps({"seat": "FOUNDRY", "event": "note", "id": "ARENA_SELFTEST_ANCHOR",
                                      "text": text, "ts": "2026-11-01T00:00:00Z"}) + "\n")


def t_ledger_trust():
    """The CLIs' loader (verified_logs, used by arena_analysis run AND arena_spend) reads the ARENA_ANCHOR notes from
    the ledger: REAL signed logs (arena_eventlog.HarnessWriter, file witness) + signed anchors -> every arm trusted;
    tampered line, truncated tail, missing ledger, unanchored ledger, forged note -> UNMEASURED; --allow-untrusted
    loads them and says so (OVERRIDE). Mutant: the ledger anchors ignored -> the genuine run is UNMEASURED."""
    import contextlib
    import io
    import os
    import shutil
    L = AA.L
    saved = {k: os.environ.get(k) for k in LEDGER_ENV}
    d = Path(tempfile.mkdtemp(prefix="aa_ledger_"))
    res = {}
    try:
        os.environ.update(ARENA_ROOT=str(d / "arena"), ARENA_EVENT_TOKEN_FILE=str(d / "secret" / "event_token"),
                          ARENA_ANCHOR_FILE=str(d / "secret" / "anchors.jsonl"),
                          ARENA_WITNESS=str(d / "secret" / "witness.jsonl"))
        p = AA.A.paths()
        L.init_token(p)
        tok = L._read_token(p)
        w = L.HarnessWriter(p)
        arms = ("trio", "v3")
        for arm in arms:
            for i in range(4):
                w.emit(arm, "assign", lane="build", run_id="%s.%d" % (arm, i), task="T%03d" % i,
                       ts="2026-11-01T0%d:00:00Z" % i)
        heads = [L.make_anchor(a, L.verify(p, a, tok)["accepted"], tok) for a in arms] + [L.roster_anchor(p, tok)]
        good, none_, forged = d / "led" / "events.jsonl", d / "led_none" / "events.jsonl", d / "led_f" / "events.jsonl"
        _ledger_note(good, L.anchor_note_text(heads))
        _ledger_note(none_, "an unrelated note, no anchors")
        _ledger_note(forged, L.anchor_note_text([dict(h, lsig="0" * 64) for h in heads]))
        missing = d / "nowhere" / "events.jsonl"
        res["genuine"] = AA.verified_logs(None, good)
        res["unanchored"] = AA.verified_logs(None, none_)
        res["forged"] = AA.verified_logs(None, forged)
        res["missing"] = AA.verified_logs(None, missing)
        res["override"] = AA.verified_logs(None, missing, allow_untrusted=True)
        real_le = AA.ledger_external
        AA.ledger_external = lambda ledger=None: (None, {"ledger": "mutant"})
        try:
            res["mut_ignored"] = AA.verified_logs(None, good)
        finally:
            AA.ledger_external = real_le
        real_lv = AA.load_verified
        AA.load_verified = lambda p=None, token=None, external=None, allow_untrusted=False: real_lv(
            p, token, external, allow_untrusted=True)
        try:
            res["mut_trust_dropped"] = AA.verified_logs(None, missing)
        finally:
            AA.load_verified = real_lv
        # the real CLI (no spend file: UNMEASURED by spend, but log_trust shows the loader's view)
        for name, extra in (("cli_genuine", ["--ledger", str(good)]), ("cli_missing", ["--ledger", str(missing)])):
            out = d / (name + ".json")
            with contextlib.redirect_stdout(io.StringIO()):
                rc = AA.main(["run", "--spend", str(d / "no_spend.json"), "--arms", "trio,v3", "--draws", "200",
                              "--out", str(out)] + extra)
            res[name] = (rc, json.loads(out.read_text()).get("log_trust", {}))
        # tamper: one byte of trio's 2nd record changed (sig no longer verifies)
        tf = p["events"] / "trio.jsonl"
        lines = tf.read_text().splitlines(True)
        bad = json.loads(lines[1])
        bad["task"] = "T999"
        tf.write_text("".join([lines[0], json.dumps(bad, sort_keys=True) + "\n"] + lines[2:]))
        res["tampered"] = AA.verified_logs(None, good)
        # truncated tail: trio's last record removed (the anchor says 4)
        tf.write_text("".join(lines[:-1]))
        res["truncated"] = AA.verified_logs(None, good)
        tf.write_text("".join(lines))
        res["restored"] = AA.verified_logs(None, good)
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(d, ignore_errors=True)
    um = lambda r, a: "unmeasured" in r[0].get(a, {"unmeasured": "absent"})   # noqa: E731
    g_logs, g_tr = res["genuine"]
    check("ledger: genuine signed + ledger-anchored logs -> every arm trusted through the CLI loader",
          all(len(g_logs.get(a, {}).get("recs", ())) == 4 for a in ("trio", "v3"))
          and g_tr.get("trusted_arms") == ["trio", "v3"] and not g_tr.get("untrusted_arms")
          and g_tr.get("status") == "read" and "OVERRIDE" not in g_tr, g_tr)
    for name, why in (("unanchored", "untrusted log"), ("forged", "untrusted log"), ("missing", "untrusted log")):
        check("ledger: %s ledger -> every arm UNMEASURED (%s)" % (name, why),
              all(um(res[name], a) and why in res[name][0][a]["unmeasured"] for a in ("trio", "v3")),
              (res[name][0], res[name][1]))
    check("ledger: a missing ledger is reported as MISSING in log_trust", str(res["missing"][1].get("status", ""))
          .startswith("MISSING"), res["missing"][1])
    check("ledger: tampered line -> that arm UNMEASURED, the other stays trusted",
          um(res["tampered"], "trio") and not um(res["tampered"], "v3"), res["tampered"][0].get("trio"))
    check("ledger: truncated tail (log shorter than the anchor) -> that arm UNMEASURED (refused)",
          um(res["truncated"], "trio") and "refused" in res["truncated"][0]["trio"]["unmeasured"]
          and not um(res["truncated"], "v3"), res["truncated"][0].get("trio"))
    check("ledger: control: the restored log is trusted again", not um(res["restored"], "trio"),
          res["restored"][0].get("trio"))
    o_logs, o_tr = res["override"]
    check("ledger: --allow-untrusted loads untrusted arms and REPORTS the override",
          all(not um(res["override"], a) for a in ("trio", "v3")) and o_tr.get("allow_untrusted") is True
          and o_tr.get("untrusted_arms") == ["trio", "v3"] and "OVERRIDE" in o_tr, o_tr)
    check("ledger MUTANT: anchors ignored (ledger_external dropped) -> the genuine run is caught (UNMEASURED)",
          all(um(res["mut_ignored"], a) for a in ("trio", "v3")), res["mut_ignored"][0])
    check("ledger MUTANT: load_verified forced to allow_untrusted -> the missing-ledger arms LOAD (the missing-ledger row has teeth)",
          all(not um(res["mut_trust_dropped"], a) for a in ("trio", "v3")), res["mut_trust_dropped"][0])
    rcg, ltg = res["cli_genuine"]
    rcm, ltm = res["cli_missing"]
    check("ledger CLI: arena_analysis.py run --ledger <anchored> reports both arms trusted in log_trust",
          ltg.get("trusted_arms") == ["trio", "v3"] and ltg.get("allow_untrusted") is False, (rcg, ltg))
    check("ledger CLI: --ledger <missing> -> exit 3, both arms untrusted", rcm == 3 and ltm.get("untrusted_arms") ==
          ["trio", "v3"] and not ltm.get("trusted_arms"), (rcm, ltm))


# ---------------------------------------------------------------- runner

CORE = (t_rule_probs, t_rule_verdict, t_tokens_and_inputs, t_cli, t_winner, t_fluke, t_loser, t_tie,
        t_hardcap_determinism, t_dq, t_exact_boundaries, t_malformed, t_chronology, t_dq_identity, t_nig_oracle,
        t_ratio_boundaries, t_chronology_r2, t_tester_masking, t_final_r2, t_overflow_r2, t_spend_missing_field,
        t_dq_measured_for_winner, t_control_absent, t_judge_gate_order, t_hardcap_pick_unit, t_hardcap_pick_scenario,
        t_refused_spend_doc_withholds_blocks, t_era_map, t_era_gate, t_stop_gate_fixes, t_cut_trial,
        t_stray_logs, t_ledger_trust, t_publish_parked)

MUTANTS = [("DECIDE_RATIO", 1.3125), ("DECIDE_RATIO", 1.1875), ("DECIDE_P", 0.97), ("DECIDE_P", 0.93),
           ("ACCEPT_MARGIN", 0.16), ("ACCEPT_MARGIN", 0.14), ("ACCEPT_P", 0.22), ("ACCEPT_P", 0.18),
           ("FUTILE_RATIO", 1.155), ("FUTILE_RATIO", 1.045), ("FUTILE_P", 0.07), ("FUTILE_P", 0.03),
           ("TIE_BAND", 0.17), ("TIE_BAND", 0.13), ("TIE_P", 0.92), ("TIE_P", 0.88),
           ("MIN_TASKS", 5), ("MIN_TASKS", 15), ("MIN_KINDS", 1), ("MIN_KINDS", 3), ("BLOCK", 4), ("BLOCK", 6),
           ("SIMPLER", ("v3", "v3c", "trio", "ralph_c", "ralph_a")), ("CONTROL", "v3c"), ("ERAS", 2), ("ERAS", 4),
           ("newest_era_missing", lambda *a: {}), ("held_kind", lambda v: v.startswith("DECIDE_FOR_")),
           ("gated", AA.held_kind), ("ledger_external", lambda ledger=None: (None, {"ledger": "mutant"})),
           ("dq_publish", _old_dq_publish)]


def mutants():
    global QUIET
    res = []
    for name, val in MUTANTS:
        old = getattr(AA, name)
        setattr(AA, name, val)
        QUIET = True
        FAILS.clear()
        try:
            for t in CORE:
                try:
                    t()
                except Exception as e:  # a crash is a detection too
                    FAILS.append("%s crashed: %s" % (t.__name__, e))
        finally:
            setattr(AA, name, old)
            QUIET = False
        res.append((name, val, len(FAILS), FAILS[:2]))
        print("%s  mutant %s=%r: %d core check(s) fail %s" % ("PASS" if FAILS else "FAIL", name, val, len(FAILS),
                                                                 FAILS[:2]))
    FAILS.clear()
    survived = [r for r in res if r[2] == 0]
    check("mutation check: every broken threshold fails the core suite (pins excluded)", not survived, survived)


def main(argv):
    if "--calib" in argv:
        n = int(argv[argv.index("--calib") + 1])
        start = int(argv[argv.index("--start") + 1]) if "--start" in argv else 0
        print(json.dumps(calib(n, start=start)))
        return 0
    if "--hardcap" in argv:
        i = argv.index("--hardcap")
        n = int(argv[i + 1])
        names = argv[i + 2].split(",") if len(argv) > i + 2 and not argv[i + 2].startswith("-") else \
            list(HARDCAP_SCENARIOS)
        st = int(argv[argv.index("--start") + 1]) if "--start" in argv else 0
        for nm in names:
            print(json.dumps(hardcap_sim(nm, n, start=st)), flush=True)
        return 0
    if "--power" in argv:
        n = int(argv[argv.index("--power") + 1])
        start = int(argv[argv.index("--start") + 1]) if "--start" in argv else 0
        print(json.dumps(power(n, start=start)))
        return 0
    if "--mutants" in argv:
        mutants()
    else:
        t_pins()
        for t in CORE:
            t()
        t_small_sims()
    print("\n%d failure(s)%s" % (len(FAILS), (": " + ", ".join(FAILS)) if FAILS else ""))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
