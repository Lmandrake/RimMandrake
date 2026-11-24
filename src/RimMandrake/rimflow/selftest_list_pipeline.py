#!/usr/bin/env python3
"""selftest_list_pipeline.py: the promises of design/specs/2026-11-23-list-stage-view/boundary.md.

    python3 src/RimMandrake/rimflow/selftest_list_pipeline.py

Pure fixtures; no ledger, no network. Before list_pipeline.py existed every test was RED: no stage function.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    import list_pipeline as LP  # noqa: E402
except ImportError:
    LP = None

NOW = 1_800_000_000.0
H = 3600.0
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def need():
    assert LP is not None, "no list_pipeline.py: no one stage function"


def it(**kw):
    d = {"state": "ready", "effect": "cmd:false", "verdict": "fails", "route": None, "waits": None, "run": None,
         "stopped": False, "promise": None}
    d.update(kw)
    return d


def st(**kw):
    need()
    return LP.stage_of(it(**kw), NOW)


def t_one_stage_per_item_from_one_rule():
    need()
    shapes = [{}, {"state": None}, {"waits": "junk"}, {"route": "junk"}, {"run": 5}, {"verdict": 3}, None, "x",
              {"waits": {"until": "not a date"}}]
    for x in shapes:
        r = LP.stage_of(x if not isinstance(x, dict) else it(**x), NOW)
        assert r["stage"] in LP.STAGES and str(r["why"]).strip(), (x, r)
    # the order: a live run beats a wait; a wait beats no check; stopped beats a live run
    assert st(run="live_work", waits={"on": "X", "resumes": "X closes", "until": None})["stage"] == "work"
    assert st(effect=None, waits={"on": "X", "resumes": "X closes", "until": None})["stage"] == "waiting"
    assert st(stopped=True, run="live_work")["stage"] == "trouble"
    assert st()["stage"] == "ready" and st(effect=None, verdict=None)["stage"] == "shape"
    assert st(verdict=None)["stage"] == "verify" and st(verdict="holds")["stage"] == "verify"
    assert st(waits={"on": "d", "resumes": "d", "until": NOW - 1})["stage"] == "shape"      # a date never launches


def t_facts_that_disagree_are_a_conflict():
    assert st(state="done", verdict="fails")["stage"] == "conflict"
    assert st(state="dropped", verdict="fails")["stage"] == "closed"      # dropped: a decision not to do it
    assert st(state="done", verdict="holds")["stage"] == "closed"


def t_unmeasured_is_never_closed_or_ready():
    for v in ("unmeasured", "weird", 0):
        r = st(verdict=v)
        assert r["stage"] == "unmeasured", (v, r)
    assert st(verdict="unmeasured", run="live_work")["stage"] == "work"     # a fact the verdict does not decide


def t_a_wait_and_a_route_name_what_resumes():
    w = st(waits={"on": "X_OPEN", "resumes": "X_OPEN closes", "until": NOW + H})
    assert w["stage"] == "waiting" and w["resumes"] == "X_OPEN closes" and "X_OPEN" in w["why"], w
    r = st(effect=None, verdict=None, route={"who": "owner", "ask": "pick", "resumes": "his card answer"})
    assert r["stage"] == "review" and r["resumes"] == "his card answer", r
    c = st(route={"who": "conductor", "ask": "choose a goal", "resumes": "its ruling"})
    assert c["stage"] == "waiting" and c["resumes"] == "its ruling" and "routed to the Conductor" in c["why"], c
    j = st(route={"who": "judge", "ask": "a taste call", "resumes": "the judge's verdict"})
    assert j["stage"] == "waiting" and j["resumes"] == "the judge's verdict", j
    # the Shape stage's split: a part routed to the Conductor, with no check, is the item's route
    shaped = {"state": "ready", "effect": None, "shape": {"size": "small", "parts": [
        {"name": "p1", "effect": None, "fooled_by": None,
         "route": {"who": "conductor", "ask": "choose a goal", "resumes": "its ruling"}}]}}
    f = LP.facts(shaped, now=NOW, his=True)
    assert f["route"]["who"] == "conductor" and LP.stage_of(f, NOW)["stage"] == "waiting", f
    import list_dispatch as LD
    assert LD.row_stage({"state": "ready", "effect": None, "route": {"who": "owner", "ask": "a", "resumes": "b"}},
                        {"decision": "routed", "why": "x"}, NOW) == "review"
    assert LD.row_stage({"state": "ready", "effect": None}, {"decision": "launched", "why": "shape"}, NOW) == "shape"


def t_a_promise_rides_beside_the_stage():
    for p in ("kept", "dead"):
        r = st(state="done", verdict="holds", promise=p)
        assert r["stage"] == "closed" and r["promise"] == p, r
    assert st(promise="bogus")["promise"] is None
    f = LP.facts({"state": "done", "live": "unit=rm-x.timer", "live_broken": "the timer is dead"}, now=NOW)
    assert f["promise"] == "dead" and LP.facts({"state": "done", "live": "once: x"}, now=NOW)["promise"] == "kept"


def t_lane_row_to_verdict():
    need()
    for d in ("close", "closed_by_check", "close_refused", "would_close"):
        assert LP.lane_verdict(d) == "holds", d
    assert LP.lane_verdict("blind") == "unmeasured"
    for d in ("disabled", "pipeline_paused", "off", "adopt", "adopted", "adopt_too_heavy", "no_effect", "not_found"):
        assert LP.lane_verdict(d) is None, d
    for d in ("slots_full", "account_hold", "waits_on", "stopped", "launch", "launched", "live", "held"):
        assert LP.lane_verdict(d) == "fails", d
    assert LP.lane_verdict("slots_full", has_effect=False) is None
    item = {"state": "ready", "effect": "cmd:false", "created_at": NOW - 5 * H}
    row = {"decision": "slots_full", "why": "2 live"}
    assert LP.facts(item, lane_row=row, lane_at=NOW - 60, now=NOW)["verdict"] == "fails"
    stale = LP.facts(item, lane_row=row, lane_at=NOW - LP.LANE_STALE_S - 1, now=NOW)
    assert stale["verdict"] == "unmeasured" and "min old" in stale["note"], stale
    blind = LP.facts(item, lane_row=None, lane_at=None, lane_cause="FileNotFoundError", now=NOW)
    assert blind["verdict"] == "unmeasured" and "FileNotFoundError" in blind["note"], blind
    assert LP.stage_of(blind, NOW)["stage"] == "unmeasured"


def t_a_run_end_the_tick_has_not_read_is_verify():
    item = {"state": "ready", "effect": "cmd:false"}
    row = {"decision": "slots_full", "why": "x"}
    ended_after = [{"unit": "u1", "at": NOW - 2 * H, "ended": NOW - 60, "status": "finished"}]
    f = LP.facts(item, ended_after, lane_row=row, lane_at=NOW - 300, now=NOW)
    assert f["run"] == "ended" and f["verdict"] is None and LP.stage_of(f, NOW)["stage"] == "verify", f
    ended_before = [{"unit": "u1", "at": NOW - 2 * H, "ended": NOW - 900, "status": "finished"}]
    g = LP.facts(item, ended_before, lane_row=row, lane_at=NOW - 300, now=NOW)
    assert LP.stage_of(g, NOW)["stage"] == "ready", g
    live = [{"unit": "u2", "at": NOW - 60, "status": "running", "live_state": "running"}]
    assert LP.stage_of(LP.facts(item, live, lane_row=row, lane_at=NOW - 300, now=NOW), NOW)["stage"] == "work"


def t_a_dead_run_nobody_acted_on_is_trouble():
    item = {"state": "ready", "effect": None}
    runs = [{"unit": "u1", "at": NOW - 5 * H, "ended": NOW - 4 * H, "status": "finished"}]
    for k in ("stopped", "capped", "refused"):
        f = LP.facts(item, runs, last_event=NOW - 5 * H, end_kind=k, now=NOW)
        assert f["stopped"] and LP.stage_of(f, NOW)["stage"] == "trouble" and k in f["note"], (k, f)
    later = LP.facts(item, runs, last_event=NOW - H, end_kind="stopped", now=NOW)
    assert not later["stopped"] and LP.stage_of(later, NOW)["stage"] == "shape", later
    evs = [{"id": "I", "event": "note", "ts": "2027-01-15T07:00:00Z", "text": "DETACHED run u1 ended killed"},
           {"id": "I", "event": "note", "ts": "2027-01-15T07:00:00Z", "why": "detached run ended", "text": "x"},
           {"id": "I", "event": "file", "ts": "2027-01-01T00:00:00Z"}]
    assert LP.last_act(evs) == {"I": LP.epoch("2027-01-01T00:00:00Z")}, LP.last_act(evs)     # the finish's notes are not acts
    silent = LP.facts(item, runs, last_event=None, end_kind="said nothing", now=NOW)
    assert not silent["stopped"] and LP.stage_of(silent, NOW)["stage"] == "shape"
    lane_stop = LP.facts({"state": "ready", "effect": "cmd:false"}, lane_row={"decision": "stopped", "why": "2 runs"},
                         lane_at=NOW - 60, now=NOW)
    assert LP.stage_of(lane_stop, NOW)["stage"] == "trouble" and "2 runs" in LP.stage_of(lane_stop, NOW)["why"]


def t_six_answers_from_the_stages():
    need()
    route = {"who": "owner", "ask": "pick", "resumes": "his answer"}
    items = {"A": it(run="live_work", age_h=1), "B": it(age_h=3), "B2": it(age_h=9), "C": it(state="done", verdict="holds"),
             "D": it(waits={"on": "X", "resumes": "X closes", "until": None}, age_h=50),
             "E": it(waits={"on": "X", "resumes": "X closes", "until": None}, age_h=5),
             "F": it(stopped=True, run="ended", age_h=2), "G": it(effect=None, verdict=None, route=route, age_h=4),
             "K": it(state="done", verdict="fails", age_h=7), "S": it(effect=None, verdict=None, run="live_shape", age_h=1)}
    s = LP.six(items, NOW)
    assert [r["item"] for r in s["doing"]] == ["A", "S"], s["doing"]
    assert [r["item"] for r in s["next"]] == ["B", "B2"], s["next"]
    assert [r["item"] for r in s["closed"]] == ["C"]
    assert [r["item"] for r in s["escalated"]] == ["F", "K"] and [r["item"] for r in s["review"]] == ["G"]
    grp = s["open_why"]["waiting on X"]
    assert grp["count"] == 2 and grp["oldest"] == "D" and grp["age_h"] == 50, grp
    ready = next(v for k, v in s["open_why"].items() if k.startswith("ready"))
    assert ready["oldest"] == "B2" and ready["count"] == 2
    placed = [i for g in s["open_why"].values() for i in g["items"]] + [r["item"] for r in s["closed"]]
    assert sorted(placed) == sorted(items), placed           # each item in exactly one group, or closed
    assert sum(s["counts"].values()) == len(items)


def t_a_question_for_the_conductor_is_not_trouble():
    need()
    q = it(route={"who": "conductor", "ask": "rule it", "resumes": "its ruling"})
    s = LP.six({"Q": q, "F": it(stopped=True, run="ended")}, NOW)
    assert [r["item"] for r in s["asked"]] == ["Q"] and [r["item"] for r in s["escalated"]] == ["F"], s
    assert s["counts"] == {"waiting": 1, "trouble": 1}, s["counts"]
    # a run that stopped on a routed item is trouble all the same
    assert LP.stage_of(it(stopped=True, route=q["route"]), NOW)["stage"] == "trouble"


def t_a_block_on_an_item_names_it_with_or_without_a_kind():
    need()
    for kind in ("item", None):
        x = {"state": "ready", "effect": "cmd:false", "blocked": True, "blocked_on": "P", "blocked_kind": kind,
             "blocked_reason": "runs after P"}
        f = LP.facts(x, now=NOW, open_ids={"P"})
        assert f["waits"]["on"] == "P" and f["waits"]["resumes"] == "P closes", (kind, f["waits"])
        assert LP.facts(x, now=NOW, open_ids=set())["waits"] is None, kind      # P is closed: nothing to wait on
    assert "no event" in LP.facts({"state": "ready", "blocked": True, "blocked_reason": "no event"}, now=NOW)["waits"]["on"]


def t_the_tick_and_the_page_call_it():
    need()
    for p, word in (("src/RimMandrake/rimflow/list_dispatch.py", "stage_of("),
                    ("src/RimMandrake/Utils/maturation_nonmod.py", "LP.stage_of"),
                    ("src/RimMandrake/Utils/maturation_now.py", "stage_of(")):
        with open(os.path.join(REPO, p), encoding="utf-8") as f:
            assert word in f.read(), p
    import list_dispatch as LD
    assert LD.row_stage({"state": "ready", "effect": "cmd:false"}, {"decision": "slots_full", "why": "x"}, NOW) == "ready"
    assert LD.row_stage({"state": "ready", "effect": "cmd:false"}, {"decision": "launched"}, NOW) == "work"
    assert LD.row_stage({"state": "ready", "effect": "cmd:false"}, {"decision": "stopped", "why": "y"}, NOW) == "trouble"
    assert LD.row_stage({"state": "ready", "effect": "cmd:false"}, {"decision": "close"}, NOW) == "verify"
    assert LD.row_stage({"state": "ready", "effect": "cmd:false", "waits_on": ["Z"]}, {"decision": "waits_on"},
                        NOW) == "waiting"
    assert LD.row_stage(None, {"decision": "blind"}, NOW) == "unmeasured"
    # the tick writes the stage on each reading row (a dry tick over fake facts)
    facts = {"items": {"A": {"state": "ready", "effect": "cmd:false", "verdict": "fails", "events": 1}}, "runs": {}}
    os.environ.setdefault("RM_LIST_DISPATCH_DIR", "/tmp/selftest_list_pipeline_lane")
    rd = LD.tick(dict(LD.load_cfg(), enabled=True), False, fx={"facts": lambda st: facts, "account": lambda: (False, "x")},
                 now=NOW)
    assert rd["items"]["A"]["stage"] == "ready", rd["items"]


def t_each_stage_says_program_or_by_hand():
    need()
    assert set(LP.MOVED_BY) == set(LP.STAGES)
    for k, (who, how) in LP.MOVED_BY.items():
        assert who in ("program", "by hand") and how.strip(), k
    assert LP.MOVED_BY["shape"][0] == "program" and "--enter" in LP.MOVED_BY["shape"][1]     # step 4's Shape run
    assert LP.MOVED_BY["ready"][0] == "program" and LP.MOVED_BY["trouble"][0] == "by hand"


def t_each_limit_names_its_danger():
    need()
    with open(LP.__file__, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"((?:#.*\n)+)LANE_STALE_S = ", src)
    assert m and "Danger" in m.group(1) and "Evidence" in m.group(1), "LANE_STALE_S has no danger and evidence beside it"


def main():
    tests = [t_one_stage_per_item_from_one_rule, t_facts_that_disagree_are_a_conflict,
             t_unmeasured_is_never_closed_or_ready, t_a_wait_and_a_route_name_what_resumes,
             t_a_promise_rides_beside_the_stage, t_lane_row_to_verdict, t_a_run_end_the_tick_has_not_read_is_verify,
             t_a_dead_run_nobody_acted_on_is_trouble, t_six_answers_from_the_stages, t_a_question_for_the_conductor_is_not_trouble,
             t_a_block_on_an_item_names_it_with_or_without_a_kind, t_the_tick_and_the_page_call_it,
             t_each_stage_says_program_or_by_hand, t_each_limit_names_its_danger]
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001
            failed += 1
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, str(e)[:400]))
    print("FAILED %d of %d" % (failed, len(tests)) if failed else "ALL PASS (%d)" % len(tests))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
