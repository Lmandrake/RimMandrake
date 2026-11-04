#!/usr/bin/env python3
"""live_observe's RMOBS protocol, validated against good and bad worlds (LIVE_ROWS_FIX_STOP_GUESSING_LOGS; GPT
test-tolerance advice 2026-11-04 rank 4 and its replay-bank table): a good implementation reads SATISFIED, a known
violation VIOLATED with its observation, a stopped or blind run UNREACHED/UNKNOWN, a malformed or foreign row INVALID,
a final PASS never erases a violation, the whole log is read, and no rows at all is NONE (the regex fallback)."""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import live_observe as O     # noqa: E402

FAILS = []
RUN = "ROT_X-A2-20270115T080000Z"


def check(name, cond, detail=""):
    if not cond:
        FAILS.append((name, detail))


def row(result, stage="result", run=RUN, clause="A2", **kw):
    r = dict(kw, run=run, clause=clause, result=result, stage=stage)
    r.setdefault("expected", ">= 1")
    r.setdefault("observed", 1)
    return "RMOBS " + json.dumps(r)


CASES = [   # (name, log, status, why holds)
    ("good world", row("SATISFIED", "observation") + "\n" + row("SATISFIED"), "SATISFIED", "A2 SATISFIED"),
    ("known violation, measured absence", row("VIOLATED", "evaluation", expected=">= 1 RM_Chittik", observed=0,
                                              absence=True), "VIOLATED", "a measured absence"),
    ("a final PASS line never overrides a violation",
     row("VIOLATED", "evaluation", observed=0) + "\n" + row("SATISFIED") + "\nVERDICT PASS", "VIOLATED", "observed 0"),
    ("a malformed row does not erase a violation", row("VIOLATED", "evaluation", observed=3) + "\nRMOBS {bad",
     "VIOLATED", "observed 3"),
    ("a violation of another clause is not this one's", row("VIOLATED", clause="A3", observed=0) + "\n" +
     row("SATISFIED"), "SATISFIED", ""),
    ("an observed None without absence is no measurement", row("VIOLATED", "evaluation", observed=None), "UNKNOWN",
     "blind read"),
    ("a satisfied None without absence is no measurement", row("SATISFIED", observed=None), "UNKNOWN", "blind read"),
    ("stale run id", row("SATISFIED", run="ROT_X-A2-20270114T080000Z"), "INVALID", "stale or foreign"),
    ("not JSON", row("SATISFIED") + "\nRMOBS {nope", "INVALID", "malformed"),
    ("not an object", row("SATISFIED") + "\nRMOBS [1]", "INVALID", "not a JSON object"),
    ("bad result word", row("PASS"), "INVALID", "result 'PASS'"),
    ("bad stage", row("SATISFIED", stage="done"), "INVALID", "stage 'done'"),
    ("measured without expected", "RMOBS " + json.dumps({"run": RUN, "clause": "A2", "result": "VIOLATED",
                                                         "stage": "evaluation", "observed": 0}), "INVALID",
     "without 'expected'"),
    ("prereqs not an object", row("SATISFIED", prereqs=["map"]), "INVALID", "prereqs"),
    ("stopped before result", row("SATISFIED", "observation"), "UNKNOWN", "stopped at observation"),
    ("unreached at transport", row("UNREACHED", "transport", note="bridge refused"), "UNREACHED", "bridge refused"),
    ("unknown beats satisfied", row("SATISFIED", "observation") + "\n" + row("UNKNOWN", "setup", note="no map"),
     "UNKNOWN", "no map"),
    ("rows only for another clause", row("SATISFIED", clause="A3"), "UNKNOWN", "none for this clause"),
    ("no rows: the regex fallback", "VERDICT PASS\nA1 FAIL: x", "NONE", "regex"),
    ("empty log", "", "NONE", ""),
    ("the decisive row far above the end (an 8 KB tail would miss it)",
     row("VIOLATED", "evaluation", observed=0) + "\n" + "x" * 200_000 + "\n" + row("SATISFIED"), "VIOLATED", ""),
]


def t_cases():
    for name, text, status, why in CASES:
        r = O.read(text, RUN, "A2")
        check("%s -> %s" % (name, status), r.status == status and why in r.why, (r.status, r.why, r.problems))


def t_stage_and_summary():
    r = O.read(row("SATISFIED", "observation") + "\n" + row("SATISFIED", "result", evidence=["/x.json"],
                                                             identity={"site": "s", "deploy": "d", "session": "g"}),
               RUN, "A2")
    s = r.summary()
    check("stage is the furthest reached", r.stage == "result" and s["rows"] == 2 and s["status"] == "SATISFIED", s)
    check("summary is JSON", json.loads(json.dumps(s)) == s, s)


def t_no_run_id_is_invalid():
    r = O.read(row("SATISFIED"), "", "A2")
    check("no run id from the supervisor: INVALID", r.status == "INVALID" and "no run id" in r.why, r.why)


def t_emit_round_trips():
    buf = io.StringIO()
    os.environ[O.RUN_ENV] = RUN
    O.emit("A2", "VIOLATED", "evaluation", expected="enabled", observed=None, absence=True, out=buf,
           identity={"session": "g"})
    O.emit("A2", "SATISFIED", "result", expected="x", observed="x", out=buf)
    r = O.read(buf.getvalue(), RUN, "A2")
    check("emit -> read: a measured absence of None is VIOLATED", r.status == "VIOLATED" and len(r.rows) == 2,
          (r.status, r.why, buf.getvalue()))


def t_huge_log_is_cut_and_says_so():
    big = row("VIOLATED", "evaluation", observed=0) + "\n" + "y" * (O.LOG_MAX + 10)
    r = O.read(big, RUN, "A2")
    check("a log past LOG_MAX keeps its head and says it was cut", r.status == "VIOLATED" and r.cut, (r.status, r.cut))


def t_run_id_of():
    check("run id is the log's stem", O.run_id_of("/r/live/ROT_X-A2-20270115T080000Z-1.log")
          == "ROT_X-A2-20270115T080000Z-1")


def main():
    for t in (t_cases, t_stage_and_summary, t_no_run_id_is_invalid, t_emit_round_trips, t_huge_log_is_cut_and_says_so,
              t_run_id_of):
        try:
            t()
        except Exception as e:     # noqa: BLE001  a crash is a red, named
            FAILS.append((t.__name__, "crashed: %r" % e))
    if FAILS:
        print(json.dumps(FAILS, default=str)[:3000])
    print("selftest_live_observe:", "FAIL" if FAILS else "OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
