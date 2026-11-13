#!/usr/bin/env python3
"""selftest_designer_park.py - the Designer parks for him (RIMMANDRAKE_PARK_UNATTENDED_DESIGNER_LOOPS) and its
judge-and-rework loop has a hard ceiling at twice the item's cap (RIMMANDRAKE_CEIL_JUDGE_LOOPS_AT_TWICE_CAP); owner note
OWNER.jsonl:1794527688430451936 and card OWNER.jsonl:1794527885746395760 on RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS.

It replays the real ExplosiveKnockback night two ways:
- its nine coverage verdicts (fixtures/ek_coverage_verdicts.json) with him away: judging parks at the SECOND refusal,
  one page for him, no judge, no Designer run, no release, no alarm after it, until his own word lifts it;
- its 83 budget charges (fixtures/ek_night_charges.json, stage.json at 780b1d1e85): the loop parks the first time its
  spend since the first judge reaches 8M (2 x the 4M cap), attended or not; spend with no judge loop stays advisory.
Then: a healthy attended walk still signs; a step ending in his certification parks only when he is away; his queue
line shouts QUICK LOOK OFFERED only when code exists; the away detector reads mode and sitting, never his input clock.
The claude call, signature, exam and result validation are stubbed; every write goes to a temp dir, and the real
alarm and told files are checked unchanged."""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cli  # noqa: E402
import concept_tree as CT  # noqa: E402
import coverage_judge as CJ  # noqa: E402
import designer_stage as DS  # noqa: E402
import incident  # noqa: E402
import refusal_contract as RC  # noqa: E402
from selftest_coverage_judge import concept  # noqa: E402
from selftest_coverage_judge_loop import Judge, answer, told_rows  # noqa: E402

VERDICTS = os.path.join(HERE, "fixtures", "ek_coverage_verdicts.json")
CHARGES = os.path.join(HERE, "fixtures", "ek_night_charges.json")
REAL_AWAY = DS.owner_away
FAILS = []
AWAY = lambda: (True, "selftest: away")        # noqa: E731
HERE_NOW = lambda: (False, "selftest: attended")   # noqa: E731


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def refused(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except DS.Refused as e:
        return str(e)
    return None


def owner_line(root, item="FOO_ITEM", **kw):
    """An OWNER-shard event naming the item, stamped now (after any park already written)."""
    t = time.time()
    with open(os.path.join(root, CT.OWNER_SHARD), "a", encoding="utf-8") as f:
        f.write(json.dumps(dict({"seat": "OWNER", "event": "note", "id": item, "ts": DS.now_iso(),
                                 "tsn": int(t * 1e9)}, **kw)) + "\n")


def ek_unattended(base, rounds, ops):
    DS.owner_away = AWAY
    root = os.path.join(base, "ek")
    d = concept(root)
    check("sanity: the concept's clone is the temp root (his word is read there, not from the real shard)",
          DS.clone_of(d) == os.path.abspath(root), DS.clone_of(d))
    judge = Judge([answer(r["verdict"], r["gaps"], r["tokens"]) for r in rounds])
    out = [CJ.run(d, root, judge, now=1794000000 + 1200 * i) for i in range(len(rounds))]
    check("away: round 1's refusal is judged and does not park", judge.calls >= 1 and not out[0][0].get("parked")
          and not out[0][0].get("stopped"), out[0][1])
    check("away: round 2's refusal parks the concept (the SECOND refusal)",
          out[1][0].get("verdict") == "not_covered" and "refused 2 times" in str(out[1][0].get("parked")), out[1][1])
    check("away: rounds 3-9 never launch a judge", judge.calls == 2 and all(o[0].get("parked") for o in out[2:]),
          (judge.calls, [o[1] for o in out[2:]]))
    st = DS.load_state(d)
    page = open(os.path.join(d, DS.PARK_FILE)).read() if os.path.exists(os.path.join(d, DS.PARK_FILE)) else ""
    check("away: status waiting_owner, park kind second_refusal, written once",
          st["status"] == "waiting_owner" and st["park"]["kind"] == "second_refusal"
          and sum(1 for h in st["history"] if h["what"] == "park") == 1, (st["status"], st.get("park")))
    check("away: the one page names what is settled, refused, the smallest fixes and what he must decide",
          all(s in page for s in ("## Settled", "## Refused, and why", "## Smallest fixes", "## What you must decide"))
          and "1. " in page and "FOO_ITEM" in page, page[:300])
    check("away: no code in the record, so no quick look is offered", "QUICK LOOK" not in page
          and st["park"]["quick_look"] is False, st["park"])
    check("away: plan says parked", CJ.plan(d, root)[0] == "parked", CJ.plan(d, root))
    check("away: the Designer's pre-launch step exits 3 and launches no judge",
          CJ.main(["run", d]) == CJ.STOP_EXIT and judge.calls == 2)
    r = refused(CJ.release, d, "the Conductor wants one more look")
    check("away: a release (a seat's word) cannot lift a park", r and "only his word" in r, r)
    r = refused(DS.open_run, d, "run-after-park", repo=root)
    check("away: no Designer run opens (no rework helper relaunches a judge)", r and r.startswith("PARKED (second_refusal)"), r)
    check("away: no alarm row and no told row (a park is his page, not an incident)",
          not RC.open_alarms() and not told_rows(ops), (RC.open_alarms(), told_rows(ops)))
    t = DS.pending_turn(d, root)
    check("away: his queue shows the park page as the turn, its reason first",
          t and t["turn"].endswith(DS.PARK_FILE) and t["asks"][0]["id"] == "park" and not t["quick_look"]
          and not DS.turn_line(t).startswith("QUICK LOOK"), t)

    # lifting: only his own word
    owner_line(root, perRuling="CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM", text="a per-ruling note")
    owner_line(root, seat="BENCH", why="a seat's own reason")
    check("lift: a --per-ruling act or a seat's note on the item does not lift it",
          DS.standing_park(DS.load_state(d), d, root) and CJ.plan(d, root)[0] == "parked", CJ.plan(d, root))
    owner_line(root, item="OTHER_ITEM", ownerSaid="go on with the other one")
    check("lift: his word on another item does not lift it", CJ.plan(d, root)[0] == "parked", CJ.plan(d, root))
    owner_line(root, ownerSaid="rework gaps 3 and 5, waive the rest")
    check("lift: his ownerSaid on the item lifts it", DS.standing_park(DS.load_state(d), d, root) is None)
    judge.script[:] = [answer("covered", [], 700000)]
    rec, msg = CJ.run(d, root, judge)
    st = DS.load_state(d)
    check("lift: the next look is judged, the park moves to parks with lifted_at, the loop restarts",
          judge.calls == 3 and rec.get("signed") and "park" not in st and len(st.get("parks") or []) == 1
          and st["parks"][0].get("lifted_at") and st.get("loop_since") == st["parks"][0]["lifted_at"], (msg, st.get("parks")))


def by_card_lifts(base):
    DS.owner_away = AWAY
    root = os.path.join(base, "card")
    d = concept(root)
    DS.park(d, "certification", "selftest", root)
    owner_line(root, byCard="Designer path -> Light path when code exists")
    st = DS.load_state(d)
    check("lift: his card answer on the item lifts it too, at the next open",
          DS.lift_park(st, d, root) and st["status"] == "ready", st.get("status"))
    check("guard: an unknown park kind is refused", refused(DS.park, d, "bored", "x", root) is not None)


def replay_charges(st, charges):
    """Append the night's charges in order; -> (index, spend, at) of the first ceiling trip, or None."""
    st["budget"]["charges"], st["budget"]["spent"] = [], 0
    for i, c in enumerate(charges):
        st["budget"]["charges"].append(dict(c))
        st["budget"]["spent"] += int(c.get("tokens") or 0)
        if DS.loop_ceiling(st):
            return i, DS.loop_spend(st), c["at"]
    return None


def ceiling(base):
    DS.owner_away = HERE_NOW        # the ceiling holds attended or not
    fx = json.load(open(CHARGES))
    charges = fx["charges"]
    check("the charges fixture holds EK's 83 night charges, 9 of them judges",
          len(charges) == 83 and sum(1 for c in charges if c["ref"].startswith(DS.JUDGE_REF)) == 9
          and fx["cap"] == 4000000, len(charges))
    root = os.path.join(base, "ceil")
    d = concept(root)
    st = DS.load_state(d)
    first_judge = min(i for i, c in enumerate(charges) if c["ref"].startswith(DS.JUDGE_REF))
    pre = sum(int(c["tokens"] or 0) for c in charges[:first_judge])
    trip = replay_charges(st, charges)
    check("ceiling: nothing before the first judge counts (no loop yet: advisory)",
          trip and trip[0] > first_judge, (trip, first_judge))
    prev = dict(st, budget=dict(st["budget"], charges=st["budget"]["charges"][:-1]))
    check("ceiling: the first trip is the charge that takes the loop's spend to 8M (2 x the 4M cap)",
          trip and trip[1] >= 8000000 and (DS.loop_spend(prev) or 0) < 8000000, (trip, DS.loop_spend(prev)))
    print("     EK night: %d tokens before the first judge (advisory); the loop trips at charge %d of 83 (%s), "
          "%d loop tokens; the night went on to %d in all" % (
              pre, trip[0] + 1, trip[2], trip[1], sum(int(c["tokens"] or 0) for c in charges)))
    DS.write_json(DS.state_path(d), st)
    r = refused(DS.open_run, d, "preview", repo=root, commit=False)
    check("ceiling: the launcher's preview is refused and writes nothing",
          r and r.startswith("PARKED (ceiling)") and "park" not in DS.load_state(d), r)
    r = refused(DS.open_run, d, "r1", repo=root)
    st2 = DS.load_state(d)
    check("ceiling: open_run parks the concept (waiting_owner, kind ceiling, page written) and refuses",
          r and r.startswith("PARKED (ceiling)") and st2["status"] == "waiting_owner"
          and st2["park"]["kind"] == "ceiling" and os.path.exists(os.path.join(d, DS.PARK_FILE)), r)
    r = refused(DS.open_run, d, "r2", repo=root)
    check("ceiling: the next open is refused on the standing park", r and r.startswith("PARKED (ceiling)"), r)
    check("ceiling: the judge is parked too", CJ.plan(d, root)[0] == "parked", CJ.plan(d, root))
    owner_line(root, ownerSaid="one more round, then stop")
    text, _ = DS.open_run(d, "r3", repo=root)
    st3 = DS.load_state(d)
    check("ceiling: his word lifts it and restarts the loop's count from then",
          text and "park" not in st3 and DS.loop_spend(st3) == 0 and not DS.loop_ceiling(st3), DS.loop_spend(st3))

    # a stage with no judge round stays advisory past the cap (ruling 2026-11-04)
    d2 = concept(os.path.join(base, "advisory"))
    st = DS.load_state(d2)
    for k in range(5):
        DS.charge_state(st, 2500000, "stage", "run build-%d" % k)
    DS.write_json(DS.state_path(d2), st)
    check("advisory: 12.5M of stage runs with no judge loop is no ceiling", DS.loop_ceiling(st) is None
          and DS.loop_spend(st) is None, DS.loop_spend(st))
    text, _ = DS.open_run(d2, "b1", repo=os.path.join(base, "advisory"))
    check("advisory: the run still opens (over budget is advisory)", text and "park" not in DS.load_state(d2)
          and any(h["what"] == "over_budget" for h in DS.load_state(d2)["history"]))


def healthy(base):
    DS.owner_away = HERE_NOW
    os.environ["RM_REFUSAL_DIR"] = os.path.join(base, "refusals_healthy")
    root = os.path.join(base, "healthy")
    d = concept(root)
    g = [{"what": "a", "where": "x", "return_to": 3, "ids": ["l1"], "new_since": "first"}]
    judge = Judge([answer("not_covered", g, 700000), answer("not_covered", [dict(g[0], new_since="unfixed")], 700000),
                   answer("covered", [], 700000)])
    recs = [CJ.run(d, root, judge, now=1794200000 + i)[0] for i in range(3)]
    st = DS.load_state(d)
    check("healthy attended walk: two refusals then covered -> signed, never parked",
          judge.calls == 3 and recs[2]["signed"] and not any(r.get("parked") for r in recs) and "park" not in st,
          [(r.get("verdict"), r.get("parked")) for r in recs])
    DS.owner_away = AWAY
    root = os.path.join(base, "healthy_away")
    d = concept(root)
    judge = Judge([answer("not_covered", g, 700000), answer("covered", [], 700000)])
    recs = [CJ.run(d, root, judge, now=1794300000 + i)[0] for i in range(2)]
    check("healthy away: one refusal then covered -> signed (away parks the second refusal, not the first)",
          recs[1].get("signed") and not any(r.get("parked") for r in recs), recs)


def stage_concept(base, name, inventory):
    root = os.path.join(base, name)
    d = concept(root, stage=2, status="ready")
    st = DS.load_state(d)
    st.setdefault("results", [])
    DS.write_json(DS.state_path(d), st)
    DS.write_json(os.path.join(d, "record.json"), {"inventory": inventory, "asks": [
        {"id": "ask_blast", "status": "sent", "text": "Which way does a wall throw a pawn?"}]})
    return root, d


def certification(base):
    real = DS.result_errors
    DS.result_errors = lambda res, d, st, repo=None: []     # the park is under test, not the result's validation
    try:
        built = [{"id": "knockback", "impl": "present", "impl_evidence": "src/x.cs"}]
        for name, away, inv, quick in (("cert_away", AWAY, built, True), ("cert_here", HERE_NOW, built, False),
                                       ("cert_nocode", AWAY, [{"id": "k", "impl": "absent"}], False)):
            DS.owner_away = away
            root, d = stage_concept(base, name, inv)
            DS.open_run(d, "c1", repo=root)
            res = {"run": "c1", "stage": 2, "outcome": "waiting_owner", "summary": "asked"}
            if quick:
                res["quick_look"] = {"offer": True, "settles": ["ask_blast"], "scene": "sc_wall"}
            DS.write_json(os.path.join(d, "result.json"), res)
            ok, errs = DS.close_run(d, "c1", 1000, repo=root)
            st = DS.load_state(d)
            parked = isinstance(st.get("park"), dict)
            t = DS.pending_turn(d, root)
            line = DS.turn_line(t) if t else ""
            if name == "cert_away":
                page = open(os.path.join(d, DS.PARK_FILE)).read()
                check("certification away: a step ending in his answer parks (kind certification)",
                      ok and parked and st["park"]["kind"] == "certification" and st["status"] == "waiting_owner", errs)
                check("certification away, code present: the page and his queue line say QUICK LOOK OFFERED",
                      "## QUICK LOOK OFFERED" in page and "knockback" in page and line.startswith("QUICK LOOK OFFERED: ")
                      and t["asks"][0]["id"] == "park" and t["asks"][1]["id"] == "ask_blast", line)
                r = refused(DS.open_run, d, "c2", repo=root)
                check("certification away: no run opens until his word", r and r.startswith("PARKED (certification)"), r)
            elif name == "cert_here":
                check("certification attended: no park, the ordinary waiting turn",
                      ok and not parked and st["status"] == "waiting_owner" and t and not str(t["turn"] or "").endswith(DS.PARK_FILE)
                      and not line.startswith("QUICK LOOK"), (st.get("park"), line))
            else:
                page = open(os.path.join(d, DS.PARK_FILE)).read()
                check("certification away, no code yet: parked, and no quick look is offered",
                      ok and parked and "QUICK LOOK" not in page and not line.startswith("QUICK LOOK"), line)
        DS.owner_away = HERE_NOW
        root, d = stage_concept(base, "cert_result_offer", built)
        DS.open_run(d, "c1", repo=root)
        DS.write_json(os.path.join(d, "result.json"), {"run": "c1", "stage": 2, "outcome": "waiting_owner",
                                                       "quick_look": {"offer": True, "settles": ["ask_blast"]}})
        DS.close_run(d, "c1", 1000, repo=root)
        t = DS.pending_turn(d, root)
        check("attended, the result offers a quick look: his queue line still shouts it",
              t and DS.turn_line(t).startswith("QUICK LOOK OFFERED: "), t)
    finally:
        DS.result_errors = real


def away_units():
    DS.owner_away = REAL_AWAY
    saved = (cli._mode_file, cli._owner_verdict, os.environ.get("RIMFLOW_MODE"))
    os.environ.pop("RIMFLOW_MODE", None)
    try:
        cli._mode_file = lambda: "afk"
        cli._owner_verdict = lambda holds, evs=None: (False, "his last deliberate interaction was 2 min ago")
        check("away: the recorded mode afk is away", DS.owner_away()[0] is True, DS.owner_away())
        cli._mode_file = lambda: "belt"
        check("present: mode belt and a sitting 2 min old is attended", DS.owner_away()[0] is False, DS.owner_away())
        os.environ["RIMFLOW_MODE"] = "afk"
        check("away: RIMFLOW_MODE=afk beats the file", DS.owner_away()[0] is True, DS.owner_away())
        os.environ.pop("RIMFLOW_MODE")
        cli._owner_verdict = lambda holds, evs=None: (True, "his last deliberate interaction was 50 min ago")
        check("away: no sitting (45+ min since his last deliberate interaction)",
              DS.owner_away()[0] is True and "no sitting" in DS.owner_away()[1], DS.owner_away())
        cli._owner_verdict = lambda holds, evs=None: (False, "his last interaction is UNMEASURED: no source read")
        check("away: an unmeasured presence parks (the safe side)", DS.owner_away()[0] is True, DS.owner_away())

        def boom(holds, evs=None):
            raise OSError("shard unreadable")
        cli._owner_verdict = boom
        check("away: an unreadable presence parks", DS.owner_away()[0] is True, DS.owner_away())
    finally:
        cli._mode_file, cli._owner_verdict = saved[0], saved[1]
        if saved[2] is None:
            os.environ.pop("RIMFLOW_MODE", None)
        else:
            os.environ["RIMFLOW_MODE"] = saved[2]
    check("code_present: only impl present counts",
          DS.code_present({"inventory": [{"id": "a", "impl": "present"}, {"id": "b", "impl": "absent"},
                                         {"id": "c", "impl": "unknown"}]}) == ["a"])


def real_marks():
    """How often the real refusal alarms and told rows name this test's concept or item (live processes write those
    files too, so their mtimes prove nothing)."""
    out = {}
    for p in (os.path.join(RC.REAL_DIR, "alarms.json"), os.path.join(incident.REAL_OPS, "told.jsonl")):
        try:
            with open(p, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            text = ""
        out[p] = text.count("concept:Foo") + text.count("FOO_ITEM")
    return out


def main():
    CJ.delta_plan = lambda d, prior, read=None: None   # the full judge's loop; the delta re-judge is selftest_coverage_delta
    saved = (CT.coverage_problem, CT.sign, DS.exam_errors)
    CT.coverage_problem = lambda d, repo, tree: "no coverage signature"
    CT.sign = lambda d, by, repo=None, **kw: []
    DS.exam_errors = lambda ex, d, st, repo=None: []
    env = {k: os.environ.get(k) for k in ("RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR", "RM_DISPATCHER_STATE")}
    with open(VERDICTS) as f:
        rounds = json.load(f)["rounds"]
    before = real_marks()
    try:
        with tempfile.TemporaryDirectory() as base:
            ops = os.path.join(base, "ops")
            os.makedirs(ops)
            os.environ.update(RM_REFUSAL_DIR=os.path.join(base, "refusals"), RM_OPS_WATCH_DIR=ops,
                              RM_DISPATCHER_STATE=os.path.join(base, "dispatcher"))
            ek_unattended(base, rounds, ops)
            by_card_lifts(base)
            ceiling(base)
            healthy(base)
            certification(base)
            away_units()
    finally:
        CT.coverage_problem, CT.sign, DS.exam_errors = saved
        DS.owner_away = REAL_AWAY
        for k, v in env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    check("the real alarm and told files are untouched", real_marks() == before, (before, real_marks()))
    print("selftest_designer_park: %s" % ("FAIL (%d)" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
