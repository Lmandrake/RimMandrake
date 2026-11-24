#!/usr/bin/env python3
"""selftest_steve_visit_feed.py - an open in-game visit's testq checks go to the SteveDesktop lane ahead of filler
(RIMMANDRAKE_ROUTE_VISIT_TESTQ_CHECKS_AHEAD_OF_FILLER; page design/specs/2026-11-22-steve-idle-takeable/boundary.md).

The ticket's acceptance test: a dispatch reading naming one waiting check with its chain, the lane idle or on a filler
job on another mod, one testq tick's feed step (testq.visit_feed_step), and then ops_watch.c_steve_takeable must read
state `busy`. Before the fix the tick had no such step and the reading stayed `waiting` (live: 633 min, 2026-11-23).
The fixtures are selftest_steve_idle_takeable.py's (temp dirs; nothing live is read). modcheck's preview is stubbed
(the fixture's chains are not real chains) and so is the is-it-on-origin/main check; the rest of `testq.py submit`
runs as it is: the owner's hold, the job schema, the duplicate check, the pending record."""
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import selftest_steve_idle_takeable as F  # noqa: E402  (sets TESTQ_QUEUE and the other fixture env first)
sys.path.insert(0, str(HERE / "testq"))
import testq as T  # noqa: E402
import coverage as C  # noqa: E402

FAILS = []
NOW = F.NOW


def check(cond, msg):
    print("%s %s" % ("ok  " if cond else "FAIL", msg))
    if not cond:
        FAILS.append(msg)


_reset = F.reset


def reset():
    """selftest_steve_idle_takeable's clean lane, with the control store made (the owner-hold list reads from it)."""
    _reset()
    sys.path.insert(0, str(HERE.parent / "rimflow"))
    import control
    control.init(os.environ["RM_CONTROL_DB"])


F.reset = reset
T.preview = lambda mod, sel: {"refusal": None, "rows": None, "drivers": [], "chains": list(sel.get("chains") or []),
                              "driver_chains": None, "floor_uncovered": None}
T.published = lambda sha: True


def step():
    """One tick's feed step; None (and nothing done) where the tick has no such step."""
    fn = getattr(T, "visit_feed_step", None)
    if fn is None:
        print("     testq has no visit_feed_step: the tick does nothing for a waiting visit check")
        return None
    out = fn(now=NOW)
    print("     feed -> %s" % json.dumps(out)[:300])
    return out


def pending():
    return [T.read_json(str(p)) for p in sorted((F.TMP / "testq" / "pending").glob("*.json"))]


def visit_jobs():
    return [j for j in pending() if j and j.get("requested_by") != "BENCH.filler"]


def t_a_waiting_check_is_queued_ahead_of_filler():
    # the ticket's case: one waiting check (p0, chain pc0) on Pyrelands visit 6, the lane idle
    F.reset()
    F.dispatch(F.one())
    step()
    p = F.read("idle lane, one check waits, after one tick")
    check((p.get("x") or {}).get("state") == "busy",
          "a-waiting-check-is-queued-ahead-of-filler: the lane reads busy after one tick (%s %s)"
          % (p.get("m"), (p.get("x") or {}).get("state")))
    js = visit_jobs()
    j = js[0] if js else {}
    check(len(js) == 1 and j.get("mod") == "Pyrelands" and "pc0" in (j.get("selector") or {}).get("chains", [])
          and j.get("lane") == "stevedesktop" and j.get("requested_by") == "BENCH.visit"
          and j.get("priority", 0) > 20 and not j.get("owner_gate"),
          "a-waiting-check-is-queued-ahead-of-filler: one ready job on Pyrelands pc0, by BENCH.visit, above the "
          "filler's priority (%s)" % {k: j.get(k) for k in ("mod", "selector", "requested_by", "priority", "lane")})
    check(T.fill_plan("CrackedLands", 4, 50, now=NOW)["verdict"] == "busy",
          "a-waiting-check-is-queued-ahead-of-filler: the filler then queues nothing (fill_plan busy)")
    # a filler job on another mod runs: the visit job still queues behind it, ready, and the lane reads busy
    F.reset()
    F.dispatch(F.one())
    F.running(F.job("J-fill", "CrackedLands", ["claim_crew"], by="BENCH.filler"))
    step()
    p = F.read("filler on CrackedLands, one check waits, after one tick")
    check((p.get("x") or {}).get("state") == "busy" and len(visit_jobs()) == 1,
          "a-waiting-check-is-queued-ahead-of-filler: beside a filler job on another mod (%s, %d queued)"
          % ((p.get("x") or {}).get("state"), len(visit_jobs())))
    # a second tick queues no second job while the first waits or runs, even for another waiting mod
    F.reset()
    F.dispatch(F.today())
    step()
    again = step() or {}
    check(len(visit_jobs()) == 1 and again.get("state") == "busy",
          "a-waiting-check-is-queued-ahead-of-filler: one visit job at a time, the next tick reads busy (%d, %s)"
          % (len(visit_jobs()), again.get("state")))


def t_a_visit_opening_with_an_offset_reads():
    # the live form (maturation writes the opening in local time with its offset): 1 h ago as -08:00
    F.reset()
    b = F.one()
    b["Pyrelands"]["opened"] = time.strftime("%Y-%m-%dT%H:%M:%S-08:00", time.gmtime(NOW - 3600 - 8 * 3600))
    F.dispatch(b)
    F.done(F.job("J-early", "Pyrelands", ["pc0"]), "DONE", NOW - 2 * 3600)      # before that opening: drains nothing
    out = step() or {}
    check(out.get("state") == "queued" and len(visit_jobs()) == 1,
          "a-visit-opening-with-an-offset-reads: %s queues its waiting check (%s)" % (b["Pyrelands"]["opened"],
                                                                                    out.get("state")))
    F.reset()
    b = F.one()
    b["Pyrelands"]["opened"] = "last tuesday"
    F.dispatch(b)
    out = step() or {}
    check(not visit_jobs() and out.get("state") == "unmeasured" and "Pyrelands" in str(out.get("why")),
          "a-visit-opening-with-an-offset-reads: an unreadable opening is named, never quiet (%s)" % out.get("state"))


def t_the_owners_hold_and_gate_still_stop_a_check():
    F.reset()
    b = F.one()
    b["Pyrelands"]["held"] = True
    F.dispatch(b)
    step()
    check(not visit_jobs(), "the-owners-hold-and-gate-still-stop-a-check: a held mod gets no job (%d)" % len(visit_jobs()))
    F.reset()
    F.dispatch(F.one())
    F.wjson(os.environ["RM_OWNER_HOLD_FILE"], {"holds": [{"mod": "Pyrelands", "date": "2026-11-22", "said": "hold"}]})
    step()
    check(not visit_jobs(), "the-owners-hold-and-gate-still-stop-a-check: the live hold list refuses it too (%d)"
          % len(visit_jobs()))
    F.reset()
    F.dispatch(F.one())
    F.pending(F.job("J-gate", "Pyrelands", ["pc0"], owner_gate="his look first"))
    step()
    check(not visit_jobs()[1:] and all(j.get("owner_gate") for j in visit_jobs()),
          "the-owners-hold-and-gate-still-stop-a-check: a chain whose job waits on his gate is not sent again")
    F.reset()
    b = F.one()
    b["Pyrelands"]["blocked"] = ["a Conductor hold stands on stage 6"]
    F.dispatch(b)
    step()
    check(not visit_jobs(), "the-owners-hold-and-gate-still-stop-a-check: a blocked visit gets no job")


def t_nothing_waits_nothing_is_sent():
    F.reset()
    F.dispatch(F.one())
    F.done(F.job("J-a", "Pyrelands", ["pc0"]), "DONE", NOW - 20 * 60)
    step()
    check(not visit_jobs(), "nothing-waits-nothing-is-sent: a chain DONE since the opening is drained")
    F.reset()
    F.dispatch(F.one())
    F.done(F.job("J-early", "Pyrelands", ["pc0"]), "DONE", NOW - 2 * 3600)      # before the opening (1 h ago)
    step()
    check(len(visit_jobs()) == 1, "nothing-waits-nothing-is-sent: a run before the opening drains nothing")
    # two refusals of the job itself since the opening: not sent a third time (the filler brake's two-in-a-row evidence)
    F.reset()
    F.dispatch(F.one())
    for jid, at in (("J-i1", NOW - 40 * 60), ("J-i2", NOW - 20 * 60)):
        F.done(F.job(jid, "Pyrelands", ["pc0"], by="BENCH.visit"), "INVALID", at)
        p = F.TMP / "testq" / "done" / (jid + ".json")
        rec = T.read_json(str(p))
        rec["result"]["cause"] = "BLOCKED_SELECTION"
        F.wjson(p, rec)
    out = step() or {}
    check(not visit_jobs() and "pc0" in json.dumps(out.get("spent") or {}),
          "nothing-waits-nothing-is-sent: a chain that failed twice since the opening is named, not sent (%s)"
          % out.get("spent"))
    # a DONE run whose rows for the chain were all UNMEASURED (no site) drains nothing, and twice stops it
    F.reset()
    F.dispatch(F.one())
    p = F.TMP / "testq" / "done" / "J-dry.json"
    F.wjson(p, {"job": F.job("J-dry", "Pyrelands", ["pc0"]), "result": {
        "outcome": "DONE", "started": F.iso(NOW - 900), "finished": F.iso(NOW - 600),
        "rows": [{"chain": "pc0", "row": "<chain setup>", "verdict": "UNMEASURED", "detail": "UNMEASURED SITE"}]}})
    step()
    check(len(visit_jobs()) == 1, "nothing-waits-nothing-is-sent: a DONE run that measured nothing drains nothing (%d)"
          % len(visit_jobs()))
    F.reset()
    F.dispatch(F.one())
    for k in (1, 2):
        F.wjson(F.TMP / "testq" / "done" / ("J-dry%d.json" % k), {"job": F.job("J-dry%d" % k, "Pyrelands", ["pc0"]),
                "result": {"outcome": "DONE", "started": F.iso(NOW - 900 * k), "finished": F.iso(NOW - 600 * k),
                           "rows": [{"chain": "pc0", "row": "x", "verdict": "UNMEASURED"}]}})
    out = step() or {}
    check(not visit_jobs() and out.get("state") == "backoff" and not (out.get("spent") or {}).get("Pyrelands"),
          "nothing-waits-nothing-is-sent: two DONE runs that measured nothing hold it back, spent nothing (%s %s)"
          % (out.get("state"), out.get("spent")))
    F.reset()
    F.dispatch(F.one())
    F.wjson(F.TMP / "testq" / "done" / "J-meas.json", {"job": F.job("J-meas", "Pyrelands", ["pc0"]), "result": {
        "outcome": "DONE", "started": F.iso(NOW - 900), "finished": F.iso(NOW - 600),
        "rows": [{"chain": "pc0", "row": "x", "verdict": "FAIL"}, {"chain": "pc0", "row": "y", "verdict": "UNMEASURED"}]}})
    step()
    check(not visit_jobs(), "nothing-waits-nothing-is-sent: a DONE run with a FAIL row drains the check")
    # the stop file and a pause stop it
    F.reset()
    F.dispatch(F.one())
    (F.TMP / "testq" / "fill.stop").write_text("stop")
    step()
    check(not visit_jobs(), "nothing-waits-nothing-is-sent: fill.stop stops the feed")
    F.reset()
    F.dispatch(F.one())
    T.S.dump({"since": F.iso(NOW - 60), "reason": "test"}, str(F.TMP / "testq" / "paused.json"))
    step()
    check(not visit_jobs(), "nothing-waits-nothing-is-sent: a paused lane gets no job")


def _refused(jid, cause, fin, chains=("pc0",)):
    """A done record the worker refused before the chain ran (live: Steve2's `Steve2 is running; it rewrites Prefs.xml
    on exit`, REFUSED LOAD, 46 of 53 Steve2 jobs 2026-11-23)."""
    p = F.TMP / "testq" / "done" / (jid + ".json")
    F.wjson(p, {"job": F.job(jid, "Pyrelands", list(chains), by="BENCH.visit"), "host": "stevedesktop.b",
                "result": {"outcome": "REFUSED", "cause": cause, "note": "Steve2 is running; it rewrites Prefs.xml",
                           "started": F.iso(fin - 60), "finished": F.iso(fin)}})
    os.utime(p, (fin, fin))


def t_a_lane_refusal_does_not_spend_a_check():
    # live 2026-11-23: four FlowWorks visit jobs refused LOAD on Steve2 at 15:57-16:03Z spent six chains; the feed
    # read `quiet` for six hours with the checks never run. A refusal before the chain ran measured nothing about it.
    for cause in sorted(T.ARCH_BOUNCE | {"SYNC"}):
        F.reset()
        F.dispatch(F.one())
        _refused("J-r1", cause, NOW - 50 * 60)
        _refused("J-r2", cause, NOW - 40 * 60)
        out = step() or {}
        js = visit_jobs()
        check(out.get("state") == "queued" and len(js) == 1 and "pc0" in js[0]["selector"]["chains"]
              and "pc0" not in json.dumps(out.get("spent") or {}),
              "a-lane-refusal-does-not-spend-a-check: two REFUSED %s runs since the opening still queue pc0 (%s, %s)"
              % (cause, out.get("state"), out.get("spent")))
    # just refused: held back a while (not resent into the same refusal every tick), and named, never `quiet`
    F.reset()
    F.dispatch(F.one())
    _refused("J-r3", "LOAD", NOW - 60)
    out = step() or {}
    check(not visit_jobs() and out.get("state") == "backoff" and "pc0" in json.dumps(out.get("backoff") or {}),
          "a-lane-refusal-does-not-spend-a-check: a check refused 1 min ago waits out its backoff, named (%s %s)"
          % (out.get("state"), out.get("backoff")))
    F.reset()
    F.dispatch(F.one())
    _refused("J-r4", "LOAD", NOW - 60 - __import__("visit_feed").BOUNCE_BACKOFF_S)
    out = step() or {}
    check(out.get("state") == "queued" and len(visit_jobs()) == 1,
          "a-lane-refusal-does-not-spend-a-check: past the backoff it is sent again (%s)" % out.get("state"))
    # a refusal for a cause about the mod (not the lane) still counts: two stop it
    F.reset()
    F.dispatch(F.one())
    _refused("J-r5", "PREFLIGHT", NOW - 50 * 60)
    _refused("J-r6", "PREFLIGHT", NOW - 40 * 60)
    out = step() or {}
    check(not visit_jobs() and (out.get("spent") or {}).get("Pyrelands") == {"pc0": 2},
          "a-lane-refusal-does-not-spend-a-check: two REFUSED PREFLIGHT runs still stop it (%s)" % out.get("spent"))


def _ran(jid, outcome, cause, at, rows=None, cancelled=False):
    F.done(F.job(jid, "Pyrelands", ["pc0"], by="BENCH.visit"), outcome, at)
    p = F.TMP / "testq" / "done" / (jid + ".json")
    rec = T.read_json(str(p))
    rec["result"].update(cause=cause, rows=rows or [])
    if cancelled:
        rec["cancelled"] = True
    p.write_text(json.dumps(rec))


def t_visit_feed_spends_a_chain_only_on_its_own_fault():
    """One failure classifier: an outcome that is not the chain's own spends nothing, and is named."""
    tag = "visit-feed-spends-a-chain-only-on-its-own-fault"
    dry = [{"chain": "pc0", "row": "r", "verdict": "UNMEASURED"}]
    for label, kw, word in (("two INTERRUPTED/CRASH", dict(outcome="INTERRUPTED", cause="CRASH"), "KILLED"),
                            ("two INVALID/GAME_DIED", dict(outcome="INVALID", cause="GAME_DIED"), "UNRESOLVED"),
                            ("two INVALID/CANARY", dict(outcome="INVALID", cause="CANARY"), "APPARATUS FAULT"),
                            ("two DONE, every row UNMEASURED", dict(outcome="DONE", cause=None, rows=dry),
                             "COULD NOT LOOK")):
        F.reset()
        F.dispatch({"Pyrelands": F.entry(6, NOW - 6 * 3600, {"p0": ["pc0"]})})
        _ran("J-x1", at=NOW - 5 * 3600, **kw)
        _ran("J-x2", at=NOW - 4 * 3600, **kw)
        out = step() or {}
        js = visit_jobs()
        check(out.get("state") == "queued" and len(js) == 1 and "pc0" in js[0]["selector"]["chains"]
              and "pc0" not in json.dumps(out.get("spent") or {})
              and ((out.get("faults") or {}).get("Pyrelands") or {}).get("pc0") == {word: 2},
              "%s: %s spend nothing, named %s (%s, spent %s, faults %s)"
              % (tag, label, word, out.get("state"), out.get("spent"), out.get("faults")))
    # each such run in a row doubles the wait, so a chain the lane cannot measure never spins it
    F.reset()
    F.dispatch({"Pyrelands": F.entry(6, NOW - 6 * 3600, {"p0": ["pc0"]})})
    for k, at in enumerate((4 * 3600, 3 * 3600, 25 * 60)):
        _ran("J-y%d" % k, "INTERRUPTED", "CRASH", NOW - at)
    out = step() or {}
    check(not visit_jobs() and out.get("state") == "backoff" and "pc0" in json.dumps(out.get("backoff") or {})
          and (out.get("faults") or {}).get("Pyrelands", {}).get("pc0") == {"KILLED": 3},
          "%s: three in a row wait 40 min, named, never `quiet` (%s %s)" % (tag, out.get("state"), out.get("backoff")))
    F.reset()
    F.dispatch({"Pyrelands": F.entry(6, NOW - 6 * 3600, {"p0": ["pc0"]})})
    for k in range(9):
        _ran("J-z%d" % k, "INTERRUPTED", "CRASH", NOW - 5 * 3600 + k * 600)
    _ran("J-z9", "INTERRUPTED", "CRASH", NOW - 2 * 3600 - 60)
    out = step() or {}
    check(out.get("state") == "queued", "%s: the wait is never longer than FAULT_BACKOFF_MAX_S (%s)" % (tag, out.get("state")))
    # an outcome nobody can class spends nothing and is named
    F.reset()
    F.dispatch({"Pyrelands": F.entry(6, NOW - 6 * 3600, {"p0": ["pc0"]})})
    _ran("J-w1", "EXPLODED", None, NOW - 5 * 3600)
    _ran("J-w2", "EXPLODED", None, NOW - 4 * 3600)
    out = step() or {}
    check(out.get("state") == "queued" and (out.get("faults") or {}).get("Pyrelands", {}).get("pc0") == {"UNCLASSED": 2},
          "%s: an unknown outcome spends nothing and is named (%s %s)" % (tag, out.get("state"), out.get("faults")))


def t_could_not_look_sends_nothing():
    for label, setup in (("no dispatch reading", lambda: None),
                         ("a stale reading", lambda: F.dispatch(F.one(), age=3600)),
                         ("no ingame_testq block", lambda: F.dispatch(F.one(), drop=True))):
        F.reset()
        setup()
        out = step() or {}
        check(not visit_jobs() and out.get("state") == "unmeasured" and out.get("why"),
              "could-not-look-sends-nothing: %s -> no job, the cause named (%s)" % (label, out.get("why")))
    # a temp queue that names no dispatch reading never reads the live one
    F.reset()
    F.dispatch(F.one())
    saved = os.environ.pop("RM_MATURATION_DISPATCH_DIR")
    try:
        out = step() or {}
    finally:
        os.environ["RM_MATURATION_DISPATCH_DIR"] = saved
    check(not visit_jobs() and out.get("state") == "unmeasured" and "not the live one" in str(out.get("why")),
          "could-not-look-sends-nothing: a test queue with no dispatch reading of its own reads none (%s)"
          % out.get("why"))


def t_mods_take_turns():
    F.reset()
    b = F.today()
    b["FlowWorks"]["opened"] = F.iso(NOW - 3600)      # Pyrelands opened 6 h ago, FlowWorks 1 h ago
    F.dispatch(b)
    step()
    first = [j["mod"] for j in visit_jobs()]
    js = visit_jobs()
    for j in js:        # the first job ran DONE on other chains: nothing of it drains, the turn passes
        os.remove(str(F.TMP / "testq" / "pending" / (j["id"] + ".json")))
        F.done(dict(j), "DONE", NOW - 30)
    step()
    second = [j["mod"] for j in visit_jobs()]
    check(first == ["Pyrelands"] and second == ["FlowWorks"],
          "mods-take-turns: the earliest-opened visit first, then the mod fed longest ago (%s, %s)" % (first, second))


def t_filler_prefers_advancing_mods():
    saved = os.environ.get("TESTQ_FILL_MODS")
    os.environ["TESTQ_FILL_MODS"] = "Abyss Pyrelands Cuisine FlowWorks Sarlacc"
    old = getattr(C, "advancing", None)
    try:
        C.advancing = lambda: ["Pyrelands", "FlowWorks", "GimmeSomeSlack"]
        got = C.fill_order(C.fill_mods(), "Cuisine")
        check(got[:2] == ["Pyrelands", "FlowWorks"] and sorted(got) == sorted(os.environ["TESTQ_FILL_MODS"].split()),
              "filler-prefers-advancing-mods: the advancing mods walk first, every mod still walked (%s)" % got)
        got = C.fill_order(C.fill_mods(), "Pyrelands")
        check(got[:2] == ["FlowWorks", "Pyrelands"],
              "filler-prefers-advancing-mods: the advancing mods take turns among themselves (%s)" % got)
    finally:
        if old is not None:
            C.advancing = old
        if saved is None:
            os.environ.pop("TESTQ_FILL_MODS", None)
        else:
            os.environ["TESTQ_FILL_MODS"] = saved


def t_site_saves_ship_when_the_registry_changes():
    calls = []

    def run_ok():
        calls.append("ok")
        return 0, "same site calm"

    def run_bad():
        calls.append("bad")
        return 1, "UNMEASURED site pyrelands"
    stage = F.TMP / "testq" / T.SITE_STAGE
    if stage.exists():
        stage.unlink()
    a = T.site_stage_step(now=NOW, run=run_ok)
    b = T.site_stage_step(now=NOW + 60, run=run_ok)
    check(a.get("state") == "ran" and b.get("state") == "unchanged" and calls == ["ok"],
          "site-saves-ship-when-the-registry-changes: a new registry ships once, then not every tick (%s)" % calls)
    d = T.read_json(str(stage))
    d["registry"] = "0" * 64                                    # the registry changed since the last copy
    T.S.dump(d, str(stage))
    T.site_stage_step(now=NOW + 120, run=run_bad)
    T.site_stage_step(now=NOW + 180, run=run_bad)
    T.site_stage_step(now=NOW + 120 + T.SITE_RETRY_S + 1, run=run_ok)
    check(calls == ["ok", "bad", "ok"],
          "site-saves-ship-when-the-registry-changes: a failed copy is retried after %d s, not every tick (%s)"
          % (T.SITE_RETRY_S, calls))


def t_the_feed_runs_after_reconcile_before_admission():
    # live 2026-11-23 07:28Z: the feed ran before reconcile, read a finished visit job as still running ("busy"), and
    # the fill loop then queued filler while 30 Pyrelands checks waited
    order = []
    saved = {k: getattr(T, k) for k in ("ssh_reachable", "steve_running", "reconcile", "drain_outbox", "remote",
                                        "admit", "archmagi_tick", "visit_feed_step", "site_stage_step")}
    try:
        T.ssh_reachable = lambda: {"busy": False}
        T.steve_running = lambda: [{"job": {"id": "J-x"}}]
        T.reconcile = lambda rec: order.append("reconcile")
        T.drain_outbox = lambda ob: order.append("outbox")
        T.remote = lambda args: (0, {"outbox": []})
        T.admit = lambda st: order.append("admit")
        T.archmagi_tick = lambda **kw: order.append("archmagi")
        T.visit_feed_step = lambda now=None: order.append("feed")
        T.site_stage_step = lambda now=None: order.append("sites")
        T.cmd_tick(None)
    finally:
        for k, v in saved.items():
            setattr(T, k, v)
    ok = "feed" in order and "reconcile" in order and "admit" in order and \
        order.index("reconcile") < order.index("feed") < order.index("admit")
    check(ok, "the-feed-runs-after-reconcile-before-admission: %s" % order)
    order.clear()
    try:
        T.ssh_reachable = lambda: None              # SteveDesktop unreachable: the feed still queues for later
        T.archmagi_tick = lambda **kw: order.append("archmagi")
        T.visit_feed_step = lambda now=None: order.append("feed")
        T.site_stage_step = lambda now=None: order.append("sites")
        T.cmd_tick(None)
    finally:
        for k, v in saved.items():
            setattr(T, k, v)
    check(order[:1] == ["feed"] and "sites" not in order,
          "the-feed-runs-after-reconcile-before-admission: with ssh down it still runs, sites do not (%s)" % order)


def main():
    for t in (t_a_waiting_check_is_queued_ahead_of_filler, t_a_visit_opening_with_an_offset_reads, t_the_owners_hold_and_gate_still_stop_a_check,
              t_nothing_waits_nothing_is_sent, t_a_lane_refusal_does_not_spend_a_check, t_visit_feed_spends_a_chain_only_on_its_own_fault, t_could_not_look_sends_nothing, t_mods_take_turns,
              t_filler_prefers_advancing_mods, t_site_saves_ship_when_the_registry_changes,
              t_the_feed_runs_after_reconcile_before_admission):
        try:
            t()
        except (Exception, SystemExit) as e:  # noqa: BLE001  a test that raises is a red, named
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("modules: %s %s" % (T.__file__, C.__file__))
    print("selftest_steve_visit_feed: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
