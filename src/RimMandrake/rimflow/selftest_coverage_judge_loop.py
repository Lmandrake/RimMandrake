#!/usr/bin/env python3
"""selftest_coverage_judge_loop.py - the coverage judge's loop limit (RIMMANDRAKE_STOP_COVERAGE_LOOP_AT_THIRD_REFUSAL,
spec design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md).

It replays the nine real ExplosiveKnockback verdicts (fixtures/ek_coverage_verdicts.json, from git: nine not_covered in
three hours, gaps 19,14,11,6,9,7,6,4,4) through a fake judge that answers each in turn with its real token count, and
shows judging stopping at the third: the concept blocked on REFUSAL_NOTHING_COULD_EVER_PASS, one alarm row and one told
row however often it trips, the Designer's run kept from starting (exit 3), and six verdicts never paid for. Then: a
healthy concept (two not_covered, then covered) still signs with no alarm; EK's own nine legacy charges stop it with no
judge run; a release grants exactly one more look; a release granted after named fixes waits for them and the re-pin,
then is one final look; the spend cap; the program's late tags; the alarm's route.
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
import refusal_contract as _RC  # noqa: E402

# covered signs only under a CALIBRATED coverage brief (RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS): the brief under test
# here is calibrated; selftest_judge_calibration tests the UNTESTED side
_RC.status = lambda family: "CALIBRATED"
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
    # RIMMANDRAKE_CLEAR_STALE_BLOCK_REASON_ON_LIFT (watched failing on d08616308): Pyrelands read "ready" with the
    # stop's "released for one more look ... judging stopped" still in blocked_on, and the page showed it as the why
    check("a release takes the stop's reason off the record with the block",
          "blocked_on" not in st and "blocked_on" not in DS.load_state(d), st.get("blocked_on"))
    judge.script[:] = [answer("not_covered", rounds[3]["gaps"], rounds[3]["tokens"])]
    rec, _ = CJ.run(d, os.path.join(root, "ek"), judge, now=1794100000)
    check("the one more look is judged, and not covering stops it again",
          judge.calls == 4 and rec.get("stopped") and DS.load_state(d)["status"] == "blocked", (judge.calls, rec))
    check("the trip after a release tells again (second told row)", len(told_rows(ops)) == 2, told_rows(ops))
    rec, _ = CJ.run(d, os.path.join(root, "ek"), judge, now=1794101000)
    check("and no look after that", judge.calls == 4 and rec.get("stopped"))


def granted(root, rounds):
    """RIMMANDRAKE_GRANT_LOOK_AFTER_FIXES_CLOSE: "fix first, then exactly one more look" as data. A release granted
    now with --after waits on its items closing and the re-pin landing, then counts as one final look."""
    os.environ["RM_REFUSAL_DIR"] = os.path.join(root, "refusals_granted")
    d = concept(os.path.join(root, "granted"))
    judge = Judge([answer(r["verdict"], r["gaps"], r["tokens"]) for r in rounds[:3]])
    for i in range(3):
        CJ.run(d, os.path.join(root, "granted"), judge, now=1794400000 + 1200 * i)
    check("granted: three not_covered stop judging", DS.load_state(d).get("status") == "blocked" and judge.calls == 3)
    states = {"FIX_A": "proposed"}
    saved, CJ.item_states = getattr(CJ, "item_states", None), lambda ids: {i: states.get(i) for i in ids}
    try:
        try:
            CJ.release(d, "one final look after a ticket never filed", after=["NOPE_NEVER_FILED"])
            check("granted: a grant naming an item never filed is refused", False)
        except DS.Refused as e:
            check("granted: a grant naming an item never filed is refused", "NOPE_NEVER_FILED" in str(e), str(e))
        rc = CJ.main(["release", d, "--why", "per d_x: one final look after FIX_A and its re-pin", "--after", "FIX_A"])
        st = DS.load_state(d)
        g = st.get("coverage_release_granted") or {}
        check("granted: `release --after` records the grant and the stop stands (no look yet)",
              rc == 0 and g.get("after") == ["FIX_A"] and st["status"] == "blocked" and st.get("coverage_stop")
              and st["history"][-1]["what"] == "coverage_release_granted" and RC.open_alarms()
              and CJ.plan(d, os.path.join(root, "granted"))[0] == "stopped", (rc, g, st.get("status")))
        try:
            CJ.release(d, "a second grant", after=["FIX_A"])
            check("granted: a second grant while one stands is refused", False)
        except DS.Refused as e:
            check("granted: a second grant while one stands is refused", "stands" in str(e), str(e))
        try:
            CJ.release(d, "the chain's release")
            check("granted: a release while FIX_A is open is refused, naming it", False)
        except DS.Refused as e:
            check("granted: a release while FIX_A is open is refused, naming it", "FIX_A" in str(e), str(e))
        states["FIX_A"] = "done"
        try:
            CJ.release(d, "the chain's release")
            check("granted: FIX_A closed but no re-pin since the grant: refused, naming the re-pin", False)
        except DS.Refused as e:
            check("granted: FIX_A closed but no re-pin since the grant: refused, naming the re-pin",
                  "re-pin" in str(e), str(e))
        st = DS.load_state(d)
        DS.hist(st, "locked_change", "fixed FIX_A; re-pinned stage 3 (scenes)")
        DS.write_json(DS.state_path(d), st)
        st = CJ.release(d, "the chain's release after the re-pin")
        rel = (st.get("coverage_releases") or [{}])[-1]
        check("granted: closed + re-pinned -> the grant applies as one final release; block and alarm lift",
              rel.get("final") is True and rel.get("after") == ["FIX_A"] and rel.get("granted_at") == g.get("at")
              and "coverage_release_granted" not in st and st["status"] == "ready" and not RC.open_alarms(),
              (rel, st.get("status")))
        judge.script[:] = [answer("not_covered", rounds[3]["gaps"], rounds[3]["tokens"])]
        rec, _ = CJ.run(d, os.path.join(root, "granted"), judge, now=1794500000)
        st = DS.load_state(d)
        check("granted: the final look is judged once; not covering stops it, the stop naming the final look",
              judge.calls == 4 and rec.get("stopped") and st["status"] == "blocked"
              and "final look" in (st.get("coverage_stop") or {}).get("why", ""), (judge.calls, st.get("coverage_stop")))
        rec, _ = CJ.run(d, os.path.join(root, "granted"), judge, now=1794501000)
        check("granted: and no look after the final one", judge.calls == 4 and rec.get("stopped"))
    finally:
        CJ.item_states = saved


def granted_late(root, rounds):
    """RIMMANDRAKE_ACCEPT_REPIN_BEFORE_GRANT_RECORDED_FIVE_MINUTES_LATE: Pyrelands, 2026-11-15. The fixes and their
    re-pin (locked_change 21:06:06Z) landed after the stop, and the grant was written at 21:11:14Z; the re-pin the grant
    waits on is one since the stop it lifts, not one since the grant, or the one look never applies."""
    os.environ["RM_REFUSAL_DIR"] = os.path.join(root, "refusals_granted_late")
    d = concept(os.path.join(root, "granted_late"))
    judge = Judge([answer(r["verdict"], r["gaps"], r["tokens"]) for r in rounds[:3]])
    for i in range(3):
        CJ.run(d, os.path.join(root, "granted_late"), judge, now=1794600000 + 1200 * i)
    states = {"FIX_B": "proposed"}
    saved, CJ.item_states = getattr(CJ, "item_states", None), lambda ids: {i: states.get(i) for i in ids}
    try:
        st = DS.load_state(d)
        DS.hist(st, "locked_change", "fixed FIX_B; re-pinned stage 3 (tree)")
        DS.write_json(DS.state_path(d), st)
        CJ.release(d, "per d_y: one final look after FIX_B (its re-pin already landed)", after=["FIX_B"])
        states["FIX_B"] = "done"
        st = CJ.release(d, "the chain's release")
        rel = (st.get("coverage_releases") or [{}])[-1]
        check("granted late: a re-pin since the stop but before the grant counts; the grant applies as the final look",
              rel.get("final") is True and rel.get("after") == ["FIX_B"] and st["status"] == "ready", (rel, st["status"]))
    except DS.Refused as e:
        check("granted late: a re-pin since the stop but before the grant counts; the grant applies as the final look",
              False, str(e))
    finally:
        CJ.item_states = saved
    d = concept(os.path.join(root, "granted_stale_repin"))
    os.environ["RM_REFUSAL_DIR"] = os.path.join(root, "refusals_granted_stale")
    st = DS.load_state(d)
    DS.hist(st, "locked_change", "an older re-pin, before the stop")
    DS.write_json(DS.state_path(d), st)
    judge = Judge([answer(r["verdict"], r["gaps"], r["tokens"]) for r in rounds[:3]])
    for i in range(3):
        CJ.run(d, os.path.join(root, "granted_stale_repin"), judge, now=1794700000 + 1200 * i)
    saved, CJ.item_states = getattr(CJ, "item_states", None), lambda ids: {i: "done" for i in ids}
    try:
        CJ.release(d, "per d_z: one final look after FIX_C", after=["FIX_C"])
        CJ.release(d, "the chain's release")
        check("granted late: a re-pin from before the stop does not count", False)
    except DS.Refused as e:
        check("granted late: a re-pin from before the stop does not count", "re-pin" in str(e), str(e))
    finally:
        CJ.item_states = saved


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


def loopholes(root):
    """RIMMANDRAKE_HASH_EVERY_COVERAGE_INPUT: scenes.json edited mid-judge, a failed runner, the caps after a release."""
    os.environ["RM_REFUSAL_DIR"] = os.path.join(root, "refusals_loopholes")

    class Editing(Judge):
        def __call__(self, argv, cwd, env, timeout):
            with open(os.path.join(self.d, "scenes.json"), "a") as f:
                f.write("\n")
            return super().__call__(argv, cwd, env, timeout)
    d = concept(os.path.join(root, "loop_scenes"))
    j = Editing([answer("covered", [], 1000)])
    j.d = d
    rec, _ = CJ.run(d, os.path.join(root, "loop_scenes"), j, now=1794300000)
    check("scenes.json edited while the judge reads it: a covered verdict is not signed",
          not rec.get("signed") and "scenes.json" in str(rec.get("error")), (rec.get("signed"), rec.get("error")))

    class Failing(Judge):
        def __call__(self, argv, cwd, env, timeout):
            return 1, super().__call__(argv, cwd, env, timeout)[1]
    d = concept(os.path.join(root, "loop_exit"))
    rec, _ = CJ.run(d, os.path.join(root, "loop_exit"), Failing([answer("covered", [], 1000)]), now=1794300100)
    check("a well-formed covered verdict from a runner that exited 1 is not taken or signed",
          not rec.get("signed") and rec.get("verdict") != "covered" and "exited 1" in str(rec.get("error")),
          (rec.get("verdict"), rec.get("signed"), rec.get("error")))

    st = {"coverage_releases": [{"rounds_at": 1}],
          "coverage_rounds": [{"judge": "j0", "verdict": "not_covered", "tokens": 1}] +
                             [{"judge": "j%d" % i, "verdict": "covered", "tokens": 1} for i in range(1, 1 + CJ.JUDGE_RUNS_MAX)]}
    why = CJ.stop_reason(st)
    check("after a release the run cap still binds, counted from the release (%d covered looks)" % CJ.JUDGE_RUNS_MAX,
          bool(why) and "since the release" in why, why)
    st = {"coverage_releases": [{"rounds_at": 0}],
          "coverage_rounds": [{"judge": "j%d" % i, "verdict": "malformed", "tokens": 1} for i in range(CJ.MALFORMED_LIMIT)]
          + [{"judge": "jc", "verdict": "covered", "tokens": 1}]}
    check("after a release the malformed cap still binds while the last look reads covered",
          bool(CJ.stop_reason(st)), CJ.stop_reason(st))


def main():
    CJ.CONTRACT = False   # bare gaps test another rule; the refusal record is selftest_coverage_refusal_record
    CJ.delta_plan = lambda d, prior, read=None: None   # the full judge's loop; the delta re-judge is selftest_coverage_delta
    DS.owner_away = lambda: (False, "selftest: attended")   # the real presence must not move this test
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
            granted(root, rounds)
            granted_late(root, rounds)
            healthy(root)
            legacy(root, rounds)
            units()
            loopholes(root)
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
