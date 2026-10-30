#!/usr/bin/env python3
"""selftest_arena_analysis.py - the stopping rule (arena_analysis.py) on synthetic logs.

    python3 src/RimMandrake/Utils/arena/selftest_arena_analysis.py              # units + scenarios + small sims
    python3 src/RimMandrake/Utils/arena/selftest_arena_analysis.py --mutants    # break each threshold: suite must fail
    python3 src/RimMandrake/Utils/arena/selftest_arena_analysis.py --calib N    # null false-DECIDE rate over N seeds
    python3 src/RimMandrake/Utils/arena/selftest_arena_analysis.py --power N    # 1.5x, sigma_d 0.8: tasks to decide

Sections: (1) the owner's thresholds pinned; (2) rule boundaries with LITERAL numbers (1.25, 0.95, 0.10, 0.2, 1.1,
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

def make_tasks(n, kinds=None):
    kinds = kinds or (lambda i: KINDS[i % 2])
    return {"T%03d" % i: {"kind": kinds(i), "size": (1, 2, 4)[i % 3]} for i in range(n)}


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


def spend_for(rows_tokens):
    return {t: {"claude_ite": tok, "gpt_ite": 0, "gpt_ite_est": 0} for t, tok in rows_tokens}


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
            "ACCEPT_MARGIN": 0.10, "ACCEPT_P": 0.2, "FUTILE_RATIO": 1.1, "FUTILE_P": 0.05, "TIE_BAND": 0.15,
            "TIE_P": 0.9, "SIMPLER": ("ralph_a", "ralph_c", "trio", "v3c", "v3"), "CONTROL": "v3"}
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
    p = AA.rule_probs(fake({"trio": [0.0] * n, "v3": [0.0] * n}, {"trio": [0.8 - 0.105] * n, "v3": [0.8] * n}),
                      ["trio", "v3"], ["trio", "v3"])
    check("accept margin: 0.105 worse counts as >= 0.10", p["accept_worse"]["trio"] == 1.0, p["accept_worse"])
    p = AA.rule_probs(fake({"trio": [0.0] * n, "v3": [0.0] * n}, {"trio": [0.8 - 0.095] * n, "v3": [0.8] * n}),
                      ["trio", "v3"], ["trio", "v3"])
    check("accept margin: 0.095 worse does not", p["accept_worse"]["trio"] == 0.0, p["accept_worse"])
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
    conv = {"claude_ite": 1.0, "gpt_ite": 2.0, "gpt_ite_est": 3.0}
    tok, why = AA.task_tokens({"claude_ite": 100, "gpt_ite": 50, "gpt_ite_est": 10}, conv)
    check("conversion: 100 + 2x50 + 3x10 = 230", tok == 230.0, (tok, why))
    tok, why = AA.task_tokens({"total_ite_mixed": 500}, conv)
    check("merged-only spend row refused", tok is None and "merged" in why, why)
    tok, why = AA.task_tokens({"claude_ite": 0, "gpt_ite": 0}, conv)
    check("zero tokens refused", tok is None and "zero" in why, why)
    tok, why = AA.task_tokens({"claude_ite": -5}, conv)
    check("negative tokens refused", tok is None, why)
    tok, why = AA.task_tokens({"claude_ite": True}, conv)
    check("boolean tokens refused", tok is None, why)
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
        Path(d, "v3c.jsonl").write_text(json.dumps(dict(logs["v3"]["recs"][0], ts="2026-11-01T00:00:00")) + "\n")
        raw = AA.load_raw(d)
    check("load_raw: a good arm loads", "recs" in raw.get("trio", {}) and len(raw["trio"]["recs"]) == 60,
          {k: list(v) for k, v in raw.items()})
    check("load_raw: an unparseable line -> arm UNMEASURED", "unmeasured" in raw.get("v3", {}), raw.get("v3"))
    check("load_raw: a zoneless ts -> arm UNMEASURED", "unmeasured" in raw.get("v3c", {}), raw.get("v3c"))


def t_cli():
    tasks = make_tasks(10)
    ids = sorted(tasks)
    with tempfile.TemporaryDirectory() as d:
        for arm in ("trio", "v3"):
            Path(d, arm + ".jsonl").write_text("\n".join(json.dumps(x) for x in
                                                         arm_log(arm, [(t, True) for t in ids])) + "\n")
        td = Path(d, "tasks")
        td.mkdir()
        for t, v in tasks.items():
            Path(td, t + ".json").write_text(json.dumps(dict(v, id=t)))
        Path(d, "spend.json").write_text(json.dumps({a: spend_for((t, 1e5) for t in ids) for a in ("trio", "v3")}))
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = AA.main(["run", "--spend", str(Path(d, "spend.json")), "--raw-dir", d, "--tasks-dir", str(td),
                          "--draws", "300", "--out", str(Path(d, "out.json"))])
            rc2 = AA.main(["run", "--spend", str(Path(d, "nope.json")), "--raw-dir", d, "--tasks-dir", str(td),
                           "--draws", "300"])
        out = json.loads(Path(d, "out.json").read_text())
    check("CLI: runs end to end on raw logs and writes the report", rc == 0 and "final" in out and out["blocks"],
          (rc, out.get("final", {}).get("verdict")))
    check("CLI: unreadable spend file -> UNMEASURED, exit 3", rc2 == 3, rc2)


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
    check("noisy equal arms at the hard cap: HARD_CAP_NO_DIFFERENCE with intervals",
          r["final"]["verdict"] == "HARD_CAP_NO_DIFFERENCE" and "eff_vs_control_90" in r["final"]["intervals"]["trio"],
          r["final"]["verdict"])
    cap = T0 + 12 * 600
    r = scenario({"trio": (1.0, rng_acc, 0.8), "v3": (1.0, rng_acc, 0.8)}, 15, hard_cap=cap)
    check("records after --hard-cap are ignored and the cap counts as passed",
          r["final"]["verdict"] == "HARD_CAP_NO_DIFFERENCE"
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
        s["trio"]["T003"] = {"claude_ite": 1e308, "gpt_ite": 1e308, "gpt_ite_est": 0}
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


# ---------------------------------------------------------------- (6) simulations: calibration and power

def sim(arms, n, seed, sigma_d=0.8, draws=1000, block_kinds=True):
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
    r = AA.analyse(logs, tasks, sp, draws=draws, seed=seed)
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


def t_small_sims():
    c = calib(6, n=30, draws=600)
    check("null calibration (small, 6 seeds x 30 tasks): no false DECIDE", c["decide"] == 0, c)
    p = power(4, n=60, draws=600)
    check("power smoke (4 seeds, 1.5x): no wrong-direction stop", p["wrong_stop"] == 0, p)
    if not QUIET:
        print("INFO  small power run (not a target): %s" % json.dumps(p))


# ---------------------------------------------------------------- runner

CORE = (t_rule_probs, t_rule_verdict, t_tokens_and_inputs, t_cli, t_winner, t_fluke, t_loser, t_tie,
        t_hardcap_determinism, t_dq, t_exact_boundaries, t_malformed, t_chronology, t_dq_identity, t_nig_oracle)

MUTANTS = [("DECIDE_RATIO", 1.3125), ("DECIDE_RATIO", 1.1875), ("DECIDE_P", 0.97), ("DECIDE_P", 0.93),
           ("ACCEPT_MARGIN", 0.11), ("ACCEPT_MARGIN", 0.09), ("ACCEPT_P", 0.22), ("ACCEPT_P", 0.18),
           ("FUTILE_RATIO", 1.155), ("FUTILE_RATIO", 1.045), ("FUTILE_P", 0.07), ("FUTILE_P", 0.03),
           ("TIE_BAND", 0.17), ("TIE_BAND", 0.13), ("TIE_P", 0.92), ("TIE_P", 0.88),
           ("MIN_TASKS", 5), ("MIN_TASKS", 15), ("MIN_KINDS", 1), ("MIN_KINDS", 3), ("BLOCK", 4), ("BLOCK", 6),
           ("SIMPLER", ("v3", "v3c", "trio", "ralph_c", "ralph_a")), ("CONTROL", "v3c")]


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
