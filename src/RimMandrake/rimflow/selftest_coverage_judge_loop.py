#!/usr/bin/env python3
"""selftest_coverage_judge_loop.py - the coverage judge's loop limit (RIMMANDRAKE_STOP_COVERAGE_LOOP_AT_THIRD_REFUSAL,
spec design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md).

It replays the nine real ExplosiveKnockback verdicts (fixtures/ek_coverage_verdicts.json, from git: nine not_covered in
three hours, gaps 19,14,11,6,9,7,6,4,4) through a fake judge that answers each in turn with its real token count, and
shows judging stopping at the third: the concept blocked on REFUSAL_NOTHING_COULD_EVER_PASS, one alarm row and one told
row however often it trips, the Designer's run kept from starting (exit 3), and six verdicts never paid for. Then: a
healthy concept (two not_covered, then covered) still signs with no alarm; EK's own nine legacy charges stop it with no
judge run; a release grants exactly one more look; the spend cap; the program's late tags; the alarm's route.
The claude call, the signature and the exam are stubbed; every write goes to a temp dir."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import concept_tree as CT  # noqa: E402
import coverage_judge as CJ  # noqa: E402
import designer_stage as DS  # noqa: E402
import incident  # noqa: E402
import refusal_contract as RC  # noqa: E402
from selftest_coverage_judge import concept  # noqa: E402

FIXTURE = os.path.join(HERE, "fixtures", "ek_coverage_verdicts.json")
FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def answer(verdict, gaps, tokens):
    res = {"structured_output": {"verdict": verdict, "gaps": [dict(g) for g in gaps], "reasons": "r", "checklist": []},
           "session_id": "sess"}
    if tokens is not None:
        res["usage"] = {"input_tokens": tokens, "output_tokens": 0, "cache_read_input_tokens": 0,
                        "cache_creation_input_tokens": 0}
    return json.dumps(res)


class Judge:
    """A fake judge: each call answers the next scripted verdict and counts itself."""

    def __init__(self, script):
        self.script, self.calls = list(script), 0

    def __call__(self, argv, cwd, env, timeout):
        self.calls += 1
        return 0, self.script.pop(0)


def told_rows(ops):
    p = os.path.join(ops, "told.jsonl")
    if not os.path.exists(p):
        return []
    with open(p) as f:
        return [json.loads(x) for x in f if x.strip() and RC.ALARM_ID in x]


def ek_replay(root, rounds, ops):
    d = concept(os.path.join(root, "ek"))
    judge = Judge([answer(r["verdict"], r["gaps"], r["tokens"]) for r in rounds])
    out = []
    for i in range(len(rounds)):
        rec, msg = CJ.run(d, os.path.join(root, "ek"), judge, now=1794000000 + 1200 * i)
        out.append((judge.calls, rec, msg, DS.load_state(d).get("status")))
    check("rounds 1 and 2 are judged and leave the concept unblocked",
          [o[0] for o in out[:2]] == [1, 2] and all(o[3] != "blocked" for o in out[:2])
          and all(not (o[1] or {}).get("stopped") for o in out[:2]), [(o[0], o[2], o[3]) for o in out[:2]])
    check("round 3's not_covered stops judging: concept blocked on the alarm",
          out[2][0] == 3 and out[2][1].get("verdict") == "not_covered" and out[2][1].get("stopped")
          and out[2][3] == "blocked" and DS.load_state(d)["blocked_on"].startswith(RC.ALARM_ID), out[2][2])
    check("rounds 4-9 never launch a judge", judge.calls == 3 and all((o[1] or {}).get("stopped") for o in out[3:]),
          (judge.calls, [o[2] for o in out[3:]]))
    st = DS.load_state(d)
    check("three rounds on file, every gap tagged",
          len(st.get("coverage_rounds") or []) == 3 and all(
              g.get("new_since") in CJ.TAGS for g in json.load(open(os.path.join(d, CJ.VERDICT_FILE)))["gaps"]),
          st.get("coverage_rounds"))
    late = [len(r.get("late") or []) for r in st["coverage_rounds"]]
    check("round 1 has no late gaps; later rounds' new ids are counted late (judge misses)",
          late[0] == 0 and sum(late[1:]) > 0, late)
    rows = RC.open_alarms()
    check("one open alarm row for the concept", len(rows) == 1 and rows[0]["subject"] == "concept:Foo"
          and rows[0]["trips"] == 7, rows)
    check("one told row however often it trips", len(told_rows(ops)) == 1, told_rows(ops))
    check("the Designer's pre-launch step exits 3 (its claude never starts) and launches no judge",
          CJ.main(["run", d]) == CJ.STOP_EXIT and judge.calls == 3)
    spared = sum(r["tokens"] or 0 for r in rounds[3:])
    spent = CJ.spend(CJ.rounds(st, d))
    print("     EK replay: judged 3 of 9, spend counted %d tokens (round 1 unmeasured at the p90), "
          "spared %d measured tokens over 6 verdicts; late ids per round %s" % (spent, spared, late))
    return d, judge


def release(d, judge, root, ops, rounds):
    try:
        CJ.release(d, "  ")
        check("a release without a reason is refused", False)
    except DS.Refused:
        check("a release without a reason is refused", True)
    st = CJ.release(d, "the Conductor read the gaps and wants one more look")
    check("a release unblocks and closes the alarm row", st["status"] == "ready" and not RC.open_alarms())
    judge.script[:] = [answer("not_covered", rounds[3]["gaps"], rounds[3]["tokens"])]
    rec, _ = CJ.run(d, os.path.join(root, "ek"), judge, now=1794100000)
    check("the one more look is judged, and not covering stops it again",
          judge.calls == 4 and rec.get("stopped") and DS.load_state(d)["status"] == "blocked", (judge.calls, rec))
    check("the trip after a release tells again (second told row)", len(told_rows(ops)) == 2, told_rows(ops))
    rec, _ = CJ.run(d, os.path.join(root, "ek"), judge, now=1794101000)
    check("and no look after that", judge.calls == 4 and rec.get("stopped"))


def healthy(root):
    os.environ["RM_REFUSAL_DIR"] = os.path.join(root, "refusals_healthy")   # every fixture concept is named Foo
    d = concept(os.path.join(root, "healthy"))
    gaps1 = [{"what": "a", "where": "x", "return_to": 3, "ids": ["l1"], "new_since": "first"},
             {"what": "b", "where": "y", "return_to": 3, "ids": ["l2"], "new_since": "first"}]
    gaps2 = [{"what": "b", "where": "y", "return_to": 3, "ids": ["l2"], "new_since": "unfixed"}]
    judge = Judge([answer("not_covered", gaps1, 700000), answer("not_covered", gaps2, 700000),
                   answer("covered", [], 700000)])
    recs = [CJ.run(d, os.path.join(root, "healthy"), judge, now=1794200000 + i)[0] for i in range(3)]
    st = DS.load_state(d)
    check("healthy: two not_covered then covered -> signed, never stopped, no alarm",
          judge.calls == 3 and recs[2]["signed"] and not any(r.get("stopped") for r in recs)
          and st["status"] != "blocked" and not RC.open_alarms(),
          [(r.get("verdict"), r.get("signed"), r.get("stopped")) for r in recs])
    check("healthy: an unfixed gap is not counted late", not recs[1].get("late"), recs[1].get("late"))


def legacy(root, rounds):
    os.environ["RM_REFUSAL_DIR"] = os.path.join(root, "refusals_legacy")
    d = concept(os.path.join(root, "legacy"))
    st = DS.load_state(d)
    for r in rounds:
        DS.charge_state(st, r["tokens"] or 0, "review" if r["tokens"] is not None else "unmeasured", r["judge"])
    DS.write_json(DS.state_path(d), st)
    judge = Judge([])
    what, why = CJ.plan(d, os.path.join(root, "legacy"))
    rec, _ = CJ.run(d, os.path.join(root, "legacy"), judge)
    check("EK's nine charged judges (no rounds on file) stop it with no judge run",
          what == "stopped" and "9 judge runs" in why and judge.calls == 0 and rec.get("stopped")
          and DS.load_state(d)["status"] == "blocked", (what, why, judge.calls))


def units():
    st = {"coverage_rounds": [{"judge": "j1", "verdict": "not_covered", "tokens": 1600000},
                              {"judge": "j2", "verdict": "not_covered", "tokens": 1500000}]}
    check("spend past 4x the p90 stops at two rounds", "spend" in (CJ.stop_reason(st) or ""), CJ.stop_reason(st))
    st["coverage_rounds"][1]["tokens"] = 10
    check("two cheap rounds do not stop", CJ.stop_reason(st) is None, CJ.stop_reason(st))
    st["coverage_rounds"] += [{"judge": "j3", "verdict": None, "tokens": None}, {"judge": "j4", "verdict": None}]
    check("a fourth judge run stops even with no third not_covered", "4 judge runs" in (CJ.stop_reason(st) or ""),
          CJ.stop_reason(st))
    gaps = [{"ids": ["a"], "new_since": "first"}, {"ids": ["b"], "new_since": "unfixed"},
            {"ids": ["c"], "new_since": "changed", "since": "scenes.json"}, {"ids": [], "new_since": "late"}]
    late = CJ.tag_gaps(gaps, [{"ids": ["a"]}])
    check("tags: named before -> unfixed; new ids with no change -> late; changed stands",
          [g["new_since"] for g in gaps] == ["unfixed", "late", "changed", "late"] and late == ["b"], (gaps, late))
    rt = incident.route_of(incident.load_table(), RC.ALARM_ID)
    check("the alarm routes to the Conductor, cause refusals",
          rt and rt["route"] == "role" and rt["reader"] == "Conductor" and rt.get("cause") == "refusals", rt)


def main():
    saved = (CT.coverage_problem, CT.sign, DS.exam_errors)
    CT.coverage_problem = lambda d, repo, tree: "no coverage signature"
    CT.sign = lambda d, by, repo=None, **kw: []
    DS.exam_errors = lambda ex, d, st, repo=None: []
    env = {k: os.environ.get(k) for k in ("RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR", "RM_DISPATCHER_STATE")}
    with open(FIXTURE) as f:
        rounds = json.load(f)["rounds"]
    check("the fixture holds the nine real EK verdicts",
          len(rounds) == 9 and [len(r["gaps"]) for r in rounds] == [19, 14, 11, 6, 9, 7, 6, 4, 4]
          and all(r["verdict"] == "not_covered" for r in rounds))
    try:
        with tempfile.TemporaryDirectory() as root:
            ops = os.path.join(root, "ops")
            os.makedirs(ops)
            os.environ.update(RM_REFUSAL_DIR=os.path.join(root, "refusals"), RM_OPS_WATCH_DIR=ops,
                              RM_DISPATCHER_STATE=os.path.join(root, "dispatcher"))
            d, judge = ek_replay(root, rounds, ops)
            release(d, judge, root, ops, rounds)
            healthy(root)
            legacy(root, rounds)
            units()
    finally:
        CT.coverage_problem, CT.sign, DS.exam_errors = saved
        for k, v in env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    print("selftest_coverage_judge_loop: %s" % ("FAIL (%d)" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
