#!/usr/bin/env python3
"""Selftest for the Stage 8 walk result (page design/specs/2026-11-22-walk-result/boundary.md; item
RIMMANDRAKE_ROUTE_FLOWWORKS_WALK_TWO_FINDINGS_BACK_ELEVEN_FILED). Each test builds a temp tree (a mod record at
his_walk, its journal, ledger shards with his events and the named items), calls the code and READS what it wrote.
The refusal store, ops and dispatcher folders are isolated into the temp tree. Red on the base 8a6412b492 (no
walk_result, no walk gate, no adopt_walk_road_back)."""
import json
import os
import shutil
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturation as M              # noqa: E402
import maturation_autonomy as MA    # noqa: E402

MOD, VER, ROUTE = "WalkMod", "0.1.0", "RIMMANDRAKE_ROUTE_WALKMOD_WALK_TWO_BACK_SELFTEST"
FIX_A, FIX_B, PICK, NEXT, SCENE = ("RIMMANDRAKE_FIX_WALKMOD_WHITE_FRAMES_SELFTEST", "RIMMANDRAKE_TRACE_WALKMOD_PALE_BLOCKS_SELFTEST",
                                   "RIMMANDRAKE_DESIGN_WALKMOD_TANK_LOOK_SELFTEST", "RIMMANDRAKE_DESIGN_WALKMOD_SOILS_SELFTEST",
                                   "RIMMANDRAKE_RESTAGE_WALKMOD_SIGNS_SELFTEST")
RELEASE, REFUSE = 4242000000000000001, 4242000000000000002
FAILS = []


def check(ok, what, got=None):
    print("%s %s%s" % ("PASS" if ok else "FAIL", what, "" if got is None else "  [read: %s]" % (str(got)[:300],)))
    if not ok:
        FAILS.append(what)


def shard(root, seat):
    return os.path.join(root, "infrastructure", "state", "ledger", "events", "%s.jsonl" % seat)


def append(root, seat, ev):
    p = shard(root, seat)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a") as f:
        f.write(json.dumps(ev) + "\n")


def fixture(tmp, stage="his_walk"):
    root = os.path.join(tmp, "repo")
    if os.path.isdir(root):
        shutil.rmtree(root)
    d = os.path.join(root, "design", "concepts", MOD)
    os.makedirs(os.path.join(d, "version", "walk_brief"))
    with open(os.path.join(d, "version", "VERSION.json"), "w") as f:
        json.dump({"version": VER}, f)
    with open(os.path.join(d, "version", "stage_record.json"), "w") as f:
        json.dump({"mod": MOD, "version": VER, "stage": stage, "pre_human_arrivals": 2, "moves": [],
                   "cycles": {"visit": 0, "total": 0}}, f, indent=1)
    with open(os.path.join(d, "journal.md"), "w") as f:
        f.write("# WalkMod journal\n\n- **Stage now:** his walk.\n- **Waiting on:** his walk.\n")
    body = "".join("## %s\nselftest text under %s\n\n" % (h, h) for h in M.WALK_BRIEF_HEADINGS)
    for n in (1, 2, 3):
        with open(os.path.join(d, "version", "walk_brief", "arrival_%d.md" % n), "w") as f:
            f.write("written_by: fresh-reader-%d\n\n%s" % (n, body))
    with open(os.path.join(d, "version", "test_table.json"), "w") as f:
        json.dump({"version": VER, "tests": {}}, f)
    append(root, "OWNER", {"seat": "OWNER", "event": "file", "id": ROUTE, "tsn": RELEASE, "title": "route the walk",
                           "ownerSaid": "Ok, release my WalkMod walkthrough."})
    append(root, "OWNER", {"seat": "OWNER", "event": "note", "id": ROUTE, "tsn": REFUSE,
                           "ownerSaid": "It does not pass yet."})
    for i, n in ((FIX_A, None), (FIX_B, "game-up"), (PICK, None), (NEXT, None), (SCENE, None)):
        ev = {"seat": "OWNER", "event": "file", "id": i, "title": "selftest %s" % i, "tsn": 4242000000000001000}
        if n:
            ev["needs"] = n
        append(root, "OWNER", ev)
    return root


def lists(**kw):
    out = {"fix": [FIX_A, FIX_B], "pick": [PICK], "scene": [SCENE], "next_version": [NEXT],
           "groups": [[FIX_A, FIX_B]], "passes": ["pit depth reads well"]}
    out.update(kw)
    return out


def run(root, **kw):
    a = dict(to="in_game", by="BENCH", why="selftest walk two not passed", owner="OWNER:%d" % RELEASE,
             item=ROUTE, **lists())
    a.update(kw)
    return M.walk_result(root, MOD, **a)


def wpath(root, n=2, ext="json"):
    return os.path.join(root, "design", "concepts", MOD, M.WALK_BRIEF_DIR, "walk_%d_result.%s" % (n, ext))


def t_walk_result_records_not_passed(tmp):
    root = fixture(tmp)
    r = run(root)
    rec = M.load(root, MOD)
    got = json.load(open(wpath(root))) if os.path.isfile(wpath(root)) else {}
    mv = (rec.get("moves") or [{}])[-1]
    check(r.get("ok") and rec["stage"] == "in_game" and got.get("verdict") == "not_passed"
          and got.get("fix") == [FIX_A, FIX_B] and got.get("pick") == [PICK] and got.get("next_version") == [NEXT]
          and got.get("owner_said", {}).get("tsn") == str(RELEASE) and os.path.isfile(wpath(root, ext="md"))
          and mv.get("from") == "his_walk" and mv.get("confirmed", {}).get("walk_result") == M.rel(
              MOD, "%s/walk_2_result.json" % M.WALK_BRIEF_DIR),
          "walk-result-records-not-passed", {"ok": r.get("ok"), "stage": rec["stage"], "file": got, "move": mv,
                                             "why": r.get("why")})


def t_walk_result_refuses_off_stage(tmp):
    root = fixture(tmp, stage="in_game")
    r = run(root)
    check(not r.get("ok") and not os.path.exists(wpath(root)) and M.load(root, MOD)["stage"] == "in_game"
          and "his_walk" in str(r.get("why")), "walk-result-refuses-off-stage", r.get("why"))


def t_walk_result_refuses_unknown_item(tmp):
    root = fixture(tmp)
    r = run(root, fix=[FIX_A, "RIMMANDRAKE_NEVER_FILED_WALKMOD_SELFTEST"], groups=[])
    check(not r.get("ok") and not os.path.exists(wpath(root)) and M.load(root, MOD)["stage"] == "his_walk"
          and "RIMMANDRAKE_NEVER_FILED_WALKMOD_SELFTEST" in str(r.get("why")), "walk-result-refuses-unknown-item",
          r.get("why"))


def t_walk_result_refuses_second_write(tmp):
    root = fixture(tmp)
    with open(wpath(root), "w") as f:
        f.write('{"verdict": "not_passed"}\n')
    r = run(root)
    check(not r.get("ok") and M.load(root, MOD)["stage"] == "his_walk"
          and open(wpath(root)).read() == '{"verdict": "not_passed"}\n', "walk-result-refuses-second-write",
          r.get("why"))


def t_road_back_takes_his_refusing_words(tmp):
    root = fixture(tmp)
    r = run(root, owner="OWNER:%d" % REFUSE)
    still = M.evaluate(fixture(tmp), MOD, "passed", by="BENCH", why="x", owner="OWNER:%d" % REFUSE)
    refused = [x["clause"] for x in still["verdict"]["refusals"]]
    check(r.get("ok") and "owner_said" in refused, "road-back-takes-his-refusing-words",
          {"walk": r.get("why") or r.get("ok"), "pass_refused": refused})


def t_road_back_takes_conductor_decision(tmp):
    root = fixture(tmp)
    r = run(root, owner=None, conductor="send it back before his walk: checks owed")
    none = run(fixture(tmp), owner=None)
    still = M.evaluate(fixture(tmp), MOD, "passed", by="BENCH", why="x", conductor="pass it")
    refused = [x["clause"] for x in still["verdict"]["refusals"]]
    check(r.get("ok") and not none.get("ok") and "owner_said" in refused, "road-back-takes-conductor-decision",
          {"with": r.get("ok"), "without": none.get("why"), "pass_refused": refused})


def _to_walk(root):
    rec = M.load(root, MOD)
    rec["stage"], rec["pre_human_arrivals"] = "pre_human", 3
    M.write_text(root, MOD, M.RECORD, M.dump(rec))
    return M.evaluate(root, MOD, "his_walk", by="BENCH", why="x")


def t_walk_gate_holds_on_open_item(tmp):
    root = fixture(tmp)
    run(root)
    e1 = _to_walk(root)
    r1 = [x for x in e1["verdict"]["refusals"] if x["clause"] == "walk_items_closed"]
    obs = str(r1[0].get("observed")) if r1 else ""
    for i in (FIX_A, FIX_B, PICK):
        append(root, "BENCH", {"seat": "BENCH", "event": "close", "id": i, "tsn": 4242000000000002000})
    e2 = M.evaluate(root, MOD, "his_walk", by="BENCH", why="x")
    r2 = [x for x in e2["verdict"]["refusals"] if x["clause"] == "walk_items_closed"]
    append(root, "BENCH", {"seat": "BENCH", "event": "drop", "id": SCENE, "tsn": 4242000000000002001})
    e3 = M.evaluate(root, MOD, "his_walk", by="BENCH", why="x")
    r3 = [x for x in e3["verdict"]["refusals"] if x["clause"] == "walk_items_closed"]
    check(r1 and all(i in obs for i in (FIX_A, FIX_B, PICK, SCENE)) and NEXT not in obs and r2 and SCENE in str(
        r2[0].get("observed")) and not r3 and e3["ok"], "walk-gate-holds-on-open-item",
          {"open": obs, "after_three_closed": [x.get("observed") for x in r2], "after_all": e3["ok"]})


def t_walk_gate_unreadable_result_refuses(tmp):
    root = fixture(tmp)
    run(root)
    with open(wpath(root), "w") as f:
        f.write("{not json")
    e = _to_walk(root)
    r = [x for x in e["verdict"]["refusals"] if x["clause"] == "walk_items_closed"]
    check(r and "walk_2_result.json" in str(r[0].get("observed")), "walk-gate-unreadable-result-refuses",
          r[0].get("observed") if r else e["verdict"]["passed"])


def t_tick_adopts_walk_road_back(tmp):
    root = fixture(tmp)
    run(root)
    s = {"road_back": {"caused_by": "RIMMANDRAKE_CONFIRM_WALKMOD_VISIT_SEVEN_OLD", "at": 1.0, "from": "in_game"}}
    MA.adopt_walk_road_back(root, MOD, s)
    rb = s.get("road_back") or {}
    newer = {"road_back": {"caused_by": "RIMMANDRAKE_LATER_STEWARD_WALKMOD", "at": 9e18, "from": "in_game"}}
    MA.adopt_walk_road_back(root, MOD, newer)
    check(rb.get("caused_by") == ROUTE and rb.get("from") == "his_walk" and sorted(rb.get("cited") or []) == sorted(
        [FIX_A, FIX_B, SCENE]) and PICK not in (rb.get("cited") or []) and NEXT not in (rb.get("cited") or [])
          and rb.get("walk_result", "").endswith("walk_2_result.json")
          and newer["road_back"]["caused_by"] == "RIMMANDRAKE_LATER_STEWARD_WALKMOD",
          "tick-adopts-walk-road-back", {"adopted": rb, "newer_kept": newer["road_back"]["caused_by"]})


def t_tick_adopts_once(tmp):
    root = fixture(tmp)
    run(root)
    s = {}
    MA.adopt_walk_road_back(root, MOD, s)
    first = json.dumps(s, sort_keys=True)
    MA.adopt_walk_road_back(root, MOD, s)
    same = json.dumps(s, sort_keys=True) == first
    s.pop("road_back", None)            # the tick pops it when every item closed
    MA.adopt_walk_road_back(root, MOD, s)
    check(same and "road_back" not in s and s.get("walk_road_backs"), "tick-adopts-once",
          {"same": same, "after_pop": s})


def t_walk_fixer_never_drops_his_finding(tmp):
    b = MA.fixer_brief(FIX_A, MOD, 5, "walk", walk_result="design/concepts/%s/version/walk_brief/walk_2_result.json"
                       % MOD, group=[FIX_A, FIX_B])
    check("his finding" in b and "not worth the touch" in b and "never" in b.lower() and FIX_B in b
          and "walk_2_result.json" in b, "walk-fixer-never-drops-his-finding", b[:400])


def t_tick_runs_no_fixer_on_pick_or_next(tmp):
    # the route run files every ticket of the walk with caused_by the route item: pick, next-version and another mod's
    # tickets too (FlowWorks walk 3, 2026-11-25). The road back reads caused_by, so only the cited ids may come back.
    root = fixture(tmp)
    other = "RIMMANDRAKE_PROVE_OTHERMOD_CHECK_SELFTEST"
    for i in (PICK, NEXT, other):
        append(root, "BENCH", {"seat": "BENCH", "event": "file", "id": i + "_CAUSED", "title": "selftest caused %s" % i,
                               "tsn": 4242000000000002000, "caused_by": ROUTE})
    run(root)
    s = {}
    MA.adopt_walk_road_back(root, MOD, s)
    rb = s.get("road_back") or {}
    got = MA.road_back_open(s, rb, lambda ids, **kw: M.ledger_items_caused_by(root, ids, **kw))
    ids = sorted(x["id"] for x in got or [])
    check(got is not None and ids == sorted([FIX_A, FIX_B, SCENE]), "tick-runs-no-fixer-on-pick-or-next", ids)


def t_tick_books_a_live_run_on_a_cited_item(tmp):
    # a cited item that already has a live run (the Conductor launched one before the walk result): the tick books that
    # run as the item's one fixer run and starts no second one, then or after it ends
    items = [{"id": FIX_A, "needs": "offline"}, {"id": FIX_B, "needs": "offline"}]
    rb = {"caused_by": ROUTE, "at": 1.0, "from": "his_walk", "cited": [FIX_A, FIX_B], "walk_result": "w.json"}
    runs = {FIX_A: [("rm-detached-bench-fix-a-1", "running")]}
    s, row = {"road_back": dict(rb)}, {"mod": MOD, "stage": "offline_build"}
    MA._road_back(s, row, lambda ids, **kw: list(items), now=5.0, runs_of=lambda i: runs.get(i, []))
    first = (row.get("fix_item"), sorted((s.get("fixers") or {}).keys()))
    s2, row2 = {"road_back": dict(rb)}, {"mod": MOD, "stage": "offline_build"}
    MA._road_back(s2, row2, lambda ids, **kw: [items[0]], now=5.0, runs_of=lambda i: runs.get(i, []))
    runs[FIX_A] = [("rm-detached-bench-fix-a-1", "finished")]
    row3 = {"mod": MOD, "stage": "offline_build"}
    MA._road_back(s2, row3, lambda ids, **kw: [items[0]], now=9.0, runs_of=lambda i: runs.get(i, []))
    check(first == (FIX_B, [FIX_A]) and row2.get("decision") == "live" and "rm-detached-bench-fix-a-1" in str(
        row2.get("waits_on")) and row3.get("aut") != "fixer", "tick-books-a-live-run-on-a-cited-item",
          {"first": first, "live": (row2.get("decision"), row2.get("waits_on")), "after": row3.get("decision")})


def main():
    TESTS = [t_walk_result_records_not_passed, t_walk_result_refuses_off_stage, t_walk_result_refuses_unknown_item,
             t_walk_result_refuses_second_write, t_road_back_takes_his_refusing_words, t_road_back_takes_conductor_decision,
             t_walk_gate_holds_on_open_item, t_walk_gate_unreadable_result_refuses, t_tick_adopts_walk_road_back,
             t_tick_adopts_once, t_walk_fixer_never_drops_his_finding, t_tick_runs_no_fixer_on_pick_or_next,
             t_tick_books_a_live_run_on_a_cited_item]
    tmp = tempfile.mkdtemp(prefix="walk_result_")
    saved = {k: os.environ.get(k) for k in ("RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR", "RM_DISPATCHER_STATE",
                                            "RM_JUDGE_CALIBRATION")}
    os.environ.update(RM_REFUSAL_DIR=os.path.join(tmp, "_refusals"), RM_OPS_WATCH_DIR=os.path.join(tmp, "_ops"),
                      RM_DISPATCHER_STATE=os.path.join(tmp, "_disp"),
                      RM_JUDGE_CALIBRATION=os.path.join(tmp, "_cal.json"))
    for k in ("RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR", "RM_DISPATCHER_STATE"):
        os.makedirs(os.environ[k], exist_ok=True)
    try:
        for t in TESTS:
            try:
                t(tmp)
            except Exception:  # noqa: BLE001  a crash is that test's FAIL, the others still run
                check(False, t.__name__[2:].replace("_", "-"), traceback.format_exc().strip().splitlines()[-1])
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d of %d promises pass" % (len(TESTS) - len(FAILS), len(TESTS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
